# TFID Org-Shape Templates

This directory holds the scratch-org definition files that point at **Trialforce
(TFID) template snapshots** of pre-built source orgs, captured at a known feature/
license/config state. Each `.json` here is a thin pointer of the form:

```json
{ "orgName": "...", "country": "US", "template": "0TT...", "instance": "USA1000" }
```

`template` is the Trialforce template ID (`0TT...`) created from the source org;
`instance` is the pod it lives on. A
scratch org created from one of these inherits the snapshot's licenses,
permissions, enabled features, and (for the richer shapes) seeded data — so the
org *shape* is baked into the template, not driven by a features list.

Most files are wired to a CCI org alias under `orgs:` in `cumulusci.yml` (e.g.
`cci org scratch tfid-qb-tso <name>`); the catalog below says which one is not.

## Template catalog

| CCI config / file | Template ID | Instance (file value) | Role | What it is |
|-------------------|-------------|----------|------|------------|
| `tfid-cdo` (`tfid-cdo.json`) | `0TTKX000001N7XD` | USA1000 | **base shape for every internal build (input)** | The base CDO template: all the licenses, org permissions, values and preferences, and the qbranch tooling needed to release through the internal org-request tooling or to a solutions workspace. `prepare_rlm_org` with `tso: true` builds onto it, and `tfid-sdo` and `tfid-sdo-lite` are built on top of it. |
| `tfid-cdo-rlm` (`tfid-cdo-rlm.json`) | `0TTEE000000A3vt` | USA1000 | optional overlay (not currently required) | `tfid-cdo` plus extra "black tab" (internal) licenses and org values, permissions or settings for RLM. Created only when a build needs something the base lacks, mainly to close the feedback loop with qbranch so the change is applied to `tfid-cdo`. Its ID is refreshed only if and when it is needed again; do not build from it by default. |
| `tfid-pde` (`tfid-pde.json`) | `0TTe60000001Zzp` | USA1016 | **Partner Developer Edition (PDE) baseline (input); works, rebuild pending** | TFID snapshot for **Partner Developer Edition** builds (`pde: true`). This is the **PDE license base** (on the R1 pod today; it moves to the R0 pod, USA1000, when rebuilt). Unlike the external `dev-r1` baseline (a standard DE scratch config), this is the TFID-snapshot path for PDE. The template still works but does not include the latest build additions; its source org will be rebuilt on USA1000 and a new TFID created from it. |
| `tfid-qb-tso` (`tfid-qb-tso.json`) | `0TTWs000001kiiD` | USA1000 | **`tso=true` output; the released build** | TFID of the **fully built QuantumBit (QB) org we release**, captured by enabling Trialforce on an org that `prepare_rlm_org` (tso=true) built successfully (or on the production TSO its template was migrated to; see the build cycle below) and logging that template ID here. *Not* a build input; used for testing and idempotency work (re-running the build against an already-built org). The current ID is the released build: it works, but does not include the latest build additions. To update it, the TSO is rebuilt (a new full build from `tfid-cdo`) and a new TFID created from it. |
| `tfid-sdo` (`tfid-sdo.json`) | `0TTjW0000007RMr` | USA1000 | qbranch shape | A qbranch demo-org shape built on `tfid-cdo`. Wired as a CCI org config in `cumulusci.yml`; no task, flow or build flag in this repo references it. |
| `tfid-sdo-lite` (`tfid-sdo-lite.json`) | `0TTKX000001D673` | USA1000 | qbranch shape | The lighter qbranch shape, also built on `tfid-cdo`. Present as a file only: **not** wired as a CCI org config in `cumulusci.yml`, and nothing in this repo references it. |

### Which pod

Use **USA1000** for new templates: it is the R0 pod, where GA TSOs live. The Instance column is the
`instance` value in each file. The `tfid-cdo`, `tfid-sdo` and `tfid-sdo-lite` IDs were refreshed
without re-checking it, and the characters after `0TT` in an ID are not a reliable pod indicator, so
treat those three as unconfirmed. `tfid-pde` (USA1016) moves to USA1000 when it is rebuilt. When an
ID changes, confirm the `instance` value with it.

