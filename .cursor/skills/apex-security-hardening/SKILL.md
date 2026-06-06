# Apex Security Hardening — USER_MODE / CRUD-FLS + Permission-Set Self-Sufficiency

> Canonical workflow for making Apex (and the permission set that backs it)
> enforce the caller's CRUD/FLS, and for proving the feature's permission set
> grants **exactly** what the user-mode code needs — no more, no less. This is
> the single highest-value preparation for the Salesforce audit that `main`
> mirrors through.
>
> Complements the Cursor reminder `.cursor/rules/apex-classes.mdc` (a file-pattern
> nudge); this skill is the canonical detailed procedure. For placement of new
> Apex, see `repo-integration/SKILL.md`.

## Quick Rules

1. **Every** SOQL reachable from an `@AuraEnabled`, `@InvocableMethod`, VF
   controller, or `webservice` entry uses `WITH USER_MODE`. **Every**
   record-mutating DML uses `as user` (or `Database.*(…, AccessLevel.USER_MODE)`).
2. Validate ids at entry: `Id oid = Id.valueOf(param);` (typed `Id`, not `String`);
   helper signatures take `Id`, not `String`.
3. The feature's permission set must be **self-sufficient**: it grants exactly the
   object CRUD + field FLS the user-mode code touches — least privilege, no over-grants.
4. Derive the grant set **from the code, not by guessing**: enumerate every
   user-mode object and every *permissionable* field selected/written, then grant
   precisely those.
5. After deploy, **read the perm set back from the org** and confirm file == org.
   Silent drops are real (see master-detail below).
6. System-mode SOQL is not a shortcut — an auditor flags any system-mode query in a
   user-facing controller. Convert it, or document a concrete reason it must stay system-mode.
7. Tests run as admin and do **not** exercise FLS — a green suite does not prove the
   perm set is sufficient. Confirm with `System.runAs` or a non-admin persona walk.

## DO NOT

- **DO NOT** reference a feature-gated custom field/component in always-on metadata
  (base layouts, base flexipages, base profiles, the assembled `post_ux`). It deploys
  for flag-off builds and breaks when the field/component was never deployed. Put it in
  the feature's patch path (`templates/.../patches/<feature>/`). See
  `repo-integration/ux-assembly-retrieve.md`.
- **DO NOT** assume `describe.permissionable == true` means the field is FLS-settable in
  a permission set. Standard **compound-address components** (`BillingStreet`,
  `ShippingCountry`, …) report `permissionable=true` but **reject** perm-set
  `fieldPermissions` ("Invalid field permission field name") — object read covers them.
- **DO NOT** grant object permissions on **master-detail children** — their CRUD is
  controlled by the master and the platform **silently drops** the child object perms on
  deploy (deploy "succeeds" but the perms never persist). Grant the master instead
  (e.g. `Quote R/E` covers `QuoteLineItem`/`QuoteLineGroup` create/edit/delete; `OrderItem`
  follows `Order`).
- **DO NOT** trust `Schema.SObjectType.X.fields.getMap()` keys to preserve casing — they
  are **lowercase**. Compare with `apiName.toLowerCase()`.
- **DO NOT** leave a perm-set object/field grant that no user-mode code path needs — an
  audit's least-privilege lens flags over-grants too. (A field touched only in a
  *system-mode* query does not need FLS.)

## Entry Conditions

| Situation | Use this skill? |
|-----------|-----------------|
| Hardening an existing Apex feature's CRUD/FLS for the audit | Yes |
| Adding a new `@AuraEnabled`/`@InvocableMethod` controller | Yes — bake USER_MODE + perm-set in from the start |
| Reviewing a PR that touches controllers/permission sets | Yes — pair with `audit-review/SKILL.md` |
| Placing new Apex / deciding force-app vs unpackaged | No — see `repo-integration/SKILL.md` |
| force-app profile rules (classAccesses-only) | See `AGENTS.md` "Profile/object rules" |

## The hardening pass (step by step)

**1. Convert the code.** Add `WITH USER_MODE` to every static `[SELECT …]` (after the
`WHERE`, before `GROUP BY`/`ORDER BY`/`LIMIT`) and to dynamic query strings; change DML
to `insert/update/delete as user`. Find what's still system-mode:

