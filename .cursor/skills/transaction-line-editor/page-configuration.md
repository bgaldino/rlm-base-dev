# Line Editor Page Configuration

> Sub-file of [`SKILL.md`](SKILL.md). Read it when changing what the line editor shows or which
> actions it offers, in Lightning App Builder or in this repo's templates. Source tags are defined
> in the parent.

## 1. Where the editor lives on the page

Admin path: Setup > Lightning App Builder > the Quote (or Order) Record Page > Edit. Help's steps
[Help: `ind.qocal_customize_transaction_line_editor`]:

1. Add a tab (label **Lines**) to the Tabs component and drag the line editor into it. Put it on
   the **default** tab so it loads with the page rather than when the rep switches tabs.
2. Drag the **Transaction Line Progress Indicator** above the editor. The editor uses it to show
   progress of line changes and info and error messages, and to support Browse Catalogs.
3. Select the editor. Under **Display Columns**, click **Select...** and pick the columns. Optionally
   turn on **Show product quick add** and **Show side panel when users click a record link**, and
   pick side panel fields.
4. For the STLE with group ramps, pick the fields for the View Ramp Details and Edit Ramp Schedule
   window.
5. Save, activate, and pick a form factor.

The editor shows as **Quote Line Items** on a quote and **Order Products** on an order. Users need a
Revenue Management permission set such as Assetize Order or Price and Tax Calculation for Quoting
[Help: `ind.qocal_customize_transaction_line_editor`]. To use it on a quote they need Manage Revenue
Management, the Create Orders from Quotes permission set and Price and Tax Calculation for Quoting
[Help: `ind.qocal_view_and_edit_quotes`]. On an order the profile also needs read access to
`OrderItem.ValidationResult`, `PriceWaterfallIdentifier`, `ParentOrderItemId`, `OrderActionId` and
`OrderItemRelationship.AssociatedOrderItemPricing`, `AssociatedQuantScaleMethod`
[Help: `ind.qocal_configure_placement_of_action_buttons`].

The side panel shows up to 200 product attributes per line, alphabetically by definition name, and
skips attributes marked hidden in Product Catalog Management [Help: `ind.qocal_customize_transaction_line_editor`].

### In this repo

The pages are generated from templates; App Builder edits in an org are drift until written back.

| Concern | Where | Notes |
|---------|-------|-------|
| Always-on columns and properties | `templates/flexipages/base/RLM_Quote_Record_Page.flexipage-meta.xml`, `RLM_Order_Record_Page.flexipage-meta.xml` | Edit the `runtime_rca:salesTxnLineTable` component's `componentInstanceProperties` [Repo] |
| Columns that need a feature flag | `templates/flexipages/patches/<feature>/RLM_{Quote,Order}_Record_Page.yml` | Patch type `add_sales_txn_line_editor_field`, or `add_display_field` (the approvals patch uses it) [Repo: `docs/features/dynamic-ux-assembly.md`] |
| Patch gate and order | `scripts/ux/_flags.py::FLEXIPAGE_PATCH_ORDER`, `UX_KNOWN_FLAGS` | A patch directory not listed in the order is never applied, and a gate flag missing from `UX_KNOWN_FLAGS` always reads as off [Repo] |
| Component identifier the patch targets | `scripts/ux/_flags.py::SALES_TXN_LINE_EDITOR_IDENTIFIER` (`runtime_rca_salesTxnLineTable`) | Override with `component_identifier:` in the patch [Repo: `scripts/ux/_patch_ops.py`] |
| Generated output | `unpackaged/post_ux/flexipages/` | Never hand-edit (AGENTS.md DO NOT 1) |
| Org edits back to templates | `ux_tool.py capture-drift`, then `apply-drift` | [Repo: `.cursor/skills/repo-integration/ux-assembly-retrieve.md`] |

