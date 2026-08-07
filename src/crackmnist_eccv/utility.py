# SPDX-FileCopyrightText: 2026 German Aerospace Center (DLR)
# SPDX-License-Identifier: GPL-3.0-or-later

"""Pollution utility functions for CrackMNIST experiments.

Provides per-image noise injection (Gaussian, Salt & Pepper, Gaussian Blur,
Blob/MVS, Uniform) and crack-tip mask enlargement used during training and
evaluation.
"""

from __future__ import annotations

import math
import random

import numpy as np
from scipy.interpolate import griddata
import torch
import torch.nn.functional as F


def add_gaussian_noise(
    tensor: torch.Tensor, mean: float = 0.0, intensity: float = 0.5
) -> torch.Tensor:
    """Add Gaussian noise to a tensor.

    Args:
        tensor: Input tensor.
        mean: Mean of the Gaussian noise.
        intensity: Standard deviation of the noise.

    Returns:
        Noisy tensor of the same shape.
    """
    noise = torch.randn_like(tensor) * intensity + mean
    return tensor + noise


def add_salt_and_pepper_noise(
    tensor: torch.Tensor,
    intensity: float = 0.25,
    salt_to_pepper_ratio: float = 0.5,
) -> torch.Tensor:
    """Add salt-and-pepper noise to a tensor.

    Args:
        tensor: Input tensor.
        intensity: Fraction of pixels to corrupt.
        salt_to_pepper_ratio: Proportion of corrupted pixels set to 1.0
            (salt) vs 0.0 (pepper).

    Returns:
        Noisy tensor of the same shape.
    """
    noisy_tensor = tensor.clone()
    total_pixels = tensor.numel()
    num_noisy_pixels = int(intensity * total_pixels)

    num_salt = int(salt_to_pepper_ratio * num_noisy_pixels)
    num_pepper = num_noisy_pixels - num_salt

    salt_indices = torch.randint(0, total_pixels, (num_salt,))
    pepper_indices = torch.randint(0, total_pixels, (num_pepper,))

    noisy_tensor.view(-1)[salt_indices] = 1.0
    noisy_tensor.view(-1)[pepper_indices] = 0.0

    return noisy_tensor


def add_uniform_noise(tensor: torch.Tensor, intensity: float = 0.1) -> torch.Tensor:
    """Add zero-centred uniform noise in [-intensity, +intensity).

    Args:
        tensor: Input tensor.
        intensity: Half-range of the uniform distribution. Must be >= 0.

    Returns:
        Noisy tensor of the same shape.

    Raises:
        ValueError: If intensity is negative.
    """
    if intensity < 0:
        raise ValueError("intensity must be non-negative")

    noise = torch.empty_like(tensor).uniform_(-intensity, intensity)
    return tensor + noise


def apply_gaussian_blur(tensor: torch.Tensor, intensity: float = 4.0) -> torch.Tensor:
    """Apply channel-wise Gaussian blur to a (B, C, H, W) tensor.

    Kernel size is derived from sigma following Yoshihara et al. (2023):
    ``kernel_size = round(8 * intensity + 1)``.

    Args:
        tensor: Input tensor of shape (B, C, H, W).
        intensity: Standard deviation (sigma) of the Gaussian kernel.

    Returns:
        Blurred tensor of the same shape.
    """
    kernel_size = round(8 * intensity + 1)

    if kernel_size % 2 == 0:
        kernel_size += 1

    def gaussian_kernel(kernel_size: int, intensity: float) -> torch.Tensor:
        """Build a normalised 2-D Gaussian kernel.

        Args:
            kernel_size: Size of the square kernel (must be odd).
            intensity: Standard deviation (sigma) of the Gaussian.

        Returns:
            Normalised kernel tensor of shape (1, 1, kernel_size, kernel_size).
        """
        kernel = torch.arange(kernel_size).float() - (kernel_size - 1) / 2
        x_grid, y_grid = torch.meshgrid(kernel, kernel, indexing="ij")
        kernel_2d = torch.exp(-(x_grid**2 + y_grid**2) / (2 * intensity**2))
        kernel_2d = kernel_2d / kernel_2d.sum()
        return kernel_2d.unsqueeze(0).unsqueeze(0)

    kernel = gaussian_kernel(kernel_size, intensity).to(tensor.device)

    blurred_tensor = tensor.clone()
    for channel in range(tensor.shape[1]):
        tensor_channel = tensor[:, channel : channel + 1, :, :]
        blurred_tensor_channel = F.conv2d(
            tensor_channel, kernel, padding=kernel_size // 2
        )
        blurred_tensor[:, channel : channel + 1, :, :] = blurred_tensor_channel

    return blurred_tensor


