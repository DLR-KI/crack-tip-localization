---
title: Checklist
hide: navigation
---
<!--
SPDX-FileCopyrightText: 2026 German Aerospace Center (DLR)
SPDX-License-Identifier: LicenseRef-Proprietary-DLR
-->
<!-- markdownlint-disable MD055 MD056 -->

<!-- markdownlint-disable-next-line MD025 -->
# Checklist for Application Class 1

/// details | Usage Hints

This checklist provides recommendations for software development.
It is primarily intended for software developers for the self-assessment of developed software and as a source of ideas for further development.
The checklist does not provide any new, revolutionary approaches to software development.
However, it helps to not forget necessary, essential steps of software development.
In addition, the recommendations can serve as an argumentation aid.

The recommendations are created with a focus on know-how maintenance and good software engineering practice.
They help to maintain the sustainability of the developed software.
The recommendations encourage the use of tools, the creation of documentation, the establishment of processes and adherence to principles.
When assessing a recommendation, it is recommended to consider to what extent the aspect mentioned is implemented and whether there is a need for improvement.
This could be implemented as follows:

- Is there currently no need for improvement and is the recommendation addressed appropriately?
    Status: **ok**
- Is there any potential for improvement that should be implemented in the near future?
    Status: **todo**, record the need for improvement
- Is the recommendation not yet relevant but could be helpful in a later development phase?
    Status: **future**
- Is the recommendation not meaningfully implementable within the development context?
    Status: **n.a.** (not applicable) explain the reason

In case of questions, you can contact the Software Engineering Contact of your institute or facility.

///