`add_sales_txn_line_editor_field` takes `property` (default `displayFields`; any list property such
as `sidepanelDetailFields`, `viewRampDetailFields` or `adjustmentTypeFields`), an optional `after`
anchor, and `field` or `fields`. It skips values already present, so it is idempotent; if the
property list or the anchor is missing it logs a warning and adds nothing [Repo: `scripts/ux/_patch_ops.py`].
`add_display_field` takes one `field`, no `property` or `after`, and appends it to the first
`displayFields` list on the page, which on the quote page is the line editor's; it skips a value
already present and warns if there is no list [Repo: `scripts/ux/_patch_ops.py`]. The order page
sets no `displayFields`, so a `displayFields` patch of either type has no list to add to there:
add the property to the order template first. There is no patch type that removes a column or
changes a scalar property; change the base template. `insert_after_xml` only inserts an XML fragment
after an anchor, so at most it can add a property the template lacks.

**Value syntax** in the templates [Repo: quote page template]:

| Kind | Example |
|------|---------|
| Line field | `QuoteLineItem.Quantity` |
| Related-record field | `QuoteLineItem.Product2.Name[Product2]` |
| Group field on the line | `QuoteLineItem.QuoteLineGroup.Name[QuoteLineGroup]` |
| Group ramp field (`groupRampFields`) | `QuoteLineGroup.RampUpliftType` |

## 2. Display columns

[Help: `ind.qocal_select_fields_for_the_line_editor`]

- **Line fields** (Quantity, Description, Total Price) are columns.
- **Group fields** ([Quote Line Group] Subtotal) appear only when the transaction has groups.
- **Related-record fields** ([Account] Name) are columns; if the related record doesn't exist the
  cells are empty and not editable.
- **Custom fields** must also be in the sales transaction context definition, or edits to them are
  not saved.
- For product and group names in the STLE, add **[Product] Product Name** (recommended as the first
  column) and **[Quote Line Group] Quote Line Group Name** or **[Order Line Group] Order Line Group Name**.
  The repo's quote page does both [Repo: quote page template].
- **TLE only:** select both Discount (Percentage) and Discount (Amount); the TLE merges them into one
  Discount column. The STLE uses the Adjustment Type column instead.
- **STLE merged columns:** when a group field and its matching line field are both selected, the STLE
  shows one column headed with the line field's name, at the position of the first one selected,
  showing the group value on group rows and the line value on line rows. Standard fields only.
  Default pairs (QuoteLineItem / QuoteLineGroup): `Product.Name`/`Name`, `NetTotalPrice`/`SummarySubtotal`,
  `SortOrder`, `Description`, `StartDate`, `EndDate`, `SegmentType`, `TotalLineAmount`/`SummaryTotalAmount`,
  `TotalCost`, `TotalAdjustment`, `TotalAdjustmentAmount`, `TotalMargin`, `TotalMarginAmount`,
  `QuoteLineGroup`/`ParentQuoteLineGroup`. On orders, `ServiceDate` replaces `StartDate` and
  `OrderItemGroup` / `ParentOrderItemGroup` replace the group lookups.
- If a field qualifies for both a group/line merge and the Adjustment Type column, the Adjustment
  Type column wins.
- Swap, upgrade and downgrade amendments need the **Type** and **Subtype** columns
  [Help: `ind.qocal_swap_upgrade_downgrade_amendments`].
- Unit Price Uplift belongs in the quote line editor columns when price revision policies are used
  [Help: `ind.qocal_consumer_price_index_and_price_uplifts`; Repo: `.cursor/skills/pricing-setup/price-revision-policies.md`].
- Advanced filters can only use fields that are columns, from the line or one relationship away
  [Help: `ind.qocal_filter_line_items_with_standard_and_advanced_filters`].

## 3. Adjustment Type column (STLE)

[Help: `ind.qocal_adjustment_type_column`]

One column that merges several adjustment fields; the rep picks the type and enters a value.

- To include a field, add it to Display Columns **and** select it in **Select Fields to Group and
  Display in the Adjustment Type column**. In the repo that is the `adjustmentTypeFields` property;
  the quote page has `QuoteLineItem.DiscountAmount` and `QuoteLineItem.Discount` [Repo: quote page template].
- Supported: editable currency and percent fields on quote and order lines and their groups.
  Defaults: Discount Amount, Discount (Percentage), Margin Amount, Margin (Percentage), Unit Cost.
- Custom currency or percent fields are allowed if editable.
- Never add read-only, calculated or formula fields (Total Adjustment): pricing tries to set them and
  fails. Remove them if pricing errors start after a change.
