# Mike's Comments on Module 5 v2 — Response Plan

**Date captured:** 2026-05-14 (Google Docs ID `1X6A714qd3WoIvkf1Fpd5RZygN1EwwQfZwo4000SSEsE`)
**Comments captured:** 8 (all from Michael Aaron, posted 2026-05-14, 1:20–1:54 PM)
**Status (2026-05-14):** All 8 applied to `module-5-v2.md`. Mike's standalone track-change suggestions show "Suggestion was deleted" in the doc sidebar — Brian processed each one (including the Stripe → Salesforce Payments inline swaps). The repo file was behind the doc on those swaps; this pass brings it to the correct end state and adds the five new sections.

## Group A — Corrections (gateway framing)

All three corrections were the same root issue: the Salesforce Payments / Adyen / Stripe framing was wrong.

| # | Mike's comment | Resolution |
|---|---|---|
| 1 | "Wrong. Salesforce Payments is a gateway. Adyen is a gateway. They are both native." | Dropped the "wrapper / native payment service" framing. Salesforce Payments and Adyen are now described plainly as the two native payment gateways. |
| 2 | "Never mix Salesforce Payment and Stripe — we use Stripe as the back end for payments but that should not matter to the customer." | Removed all Stripe mentions. Stripe is Salesforce Payments' backend and stays invisible to the customer. |
| 3 | "Pick another topic this is wrong." (anchored to the "What's in a Name?" callout) | The callout's premise — a wrapper-vs-gateways distinction — doesn't exist, so it produced nonsense ("Salesforce Payments + Salesforce Payments"). Replaced it with a Seller Sidebar on what "native" actually buys the customer (no Apex adapter, guided setup). |

Committed in `f77040a9`.

## Group B — New sections (all grounded against the 262 snapshot)

| # | Mike's comment | New content | 262 source |
|---|---|---|---|
| 4 | "Need to add a section on L2 and L3 payment data, a 262 feature." | New section **"Send Level 2 and Level 3 Payment Data"** after the Payment Gateway Adapter section. L1 = bare charge; L2 = transaction-level metadata (tax, discount, invoice/PO reference, postal code); L3 = line-item detail (product code/SKU, quantity, unit price, line-level tax, commodity code, UOM). Enabled via Billing Settings → Level 2 and Level 3 Data Support. Third-party Apex-adapter gateways only. | `ind.billing_send_l2_l3_data.htm` |
| 5 | "We need a section here to discuss the creation of Payment Schedule and Payment Schedule Items — how they are created (via an invoice run or a payment plan)." | New section **"Create Payment Schedules and Payment Schedule Items"** before "Set Up Payment Runs." Two creation paths: automatically from posted invoices (Billing Settings toggle) or manually as a payment plan. A run processes items in Ready for Processing status under a schedule in Open status. | `ind.billing_payment_schedules_and_payment_schedule_items_auto_manual.htm`, `ind.billing_payment_batch_run_overview.htm` |
| 6 | "Need to discuss how the system selects the right payment method for the invoice." | Folded into the new Payment Schedules section: auto-created schedules charge the account's **default saved** payment method; manually created schedules charge the **most recently created saved** payment method for the account related to the invoice. | `ind.billing_payment_batch_run_overview.htm` |
| 7 | "Need to discuss the 262 feature that combines multiple invoices into a single payment." | New section **"Consolidate Multiple Invoices into a Single Payment"** after the Payment Schedules section. Payment Schedule Treatment with Grouping Source = Account and a Due Date Window; groups invoices sharing currency + payment method + due-date window into one Payment Schedule (sum of amounts; earliest due date). Reduces gateway calls and fees. | `ind.billing_payments_consolidate_invoices.htm`, `ind.billing_generate_single_payment_schedule.htm` |
| 8 | "Need to outline how to create an error category." | Expanded the "Implement a Payment Retry Strategy" section with a paragraph on building a Payment Retry Rule scoped to a gateway error category. **Terminology note for Mike:** error categories are not created — they are a predefined list you *select* from when defining a Payment Retry Rule (with an optional error code). The new paragraph says this explicitly. | `ind.billing_setup_payment_retry_rules.htm` |

### Supporting updates

- **Unit 1 LOs** grew from 4 to 6 (added L2/L3 data; added Payment Schedule generation + consolidation).
- **Intro paragraph** rewritten to walk the payment path end to end.
- **Key Takeaways** updated to cover L2/L3 data, Payment Schedules/Items, and consolidation.
- **Resources** added three article links (L2/L3 data, Payment Schedules, consolidate invoices).
- **Quiz** added one item for the Payment Schedule consolidation LO.

## Open note for Mike

**#8 — "create an error category."** Error categories aren't author-created objects; they're a fixed list of gateway error categories you select on a Payment Retry Rule. The new content is written that way. If Mike meant something else (e.g., a custom error-classification mechanism), flag it.

---

*Comments captured 2026-05-14 from `https://docs.google.com/document/d/1X6A714qd3WoIvkf1Fpd5RZygN1EwwQfZwo4000SSEsE/edit`.*
