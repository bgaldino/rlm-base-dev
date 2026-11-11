# Line Editor Runtime Behaviour

> Sub-file of [`SKILL.md`](SKILL.md). Read it before rehearsing or debugging a demo in the line
> editor or the configurator. Source tags are defined in the parent. Items tagged `[Measured]` were
> observed on 264 demo orgs in early November 2026 and are not in the Help.

## 1. Adding products

[Help: `ind.qocal_view_and_edit_quotes`, `ind.qocal_view_and_edit_orders`, `ind.qocal_discover_and_configure_products`]

Three ways in: **Browse Catalogs**, the **Add Product** quick-add search, and **Add Assets** (existing
assets on an initial sale). The first add sets the price book; keep every product, children included,
on one price book. Added products are unsaved **transient lines** that can't be edited until the
quote or order is saved. Saving creates the lines and their attribute records.

Browse Catalogs flow: select a catalog > Next > filter > set quantities > **Show buying options** for
products with selling models, **Configure** for configurable ones > **Add** or **Add Selection to
Quote** into the New Quote Line Items preview > **Add Items to Quote**. A configured product that is
saved is created even if it doesn't show in the preview. Derived-price products show list price 0 until
added. If the page has no line editor, save from the Browse Catalogs page. Using it needs Use Product
Discovery, Manage Revenue Management and Run Flows.

Child products appear in the editor only when **Quote Visibility** on the product-related component is
blank, Always or Transaction Line Editor [Help: `ind.qocal_view_and_edit_quotes`; Dev guide:
`product_catalog_management_fields_on_product_related_component`].

Measured traps:

- **Browse Catalogs opens on the first catalog in the list.** That catalog may show "No products to
  show" until the rep switches catalog [Measured: early Nov 2026, 264]. In a demo, switch to the
  intended catalog first.
- **A top-level category whose products sit only in subcategories shows no products** until a
  subcategory is picked [Measured: early Nov 2026, 264].
- On a group ramp, Browse Catalogs from a segment row first asks **Select Segments to Add Products**;
  see `ramped-quotes/ui-group-ramp.md` [Repo: `.cursor/skills/ramped-quotes/ui-group-ramp.md`].

## 2. Editing lines

[Help: `ind.qocal_view_and_edit_quotes`]

- Click a cell, edit, save. **Bulk edit:** select several lines, edit the cell on one, save; the value
  goes to all selected lines. The STLE bulk-edits groups too.
- Unsaved edits are lost on page reload or session expiry.
- Decimal quantities only for products with a unit of measure; the grid shows two decimals and stores
  the unit of measure's scale.
- If the editor won't switch a line between Discount (Percentage) and Discount (Amount), clear the value
  on the line record, then enter the new type in the editor.
- Hover **Net Unit Price** for the price waterfall (bundle, tier, attribute, derived and contract
  adjustments); hover **Total Price** for bundle parent price, sum of lines and bundle subtotal.
- **Freeze up to this Column** pins columns; the filter row searches columns. Column filtering covers
  parent lines only; bundle children are excluded.
- **STLE filters:** predefined All Lines, Errored Lines, Ramped Lines, Unconfigured Lines; advanced
  filters take up to 5 conditions with AND/OR, scoped to all or selected groups. The most recently
  applied of a column filter and a predefined or advanced filter wins
  [Help: `ind.qocal_filter_line_items_with_standard_and_advanced_filters`].
- **Variation products:** quick add lists variations, not their parents. Row action **Change** replaces
  the line with a new one and drops its discounts and adjustments [Help: `ind.qocal_product_variation_use_in_transaction_management`].

## 3. Line groups

[Help: `ind.qocal_view_and_edit_quotes`, `ind.qocal_view_and_edit_orders`]

- Needs **Enable Groups** in Revenue Settings (on in this repo). Once a transaction is grouped, every
  line must be in a group.
- **Add Group** the first time moves all existing lines into one group; click again for more. Name
  each group. **Move Selected Items** reassigns lines or groups; **load more** reveals more groups.
- Up to five levels of nested groups and lines in one table, with subtotals per level.
- **Group By** on a column groups automatically, in the **TLE only**; not in the STLE, and not on
  formula fields.
