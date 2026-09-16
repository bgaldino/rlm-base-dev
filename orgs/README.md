# Scratch Org Definition Files

Standard scratch-org definitions live here (`orgs/*.json`) and in `orgs/internal/`
for instance-specific shapes. Trialforce template pointers are separate — see
[`orgs/tfid/README.md`](tfid/README.md).

Most files are wired to a CCI org alias under `orgs:` in `cumulusci.yml`
(`cci org scratch <alias> <name>`). Two are not, and are used ad hoc via the
`sf` CLI (`sf org create scratch -f orgs/<file>.json`):

| File | Wired to a CCI alias? |
|------|----------------------|
| `beta.json`, `dev.json`, `ent.json` | Yes (`beta`, `dev`, `ent`) |
| `orgs/internal/*.json` | Yes (`dev-r1`, `dev-sb0`, `ent-r1`, `ent-sb0`, `ent-sdb*`, `ent-datacloud`) |
| `feature.json`, `release.json` | Not under `orgs:` — these are CumulusCI's built-in org names, resolved by convention |
| `dev-mfg.json`, `dev-mfg-previous.json` | **No** — ad hoc only |

## The `release` field — relative to the dev hub, and not pinnable

`dev-mfg-previous.json` is the only definition that sets `release`. It is worth
understanding before you use it, because the value is **relative to whatever
release the dev hub is on**, not a fixed version:

```json
"release": "previous"
```

`ScratchOrgInfo.Release` is a picklist whose only values are **`Current`**,
**`Preview`**, and **`Previous`** (verified by describe against the 264 dev hub
at v68.0). **There is no way to pin a numeric release** — `"release": "260"` is
not expressible, so "make this file explicitly target 260" is not an available
option.

The consequence is that the release this file yields moves every time the dev hub
moves:

| Dev hub release | `release: previous` yields |
|-----------------|---------------------------|
| 262 | 260 |
| **264 (current)** | **262** |

So the file name means "one release behind the hub", which is still accurate — the
assumption that it meant *260 specifically* is what went stale. If you need a
particular older release, the mechanism does not exist; use an existing org on
that release instead.

Read the other direction, this is the **only** way to provision a fresh org on the
prior release. With no 262 dev hub remaining, `release: previous` on the 264 hub is
how a fresh 262 comparison org gets created — which the deferred `erd-data.json`
refresh needs (it requires a fresh 264 org *and* a fresh 262 org to cross-validate;
see `.cursor/skills/schema-validation/SKILL.md`). Keep the mechanism available even
if this particular manufacturing-shaped file is not the right vehicle for it.
