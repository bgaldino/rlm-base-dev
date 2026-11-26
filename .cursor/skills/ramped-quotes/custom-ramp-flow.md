# Ramped Quotes — The Create Ramp Schedule flow, uplift edits after creation, automatic ramping

> Sub-file of `.cursor/skills/ramped-quotes/SKILL.md`. Read it before replacing the flow behind Create Ramp Schedule,
> when a rep must change a segment's uplift after the schedule exists, or when asked to ramp products automatically.

## What a custom Create Ramp Schedule flow receives and must return

Revenue Settings has "Set Up Flow for Creating Ramp Schedules" (org value `RampScheduleGuidedFlowName`; default
`transactionManagement__CreateRampSched`). It is readable only with group ramp access [Open: default name and access
requirement are carried from desk notes, not re-read on a live org; check Revenue Settings on the target release].

- **Inputs: none on 264.** A probe flow with `recordId`, `selectedScopeJson` and `source` input variables, launched from the
  quote's Create Ramp Schedule action, logged all three empty; the same flow launched by URL with `recordId` logged
  it (positive control). The guided modal passes an empty input list, so a custom flow cannot read the quote id, its
  dates or its term [Measured: 2026-11-26, 264.12.x (USA796), ent-sb0 harness build].
  [Open: later releases may pass a selection scope; probe the flow on the target release]
- **Outputs: the modal creates the schedule itself.** It reads the flow's `errorMessage` and schedule outputs, so a
  replacement flow must return the managed flow's output variables, not create groups itself
  [Platform behaviour, traced].
- **Quote context:** launch your own flow from a quote action (there `recordId` arrives) and build the schedule
  with the Place sequence in [build-sequence.md](build-sequence.md); wrapping the managed flow in an action was
  reported not to create groups [Open: partner report, not reproduced].
- **Setting it** is a Revenue Settings text box with its own Save button on the same row; this repo has no task that
  sets it. [Open: a browser recipe (which Save belongs to the input, how to clear the box headless, verify by
  reloading) is pending a reusable front-door helper]

## Editing a segment's uplift after creation

[Measured: 2026-11-26, 264.12.x (USA796), ent-sb0 harness build], one Standard ramp in the quote UI:

- Create Ramp Schedule takes a per-segment Unit Price Uplift %. It defaults to 40 months with a trial; change both.
- **Edit Ramp Schedule** shows segment name, dates, duration, type and Ramp Uplift Type: no uplift column as built.
  **View Ramp Details** shows Unit Price Uplift and Applied Unit Price Uplift Percent read-only.
- The segment side panel shows the **Quote Line Group page layout**, which has no Unit Price Uplift by default. An admin
  adds the field to that layout for reps to edit it there [Help: ind.qocal_ramp_deal_compound_uplift_sales_reps.htm]
  [Open: the rep click path with the field added was not run].
- **Headless:** a Place PATCH of the segment `QuoteLineGroup` with `UnitPriceUplift` and `pricingPref: "Force"` saved,
  reached `CompletedWithPricing`, and repriced that segment's line (net 1,320 to 1,380 for a 10 to 15 uplift); the
  other segments' lines did not move. On a Compound ramp still read every segment's net prices afterwards
  ([pitfalls.md](pitfalls.md#partial-line-patch-on-a-compound-ramp)).

## Ramping products automatically

No setting ramps a rampable product when it is added [Help: ind.qocal_configure_ramp_segments.htm].
- **Group ramps (design path):** build the schedule first, then add products from segment 1's Browse Catalogs with
  *Current and Subsequent Segments*: one add places the product in every segment with ramp identity
  ([ui-group-ramp.md](ui-group-ramp.md)). A product added at quote level lands in the first, unramped group.
- **Automation:** an after-insert flow or queueable on `QuoteLineItem` that calls the ramp Connect resources
  (create ramp deal, group ramp actions). [Open: untested here; needs a recursion guard and batching, because Place saves async and reprices]
