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
as a whole has not been run, but a model built on its patterns has (rows M22 to M33).
Where the dev guide and the org disagree, this file follows the org and says so.

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
8. **Annotate each component type a rule sizes `@(split = false)`,** unless its lines must
   carry different attribute values. Without it, a downward hand edit split the line
   instead of being rejected `[Measured: M22]`. See [One line per component](#one-line-per-component-split--false).
9. **Set `property maxRelationSize` when any relation can exceed 9,999.** That is the
   default cap on every relation, whatever its declared bounds `[Measured: M25]`
   `[Dev guide: cml_relationships]`.

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
- **DO NOT** declare a bound above 9,999 and expect it to hold. 9,999 is the default
  `maxRelationSize`, and it caps a bounded relation too: a cardinality constraint asking
  for more failed with the sizing rule's message, which reads like a rule rejection, not
  a limit `[Measured: M25]`. Raising the PCM `MaxQuantity` didn't lift it; a top-level
  `property maxRelationSize = <n>;` did `[Measured: M26]`.
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
products `[Dev guide: cml_relationship_variable_functions]`. The org did the same `[Measured: M14]`.
A line already on the quote can change that; see
[One line per component](#one-line-per-component-split--false).

**Check the component's PCM quantity settings.** With `IsQuantityEditable = false` on the
component's `ProductRelatedComponent`, a CML-set quantity drew a `bundlevalidation`
warning `[Measured: M16]`, and a hand edit of that line wrote an error log that blocked
the order `[Measured: M31]`.

### `sum()` and `total()` aren't the same

`sum(attr)` multiplies each instance's value by its line quantity; `total(attr)` doesn't
`[Dev guide: cml_relationship_variable_functions]`. When you derive one quantity from
another component's per-unit attribute (hours per connector, say), choose deliberately.
Using `sum()` on an attribute that is already a line total multiplies it by the quantity a
second time.

---

## One line per component: `@(split = false)`

The `split` type annotation decides how the engine reaches a relation's quantity. Unset,
a relation can hold several instances of the type with different quantities; `false`
keeps one instance and adds quantity to it; `true` makes every instance quantity 1
`[Dev guide: cml_annotation_example_split]` `[Dev guide: cml_type_annotations]`.

| Case | Unset (default) | `@(split = false)` |
|---|---|---|
| A default component, added at 1 by Place with defaults on | Kept at 1; the solver added a line for the rest (1 + (n − 1) for a rule of n) `[Measured: M22]` | One line at the rule's quantity `[Measured: M23]` |
| A rep adds an optional add-on at quantity 1 | Kept; a second line for the rest `[Measured: M22]` | One line, raised to the rule's quantity `[Measured: M23]` |
| A hand edit of a sized line, down | Kept; a second line for the difference (n edited to m became m + (n − m)). No rule message; at most a `bundlevalidation` group-range warning (see below) `[Measured: M22]` | Rejected with the rule's message `[Measured: M23]` |
| A hand edit of a sized line, up | Not measured | Rejected with the rule's message `[Measured: M23]` |
| The configurator UI | A default component split into two instances (1 + the rest); non-default children stayed one instance `[Measured: M24]` | One line per component at the rule's quantity, defaults kept, no warning; a changed answer resized each line `[Measured: M24]` |

Where the PCM component groups had a quantity range, each split group drew a
`bundlevalidation` group-range warning `[Measured: M22]`; don't rely on it to detect a
split, assert the line count. "Rejected" means flagged, not undone: Place saved the edit (read back
for one downward edit) `[Measured: M23]`; read the message as in [Reading a result](#reading-a-result).

Put the annotation on each leaf type that is a sized component (in the worked example,
every type but the abstract `Support`). Leave it off a type whose lines must carry
different attribute values: `split = false` allows only one instance
`[Dev guide: cml_annotation_example_split]`. Group ramps are
[open item 15](#open-items).

---

## Raising the 9,999 cap: `maxRelationSize`

`maxRelationSize` is the largest cardinality of any single relation in the model. Its
default is 9,999 and its maximum 1,073,741,824. It is a model-level `property`, written
before the types `[Dev guide: cml_relationships]` (*Set Maximum Relationship Size*):

```
property maxRelationSize = 20000;

type LineItem;
type Root : LineItem {
    int hours = [0..20000];
    relation services : ServiceHours[0..20000];
    constraint(services[ServiceHours] == hours, "Service hours: expected {}.", hours);
}
@(split = false)
type ServiceHours : LineItem;
```

Set it to the largest upper bound you declare, not higher. The dev guide warns that an
overly high limit lets the engine backtrack through the whole range on a conflict
`[Dev guide: cml_relationships]`. The cap applies to relations only: a CML-only `int` of
more than 9,999 solved without it `[Measured: M25]`. Test the answer that produces the
largest quantity; nothing below the cap shows the problem.

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
`sites`, so the rule alone doesn't require the add-on. What happens when a rep adds it
depends on `split`; see [One line per component](#one-line-per-component-split--false).

`constraint()` makes the quantity a rule; `setdefault()` makes it a default. The Logical
Constraints page says the engine never overrides a value the user selected, except through
`exclude`, so a user value that breaks a `constraint` produces an error, not a correction
`[Dev guide: cml_logical_constraints]`. On the org, that depends on `split`; see
[One line per component](#one-line-per-component-split--false). Two other pages qualify that: the solver doesn't
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
- **Copying a root answer down to the children.** When the components sit in PCM product
  component groups and the model declares no group types, `parent(<attr>)` with no level
  reached the root `[Measured: M27]`:

  ```
  type Root : LineItem {
      string region = ["North", "South"];
      relation software : Software[0..500];
  }
  @(split = false)
  type Software : LineItem {
      string region = parent(region);
  }
  ```

  The child product must carry the same attribute (the same attribute definition, so the
  same CML name), for example through a second classification. Only the root's answer was
  sent; the engine wrote it to each child's attribute record, so a price-impacting child
  attribute could price from it, and editing the root's answer re-derived the children.
  With no parent in the model to read, nothing was copied: under a bundle root that isn't
  a type in the model, the children kept their attribute default; a child placed alone got
  no attribute record. Both solved with no message `[Measured: M28]`.

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
| `rel.count(<condition>)` | "the number of component instances" that match the condition. Another page says that when the condition covers every instance it returns the same value as `cardinality()`. Lines or quantity: [open item 14](#open-items) | `[Dev guide: cml_relationship_variable_functions]` `[Dev guide: cml_using_proxy_variables_constraints]` |
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
is [open item 14](#open-items).

### Zero for a component a choice excludes

| Rule | When to use it | Source |
|---|---|---|
| `constraint(choice != "X" -> rel[Type] == 0, "<message>");` | The quantity is already rule-owned. A conflicting user value raises the message | `[Dev guide: cml_logical_constraints]` |
| `exclude(<condition>, rel[Type], "<message>");` | A rep may add the item by hand and you want it removed. `exclude` overrides user input; the type must be a leaf | `[Dev guide: cml_exclude_rule]` |

Pick one per relation; using both is an [open item](#open-items).

---

## Checks across top-level lines: a virtual `Quote` container

A rule that spans lines with no parent in common (a plan sold as its own line beside the
bundle, say) goes on a virtual container that holds each of them as a relation
`[Dev guide: cml_best_practice_virtual_quote_root]`. The shipped QuantumBit bundle model has
one `[Repo: datasets/constraints/qb/QuantumBitBundle/blobs/ESDV_QuantumBitBundle_V1.ffxblob]`.
Container relations have no `ProductRelatedComponent`, so no `Port` association
([SKILL.md → Ports are per bundle relation](SKILL.md#ports-are-per-bundle-relation-not-per-type)).

```
@(virtual = "true")
type Quote {
    @(sourceContextNode = "SalesTransaction.SalesTransactionItem")
    relation platform : Platform[0..1] {
        platformSites = total(sites);
    }
    @(sourceContextNode = "SalesTransaction.SalesTransactionItem")
    relation basicPlan : BasicPlan[0..500];
    @(sourceContextNode = "SalesTransaction.SalesTransactionItem")
    relation proPlan : ProPlan[0..500];

    int qSites = [0..500];
    constraint(qSites == platform.platformSites);

    message(qSites > 0 && basicPlan[BasicPlan] + proPlan[ProPlan] != qSites,
            "Cover every site with exactly one plan.", "Error");
}
```

- **Give every container relation
  `@(sourceContextNode = "SalesTransaction.SalesTransactionItem")`.** The annotation names
  the context path of a virtual container's instances
  `[Dev guide: cml_relationship_annotations]`; the dev guide's virtual-root example omits
  it. Without it no line attached to the container: Place and `configure` succeeded, the
  container's own rules ran, and every rule on the line types silently stopped
  `[Measured: M34]`.
- **Check across lines with `message(..., "Error")`, not constraints.** Constraints on a
  container relation to top-level lines didn't refuse a rep's lines: the solver rewrote
  them and added instances, once a second bundle root, to satisfy the rule. An `Error`
  message refused without moving anything: an error log row with its text, as in
  [Reading a result](#reading-a-result) `[Measured: M35]`. Bound the bundle relation
  `[0..1]`.
- **Don't add `closeRelation = true` to a relation the container aggregates.** With it,
  `total()` and `max()` on that relation failed with "There's a goal execution error in
  your CML code" instead of the rule's message `[Measured: M36]`.
- **Read a bundle's child quantity through the relation path** (`platform.addOns[AddOn]`)
  rather than staging it in an `int` on the bundle set equal to the cardinality. In one
  model, that `int` changed how the solver met an add-on rule: it dropped a default
  add-on instead of raising it. Seen twice in that model only `[Measured: M37]`.
- A quote that holds the plan lines but not the bundle (an amendment of the plan assets
  alone, say) has nothing in `platform`, so this check doesn't compare the plans with
  `sites` there.
- `validate_cml` warns "Missing port association" for each container relation and
  "Missing type association" for the container type `[Repo: tasks/rlm_cml.py]`
  `[Measured: M37]`. Those warnings are expected.

---

## Answers on an amendment

An amendment that changed a root answer re-derived the children: the amendment lines
carried the quantity changes `[Measured: M38]`. What it keeps of the other answers depends
on the engine's node status, which records which answers the rep set (per answer,
`cfgStatus` `User`, `Default` or `Engine`); the values themselves come from the line
attributes `[Measured: M39]`. The Constraint Rules Engine setup copies the node status
from the source asset's latest asset action source onto new quote or order lines
`[Help: ind.product_configurator_set_up_constraint_engine_prerequisites]`; this repo ships
the quote-line trigger and the node-status fields
`[Repo: unpackaged/post_constraints/triggers/RLM_QuoteItemTrigger.trigger]`.

Measured on 264 `[Measured: M39]`:

- Activation filled `AssetActionSource` node status only when the context definition had
  an order → asset rule: `AssetActionSource` node status from `SalesTransactionItem` node
  status, in `AssetToSalesTransactionMapping`. Help's Constraint Rules Engine
  context-definition article lists only the asset → transaction rule
  `[Help: ind.product_configurator_set_up_constraint_engine_context_definitions]`, and so
  does this repo's plan `[Repo: datasets/context_plans/ConstraintEngineNodeStatus]`.
- Even with that rule, rows made from an order item detail stayed blank. An answer change
  activates as a cancel-and-reprice pair whose rows reference order item details, so the
  next amendment started blank again.
- With a blank node status, an amendment that edited one answer reset every answer it
  didn't send to its CML default, and re-derived the children from those defaults. An
  amendment that changed only a line quantity, with no answer in the request, was
  unaffected.

So, before amending a CML bundle's answers:

1. **Check** that the root's latest `AssetActionSource` rows carry the node status
   (`RLM_ConstraintEngineNodeStatus__c` in this repo). It's a long-text field: read it,
   since SOQL can't filter on it. Check again after each activation in a multi-step
   replay.
2. **If it's blank,** backfill it from the order item's value before amending
   `[Measured: M39]`, or send every answer that differs from its CML default in the
   amendment request, not only the changed one (follows from the reset; not run).

The fix in this repo, an order → asset context rule plus a before-insert trigger on
`AssetActionSource` that fills detail-sourced rows, is a separate change; check whether
the org has it before relying on it. Assets activated before it keep blank rows.

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
2. **Send each answer so it binds, then check that it did.** In a Place graph, a
   `QuoteLineItemAttribute` with `AttributeDefinitionId` and `AttributeValue` (plus
   `AttributePicklistValueId` for a picklist) bound to the CML variable named by the
   definition's developer name, with no `AttributeName`. A number stored with a decimal
   (`"12.0"`) still bound to an `int` `[Measured: M30]`. Product Configurator API requests are different:
   there, an attribute created or updated without `AttributeName` isn't matched to its CML
   variable and the engine applies the CML default
   `[Dev guide: cml_best_practice_attribute_name]`. Either way, use answers that differ
   from the CML defaults: an answer that didn't bind sizes the bundle from the default,
   which can still pass a weak assertion.
3. **Send a `BillingFrequency` on every Term-defined and Evergreen line in the Place
   graph.** Without it, a configuration the rules rejected came back as
   `FIELD_INTEGRITY_EXCEPTION`, "When the SellingModelType is Evergreen or Term-Defined,
   BillingFrequency can't be null", on the root line, which hides the rule. Valid
   configurations placed without it `[Measured: M32]`.
4. **Call `configure` with `executeConfigurationRules: true`,** then read the result as
   in [Reading a result](#reading-a-result).
5. **Assert every component's quantity**, including the zeros, against a hand-computed
   table (see the worked example), and one line per `@(split = false)` component. Pick answers on
   each rounding boundary: exact multiples (`sites = 10`) and one past (`sites = 11`). Add
   the answers that produce the largest quantity, to test the 9,999 cap
   ([Raising the 9,999 cap](#raising-the-9999-cap-maxrelationsize)).
6. **For each rejection, submit the conflicting state and assert that the message of a
   rule it breaks appears** in either place [Reading a result](#reading-a-result) names,
   not merely that something failed. When a state breaks several rules, accept any of
   their messages and no other: one state that broke two rules reported only one
   `[Measured: M33]`. To get a particular rule's message, state that rule so it can fail
   alone, for example on the answer as well as on the line. That is why every constraint
   in the worked example has its own message.
7. **Check the activation result before reading any `configure` result.** A model that
   failed activation stayed inactive, and `configure` then returned `success: true` with
   no messages, which looks like a pass `[Measured: M20]`.

### Reading a result

For every answer set, check Place, then look for rule messages in two places, `configure`
and the error log, a few seconds after Place:

| Where | Seen for a rejected configuration | Require for a valid one |
|---|---|---|
| Place | `isSuccess: true`; it saved what it was sent `[Measured: M29]` | `isSuccess: true` |
| `configure` | Usually `success: true`, `solverStatus: "error"`, `errors: []`, the rule's message in `messages` `[Measured: M29]` | `success: true`, `solverStatus: "success"`, `errors: []` `[Repo: .cursor/skills/constraint-models/SKILL.md]` |
| `RevenueTransactionErrorLog` on the quote | A row with the rule's message in `ConfiguratorErrorMessage` `[Measured: M29]` | No row with a constraint's failure message |

`success: true` and `isSuccess: true` prove nothing about the rules. Once, the rule's
message was only in the error log and a later `configure` returned
`solverStatus: "success"` `[Measured: M29]`. Assert expected `Info` or `Warning` notes
from `message(...)` separately, in `configure`'s `messages`; whether they also reach the
log wasn't measured. Bundle-validation rows can appear in the log too, and one made
`createOrdersFromQuote` refuse the quote `[Measured: M29, M31]`; which of them block
ordering is [open item 1](#open-items).

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

// One line per sized component (Quick Rule 8)
@(split = false)
type Gateway : LineItem;
@(split = false)
type GatewayMount : LineItem;
@(split = false)
type Rack : LineItem;
@(split = false)
type UserLicense : LineItem;
@(split = false)
type Connector : LineItem;
@(split = false)
type ImplementationService : LineItem;
@(split = false)
type IntegrationService : LineItem;
@(split = false)
type ProjectManagement : LineItem;
type Support : LineItem;
@(split = false)
type StandardSupport : Support;
@(split = false)
type PremiumSupport : Support;
```

Notes on the model:

- No relation can exceed 9,999 (the largest bound is 5,000), so the model needs no
  `maxRelationSize` ([Raising the 9,999 cap](#raising-the-9999-cap-maxrelationsize)).
  Widen an answer domain and check again.
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

The "by hand" rows are rejected only because every component type is `@(split = false)`;
without it the edit would split the line instead
([One line per component](#one-line-per-component-split--false)). Read each message as in
[Reading a result](#reading-a-result).

If the `support` relation's `[1..1]` bound rejects two plans first (an
[open item](#open-items)), the message assertion catches it. Then either drop the bound to
`[0..1]` or add the bound's message to the accepted set.

---

## Measured on 264

The 2026-11-10 rows come from a temporary probe model on a 264 (API v68.0) scratch org:
rules added to an active bundle model, imported and cycled, then read back through
`message(...)` values in a `configure` response after a Place with rules on. Row M21 is an
earlier headless test of a different model. The 2026-11-11 rows (M22 to M39) come from fresh
264 `ent-sb0` scratch orgs: a bundle model built on this file's patterns (more than a dozen
components sized from root answers, the largest relation above 9,999), probe models, and
the line editor and configurator UI. Quotes went through Place with rules on (`Force`),
then `configure`, then a query of `RevenueTransactionErrorLog`. Nothing else in this file
was run.

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
| M22 | Sized component types with no `split` annotation: Place with `addDefaultConfiguration: true`; a rep's optional add-on at quantity 1; a sized line edited down | Every case kept the line as placed and added a second line for the rest (1 + (n − 1); m + (n − m)); quantities totalled right, no rule message. Each split group drew a `bundlevalidation` "number of child products … isn't in the specified range" warning | 2026-11-11 |
| M23 | The same with `@(split = false)` on every component type | One line per component at the rule's quantity; the add-on at 1 raised to `sites`. Edits of the add-on line and of an hours line, each down and up, rejected with the rule's message. The edited quantity stayed on the quote (read back for one downward edit) | 2026-11-11 |
| M24 | Configurator UI (two orgs). Without the annotation: a default sized child. With it: an existing root line reconfigured (add-on ticked at 1, `sites` changed) and a fresh bundle add from Browse Catalogs | Without: two instances (1 + the rest); in a group ramp, later segments kept a stale split that broke the constraint, with only a group-range warning; non-default children were one instance. With: one line per child at the rule's quantity, the add-on raised to `sites`, each line resized when `sites` changed, defaults kept, no warning | 2026-11-11 |
| M25 | A relation declared with an upper bound above 9,999, its cardinality set by a constraint from an `int` whose domain reaches the same bound, no `maxRelationSize` | A quantity just below 9,999 solved; one just above was rejected with the sizing rule's message, not a limit message. A CML-only `int` above 9,999 solved | 2026-11-11 |
| M26 | The M25 case with the PRC `MaxQuantity` above the needed quantity; then with `property maxRelationSize` set to the relation's upper bound | `MaxQuantity`: still rejected. The property: the bound itself solved | 2026-11-11 |
| M27 | `string region = parent(region);` in child types, no level; children in PCM component groups; no group types in the model; only the root's answer sent (two orgs) | Each child's attribute record held the root's value; editing the root's answer re-derived it and repriced; also in the configurator UI | 2026-11-11 |
| M28 | The M27 child types under a bundle root that isn't a type in the model; one child placed alone | Under that root: the children kept their attribute default. Alone: no attribute record written. Solver success, no message, both | 2026-11-11 |
| M29 | Place (rules on, `Force`) of configurations the rules reject | Place `isSuccess: true`, saving what it was sent. `configure`: `success: true`, `solverStatus: "error"`, `errors: []`, the rule's message in `messages` at type `error`; an error log of `Severity` Error with the message in `ConfiguratorErrorMessage`. Bundle-validation warnings in the same run were logged as a separate row of `Severity` Warning. In one case the message was only in the error log, and a later `configure` returned `solverStatus: "success"` | 2026-11-11 |
| M30 | Place graph answers as `QuoteLineItemAttribute` with `AttributeDefinitionId`, `AttributeValue` and, for picklists, `AttributePicklistValueId`; no `AttributeName` | Bound to the CML variables named by the definitions' developer names; a number stored with a decimal (`"12.0"`) bound to an `int` | 2026-11-11 |
| M31 | Place PATCH of a bundle child's quantity with `IsQuantityEditable = false` on its PRC (two quotes); then `createOrdersFromQuote`; then the quantity set back | `isSuccess: true`, the line saved and repriced; within seconds a `RevenueTransactionErrorLog` (BundleValidation: the quantity "can't be edited"); the order refused, "existing Revenue Transaction Error Logs". Setting it back deleted the log. The line editor saved the same edit with a warning icon and the same log | 2026-11-11 |
| M32 | Place of a rejected configuration without `BillingFrequency` on Term-defined and Evergreen lines | `FIELD_INTEGRITY_EXCEPTION` on the root, "… BillingFrequency can't be null", instead of the rule. Valid configurations placed without it | 2026-11-11 |
| M33 | One state breaking two rules: a line-form rule (add-on present → other plan's quantity 0) and the answer-sized plan rule | One message, the plan rule's; the test targeted the first rule. With the first rule also stated on the answer (add-on present → the answer is the required plan), its own message | 2026-11-11 |
| M34 | A virtual `Quote` container whose relations had no `sourceContextNode` (relations to the bundle and to top-level lines; also a single `relation lineitems : LineItem;`) | Place and `configure` succeeded; the bundle's rules didn't run (defaults at 1, nothing sized); a probe `message` on the container fired and one on the bundle didn't. Declaration order made no difference | 2026-11-11 |
| M35 | The container with `sourceContextNode`: constraints and preferences sizing top-level plan lines from a bundle answer; then the same checks as `message(..., "Error")` with the bundle relation `[0..1]` | Constraints: two plans placed at full quantity became n − 1 + 1; a plan edited down got the other plan added for the rest; a bundle add-on that the check forbade beside a plan was dropped; with the bundle relation `[0..10]` a second bundle root was added. `Error` messages: lines unchanged, an error log row with the message; `configure` could report success | 2026-11-11 |
| M36 | `closeRelation = true` on the container's bundle relation, which carries `total()` and `max()` aggregates | "There's a goal execution error in your CML code: IntTotalAttrConstraint(…)" (and IntMinMaxAttrConstraint) instead of the rule's message | 2026-11-11 |
| M37 | An `int` on the bundle set equal to an add-on's cardinality, for the container to read; `validate_cml` on the model with the container | The default add-on was dropped instead of raised to its rule's quantity, with and without the container (two runs, one model); reading the cardinality through the container's relation path restored it. `validate_cml`: "Missing port/type association" warnings for the container | 2026-11-11 |
| M38 | Amendment changing a root sizing answer | The children re-derived; the amendment lines carried the changes as quantity deltas | 2026-11-11 |
| M39 | Node status through sell → activate → amend → activate → amend on the shipped bundle model; context rule `AssetActionSource` ⇐ `SalesTransactionItem` added to `AssetToSalesTransactionMapping`; then a before-insert trigger on `AssetActionSource` | Node status holds `cfgStatus` per answer, not values. Without the rule: every asset action source blank; an amendment changing one answer reset an unsent answer to its CML default (`cfgStatus` Default). With the rule: rows from order items filled; rows from order item details (the answer change's cancel-and-reprice pair) blank, so the next amendment reset again. With the trigger as well: both filled, answers held across two amendments. A line-only amendment was unaffected without either. A backfill of blank rows from the order item's value also kept the answers | 2026-11-11 |

---

## Open items

Each needs a live 264 org:

1. For a component with `IsQuantityEditable = false`: whether `true` clears the M16
   warning, and whether a CML-set quantity alone, with no hand edit, writes an error log
   (M31 edited by hand). Also whether an error-log row of `Severity` Warning blocks
   ordering (M29 saw such rows for bundle-validation warnings).
2. How a large cardinality (600 service hours) displays in the configurator and the
   Transaction Line Editor.
3. What a rep sees in the configurator or the Transaction Line Editor when they edit the
   quantity of a line that a `constraint` sizes on a `@(split = false)` type (error
   banner, locked field, or something else; through Place the edit was saved and flagged,
   M23), and whether a `setdefault` quantity stays as the rep set it after they change an
   unrelated answer.
4. Whether an inline `ceil()` recalculates when a rep changes the PCM attribute it reads.
5. Whether an `exclude` and a `constraint` that both set the same relation to zero, under
   the same condition, behave the same as either alone.
6. Which action counts as the "next step" that a `Warning` blocks (save, pricing, submit
   for approval).
7. Why one rejection's message appeared only in `RevenueTransactionErrorLog` while a
   later `configure` returned `solverStatus: "success"` (M29), and which rejections do
   that. (Elsewhere the message was in `configure`'s `messages` at type `error`, with
   `errors: []`.)
8. Whether the `support` relation's `[1..1]` bound rejects two plans first, with a
   different message or none. (One state that broke two rules reported one message, M33;
   a hand-set quantity split the line or, with `@(split = false)`, was rejected, M22 and
   M23.)
9. Whether a rep can see or edit a derived variable in the configurator, with or without
   `@(configurable = false)`.
10. Solve time for the worked example's largest answers (200 sites, 5,000 users, 20
    integrations).
11. Whether a literal `%` in a message string is passed through or read as a Java format
    specifier. The dev guide documents Java format for these strings
    `[Dev guide: cml_logical_constraints]`; the worked example avoids `%`.
12. Whether an amendment that changes only a line quantity re-derives the quantities that
    depend on it (an answer change does, M38; see
    [Answers on an amendment](#answers-on-an-amendment)), and which rules run on an
    amendment. A future-dated order with CML products can be amended, but the amendment
    "doesn't conform to all the rules"
    `[Help: ind.qocal_future_dated_order_amendments_important_considerations]`.
    Configurator requests take a `validateAmendRenewCancel` option that runs amend, renew
    and cancel validations `[Dev guide: connect_requests_configuration_options_input]`.
    Order-type amendments, renewals and cancellations weren't run for node status.
13. How to model a mixed per-site plan split, which
    [Exactly one of a choice group](#exactly-one-of-a-choice-group) can't express.
    Candidates, neither in the dev guide nor run: an answer per plan (a site count each,
    constrained to sum to `sites`, each driving its plan's cardinality), or per-site child
    instances that each carry a plan. One route was run: the plans as top-level lines
    sized outside the configurator and checked on a virtual container
    ([Checks across top-level lines](#checks-across-top-level-lines-a-virtual-quote-container)),
    which leaves a quote without the bundle unchecked.
14. How to require exactly one plan, each sized per site, when the rep picks the plan by
    adding it ([Exactly one plan when each plan is sized per site](#exactly-one-plan-when-each-plan-is-sized-per-site)).
    Unsettled: whether `count(<condition>)` counts lines or quantity; whether Group Type
    `maxInstanceQty=1` admits one plan line of quantity `sites`, given that the two dev-guide
    pages describe it differently. A candidate in neither source: one exclusion per pair of
    plans, such as `support[StandardSupport] > 0 -> support[PremiumSupport] == 0`. None run.
15. Whether `@(split = false)` keeps one line per component in later group-ramp segments
    (M24 measured only the unannotated case).

---

## Validation Checks

1. Every derived variable is `int`, has an explicit domain derived from the answer
   domains, and is set by its own `constraint`. Every round-up is a bracket.
2. No `constraint(...)` contains `ceil(`, or `^` used as a power. Run
   `grep -nE 'ceil\(|\^' <blob>` and confirm that no such hit is part of a
   `constraint(...)`, including one that continues onto later lines. Hits elsewhere, such
   as a `^` in a regular expression in a `define`, are fine.
3. Every component quantity is a cardinality (`relation[Type] == …`); no rule writes
   `lineItemQuantity`, `ItemEndQuantity` or `this.quantity`. Every sized component type is
   `@(split = false)`, unless its lines must carry different attribute values.
4. No derived variable depends, directly or through an aggregate, on a cardinality it sets.
5. Each "per N" rule is checked at an exact multiple and one past it. If any relation's
   upper bound is above 9,999, the model sets `property maxRelationSize` equal to the
   largest declared upper bound, and the answers that produce the largest quantity are tested.
6. Review notes use `Info`; nothing meant as advice uses `Warning` or `Error`. Checks
   across top-level lines are `Error` messages on a virtual container whose relations all
   carry `sourceContextNode`.
7. Headless test: placed with rules on and a `BillingFrequency` on every recurring line,
   answers that bind (checked against non-default values), every quantity asserted as one
   line per `@(split = false)` component, every rejection asserted by the message of a rule it breaks, and
   every result read as in [Reading a result](#reading-a-result). Then the parent
   skill's [Validation Checks](SKILL.md#validation-checks), including the configurator
   check that the deployed model is the one you changed.
