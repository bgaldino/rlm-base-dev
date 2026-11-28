# Elevated Data Access for Quotes and Orders

> Sub-file of `.cursor/skills/pricing-setup/SKILL.md`. Release 264 / API v68.0. Source: Help
> `ind.qocal_elevated_data_access_for_pricing.htm`. Facts are tagged [Help], [Repo], [Core], [Measured] or [Open].

Lets a sales rep price quotes and orders when the rep has no field-level security (FLS) on the
fields the pricing procedure reads. Without it, the context and pricing services run as the
logged-in user and a protected input is dropped.

## When you need it

- A pricing input (a cost, a margin floor, a discount-table key, a custom header field) is
  hidden from reps by FLS, and reps still have to price.
- A rep's price differs from an admin's price on the same quote and nothing errors.

## Set it up

1. Setup > Revenue Settings > Pricing: turn on **Elevated Data Access for Quotes and Orders** and
   **Procedure Plan Orchestration for Pricing**. Help says to turn on both so elevated access covers
   the full execution path, plan orchestration included. [Help]
2. Metadata names (`RevenueManagementSettings`): Elevated Data Access is
   `enableFullEscalationHydration`; Procedure Plan Orchestration for Pricing is `enableRevUnifiedSetup`.
   The ent scratch org definition sets both true [Repo: orgs/ent.json]. Both were true on a default
   harness build [Measured: 2026-11-26, 264 (USA796), ent-sb0 harness build, one org].
3. Set FLS the way Help describes: remove Read and Edit on the sensitive fields from the profiles that
   must not see them, and keep the fields available to the admin that runs the elevated context.
   Layouts alone are not a control; FLS is. [Help]
4. Scope [Help]: new-sale, amendment, renewal and cancellation quotes and orders.
5. Optional hook [Help]: a pricing Apex hook class (pre-pricing, post-pricing or both) that adds or
   validates the sensitive fields the engine needs and, in the post hook, strips them from the context
   output returned to the caller. Help requires Author Apex to create it.

## What the setting does, measured

A quote header field was mapped into `RLM_SalesTransactionContext` and read by a formula (6% off
when the field is 3 or more). All rows: [Measured: 2026-11-26, 264 (USA796), ent-sb0 harness build, one org].

| Pricing user | Setting | Hook | Result |
|---|---|---|---|
| Rep without FLS on the field | on | none | 9,400 (correct) |
| Rep without FLS on the field | off | none | 10,000, status CompletedWithPricing, no error or warning |
| Admin with FLS | either | none | 9,400 |

- The setting alone lets pricing read a mapped header input; the hook was **not** needed. Turning the
  setting off fails **silently**: the discount is not applied and nothing reports it.
- A line-level input behaves the same. With a `QuoteLineItem` input field, a rep (Standard User plus
  the `RLM_Sales_Representative` permission set group) and a procedure-written field the rep cannot
  query or edit: setting on, pricing reads the input and writes the procedure output back (persisted);
  setting off, neither happens, and the stored value is not cleared. [Measured: 2026-11-26, 264 (USA796),
  ent-sb0 harness build, one org]
- The price waterfall exposes the protected input. The waterfall GET called as the rep returned the
  field's value in the discount step's input parameters. Treat the waterfall as readable by anyone who
  can open the line (see
  [`../pricing-procedures/runtime-and-observability.md`](../pricing-procedures/runtime-and-observability.md)).
  [Measured: 2026-11-26, 264 (USA796), ent-sb0 harness build, one org]
- Why it fails silently [Core]: the context access check drops attributes the user cannot
  access, without an error.
- Not run: orders, the line editor UI, the Apex hook itself, and whether a post-pricing hook
  keeps the values out of the waterfall.
  [Open: does Elevated Data Access apply on amend, renew and cancel; settle by running each as a no-FLS rep with the setting on and off]

## Test it with a rep who has no FLS

1. Deploy the test field with FLS only in a permission set for the admin; a new field gets no profile
   FLS. [Measured: 2026-11-26, 264 (USA796), ent-sb0 harness build, one org] If you remove FLS on the Admin profile, keep admin access through a permission set first,
   or the running admin loses the field too.
2. Create the rep: `sf org create user profileName="Standard User"`, then insert a
   `PermissionSetAssignment` for the `RLM_Sales_Representative` permission set group (its licenses
   come with it).
3. A quote with no opportunity or account is visible only to its owner and admins (a `QuoteShare` insert
   is refused: `ControlledByParent`) [Measured: 2026-11-26, 264 (USA796), ent-sb0 harness build, one org]. Transfer the quote to the rep for the run, or build it as the rep.
4. Price as the rep with the setting on, then off; compare. Restore the setting, FLS and owner.
5. Routing alternative to a procedure plan: point the Revenue Settings default pricing procedure at the
   test procedure (Setup UI; see
   [`../pricing-procedures/operations-and-troubleshooting.md`](../pricing-procedures/operations-and-troubleshooting.md)),
   then restore it.

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| A rep's price is higher than an admin's, status CompletedWithPricing, no error | Elevated Data Access is off and a mapped input has no FLS for the rep | Turn the setting on; compare as the rep [Measured: 2026-11-26, 264 (USA796), ent-sb0 harness build, one org] |
| A rep sees a protected value in the waterfall | The waterfall lists the hydrated inputs of each step | Removing FLS does not hide a value a step consumes from the waterfall; decide who may open the waterfall [Measured: 2026-11-26, 264 (USA796), ent-sb0 harness build, one org] |
| A procedure-written field is not updated for a rep | Setting off and no write access | Setting on; the write-back persists [Measured: 2026-11-26, 264 (USA796), ent-sb0 harness build, one org] |

## Gaps

- No helper script builds the no-FLS rep and restores the org; the steps above are manual.
