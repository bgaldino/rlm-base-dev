# Bundles and Cardinality

> Sub-file of [`SKILL.md`](SKILL.md). Release 264. Read when designing or reviewing a
> bundle. Source tags follow the parent skill's convention.

## The four product shapes

`Type` and `ConfigureDuringSale` on `Product2` together make the shape.
[Help: `ind.product_catalog_products.htm`]

| `Type` | `ConfigureDuringSale` | Shape | Allowed children |
|---|---|---|---|
| None | Not Allowed / None | Static simple | none |
| None | Allowed | Configurable simple | none |
| Bundle | Not Allowed / None | Static bundle | static simple, static bundle |
| Bundle | Allowed | Configurable bundle | any of the four |

`Type` cannot change after create; a static bundle can become configurable and back.
Configurable → static needs every attribute defaulted, every child Not Allowed/None,
every child included by default with quantity locked, and no classification components.
[Help: `ind.product_catalog_create_simple_products.htm`; `ind.product_catalog_conversion_of_bundle_products.htm`; `ind.product_catalog_change_a_configurable_bundle_product_to_a_static_bundle_product.htm`]

**Choose static when** the kit never varies: it is cheaper to keep valid and has no
configurator decisions. **Choose configurable when** anything (a child, a quantity, an
attribute) is the buyer's choice. A configurable *simple* product is the right shape for a
single SKU whose only choices are attributes. [Help: `ind.product_catalog_products.htm`]

### Static kit or locked configurable bundle, when children recur

A kit that never varies but whose children are Term Defined or Evergreen (support or a
subscription that must renew or bill on its own model) is not settled by the rule above:

