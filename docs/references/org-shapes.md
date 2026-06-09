# Org Shapes Reference

Scratch org definition files live in `orgs/` and its subdirectories.
Every entry in `cumulusci.yml` under `orgs.scratch` maps a CCI alias to one of
these files. Use this reference to pick the right shape before running
`cci org scratch create` or `cci flow run`.

## Directory layout

```
orgs/
├── beta.json          # Enterprise — primary CI/beta-testing shape
├── dev.json           # Developer  — primary day-to-day dev shape
├── ent.json           # Enterprise — general-purpose enterprise shape
├── feature.json       # Enterprise — CCI default feature-branch shape (unregistered)
├── release.json       # Enterprise — CCI default release-branch shape (unregistered)
├── internal/          # Instance-pinned shapes (require access to specific pods)
│   ├── dev-r1.json        — Developer, pinned to R1 preview pod
│   ├── dev-sb0.json       — Developer, pinned to SB0 internal pod
│   ├── ent-datacloud.json — Enterprise + Data Cloud (CDP) integration
│   ├── ent-r1.json        — Enterprise, pinned to R1 preview pod
│   ├── ent-sb0.json       — Enterprise, pinned to SB0 internal pod
│   ├── ent-sdb6.json      — Enterprise, pinned to SDB6 internal pod
│   ├── ent-sdb9.json      — Enterprise, pinned to SDB9 internal pod
│   ├── ent-sdb27.json     — Enterprise, pinned to SDB27 internal pod
│   └── ent-sdb39.json     — Enterprise, pinned to SDB39 internal pod
└── tfid/              # Trialforce template orgs (snapshot-based)
    ├── tfid.json          — Standard RLM Trialforce template
    ├── tfid-cdo.json      — CDO Trialforce template
    ├── tfid-cdo-rlm.json  — CDO + RLM combined Trialforce template
    ├── tfid-qb-tso.json   — QuantumBit TSO Trialforce template
    ├── tfid-sdo.json      — SDO (Salesforce Demo Org) Trialforce template
    └── tfid-sdo-lite.json — SDO Lite Trialforce template (unregistered)
```

---

## Quick selection guide

| Goal | Use this alias |
|------|---------------|
| Day-to-day feature development | `dev` |
| Pre-merge / CI validation on a feature branch | `dev` |
| Enterprise edition testing (Orders, PRM, Sales Cloud) | `ent` |
| Pre-release branch testing (before `main`) | `beta` |
| Data Cloud + RLM integration work | `ent-datacloud` |
| Testing against the next Salesforce release (R1 preview) | `dev-r1` or `ent-r1` |
| Reproducing an issue on SB0 internal infra | `dev-sb0` or `ent-sb0` |
| Reproducing an issue on a specific internal SDB pod | `ent-sdb6/9/27/39` |
| Demo org from a known Trialforce snapshot | `tfid`, `tfid-sdo`, etc. |

---

## Standard scratch orgs (no instance pin)

These shapes create orgs on any available Salesforce infrastructure pod
and are the right choice for most development work.

### `dev`

| Property | Value |
|----------|-------|
| **File** | `orgs/dev.json` |
| **CCI alias** | `dev` |
| **Edition** | Developer |
| **Instance pin** | None |

**Purpose:** Primary shape for day-to-day development and feature-branch CI.
Developer edition is cheaper (lower API and data limits) but has slightly
reduced capabilities: notably no `SalesCloudEinstein` feature compared with
the Enterprise shapes.

**Distinctive settings:** Full RLM feature set — Billing, CPQ, Order Management,
OmniStudio, Pricing Waterfall, Revenue Management, Agent Platform, PRM, B2B
Commerce, Contract AI.

**When to use:** All standard development work, CCI flow validation, unit test
runs. Pick `ent` only when you specifically need Sales Cloud Einstein or
another Enterprise-only behaviour.

```bash
cci org scratch create dev --org dev
cci flow run prepare_rlm_org --org dev
```

---

### `beta`

| Property | Value |
|----------|-------|
| **File** | `orgs/beta.json` |
| **CCI alias** | `beta` |
| **Edition** | Enterprise |
| **Instance pin** | None |

**Purpose:** Pre-release testing shape. Semantically paired with `main`-branch
work and beta-build automation. Enterprise edition with `SalesCloudEinstein`
enabled.

