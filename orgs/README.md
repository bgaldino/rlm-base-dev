# Scratch Org Definition Files

Standard scratch-org definitions live here (`orgs/*.json`) and in `orgs/internal/`
for instance-specific shapes. Trialforce template pointers are separate — see
[`orgs/tfid/README.md`](tfid/README.md).

Most files are wired to a CCI org alias under `orgs:` in `cumulusci.yml`
(`cci org scratch <alias> <name>`). Three are not: `feature.json` and `release.json` (CumulusCI's
built-in org names), and `dev-mfg.json`, which is used ad hoc via the `sf` CLI
(`sf org create scratch -f orgs/<file>.json`):

| File | Wired to a CCI alias? |
|------|----------------------|
| `beta.json`, `dev.json`, `ent.json` | Yes (`beta`, `dev`, `ent`) |
| `orgs/internal/*.json` | Yes (`dev-r0`, `dev-r1`, `dev-sb0`, `ent-r0`, `ent-r1`, `ent-sb0`, `ent-sdb*`, `ent-datacloud`) |
| `feature.json`, `release.json` | Not under `orgs:` — these are CumulusCI's built-in org names, resolved by convention |
| `dev-mfg.json` | **No** — ad hoc only |

## Which shape to use

Most shapes share `ent.json`'s Revenue Cloud settings and differ only in edition, a feature or two,
or a pinned `instance`. Every `orgs/internal/*.json` file except `ent-datacloud` and `ent-sdb39` is
its base file (`ent.json` or `dev.json`) plus `instance`. `ent-datacloud` and `dev-mfg` carry
different *settings*, not just features, so don't treat either as "ent plus a feature". Compare any
two with `diff <(jq -S 'del(.instance)' a.json) <(jq -S 'del(.instance)' b.json)`.

| Shape | Edition | Differs from `ent.json` (ignoring `instance`) | Use it when |
|---|---|---|---|
| `ent` (`ent.json`) | Enterprise | — | The default shape for a full build. |
| `beta`, `feature`, `release` | Enterprise | Nothing: identical | Building under one of those org names. |
| `dev` (`dev.json`) | Developer | Edition; no `SalesCloudEinstein` | You need a Developer Edition org. Builds detect it through `org_config.org_type` (AGENTS.md → PR Review Focus Areas → Edition flags). |
| `ent-r0`, `ent-r1`, `ent-sb0`, `ent-sdb6`, `ent-sdb9`, `ent-sdb27` | Enterprise | Nothing; each pins an `instance` | You need a particular instance, for example one already on the release you're testing. This repo's live verifications are usually built on `ent-sb0`. |
| `ent-sdb39` | Enterprise | Pins an `instance`; adds `LargeTransactionPilot` | Large-deal work. |
| `ent-datacloud` | Enterprise | No `instance`; adds `CustomerDataPlatform`, `CustomerDataPlatformLite` and `customerDataPlatformSettings`; **lacks** `agentPlatformSettings`, `industriesSettings` and `omniStudioSettings` | Data Cloud (Data 360) work. |
| `dev-r0`, `dev-r1`, `dev-sb0` | Developer | As `dev`; each pins an `instance` | The `dev` shape on a particular instance. |
| `dev-mfg` (ad hoc) | Enterprise | A Manufacturing feature set (`IndustriesManufacturing*`, `IndustriesMfgRebates`, `IndustriesMfgTargets`, analytics, AI providers), several `ent` features dropped, `enableOptionalPricebook: true` (`ent` has false), and most `revenueManagementSettings` absent (no group ramp, ramp deals, transaction processor, advanced create-orders-from-quote), plus no agent-platform, industries, OmniStudio, Omni-Channel, forecasting, email-template or security settings | The manufacturing (mfg) work only. |

## The `MaxBundleDepth:5` feature value

Every `features` array in this directory (and `config/project-scratch-def.json`)
carries `MaxBundleDepth:5`. It raises the PCM `MaxBundleDepth` org value from its
scratch-org default of 3 to 5 — the maximum this org value supports — so the
**QuantumBit - OmniRack DC42 Series** bundle's 6-product, 5-link nesting (in
the `qb-pcm` SFDMU plan) loads in full. Without it, 56 of this plan's 234
`ProductRelatedComponent` rows (per the plan's tracked record count — see
`datasets/sfdmu/qb/en-US/qb-pcm/README.md`) fail with
`bundle or set levels would exceed 3`; SFDMU logs the failure and the build
carries on, so the gap is easy to miss. Live-verified against a fresh scratch org
in [PR #516](https://github.com/bgaldino/rlm-base-dev/pull/516) (234/234 rows
loaded, no depth error). `orgs/tfid/*.json` files are template pointers with no
`features` array, so the value does not apply there; see
`.cursor/skills/troubleshooting/SKILL.md` → **SFDMU Data Loading Errors** for the
failure mode and `datasets/sfdmu/qb/en-US/qb-pcm/README.md` for the dataset side.

If you add a new scratch org definition under `orgs/`, carry this value forward —
it has no Setup UI or Metadata API surface, so there is no way to raise it after
the org is built; a persistent org (sandbox, DE) that still needs it requires a
Salesforce Support case, not a repo change.
