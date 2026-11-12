---
name: transaction-line-editor
description: >-
  Configure and use the Revenue Cloud Transaction Line Editor and Sales Transaction Line
  Editor (STLE) on quote and order record pages: display columns, the Adjustment Type
  column, line groups, header action buttons (Reprice All, Create Ramp Schedule, Manage
  Header Adjustment and the rest), Browse Catalogs, Instant Pricing, Transaction Summary auto-refresh,
  configuring a bundle from a line, and what amendment, renewal and cancellation lines show.
  Use when changing the line editor on a page in this repo (templates/flexipages and the UX
  assembler, never unpackaged/post_ux), preparing or debugging a demo in the line editor or
  configurator, or explaining why a line shows blank prices, reset attributes or a doubled
  header discount. Use ramped-quotes for group-ramp builds, pricing-procedures for pricing
  elements, and repo-integration for the assembler itself.
---

# Transaction Line Editor — Configure and Use the Quote and Order Line Editor

The line editor is the grid on a quote or order record page where reps add, configure,
group, discount and price lines. This skill covers how an admin configures it in Lightning
App Builder, how this repo ships that configuration through `templates/flexipages/`, and how
the editor and the configurator behave at run time on 264, including behaviour measured
on demo orgs that the Help does not describe. Any agent can read it; it assumes no org
access.

Two components exist. The **Sales Transaction Line Editor (STLE)** is the one Salesforce
recommends; the older **Transaction Line Editor (TLE)** "remains available" but is "no
longer being enhanced" [Help: `ind.qocal_customize_transaction_line_editor`]. Help uses
"line editor" for both; so does this skill unless a rule applies to only one.

**Source tags.** `[Help: <article>]` is the 264 Help snapshot,
`docs/salesforce/264/help/articles/<article>.htm.md`. `[Dev guide: <article>]` and
`[Release notes: <article>]` are the sibling `dev-guide/` and `release-notes/` snapshots.
`[Repo: <file>]` is this repository. `[Measured: <date>, 264]` is behaviour observed on a 264
demo org; `[Measured: <date>, fresh 264 ent-sb0 scratch org]` on a scratch org freshly built from
this repo with the `ent-sb0` shape. **Open — needs live verification** marks anything only a live org can settle.
Ground new claims with [`revenue-cloud-docs`](../revenue-cloud-docs/SKILL.md).

## Quick Rules

1. **Change the page in `templates/flexipages/`, then assemble.** The quote and order pages are
   `templates/flexipages/base/RLM_Quote_Record_Page.flexipage-meta.xml` and
   `RLM_Order_Record_Page.flexipage-meta.xml`; `unpackaged/post_ux/` is generated output
   (AGENTS.md DO NOT 1) [Repo: `.cursor/skills/repo-integration/ux-assembly-retrieve.md`].
   For a feature-gated column use a patch in `templates/flexipages/patches/<feature>/`:
   `add_sales_txn_line_editor_field`, or the older `add_display_field`, which appends to the page's
   first `displayFields` list (see [`page-configuration.md`](page-configuration.md)).
2. **Use the STLE.** Group ramps and *Instant Pricing Active by Default* work only in the STLE
   [Help: `ind.qocal_set_up_ramp_deals_for_groups`, `ind.qocal_turn_on_quote_and_order_capture`].
   Both repo pages use the `runtime_rca:salesTxnLineTable` component [Repo: both page templates].
3. **Add every custom column field to the sales transaction context definition.** Without it,
   edits to that field in the editor are not saved [Help: `ind.qocal_select_fields_for_the_line_editor`].
   Use [`context-service`](../context-service/SKILL.md).
4. **Put only editable currency or percent fields in the Adjustment Type column.** A read-only or
   calculated field causes pricing errors; Start Date or End Date can reset ramped line dates
   [Help: `ind.qocal_adjustment_type_column`].
5. **Reprice after anything that changed lines outside the editor.** API, Process Builder,
   trigger and manual field updates invalidate the pricing status and need Reprice All [Help: `ind.qocal_limitations_for_using_quote_and_order_capture`].
   A header-only Place PATCH, even of a field pricing reads, left the line prices unchanged until
   Reprice All [Measured: 2026-11-11, fresh 264 `ent-sb0` scratch org]. Under System pricing only a request
   that includes a line (or line attribute) record reprices; Reprice All uses Force pricing
   [Platform behaviour, traced].
   Reprice All re-runs pricing only; Refresh Prices also re-runs configuration and taxes
   [Help: `ind.qocal_reprice_all_quotes_and_orders`, `ind.qocal_view_and_edit_quotes`].
