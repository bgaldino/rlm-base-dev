# Expression Set types (Revenue Cloud)

Progressive-disclosure sub-file of `.cursor/skills/expression-sets/SKILL.md`. Which `interfaceSourceType` values Revenue Cloud uses and how Constraint sets differ.

## <a name="expression-set-types"></a>Expression Set types (Revenue Cloud)

Every Expression Set carries an `interfaceSourceType` (the consuming-cloud
discriminator, on the runtime `ExpressionSet` object) paired with a `usageType`.
The engine enum has 11 members (see the [full enum](#the-full-enum) below), but
**Revenue Cloud uses six** — grounded against the live org
(`SELECT InterfaceSourceType, UsageType, COUNT(Id) FROM ExpressionSet …`) and the
Release 262 dev-guide/Help snapshots (not re-checked against 264):

| `interfaceSourceType` | What it computes / when it runs | Paired `usageType` (live) | Shipped example(s) in this repo | Authoring |
|---|---|---|---|---|
| **PricingProcedure** | The pricing waterfall — list price → discounts → derived/rounded net price. Runs on quote/order repricing. | `DefaultPricing` | `RLM_DefaultPricingProcedure`, `RLM_ProductDiscoveryPricingProcedure`, `RLM_PRM_DISTI_Pricing_Procedure`, `RLM_Price_Distribution_Procedure`, `RLM_Revenue_Management_Recalc_Procedure` | Step graph (this skill); element configuration in `pricing-procedures` |
| **DiscoveryProcedure** | Product Discovery pricing — computes prices shown while browsing/adding products (pre-quote). | `PricingDiscovery` | `RLM_DefaultPricingDiscoveryProcedure`, `Salesforce_Pricing_Discovery_Procedure` | Step graph (this skill) |
| **RatingProcedure** | Usage/consumption rating — turns usage into rated amounts. | `DefaultRating` | `RLM_DefaultRatingProcedure`, `Negotiable_Rating_Procedure` | Step graph (this skill) |
| **RatingDiscoveryProcedure** | Rating discovery — the discovery-phase counterpart for rating. | `RatingDiscovery` | `RLM_DefaultRatingDiscoveryProcedure` | Step graph (this skill) |
| **QualificationProcedure** | Product qualification/disqualification — eligibility gating in Product Discovery. | `ProductQualification` | `RLM_ProductDiscoveryQualificationProcedure` | Step graph (this skill) |
| **Constraint** ⚠ | Product Configurator constraint rules — compatibility/recommendation logic (GA 262 "Product Discovery with Constraint Rules"). | `Constraint` | *(shipped as constraint models, not `expressionSetDefinition` step XML)* | **CML** — see note |

> ⚠ **Constraint is CML-based, not a step graph — use
> [`.cursor/skills/constraint-models/SKILL.md`](../constraint-models/SKILL.md), not this
> skill.** Constraint expression sets are authored in **CML** (Constraint Modeling
> Language) and shipped as a plain-text `.ffxblob`, not as a flat `steps[]` graph. The
> Connect-overlay tooling, the `steps[]`/`parentStep` model, and the script routing in
> this skill **do not apply** to Constraint sets. They surface in the same
> `ExpressionSet`/`interfaceSourceType` enum, so they are listed here for completeness.
>
> **Two rules in this skill are actively misleading for Constraint sets:**
>
> 1. **Quick Rule 7 / DO NOT (“PATCH on an active version is rejected”).** Constraint
>    models fail the *opposite* way: `import_cml` against an **active** version
>    **succeeds** and simply does not redeploy — no error, stale model still running.
>    You get no signal from the import, and there is no separately readable
>    "deployed" artifact either: `ExpressionSetDefinitionVersion.ConstraintModel` is the
>    field `import_cml` writes, so reading it back only confirms the upload. Verify by
>    exercising the configurator.
> 2. **The activation tooling differs.** `scripts/expression_sets/activate_expression_set.py`
>    and the Connect deactivate→PATCH→reactivate cycle are for step-graph sets.
>    Constraint models go through `manage_expression_sets` + `import_cml`.
>    `manage_expression_sets` activates and deactivates a constraint model through
>    `/industries/constraints/{setId}/versions/{versionId}`, which deploys it to the solver; a
>    plain `ExpressionSetVersion.IsActive` update never does. `prepare_constraints` deactivates
>    only AFTER importing. See the constraint-models skill.
>
> Source material: `docs/salesforce/264/dev-guide/` (`cml-*` articles) and the
> Configurator Help suite.

### <a name="the-full-enum"></a>The full enum vs. Revenue Cloud

The `interfaceSourceType` enum (`INTERFACE_SOURCE_TYPES` in
`tasks/expression_set_schema.py` — **the single source of truth**) has 11 members.
The five **not** used by Revenue Cloud belong to other clouds/verticals and are
listed only so an unexpected value isn't mistaken for RC:

- **Not Revenue Cloud:** `EventOrchestration`, `GpaCalculationProcedure`,
  `IntelligentDecisionStudio`, `ItServiceManagement`.
- **Doc/test placeholder (not a real RC type):** `Sample` — appears only as the
  dev-guide's own "Declarative Metadata Sample Definition" example; **0** live
  instances. Do not author RC procedures with it (`usageType: sample` also keeps
  the ES from surfacing in the pricing UI).

Ground truth: the code enum (`tasks/expression_set_schema.py`) →
`validate_expression_set` errors on an out-of-enum value. The
`docs/references/expression-set-connect-api-reference.md` enum list mirrors it.