**Differences from `dev`:** `edition: enterprise`, adds `SalesCloudEinstein`
feature.

**When to use:** Integration tests before merging to `main`, end-to-end validation
of release candidates, running the full `prepare_rlm_org` flow against an
enterprise org.

```bash
cci org scratch create beta --org beta
cci task run insert_quantumbit_pricing_data --org beta
```

---

### `ent`

| Property | Value |
|----------|-------|
| **File** | `orgs/ent.json` |
| **CCI alias** | `ent` |
| **Edition** | Enterprise |
| **Instance pin** | None |

**Purpose:** General-purpose enterprise org for testing enterprise-specific
features. Feature set is identical to `beta`; the distinction is semantic —
`ent` is for exploratory/ad-hoc enterprise work, `beta` for release-validation
workflows.

**When to use:** Enterprise-edition behaviour testing (Orders, PRM, Sales Cloud
Einstein) outside of a formal release cycle. Also the shape to reach for when
you need a quick enterprise scratch org without the beta-release connotations.

```bash
cci org scratch create ent --org ent
```

---

## Instance-pinned orgs (`orgs/internal/`)

These shapes add an `"instance"` field that directs Salesforce to provision
the scratch org on a specific infrastructure pod. They are primarily used by
the Salesforce internal engineering team to reproduce pod-specific issues or
to align scratch orgs with a particular release track.

> **Note:** Access to internal pods (SDB*, USA1016, USA796) requires Salesforce
> internal org permissions. External contributors should use the un-pinned shapes.

### Instance legend

| Instance value | What it means |
|---------------|---------------|
| `USA1016` | R1 — Release 1 preview track (next Salesforce release) |
| `USA796` | SB0 — Internal Salesforce sandbox pod (Sandbox 0) |
| `SDB6` | Internal Salesforce Development Box pod 6 |
| `SDB9` | Internal Salesforce Development Box pod 9 |
| `SDB27` | Internal Salesforce Development Box pod 27 |
| `SDB39` | Internal Salesforce Development Box pod 39 |

---

### `dev-r1`

| Property | Value |
|----------|-------|
| **File** | `orgs/internal/dev-r1.json` |
| **CCI alias** | `dev-r1` |
| **Edition** | Developer |
| **Instance pin** | `USA1016` (R1 preview) |

**Purpose:** Developer edition org pinned to the R1 preview pod. Use this to
validate that RLM flows work correctly against the upcoming Salesforce release
before it reaches GA.

**When to use:** Pre-release compatibility testing, API v67+ feature validation
on the next release track.

```bash
cci org scratch create dev-r1 --org dev-r1
```

---

### `dev-sb0`

| Property | Value |
|----------|-------|
| **File** | `orgs/internal/dev-sb0.json` |
| **CCI alias** | `dev-sb0` |
| **Edition** | Developer |
| **Instance pin** | `USA796` (SB0) |

**Purpose:** Developer edition org pinned to the SB0 internal Salesforce sandbox
pod. Used by internal teams to reproduce or debug issues that are specific to
SB0 infrastructure.

**When to use:** Reproducing SB0-specific bugs, internal dogfooding on SB0 infra.

```bash
cci org scratch create dev-sb0 --org dev-sb0
```

---

### `ent-r1`

| Property | Value |
|----------|-------|
| **File** | `orgs/internal/ent-r1.json` |
| **CCI alias** | `ent-r1` |
| **Edition** | Enterprise |
| **Instance pin** | `USA1016` (R1 preview) |

**Purpose:** Enterprise edition org on the R1 preview pod. Combines the full
enterprise feature set with next-release infrastructure.

**When to use:** Enterprise-specific pre-release compatibility testing, R1 release
readiness validation with Orders, PRM, and Sales Cloud Einstein enabled.

```bash
cci org scratch create ent-r1 --org ent-r1
```

---

### `ent-sb0`

| Property | Value |
|----------|-------|
| **File** | `orgs/internal/ent-sb0.json` |
| **CCI alias** | `ent-sb0` |
| **Edition** | Enterprise |
| **Instance pin** | `USA796` (SB0) |

**Purpose:** Enterprise edition org pinned to SB0. Used when an issue is
reproducible only on SB0 and requires enterprise capabilities.

