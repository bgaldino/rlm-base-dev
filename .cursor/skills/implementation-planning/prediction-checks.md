# Prediction Checks — What to Run Before You Predict

Read this when writing the plan's decisions, rule decision record, live spikes and
golden tests with [implementation-planning](SKILL.md). A prior build tracked every
prediction a blind plan made and recorded each outcome as it was measured (SKILL.md
step 9). Where a prediction was modified or refuted because the planner skipped a step,
that step is a check below. Check 15 sharpens a guard the plans already had: the build
measured why a freshness check alone wasn't enough. Check 16 applies `dro-plans`
guidance, not a measured miss; `dro-plans` holds a composition smoke, a recheck and measured
runtime behaviour, each on one org, and check 16 also cites Help directly for
decomposition scope and quantity. The platform facts live in the domain skills and Help
articles named; this file says when the plan must apply them.

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
   `bundle-children-lifecycle.md`). The same holds for a measured limitation: it is
   trigger (b) only in the shape it was measured in. A measurement whose run didn't
   record a setting the plan changes is outside its measured conditions for that plan.
2. **Name the inputs a documented element is assumed to take.** An element the snapshot
   documents, at a position or with an input the docs don't show, is **Snapshot** when
   nothing contradicts it. List the parameters and context fields the plan assumes, so
   its build gate checks each one. A prior build found a parameter that a skill listed
   as optional, and the build used, refused at creation (`pricing-procedures` →
   `elements/rounding-values.md`, Configuration).
3. **A spike's must-hit is the source's value, not a guess at the platform's.** Where the
   platform measures differently, carry the source value through a stated mapping (such
   as day-based proration), or record the decision that makes the build match the
   source. Where a
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
      `quantities-from-attributes.md`, Checks across top-level lines). If the plan also
      builds group ramps, that container sees every segment's lines at once: a `[0..1]`
      bundle relation together with one-instance types there refused the ramp, so
      cross-line checks compare totals across segments (`ramped-quotes`).
    - Weigh the top-level route against keeping the split inside the bundle. The
      top-level route is the one that was run. Its costs: the rules no longer size those
      lines (the rep or build automation does; the converter only computes their golden
      quantities), a quote without the bundle goes unchecked, and where a container rule
      counts those lines, a root-only amendment without them logged an Error, which
      blocks ordering; amending those assets at quantity change 0 alongside the root
      cleared it, and a root renewal carrying them as No Change lines at quantity 0
      ordered with no message (`asset-lifecycle-changes` Quick Rule 7, one org; a renewal
      without them wasn't run). List the pricing
      steps keyed on the bundle that the moved lines lose, and say how a change to the
      moved lines alone gets checked: such a change without the root raised no rule
      message and ordered (`asset-lifecycle-changes` Quick Rule 7, one org), so a rule that must hold there would need a
      quote-level validation that reads the assets (a custom build) `[inferred]`; adding the root at
      quantity change 0 to such a change wasn't run. Open item 13 in
      `constraint-models` → `quantities-from-attributes.md` lists two in-bundle
      candidates, neither run: choose one only with a spike that also covers the
      answers surviving an answer change (`asset-lifecycle-changes` Quick Rule 2), and
      the top-level route as its fallback.
    - A group ramp of a configurable bundle is a structure too. Every child, One-Time
      included, repeats in every segment of a UI-built ramp, and unticking a child that a
      rule sizes is silently undone. Before predicting a ramp's contract value, name how
      the repeats leave later segments. A root answer that sizes the one-time children to
      0, set in segment 2, reached the later segments and left segment 1 alone; the build
      that worked lowered those groups' minimums to 0 (`ramped-quotes` →
      `bundle-children-lifecycle.md`).

   A prior plan kept such a choice as a component and needed that fallback after its
   lifecycle spikes. Another sent the ramp repeats to a spike whose options didn't
   include the root answer the build used.
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
   ramp segments, amendments and renewals; list each as a golden case, with the count
   each one uses:
    - In a ramp segment (a dated line group), an until-cancelled line counts that
      segment's months, not the whole term. This applies to cost as well as value.
    - On an amendment, it counts the months left from the contract's start. That start
      isn't on the quote: name the mechanism that puts it there (a flow stamping it from
      the amended lines' source assets) and the full reprice that has to follow, because
      the first price is calculated before the stamp lands.
    - If it sums a subset of lines, such as one product line, check that the field
      selecting them is in the pricing context. The sales transaction context has no
      product Family.
    - If amendment quotes go through approval, give each quote-level dimension
      (deal size, margin, and discount when the source measures it on the quote rather
      than per line) a basis there: the change, or the contract after it
      (`advanced-approvals` → `matrix-modeling.md` §1 records a route for the contract
      after it). A ratio taken
      on the change alone can land in a different level from the contract after it, so
      compute each amendment golden's ratio on the chosen basis, and decide what a change
      with revenue at or below zero does.

   See `pricing-setup` → `scenarios/full-term-value.md` and `context-service`. A golden
   that keeps a running total across changes carries each step's platform value next to
   the source's, as check 10 says.

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
    values through the mapping, or a decision makes the build match the source. Carry the
    platform value into every golden derived from those lines too: the change's total,
    running totals, full-term or contract values, and the approval inputs that read them. A
    derived golden built from the source's figure is off by the proration difference at
    every later step, and an approval input read from it can land in a different level.