- **Help says to set no component selling model on either shape's rows.** Under a new
  static bundle, select None as the parent selling model and no component selling model;
  for a configurable bundle, select no component selling model. The shipped q3 static
  bundle `CERT007` sets both (see the linked section). Children keep their own selling
  model options. [Help: `ind.product_catalog_add_components_to_a_static_product_bundle.htm`; `ind.product_catalog_product_relationships.htm`; [`selling-models-and-lifecycle.md`](selling-models-and-lifecycle.md#selling-models-inside-bundles)]
- **For a bundle's children, the run-time selling model choice Help documents is in the
  configurator.** Product Discovery's buying options offer one for the item being added;
  the configurator's Product Header offers one for each product or option; and a static
  bundle cannot be configured at run time. [Help: `ind.qocal_discover_and_configure_products.htm`; `ind.product_configurator_flow_product_header.htm`; `ind.product_catalog_create_bundled_products.htm`]
  No snapshot article says which selling model a static kit's Term Defined or Evergreen
  child is quoted on, or whether it then renews and bills on it: **Open — needs live
  verification.**

Until that is measured, the shape to test against a static kit is a **locked configurable
bundle**: `ConfigureDuringSale=Allowed`, every child under a group, each child with
*Require this component* and *Include component by default* on and *Allow quantity changes*
(`IsQuantityEditable`) off, and group limits that pass
[Validate Product Definition](#mistakes-validate-product-definition-catches).
[Help: `ind.product_catalog_products.htm`; `ind.product_catalog_local_cardinality.htm`; `ind.product_catalog_bundled_product_validations.htm`]
On one measured component with `IsQuantityEditable = false`, a CML rule that set its
quantity returned `success: true`, and the line drew a PCM `bundlevalidation` warning. [Repo: `constraint-models/quantities-from-attributes.md`, run M16]
A hand edit of the same kind blocked order creation (below); whether the CML-set case writes
the same error log: **Open — needs live verification.**

Measured on a locked configurable bundle (Term Defined root at a zero price; one group whose
min and max equal its four children, each required, default, quantity 1, not editable, with
no scaling method given, so stored `Proportional`; the children One Time, Term Defined and Evergreen) [Measured: 2026-11-11, fresh 264 ent-sb0 scratch org]:

| Where | What happened |
|---|---|
| Configurator (Configure on the root line) | Opens. Each child's include checkbox, quantity and purchasing option (its selling model) show and are **disabled**; only the root quantity is editable. |
| Line editor | The child quantity cells are editable. Editing a locked child's quantity **saves** and reprices, with a warning icon: "The Quantity of the line item containing product … can't be edited." |
| Place Sales Transaction (rules on) | The same edit returns `isSuccess: true` and reprices. |
| After either save | The platform writes a `RevenueTransactionErrorLog` (BundleValidation) within seconds, and `createOrdersFromQuote` is **refused** while it exists ("there are existing Revenue Transaction Error Logs"). Setting the quantity back deletes the log. |
| Renewal (Connect `renew` on the root asset, no renewal term passed) | The Term Defined child renews at its quantity for **one** term of its selling model, even after a multi-term sale; the Evergreen and One Time children come through at quantity 0; the root at quantity 1. |

So the lock holds in the configurator and at order creation, not at save: a headless test
of "locked children can't change" must try the order (or read the error log), not trust
the save's success. Root and child renewal rules by selling model are in
[`selling-models-and-lifecycle.md`](selling-models-and-lifecycle.md#selling-model-of-the-bundle-root).
How locked children behave on an amendment, and whether the lock holds on the renewal
quote: **Open — needs live verification.**

## Structure rules

| Rule | Static bundle | Configurable bundle |
|---|---|---|
| Groups | Optional | **Mandatory**; children only under groups, never under the root |
| Group contents | Products only | Child groups, or products, or **one** classification component; never mixed in one group |
| Nesting | Help conflicts: `creation_of_a_bundled_product_structure` says a static bundle's group holds only products; the static add-components and validation articles describe nested child groups | Two levels: root group → child group; a child group holds products or one classification |
| Children | Static only; *Include by default* on, *Allow quantity changes* off | Static or configurable, simple or bundle |
| Classification-based attributes | Every attribute of every component needs a default | Runtime-editable |

Deleting a group deletes every component under it. [Help: `ind.product_catalog_products.htm`; `ind.product_catalog_creation_of_a_bundled_product_structure.htm`; `ind.product_catalog_add_components_to_a_static_product_bundle.htm`; `ind.product_catalog_bundled_product_validations.htm`]

Separate from group nesting, **product-in-product depth** (a bundle inside a bundle) is
capped by the org value `MaxBundleDepth`: default 3, ceiling 5. The QuantumBit plan has
one five-level chain and needs `MaxBundleDepth:5` in the scratch definition.
[Repo: `datasets/sfdmu/qb/en-US/qb-pcm/README.md`; `orgs/README.md`] Keep a new model at
depth 3 unless you own the org shape.

**Trade-off of depth:** every nested bundle is another configurator level and another set
of `ProductRelatedComponent` rows whose create-only lookups (`ChildProductId`,
`ParentSellingModelId`) a reload cannot repair. [Repo: `sfdmu-data-plans/SKILL.md` → *Reloading a Plan Into a Live Org*]

## Component vs classification component

A **product component** adds one product. A **classification component** adds, at run
time, every product based on that classification; one per group, groups only.
[Help: `ind.product_catalog_creation_of_a_bundled_product_structure.htm`]

| | Product component | Classification component |
|---|---|---|
| Relationship type | Bundle to Bundle Component Relationship | Bundle to Product Classification Component Relationship |
| Required / default | Allowed | **Must be off** |
| New product of the class | Needs a new component row | Appears automatically |
| CML sync | Child removal and cardinality sync | Adding/removing a product from a class does **not** sync |

[Help: `ind.product_catalog_product_relationships.htm`; `ind.product_catalog_local_cardinality.htm`; `ind.product_configurator_sync_cml_and_pcm.htm`]

Use a classification component for an open-ended "choose any X" list that grows with the
catalog; use product components when one choice must be required or pre-selected, or when
CML must name each member.

## Two kinds of cardinality

**Group cardinality** (`ProductComponentGroup.MinBundleComponents` / `MaxBundleComponents`)
bounds how many components a buyer may pick from the group. Help says it counts **distinct
components**. [Help: `ind.product_catalog_group_cardinality.htm`] Measured at run time, it
counted **lines**: a 1..1 group holding one product on two lines (a split, below) drew a
`bundlevalidation` range message (the number of child products isn't in the specified range;
the configurator shows it as a warning). Whether it then blocks the order, as the
locked-quantity message above does: **Open — needs live verification.**
[Measured: 2026-11-11, fresh 264 ent-sb0 scratch org] Design with Help's rule, then keep each component on one line. Blank min = 0, blank
max = unlimited; max ≥ min. With nested groups, only the **lowest-level** group's
cardinality is enforced at run time; a parent group's limits count child groups for
validation. [Help: `ind.product_catalog_group_cardinality.htm`; `ind.product_catalog_cardinality_examples.htm`; `ind.product_catalog_bundled_product_validations.htm`]

**Local cardinality** (`ProductRelatedComponent`) is per component:

| Field (UI) | API | Meaning |
|---|---|---|
| Require this component | `IsComponentRequired` | Cannot be removed; requires *Include by default* |
| Include component by default | `IsDefaultComponent` | Pre-selected |
| Allow quantity changes | `IsQuantityEditable` | Off → no min/max can be entered |
| Quantity / Min / Max | `Quantity`, `MinQuantity`, `MaxQuantity` | Default and bounds of the **quantity** of that product |
| Price includes component | `DoesBundlePriceIncludeChild` | Bundle price covers the child; quantity must be locked |
| Quantity scaling method | `QuantityScaleMethod` | Constant, Proportional, or blank (see below) |

[Help: `ind.product_catalog_local_cardinality.htm`; `ind.product_catalog_product_relationships.htm`; Repo: `scripts/ai/query_erd.py describe ProductRelatedComponent`]

Writing component rows by API [Measured: 2026-11-11, fresh 264 ent-sb0 scratch org]:

- `ParentProductRole` and `ChildProductRole` are not writable; the platform sets them from
  the `ProductRelationshipType`. Leave them out of a hand-written insert. (The shipped PCM
  plans carry both columns, from extraction, and load.)
- `MinQuantity`, when given, must be at least 1. Leave it blank for no minimum.

For a classification component, its min/max/default quantity apply to **each** product the
buyer picks from that class, while the group bounds how many distinct products. Example:
group 2..2 over a class with component quantity 1..5 default 2 → exactly two products, each
quantity 1–5. [Help: `ind.product_catalog_cardinality_examples.htm`; `ind.product_catalog_nested_group_cardinality_and_product_classification_component_cardinality.htm`]

### Patterns

| Commercial rule | Model |
|---|---|
| Pick exactly one of N, one pre-selected | Group min = max = 1; `IsDefaultComponent` on one child, none required |
| Always included, cannot remove | `IsComponentRequired` + `IsDefaultComponent` |
| Optional add-ons, any number | Group with blank min/max; children neither required nor default |
| At least two of these | Group min = 2, and at least two distinct children |
| Quantity follows the parent (per-seat support) | `QuantityScaleMethod = Proportional`, quantity locked |
| Fixed quantity whatever the parent quantity | `Constant`, *Allow quantity changes* off |
| Included in the bundle price | `DoesBundlePriceIncludeChild`, quantity locked |

### Mistakes Validate Product Definition catches

Run **Validate Product Definition** on a bundle after a change. For configurable bundles it
checks: products in a group ≥ group min; required products in a group ≤ group max; child
groups ≥ parent group min; child groups with required products ≤ parent group max. Static
bundles: default components within min/max, and child-group count within the parent's
bounds. [Help: `ind.product_catalog_bundled_product_validations.htm`]

Two invalid designs from Help's examples: **required children exceeding the group max**
(Example 4: more required children than the group's max of 5), and a group min above the
number of distinct children. [Help: `ind.product_catalog_cardinality_examples.htm`]

## Quantity scaling and lifecycle

| Method | Run time | Amend / renew / cancel |
|---|---|---|
| None (blank in the API, with *Allow quantity changes* on) | Editable if *Allow quantity changes*, independent of parent | — |
| Constant | Fixed at design-time quantity; *Allow quantity changes* must be off | — |
| Proportional | Child = parent qty × child qty; with *Allow quantity changes* on, editable only in the configurator during a **new sale**, read-only in the line editor | **Read-only** in the configurator: the original ratio stays for the asset's life; change the parent quantity instead |

In the 264 API the picklist holds only `Constant` and `Proportional`: writing `None` is
rejected (`INVALID_OR_NULL_FOR_RESTRICTED_PICKLIST`). Blank means None only when
`IsQuantityEditable` is true: a row inserted with `IsQuantityEditable = false` and no method
was stored `Proportional`. [Measured: 2026-11-11, fresh 264 ent-sb0 scratch org]
Proportional is the default when *Allow quantity changes* is off at creation; None when on.
Help's warning says child quantities are read-only in the runtime cart when the method is
Constant or "Default" (a value its own list of methods does not include), even on legacy
rows with *Allow quantity changes*. [Help: `ind.product_catalog_product_relationships.htm`; `ind.product_catalog_local_cardinality.htm`]
Separately from that warning, measured on a **Proportional** child with *Allow quantity
changes* off: its quantity was read-only in the configurator, but in the line editor and
through Place the edit saved, and it was refused only at order creation. See [the locked bundle measurement](#static-kit-or-locked-configurable-bundle-when-children-recur). [Measured: 2026-11-11, fresh 264 ent-sb0 scratch org]

**Downstream:** choosing Proportional fixes the parent-to-child ratio for every later
amendment. If a customer must later change one child's quantity independently, model it
with None (blank, with *Allow quantity changes* on) or as a separate line. [Help: `ind.product_catalog_product_relationships.htm`]

## CML-sized default components

A component that is `IsDefaultComponent` and whose quantity a CML rule sets (for example
`relation[Type] == n` from a root answer) **splits**: the default instance stays at its PCM
quantity and the solver adds a second instance for the rest (measured with a default
quantity of 1: 1 + (n − 1)). Measured in the
UI configurator and on the API defaults path (Place with `addDefaultConfiguration: true`);
a hand edit below the rule's quantity split the same way instead of being rejected. On a
single quote the total quantity stays right, but each split counts as two lines against its
group's max (above). In a group
ramp, setting the first segment's component back to one line by hand did not fix the later
segments: each still held two lines per component, with a total quantity of n + 1, flagged
only by the `bundlevalidation` range message. A component added without defaults (not
`IsDefaultComponent`, or the API sending the child lines itself) gave one instance.
[Measured: 2026-11-11, fresh 264 ent-sb0 scratch org]

Keep the default flag and fix it in the model: the `split` annotation set to false on the
component's CML type (`@(split = false)`) keeps one instance [Dev guide: `cml_annotation_example_split.htm`],
so the default line takes the rule's quantity, and a hand edit to another quantity is
rejected with the rule's message. [Measured: 2026-11-11, fresh 264 ent-sb0 scratch org] Dropping `IsDefaultComponent` also avoids the
split, but loses the pre-selection and cannot keep a required child (a required child must
be a default). [Help: `ind.product_catalog_local_cardinality.htm`] `constraint-models`
covers writing the CML. Its one-line result for `relation[Type] == n` (run M14) does not
record whether the component was a default; for a default component, expect the split.

## Quote visibility

`QuoteVisibility` (Always, Never, Transaction Line Editor Only, Quote Document Only; blank
shows both). Hiding a bundle hides its children. Use it for a technical child that must be
priced or fulfilled but not read by the buyer. [Help: `ind.product_catalog_product_relationships.htm`]

## Overrides in a bundle context

Cardinality of components and groups at the **second level and below** can be overridden
for a given root bundle and restored later (`ProductComponentGrpOverride`,
`ProductRelComponentOverride`). Attribute overrides in a bundle are covered in
[`attributes-and-classifications.md`](attributes-and-classifications.md). An attribute
override applies to every instance of that product in the bundle. [Help: `ind.product_catalog_override_local_cardinality.htm`; `ind.product_catalog_override_group_cardinality.htm`; `ind.product_catalog_override_product_component_attributes_in_bundles.htm`]

The QuantumBit plan declares both override objects but excludes them (no rows).
[Repo: `datasets/sfdmu/qb/en-US/qb-pcm/README.md`]

## What reaches configuration rules

Constraint Builder's Sync updates CML for: child removal, product cardinality, *required*,
attribute deletion or deactivation, attribute value add/remove/deactivate, and default value
changes. It does **not** sync: component groups, class membership, attributes under a
product class, attributes inside a parent type, relations in a virtual container, context
tags, or newly added components or attributes. [Help: `ind.product_configurator_sync_cml_and_pcm.htm`]

**Downstream:** a group cardinality change, or a new component, needs a CML edit too.
`constraint-models` covers the four records a new bundle member needs.
