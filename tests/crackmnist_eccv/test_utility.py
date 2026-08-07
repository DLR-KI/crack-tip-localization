# SPDX-FileCopyrightText: 2026 German Aerospace Center (DLR)
# SPDX-License-Identifier: GPL-3.0-or-later

"""Tests for utility.py and for_blob_formatting.py."""

import numpy as np
import pytest
import torch

from crackmnist_eccv.for_blob_formatting import extract_first_float
from crackmnist_eccv.utility import (
    add_gaussian_noise,
    add_salt_and_pepper_noise,
    apply_gaussian_blur,
    enlarge_crack_tip,
    generate_blob_mask_to_match_oar,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def batch_tensor() -> torch.Tensor:
    """Return a small (2, 2, 8, 8) batch tensor filled with 0.5."""
    return torch.full((2, 2, 8, 8), 0.5)


@pytest.fixture()
def single_tensor() -> torch.Tensor:
    """Return a (1, 2, 16, 16) tensor filled with 0.5."""
    return torch.full((1, 2, 16, 16), 0.5)


# ---------------------------------------------------------------------------
# add_gaussian_noise
# ---------------------------------------------------------------------------


class TestAddGaussianNoise:
    def test_output_shape(self, batch_tensor: torch.Tensor) -> None:
        """Output shape must match input shape."""
        out = add_gaussian_noise(batch_tensor)
        assert out.shape == batch_tensor.shape

    def test_noise_is_added(self, batch_tensor: torch.Tensor) -> None:
        """Output must differ from input when intensity > 0."""
        out = add_gaussian_noise(batch_tensor, intensity=1.0)
        assert not torch.allclose(out, batch_tensor)

    def test_zero_intensity_unchanged(self, batch_tensor: torch.Tensor) -> None:
        """Zero intensity with zero mean should leave tensor unchanged."""
        out = add_gaussian_noise(batch_tensor, mean=0.0, intensity=0.0)
        assert torch.allclose(out, batch_tensor)


# ---------------------------------------------------------------------------
# add_salt_and_pepper_noise
# ---------------------------------------------------------------------------


class TestAddSaltAndPepperNoise:
    def test_output_shape(self, batch_tensor: torch.Tensor) -> None:
        """Output shape must match input shape."""
        out = add_salt_and_pepper_noise(batch_tensor)
        assert out.shape == batch_tensor.shape

    def test_corrupted_pixels_are_zero_or_one(self, batch_tensor: torch.Tensor) -> None:
        """All pixel values in the output must be 0.0, 0.5, or 1.0."""
        out = add_salt_and_pepper_noise(batch_tensor, intensity=0.5)
        unique = out.unique()
        for val in unique:
            assert val.item() in {0.0, 0.5, 1.0}

    def test_zero_intensity_unchanged(self, batch_tensor: torch.Tensor) -> None:
        """Zero intensity should leave tensor unchanged."""
        out = add_salt_and_pepper_noise(batch_tensor, intensity=0.0)
        assert torch.allclose(out, batch_tensor)


# ---------------------------------------------------------------------------
# apply_gaussian_blur
# ---------------------------------------------------------------------------


class TestApplyGaussianBlur:
    def test_output_shape(self, batch_tensor: torch.Tensor) -> None:
        """Output shape must match input shape."""
        out = apply_gaussian_blur(batch_tensor, intensity=1.0)
        assert out.shape == batch_tensor.shape

    def test_uniform_input_unchanged(self, batch_tensor: torch.Tensor) -> None:
        """Blurring a uniform tensor should leave interior values unchanged."""
        large = torch.full((2, 2, 32, 32), 0.5)
        out = apply_gaussian_blur(large, intensity=1.0)
        assert torch.allclose(out[:, :, 8:-8, 8:-8], large[:, :, 8:-8, 8:-8], atol=1e-5)


# ---------------------------------------------------------------------------
# generate_blob_mask_to_match_oar
# ---------------------------------------------------------------------------


class TestGenerateBlobMask:
    def test_oar_within_range(self) -> None:
        """OAR of generated mask must lie within the target interval."""
        rng = np.random.default_rng(42)
        _, oar = generate_blob_mask_to_match_oar(
            (32, 32),
            radius=3,
            target_min_oar=0.05,
            target_max_oar=0.20,
            rng=rng,
        )
        assert 0.05 <= oar <= 0.20

    def test_mask_is_binary(self) -> None:
        """Mask values must be 0 or 1."""
        rng = np.random.default_rng(0)
        mask, _ = generate_blob_mask_to_match_oar(
            (32, 32), radius=3, target_min_oar=0.05, target_max_oar=0.20, rng=rng
        )
        assert set(np.unique(mask)).issubset({0, 1})

    def test_invalid_oar_range_raises(self) -> None:
        """target_min_oar > target_max_oar must raise ValueError."""
        with pytest.raises(ValueError, match="Invalid OAR range"):
            generate_blob_mask_to_match_oar(
                (32, 32), target_min_oar=0.5, target_max_oar=0.1
            )

    def test_mask_shape(self) -> None:
        """Mask shape must match the requested shape."""
        rng = np.random.default_rng(1)
        mask, _ = generate_blob_mask_to_match_oar(
            (28, 28), radius=2, target_min_oar=0.05, target_max_oar=0.20, rng=rng
        )
        assert mask.shape == (28, 28)


# ---------------------------------------------------------------------------
# enlarge_crack_tip
# ---------------------------------------------------------------------------


class TestEnlargeCrackTip:
    def test_foreground_expands(self) -> None:
        """A single foreground pixel should expand to a 3x3 block."""
        mask = np.zeros((10, 10), dtype=np.uint8)
        mask[5, 5] = 255
        enlarged = enlarge_crack_tip(mask, kernel_size=3)
        assert enlarged[4:7, 4:7].min() == 255

    def test_background_unchanged_far_from_tip(self) -> None:
        """Pixels far from any foreground pixel should remain 0."""
        mask = np.zeros((20, 20), dtype=np.uint8)
        mask[10, 10] = 255
        enlarged = enlarge_crack_tip(mask, kernel_size=3)
        assert enlarged[0, 0] == 0

    def test_output_shape_unchanged(self) -> None:
        """Output shape must equal input shape."""
        mask = np.zeros((16, 16), dtype=np.uint8)
        mask[8, 8] = 255
        enlarged = enlarge_crack_tip(mask, kernel_size=3)
        assert enlarged.shape == mask.shape

    def test_empty_mask_unchanged(self) -> None:
        """An all-zero mask should remain all-zero after enlargement."""
        mask = np.zeros((10, 10), dtype=np.uint8)
        enlarged = enlarge_crack_tip(mask, kernel_size=3)
        assert enlarged.sum() == 0


# ---------------------------------------------------------------------------
# extract_first_float (from for_blob_formatting.py)
# ---------------------------------------------------------------------------


class TestExtractFirstFloat:
    def test_plain_float_string(self) -> None:
        """A plain float string should be parsed directly."""
        assert extract_first_float("0.5") == pytest.approx(0.5)

    def test_tuple_string(self) -> None:
        """A tuple-like string should return the first element."""
        assert extract_first_float("(0.1, 0.2)") == pytest.approx(0.1)

    def test_float_input(self) -> None:
        """A float input should be returned as-is."""
        assert extract_first_float(0.3) == pytest.approx(0.3)

    def test_invalid_returns_none(self) -> None:
        """An unparsable string should return None."""
        assert extract_first_float("not_a_number") is None