11. **Round where the source rounds, and nowhere else.** Check the source's arithmetic
    at each step before adding a rounding: one the source doesn't do moves the goldens. A
    compound ramp uplift isn't rounded to the cent (`pricing-procedures` →
    `elements/price-revision-compound-uplift.md`; `ramped-quotes` Quick Rule 10), so if
    the source rounds an uplifted price, a plan that rounds before the uplift needs a
    second rounding after it. That step rounds the base times the cumulative factor once; a
    source that rounds each year and compounds from the rounded price can differ by a cent
    from the third segment on (`ramped-quotes` → `compound-uplift.md`, not told apart in
    the measured runs), so carry both values through a mapping or record a decision.
12. **State the line inputs a pricing step filters on,** as the placing script sends
    them. A commitment-term step read `SubscriptionTerm`, and a line placed with start
    and end dates alone had none, so it got no discount; a header-only Place change
    didn't reprice (`pricing-procedures` → `elements/commitment-term-discount.md`, Line
    inputs on real quotes). State them for every way the plan creates lines: segment
    lines of a UI-built group ramp carried a term of 1 (same file, Line inputs on real
    quotes; for the fix and its limit, `concept-map.md`, Discount for a longer commitment).
    If any gate runs an action with Order output or reprices an order, the pricing gate
    also checks every tag the procedure declares on the Order lens, stock tags included: a declared tag with a
    Quote-lens row and no Order-lens row failed an Order-output action, and a field-less
    Order-lens row cleared it (a tag with no row on either lens passed; one org, cause not
    traced). For a declared tag with a Quote-lens row that the procedure doesn't read, a
    field-less Order-lens row is enough `[inferred]` from the one tag measured; don't add
    rows for every declared tag: one with no row on either lens passed (one org).
    A field-less row leaves the value empty on Order output, so for a tag whose
    value the procedure reads, map a real field on the Order-lens object (`Order` for a
    header tag, `OrderItem` for a line tag) (`pricing-procedures` →
    `operations-and-troubleshooting.md`; `context-service` → `authoring-and-lifecycle.md`;
    `rlm-business-apis` → `backdated-asset-lifecycle.md`).
