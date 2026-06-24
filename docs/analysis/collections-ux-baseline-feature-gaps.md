# Collections UX — baseline feature gaps (investigation)

Status: **open investigation** — two collections record-page components were
removed to unblock the first standard (non-TSO) foundation build with
`collections: true`. Both need a follow-up decision (enable the feature in the
foundation scratch def, gate behind an edition/`tso` patch, or leave removed).

## Context

The `collections` tier had never been built in a standard foundation scratch org
before (it defaults to `collections: false`, and the collections-variant
flexipages only assemble when the flag is on). The first such build
(`prepare_rlm_org` on `resyncbilling2`) failed at `prepare_ux.assemble_and_deploy_ux`
because the collections record pages embed components that depend on features not
enabled in a baseline foundation org. These pages were authored against a
feature-rich source org.

After removing the two components below, the UX deploy succeeds
(113 components, status=Succeeded) on a standard build.

## Gap 1 — `forceKnowledge:articleSearchDesktop` (Salesforce Knowledge)

- **Error:** `Your org doesn't have access to component forceKnowledge:articleSearchDesktop.`
- **Pages:** `RLM_Collection_Plan_Record_Page`, `RLM_Billing_Account_Record_Page`
  (collections standalone variants).
- **Cause:** Salesforce Knowledge is not enabled in the foundation scratch
  definition (`config/project-scratch-def.json` / `orgs/*.json`).
- **Action taken:** removed the component (kept the surrounding region content —
  the Create Late Fee flow on Collection Plan, the activity panel on Billing
  Account).
- **To investigate:** should Knowledge be a foundation feature (add to the
  scratch `features` + the relevant permission set), or is the article-search
  sidebar TSO/edition-specific and better gated via a `tso` patch (like the
  billing-dispute components in `templates/flexipages/patches/tso/`)?

## Gap 2 — `Refunds` related list on Account

- **Error:** `Component [force:relatedListSingleContainer] attribute [relatedListApiName]: Could not find related list [Refunds] for entity [Account].`
- **Page:** `RLM_Collections_Account_Record_Page` (new in this branch); the
  related list lived in a "Refunds" tab. The template originally referenced a
  stale relationship name `AARAccounts` (carried over from the source org); that
  was corrected to `Refunds`, which is the real Account→Refund child relationship.
- **Cause (open):** `Refund.AccountId → Account` exists and the child
  relationship `Refunds` is present in the Account describe, yet the related list
  is not resolvable at flexipage-deploy time in a baseline org. By contrast the
  `Payments` related list (Account→Payment, same payments domain) **is** used in
  other flexipages and validates fine in the same build. No explicit
  Payments/Refund feature appears in the scratch `features` list, so the
  differentiator between Payment (works) and Refund (doesn't) is unknown.
- **Action taken:** removed the "Refunds" tab (facet + tabset nav entry) for now.
- **Expected:** Refunds should be available in the base with the existing scratch
  feature configuration — if it isn't, find out why.
- **To investigate:**
  - Why is the `Payments` related list registered/available but `Refunds` is not,
    given both child relationships exist? Compare object setup, permission sets,
    and any feature/license gating between `Payment` and `Refund`.
  - Confirm the correct `relatedListApiName` for the Refund related list on
    Account (verify it is `Refunds`).
  - Once resolved, restore the Refunds tab to
    `templates/flexipages/standalone/collections/RLM_Collections_Account_Record_Page.flexipage-meta.xml`.

## Verification

- Standard build (`collections: true`) UX assembly + deploy to `resyncbilling2`:
  `Deployment succeeded: 113 component(s) deployed (status=Succeeded)` after the
  two removals.
