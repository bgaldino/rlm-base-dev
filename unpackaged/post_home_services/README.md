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

## Runtime gating: Hierarchy custom setting

All Home Services automation (6 flows, 2 triggers) is gated by the
`RLM_HomeServices_Settings__c.RLM_Enabled__c` Hierarchy custom setting. The
field's `defaultValue` is `true`, so automation is active immediately on
deploy — no seed data or org-default record is required.

To disable: set the org-default record's `RLM_Enabled__c` to `false` (or
per-profile/user via the Hierarchy). A toggle card on the app homepage
("Required Demo Setup" tab) provides a one-click UI for this.

Flows use a `$Setup.RLM_HomeServices_Settings__c.RLM_Enabled__c` Decision
node (not start-element filters, which don't support `$Setup`). Triggers
call `RLM_HomeServices_Settings__c.getOrgDefaults().RLM_Enabled__c` as an
early-return guard.

## Design decision: StandardValueSets excluded

The Home Services source content uses several `AccountSource`, `LeadSource`,
`Industry`, and `Opportunity.Type` values absent from a stock org. These are
org-wide additions with no way to scope them to a single app. Rather than
leak Home-Services-specific dropdown values into the main QuantumBit demo,
this bundle **excludes the StandardValueSet additions entirely**.

The four excluded files are backed up at `unpackaged/_deferred_home_services/`
(a sibling directory outside the deploy root). `OpportunityStage` remains in
`standardValueSets/` — its added values (`New Inquiry`, `On-site Assessment`,
`Proposal/Quote`) are clearly HS-scoped by name and don't conflict with QB
stages.