13. **Assert a refusal where its message appears, and on each path decide whether it
    appears at all.** Place returned success for a configuration it then logged as an
    error; the message can appear only in `RevenueTransactionErrorLog` or a later
    `configure` (`constraint-models` → `quantities-from-attributes.md`, Reading a result).
    A rule can also remove a line instead of refusing. On an amendment that changes a
    root answer, an optional add-on whose requirement no longer held was removed with no
    message (`asset-lifecycle-changes` Quick Rule 7). So for every refusal golden that an
    amendment or renewal reaches, write down how the change arrives (an answer change or
    a line edit) and which form of the rule meets it. Predict the message only where a run
    showed it on that path. Elsewhere assert the line deltas and the stored answers: a rule
    may remove a line the rep didn't touch, and a conflict was reported through a different
    rule than the one broken (`constraint-models` → `quantities-from-attributes.md`, Zero
    for a component a choice excludes). A prior plan predicted a rule's message on an amendment. The answer change removed the
    add-on silently, and a line edit drew a different rule's message.
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
16. **Count an orchestrated fulfilment before predicting it.** For a representative order
    and each lifecycle order, write every dependency as an edge between two step
    instances (with their scopes, items and source lines), and count the expected
    fulfilment lines, steps and edges (`dro-plans` → `authoring-and-deployment.md`). Count
    instances from each technical product's decomposition scope and from the lines the
    configurator places, not from a line's quantity: Order Line Item gives one per line,
    while Order, Bundle and Account give one per order, per bundle within an order, or per account across
    its orders, merging the lines that decompose to the product (for Account, every line of
    the account `[inferred]`, `dro-plans` → `updates-and-runtime.md`), and Custom one per scope
    identifier (unmeasured in `dro-plans`) (Help `ind.dro_decomposition_scope`). Later orders can still carry lines for an Account-scope item (see the
    bullets below). Take each instance's quantity from its
    quantity method: Always One gives each instance quantity 1 (Help
    `ind.product_catalog_create_simple_products`,
    `ind.dro_assetization_in_dynamic_revenue_orchestrator`; `dro-plans` →
    `authoring-and-deployment.md` shows it on Order Line Item scope, and leaves merging
    scopes unmeasured),
    and Aggregate sums the source lines' quantities with no unit-of-measure conversion
    (Help `ind.dro_unit_of_measure_inheritance_and_rounding_values`); quantities on fulfilment
    lines and assets are rounded to DRO's unit-of-measure scale and rounding rules (same
    article; the order of summing and rounding is unstated); where source lines in different
    units feed one Aggregate item, decide where their quantities are converted before
    submission (same article). No method means
    Aggregate and no scope means Order Line Item (Help `ind.dro_creating_a_technical_product`,
    `ind.dro_decomposition_scope`). The count golden has columns for groups, definitions,
    lines with their quantities (and, on lifecycle orders, their actions), steps with
    their scopes and edges with their scopes, a row for each order shape,
    kit and variant the source fulfils, and a predicted row for each lifecycle order. Decide
    each edge's shape like any rule ([knowledge-sources.md](knowledge-sources.md)).
    - Count groups and step definitions per item before step instances. A definition
      belongs to one group, so a step several items need with different predecessors is
      one definition per group (`dro-plans` → `authoring-and-deployment.md`).
    - On each lifecycle order, list the items and steps it creates and each line's
      action: in one run, an amendment built the full step set (`dro-plans` →
      `updates-and-runtime.md`). On one bundle amendment, some unchanged lines came through
      as an add and a cancel netting to zero while another was No Change, so record each
      line's action, quantity and fulfillment asset quantities on the first amendment.
    - Where a later order must act on an item an earlier order created, record the item's
      scope as a decision and check the line actions on the first such order. `dro-plans`
      → `updates-and-runtime.md` (An item across orders) holds what one later new-sale
      order showed (one org), the cross-order-scope inference `[inferred]` from Help, and
      what it leaves unmeasured (an item that must stay one per sold line, custom scopes); spike any the plan relies on.
    - Count the lines that come back on later orders: an Account-scope assetizable item got
      Amend and another got No Change (`dro-plans` → `updates-and-runtime.md`, An item
      across orders, one org; Help sets Amend where a line differs from its fulfillment
      asset), so where a scenario on the item chooses that action, expect its group's steps
      to compose again unless a condition skips them `[inferred]`. A non-assetizable
      Account-scope item got Add with no asset on the same order (same bullet, one org), so
      expect its Add steps to compose on each later new-sale order that carries a line
      decomposing to it `[inferred]`; unmeasured for an Account-scope item on other lifecycle orders (the cancel case below
      didn't record its scope). Cancelling a bundle's root
      asset brought its non-assetizable technical line through as an Add of quantity 0 whose
      Add steps were created and started (same file, Cancel of a non-assetizable technical
      line, one org).
    - Say what happens to an edge whose predecessor isn't on that order's plan, on the
      new sale too where an item is sold only in some configurations; don't assume it is
      re-pointed.