# BLOB POLLUTION SEGMENT (MVS) ###
def generate_blob_mask_to_match_oar(
    shape: tuple[int, int],
    *,
    radius: int = 4,
    target_min_oar: float = 0.10,
    target_max_oar: float = 0.30,
    max_draw_attempts: int = 2_000,
    rng: np.random.Generator | None = None,
) -> tuple[np.ndarray, float]:
    """Create a binary mask whose OAR lies in [target_min_oar, target_max_oar].

    Keeps stamping discs until the lower bound is reached, skipping discs
    that would push the OAR past ``target_max_oar``.

    Args:
        shape: (H, W) resolution of the mask.
        radius: Intended radius of each disc in pixels.
        target_min_oar: Lower bound of the desired OAR interval.
        target_max_oar: Upper bound of the desired OAR interval.
        max_draw_attempts: Safety cap on total centre-samples tried.
        rng: Optional RNG for deterministic tests.

    Returns:
        Tuple of (mask, oar) where mask is a uint8 array and oar is
        ``mask.mean()``.

    Raises:
        ValueError: If target_min_oar > target_max_oar.
        RuntimeError: If max_draw_attempts is exceeded.
    """
    if target_min_oar > target_max_oar:
        raise ValueError(f"Invalid OAR range: {target_min_oar} > {target_max_oar}")

    rng = rng or np.random.default_rng()
    H, W = shape
    total_px = H * W

    mask = np.zeros((H, W), dtype=np.uint8)
    current_px = 0

    Y, X = np.ogrid[:H, :W]

    for _ in range(max_draw_attempts):
        current_oar = current_px / total_px
        if current_oar >= target_min_oar:
            break

        remaining_px_max = target_max_oar * total_px - current_px
        if remaining_px_max < 1:
            break

        r_use = min(
            radius,
            math.floor(math.sqrt(remaining_px_max / math.pi)) or 1,
        )

        cx = rng.integers(0, W)
        cy = rng.integers(0, H)

        disc = (X - cx) ** 2 + (Y - cy) ** 2 <= r_use**2
        new_pixels = disc & (mask == 0)

        added = int(new_pixels.sum())
        if added == 0:
            continue

        mask[new_pixels] = 1
        current_px += added
    else:
        raise RuntimeError(
            "Exceeded max_draw_attempts while trying to reach the OAR band "
            f"[{target_min_oar}, {target_max_oar}]. "
            "Consider increasing `max_draw_attempts`, enlarging `radius`, "
            "or relaxing the OAR constraints."
        )

    return mask, mask.mean()


def add_blob_pollution_and_interp(
    tensor: torch.Tensor,
    *,
    radius: int = 4,
    target_min_oar: float = 0.10,
    target_max_oar: float = 0.20,
    interp_method: str = "linear",
) -> tuple[torch.Tensor, np.ndarray, float]:
    """Mask a (1, C, H, W) tensor with blob occlusion and in-paint the holes.

    Args:
        tensor: Input tensor of shape (1, C, H, W).
        radius: Disc radius for blob generation.
        target_min_oar: Lower OAR bound.
        target_max_oar: Upper OAR bound.
        interp_method: Interpolation method passed to scipy.griddata.

    Returns:
        Tuple of (tensor_filled, blob_mask, oar) where tensor_filled has NaNs
        replaced by interpolated values, blob_mask is a (H, W) uint8 array,
        and oar is the final Occluded Area Ratio.

    Raises:
        ValueError: If tensor shape is not (1, C, H, W).
        RuntimeError: If fewer than 4 valid points remain for interpolation.
    """
    if tensor.ndim != 4 or tensor.size(0) != 1:
        raise ValueError("Expected tensor shape (1, C, H, W).")

    dev = tensor.device
    _, C, H, W = tensor.shape

    blob_mask, oar = generate_blob_mask_to_match_oar(
        (H, W),
        radius=radius,
        target_min_oar=target_min_oar,
        target_max_oar=target_max_oar,
    )
    blob_mask_t = torch.from_numpy(blob_mask).to(dev)

    polluted = tensor.clone()
    nan_val = torch.tensor(float("nan"), device=dev)
    polluted[:, :, blob_mask_t.bool()] = nan_val

    yy, xx = np.mgrid[0:H, 0:W]
    xx_flat, yy_flat = xx.ravel(), yy.ravel()

    filled = polluted.clone()
    for c in range(C):
        img = polluted[0, c].cpu().numpy()
        valid = ~np.isnan(img)
        n_valid = int(valid.sum())

        if n_valid < 4:
            raise RuntimeError(
                f"Channel {c}: only {n_valid} valid points left; cannot interpolate."
            )

        pts = np.column_stack((xx_flat[valid.ravel()], yy_flat[valid.ravel()]))
        vals = img[valid]

        method = interp_method if n_valid >= 30 else "nearest"
        interp = griddata(pts, vals, (xx, yy), method=method)

        if np.isnan(interp).any():
            nearest = griddata(pts, vals, (xx, yy), method="nearest")
            interp = np.where(np.isnan(interp), nearest, interp)

        filled[0, c] = torch.from_numpy(interp).to(dev)

    return filled, blob_mask, oar