**When to use:** SB0-specific enterprise bug reproduction and internal team
workflows on SB0.

```bash
cci org scratch create ent-sb0 --org ent-sb0
```

---

### `ent-sdb6`, `ent-sdb9`, `ent-sdb27`, `ent-sdb39`

| Property | Value |
|----------|-------|
| **Files** | `orgs/internal/ent-sdb{6,9,27,39}.json` |
| **CCI aliases** | `ent-sdb6`, `ent-sdb9`, `ent-sdb27`, `ent-sdb39` |
| **Edition** | Enterprise |
| **Instance pins** | `SDB6`, `SDB9`, `SDB27`, `SDB39` respectively |

**Purpose:** Enterprise edition orgs pinned to specific Salesforce internal
Development Box (SDB) pods. These are used by the Salesforce internal engineering
team when testing or debugging behaviour on a specific SDB pod, or when an issue
has been triaged to a particular pod.

Feature set is identical to `ent.json` — only the `"instance"` field differs.

**When to use:** Pod-specific issue reproduction on SDB infrastructure. Each
alias maps to a different pod; choose the one that matches the target environment.

```bash
cci org scratch create ent-sdb27 --org ent-sdb27
```

---

### `ent-datacloud`

| Property | Value |
|----------|-------|
| **File** | `orgs/internal/ent-datacloud.json` |
| **CCI alias** | `ent-datacloud` |
| **Edition** | Enterprise |
| **Instance pin** | None |

**Purpose:** Enterprise org with Salesforce Data Cloud (CDP) enabled for
RLM + Data Cloud integration testing. This is the only shape that includes the
`CustomerDataPlatform` and `CustomerDataPlatformLite` features.

**Distinctive differences from `ent`:**
- Features added: `CustomerDataPlatform`, `CustomerDataPlatformLite`
- Settings added: `customerDataPlatformSettings.enableCustomerDataPlatform: true`
- Settings omitted (not compatible with CDP scratch orgs): `agentPlatformSettings`,
  `einsteinGptSettings`, `industriesSettings`, `omniStudioSettings`

**When to use:** Testing Data Cloud + Revenue Cloud integration scenarios,
validating customer data unification with RLM billing and subscription data.

```bash
cci org scratch create ent-datacloud --org ent-datacloud
```

---

## Trialforce template orgs (`orgs/tfid/`)

Trialforce (TFID) orgs spin up from a pre-configured org snapshot rather than
from a feature/settings list. They contain fully loaded demo data, installed
packages, and preconfigured customizations. Because they reference a live
template (`0TT...` ID), the resulting org mirrors whatever state the source
org was in when the template was last published.

> **Note:** TFID orgs require access to the Trialforce source org. Template IDs
> must be refreshed when the source org is updated. The instance pin routes
> the provisioning request to the same pod as the source.

### `tfid`

| Property | Value |
|----------|-------|
| **File** | `orgs/tfid/tfid.json` |
| **CCI alias** | `tfid` |
| **Template ID** | `0TTWs000001w7YP` |
| **Instance pin** | `USA796` (SB0) |

**Purpose:** Standard RLM Trialforce template. The baseline demo/test org for
Revenue Cloud scenarios. Pre-loaded with RLM configuration, products, and demo
accounts.

**When to use:** Demo preparation, enablement exercises, customer-facing sandbox
environments, scenarios that need a fully provisioned RLM org without running
`prepare_rlm_org` from scratch.

```bash
cci org scratch create tfid --org tfid
```

---

### `tfid-cdo`

| Property | Value |
|----------|-------|
| **File** | `orgs/tfid/tfid-cdo.json` |
| **CCI alias** | `tfid-cdo` |
| **Template ID** | `0TTKX000001N3pi` |
| **Instance pin** | `USA796` (SB0) |

**Purpose:** Trialforce template for CDO (Customer Data Organization) scenarios.
Provisions an org pre-configured with CDO setup alongside RLM.

**When to use:** Testing or demonstrating CDO-related RLM workflows.

---

### `tfid-cdo-rlm`

| Property | Value |
|----------|-------|
| **File** | `orgs/tfid/tfid-cdo-rlm.json` |
| **CCI alias** | `tfid-cdo-rlm` |
| **Template ID** | `0TTWt000000oJCL` |
| **Instance pin** | `USA796` (SB0) |

