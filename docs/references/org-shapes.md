# Org Shapes Reference

Canonical reference for all scratch org definition files in `orgs/`. Each file is registered in `cumulusci.yml` under `orgs.scratch` and is passed to `cci org scratch <config> <alias>` when creating a scratch org.

> **Target release:** Salesforce Release 260 (Spring '26), API v66.0

---

## Overview

The 24 org shapes fall into two categories:

| Category | Count | How it works |
|----------|-------|-------------|
| **Feature-based** | 14 | Full `edition`, `features`, and `settings` blocks — Salesforce builds the org from scratch |
| **Template-based (TFID)** | 10 | Only a `template` ID + `instance` — org is cloned from a live Salesforce org snapshot |

### Instance Pins

Many org shapes pin to a specific Salesforce infrastructure pod via the `instance` field. Leaving it unset lets Salesforce pick any available pod on the current release track.

| Instance | Pod / Track | Notes |
|----------|-------------|-------|
| *(unset)* | Any available | Default; Salesforce picks automatically |
| `USA794` | SB0 pre-release | Gets Salesforce releases before GA; used for SB0-track testing |
| `USA1000` | R1 | First GA-release instance track |
| `NA234` | NA pod | North America pod; used for IDO Tech R2 template |

---

## Feature-Based Org Shapes

These 14 orgs specify `edition`, `features`, and `settings` inline. All enable the full RLM feature stack (Billing, CPQ, OmniStudio, Order Management, Pricing/Rating, PRM, AI Platform, Communities, etc.). Differences between them are called out explicitly below.

### Developer Edition Orgs

Developer Edition orgs (`"edition": "developer"`) have different governor limits than Enterprise but include all the necessary RLM features. They **do not** include `SalesCloudEinstein` (which requires Enterprise licensing).

#### `dev.json` — Standard Developer Org

```
CCI alias: dev
Edition:   developer
Instance:  (unset — any available pod)
```

**Use when:** Everyday feature development. The default dev org for most work. No instance constraints, so Salesforce provisions it on the fastest available pod.

**Key characteristics:**
- Full RLM feature set (excluding `SalesCloudEinstein`)
- No instance pin — fastest to provision

---

#### `dev-r1.json` — Developer Org on R1 Infrastructure

```
CCI alias: dev-r1
Edition:   developer
Instance:  USA1000 (R1 pod)
```

**Use when:** Reproducing or validating issues that are specific to the R1 release track. Also useful when your work needs to be validated against R1 before that infrastructure receives the GA release.

**Key characteristics:**
- Identical features to `dev.json`
- Pinned to R1 pod (USA1000)

---

#### `dev-sb0.json` — Developer Org on SB0 Infrastructure

```
CCI alias: dev-sb0
Edition:   developer
Instance:  USA794 (SB0 pre-release pod)
```

**Use when:**
- UX assembly and drift capture/apply workflows (see `docs/features/dynamic-ux-assembly.md`) — this is the **canonical org** for UX work
- Testing features against the pre-release Salesforce build that ships to SB0 before GA

**Key characteristics:**
- Identical features to `dev.json`
- Pinned to SB0 pod (USA794) — receives Salesforce updates before GA
- Referenced throughout the UX assembly documentation as the default target

---

### Enterprise Edition Orgs

Enterprise Edition orgs (`"edition": "enterprise"`) more closely match customer production environments. They include `SalesCloudEinstein` (unless noted) and reflect the full commercial licensing model.

#### `dev-enhanced.json` — Enhanced Developer Org (Enterprise Edition)

```
CCI alias: dev_enhanced
Edition:   enterprise
Instance:  (unset)
Features:  All standard + SalesCloudEinstein
```

**Use when:** Development work that requires Enterprise Edition licensing (e.g., testing behavior differences between Developer and Enterprise editions, or features gated by `org_config.org_type != "Developer Edition"` in `cumulusci.yml`).

**Key characteristics:**
- Enterprise edition upgrade of `dev.json`
- Adds `SalesCloudEinstein` feature
- No instance pin

---

#### `dev-datacloud.json` — Developer Org with Data Cloud (CDP)

```
CCI alias: dev_datacloud
Edition:   enterprise
Instance:  (unset)
Features:  Standard + CustomerDataPlatform + CustomerDataPlatformLite
```

**Use when:** Working on Data Cloud / Customer Data Platform (CDP) integrations or features that require the `CustomerDataPlatform` license. This is the only org shape that enables CDP.

**Key characteristics:**
- Adds `CustomerDataPlatform` and `CustomerDataPlatformLite` features
- Enables `customerDataPlatformSettings.enableCustomerDataPlatform: true`
- **Does not** include `agentPlatformSettings` or `industriesSettings` blocks — different settings profile from all other feature-based orgs
- Does not include `B2BCommerce`, `Chatbot`, or `ContractsAI` in its feature list — leaner feature set focused on CDP integration

---

#### `dev_preview.json` — Next Salesforce Release (Preview)

```
CCI alias: dev_preview
Edition:   enterprise
Release:   preview
Instance:  (unset)
```

**Use when:** Testing compatibility with the **next upcoming** Salesforce release before it reaches GA. Use this to catch API/metadata breaking changes early.

**Key characteristics:**
- Uses `"release": "preview"` — Salesforce provisions this on the preview release track
- Feature set identical to `beta.json`

---

#### `dev_previous.json` — Prior Salesforce Release

```
CCI alias: dev_previous
Edition:   enterprise
Release:   previous
Instance:  (unset)
```

**Use when:** Reproducing issues on the prior Salesforce release, or validating backwards compatibility when a change might affect orgs that haven't yet received the current release.

**Key characteristics:**
- Uses `"release": "previous"` — Salesforce provisions on the prior release track
- Feature set identical to `beta.json`

---

#### `beta.json` — Standard Enterprise Org (CI/Beta Pipeline)

```
CCI alias: beta
Edition:   enterprise
Instance:  (unset)
```

**Use when:** General-purpose enterprise scratch org. The primary org for CI pipelines and integration testing. Named `beta` to align with the CumulusCI standard `beta` branch/pipeline convention.

**Key characteristics:**
- Full feature set including `SalesCloudEinstein`
- No instance pin — Salesforce picks any available pod
- The most commonly referenced org in documentation and scripts

---

#### `feature.json` — Feature Branch Enterprise Org

```
CCI alias: feature
Edition:   enterprise
Instance:  (unset)
```

**Use when:** Feature branch CI pipelines. Aligns with the CumulusCI `feature` branch automation convention, where feature branches run against a separate org config from `beta`.

**Key characteristics:**
- JSON settings identical to `beta.json`
- Distinguished by name for CI pipeline routing (feature vs. beta branches)

---

#### `release.json` — Release Candidate Enterprise Org

```
CCI alias: release
Edition:   enterprise
Instance:  (unset)
```

**Use when:** Release branch validation before a GA promotion. Aligns with the CumulusCI `release` branch automation convention.

**Key characteristics:**
- JSON settings identical to `beta.json`
- Distinguished by name for CI pipeline routing (release branches)

---

#### `ent.json` — Enterprise Baseline (No Instance Pin)

```
CCI alias: ent
Edition:   enterprise
Instance:  (unset)
```

**Use when:** Ad-hoc enterprise org creation without a specific instance requirement. Functionally equivalent to `beta.json` — use when you need an enterprise org and don't need the CI pipeline naming semantics of `beta`.

**Key characteristics:**
- JSON settings identical to `beta.json`
- No instance pin

---

#### `ent-r1.json` — Enterprise Org on R1 Infrastructure

```
CCI alias: ent-r1
Edition:   enterprise
Instance:  USA1000 (R1 pod)
```

**Use when:** Enterprise-edition testing pinned to the R1 release track. Use when reproducing R1-specific issues or validating against R1 before GA.

**Key characteristics:**
- Identical features to `ent.json`
- Pinned to R1 pod (USA1000)

---

#### `ent-sb0.json` — Enterprise Org on SB0 Infrastructure

```
CCI alias: ent-sb0
Edition:   enterprise
Instance:  USA794 (SB0 pre-release pod)
```

**Use when:** Enterprise-edition testing on the pre-release SB0 infrastructure. Use when validating features in an enterprise org that receives updates before GA.

**Key characteristics:**
- Identical features to `ent.json`
- Pinned to SB0 pod (USA794)

---

#### `test-sb0.json` — Automated Test Org on SB0 Infrastructure

```
CCI alias: test-sb0
Edition:   enterprise
Instance:  USA794 (SB0 pre-release pod)
```

**Use when:** Running Robot Framework automated tests against an enterprise org on the SB0 pod. Dedicated test org shape to keep CI test runs separate from manual development orgs on the same instance.

**Key characteristics:**
- Identical features and instance to `ent-sb0.json`
- Named `test-sb0` to signal automated test use — referenced in the CI workflow `prepare-rlm-org.yml` as an example config

---

## Template-Based (TFID) Org Shapes

These 10 org shapes use a Salesforce **org template ID** (`template: 0TT...`) instead of inline features and settings. The org is cloned from a live Salesforce org snapshot (a Trialforce Source Org) rather than built from scratch. This means:

- Features and settings are inherited from the snapshot, not declared in the JSON
- Template IDs are environment-specific — if the underlying TSO is refreshed, the template ID may need updating
- The `instance` field is required to match the pod where the template was captured

**How to create a TFID org:**
```bash
cci org scratch tfid my-tfid-org --default
cci flow run prepare_rlm_org --org my-tfid-org
```

> The `tso: true` feature flag in `cumulusci.yml` activates TSO-specific steps in `prepare_rlm_org` (additional permission set licenses, TSO metadata bundles). Set this flag when running against TFID orgs for a full TSO setup.

---

### `tfid.json` — Primary Base Trialforce Template

```
CCI alias: tfid
Template:  0TTKX000000RHfW
Instance:  USA794 (SB0)
```

**Use when:** Creating a Trialforce-based org from the primary base TSO template. This is the canonical TFID shape used for standard Trialforce org generation on the SB0 pod.

---

### `tfid-cdo.json` — CDO Trialforce Template

```
CCI alias: tfid-cdo
Template:  0TTKX000001N2AL
Instance:  USA1000 (R1)
```

**Use when:** Creating a Customer Data Org (CDO) from its Trialforce template. The CDO template lives on the R1 pod (USA1000).

---

### `tfid-cdo-rlm.json` — CDO + RLM Combined Trialforce Template

```
CCI alias: tfid-cdo-rlm
Template:  0TTHo000004e0cY
Instance:  USA1000 (R1)
```

**Use when:** Creating a Trialforce org that combines both CDO (Customer Data Org) and RLM capabilities from a single shared template. Distinct from `tfid-cdo.json` — this template includes the full RLM layer on top of the CDO base. Lives on R1 pod.

---

### `tfid-dev.json` — Developer Edition Trialforce Template

```
CCI alias: tfid-dev
Template:  0TTWs000000btWz
Instance:  USA794 (SB0)
```

**Use when:** Creating Developer Edition Trialforce-based orgs. This template is provisioned from a Developer Edition TSO (as opposed to the Enterprise edition templates used by most other TFID shapes).

---

### `tfid-enable.json` — Enablement Trialforce Template

```
CCI alias: tfid-enable
Template:  0TTWs00000110mz
Instance:  USA794 (SB0)
```

**Use when:** Org enablement and onboarding Trialforce flows. This template is used for orgs that need to go through an enablement activation path rather than a full `prepare_rlm_org` setup.

---

### `tfid-ido-tech-SB0.json` — IDO Tech Template (SB0)

```
CCI alias: tfid-ido-tech (maps to SB0.json)
Template:  0TTKX000001yZlJ
Instance:  USA794 (SB0)
```

**Use when:** Creating Industry Demo Org (IDO) technical team orgs on the SB0 pre-release pod. The IDO Tech team uses this shape to validate their templates against the pre-release infrastructure.

---

### `tfid-ido-tech-R2.json` — IDO Tech Template (R2 / NA234)

```
CCI alias: tfid-ido-tech-R2
Template:  0TTKX000001yZlJ (same template as SB0 variant)
Instance:  NA234 (NA pod)
```

**Use when:** Creating IDO Technical team orgs on the NA234 R2 pod. Uses the same underlying template as `tfid-ido-tech-SB0.json` but provisioned on a different infrastructure pod (NA234 vs USA794).

**Note:** Both IDO Tech shapes reference the same template ID — the only difference is the `instance` pin.

---

### `tfid-qb-tso.json` — QuantumBit TSO Template

```
CCI alias: tfid-qb-tso
Template:  0TTKX000000SEu9
Instance:  USA794 (SB0)
```

**Use when:** Creating Trialforce Source Orgs that include the QuantumBit product dataset. This template captures a TSO with the full QuantumBit demo data shape already loaded — use it when the target Trialforce org needs to ship with QuantumBit data pre-seeded rather than loading it at runtime.

---

### `tfid-sdo.json` — Sales Demo Org (SDO) Template

```
CCI alias: tfid-sdo
Template:  0TTKX000001hyCa
Instance:  USA794 (SB0)
```

**Use when:** Creating Sales Demo Org (SDO) Trialforce-based orgs. SDOs are demo environments used by the Salesforce field organization for customer-facing demonstrations.

---

### `tfid-sdo-lite.json` — Sales Demo Org Lite Template

```
CCI alias: tfid-sdo-lite
Template:  0TTKX000001Cy9N
Instance:  USA794 (SB0)
```

**Use when:** Creating a lightweight Sales Demo Org (SDO Lite). A smaller/faster-to-provision variant of the full SDO template — use when you need a demo-ready org but don't need the complete SDO feature set or when provisioning speed matters.

---

## Quick Selection Guide

| Goal | Use |
|------|-----|
| Day-to-day feature development | `dev` |
| UX assembly / drift workflows | `dev-sb0` |
| Feature needs enterprise edition | `dev-enhanced` |
| Data Cloud / CDP integration work | `dev-datacloud` |
| Test against next Salesforce release | `dev_preview` |
| Test against prior Salesforce release | `dev_previous` |
| CI pipeline — feature branch | `feature` |
| CI pipeline — beta / integration | `beta` |
| CI pipeline — release candidate | `release` |
| Enterprise org, no instance pin | `ent` |
| Enterprise testing on SB0 | `ent-sb0` |
| Enterprise testing on R1 | `ent-r1` |
| Developer org on SB0 | `dev-sb0` |
| Developer org on R1 | `dev-r1` |
| Automated Robot tests on SB0 | `test-sb0` |
| Trialforce org from base template | `tfid` |
| Trialforce org — CDO | `tfid-cdo` |
| Trialforce org — CDO + RLM combined | `tfid-cdo-rlm` |
| Trialforce org — Developer Edition | `tfid-dev` |
| Trialforce org — Enablement flow | `tfid-enable` |
| IDO Tech org on SB0 | `tfid-ido-tech` |
| IDO Tech org on R2/NA234 | `tfid-ido-tech-R2` |
| QuantumBit TSO Trialforce | `tfid-qb-tso` |
| Sales Demo Org | `tfid-sdo` |
| Sales Demo Org (lightweight) | `tfid-sdo-lite` |

---

## Creating a Scratch Org

```bash
# Create a scratch org and run the full build
cci org scratch <config> <alias> --default
cci flow run prepare_rlm_org --org <alias>

# Examples
cci org scratch dev my-dev --default
cci org scratch dev-sb0 ux-work --default
cci org scratch beta ci-test --default
cci org scratch tfid tfid-test --default   # add tso: true flag for TSO setup

# Open in browser
cci org browser <alias>

# Delete when done
cci org scratch_delete <alias>
```

> See `docs/guides/prepare-rlm-org-build-guide.md` for a full walkthrough of the `prepare_rlm_org` flow and its feature flags.