> The checklist is in version 1.1.1.
> It bases on the document [QMH-DLR-VA005](https://sycatqp:8081/document/de-DE/D106/download/) in version 1.0.2.

<!-- use `<h2>` instead of `## ` to hide headline from table of contents -->
<h2 id="summary">Summary of Results</h2>

The software _Assessing the Data-Centric Robustness of a Crack Tip Detection Model through Artificial Data Pollution_ implements 0/25 recommendations of application class 1.

The focus of future improvements is on:

- ...

<!-- use `<h2>` instead of `## ` to hide headline from table of contents -->
<h2 id="toc">Table of Contents</h2>

- [Qualification](#qualification)
- [Requirements Management](#requirements-management)
- [Software Architecture](#software-architecture)
- [Change Management](#change-management)
- [Design and Implementation](#design-and-implementation)
- [Software Test](#software-test)
- [Release Management](#release-management)
- [Automation and Dependency Management](#automation-and-dependency-management)

## Qualification

| Recommendation                                    | Status | Comment                                                |
|---------------------------------------------------|:------:|--------------------------------------------------------|
| The software responsible recognizes the different |        |                                                        |
| application classes and knows which is to be used |        |                                                        |
| for his/her software. **(EQA.1)**                 |        |                                                        |
|                                                   |        |                                                        |
| The software responsible knows how to request     |        |                                                        |
| specific support at the beginning and during      |        |                                                        |
| development as well as to exchange ideas with     |        |                                                        |
| other colleagues on the subject of software       |        |                                                        |
| development. **(EQA.2)**                          |        |                                                        |
|                                                   |        |                                                        |
| The persons involved in the development determine |        |                                                        |
| the skills needed with regard to their role and   |        |                                                        |
| the intended application class. They communicate  |        |                                                        |
| these needs to the supervisor. **(EQA.3)**        |        |                                                        |
|                                                   |        |                                                        |
| The persons involved in the development are given |        |                                                        |
| the tools needed for their tasks and are trained  |        |                                                        |
| in their use. **(EQA.4)**                         |        |                                                        |

## Requirements Management

| Recommendation                                    | Status | Comment                                                |
|---------------------------------------------------|:------:|--------------------------------------------------------|
| The problem definition is coordinated with all    |        |                                                        |
| parties involved and documented. It describes the |        |                                                        |
| objectives, the purpose of the software, the      |        |                                                        |
| essential requirements and the desired            |        |                                                        |
| application class in a concise, understandable    |        |                                                        |
| way. **(EAM.1)**                                  |        |                                                        |
|                                                   |        |                                                        |
| The constraints are documented. **(EAM.3)**       |        |                                                        |

## Software Architecture

| Recommendation                                    | Status | Comment                                                |
|---------------------------------------------------|:------:|--------------------------------------------------------|
| Essential architectural concepts and              |        |                                                        |
| corresponding decisions are at least documented   |        |                                                        |
| in a lean way. **(ESA.2)**                        |        |                                                        |

## Change Management

| Recommendation                                    | Status | Comment                                                |
|---------------------------------------------------|:------:|--------------------------------------------------------|
| The most important information describing how to  |        |                                                        |
| contribute to development are stored in a central |        |                                                        |
| location. **(EÄM.2)**                             |        |                                                        |
|                                                   |        |                                                        |
| Known bugs, important unresolved tasks and ideas  |        |                                                        |
| are at least noted in bullet point form and       |        |                                                        |
| stored centrally. **(EÄM.5)**                     |        |                                                        |
|                                                   |        |                                                        |
| A repository is set up in a version control       |        |                                                        |
| system. The repository is adequately structured   |        |                                                        |
| and ideally contains all artefacts for building a |        |                                                        |
| usable software version and for testing it.       |        |                                                        |
| **(EÄM.7)**                                       |        |                                                        |
|                                                   |        |                                                        |
| Every change of the repository ideally serves a   |        |                                                        |
| specific purpose, contains an understandable      |        |                                                        |
| description and leaves the software in a          |        |                                                        |
| consistent, working state. **(EÄM.8)**            |        |                                                        |

## Design and Implementation

| Recommendation                                    | Status | Comment                                                |
|---------------------------------------------------|:------:|--------------------------------------------------------|
| The usual patterns and solution approaches of the |        |                                                        |
| selected programming language are used and a set  |        |                                                        |
| of rules regarding the programming style is       |        |                                                        |
| consistently applied. The set of rules refers at  |        |                                                        |
| least to the formatting and commenting.           |        |                                                        |
| **(EDI.1)**                                       |        |                                                        |
|                                                   |        |                                                        |
| The software is structured modularly as far as    |        |                                                        |
| possible. The modules are coupled loosely. I.e.,  |        |                                                        |
| a single module depends as little as possible on  |        |                                                        |
| other modules. **(EDI.2)**                        |        |                                                        |
|                                                   |        |                                                        |
| The source code and the comments contain as       |        |                                                        |
| little duplicated information as possible.        |        |                                                        |
| ("Don`t repeat yourself.") **(EDI.9)**            |        |                                                        |
|                                                   |        |                                                        |
| Prefer simple, understandable solutions.          |        |                                                        |
| ("Keep it simple and stupid."). **(EDI.10)**      |        |                                                        |

## Software Test

| Recommendation                                    | Status | Comment                                                |
|---------------------------------------------------|:------:|--------------------------------------------------------|
| The basic functions and features of the software  |        |                                                        |
| are tested in a near-operational environment.     |        |                                                        |
| **(EST.4)**                                       |        |                                                        |
|                                                   |        |                                                        |
| The repository ideally contains all artefacts:    |        |                                                        |
| required to test the software. **(EST.10)**       |        |                                                        |

## Release Management

| Recommendation                                    | Status | Comment                                                |
|---------------------------------------------------|:------:|--------------------------------------------------------|
| Every release has a unique release number. The    |        |                                                        |
| release number can be used to determine the       |        |                                                        |
| underlying software version in the repository.    |        |                                                        |
| **(ERM.1)**                                       |        |                                                        |
|                                                   |        |                                                        |
| The release package contains or references the    |        |                                                        |
| user documentation. At least, it consists of      |        |                                                        |
| installation, usage and contact information as    |        |                                                        |
| well as release notes. In the case of the         |        |                                                        |
| distribution of the release package to third      |        |                                                        |
| parties outside DLR, the licensing conditions     |        |                                                        |
| must be enclosed. **(ERM.2)**                     |        |                                                        |
|                                                   |        |                                                        |
| All foreseen test activities are executed during  |        |                                                        |
| release performance. **(ERM.6)**                  |        |                                                        |
|                                                   |        |                                                        |
| Prior to distribution of the release package to   |        |                                                        |
| third parties outside DLR, it must be ensured     |        |                                                        |
| that a license is defined, that the licensing     |        |                                                        |
| terms of used third-party software are met, and   |        |                                                        |
| that all necessary license information is         |        |                                                        |
| included in the release package. **(ERM.9)**      |        |                                                        |
|                                                   |        |                                                        |
| Prior to distribution of the release package to   |        |                                                        |
| third parties outside DLR, it has to be ensured   |        |                                                        |
| that the export control regulations are met.      |        |                                                        |
| **(ERM.10)**                                      |        |                                                        |

## Automation and Dependency Management

| Recommendation                                    | Status | Comment                                                |
|---------------------------------------------------|:------:|--------------------------------------------------------|
| The simple build process is basically automated   |        |                                                        |
| and necessary manual steps are described. In      |        |                                                        |
| addition, there is sufficient information         |        |                                                        |
| available about the operational and development   |        |                                                        |
| environment. **(EAA.1)**                          |        |                                                        |
|                                                   |        |                                                        |
| The dependencies to build the software are at     |        |                                                        |
| least described by name, version number, purpose, |        |                                                        |
| licensing terms and reference source. **(EAA.2)** |        |                                                        |
|                                                   |        |                                                        |
| The repository ideally contains all artefacts to  |        |                                                        |
| perform the build process. **(EAA.10)**           |        |                                                        |