### Which baseline to build from

| Build | Baseline |
|-------|----------|
| External (trials, partner and customer orgs) | `ent-sb0`, `ent-r0` or `ent-r1`, by the release cluster you need |
| Internal (qbranch and qbrix orgs) | `tfid-cdo` (or `tfid-cdo-rlm`, only while a black-tab addition is pending; refresh its ID first) |
| PDE | `tfid-pde` (a Trialforce snapshot) or the external `dev-r1` standard scratch config |

External builds use standard scratch configs, not TFID snapshots:

| Baseline | Edition | Used for |
|----------|---------|----------|
| `ent-sb0`, `ent-r0`, `ent-r1` | Enterprise | external Enterprise builds (trials, etc.), by release cluster |
| `dev-sb0`, `dev-r0`, `dev-r1` | Developer | external Developer-edition builds, by release cluster |

> **PDE has two baseline paths:** the external standard-scratch `dev-r1` config
> (above) **or** the TFID-snapshot `tfid-pde` shape (in the catalog above). Use
> `tfid-pde` when you need the PDE org to start from a Trialforce snapshot rather
> than a vanilla DE scratch config.

## The `tso=true` build cycle (input → output)

`tso=true` is the **internal** build path. The direction matters:

1. **Input baseline:** create the scratch org from **`tfid-cdo`**. This is the
   base shape (licenses, settings and tooling, but no RLM build), **not** the fully-built QB org.
2. **Build:** run `cci flow run prepare_rlm_org` with `tso: true`. The flow
   deploys TSO-specific metadata, assigns the TSO PSL/PSG sets (`*_tso_*` anchors
   in `cumulusci.yml`), and skips steps the template is expected to cover (e.g.
   `enable_timeline`; whether a `tfid-cdo` org already has Timeline on is unverified).
3. **Output capture:** once a build succeeds, enable Trialforce on that org to
   create a template ID, and record it in **`tfid-qb-tso.json`**. Releasing needs
   a second Trialforce step: the scratch-org template is migrated to a production
   org, which becomes the TSO, and Trialforce is enabled there again for release.
   `tfid-qb-tso` records either the scratch-org template or the production TSO's
   template, depending on the workflow. A stable release always uses the
   **production** TSO's template. `tfid-qb-tso` is the
   *product* of a green build, used afterwards for testing and **idempotency**
   work. Never use it as the build *input*.

So: **`tfid-cdo` (in) → prepare_rlm_org [tso=true] → Trialforce → `tfid-qb-tso` (out)**.

## Notes for agents

- **Don't confuse input and output.** A `tso=true` build runs *onto*
  `tfid-cdo`; `tfid-qb-tso` is the captured result, not a baseline.
- Some collections UX components are gated behind a `tso` patch because the
  baseline foundation shape doesn't provision them — see
  `.agents/artifacts/topics/collections/collections-ux-baseline-feature-gaps.md` (private artifacts repo).
- **External builds** don't use TFID snapshots: they baseline from `ent-sb0`,
  `ent-r0` or `ent-r1` (Developer-edition builds from `dev-sb0`, `dev-r0` or `dev-r1`; PDE's standard-scratch path is `dev-r1`).
  For a TFID-snapshot PDE baseline instead, use `tfid-pde`.
- "Black tab" = Salesforce-internal license/feature toggles layered on top of
  the base CDO template. Additions are tried through `tfid-cdo-rlm` and then
  folded back into `tfid-cdo` by qbranch.
- Template IDs are environment-specific snapshots. Most are refreshed per release
  (`tfid-cdo-rlm` only when it is needed; `tfid-pde` and `tfid-qb-tso` are due for
  a rebuild, see the catalog). If a `cci org scratch` call fails with an invalid/expired template, get a new
  TFID: for `tfid-qb-tso` and `tfid-pde`, rebuild the TSO and create a new TFID from it; for the
  qbranch shapes (`tfid-cdo`, `tfid-sdo`, `tfid-sdo-lite`), get the current ID from qbranch; `tfid-cdo-rlm` is created on request when a
  black-tab addition is needed (see the catalog). Then update `template` (and `instance`) here.
