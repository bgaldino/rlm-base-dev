# Sizing a Bundle from Answers — Component Quantities from Attributes

Sub-file of the [constraint-models skill](SKILL.md). Read it when a constraint model has to
set component quantities from answers on the bundle, for example one gateway per site,
racks per ten sites rounded up, or service hours computed from other quantities.

The parent skill covers file layout, wiring, deployment and the headless `configure`
check. This file covers only the CML that sizes a bundle and how to test it.

**Claim tags.** `[Dev guide: <article>]` is the 264 developer guide snapshot under
`docs/salesforce/264/dev-guide/articles/`, cited by file name without `.htm.md`.
`[Repo: <file>]` is this repository. `[Measured: <date>, 264]` is a live run on a 264
(API v68.0) scratch org. Items marked **Open — needs live verification** are not settled
by any of these.

The 2026-11-10 measurements come from a temporary probe model: rules added to an active
bundle model, imported and cycled, then read back through `message(...)` values in a
`configure` response after a Place with rules on. The probe tested arithmetic, `ceil()`,
`^`, `configurable = false`, message severity and a decimal-driven cardinality. Along
the way it also observed the `bundlevalidation` warning, the shape of `messages` and what
an inactive model returns, all described below. Nothing else was tested. The 2026-11-03
measurement is an earlier headless test of a different model on a 264 org: placed with
rules off, `configure` returned `success` for a combination that the model rejects with
rules on. The worked example as a whole has not been run. Where
the dev guide and the org disagree, this file follows the org and says so.

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
   **Rounding up:** `ceil()` does nothing inside `constraint(...)`
   `[Measured: 2026-11-10, 264]`. Round up with an integer bracket, which keeps this rule
   and is the choice for answers the rep edits. An inline `ceil()` also rounds up, but its
   variable can't have an explicit domain (see
   [Why `ceil()` isn't in a constraint here](#why-ceil-isnt-in-a-constraint-here)).
4. **Use `int`, not `decimal`, for anything that becomes a line quantity.** `decimal` isn't
   supported for the quote line quantity field `[Dev guide: cml_variable_data_types]`.
5. **Keep data flowing one way:** answers → derived variables → cardinalities. A loop
   through `total()` or `sum()` back into the same relation leaves the aggregate unbound
   `[Dev guide: cml_business-centric_cml_guidelines_quantity_and_aggregation_fun]`.
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
- **DO NOT** put `ceil()` inside `constraint(...)`. It returns its argument unchanged
  there: `ceil(2.30)` on a `decimal(2)` stays 2.30. With `int` operands,
  `constraint(q == ceil(15 / 10))` sets 1, because `/` has already truncated. An `int` set
  equal to `ceil(23 * 0.1)`, a non-integer constant, inside a constraint made the model fail
  to activate `[Measured: 2026-11-10, 264]`. The dev guide's own `ceil()` example is written
  this way `[Dev guide: cml_core_concept_examples]`.
- **DO NOT** use `^` for powers inside a constraint. Even in parentheses
  (`constraint(p == (2 ^ 3))`), it compiles to a false constraint and the model fails to
  activate. Inline, `int p = 2 ^ 3;` gives 8 `[Measured: 2026-11-10, 264]`. Multiply instead.

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
products `[Dev guide: cml_relationship_variable_functions]`. Measured the same way:
`softwaremaintenance[SoftwareMaintenance] == 3` produced one line with `Quantity` 3 in the
`configure` response `[Measured: 2026-11-10, 264]`.

**Check the component's PCM quantity settings.** On that run the component's
`ProductRelatedComponent` had `IsQuantityEditable = false`. `configure` still returned
`success: true`, but with a `bundlevalidation` warning on the line: "The Quantity of the
line item containing product … can't be edited" `[Measured: 2026-11-10, 264]`.

**Open — needs live verification:** whether `IsQuantityEditable = true` clears that
warning; how a large cardinality (600 service hours) displays in the configurator and the
transaction line editor.

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
| Per N, rounded up (bracket) | `constraint(rackQty * 10 >= sites && (rackQty - 1) * 10 < sites, "<message>");` | 23 → 3 `[Measured: 2026-11-10, 264]` |
| Per N, rounded up (inline) | `int rackQty = ceil(<int variable> / 10);` | 23 → 3, with a variable that a constraint set, not a rep-edited answer `[Measured: 2026-11-10, 264]`. No explicit domain; see [Why `ceil()` isn't in a constraint here](#why-ceil-isnt-in-a-constraint-here) |
| Zero unless a choice is made | `constraint(hosting != "OnPrem" -> rackQty == 0, "<message>");` | `[Dev guide: cml_logical_constraints]` |
| Equal to another component's quantity | `constraint(mounts[GatewayMount] == gateways[Gateway], "<message>");` | `[Dev guide: cml_best_practice_access_quantity]`. When both follow one answer, size each from the answer instead (see [Chained derivations](#chained-derivations)) |
| A default the rep can change | `setdefault(<condition>, rel[Type] == defaultQty, "<message>");` | `[Dev guide: cml_setdefault_rule]` `[Dev guide: cml_cml_best_practices]` |

`constraint()` makes the quantity a rule; `setdefault()` makes it a default. The Logical
Constraints page says the engine never overrides a value the user selected, except through
`exclude`, so a user value that breaks a `constraint` produces an error, not a correction
`[Dev guide: cml_logical_constraints]`. Two other pages qualify that: the solver doesn't
override user input "unless no other solution exists" `[Dev guide: cml_cml_best_practices]`
(*Sequence and Configurable*), and the engine changes a variable annotated `Peelable` true,
when that finds a valid configuration, rather than reporting an error; the default is false `[Dev guide: cml_variable_annotations]`.

`setdefault` tries to satisfy its expression only when part of its condition changes or
the parent is new; otherwise it only evaluates `[Dev guide: cml_setdefault_rule]`. The
dev guide calls such defaults "dynamic, overridable" `[Dev guide: cml_cml_best_practices]`.

**Open — needs live verification:** what a rep sees when they edit the quantity of a line
that a `constraint` sizes (error banner, locked field, a silent correction, or something
else), and whether a `setdefault` quantity stays as the rep set it after they change an
unrelated answer.

### Why `ceil()` isn't in a constraint here

The dev guide puts `ceil()` inside a named constraint,
`constraint calculateCeil(requiredCrates == ceil(totalItems / itemsPerCrate));`, with both
operands `int` `[Dev guide: cml_core_concept_examples]`. On a 264 org that form never
rounds up `[Measured: 2026-11-10, 264]`:

| Expression | Inside `constraint(...)` | Inline (`int x = …;` / `decimal(2) x = …;`) |
|---|---|---|
| `15 / 10`, `23 / 10` | 1, and 2.00 into a `decimal(2)`: integer division truncates | `int q = 23 / 10;` → 2 |
| `ceil(15 / 10)` | 1 | — |
| `ceil(<int var 23> / 10)` | — | 3 |
| `ceil(2.30)`, on a `decimal(2)` variable, a literal or a `double(2)` | 2.30, named or unnamed constraint | 3.00, or 3 into an `int` |
| `int == ceil(23 * 0.1)` | Model fails to activate: "couldn't find a solution … for the rule" | 3 |
| `((15 + 99) / 100) * 100` | 100: the round-up-to-a-multiple idiom works | — |

So inside a constraint, integer `/` truncates and `ceil()` is the identity. Inline, `/`
keeps the fraction until the result is stored, and `ceil()` rounds up. That also settles
the dev guide's `((x + 99) / 100) * 100` example `[Dev guide: cml_best_practice_relation_aggregates]`:
it relies on truncation, and inside a constraint it works.

Two forms round up:

- **The integer bracket inside a constraint.** It pins the one integer `q` with
  `N*(q-1) < x <= N*q`, the ceiling of `x / N` for `x >= 0`. It keeps everything in solver
  constraints, so the dev guide's advice to calculate inside constraints still holds
  `[Dev guide: cml_best_practice_calculations]`. The worked example uses it.
- **Inline `ceil()`**, as in `int rackQty = ceil(<int variable> / 10);`. Shorter, but the variable
  is declared by its expression and can't have an explicit domain. The dev guide warns that
  inline derived declarations can leave domains uninitialized
  `[Dev guide: cml_core_concept_examples]` (*Key Considerations for Calculations and
  Aggregations*). Measured only with an input that a constraint set within the same solve,
  not with a rep-edited answer such as `sites`, so the open item below applies.

**Open — needs live verification:** whether an inline `ceil()` recalculates when a rep
changes the PCM attribute it reads in the configurator. Until that is measured, prefer the
bracket for answers the rep edits.

---

## Rounding and number types

| Need | Documented | Measured on 264 |
|---|---|---|
| Round up | `ceil()`: smallest integer >= the argument `[Dev guide: cml_mathematical_functions_numerical_derivation]` | Works inline only; the identity inside `constraint(...)`. See above `[Measured: 2026-11-10, 264]` |
| Integer division | `/` listed with no stated semantics `[Dev guide: cml_constraints]` | Inside a constraint, `int / int` truncates. Inline, the fraction survives until the result is stored, so `int q = 23 / 10` is 2 but `ceil()` of an `int` variable holding 23, divided by 10, is 3 `[Measured: 2026-11-10, 264]` |
| Power | The math-functions page lists `^` as power; the Constraints page lists `^` as XOR `[Dev guide: cml_mathematical_functions_numerical_derivation]` `[Dev guide: cml_constraints]` | Inline, `2 ^ 3` = 8, so the power reading holds there. Inside a constraint, `^` compiled to a false constraint and the model failed to activate `[Measured: 2026-11-10, 264]`; whether it acts as XOR there wasn't tested. Multiply instead |
| Other arithmetic | `+ - * %` (`%` is remainder) `[Dev guide: cml_constraints]` | `+` and `*` in constraints and inline `[Measured: 2026-11-10, 264]` |
| Round down, round to nearest, absolute value | Not documented | Round down is integer `/` inside a constraint. Write the others as a bracket or with `%` |
| Decimal values | `decimal(n)` fixed-point; `double(n)` 64-bit. Each digit of scale multiplies the values the engine may test `[Dev guide: cml_variable_data_types]` `[Dev guide: cml_cml_best_practices]` | — |
| Line quantity | `decimal` isn't supported for the quote line quantity field `[Dev guide: cml_variable_data_types]` | A `decimal(2)` value of 1.50 × 2 set a cardinality of 3 `[Measured: 2026-11-10, 264]`. A fractional result wasn't tested. Keep quantities `int` |

Percentages: inside a constraint, write 15% as integer arithmetic
(`pmHours * 100 >= 15 * base && (pmHours - 1) * 100 < 15 * base`); 752 → 113
`[Measured: 2026-11-10, 264]`. Inline, `int pmHours = ceil(base * 0.15);` also works,
without an explicit domain:
`int x = ceil(23 * 0.1)` gave 3 `[Measured: 2026-11-10, 264]`. Don't write
`constraint(pmHours == ceil(base * 0.15))`: `ceil()` does nothing there, and the constant
form, `int == ceil(23 * 0.1)`, made the model fail to activate. The variable form wasn't
tested.

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

Where order still matters, the dev guide orders a read-calculate-write chain with
`@(sequence = n)` on constraints, lower first
`[Dev guide: cml_business_centric_cml_examples]` (*Resolving Circular Dependencies*).

Size domains from the answer domains. With `sites = [1..200]`, `24 * sites + 80` runs from
104 to 4,880, so `[104..4880]` is the domain, not `[0..99999]`. A smaller domain gives the engine
fewer values to test `[Dev guide: cml_cml_best_practices]` (*Variable Domains*).

The dev guide says to calculate inside constraints, not with inline expressions, for
performance `[Dev guide: cml_best_practice_calculations]` and so that derived domains
initialize `[Dev guide: cml_core_concept_examples]` (*Key Considerations for Calculations
and Aggregations*). Some of its own examples use
inline ones (`int totalWeight = quantity * weightPerUnit;`)
`[Dev guide: cml_cml_best_practices]` (*Dependent Logic*). Both forms evaluate:
`int x = a * b;` gave 150 for 15 × 10 `[Measured: 2026-11-10, 264]`. They don't evaluate
the same way. Inline, `/` keeps the fraction until the result is stored and `ceil()` rounds
up; inside a constraint, `int / int` truncates and `ceil()` does nothing (see
[Why `ceil()` isn't in a constraint here](#why-ceil-isnt-in-a-constraint-here)). Default to
constraints and round up with the bracket. Use an inline `ceil()` only where its input isn't
an answer the rep edits. The performance difference wasn't measured.

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

### Zero for a component a choice excludes

| Rule | When to use it | Source |
|---|---|---|
| `constraint(choice != "X" -> rel[Type] == 0, "<message>");` | The quantity is already rule-owned. A conflicting user value raises the message | `[Dev guide: cml_logical_constraints]` |
| `exclude(<condition>, rel[Type], "<message>");` | A rep may add the item by hand and you want it removed. `exclude` overrides user input; the type must be a leaf | `[Dev guide: cml_exclude_rule]` |

**Open — needs live verification:** whether an `exclude` and a `constraint` that both set
the same relation to zero, under the same condition, behave the same as either alone.
Pick one.

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

The severity argument is case-insensitive: `"warning"` and `"Warning"` both came back as
`messageType: "warning"`, and `"Info"` or no severity came back as `"info"`. A headless
`configure` response tells them apart. `messages` is an object keyed by line Id. Each
entry carries `category` (`configurationrules` for CML, `bundlevalidation` for PCM bundle
checks), `message`, `messageType`, `primaryRecordId` (the quote) and `relatedRecordId`
(the line) `[Measured: 2026-11-10, 264]`.

**Open — needs live verification:** which action counts as the "next step" that a
`Warning` blocks (save, pricing, submit for approval).

---

## Testing it headlessly

Run the parent skill's headless `configure` check
([Validation check 7](SKILL.md#validation-checks)) once per answer set, with a Place step
in front of it (step 1 below).

1. **Place with configuration rules on:** `configurationMethod: Force` with
   `executeConfigurationRules: true`. `configurationMethod` defaults to `Skip`
   `[Dev guide: connect_requests_configurator_preference_input]`, and
   `executeConfigurationRules: true` alone runs nothing at Place `[Repo: .cursor/skills/constraint-models/SKILL.md]`.
   With rules off, `configure` returned `success` for an invalid combination
   `[Measured: 2026-11-03, 264]`.
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
6. **Check the activation result before reading any `configure` result.** The two
   rules above that the solver couldn't satisfy, an `int` equal to `ceil(23 * 0.1)` and
   a `^` inside a constraint, failed when the version was activated
   (`manage_expression_sets` reported "couldn't find a solution … for the rule …" and
   "extra variables [… FalseConstraint]"), and the version stayed **inactive**.
   `configure` against the inactive model then returned `success: true` with no messages,
   which looks like a pass `[Measured: 2026-11-10, 264]`.

`message(...)` output appears in `messages` as described under
[Warnings that don't block](#warnings-that-dont-block) `[Measured: 2026-11-10, 264]`.

**Open — needs live verification:** where a violated `constraint`'s own failure message
appears in a 264 `configure` response (in `messages`, in `errors`, or both).

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

    // Per 10 sites, rounded up; zero unless on-premises.
    // Bracket, not ceil(): ceil() does nothing inside constraint().
    constraint(hosting == "OnPrem" -> rackQty * 10 >= sites && (rackQty - 1) * 10 < sites,
            "Racks: one per 10 sites, rounded up, for {} sites.", sites);
    constraint(hosting != "OnPrem" -> rackQty == 0, "Racks: none unless hosting is OnPrem.");
    constraint(racks[Rack] == rackQty, "Racks: expected {}.", rackQty);

    constraint(userLicenses[UserLicense] == users, "One license per user: expected {}.", users);
    constraint(connectors[Connector] == integrations, "One connector per integration: expected {}.", integrations);

    // Chained: base hours, then project management from the staged variables
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
  skill ([The four records a bundle member needs](SKILL.md#the-four-records-a-bundle-member-needs)).
  With `IsQuantityEditable = false` on a sized component's `ProductRelatedComponent`, a
  CML-set quantity drew a `bundlevalidation` warning `[Measured: 2026-11-10, 264]`. Whether
  `IsQuantityEditable = true` clears it is open (see
  [Cardinality vs reading quantity](#cardinality-vs-reading-quantity)).
- The bracket forms used here gave 3 racks for 23 sites and 113 PM hours for a 752-hour
  base `[Measured: 2026-11-10, 264]`.
- The derived `int` variables could carry `@(configurable = false)`. The dev guide
  disagrees with itself about what that does. The annotation reference says the engine
  can't set the variable `[Dev guide: cml_variable_annotations]`
  `[Dev guide: cml_annotation_example_configurable]`. *Sequence and Configurable* and
  *Dependent Logic* say the solver sets it `[Dev guide: cml_cml_best_practices]`. The org
  sides with the second: a CML-only `@(configurable = false) int` set by
  `constraint(x == 7)` came back as 7 `[Measured: 2026-11-10, 264]`. A
  `configurable = false` variable that maps to a PCM attribute wasn't tested.
- **Open — needs live verification:** whether a rep can see or edit a derived variable in
  the configurator, with or without `@(configurable = false)`.
- **Open — needs live verification:** solve time for the largest answers (200 sites,
  5,000 users, 20 integrations).

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

**Open — needs live verification:** which message a 264 `configure` reports when one state
breaks several rules (the rack and support rows), and whether the `support` relation's
`[1..1]` bound rejects two plans first, with a different message or none, and whether the
engine corrects a hand-set quantity instead of rejecting it. If the bound rejects first,
the message assertion catches it. Then either drop the bound to `[0..1]` or add the
bound's message to the accepted set.

---

## Validation Checks

1. Every derived variable is `int` and is set by its own `constraint`, with an explicit
   domain derived from the answer domains. The one exception is a round-up written as an
   inline `ceil()`, which has no domain.
2. No `constraint(...)` contains `ceil(` or `^`. Run `grep -nE 'ceil\(|\^' <blob>` and
   confirm that no hit is part of a `constraint(...)`, including one that continues onto
   later lines. Hits elsewhere, such as a `^` in a regular expression in a `define`, are
   fine.
3. Every component quantity is a cardinality (`relation[Type] == …`); no rule writes
   `lineItemQuantity`, `ItemEndQuantity` or `this.quantity`.
4. No derived variable depends, directly or through an aggregate, on a cardinality it sets.
5. Each "per N" rule is checked at an exact multiple and one past it.
6. Review notes use `Info`; nothing meant as advice uses `Warning` or `Error`.
7. Headless test: placed with rules on, answers sent with `AttributeName`, every quantity
   asserted, every rejection asserted by the message of a rule it breaks. Then the parent skill's
   [Validation Checks](SKILL.md#validation-checks), including the configurator check that
   the deployed model is the one you changed.