6. **Don't demo an inline quantity edit on an amendment of a configured product.** With
   configuration rules on it resets the line's attributes to product defaults, and activation
   keeps them on the asset [Measured: early Nov 2026, 264]. Change the quantity in the configurator.
7. **Header adjustments depend on the Discount Distribution Service (DDS) element; make sure only
   one DDS runs per pricing pass.** Help's setup puts a DDS element in the pricing procedure;
   the rep picks the type, value and distribution in Manage Header Adjustment, and pricing spreads
   it across the lines [Help: `ind.qocal_header_adjustments_overview`, `ind.qocal_header_adjustments_use`].
   Help allows one DDS per pricing procedure [Help: `ind.pricing_discount_distribution_service_limits`];
   the one-per-pass rule is this skill's conclusion from the doubling below. The repo's `RLM_DefaultPricingProcedure` has a DDS step, and so does `RLM_Price_Distribution_Procedure`,
   which the procedure plan runs. With the plan active and `skipOrgSttPricing` on, both ran and a 10%
   header discount came out at 19% [Measured: early Nov 2026, 264; Repo: `datasets/sfdmu/procedure-plans/README.md`].
   Keep the plan inactive (the repo default) for header-adjustment demos.

## DO NOT

- **DO NOT** edit `unpackaged/post_ux/flexipages/RLM_Quote_Record_Page.flexipage-meta.xml` or the
  order page by hand; edit the template and run the assembler (AGENTS.md DO NOT 1).
- **DO NOT** reference a feature-gated custom field in the base page template's line editor
  columns. Base output deploys on every build and breaks deploy where the field doesn't exist;
  use that feature's patch file [Repo: `.cursor/skills/repo-integration/ux-assembly-retrieve.md`].
- **DO NOT** add read-only, formula or calculated fields (for example Total Adjustment) to the
  Adjustment Type column [Help: `ind.qocal_adjustment_type_column`].
- **DO NOT** edit Net Unit Price, Net Total Price, Total Adjustment Amount or Pricing Term Count
  in the editor when Salesforce Pricing is active [Help: `ind.qocal_view_and_edit_quotes`].
- **DO NOT** add or edit lines with the standard Quote Line Items or Order Products related-list
  buttons; Revenue Management doesn't support them [Help: `ind.qocal_discover_and_configure_products`].
- **DO NOT** expect admin-created custom actions in the header action picker; only built-in
  actions are available [Help: `ind.qocal_action_button_group_important_considerations`].
- **DO NOT** update `Calculation Status` by hand to unstick a transaction left in *Saving* while
  another recovery exists; retry with the Place Sales Transaction API. Help recommends a manual
  update only as a last resort, with the Edit Calculation Status on Quote and Order permission
  [Help: `ind.qocal_differences_between_calculation_status_field_and_validation_result_field`].
- **DO NOT** read a blank Sales Price or Net Unit Price on an amended parent line as a pricing
  failure until you check its detail rows and the line total (see [`runtime-behavior.md`](runtime-behavior.md)).

## Entry Conditions

| Task | Use this skill? | Instead / also |
|------|-----------------|----------------|
| Add, remove or reorder line editor columns, side panel or ramp-detail fields | Yes | [`page-configuration.md`](page-configuration.md); assembler mechanics in [`repo-integration`](../repo-integration/SKILL.md) |
| Arrange header action buttons or button groups | Yes | [`page-configuration.md`](page-configuration.md) |
| Turn on STLE and Transaction Summary auto-refresh | Yes | [`page-configuration.md`](page-configuration.md) |
| Rehearse or debug a demo in the editor or configurator | Yes | [`runtime-behavior.md`](runtime-behavior.md); click paths in [`qb-demo-script`](../qb-demo-script/SKILL.md) |
| Explain amendment, renewal or cancellation line display | Yes | [`runtime-behavior.md`](runtime-behavior.md); asset data in [`renewal-asset-creation`](../renewal-asset-creation/SKILL.md) |
| Build a group ramp (API or UI) and check uplift | No | [`ramped-quotes`](../ramped-quotes/SKILL.md), `ramped-quotes/ui-group-ramp.md` |
| Fix a wrong price, DDS or header-distribution procedure | No | [`pricing-procedures`](../pricing-procedures/SKILL.md), [`pricing-setup`](../pricing-setup/SKILL.md) |
| Change bundle rules or why the configurator rejects a choice | No | [`constraint-models`](../constraint-models/SKILL.md) |
| Write or fix a Robot keyword that drives the editor | Partly | [`robot-testing`](../robot-testing/SKILL.md); live verification is required (AGENTS.md DO NOT 9) |
| Capture page edits made in an org back into templates | No | `repo-integration/ux-assembly-retrieve.md` (`ux_tool.py capture-drift`, `apply-drift`) |