```python
import re
for f in ["path/to/Controller.cls"]:
    src = open(f).read()
    for m in re.finditer(r'\[\s*(SELECT\b.*?)\]', src, re.IGNORECASE|re.DOTALL):
        if not re.search(r'WITH\s+USER_MODE', m.group(1), re.I):
            ln = src[:m.start()].count('\n')+1
            fm = re.search(r'FROM\s+([A-Za-z_]+)', m.group(1), re.I)
            print(f"{f}:{ln} SYSTEM  FROM {fm.group(1) if fm else '?'}")
```

**2. Enumerate the user-mode surface.** For every user-mode query/DML, record the object
and the fields selected/written (own fields + relationship traversals like `Product2.Name`).

**3. Cross-check permissionability** — only *permissionable* fields need explicit FLS;
non-permissionable standard fields (Name, lookups, Quantity, address components) are
covered by object access:

```python
import json, subprocess
d = json.loads(subprocess.run(["sf","sobject","describe","-s","Quote","--target-org",ORG,"--json"],
                               capture_output=True,text=True).stdout)
perm = {fld['name'] for fld in d['result']['fields'] if fld.get('permissionable')}
```

**4. Build the perm set** — `objectPermissions` for each user-mode object (least CRUD it
needs) + `fieldPermissions` for each permissionable field. `editable=true` only where the
code writes the field; otherwise read-only.

**5. Resolve dependency chains** (deploy iteratively — the error tells you the next one):
`Read Quote depends on Read Opportunity`; `Delete <obj> depends on Edit <obj>`.

**6. Read back + verify self-sufficiency** — confirm the org persisted what the file
declares (catches silent master-detail/compound drops):

```bash
sf data query --target-org $ORG -q "SELECT SobjectType, PermissionsRead, PermissionsCreate, PermissionsEdit, PermissionsDelete FROM ObjectPermissions WHERE ParentId IN (SELECT Id FROM PermissionSet WHERE Name='<PermSet>')"
sf data query --target-org $ORG -q "SELECT Field, PermissionsRead, PermissionsEdit FROM FieldPermissions WHERE ParentId IN (SELECT Id FROM PermissionSet WHERE Name='<PermSet>')"
```

**7. Persona/runAs verification (the real proof).** Tests run as admin and bypass FLS.
Assign *only* the perm set (+ a minimal profile that carries the feature's Permission
Set License) to a user and walk the flows, or write a `System.runAs` test. Note: the
PSL/feature-license dimension is orthogonal to the perm set — a Minimum-Access user may
lack the license entirely, producing false negatives.

## The gotchas table (hard-won)

| Symptom on deploy / runtime | Cause | Fix |
|---|---|---|
| `Invalid field permission field name … Account.ShippingCountry` | Standard compound-address component; not perm-set-FLS-settable | Drop the FLS row; object read covers it |
| Deploy "succeeds" but object perm not in org read-back | Master-detail child (CRUD parent-controlled) | Grant the master object; omit the child |
| `Permission Read X depends on permission(s): Read Y` | Object-perm dependency chain | Add the dependency (read/edit) |
| `Delete X depends on Edit X` | Delete requires Edit | Set `allowEdit=true` on X |
| Field-presence check always false for mixed-case API name | `getMap()` keys are lowercase | Compare `apiName.toLowerCase()` |
| A "priced/ready" signal is null even on success | Field not stamped on that path (e.g. `LastPricedDate`) | Gate on the field the platform actually checks (e.g. `ValidationResult==null`), not a proxy |

## Examples

- `unpackaged/post_large_stx/permissionsets/RLM_LargeSalesTransaction.permissionset-meta.xml`
  — built by this exact pass: object CRUD for Order/Quote (R/E) + Opportunity (read
  dependency) + read-only refs (BillingTreatment, Product2, AsyncOperationTracker,
  RevenueTransactionErrorLog, Account, Contact, TransactionProcessingType); FLS only on
  permissionable user-mode fields; master-detail children (QuoteLineItem/QuoteLineGroup)
  omitted and covered by Quote; Account address components omitted (object read).
- `unpackaged/post_large_stx/classes/RLM_PreProcessOrderController.cls` /
  `RLM_SetUpQuoteInvocable.cls` — all entry-reachable SOQL in `WITH USER_MODE`, DML `as user`.

## Validation Checks

- Run the step-1 parser → **zero** system-mode static queries in the controllers.
- `sf project deploy start` the perm set → clean (dependencies resolved).
- Read-back query → org object/field perms == the perm-set file (no silent drops).
- `sf apex run test` → green (necessary, not sufficient — admin context).
- Persona walk or `System.runAs` → the perm set is actually sufficient at runtime.