- Never add Start Date or End Date: editing an adjustment can reset dates on ramped lines.

## 4. Header action buttons

[Help: `ind.qocal_configure_placement_of_action_buttons`, `ind.qocal_action_button_group_important_considerations`]

Prerequisites: **Enable Groups** on for group actions; **Header Adjustments** on for the quote or
order adjustment action. Permission to configure: Customize Application and the Manage Revenue
Management system permission.

Supported actions (API names are case-sensitive):

| Display label | API name | What it does |
|---------------|----------|--------------|
| Add Assets | `AddAssets` | Add assets to the editor |
| Add Group | `AddGroup` | Create a group of lines |
| Ungroup | `Ungroup` | Remove grouping from selected lines |
| Move Selected Lines | `MoveSelectedLines` | Move selected lines |
| Reprice All | `RepriceAll` | Recalculate prices for all lines |
| Bulk Delete | `BulkDelete` | Delete selected lines |
| Estimate Taxes | `EstimateTaxes` | Tax estimate for the transaction |
| Import Lines | `ImportQuoteLineItems` | Upload lines from an external source |
| Create Ramp Schedule | `CreateRampSchedule` | Create a group ramp schedule |
| Manage Header Adjustment | Help's *Action API Name* column lists `ManageHeaderAdjustment`; the STLE component names the action `HeaderAdjustment`, with `QuoteAdjustment` and `OrderAdjustment` as aliases of it [Platform behaviour, traced]. Whether `ManageHeaderAdjustment` is accepted was not traced | Header discount or override |

The table has two API-name columns (*Action API Name* and *API Name*); they differ only for Manage
Header Adjustment. Help also names `ExpandAllGroups` and `CollapseAllGroups` in a syntax example.
Browse Catalogs is not in the list; whether it can be moved is Open.

**Text-box syntax** (Help), one entry per line in the **Action Buttons** field:

| Want | Enter |
|------|-------|
| A standalone button | `AddGroup` |
| Buttons separated by a divider | `AddGroup, Ungroup` |
| Menu items under a main button | `MoveSelectedLines, (AddGroup), (Ungroup)` |
| A dropdown of actions | `(AddGroup, ExpandAllGroups, CollapseAllGroups, Ungroup)` |

**Button groups** (Help, both articles above). Up to 10 groups of up to 10 actions; an action belongs
to one group; actions reorder within a group but groups can't be dragged into a new order. Only
built-in actions are in the action picker. With nothing configured, the default is four groups:
`QuoteAdjustment`, `AddAssets`, `ImportQuoteLineItems`, then the rest with four visible. The run-time
limit is stated three ways in Help: the considerations article says only the first 10 actions show, the
configuration article says 10 visible action slots across all groups, and the release note says 10
**groups** show and the rest go to an overflow menu. In the STLE component the cap is global: 10 inline actions across
all groups combined, the rest under a More menu, and below a width breakpoint only 2 inline. It caps
rendering, not configured actions [Platform behaviour, traced]. That disagrees with the release note's
"groups" wording; the considerations article's "first 10 actions" is consistent if "show" means inline. The release note also says the visual UI replaces
the text box, that existing text-box values carry over, and that the header hides actions a rep can't
use and shows the next one in the group
[Release notes: `release-notes.rn_transaction_management_stle_enhance_button_groups`]. Help gives the
text-box steps and the button-group model side by side. Which UI a 264 org has is Open.

**In this repo** neither page template sets a line editor action-button property, so both editors
show the default layout [Repo: both page templates]. Don't confuse it with the record page's
highlights panel (`force_highlightsPanel` `actionNames`), which lists `BrowseCatalog` on both pages
and `CreateRampSchedule` and `QuoteAdjustment` on the quote page; those are page-header actions,
configured separately. Create Ramp Schedule appears as a header button and Browse
Catalogs as a ramp-segment row action on a measured 264 org [Repo: `.cursor/skills/ramped-quotes/ui-group-ramp.md`].
Before writing an action layout into a template, configure it once in App Builder on a scratch org
and capture the property with `ux_tool.py capture-drift`, so the template matches what the org writes.

## 5. Transaction Summary