def apply_per_image_pollution(
    inputs: torch.Tensor,
    pollution_ratio: float = 0.5,
    pollution_type: str = "gaussian",
    **kwargs: float | str,
) -> torch.Tensor:
    """Apply noise to a random subset of images in a batch.

    Args:
        inputs: Batch of input tensors (B, C, H, W).
        pollution_ratio: Proportion of images to pollute.
        pollution_type: One of 'gaussian', 'salt_pepper', 'gaussian_blur',
            'blob', 'uniform'.
        kwargs: Extra keyword arguments forwarded to the pollution function.
                Values must be float, int, or str.

    Returns:
        Tensor with selected images polluted, same shape as inputs.

    Raises:
        ValueError: If pollution_type is not recognised.
    """
    polluted_inputs = inputs.clone()
    batch_size = inputs.size(0)
    num_polluted = int(batch_size * pollution_ratio)

    indices_to_pollute = sorted(random.sample(range(batch_size), num_polluted))

    for i in indices_to_pollute:
        img = inputs[i].unsqueeze(0)

        if pollution_type == "gaussian":
            img = add_gaussian_noise(img, **kwargs)  # ty: ignore[invalid-argument-type]
        elif pollution_type == "salt_pepper":
            img = add_salt_and_pepper_noise(img, **kwargs)  # ty: ignore[invalid-argument-type]
        elif pollution_type == "gaussian_blur":
            img = apply_gaussian_blur(img, **kwargs)  # ty: ignore[invalid-argument-type]
        elif pollution_type == "blob":
            img, _blob_mask, _oar = add_blob_pollution_and_interp(img, **kwargs)  # ty: ignore[invalid-argument-type]
        elif pollution_type == "uniform":
            img = add_uniform_noise(img, **kwargs)  # ty: ignore[invalid-argument-type]
        else:
            raise ValueError(f"Unknown pollution type: {pollution_type}")

        polluted_inputs[i] = img.squeeze(0)

    return polluted_inputs


def enlarge_crack_tip(mask: np.ndarray, kernel_size: int = 3) -> np.ndarray:
    """Enlarge the annotated crack tip region in a binary mask.

    Expands each foreground pixel into a square neighbourhood of size
    ``kernel_size x kernel_size``.

    Args:
        mask: 2D numpy array of shape (H, W) with foreground pixels encoded
            as 255 and background as 0.
        kernel_size: Size of the square neighbourhood. Must be an odd integer
            (e.g. 1, 3, 5). Default is 3.

    Returns:
        New 2D mask of the same shape with the crack tip region enlarged.
    """
    pad = kernel_size // 2
    height, width = mask.shape
    new_mask = np.copy(mask)
    y, x = np.where(mask == 255)
    for i in range(len(x)):
        y_start = max(y[i] - pad, 0)
        y_end = min(y[i] + pad + 1, height)
        x_start = max(x[i] - pad, 0)
        x_end = min(x[i] + pad + 1, width)
        new_mask[y_start:y_end, x_start:x_end] = 255
    return new_mask
