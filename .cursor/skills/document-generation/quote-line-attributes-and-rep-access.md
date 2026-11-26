# Quote Documents: Line Attributes and Rep Access

Read this when a quote document must print the attributes a rep chose in the configurator, or
when a sales rep's generation fails or prints blanks while an admin's works. Parent:
[document-generation](SKILL.md). Mapper mechanics: [data-mapper-authoring.md](data-mapper-authoring.md) and
`../odt-authoring/SKILL.md`.

## Print selected attributes on a quote line

`QuoteLineItemAttribute` (QLIA) is a virtual object over the attribute value store, controlled by its parent quote. It is queryable
but not customizable or Apex-triggerable, so nothing can stamp values onto the line with a trigger or record-triggered flow
[Measured: 2026-11-26, 264 (USA796), ent-sb0 harness build; fields `AttributeName`, `AttributeValue`,
`AttributePicklistValueId`, `QuoteLineItemId`, `IsPriceImpacting`]. A DocGen extract can still read it. The recipe, built as a copy of the
shipped quote proposal extract and run for an admin, a rep (three runs) and a 200-line quote with zero mismatches
[Measured: 2026-11-26, 264 (USA796), ent-sb0 harness build]:

1. **Extract:** add an object query on `QuoteLineItemAttribute` filtered on the direct `QuoteLineItemId` under the line node, and a second
   under bundle child lines. Filtering on the direct field avoids the 2,000-row limit that applies to queries filtered through a parent
   relationship such as `QuoteLineItem.QuoteId` [Help: `ind.qocal_limitations_for_using_quote_and_order_capture`].
2. **Picklist labels:** `AttributeValue` holds the code. Add an FK object query on `AttributePicklistValue` (`Id` = the attribute's
   `AttributePicklistValueId`) for `DisplayValue`. Relationship traversal on the virtual QLIA inside a field mapping returned nothing; the FK
   query works.
3. **Map and pass through:** map `AttributeName`, `AttributeValue` and `DisplayValue`, and pass them through the Transform.
4. **Template:** loop them under each line, and under each child line, with distinct loop keys so mustache scopes do not leak between the
   line and child loops.
5. **Shapes:** a single child comes back as an object, not an array; mustache still renders it. A child with no attributes prints none.
6. **Names:** ODT names must be alphanumeric (a name with underscores failed the deploy).

Limits: two-level nested SOQL (Quote to line to QLIA) fails because QLIA is treated as an external object, so use the object-query
hierarchy above, not nested SOQL. A Context Service template can't print attributes until its context has an attribute node and QLIA
mapping; the shipped `RLM_QuoteDocGenContext` has only Quote and line nodes [Repo: `datasets/context_plans/DocGen/contexts/quote_docgen.json`].
Copying attributes onto a line field with Apex is possible but any `QuoteLineItem` update outside the line editors invalidates pricing:
an API update of a line's `Description` set the quote's `ValidationResult` to `TransactionIncomplete` [Measured: same].
[Open: whether generation consumes a DocGen entitlement, and the UI Generate Document action; generation was driven through
`DocumentGenerationProcess` records.]

## A rep can't generate, or prints blanks

Two separate access layers apply, and the shipped seeded rep lacks both for the shipped proposal template
[Measured: 2026-11-26, 264 (USA796), ent-sb0 harness build]:

| Symptom | Cause | Fix |
|---|---|---|
| Every generation fails: "contentVersion ... user does not have access" | The rep can't read the template's `ContentDocument` | Share it with the rep, or add the rep to the library that holds it. Sharing one template's document turned three failures into three successes; the shipped-template control failed the same way until shared |
| Generation succeeds but a field prints blank, no error | No field-level security on a printed field | Grant read on every printed field in a permission set. Granting it gave full parity with the admin's output |
| `DocumentTemplate` not visible, or `DocGenRuntimeUser` can't be granted | The separately licensed DocGen set is missing | See Runtime permissions in [SKILL.md](SKILL.md) |

Which library membership a persona should hold is [Open: tracked as a separate persona-access item].
Child row order can vary between runs of the same quote.

## Blank paragraphs and locked sections

- A blank paragraph left by an empty or false section: [Open: tag placement and paragraph marks not measured; see the page-break
  rules in [architecture-and-tokens.md](architecture-and-tokens.md)].
- Data true-up and locked sections (`DT_` tokens, add-in edit lists and lock profiles): [Open: not measured on this release; read the
  release's Help before promising it].
