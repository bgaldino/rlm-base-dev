---
# Frontmatter is the source of truth for the eventual auto-gen.
# Render scripts read these fields to build cover page, headers, footers.
release_version: 260           # RCA package version (e.g. 260, 262)
release_name: "Spring '26"      # Seasonal name
api_version: 66.0               # Salesforce API version
area: "Salesforce Pricing"      # Functional area name (must match journey map label)
document_version: 1.0           # Increment when content changes within a release cycle
status: draft                   # draft | review | final
last_updated: 2026-05-06
authors:
  - Brian Galdino
data_shape: qb                  # Which dataset this exercise assumes (qb | mfg | q3)
prerequisites:
  - prepare_rlm_org flow completed
  - QuantumBit catalog loaded (qb=true)
---

# Revenue Cloud — {{ area }}

**Enablement Exercises** · Version {{ document_version }}, {{ release_name }}

> Org / data shape: {{ data_shape }}. These exercises assume an org provisioned by `rlm-base-dev`'s `prepare_rlm_org` flow with the QuantumBit catalog loaded.

---

## Table of Contents

<!-- Generated from H2/H3 headers; markdown renderers (and the eventual auto-gen) populate this. -->

---

## Release Overview

Salesforce Revenue Cloud {{ area }} includes the following new features in {{ release_name }}:

1. **{{ feature_1_name }}** — {{ feature_1_one_liner }}
2. **{{ feature_2_name }}** — {{ feature_2_one_liner }}
<!-- Add one bullet per new feature in this release. -->

> **Carry-forward features** from prior releases (covered in earlier release exercise PDFs, not re-explained here): {{ carry_forward_list }}

---

<!--
Each new feature gets its own H2 section with the four-part structure below.
The auto-gen reads the structure literally — keep section headers consistent.
-->

## {{ feature_name }}

### Business Objective

{{ what_problem_does_this_solve }}

### Use Cases

**{{ persona }} persona:**

- **{{ use_case_title }}** — {{ use_case_narrative }}

### Design Time Configuration

<!-- Numbered, executable steps. Reference QuantumBit data (specific products, SKUs, price books) by name. -->

1. Navigate to {{ where }}.
2. {{ next_step }}.
3. {{ ... }}.

### Configuration and Runtime Video

{{ link_or_note }}

---

<!-- Repeat the four-part block for each feature. -->

## Footer

© Copyright 2000–{{ current_year }} Salesforce, Inc. All rights reserved. Salesforce is a registered trademark of Salesforce, Inc., as are other names and marks.

---

## Authoring Notes (delete before publishing)

- Use **QuantumBit catalog** product names and SKUs in all data references. Look them up in `datasets/sfdmu/qb/en-US/qb-pcm/Product2.csv`.
- For pricing-specific data (price books, adjustment schedules), use names from `datasets/sfdmu/qb/en-US/qb-pricing/`.
- Screenshots: capture against an org provisioned by `cci flow run prepare_rlm_org` so visuals match user environment.
- New features that depend on org setup not in `prepare_rlm_org` should call out the prerequisite explicitly at the top of the feature section.
- "Carry-forward features" list keeps each release exercise scoped to net-new content. Readers reference prior-release exercise PDFs in the historical archive (`docs/enablement/258/` and earlier) for stable features.
