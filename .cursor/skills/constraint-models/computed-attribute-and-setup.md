# Copying a computed attribute to a line field, and setting up a test product

Two recipes that came out of building on the configurator. Both are
`[Measured: 2026-11-26, 264 (USA796), ent-sb0 harness build]` unless marked.

## CML cannot write a custom context tag: copy the attribute after save

When a rule computes a value (a derived code, a tier) that a quote line field must hold,
the model cannot write that field. Compute it into a hidden attribute and copy it to the
field after the configurator saves.

1. A record-triggered flow on `QuoteLineItem`, on the **asynchronous after-commit path**.
   It reads the line's `QuoteLineItemAttribute` row for the attribute definition and writes
   a **separate** custom field on the line.
2. **Why async.** A real UI save persisted the CML-computed Hidden attribute and left the
   field null until the flow copied it, three saves in a row. A before-save flow, or a
   synchronous after-save flow, runs before the configurator writes the attribute rows, so
   it copies the previous save's value.
3. **Recursion guard.** The flow's own update to the line re-enters the async path and fails
   `SELF_RESCHEDULING_ASYNC_PATH`. Give the entry condition "attribute value IsChanged" and
   "copy field IsChanged = false"; the second condition stops the re-entry. Use the same
   guard on any async-path flow that updates the record that triggered it.
4. **Apex triggers on `QuoteLineItemAttribute` are not allowed.** Trigger on the
   line, not on the attribute object. The same holds for `QuoteLineRelationship`: Place
   writes relationships after the lines, so a value derived from the bundle hierarchy also
   needs the line's after-commit step.

### Rule: a tag is a solver input, never a copy target

An `extern` tag that maps a context field is an **input** to the solver. Writing the copy
into the field a CML tag maps to fed a non-null tag back as a fixed input, and the solver
then refused a configuration the rules allow (a rule `Speed == "10G" -> tag == "A"` refused
10G). Copy into a field **no CML tag maps to**.

## Associating a rule with a classification

An `ExpressionSetConstraintObj` can associate a CML type with a `ProductClassification`
(`ReferenceObjectId` is the classification, tag type `Type`). One `type <Class> : LineItem
{ ... }` holding the attributes and rules then covers every product based on that
classification, including a product with no type of its own, no product attribute rows
and no mention in the model; a product-associated type can inherit it
(`type <Product> : <Class>;`). Pointing the association at an empty classification
stopped the rule for the unassociated product (negative control). Cycle the version
after changing an association ([import-and-deploy.md](import-and-deploy.md)).

A product created by API with `BasedOnId` gets no `ProductAttributeDefinition` rows, and
the configurator still shows and saves the classification's attributes.

## Making a test product reachable from Configure

Checklist, in order. A missing step fails with the same banner each time: "couldn't
retrieve the product and price information ... refresh the Decision Tables".

1. The product sits in a catalog and category the quote's Browse Catalogs reads. A product
   with no category is hidden from search and listing, whatever its sold-only flag
   `[Measured: 2026-11-26, fresh 264 ent-sb0 scratch org]`.
2. A price book entry with a selling model option on the quote's price book.
3. Refresh `Price_Book_Entry_Decision_Table_v2` (a new product fails in the configurator
   until it is refreshed); then confirm every table is Fresh
   (`check_decision_table_freshness`; skill: `decision-tables`).
4. An active model whose type covers the product (a product association, or a
   classification association above).
5. For a headless build of items 1, 2 and 4 from a spec, see
   `scripts/constraint_models/cml_tool.py scaffold` ([tooling.md](tooling.md)).