- Sort Order on the Quote Line Groups related list sets group order; blank ones go last, by creation date.
- **Ungroup** returns to a flat list. Groups carry over from quote to order.
- Lines created through the Place Sales Transaction API should carry a group ID when the STLE will be
  used on that quote afterwards [Dev guide: `connect_resources_place_sales_transaction`].
- Group ramps (Create Ramp Schedule, segments, uplift) are covered in
  [`ramped-quotes`](../ramped-quotes/SKILL.md); the legacy TLE doesn't support them.

## 4. Pricing actions

| Action | What it does | Source |
|--------|--------------|--------|
| **Save** | Prices inline edits | [Help: `ind.qocal_view_and_edit_quotes`] |
| **Instant Pricing** | Reprices each price-impacting change at once; turns off on page reload or session expiry. *Instant Pricing Active by Default* (STLE only) turns it on by default | [Help: `ind.qocal_view_and_edit_quotes`, `ind.qocal_turn_on_quote_and_order_capture`] |
| **Reprice All** | Full repricing of every line, even with no changes and even with Delta Pricing on; skips configuration | [Help: `ind.qocal_reprice_all_quotes_and_orders`] |
| **Refresh Prices** | Pricing, configuration and taxes | [Help: `ind.qocal_view_and_edit_quotes`] |
| **Estimate Taxes** | Tax estimate; needs *Add Estimated Tax to Quotes and Orders* | [Help: `ind.qocal_reprice_all_quotes_and_orders`] |

Use Reprice All when pricing was skipped at commit, validation errors stopped a run, discounts or bundle
configuration need a refresh, or usage resource grants on a quote line were deleted (it rebuilds them)
[Help: `ind.qocal_reprice_all_quotes_and_orders`]. Any update to an order or its products outside the
line editor, including Description, sets the validation result to Transaction Incomplete, and the order
must be repriced before activation; the same applies to quote lines
[Help: `ind.qocal_limitations_for_using_quote_and_order_capture`].

Measured: **Reprice All on a quote whose lines are already priced changed nothing** and showed "The prices
were refreshed and the configuration was validated." [Measured: early Nov 2026, 264]. The message's
mention of configuration conflicts with Help's "skips configuration"; see the parent's Open list.

## 5. Header adjustments

[Help: `ind.qocal_header_adjustments_use`, `ind.qocal_header_adjustments_overview`]