**Purpose:** Combined CDO + RLM Trialforce template. Provisions an org with both
CDO and Revenue Cloud fully configured from a shared snapshot.

**When to use:** Integrated CDO + RLM demos and testing where both platforms need
to be preconfigured simultaneously.

---

### `tfid-qb-tso`

| Property | Value |
|----------|-------|
| **File** | `orgs/tfid/tfid-qb-tso.json` |
| **CCI alias** | `tfid-qb-tso` |
| **Template ID** | `0TTWs000001kiiD` |
| **Instance pin** | `USA794` |

**Purpose:** QuantumBit TSO (Technical Support Org) Trialforce template. Provisions
an org pre-loaded with the QuantumBit demo scenario data (Infinitech/Global Media
accounts, QB products, SKUs) for technical support and partner enablement use.

**When to use:** QB demo script walkthroughs, TSO-based support cases, partner
enablement exercises that require the full QuantumBit scenario pre-loaded.

---

### `tfid-sdo`

| Property | Value |
|----------|-------|
| **File** | `orgs/tfid/tfid-sdo.json` |
| **CCI alias** | `tfid-sdo` |
| **Template ID** | `0TTKX000001hyCa` |
| **Instance pin** | `USA794` |

**Purpose:** SDO (Salesforce Demo Org) Trialforce template. Provisions an org from
the standard Salesforce Demo Org snapshot with RLM configured for AE/SE-facing demos.

**When to use:** Sales Engineering demos, AE-led customer walkthroughs, scenarios
requiring the SDO base configuration.

---

## Unregistered org shapes

These files exist in `orgs/` but are **not registered** in `cumulusci.yml`.
They cannot be used with `cci org scratch create <alias>` without first adding
an entry to `cumulusci.yml`.

### `feature` and `release`

| File | Edition | Notes |
|------|---------|-------|
| `orgs/feature.json` | Enterprise | Identical feature set to `ent.json` |
| `orgs/release.json` | Enterprise | Identical feature set to `ent.json` |

These correspond to CCI's conventional `feature` and `release` org names used in
automated release pipelines. They are not currently wired into `cumulusci.yml`
but are kept on-disk so they can be registered if CCI automated release flows are
added in the future.

### `tfid-sdo-lite`

| File | Template ID | Instance |
|------|------------|---------|
| `orgs/tfid/tfid-sdo-lite.json` | `0TTKX000001Cy9N` | `USA794` |

A lighter-weight SDO Trialforce template. Not yet registered in `cumulusci.yml`.
To use it, add the following to `cumulusci.yml` under `orgs.scratch`:

```yaml
    tfid-sdo-lite:
      config_file: orgs/tfid/tfid-sdo-lite.json
      days: 30
```

---

## Feature differences at a glance

Most orgs share the same full RLM feature list. The table below calls out
only the differences.

| Shape | Edition | Instance | Unique features / omissions |
|-------|---------|----------|------------------------------|
| `dev` | Developer | — | No `SalesCloudEinstein` |
| `dev-r1` | Developer | USA1016 (R1) | No `SalesCloudEinstein`; R1 preview pod |
| `dev-sb0` | Developer | USA796 (SB0) | No `SalesCloudEinstein`; SB0 pod |
| `beta` | Enterprise | — | Full standard set |
| `ent` | Enterprise | — | Full standard set (identical to `beta`) |
| `ent-r1` | Enterprise | USA1016 (R1) | Full standard set; R1 preview pod |
| `ent-sb0` | Enterprise | USA796 (SB0) | Full standard set; SB0 pod |
| `ent-sdb6` | Enterprise | SDB6 | Full standard set; SDB6 pod |
| `ent-sdb9` | Enterprise | SDB9 | Full standard set; SDB9 pod |
| `ent-sdb27` | Enterprise | SDB27 | Full standard set; SDB27 pod |
| `ent-sdb39` | Enterprise | SDB39 | Full standard set; SDB39 pod |
| `ent-datacloud` | Enterprise | — | Adds `CustomerDataPlatform`, `CustomerDataPlatformLite`; omits OmniStudio, Agent Platform, industriesSettings |
| `tfid*` | Template | USA794/796 | No feature list — spun from org snapshot |
