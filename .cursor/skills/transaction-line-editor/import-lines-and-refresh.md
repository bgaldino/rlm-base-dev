# Import Lines, the refresh banner and header defaults

Read this when lines arrive outside the editor's own save (CSV import, API, automation), when users ask why the
"refresh prices" banner appears, or when quote header dates or terms must reach lines. Setup of the editor itself is
in `page-configuration.md`; day-to-day use is in `runtime-behavior.md`. Source tags are defined in SKILL.md.

## 1. Import Lines (Quote Line Import)

- The **Import Lines** action (`ImportQuoteLineItems`) uploads a CSV through a clone-able import flow and a Data
  Processing Engine definition [Help: ind.qocal_qli_import_user_import_lines_csv,
  ind.qocal_qli_import_considerations_customize_flow, ind.qocal_qli_import_extend_functionality].
- Setup requires **Hide Price Refresh Notification** off so the rep sees the refresh banner after the import
  [Help: ind.qocal_set_up_quote_line_item_import].
- The import loads defaults (default child products and attribute values) but **skips configuration rules and
  pricing**. The Help says to configure the quote line items after a successful import
  [Help: ind.qocal_qli_import_user_import_lines_csv]. In the line node the configurator call skips
  rule execution, pricing, qualification and catalog validation for import speed
  [Platform behaviour, traced].
- After the import, the banner's refresh (full pricing and configuration through Place Sales Transaction) is the
  step that prices; **Reprice All** runs pricing only [Platform behaviour, traced].
- Whether conditional rules over imported attribute values fire after the banner refresh on 264: imported lines can
  carry a Default constraint status, so context-tag values read by conditional rules are missing until a line is
  edited and saved [Open: untested risk; to settle it, import lines for a product with a conditional rule on an attribute value, refresh, and see whether the rule fires]. Interim: edit any field on
  each imported line and Save [Open: untested; same check]. Whether unconditional auto-add of required components
  works at import [Open: untested; to settle it, import a line for a bundle with a required default component and read the children].
- Quote `CalculationStatus` takes `ImportQLIInProgress`, `ImportQLISuccess` and `ImportQLIFailed` during an import;
  Place Sales Transaction is allowed once the import has finished, not while it is in progress
  [Platform behaviour, traced]. The import never prices on its own. To price after import without a person, a
  flow or scheduled Apex can call the Place Sales Transaction executor with Force pricing for quotes in
  `ImportQLISuccess` [Open: build that flow, import a quote, and confirm the quote prices]. Help says not to use the calculation status as a
  state machine: its values are often imprecise [Help: ind.qocal_differences_between_calculation_status_field_and_validation_result_field].
- Dates and terms in imports: a blank Start Date defaults to today for term-defined and evergreen lines; the import
  definition can be cloned (Save As) and edited to default differently [Platform behaviour, traced].

## 2. The refresh banner and Hide Price Refresh Notification


- A Save in the standalone line editor reprices and never raises the banner, with Instant Pricing on or off [Measured: 2026-11-26, 264, ent-sb0 harness build]. The
  banner appears after line edits made **outside** the editor (API, automation, record edit page), even with
  Instant Pricing on and active [Measured: 2026-11-26, 264, ent-sb0 harness build]. Instant Pricing previews price-impacting edits inside the editor only
  [Help: ind.qocal_turn_on_quote_and_order_capture, ind.qocal_view_and_edit_quotes].
- An API or Apex edit of a non-price field (a line Description) also set the quote stale and showed the banner [Measured: 2026-11-26, 264, ent-sb0 harness build]. The
  trigger is not a price-field list [Platform behaviour, traced].
- The banner's Refresh link and **Reprice All** both clear the stale flag; it stays clear on reload and returns only
  after a later edit outside the editor [Measured: 2026-11-26, 264, ent-sb0 harness build].
- **Hide Price Refresh Notification hides only the banner.** The stale flag (`Quote.ValidationResult` =
  `TransactionIncomplete`) stays set [Measured: 2026-11-26, 264, ent-sb0 harness build]: Create Order fails "We couldn't create the order because the prices aren't
  updated. Click Reprice All and try again." [Measured: 2026-11-26, 264, ent-sb0 harness build] and order activation fails "The prices aren't currently up to date on
  this Order. Click Reprice All, and try again." [Measured: 2026-11-26, 264, ent-sb0 harness build]. The Help recommends leaving it off (banner shown), and Import Lines setup requires it off
  [Help: ind.qocal_turn_on_quote_and_order_capture, ind.qocal_set_up_quote_line_item_import].
- Automation that writes non-price fields can avoid the banner by going through Place Sales Transaction with pricing
  Skip [Measured: 2026-11-26, 264, ent-sb0 harness build], but Skip also leaves a real price change unflagged [Measured: 2026-11-26, 264, ent-sb0 harness build]; an after-save flow that clears the flag masks
  staleness already on the quote (a Description edit after an unpriced Quantity edit cleared the flag with the
  total still stale) [Measured: 2026-11-26, 264, ent-sb0 harness build].
- STLE auto-refresh redisplays data after background changes; it does not reprice and does not clear the flag
  [Help: ind.qocal_auto_refresh_stle_transaction_summary_considerations].

## 3. Defaulting dates and term from the quote header

- The quote has a Start Date and an Expiration Date but no term or end date; lines have Start Date, End Date,
  Subscription Term and unit [Repo: scripts/erd/schema_diff/264-schema.json].
- Nothing cascades from the quote header to its lines out of the box: a line added in the editor defaults its Start
  Date to today, not the quote's [Platform behaviour, traced in part] (traced for the Place Sales Transaction add path and the CSV import; the
  editor's own add path was not traced) [Open: add a line in the editor on a quote whose Start Date is not today and read the line's Start Date].
- Ramped groups are the exception: a group's End Date sets the end date of its term-defined lines, and editing a
  ramp segment's dates updates its lines [Help: ind.qocal_ramp_deal_for_groups_create].
- Building a header default is a customer build. Candidate designs [Open: build one design, add a line, and read the line's dates and the banner] are custom header term fields plus a before-save flow on line create; an after-save
  quote flow that sends one Place Sales Transaction update per line with Force pricing (direct DML on lines marks
  the transaction incomplete and needs a reprice [Help: ind.qocal_limitations_for_using_quote_and_order_capture]);
  an edited import definition for imports only. Expect the refresh banner on line updates, and the end date not
  recomputing when a rep later edits the start date.

## 4. Smaller facts

- Side-panel attributes and their read-only behavior: [`page-configuration.md`](page-configuration.md#1-where-the-editor-lives-on-the-page).
- **Transaction Summary totals**: with `displayTotalPriceBreakdown` true the quote summary shows a One Time total and
  an expandable Recurring total grouped by term unit and selling model, display only and not normalized to a
  month [Platform behaviour, traced]. Orders do not show recurring totals [Open: untested on 264; to settle it, open an order with the setting on and read the summary].
  Help's Transaction Summary article does not mention the setting [Help: ind.qocal_customize_transaction_summary].
- Move Selected Items and group order: [`runtime-behavior.md`](runtime-behavior.md#3-line-groups).
