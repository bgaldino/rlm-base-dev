# Mike's Comments on Module 4 v2 — Response Plan

**Date captured:** 2026-05-13 (Google Docs ID `1HFbLR0P9G4f-NpY84aeyrH_5CKF5V6OfKTjqSrzdnho`)
**Comments captured:** 3 (all from Michael Aaron, posted 2026-05-12 evening)
**Status (2026-05-13):** All 3 applied to `module-4-v2.md`. All of Mike's standalone track-change suggestions are marked "Suggestion was deleted" in the doc sidebar — Brian has processed each one. 0 new comments outstanding.

## Comments + responses

### 1. Bill Cycle Day → Billing Day of Month + proration impact

- **Mike (5:42 PM):** "Its important to point out that switching the Bill Cycle Date (its actually called the Bill Day Of Month) at the Billing Schedule Group level will force proration to the next invoice on recurring BSGs to align to the new billing cycle."
- **Grounding:** 262 snapshot confirms the field is **Billing Day of Month** (`ind.billing_understand_period_boundaries_and_billing_day_of_month.htm` — "The Billing Day of the Month field on the Billing Schedule record"; `ind.billing_billing_profiles_create.htm` — "bill day of month"). "Bill Cycle Day" was wrong. The proration-on-change behavior is Mike's SME knowledge; the snapshot documents that the billing day determines the invoice generation day and that the next billing date follows the period-boundary calculation, which is consistent with Mike's claim.
- **Applied:** Renamed the section "Describe Bill Cycle Day and Next Billing Date" → "Describe Billing Day of Month and Next Billing Date." Renamed the field label throughout (kept `BillDayOfMonth` API name). Added a paragraph: changing the Billing Day of Month on a recurring BSG forces proration on the next invoice to realign the schedule.

### 2. Billing Day of Month change impacts Next Billing Date

- **Mike (5:55 PM):** "See my comment above, you cant change the Bill Day Of Month without it impacting the Next Billing Date."
- **Applied:** Same paragraph as #1 — the new text explicitly states "You can't change the Billing Day of Month on a recurring Billing Schedule Group without it impacting the Next Billing Date." Key Takeaways updated to note the two fields are linked.

### 3. Billing Batch Scheduler terminology — "make this clean"

- **Mike (5:15 PM):** "Actually the process [that] runs the show is called the Billing Batch Scheduler. The trigger that kicks off the process is called the Billing Scheduler which can either trigger invoices or payments. The Invoice Batch Runs (aka Bill Runs) are a single instance of the Billing Scheduler. Make this clean here."
- **Grounding:** 262 snapshot (`ind.billing_automate_invoice_run_schedules.htm`, `ind.billing_payment_runs_schedule.htm`) confirms: the App Launcher entry is **Billing Batch Schedulers**; the record is a **Billing Batch Scheduler** with a **Job Type** field (Invoice or Payment); "New Invoice Scheduler" / "New Payment Scheduler" are the creation actions; "A Billing Batch Scheduler record with Payment as the Job Type is created"; "At the start time of the scheduler, a Payment Batch Run record is created"; max 30 active Billing Batch Schedulers. Mike's "Billing Scheduler" maps to the doc's "Billing Batch Scheduler" record (which does carry the Invoice-or-Payment Job Type).
- **Applied:** Rewrote the "Map the Invoice Batch Run" opener as a clean three-term hierarchy — **Billing Batch Scheduler** (the config record, Job Type = Invoice or Payment, max 30 active) → fires → **Invoice Batch Run** (aka Bill Run, one instance; Payment Batch Run is the payment-side equivalent in Module 5) → processes **Billing Schedules**. The earlier draft called the config record the "Invoice Scheduler," which Mike's correction clarifies is just the invoice-job-type Billing Batch Scheduler. Also tidied the Unit 2 "Invoice Scheduler" reference to call it "the invoice-job-type Billing Batch Scheduler" for consistency. Key Takeaways updated.

## What's not in this comment set

Mike's 3 comments cover Unit 1 only (the cadence fields + the batch machinery). He didn't comment on:
- Billing Arrangements / split invoices (Unit 1)
- Debit Memo → Invoice Line conversion (Unit 1)
- Invoice delivery flow, Document Generation Service, email delivery (Unit 2)
- Convert Negative Invoice Lines to Credit Memo Lines (Unit 2)
- Self-Service Billing Portal (Unit 2)
- Subagent: Invoice Line Explanation (Unit 2)

Those sections stay as-is for this revision pass.

---

*Comments captured 2026-05-13 from `https://docs.google.com/document/d/1HFbLR0P9G4f-NpY84aeyrH_5CKF5V6OfKTjqSrzdnho/edit`.*
