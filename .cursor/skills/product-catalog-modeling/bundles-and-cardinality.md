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
Measured on a locked configurable bundle with a Term Defined root and four children (two One
Time, one Term Defined, one Evergreen), each required, default, quantity 1, not editable and
`Proportional` [Measured: 2026-11-11, fresh 264 ent-sb0 scratch org]:

| Where | What happened |
|---|---|
| Configurator | Opens; each child's include checkbox, quantity and purchasing option (selling model) show, **disabled**. |
| Line editor, or Place Sales Transaction with rules on | A child quantity edit **saves** and reprices (warning icon in the line editor; `isSuccess: true` from Place). Within seconds the platform writes a `RevenueTransactionErrorLog` (BundleValidation). |
| `createOrdersFromQuote` | **Refused** while that log exists. Setting the quantity back deletes the log. |
| Renewal (Connect `renew`, no renewal term passed) | The Term Defined child renews for one term of its selling model; the Evergreen and One Time children come through at quantity 0. |

So test the lock at order creation, or read the error log, not the save's result. Other
`bundlevalidation` messages are not measured this far: a CML rule that sets a locked child's
quantity draws one (`constraint-models` run M16), and so does a group out of range (below);
whether either blocks the order, how locked children amend, and whether the lock holds on the
renewal quote: **Open — needs live verification.** Renewal rules by selling model are in
[`selling-models-and-lifecycle.md`](selling-models-and-lifecycle.md#selling-model-of-the-bundle-root).

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
bounds how many components a buyer may pick from the group. Help says it counts distinct
components [Help: `ind.product_catalog_group_cardinality.htm`], but at run time it counted
lines: a 1..1 group holding one product on two lines drew a `bundlevalidation` range
message. [Measured: 2026-11-11, fresh 264 ent-sb0 scratch org] So keep each component on one line
([CML-sized default components](#cml-sized-default-components)). Blank min = 0, blank
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
| None | Editable if *Allow quantity changes*, independent of parent | — |
| Constant | Fixed at design-time quantity; *Allow quantity changes* must be off | — |
| Proportional | Child = parent qty × child qty; with *Allow quantity changes* on, editable only in the configurator during a **new sale**, read-only in the line editor | **Read-only** in the configurator: the original ratio stays for the asset's life; change the parent quantity instead |

Help: Proportional is the default when *Allow quantity changes* is off at creation, None when
on; child quantities are read-only in the runtime cart when the method is Constant or
"Default" (a value its own list of methods does not include). [Help: `ind.product_catalog_product_relationships.htm`; `ind.product_catalog_local_cardinality.htm`]
In the 264 API the picklist holds only `Constant` and `Proportional`; writing `None` is
rejected (`INVALID_OR_NULL_FOR_RESTRICTED_PICKLIST`). An editable row is left blank for None,
but a locked row inserted blank through the API was stored `Proportional`, so give new locked
rows a method. (The QuantumBit plan has locked rows with a blank method; what a load stores
for them was not checked.) [Measured: 2026-11-11, fresh 264 ent-sb0 scratch org] A locked
child's quantity edit still saved in the line editor; see
[the locked bundle measurement](#static-kit-or-locked-configurable-bundle-when-children-recur).

**Downstream:** choosing Proportional fixes the parent-to-child ratio for every later
amendment. If a customer must later change one child's quantity independently, model it
with None (blank, with *Allow quantity changes* on) or as a separate line. [Help: `ind.product_catalog_product_relationships.htm`]

## CML-sized default components

When a CML rule sets a default component's quantity (for example `relation[Type] == n`) and
the component's CML type has no `split` annotation, the component **splits**: the default
line keeps its PCM quantity and the solver adds a second line for the rest. Seen in the UI
configurator and on Place with `addDefaultConfiguration: true`; a hand edit below the rule's
quantity split the same way instead of being rejected. The second line counts against the
group's max (above), and in a group ramp the later segments kept the split. A non-default
component gave one line. [Measured: 2026-11-11, fresh 264 ent-sb0 scratch org]

Fix it in the model: `@(split = false)` on the component's CML type keeps one instance
[Dev guide: `cml_annotation_example_split.htm`], so the default line takes the rule's
quantity and a hand edit to another quantity is rejected with the rule's message. [Measured: 2026-11-11, fresh 264 ent-sb0 scratch org]
Dropping `IsDefaultComponent` also avoids the split, but loses the pre-selection, and a
required child must stay a default. [Help: `ind.product_catalog_local_cardinality.htm`]
`constraint-models` covers the CML; its run M14 (one line) doesn't say whether the component
was a default.

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
