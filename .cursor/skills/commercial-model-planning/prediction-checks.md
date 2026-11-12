# Prediction Checks — What to Run Before You Predict

Read this when writing the plan's decisions, rule decision record, live spikes and
golden tests with [commercial-model-planning](SKILL.md). A prior build tracked every
prediction a blind plan made and recorded each outcome as it was measured (SKILL.md
step 9). Where a prediction was modified or refuted because the planner skipped a step,
that step is a check below. Check 15 sharpens a guard the plans already had: the build
measured why a freshness check alone wasn't enough. The platform facts live in the
domain skills named; this file says when the plan must apply them.

Run each check that applies, and record the result where the plan already holds that
prediction: a decision, a rule decision record row, a spike's must-hit or a golden.

## Knowledge source (step 4)

1. **A skill's measurement covers the shape and route it measured.** A fact measured on
   an API-built ramp, a top-level line or a bundle without children of one selling model
   doesn't settle a UI-built ramp, a bundle component or a mixed bundle. Read the skill's
   measured shape before citing it as **Repo**; where the plan's shape differs, the rule is
   **Repo (inferred)** at its build gate, or **Live** when a later phase depends on the
   answer. A prior plan cited "one-time children in segment 1 only" as measured. The
   skill had measured it on an API-built ramp and on an optional child; a UI-built ramp
   of the plan's bundle put every child in every segment (`ramped-quotes` →
   `bundle-children-lifecycle.md`).
2. **Name the inputs a documented element is assumed to take.** An element the snapshot
   documents, at a position or with an input the docs don't show, is **Snapshot** when
   nothing contradicts it. List the parameters and context fields the plan assumes, so
   its build gate checks each one. A prior build found a parameter that a skill listed
   as optional, and the build used, refused at creation (`pricing-procedures` →
   `elements/rounding-values.md`, Configuration).
3. **A spike's must-hit is the source's value, not a guess at the platform's.** Where a
   skill marks a behaviour open, don't list candidate platform outcomes as must-hits: a
   prior spike listed two and the platform produced a third. State the source value, what
   to record about the native result, and the fallback that reaches the source value if
   native misses it (often **Build (custom)**, such as a procedure overlay).
4. **Before predicting a price on an amendment or renewal, find which procedure branch
   its lines take.** The asset's `PricingSource` decides it, and the shipped procedure's
   XML shows the branch. Added units on a `LastTransaction` asset took the last net price
   with no volume step (`asset-lifecycle-changes` → `change-policy-mapping.md`, the
   volume-band row).

## Structure and decisions (step 6)

5. **Choose a structure against every lifecycle change in the source,** not the new
   sale alone. Run each change through the candidate structure before deciding it:
    - A choice held as a one-of component group can't hold a split, such as moving part
      of a bundle's units to another plan: the split puts two components in a group whose
      maximum is one (`product-catalog-modeling` → `bundles-and-cardinality.md`, Two kinds
      of cardinality), and a configuration rule written for the new sale refuses it too.
    - A component can't be cancelled or renewed alone (`asset-lifecycle-changes` Quick
      Rule 3).
    - Where any change needs it, the item is its own top-level line. Cross-line checks
      then sit on a virtual `Quote` container (`constraint-models` →
      `quantities-from-attributes.md`, Checks across top-level lines).

   A prior plan kept such a choice as a component and needed that fallback after its
   lifecycle spikes.
6. **Every recommendation names its mechanism, and every layer that could refuse it.**
   "Treat the rule as new-sale only" or "permit the split on amendment" isn't a
   mechanism. Name the condition in the model, the procedure step or the validation that
   does it. Then check the other layers that act on the same change (component group
   cardinality, other configuration rules, bundle validation) for one that refuses it
   anyway. A prior recommendation of this kind was refused by the rule it meant to
   relax, which nothing relaxed, and by a group cardinality it didn't name.
7. **For each native guard, name where the platform enforces it and on which paths.**
   List every path the build creates the record on (catalog UI, Place API, clone,
   amendment, renewal) and the step that refuses (category assignment, configurator,
   Place, order, activation). A path the guard doesn't cover gets its own check, or the
   gap is a decision. `IsSoldOnlyWithOtherProds` was measured refusing only at category
   assignment; Place, order and activation accepted the product alone
   (`product-catalog-modeling` → `selling-models-and-lifecycle.md`).
8. **Gate a custom computation on every quote structure the plan creates.** A value
   that counts terms or dates (contract value, cost over the term) runs on plain quotes,
   ramp segments (dated line groups), amendments (the months left from the asset's
   start) and renewals; list each as a golden case. If it sums a subset of lines, such as
   one product line, check that the field selecting them is in the pricing context. The
   sales transaction context has no product Family (`pricing-setup` →
   `scenarios/full-term-value.md`; `context-service`).

## Golden tests (step 5)

9. **Compute every derived quantity at each answer's maximum** and compare it with the
   platform limits the domain skill lists. A component relation is capped at 9,999 unless
   the model raises `maxRelationSize` (`constraint-models` →
   `quantities-from-attributes.md`).
10. **Prorate partial periods by day unless the plan builds otherwise.** The proration
    policy the base build ships counted whole periods plus the days left in the current
    one, so a months-based source value matches only on an anniversary (`pricing-setup` →
    `proration-and-selling-models.md`, Measured: a partial year prorates by days;
    `asset-lifecycle-changes` Quick Rule 6). A mid-period change's golden carries both
    values through the mapping, or a decision makes the build match the source.
11. **Round after every step that multiplies, not once.** A compound ramp uplift kept
    four decimals (`pricing-procedures` → `elements/price-revision-compound-uplift.md`),
    so a plan that rounds before the uplift needs a second rounding after it.
12. **State the line inputs a pricing step filters on,** as the placing script sends
    them. A commitment-term step read `SubscriptionTerm`, and a line placed with start
    and end dates alone had none, so it got no discount; a header-only Place change
    didn't reprice (`pricing-procedures` → `elements/commitment-term-discount.md`, Line
    inputs on real quotes).
13. **Assert a refusal where its message appears.** Place returned success for a
    configuration it then logged as an error; the message can appear only in
    `RevenueTransactionErrorLog` or a later `configure`. A rule can also remove a line
    silently, so read the deltas (`constraint-models` → `quantities-from-attributes.md`,
    Reading a result; `asset-lifecycle-changes` Quick Rule 7).
14. **On a bundle sized by configuration answers, carry the answers across changes.**
    After each activation, read the root's asset action source rows for node status, and
    run two answer-change amendments in a row with every unchanged answer asserted.
    Without the context rule and trigger the repo ships, unchanged answers reset to their
    defaults (`asset-lifecycle-changes` Quick Rule 2).
15. **Wait for the decision tables to be fresh before pricing,** not only check them.
    The refresh flow returned before the tables were fresh, and a quote priced in that
    window got empty volume and cost lookups with no error (`decision-tables` → Wait for
    fresh tables before pricing). Every gate that prices after a catalog or pricing load
    reruns `check_decision_table_freshness` until none of the tables it reads is Stale
    (`decision-tables` Quick Rule 1).
