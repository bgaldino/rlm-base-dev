# Sizing a Bundle from Answers — Component Quantities from Attributes

Sub-file of the [constraint-models skill](SKILL.md). Read it when a constraint model has to
set component quantities from answers on the bundle, for example one gateway per site,
racks per ten sites rounded up, or service hours computed from other quantities.

The parent skill covers file layout, wiring, deployment and the headless `configure`
check. This file covers only the CML that sizes a bundle and how to test it.

**Claim tags.** `[Dev guide: <article>]` is the 264 developer guide snapshot under
`docs/salesforce/264/dev-guide/articles/`, cited by file name without `.htm.md`.
`[Help: <article>]` is the 264 Help snapshot under `docs/salesforce/264/help/articles/`,
cited the same way. `[Repo: <file>]` is this repository. `[Measured: M<n>]` is row M<n> of
[Measured on 264](#measured-on-264), a live run on a 264 (API v68.0) scratch org. Questions
none of these settle are listed once, under [Open items](#open-items). The worked example
as a whole has not been run. Where the dev guide and the org disagree, this file follows
the org and says so.

---

## Quick Rules

1. **Create and remove components with cardinality: `relation[Type] == <expression>`.**
   A cardinality constraint makes the engine add or remove instances to satisfy it
   `[Dev guide: cml_best_practice_access_quantity]`.
2. **Treat `lineItemQuantity`, `ItemEndQuantity` and `this.quantity` as read-only.** Use
   them only in calculation or evaluation rules, never to create components
   `[Dev guide: cml_best_practice_access_quantity]`
   `[Dev guide: cml_using_proxy_variables_constraints]`.
3. **Stage every derived number in an `int` variable with an explicit, small domain,** set
   by a `constraint(...)`, then drive the cardinality from that variable. Derived values
   without explicit domains can fail to initialize
   `[Dev guide: cml_core_concept_examples]`
   `[Dev guide: cml_business-centric_cml_guidelines_quantity_and_aggregation_fun]`.
   Round up with the integer bracket in [Rounding up](#rounding-up), never with `ceil()`
   inside a constraint (see [DO NOT](#do-not)).
4. **Use `int`, not `decimal`, for anything that becomes a line quantity.** `decimal` isn't
   supported for the quote line quantity field `[Dev guide: cml_variable_data_types]`. A
   `decimal(2)` product of 1.50 × 2 did set a cardinality of 3; a fractional result wasn't
   tested `[Measured: M15]`.
5. **Keep data flowing one way:** answers → derived variables → cardinalities. A loop
   through `total()` back into the same relation leaves the aggregate unbound if the loop
   isn't broken
   `[Dev guide: cml_business-centric_cml_guidelines_quantity_and_aggregation_fun]`. The
   dev guide breaks such a loop with `@(sequence = n)` (see
   [Chained derivations](#chained-derivations)); this file avoids the loop instead.
6. **Give every constraint that sizes or derives a quantity its own message,** so a test
   can tell which rule rejected a configuration `[Dev guide: cml_logical_constraints]`.
7. **Test with configuration rules on,** and assert each expected rejection by its own
   message (see [Testing it headlessly](#testing-it-headlessly)).

## DO NOT

- **DO NOT** write `constraint(x[X].lineItemQuantity == 3)` to create or size components.
  Write `constraint(x[X] == 3)` `[Dev guide: cml_best_practice_access_quantity]`.
- **DO NOT** read `lineItemQuantity` or `ItemEndQuantity` at a parent or aggregate scope
  when the product can have several instances. Read it per instance; at an aggregate scope
  it can be unbound or ambiguous `[Dev guide: cml_best_practice_access_quantity]`.
- **DO NOT** write several `setdefault` rules that target the same `relation[Type]`. Only
  the last one evaluates reliably. Combine the conditions into one derived variable and
  one `setdefault` `[Dev guide: cml_cml_best_practices]` (*Consolidate Multiple Default
  Configurations*).
- **DO NOT** use `Warning` severity for a note that must not hold the rep up. `Warning`
  blocks the next step until the rep acts; `Info` doesn't
  `[Dev guide: cml_message_rule]`.
- **DO NOT** leave relation cardinality open (`relation x : X;`). Without bounds the
  engine tries quantities up to 9,999 `[Dev guide: cml_best_practice_cardinality]`
  `[Dev guide: cml_relationships]`.
- **DO NOT** put `ceil()` inside `constraint(...)`. There it returned its argument
  unchanged, and an `int` set equal to `ceil()` of a non-integer constant made the model
  fail to activate `[Measured: M4, M7]`. Round up with the bracket in
  [Rounding up](#rounding-up). The dev guide's own `ceil()` example,
  `constraint calculateCeil(requiredCrates == ceil(totalItems / itemsPerCrate));` with
  `int` operands, is written this way `[Dev guide: cml_core_concept_examples]`.
- **DO NOT** use `^` for powers inside a constraint. The math-functions page lists `^` as
  power and the Constraints page lists it as XOR
  `[Dev guide: cml_mathematical_functions_numerical_derivation]` `[Dev guide: cml_constraints]`.
  Used as a power inside a constraint, `p == 2 ^ 3` compiled to a false constraint and the
  model failed to activate `[Measured: M12]`. Multiply instead.

---

## Cardinality vs reading quantity

| You want to… | Write | Engine behaviour |
|---|---|---|
| Add or remove instances so the quantity matches | `relation[Type] == n` | Configures: adds or removes instances `[Dev guide: cml_best_practice_access_quantity]` |
| Read a line's quantity in a calculation | `int q = this.quantity;` in that type | Read-only, calculation rules only `[Dev guide: cml_using_proxy_variables_constraints]` |
| Validate a quantity already on the line | `lineItemQuantity` / `ItemEndQuantity`, per instance | Validates, doesn't configure `[Dev guide: cml_best_practice_access_quantity]` |
| Count the instances in a relation | `cardinality()` or `count(<condition>)` | `cardinality()` includes the quantity of every instance of that type `[Dev guide: cml_using_proxy_variables_constraints]` |

`relation[Type] == n` sets a **quantity**. The dev guide's `count()` example satisfies
`warranties[Warranty] == 2` by adding one warranty product with quantity 2, not two
products `[Dev guide: cml_relationship_variable_functions]`. The org did the same
`[Measured: M14]`.

**Check the component's PCM quantity settings.** With `IsQuantityEditable = false` on the
component's `ProductRelatedComponent`, a CML-set quantity drew a `bundlevalidation`
warning `[Measured: M16]`.

### `sum()` and `total()` aren't the same

`sum(attr)` multiplies each instance's value by its line quantity; `total(attr)` doesn't
`[Dev guide: cml_relationship_variable_functions]`. When you derive one quantity from
another component's per-unit attribute (hours per connector, say), choose deliberately.
Using `sum()` on an attribute that is already a line total multiplies it by the quantity a
second time.

---

## Deriving quantities from attribute values

The answers (sites, users, integrations) are attributes on the bundle's root product. A
PCM attribute imported into CML takes the attribute's developer name as its variable name
`[Dev guide: cml_best_practice_attribute_name]`.

| Pattern | CML | Source |
|---|---|---|
| One per answer unit | `constraint(gateways[Gateway] == sites, "One gateway per site: expected {}.", sites);` | `[Dev guide: cml_logical_constraints]` (message with `{}` arguments) |
| Per N, rounded up | `constraint(rackQty * 10 >= sites && (rackQty - 1) * 10 < sites, "<message>");` | See [Rounding up](#rounding-up) |
| Zero unless a choice is made | `constraint(hosting != "OnPrem" -> rackQty == 0, "<message>");` | `[Dev guide: cml_logical_constraints]` |
| One per answer unit, only if the rep adds it | `relation security : SecurityAddOn[0..200];` with `constraint(security[SecurityAddOn] > 0 -> security[SecurityAddOn] == sites, "<message>");` | `[Dev guide: cml_annotation_example_sequence]` (Examples 4 and 5). See the note below the table |
| Equal to another component's quantity | `constraint(mounts[GatewayMount] == gateways[Gateway], "<message>");` | `[Dev guide: cml_best_practice_access_quantity]`. When both follow one answer, size each from the answer instead (see [Chained derivations](#chained-derivations)) |
| A default the rep can change | `setdefault(<condition>, rel[Type] == defaultQty, "<message>");` | `[Dev guide: cml_setdefault_rule]` `[Dev guide: cml_cml_best_practices]` |

The "only if the rep adds it" row takes the dev guide's form
`constraint(alternators[Alternator] > 0 -> alternators[Alternator] == alternatorsQty, ...)`
`[Dev guide: cml_annotation_example_sequence]`; the `mouse` example has the same form
`[Dev guide: cml_best_practice_sequence_configurable]`. Those relations have a lower bound
of 1; the row's bound of 0 lets the add-on be absent. The implication holds at 0 and at
`sites`, so the rule alone doesn't require the add-on. What the engine does when a rep
adds it at quantity 1 is [open item 14](#open-items).

`constraint()` makes the quantity a rule; `setdefault()` makes it a default. The Logical
Constraints page says the engine never overrides a value the user selected, except through
`exclude`, so a user value that breaks a `constraint` produces an error, not a correction
`[Dev guide: cml_logical_constraints]`. Two other pages qualify that: the solver doesn't
override user input "unless no other solution exists" `[Dev guide: cml_cml_best_practices]`
(*Sequence and Configurable*), and the engine changes a variable annotated `Peelable` true,
when that finds a valid configuration, rather than reporting an error; the default is
false `[Dev guide: cml_variable_annotations]`.

`setdefault` tries to satisfy its expression only when part of its condition changes or
the parent is new; otherwise it only evaluates `[Dev guide: cml_setdefault_rule]`. The
dev guide calls such defaults "dynamic, overridable" `[Dev guide: cml_cml_best_practices]`.

---

## Rounding up

Use an integer bracket inside a constraint. It pins the one integer `q` with
`N*(q-1) < x <= N*q`, the ceiling of `x / N` for `x >= 0`:

| Need | Constraint | Measured |
|---|---|---|
| `x / N`, rounded up | `constraint(q * N >= x && (q - 1) * N < x, "<message>");` | `x` = 23, `N` = 10 → 3 `[Measured: M9]` |
| `p` percent of `x`, rounded up | `constraint(q * 100 >= p * x && (q - 1) * 100 < p * x, "<message>");` | `x` = 752, `p` = 15 → 113 `[Measured: M10]` |

Give `q` an explicit domain and drive the cardinality from it (Quick Rule 3). The bracket
keeps the calculation inside a constraint, as the dev guide asks
`[Dev guide: cml_best_practice_calculations]`. An inline `int q = ceil(x / N);` also
rounded up `[Measured: M5]`, but its variable can't have an explicit domain, which the dev
guide warns against `[Dev guide: cml_core_concept_examples]` (*Key Considerations for
Calculations and Aggregations*). For `ceil()` inside a constraint, see [DO NOT](#do-not).

---

## Chained derivations

When one quantity depends on others (project-management hours as a share of all other
service hours), compute in stages:

1. Each base quantity in its own `int` variable with an explicit domain, set by its own
   `constraint` `[Dev guide: cml_core_concept_examples]` (*Key Considerations for
   Calculations and Aggregations*).
2. The dependent quantity from those **variables**, not from the relations' cardinalities
   or aggregates. When preferences act on the same relation, staging its aggregates in
   local variables reduces solver oscillation
   `[Dev guide: cml_best_practice_relation_aggregates]`. This file applies the same staging
   to constraint chains.
3. Every cardinality from its variable, last.

Where a quantity must depend on an aggregate of its own relation, the dev guide breaks the
loop with a read-calculate-write chain ordered by `@(sequence = n)` on constraints, lower
first `[Dev guide: cml_business_centric_cml_examples]` (*Resolving Circular
Dependencies*). This file avoids such loops instead (Validation check 4).

Size domains from the answer domains. With `sites = [1..200]`, `24 * sites + 80` runs from
104 to 4,880, so `[104..4880]` is the domain, not `[0..99999]`. A smaller domain gives the
engine fewer values to test `[Dev guide: cml_cml_best_practices]` (*Variable Domains*).

The dev guide says to calculate inside constraints, not with inline expressions, for
performance `[Dev guide: cml_best_practice_calculations]` and so that derived domains
initialize `[Dev guide: cml_core_concept_examples]` (*Key Considerations for Calculations
and Aggregations*), though some of its own examples are inline
`[Dev guide: cml_cml_best_practices]` (*Dependent Logic*). Inline and in-constraint
arithmetic don't evaluate the same way; compare the inline and in-constraint rows of
[Measured on 264](#measured-on-264).

---

## Scope: read quantity per instance

- `this.quantity` is the quantity of the instance it appears in. Use it only in a
  calculation rule `[Dev guide: cml_using_proxy_variables_constraints]`.
- `cardinality()` is the size of the relation, across instances
  `[Dev guide: cml_using_proxy_variables_constraints]`.
- Size the bundle from the **answers** on the root, not from quantities read back off
  child lines. Reading `lineItemQuantity` at the bundle scope when a child has several
  instances can be unbound or ambiguous `[Dev guide: cml_best_practice_access_quantity]`.
- A component inside a product component group (Group Type) is reached through the group
  variable, `group.relation[Type]` `[Dev guide: cml_group_type]`. The dev guide disagrees
  about `parent()` there: the Group Type page reaches the root with `parent(attribute, 1)`
  `[Dev guide: cml_group_type]`; the best-practices page says `parent` isn't supported with
  Group Type `[Dev guide: cml_cml_best_practices]`. Sizing from the root through the group
  variable doesn't need `parent()`.

---

## Exclusions

### Exactly one of a choice group

| Tool | Behaviour | Source |
|---|---|---|
| Relation cardinality `[1..1]` over a base type with subtypes | Bounds the relation; a subtype is then picked with `rel[Subtype] == 1` | `[Dev guide: cml_relationships]` (*skipTypeGeneration* example) |
| A sum of subtype cardinalities | `constraint(support[StandardSupport] + support[PremiumSupport] == 1, "<message>");`, which carries a message a test can assert | `[Dev guide: cml_core_concept_examples]` (adds two cardinalities) |
| Group Type `@(minInstanceQty=1, maxInstanceQty=1)` | Limits **unique instances** chosen from the group. The chosen component can still have a high quantity | `[Dev guide: cml_group_type]` |

Tie the choice to an answer with one implication per subtype, as in the dev guide's
warranty example, each with its own message:
`constraint(supportLevel != "Premium" -> support[PremiumSupport] == 0, "<message>");`
`[Dev guide: cml_logical_constraints]`.

This picks one plan for the whole bundle. It can't express a mixed split, with some sites
on one plan and the rest on another. The dev guide has no such example; how to model one
is [open item 13](#open-items).

### Exactly one plan when each plan is sized per site

The first two rows of the choice-group table above count quantity, not distinct
components. `rel[Type]` and `cardinality()` include the quantity of every instance
`[Dev guide: cml_using_proxy_variables_constraints]`, and a relation's bounds are a
quantity range `[Dev guide: cml_relationships]`. M14 set a cardinality of 3 as one line of
quantity 3 `[Measured: M14]`. So with each plan at `sites`, the sum `== 1` and a `[1..1]`
bound can't hold once `sites` is above 1; that failure itself wasn't run.

| Tool | What the dev guide says it counts | Source |
|---|---|---|
| `rel.count(<condition>)` | "the number of component instances" that match the condition. Another page says that when the condition covers every instance it returns the same value as `cardinality()`. Lines or quantity: [open item 15](#open-items) | `[Dev guide: cml_relationship_variable_functions]` `[Dev guide: cml_using_proxy_variables_constraints]` |
| Group Type `@(minInstanceQty=1, maxInstanceQty=1)` | Unique instances chosen from the group; the chosen component can still have a high quantity. The annotation reference calls it the maximum cardinality for a component in a group | `[Dev guide: cml_group_type]` `[Dev guide: cml_type_annotations]` |

**When an answer picks the plan,** nothing needs counting. Size the chosen plan from the
answer, zero the other, and drop the sum:

```
relation support : Support[1..200];
constraint(supportLevel == "Standard" -> support[StandardSupport] == sites, "<message>");
constraint(supportLevel == "Premium" -> support[PremiumSupport] == sites, "<message>");
constraint(supportLevel != "Standard" -> support[StandardSupport] == 0, "<message>");
constraint(supportLevel != "Premium" -> support[PremiumSupport] == 0, "<message>");
```

`supportLevel` holds one value, so one plan carries `sites` and the other 0. The dev guide
sets a subtype's cardinality behind an implication
(`DutyRating == ... -> engine[PrimePowerEngine] == 1`) `[Dev guide: cml_relationships]`;
here the right side is `sites`, as in the "One per answer unit" row of
[Deriving quantities](#deriving-quantities-from-attribute-values). Not run.

**When the rep picks the plan by adding it,** with no answer behind it, neither row of the
table settles it: `count()`'s unit is unclear, and Group Type needs the plans in a product
component group, while the Relationships page says not to include product component groups
when importing product relationships from PCM `[Dev guide: cml_relationships]`. This case
is [open item 15](#open-items).

### Zero for a component a choice excludes

| Rule | When to use it | Source |
|---|---|---|
| `constraint(choice != "X" -> rel[Type] == 0, "<message>");` | The quantity is already rule-owned. A conflicting user value raises the message | `[Dev guide: cml_logical_constraints]` |
| `exclude(<condition>, rel[Type], "<message>");` | A rep may add the item by hand and you want it removed. `exclude` overrides user input; the type must be a leaf | `[Dev guide: cml_exclude_rule]` |

Pick one per relation; using both is an [open item](#open-items).

---

## Warnings that don't block

| Severity | Runtime behaviour | Source |
|---|---|---|
| `Info` (the default) | Gray banner; no action needed to continue | `[Dev guide: cml_message_rule]` |
| `Warning` | Yellow banner; the rep can continue the current task but is blocked from the next step until they act | `[Dev guide: cml_message_rule]` |
| `Error` | Red banner; blocks the task, **except** in the Transaction Line Editor, where the rep can still save | `[Dev guide: cml_message_rule]` |

A review note for a combination that is allowed but unusual is an `Info` message:

```
message(integrations > 10 && supportLevel == "Standard",
        "Review: {} integrations on Standard support. Premium is usual above 10.",
        integrations, "Info");
```

Syntax: `message(condition, string, arg, …, severity)`
`[Dev guide: cml_message_rule]`. A `preference(...)` that can't be met also reports at
`Info` severity `[Dev guide: cml_preference_rule]`, but a preference also moves the
solver; a `message` only reports.

`"warning"` and `"Warning"` both came back as `warning`, and a headless `configure`
response reports the severity per line in `messages` `[Measured: M18, M19]`.

---

## Testing it headlessly

Run the parent skill's headless `configure` check
([Validation check 7](SKILL.md#validation-checks)) once per answer set, with a Place step
in front of it (step 1 below).

1. **Place with configuration rules on:** `configurationMethod: Force` with
   `executeConfigurationRules: true`. `configurationMethod` defaults to `Skip`
   `[Dev guide: connect_requests_configurator_preference_input]`, and
   `executeConfigurationRules: true` alone runs nothing at Place
   `[Repo: .cursor/skills/constraint-models/SKILL.md]`. With rules off, `configure`
   returned `success` for an invalid combination `[Measured: M21]`.
2. **Send every answer with its `AttributeName`.** Without it the engine can't match the
   value to the CML variable and applies the CML default
   `[Dev guide: cml_best_practice_attribute_name]`. A missing name sizes the bundle from
   the default (often the lowest value in the domain), which can still pass a weak
   assertion.
3. **Call `configure` with `executeConfigurationRules: true`** and require
   `success: true`, `solverStatus: "success"`, `errors: []`
   `[Repo: .cursor/skills/constraint-models/SKILL.md]`.
4. **Assert every component's quantity**, including the zeros, against a hand-computed
   table (see the worked example). Pick answers on each rounding boundary: exact multiples
   (`sites = 10`) and one past (`sites = 11`).
5. **For each rejection, submit the conflicting state and assert that the response message
   is the text of a rule that state breaks,** not merely that the call failed. When a state
   breaks several rules, accept any of their messages and no other. The solver can reject
   the right case for a different reason. That is why every constraint in the worked
   example has its own message.
6. **Check the activation result before reading any `configure` result.** A model that
   failed activation stayed inactive, and `configure` then returned `success: true` with
   no messages, which looks like a pass `[Measured: M20]`.

---

## Examples

### Worked example — a fictional "Field Operations Platform" bundle

**Fictional.** No product, catalog or customer in this repository has these names. Sized
by three answers on the root product, plus two choices:

| Component | Quantity rule |
|---|---|
| Gateway | one per site |
| Gateway mount | one per site, so equal to the gateway quantity |
| Rack | on-premises hosting only: ceil(sites / 10); otherwise 0 |
| User license | one per user |
| Connector | one per integration |
| Implementation service (hours) | 24 × sites + 80 |
| Integration service (hours) | 40 × integrations |
| Project management (hours) | ceil(15% of implementation + integration hours) |
| Support plan | exactly one: Standard or Premium, by answer |

```
type LineItem;

type FieldOpsPlatform : LineItem {
    // Answers: PCM attributes on the root product
    int sites = [1..200];
    int users = [1..5000];
    int integrations = [0..20];
    string hosting = ["Cloud", "OnPrem"];
    string supportLevel = ["Standard", "Premium"];

    // Derived values: explicit, smallest domains; set only by constraints
    int rackQty = [0..20];
    int implHours = [104..4880];
    int integrationHours = [0..800];
    int pmHours = [16..852];

    relation gateways : Gateway[1..200];
    relation mounts : GatewayMount[1..200];
    relation racks : Rack[0..20];
    relation userLicenses : UserLicense[1..5000];
    relation connectors : Connector[0..20];
    relation implementation : ImplementationService[104..4880];
    relation integrationSvc : IntegrationService[0..800];
    relation projectMgmt : ProjectManagement[16..852];
    relation support : Support[1..1];

    // One per site; mounts follow the same answer, not the gateway cardinality
    constraint(gateways[Gateway] == sites, "One gateway per site: expected {}.", sites);
    constraint(mounts[GatewayMount] == sites, "One mount per site: expected {}.", sites);

    // Per 10 sites, rounded up with the bracket; zero unless on-premises
    constraint(hosting == "OnPrem" -> rackQty * 10 >= sites && (rackQty - 1) * 10 < sites,
            "Racks: one per 10 sites, rounded up, for {} sites.", sites);
    constraint(hosting != "OnPrem" -> rackQty == 0, "Racks: none unless hosting is OnPrem.");
    constraint(racks[Rack] == rackQty, "Racks: expected {}.", rackQty);

    constraint(userLicenses[UserLicense] == users, "One license per user: expected {}.", users);
    constraint(connectors[Connector] == integrations, "One connector per integration: expected {}.", integrations);

    // Chained: base hours, then project management (15 percent, bracket) from the staged variables
    constraint(implHours == 24 * sites + 80, "Implementation hours: 24 per site plus 80.");
    constraint(integrationHours == 40 * integrations, "Integration hours: 40 per integration.");
    constraint(pmHours * 100 >= 15 * (implHours + integrationHours)
            && (pmHours - 1) * 100 < 15 * (implHours + integrationHours),
            "Project management hours: 15 percent of implementation and integration hours, rounded up.");
    constraint(implementation[ImplementationService] == implHours, "Implementation hours: expected {}.", implHours);
    constraint(integrationSvc[IntegrationService] == integrationHours, "Integration hours: expected {}.", integrationHours);
    constraint(projectMgmt[ProjectManagement] == pmHours, "Project management hours: expected {}.", pmHours);

    // Exactly one support plan, chosen by the answer
    constraint(supportLevel != "Standard" -> support[StandardSupport] == 0, "Standard support needs the Standard answer.");
    constraint(supportLevel != "Premium" -> support[PremiumSupport] == 0, "Premium support needs the Premium answer.");
    constraint(support[StandardSupport] + support[PremiumSupport] == 1, "Choose exactly one support plan.");

    // Non-blocking review note
    message(integrations > 10 && supportLevel == "Standard",
            "Review: {} integrations on Standard support. Premium is usual above 10.",
            integrations, "Info");
}

type Gateway : LineItem;
type GatewayMount : LineItem;
type Rack : LineItem;
type UserLicense : LineItem;
type Connector : LineItem;
type ImplementationService : LineItem;
type IntegrationService : LineItem;
type ProjectManagement : LineItem;
type Support : LineItem;
type StandardSupport : Support;
type PremiumSupport : Support;
```

Notes on the model:

- The relation lower bounds follow the derived domains. `implementation` can't be below 104
  because `implHours` can't. Keep the two in step when you change an answer domain.
- Each component is a bundle member, so it still needs the four records in the parent
  skill ([The four records a bundle member needs](SKILL.md#the-four-records-a-bundle-member-needs)),
  and the PCM quantity settings under
  [Cardinality vs reading quantity](#cardinality-vs-reading-quantity).
- The derived `int` variables could carry `@(configurable = false)`. The dev guide
  disagrees with itself about what that does. The annotation reference says the engine
  can't set the variable `[Dev guide: cml_variable_annotations]`
  `[Dev guide: cml_annotation_example_configurable]`. *Sequence and Configurable* and
  *Dependent Logic* say the solver sets it `[Dev guide: cml_cml_best_practices]`. The org
  sides with the second `[Measured: M17]`.

Expected quantities (hand-computed from the rules above; the whole model has not been run):

| Answers | Gateway / mount | Rack | License | Connector | Impl. h | Integ. h | PM h | Support | Review note |
|---|---|---|---|---|---|---|---|---|---|
| 23 sites, 180 users, 3 int., OnPrem, Standard | 23 / 23 | 3 | 180 | 3 | 632 | 120 | 113 (752 × 15% = 112.8) | Standard 1, Premium 0 | no |
| 10 sites, 50 users, 12 int., OnPrem, Standard | 10 / 10 | 1 (exact multiple) | 50 | 12 | 320 | 480 | 120 (800 × 15% = 120, exact) | Standard 1, Premium 0 | **yes, Info** |
| 11 sites, 50 users, 0 int., OnPrem, Premium | 11 / 11 | 2 (one past a multiple) | 50 | 0 | 344 | 0 | 52 (344 × 15% = 51.6) | Premium 1, Standard 0 | no |
| 11 sites, 50 users, 0 int., Cloud, Premium | 11 / 11 | 0 (Cloud) | 50 | 0 | 344 | 0 | 52 (344 × 15% = 51.6) | Premium 1, Standard 0 | no |

Rejections to assert by message. Where a state breaks more than one rule, accept any of
those rules' messages and no other:

| Submit | Expect one of |
|---|---|
| 23 sites, OnPrem, rack line set to 2 by hand | `Racks: expected 3.`, `Racks: one per 10 sites, rounded up, for 23 sites.` |
| Standard answer, both support plans on the bundle | `Choose exactly one support plan.`, `Premium support needs the Premium answer.` |
| 10 sites, gateway line set to 9 by hand | `One gateway per site: expected 10.` |

If the `support` relation's `[1..1]` bound rejects two plans first (an
[open item](#open-items)), the message assertion catches it. Then either drop the bound to
`[0..1]` or add the bound's message to the accepted set.

---

## Measured on 264

The 2026-11-10 rows come from a temporary probe model on a 264 (API v68.0) scratch org:
rules added to an active bundle model, imported and cycled, then read back through
`message(...)` values in a `configure` response after a Place with rules on. Row M21 is an
earlier headless test of a different model. Nothing else in this file was run.

| # | Run | Result | Date |
|---|---|---|---|
| M1 | `15 / 10` and `23 / 10` inside `constraint(...)` | 1, and 2.00 into a `decimal(2)`: `int / int` truncated | 2026-11-10 |
| M2 | `int q = 23 / 10;` inline | 2 | 2026-11-10 |
| M3 | `ceil(15 / 10)` inside `constraint(...)` | 1 | 2026-11-10 |
| M4 | `ceil(2.30)` inside `constraint(...)`, on a `decimal(2)` variable, a literal or a `double(2)`, in a named or unnamed constraint | 2.30 | 2026-11-10 |
| M5 | `ceil(<int variable> / 10)` inline, the variable holding 23 and set by a constraint in the same solve | 3 | 2026-11-10 |
| M6 | `ceil(2.30)` inline | 3.00, or 3 into an `int` | 2026-11-10 |
| M7 | `int == ceil(23 * 0.1)` inside `constraint(...)`; `int x = ceil(23 * 0.1);` inline | Inside: the model failed to activate, "couldn't find a solution … for the rule". Inline: 3 | 2026-11-10 |
| M8 | `((15 + 99) / 100) * 100` inside `constraint(...)` | 100 | 2026-11-10 |
| M9 | `q * 10 >= x && (q - 1) * 10 < x` inside `constraint(...)`, `x` = 23 | 3 | 2026-11-10 |
| M10 | `q * 100 >= 15 * x && (q - 1) * 100 < 15 * x` inside `constraint(...)`, `x` = 752 | 113 | 2026-11-10 |
| M11 | `int p = 2 ^ 3;` inline | 8 | 2026-11-10 |
| M12 | `constraint(p == 2 ^ 3)`, with and without parentheses | A false constraint; the model failed to activate, "extra variables [… FalseConstraint]". Whether `^` acts as XOR wasn't tested | 2026-11-10 |
| M13 | `int x = a * b;` inline, 15 × 10; `+` and `*` in constraints and inline | 150; both operators evaluated | 2026-11-10 |
| M14 | `softwaremaintenance[SoftwareMaintenance] == 3` | One line with `Quantity` 3 in the `configure` response | 2026-11-10 |
| M15 | A `decimal(2)` value of 1.50 × 2 driving a cardinality | Cardinality 3: one line, quantity 3 | 2026-11-10 |
| M16 | The component in M14, with `IsQuantityEditable = false` on its `ProductRelatedComponent` | `success: true`, plus a `bundlevalidation` warning on the line: "The Quantity of the line item containing product … can't be edited" | 2026-11-10 |
| M17 | A CML-only `@(configurable = false) int` set by `constraint(x == 7)`. A variable that maps to a PCM attribute wasn't tested | 7 | 2026-11-10 |
| M18 | `message(...)` severity `"warning"`, `"Warning"`, `"Info"` and none | `messageType` `"warning"`, `"warning"`, `"info"` and `"info"` | 2026-11-10 |
| M19 | Shape of `messages` in the `configure` response | An object keyed by line Id. Each entry carries `category` (`configurationrules` for CML, `bundlevalidation` for PCM bundle checks), `message`, `messageType`, `primaryRecordId` (the quote) and `relatedRecordId` (the line) | 2026-11-10 |
| M20 | `configure` after the models in M7 and M12 failed activation | The version stayed inactive; `configure` returned `success: true` with no messages | 2026-11-10 |
| M21 | A different model, placed with rules off, then `configure` | `success` for a combination the model rejects with rules on | 2026-11-03 |

---

## Open items

Each needs a live 264 org:

1. Whether `IsQuantityEditable = true` clears the `bundlevalidation` warning in M16.
2. How a large cardinality (600 service hours) displays in the configurator and the
   Transaction Line Editor.
3. What a rep sees when they edit the quantity of a line that a `constraint` sizes (error
   banner, locked field, a silent correction, or something else), and whether a
   `setdefault` quantity stays as the rep set it after they change an unrelated answer.
4. Whether an inline `ceil()` recalculates when a rep changes the PCM attribute it reads.
5. Whether an `exclude` and a `constraint` that both set the same relation to zero, under
   the same condition, behave the same as either alone.
6. Which action counts as the "next step" that a `Warning` blocks (save, pricing, submit
   for approval).
7. Where a violated `constraint`'s own failure message appears in a `configure` response
   (in `messages`, in `errors`, or both).
8. Which message `configure` reports when one state breaks several rules (the rack and
   support rejection rows); whether the `support` relation's `[1..1]` bound rejects two
   plans first, with a different message or none; and whether the engine corrects a
   hand-set quantity instead of rejecting it.
9. Whether a rep can see or edit a derived variable in the configurator, with or without
   `@(configurable = false)`.
10. Solve time for the worked example's largest answers (200 sites, 5,000 users, 20
    integrations).
11. Whether a literal `%` in a message string is passed through or read as a Java format
    specifier. The dev guide documents Java format for these strings
    `[Dev guide: cml_logical_constraints]`; the worked example avoids `%`.
12. Whether a sizing model re-derives service quantities on an amendment, both when the
    root's sizing answer changes (`sites` from 23 to 30, say) and when the amendment
    changes only a line quantity. The sources stop short of it. A future-dated order with
    CML products can be amended, but the amendment "doesn't conform to all the rules"
    `[Help: ind.qocal_future_dated_order_amendments_important_considerations]`. The
    Constraint Rules Engine setup copies the engine's `ConstraintEngineNodeStatus` from the
    source asset's latest asset action source onto lines that a quote or order action
    creates `[Help: ind.product_configurator_set_up_constraint_engine_prerequisites]`; this
    repo ships the quote-line trigger
    `[Repo: unpackaged/post_constraints/triggers/RLM_QuoteItemTrigger.trigger]`.
    Configurator requests take a `validateAmendRenewCancel` option that runs amend, renew
    and cancel validations `[Dev guide: connect_requests_configuration_options_input]`.
    None says which rules run on an amendment or whether a cardinality is solved again.
13. How to model a mixed per-site plan split, which
    [Exactly one of a choice group](#exactly-one-of-a-choice-group) can't express.
    Candidates, neither in the dev guide nor run: an answer per plan (a site count each,
    constrained to sum to `sites`, each driving its plan's cardinality), or per-site child
    instances that each carry a plan.
14. For an add-on sized `rel[Type] > 0 -> rel[Type] == sites` with a lower bound of 0
    ([Deriving quantities](#deriving-quantities-from-attribute-values)): whether a rep's add
    at quantity 1 is raised to `sites`, removed, or rejected with the message, and whether
    the add-on follows a later change to `sites`.
15. How to require exactly one plan, each sized per site, when the rep picks the plan by
    adding it ([Exactly one plan when each plan is sized per site](#exactly-one-plan-when-each-plan-is-sized-per-site)).
    Unsettled: whether `count(<condition>)` counts lines or quantity; whether Group Type
    `maxInstanceQty=1` admits one plan line of quantity `sites`, given that the two dev-guide
    pages describe it differently. A candidate in neither source: one exclusion per pair of
    plans, such as `support[StandardSupport] > 0 -> support[PremiumSupport] == 0`. None run.

---

## Validation Checks

1. Every derived variable is `int`, has an explicit domain derived from the answer
   domains, and is set by its own `constraint`. Every round-up is a bracket.
2. No `constraint(...)` contains `ceil(`, or `^` used as a power. Run
   `grep -nE 'ceil\(|\^' <blob>` and confirm that no such hit is part of a
   `constraint(...)`, including one that continues onto later lines. Hits elsewhere, such
   as a `^` in a regular expression in a `define`, are fine.
3. Every component quantity is a cardinality (`relation[Type] == …`); no rule writes
   `lineItemQuantity`, `ItemEndQuantity` or `this.quantity`.
4. No derived variable depends, directly or through an aggregate, on a cardinality it sets.
5. Each "per N" rule is checked at an exact multiple and one past it.
6. Review notes use `Info`; nothing meant as advice uses `Warning` or `Error`.
7. Headless test: placed with rules on, answers sent with `AttributeName`, every quantity
   asserted, every rejection asserted by the message of a rule it breaks. Then the parent
   skill's [Validation Checks](SKILL.md#validation-checks), including the configurator
   check that the deployed model is the one you changed.