## Discovery

Find what a page and an org use before changing anything; the repo snapshot below will age.

```bash
# Line editor components and their properties in the templates
grep -n "salesTxnLineTable\|progressIndicator\|transactionSummary" templates/flexipages/base/RLM_*_Record_Page.flexipage-meta.xml
# Patch files that touch the quote or order page, per feature flag
ls templates/flexipages/patches/*/RLM_{Quote,Order}_Record_Page.yml
# Revenue Settings the build deploys (groups, delta pricing, instant pricing default, skipOrgSttPricing)
cat unpackaged/pre/1_settings/RevenueManagement.settings-meta.xml
# What the org has now: retrieve and diff against the templates
python scripts/ux/ux_tool.py capture-drift --target-org <sf_alias>
```

**What this repo ships today** (snapshot, 2026-11-10) [Repo: the two page templates]:

| Page | Line editor tab | Components in the tab | Line editor properties set |
|------|-----------------|-----------------------|----------------------------|
| Quote | `Quote Lines` (active tab) | Progress Indicator, STLE, Transaction Summary | `displayFields` (14 in the template), `adjustmentTypeFields` (Discount Amount, Discount), `sidepanelDetailFields`, `viewRampDetailFields`, `groupRampFields`, `enableQuickAdd`, `enableSidepanel` |
| Order | `Standard.Tab.transactionLines` | STLE, Transaction Summary (Progress Indicator is in the header region) | `enableQuickAdd`, `enableSidepanel` only; columns are the component defaults |

Neither page sets the line editor's header action buttons, so both use the default layout. One
patch touches the line editor: `patches/approvals/RLM_Quote_Record_Page.yml` adds
`QuoteLineItem.RLM_Approval__c` with `add_display_field`, gated on `quantumbit` and `approvals`
(both on by default), so a default build deploys 15 quote columns. The record-page highlights panel (`force_highlightsPanel`
`actionNames`), a separate component, carries `BrowseCatalog` on both pages and
`CreateRampSchedule` and `QuoteAdjustment` on the quote page.

## Sub-files

| File | Read when |
|------|-----------|
| [`page-configuration.md`](page-configuration.md) | Changing columns, the Adjustment Type column, side panel or ramp fields, action buttons, the Transaction Summary, the settings the editor depends on, or auto-refresh, in Lightning App Builder or in this repo's templates |
| [`runtime-behavior.md`](runtime-behavior.md) | Using the editor: Browse Catalogs, groups, Instant Pricing, Reprice All, header adjustments, configuring a bundle from a line, amendment, renewal and cancellation lines, filters, bulk edit, a product-line discount inside a bundle, and the measured demo traps |

## Open — needs live verification

1. Whether a 264 org's Lightning App Builder shows the **text box** for action buttons, the
   **visual button-group UI**, or both, and the flexipage property each writes.
   `ind.qocal_configure_placement_of_action_buttons` gives text-box steps and, in the same
   article, button groups and an action picker; the release note
   `release-notes.rn_transaction_management_stle_enhance_button_groups` says the visual UI
   replaces the text box.
2. Which Help wording of the 10-item limit a 264 org follows is closed for the STLE: the cap is global across
   groups (see `page-configuration.md`).
3. (Closed) The Manage Header Adjustment API name is `HeaderAdjustment`; see `page-configuration.md`.
4. Whether Browse Catalogs can be placed or removed through the line editor's action-button
   configuration; it is not in the Help's list of supported action API names. The repo places it
   as a record-page highlights-panel action (`BrowseCatalog`) instead.
5. (Closed) Reprice All skips configuration; the success toast's wording is not evidence it validated it
   [Platform behaviour, traced].
6. Which Setup label `enableRevInstPricingDefaultPref` maps to (assumed *Instant Pricing Active
   by Default*), and whether `enableRevenueAdjustment`, which the repo's Revenue Settings file and
   scratch definitions set to true, is the **Header Adjustments** setting. The 264 dev guide doesn't
   document that field. A header discount did work on a fresh 264 build with the plan inactive
   [Repo: `datasets/sfdmu/procedure-plans/README.md`].
7. How renewal and cancellation lines display in the STLE (quantities, price columns, detail rows);
   only amendment lines were measured.
