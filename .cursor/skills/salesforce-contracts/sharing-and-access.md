# Contract Sharing, Restriction Rules and Access

Read this when someone asks to give contract managers different rights from account
team members, to hide some contracts from some users, or to make a contract read-only
while its account stays editable. Parent: [salesforce-contracts](SKILL.md).

## How Contract sharing behaves on 264

- **Default access follows Account.** `Contract` reads ReadWrite internal and Private external when
  Account does. A Contract-only org-wide-default deploy (`sharingModel` Private, then Read, with Account
  untouched) returned Succeeded and changed nothing; deploying Account `sharingModel` Read moved Contract to
  Read with it, and restoring Account moved it back [Measured: 2026-11-26, 264 (USA796), ent-sb0 harness build].
- **Contract-only sharing rules are refused.** A criteria rule and an owner rule on Contract each failed to
  deploy with "Not available for deploy for this organization." [Measured: same]. The metadata type list
  shows `sharingModel` and `SharingRules` for Contract, but that is schema, not capability: do not treat either
  as proof Contract can be shared on its own.
- **Controls that do work:**
    1. **A permission set with Contract Read-only.** A user with Account Read and Edit and Contract Read-only:
       Account updates succeeded, Contract updates were refused ("DML operation UPDATE not allowed on Contract"),
       Contract was not updateable; a control user with Contract Edit did both. It applies to all contracts, not
       per record. Measured through Apex run as the user with user-mode DML, not the UI [Measured: same].
    2. **A Restriction Rule on Contract** (below).

## Restriction Rules on Contract

A Restriction Rule is an allow-list: a user the rule's user criteria match sees only the records its record
criteria match, while the account stays visible. A user the rule does not match is unaffected.
[Measured: 2026-11-26, 264 (USA796), ent-sb0 harness build]

| Part | What was accepted or refused |
|---|---|
| User criteria | A `$User` field expression, for example `$User.Department = '<value>'`. `Username = ...` was refused |
| Record criteria | A plain text field on Contract (for example `ContractType`) was accepted. A picklist field compared with `=` (`Status`) was refused, with or without `TEXT()`; `ISPICKVAL(Status,'Draft')` was accepted inactive (see below). A compound field (`BillingCity`) was refused |
| Active cap | Enterprise allowed 2 active rules per object. A third active Contract rule failed with `LIMIT_EXCEEDED` ("Maximum limit for active ABAC rules reached") |

Working rule, created through the Tooling API (`POST /services/data/v68.0/tooling/sobjects/RestrictionRule`) and read back unchanged:

```json
{"FullName": "Contract_East_Only",
 "Metadata": {"active": false, "enforcementType": "Restrict", "masterLabel": "Contract East Only",
              "targetEntity": "Contract", "recordFilter": "ContractType = 'East'",
              "userCriteria": "$User.Department = 'Contracts-East'", "version": 1,
              "description": "Contracts-East users see only East contracts"}}
```

Create it inactive, then set `active` to true. Refusals reproduced on this build: a picklist filter (`Status = 'Draft'`) failed with
"Field Status is a picklist field. Picklist fields are only supported in certain functions." and `Username = '...'` as user criteria
failed with "You can't create restriction rules with this user criterion" [Measured: 2026-11-26, 264 (USA796), ent-sb0 harness build].
A matching user saw the one contract of two whose type matched; a user outside the department saw both.
[Help: `ind.sf_contracts_known_limitation_for_salesforce_contracts` says picklist values can be selected in Restriction and
Scoping Rule record criteria, a single value only.] That conflicts with the refused `Status = 'Draft'` filter above. The error
text points to picklist functions, and a rule with `recordFilter` `ISPICKVAL(Status,'Draft')` was accepted when created inactive
[Measured: 2026-11-26, 264 (USA796), ent-sb0 harness build]. [Open: activating that rule and the filtering it gives were not run.]
[Open: the active-rule cap on Performance and Unlimited editions (not testable on an Enterprise org); behavior with
two rules matching one user.]

## When none of these fits

- Confidential contract data that must be private per user: keep it on a custom object or record type with a private default,
  related to Account. The cost is losing standard Contract features and the order and asset linkage [Open: design guidance, not built].
- Blocking edits by profile or status with a validation rule or trigger is not a sharing control: reads stay open [inferred: a validation rule runs on write only].
- Independent Contract default and rules are a platform sharing change, not a repo setting [Open: no platform setting was found in the Help snapshot].
