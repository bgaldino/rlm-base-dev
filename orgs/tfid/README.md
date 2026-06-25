# TFID Org-Shape Templates

This directory holds the scratch-org definition files that point at **Trialforce
(TFID) template snapshots** — pre-built source orgs captured at a known feature/
license/config state. Each `.json` here is a thin pointer of the form:

```json
{ "orgName": "...", "country": "US", "template": "0TT...", "instance": "USA79x" }
```

`template` is the Trialforce source-org ID; `instance` is the pod it lives on. A
scratch org created from one of these inherits the snapshot's licenses,
permissions, enabled features, and (for the richer shapes) seeded data — so the
org *shape* is baked into the template, not driven by a features list.

Each file is wired to a CCI org alias under `orgs:` in `cumulusci.yml` (e.g.
`cci org scratch tfid-qb-tso <name>`).

## Template catalog

| CCI config / file | Template ID | Instance | Role | What it is |
|-------------------|-------------|----------|------|------------|
| `tfid-cdo` (`tfid-cdo.json`) | `0TTKX000001N46s` | USA1016 | future baseline | **Base CDO license template, no modifications.** The *eventual* `tso=true` baseline goal — reached once all the black-tab mods (see `tfid-cdo-rlm`) are folded into the base license shape template. |
| `tfid-cdo-rlm` (`tfid-cdo-rlm.json`) | `0TTWt000000rQ2n` | USA1016 | **`tso=true` baseline (input)** | `tfid-cdo` **plus** minor "black tab" (internal) license and org value/permission adjustments for RLM. **This is the current starting shape that `prepare_rlm_org` builds *onto* when `tso: true`.** |
| `tfid-qb-tso` (`tfid-qb-tso.json`) | `0TTWs000001kiiD` | USA1016 | **`tso=true` output** | TFID of the **fully built QuantumBit (QB) org we release** — captured by cloning an org that `prepare_rlm_org` (tso=true) built successfully and logging that template ID here. *Not* a build input; used for testing and idempotency work (re-running the build against an already-built org). |
| `tfid` (`tfid.json`) | `0TTWs000001w7YP` | USA1016 | _TBD_ | _TBD — to be documented._ |
| `tfid-sdo` (`tfid-sdo.json`) | `0TTKX000001hzYr` | USA1016 | _TBD_ | _TBD — to be documented._ |
| `tfid-sdo-lite` (`tfid-sdo-lite.json`) | `0TTKX000001D0iI` | USA1016 | _TBD_ | _TBD — to be documented._ Note: present as a file but **not** wired as a CCI org config in `cumulusci.yml`. |

### External (non-TFID) build baselines

For external editions the build starts from standard scratch configs, not TFID
snapshots:

| Baseline | Edition | Used for |
|----------|---------|----------|
| `ent-r1` | Enterprise | external Enterprise builds (trials, etc.) |
| `dev-r1` | Developer | external Developer-edition builds (e.g. `pde: true`) |

## The `tso=true` build cycle (input → output)

`tso=true` is the **internal** build path. The direction matters:

1. **Input baseline:** create the scratch org from **`tfid-cdo-rlm`** (today; the
   goal is to graduate to `tfid-cdo` once black-tab mods are in the base license
   shape). This is a *minimal* shape, **not** the fully-built QB org.
2. **Build:** run `cci flow run prepare_rlm_org` with `tso: true`. The flow
   deploys TSO-specific metadata, assigns the TSO PSL/PSG sets (`*_tso_*` anchors
   in `cumulusci.yml`), and skips steps already covered by the path (e.g.
   `enable_timeline`).
3. **Output capture:** once a build succeeds, clone the resulting org and record
   that new template ID in **`tfid-qb-tso.json`**. `tfid-qb-tso` is therefore the
   *product* of a green build, used afterwards for testing and **idempotency**
   work (re-running the build against an already-built org). Never use it as the
   build *input*.

So: **`tfid-cdo-rlm` (in) → prepare_rlm_org [tso=true] → `tfid-qb-tso` (out)**.

## Notes for agents

- **Don't confuse input and output.** A `tso=true` build runs *onto*
  `tfid-cdo-rlm`; `tfid-qb-tso` is the captured result, not a baseline.
- Some collections UX components are gated behind a `tso` patch because the
  baseline foundation shape doesn't provision them — see
  `.agents/artifacts/collections-ux-baseline-feature-gaps.md` (private artifacts repo).
- **External builds** don't use TFID snapshots: Enterprise builds (trials, etc.)
  baseline from `ent-r1`; Developer-edition builds (e.g. `pde: true`) baseline
  from `dev-r1`.
- "Black tab" = Salesforce-internal license/feature toggles layered on top of
  the base CDO template. The long-term goal is to fold these into the base
  license shape so `tfid-cdo` can serve as the build baseline directly.
- Template IDs are environment-specific snapshots and are refreshed per release;
  if a `cci org scratch` call fails with an invalid/expired template, the
  snapshot likely needs to be recaptured and the `template` ID updated here.