8. Whether bundle child lines can be moved with **Move Selected Items** (either editor), and whether
   the legacy TLE lets them be selected or bulk edited at all. In the STLE, selecting children and bulk editing them is
   measured: an Adjustment Type edit went to every selected child [Measured: 2026-11-11, fresh 264
   `ent-sb0` scratch org; see `runtime-behavior.md` section 2].
9. How **Group By** (TLE) places bundle child lines, which columns count as groupable, and whether
   the STLE's predefined and advanced filters include child lines
   (`ind.qocal_filter_line_items_with_standard_and_advanced_filters` doesn't say).
10. Whether a discount entered on a group row reaches bundle child lines in that group, and whether
    a bundle's children can sit in a different group from their root. Group rows can carry Adjustment
    Type fields (`ind.qocal_adjustment_type_column`), and the group-ramp articles show a rep entering
    a discount on a group (`ind.qocal_basic_example_ramp_deals_for_groups`,
    `ind.qocal_ramp_deals_for_groups_transition`,
    `ind.qocal_ramp_schedule_with_trial_and_proration_segments`); the last says products added to a
    segment inherit its Discount Percent, which doesn't settle bundle children in a non-ramp group.

## Examples

**Add a feature-gated custom column to the quote line editor.** The field
`QuoteLineItem.RLM_Example__c` ships only with flag `example`. Add it to the sales transaction
context definition (`context-service`), then create or extend
`templates/flexipages/patches/example/RLM_Quote_Record_Page.yml`:

```yaml
feature: example
feature_flag: example
patches:
  - type: add_sales_txn_line_editor_field
    property: displayFields          # default; also sidepanelDetailFields, viewRampDetailFields, adjustmentTypeFields
    after: "QuoteLineItem.DiscountAmount"
    fields:
      - "QuoteLineItem.RLM_Example__c"
```

If `patches/example/` is a new directory, register it with its gate in
`scripts/ux/_flags.py::FLEXIPAGE_PATCH_ORDER`; the assembler applies only listed directories and
never reads the YAML's `feature_flag:` key. If `example` is also a new flag, add it to
`project.custom` in `cumulusci.yml` and to `scripts/ux/_flags.py::UX_KNOWN_FLAGS` (the assembler
treats any other flag as off, and `ux_tool.py` rejects it in `--flag`). Then check both flag
states into a scratch directory, which leaves `unpackaged/post_ux/` alone:
`python scripts/ux/ux_tool.py assemble --flag example=true --output-path <scratch_dir>` (the field is
in the quote page) and the same with `example=false` (it isn't). Finish with
`cci task run assemble_and_deploy_ux -o deploy false` at the committed default flags
[Repo: `scripts/ux/_patch_ops.py`, `scripts/ux/_flags.py`, `scripts/ux/ux_tool.py`].

**A rep says the amendment line lost its price.** After a UI quantity edit on an amendment line,
Sales Price and Net Unit Price are blank on the parent and the price sits on detail rows (for
example +2 and −1 at the unit price) while the line total is right [Measured: early Nov 2026, 264].
Check the detail rows and the total before treating it as a pricing fault.

**Prepare a header-discount demo.** Confirm Header Adjustments is on, the active pricing procedure has
one DDS step (the repo's default procedure does), and the quote procedure plan is inactive (repo
default). Apply the discount from Manage Header Adjustment, then click Reprice All,
which Help requires when Delta Pricing is on, as it is in this repo
[Help: `ind.qocal_header_adjustments_use`; Repo: `unpackaged/pre/1_settings/RevenueManagement.settings-meta.xml`].

## Validation Checks

For a page change:

```bash
cci task run assemble_and_deploy_ux -o deploy false        # assembly succeeds locally
git diff --stat -- templates/flexipages unpackaged/post_ux # only the pages you meant to change
python -m pytest tests/test_ux_tool.py -q                  # assembler and patch-op tests
python scripts/ai/pr_gate.py --base origin/main
```

Also check:

- `unpackaged/post_ux/` was regenerated by the assembler, at the committed default flags, not
  edited (`assembly_manifest.json` `feature_flags`).
- Every new custom column is in the sales transaction context definition.
- No gated field appears in a base template (`grep` the field name across `templates/flexipages/base/`).
- After deploying to a scratch org, open a quote and an order and confirm the columns, buttons and
  Transaction Summary render; a Robot change that depends on them needs a live run.

For this skill: `python scripts/ai/analyze_agent_tooling.py check` and
`python scripts/ai/skill_manifest.py --check`.
