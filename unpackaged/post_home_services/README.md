# Home Services Demo

The Home Services feature is opt-in through `project.custom.home_services` and
requires `billing_ui`.

The deployment is split into two packages so a fresh org receives Experience
Cloud metadata in dependency order:

1. `unpackaged/post_home_services` deploys application dependencies: fields,
   Apex, LWC, flows, record pages, and the internal-user permission set.
2. `unpackaged/post_home_services_site` deploys the enhanced-LWR
   `DigitalExperienceConfig`, `DigitalExperienceBundle`, `Network`, and
   `CustomSite` after `create_home_services_community` creates the target site.
   It also grants the generated site guest profile access to the public signup
   Apex entry points.

`prepare_home_services` patches target-org-specific immutable Network and
CustomSite values immediately before the site deploy, restores the committed
non-PII placeholders afterward, publishes the community, and assigns
`RLM_HomeServices` to the running user.

Product demo data is intentionally not seeded by this flow. Use the separate
Home Services product workflow packaged in `RLM_HomeServices_Skills`.

## Design decision: AccountSource, LeadSource, Industry, and OpportunityType StandardValueSets excluded

The Home Services source content (the `homeserveSrc` demo org) uses several
`AccountSource`/`LeadSource` values, two `Industry` values, and two
`Opportunity.Type` values that don't exist in a stock org's StandardValueSet.
Deploying them requires adding entries to that StandardValueSet — which is a
single org-wide list. There is no way to scope a StandardValueSet *addition*
to one RecordType: any RecordType without an explicit restriction (including
every QuantumBit `*_Business_*` Master/unrestricted RecordType on Account and
Opportunity) immediately exposes the new dropdown values too. Rather than
leak Home-Services-specific values into every other RecordType on these
shared standard objects, this bundle **excludes the StandardValueSet
additions entirely** and narrows each RecordType's picklist restriction to
only the values already present in a stock org:

- `RLM_HomeServices_Account`: `AccountSource` restriction removed outright
  (was 10 values, all absent from a stock org); `Industry` restriction
  trimmed by 2 (`Financial Services`, `Healthcare & Life Sciences` dropped).
- `RLM_HomeServices_Opportunity`: `LeadSource` restriction removed outright
  (was 10 values, 9 absent from a stock org — `Partner` was the only stock
  value); `Type` restriction trimmed by 2 (`Add-On Business`, `Services`
  dropped, leaving `Existing Business`/`New Business`).

The four excluded StandardValueSet files are backed up at
`unpackaged/_deferred_home_services/` — a sibling directory outside
`post_home_services` (the `sf` CLI's source-to-MDAPI conversion discovers
metadata by file-suffix pattern anywhere under the deploy root regardless of
subfolder name, so a subfolder *inside* `post_home_services` still gets swept
into the deploy). `AccountSource` additionally failed to deploy via MDAPI on
its own (`insert isn't supported for the standard value set AccountSource.`,
reproducible even as a no-op re-deploy of already-present values,
not root-caused) — an independent problem from the leakage concern above, and
moot now that the value set isn't part of the deploy either way.

`OpportunityStage` is unaffected by this decision and remains in
`standardValueSets/` — its 3 added values (`New Inquiry`, `On-site
Assessment`, `Proposal/Quote`) are scoped through
`RLM_HomeServices_OpptyBizProcess`, a dedicated BusinessProcess rather than a
shared object-wide StandardValueSet restriction, so they don't carry the same
cross-RecordType leakage risk.

To restore full fidelity for any of the four excluded fields: move the
relevant file back from `unpackaged/_deferred_home_services/` into
`standardValueSets/`, re-add the dropped values to the corresponding
RecordType's `<picklistValues>` block, and accept that those values become
selectable on every RecordType for that object org-wide.
