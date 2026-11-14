# Billing Operations — Tax

Read this when choosing a tax engine, building tax policies and treatments, or explaining
estimated vs actual tax. Parent: [SKILL.md](SKILL.md). A read of Help; not measured here.

## How an invoice line gets taxed

1. The product's **tax policy** passes to the order product and on to the billing schedule.
2. The policy's **treatment selection** picks the treatment [Help:
   `ind.billing_tax_policies_and_treatments_create`]:
   - Default: the policy's default treatment, else the org's default tax treatment.
   - Manual: the order product's own treatment; none falls back to the policy default, then
     the org default; with no org default the tax calculation fails.
   - Legal Entity: the treatment of the order product's (or order's) legal entity, else the
     org's default legal entity, else the policy's default treatment; with no default
     anywhere the calculation fails.
3. A treatment marked **Is Taxable** names a **tax engine**; the tax code on the treatment
   (or its treatment items, when Use Tax Treatment Items is selected) goes to the engine.
   A missing code sends a null value.
4. Generating an invoice triggers the Calculate Tax API with that engine
   [Help: `ind.billing_tax_calculation_results`].

Org defaults (billing treatment, tax treatment, legal entity) are set in Billing Settings
under Billing Defaults [Help: `ind.billing_setup_default_records`].

## Estimated vs actual

- **Estimated tax** is calculated for draft invoices; **actual tax** for posted invoices
  [Help: `ind.billing_tax_calculation_results`].
- Invoice lines carry a Tax Processing Status; ingested lines with Pending or Estimated use
  the Invoice Estimated Tax Calculation API (dev guide resource
  `/commerce/invoicing/invoices/collection/actions/calculate-estimated-tax`)
  [Help: `ind.billing_invoice_creation`] [Dev guide: `connect_resources_calculate_estimated_tax`].
- Posted invoices call the engine for actual tax; the result lands on Invoice Line Tax
  records (amount, code, rate, name, document and transaction numbers, effective date,
  exempt amount) and rolls up to the line and invoice total tax.
- Voiding a posted invoice calls the engine to void or adjust tax; the related credit memo
  is Voided or Posted depending on the engine's response by line type
  [Help: `ind.billing_void_taxes`].

How long, how many calls, or what a failed engine does to a run: not measured.

## Choose the engine

- Complex jurisdictions, or an existing tax vendor: a partner or custom engine through the
  `TaxEngineAdapter` Apex interface [Help: `ind.billing_partner_or_custom_tax_engine`].
- Simple rates, no external call, data residency limits: the Revenue Standard Tax Engine
  [Help: `ind.billing_standard_tax_rate`].
- Tax computed outside Salesforce: imported tax lines on draft invoices
  [Help: `ind.billing_tax_lines_import`].

Engines can be mixed: a treatment names its engine, so legal entities or products can
differ [Help: `ind.billing_tax_configuration_engine`].

Questions to ask the customer, with the Help-grounded consequence:

- **Does tax have to be certified or jurisdiction-exact?** The Revenue Standard Tax Engine
  is described as for simple calculations, at line level with line-level rounding, and
  not necessarily suitable for compliance needs [Help: `ind.billing_standard_tax_rate`].
- **Exemptions?** Use a tax system that supports certificate management; keep a matching
  key between Billing and the tax system, the Account Id for account-level exemptions
  [Help: `ind.billing_tax_calculation_results`]. Tax identification details can be stored on
  the Billing Account and passed to the engine [Help: `ind.billing_tax_identification_configure`].
- **Different ship-to for one product?** Change the schedule group's billing and shipping
  addresses; they flow to the invoice tax lines. Turn on field history on those fields to
  audit [Help: `ind.billing_tax_address_invoice_line_override`].
- **One tax total per invoice?** See header tax below.

## Partner or custom engine

Prerequisites: provider details (seller code, address, credentials), a named credential
for callouts, and a custom adapter extending `TaxEngineAdapter` for your own engine. Billing
supports up to 2,000 invoice lines on one invoice, so test the adapter against the Apex
total heap size limit [Help: `ind.billing_tax_configuration_prerequisites`,
`ind.billing_limits`]. Then create a tax engine provider and a tax engine
[Help: `ind.billing_tax_engine_and_engine_providers_create`]; only Active engines calculate
tax. The Tax Admin permission set creates engines, policies and treatments.

## Revenue Standard Tax Engine

- Create a Tax Engine with type Revenue Standard Tax Engine (a blank type is read as
  Revenue Cloud Tax Extension); set Active [Help: `ind.billing_tax_engine_create`].
- Tax rates match on shipping address, product code, legal entity and currency through the
  Revenue Standard Tax Entries decision table, or a cloned and activated copy named on the
  engine. Matching uses Geo Country and Geo State records, so enable the state and country
  picklists; all matching rates apply in priority order, lower number first
  [Help: `ind.billing_standard_tax_rate_application`, `ind.billing_tax_rate_configure`].
- Match custom attributes (product category, exemption criteria) by cloning the decision
  table and mapping fields with a custom metadata type
  [Help: `ind.billing_extend_revenue_standard_tax_engine`,
  `ind.billing_standard_tax_custom_metadata_types_configure`].
  Refresh and freshness of decision tables: `decision-tables`.

## Header tax

Set Credit, Payment and Refund Application Level to Header Level in Billing Settings; a
Capture Taxes At Header option then appears on tax engines. Balance calculation then uses
the header tax amount (Total Taxes Captured at Header) instead of summed line tax; line
tax is used when the header amount is missing or a number of listed failures occur
[Help: `ind.billing_setup_header_tax_enable`, `ind.billing_tax_summary_difference`].
Choose it only if the customer's tax system returns one consolidated amount
[inferred from Help].

## Imported tax

Create draft invoices for products whose tax treatment has Is Taxable off, export invoice
line fields, have the external system produce a CSV of Invoice Line Tax with Tax Processing
Status Posted, import it, check it points at the right lines, edit if needed, then post
[Help: `ind.billing_tax_lines_import`].

## What the repo ships

`qb-tax` loads legal entities, a tax engine and provider, tax policies and treatments, and
assigns the policy to products. Its engine reads a mock-tax named credential, so what the
repo builds is a test setup, not a real tax provider
[Repo: `datasets/sfdmu/qb/en-US/qb-tax/README.md`, `TaxEngine.csv`]. The build uses the
`prepare_tax` flow. Tax results from it against a real engine: not measured.

## Read-backs

```sql
SELECT TaxEngineName, Status FROM TaxEngine
SELECT Name, Status, DefaultTaxTreatmentId FROM TaxPolicy
SELECT Name, TaxPolicyId, TaxEngineId FROM TaxTreatment
SELECT InvoiceLineId, TaxAmount, TaxCode FROM InvoiceLineTax
SELECT Id, TaxProcessingStatus FROM InvoiceLine
```

Check: every taxable product has a policy whose treatment names an active engine; a draft
invoice shows estimated tax and its posted version actual tax; tax lines carry the expected
code and rate; amounts agree with the engine's own record via Tax Document Number.