**Manage Header Adjustment** > type (**Amount**, **Percentage**, **Amount Override**) > value >
distribution (**Equal**, or **Proportionate** to each line's list price × quantity). With Delta Pricing on
(this repo), click **Reprice All** afterwards. The waterfall shows each line's share. Users need
Salesforce Pricing Run Time User.

**The editor doesn't distribute the discount; the Discount Distribution Service (DDS) element does.**
Manage Header Adjustment records the type, value and distribution logic, and the DDS element in the
pricing procedure spreads them across the lines at pricing time [Help: `ind.qocal_header_adjustments_overview`].
So the setup is:

- **Header Adjustments** on in Revenue Settings.
- A pricing procedure with a DDS element, fed by list groups that read the header discount type
  (Amount, Percentage, Override). DDS must come last, with only Aggregate Price or Rounding after it,
  and it can't share a procedure with Derived Price. When derived pricing is needed, put DDS in its own
  procedure and run both through a procedure plan with Procedure Plan Orchestration for Pricing on
  [Help: `ind.qocal_header_adjustments_overview`]. Element detail:
  `pricing-procedures/elements/discount-distribution-service.md`.

In this repo, `RLM_DefaultPricingProcedure` has the header-discount list groups (seq 36–38) and a DDS
step (seq 39), followed by the aggregates. That is the Revenue Settings procedure, so header adjustments
work with the procedure plan inactive. `RLM_Price_Distribution_Procedure` (`unpackaged/post_procedureplans`)
has a second DDS, and the plan's Header Distribution section runs it after the default procedure
[Repo: `.cursor/skills/pricing-procedures/elements/discount-distribution-service.md`,
`datasets/sfdmu/procedure-plans/README.md`].

Measured: **a 10% header discount was applied twice (19% total)** with an active pricing procedure plan
and `skipOrgSttPricing` on; line discounts on the same quote were exact [Measured: early Nov 2026, 264].
Both DDS steps ran, the default procedure's and then the plan's distribution procedure's. The repo's own
measurement agrees: 10% on 5,240 gave 4,244.40, not 4,716 [Repo: `datasets/sfdmu/procedure-plans/README.md`].
The repo builds the plan inactive and `skipOrgSttPricing` false, so a default build runs one DDS.
If the plan must be active, follow `pricing-procedures/operations-and-troubleshooting.md` section 3:
with `skipOrgSttPricing` off the plan re-runs other steps too (a price revision doubles), so the fix is
not only a question of where DDS sits.

## 6. Configuring a bundle from a line

[Help: `ind.product_configurator_configure_bundled_products`, `ind.product_configurator_get_latest_pricing`]

- On the quote's line tab or the order's Lines tab, open the line's quick action menu > **Configure**.
- The record's **Transaction Type** selects which rules engine runs configuration rules.
- In the configurator: Compact Mode, **Load Configuration** for a saved one, add products to a component
  group, **Clone** an option card (needs the flow's Display Clone Option attribute; quantity isn't
  cloned). **Instant Pricing** in the configurator updates the summary on each change; otherwise click
  **Update Price**. **Save and Exit** returns to the editor.
- The configurator keeps no state: deselect then reselect a child and it comes back as a new line with
  defaults.
- Help notes that amending and cancelling a child product doesn't update the line quantity.

Measured:

- **A line placed by API with configuration rules off can open in the configurator with a different
  configuration than the one saved.** Lines placed with rules on opened correctly
  [Measured: early Nov 2026, 264]. Place demo lines with rules on, or check each one in the configurator
  before the demo. Rule behaviour itself is in [`constraint-models`](../constraint-models/SKILL.md).

## 7. Amendment, renewal and cancellation lines

What Help says:

- Amendment, renewal and cancellation quotes and orders copy asset attribute values to the line
  attributes [Help: `ind.qocal_amend_assets`, `ind.qocal_renew_assets`].
- A negative delta quantity on an amendment or cancellation is priced from prior sale prices, last in,
  first out [Help: `ind.qocal_amend_assets`, `ind.qocal_cancel_assets`].
- With derived pricing on amendments, the derived product's Net Unit Price isn't shown; the line total
  is accurate [Help: `ind.qocal_amend_assets`].
- A price amendment has delta quantity zero, action Amend, and a total that is a prorated credit for the
  old price plus a charge for the new one [Help: `ind.qocal_field_and_pricing_amendments`]. The repo
  turns on Sales Price Amendments [Repo: `unpackaged/pre/1_settings/RevenueManagement.settings-meta.xml`].
- Swaps, upgrades and downgrades show their action in the **Type** column and SwapIn/SwapOut,
  UpgradeFrom/UpgradeTo, DowngradeFrom/DowngradeTo in **Subtype** [Help: `ind.qocal_swap_upgrade_downgrade_amendments`].

Measured on amendment lines [Measured: early Nov 2026, 264]:

- **After a UI quantity edit, Sales Price and Net Unit Price are blank on the parent line.** The price
  moves to detail rows (for example +2 and −1 at the unit price) and the line total is right. The API's
  `quantityChange` keeps the price on the parent line, so UI and API amendments look different in the
  editor.
- **A UI quantity edit with configuration rules on resets the line's attributes to the product
  defaults**, and activation writes those defaults to the asset. Reopening such a line in the
  configurator shows the diff against the asset. Don't demo an inline quantity edit on an amendment of a
  configured product; change the quantity in the configurator, or demo a product without attributes.

Renewal and cancellation line display in the STLE was not measured; see the parent's Open list.

## 8. Demo checklist

1. Quote page: line editor on the default tab, Progress Indicator above it, Transaction Summary in the
   same tab (repo quote page does this).
2. Change Data Capture on Quote and Order, if the demo runs a flow or agent action against the open
   quote (`enable_change_data_capture`).
3. Browse Catalogs: switch to the demo catalog and a leaf subcategory before adding.
4. Demo lines placed with configuration rules on; open each configurable line once in the configurator.
5. Procedure plan inactive before any header-discount demo.
6. Amendment demo: no inline quantity edit on configured products; explain blank parent prices as
   detail-row pricing if they appear.
7. Reprice All on an already-priced quote is a no-op; don't present it as a visible change.