[Help: `ind.qocal_customize_transaction_summary`]

- Place it in the **same tab** as the line editor; Help says it always renders at the bottom of
  the page in the live view, wherever it is dropped in App Builder.
- Pick footer and body fields; **Expanded by Default** shows the details on load. Address fields
  (Ship To, Bill To) are not supported.
- On orders, users need read access to `Order.TotalRoundedLineAmount`, `DiscountPercent` and
  `TotalAmount`.
- The repo's quote and order pages set `defaultState` false and `displayTotalPriceBreakdown` true
  [Repo: both page templates].

## 6. Revenue Settings the editor depends on

| Setting | Effect on the editor | Repo build |
|---------|----------------------|------------|
| Enable Groups | Group actions and group columns | `groupsEnabled` true [Repo: `unpackaged/pre/1_settings/RevenueManagement.settings-meta.xml`] |
| Ramp deals for groups | Create Ramp Schedule, ramp columns; STLE only | `enableGroupRampPref`, `enableGroupRampMultiSchedulePref`, `enableGroupRampTrialSegmentPref` true [Repo: same file] |
| Instant Pricing | Reprices price-impacting edits immediately | Toggled by `configure_revenue_settings` (Robot), flow `prepare_revenue_settings` [Repo: `cumulusci.yml`] |
| Instant Pricing Active by Default | Starts each quote with Instant Pricing on; STLE only [Help: `ind.qocal_turn_on_quote_and_order_capture`] | `enableRevInstPricingDefaultPref` true; label mapping Open |
| Delta Pricing | Help: click Reprice All after a header adjustment [Help: `ind.qocal_header_adjustments_use`]; the action itself runs a full reprice, Reprice All is needed for header edits made by other means [Platform behaviour, traced] | `enableDeltaPricing` true [Repo] |
| Header Adjustments | Manage Header Adjustment action; setup needs a Discount Distribution Service element in the pricing procedure [Help: `ind.qocal_header_adjustments_overview`] | Probably `enableRevenueAdjustment` true, unconfirmed (Open) [Repo: `unpackaged/pre/1_settings/RevenueManagement.settings-meta.xml`]; `RLM_DefaultPricingProcedure` has the DDS step [Repo: `.cursor/skills/pricing-procedures/elements/discount-distribution-service.md`] |
| Sales Price Amendments | Credit and charge detail lines on amended prices | `enableSalesPriceAmendments` true [Repo] |
| Exclude Default and STT Pricing Procedures (`skipOrgSttPricing`) | With an active procedure plan: on, a header discount is distributed twice; off, the Revenue Settings procedure re-runs after the plan and a price revision doubles (section in `runtime-behavior.md`) [Repo: `datasets/sfdmu/procedure-plans/README.md`] | false [Repo] |

The configurator the editor opens is the product's assigned Product Configuration Flow, or the org's
default flow for products and classifications without one
[Help: `ind.product_configurator_create_a_product_configuration_flow`]. The build
registers `RLM_Product_Configurator_Flow` (non-blocking, instant pricing on) as the org default through
`insert_default_configurator_flow` [Repo: `cumulusci.yml`].

## 7. Auto-refresh (STLE and Transaction Summary)

[Help: `ind.qocal_auto_refresh_stle_transaction_summary_help`, `ind.qocal_auto_refresh_stle_transaction_summary_considerations`]

- **Setup:** Setup > Change Data Capture > select **Quote** and **Order**. Don't select child
  objects; the parents cover lines, groups, line details and line attributes. Selecting only one
  object limits auto-refresh to that object. No new permission is needed.
- **In this repo** the `enable_change_data_capture` task does this, adding only what is missing and
  warning instead of failing if the org's CDC allocation is used up; it is step 17 of `prepare_core`
  [Repo: `cumulusci.yml`].
- **Scope:** only the user whose action (flow, Apex trigger, Agentforce action, record-page edit)
  changed the record sees the refresh. Edits by another user need **Refresh** from the editor's
  dropdown.
- **Unsaved edits:** the STLE asks Save, Discard or Cancel before refreshing; with no unsaved edits it
  refetches after a short loading state. It holds changes while a save is running. The Transaction
  Summary is read-only and refreshes without a prompt.
