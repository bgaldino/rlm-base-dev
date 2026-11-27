# Extract and Transform Item Types, DocumentTemplate Record

Read when authoring or reading ODT items field by field. Parent: [document-generation](SKILL.md).

> Provenance: moved unchanged from this skill's entry point as of 661e50bbb, which stated "Verified on Release 262, API v67.0" [Repo: statement added in 7e1860b35, 2026-07-02]. [Open: not re-verified on the active release; run the check or generation it describes on a current org before relying on it.]

## Extract ODT — Item Types

### Object Query Items

Define which SObjects to query and how to join them:

| Field | Purpose | Example |
|-------|---------|---------|
| `InputObjectName` | SObject to query | `Invoice` |
| `InputFieldName` | Field on this object to match against FilterValue (see below) | `Id`, `InvoiceId` |
| `OutputFieldName` | Internal hierarchy path (join scope) | `Invoice`, `Invoice:Account` |
| `OutputObjectName` | Always `json` | `json` |
| `InputObjectQuerySequence` | Execution order (1, 2, 3...) | `1` |
| `FilterOperator` | Match operator | `=` |
| `FilterValue` | Value or path to match | `Id` (for root), `Invoice:BillingAccountId` (for FK lookup) |
| `FilterGroup` | Required grouping | `0` |

**InputFieldName semantics (critical — generates the WHERE clause):**
```
WHERE <InputFieldName> = <resolved FilterValue>
```

Two join patterns:

| Pattern | InputFieldName | FilterValue | Meaning |
|---------|---------------|-------------|---------|
| **Root** (input param) | `Id` | `Id` | Match input `Id` param → this object's `Id` |
| **FK lookup** (many:1) | `Id` | `Parent:FKField` | Match parent's FK → target's `Id` (1 result per parent) |
| **Child-of** (1:many) | Child's FK field | `Parent:Id` | Match parent's Id → child's FK (0..N per parent) |

**Examples:**
```
Seq 1: Invoice,     InputFieldName="Id",        FilterValue="Id"                        ← root
Seq 4: Account,     InputFieldName="Id",        FilterValue="Invoice:BillingAccountId"  ← FK lookup (safe)
Seq 5: InvoiceLine, InputFieldName="InvoiceId", FilterValue="Invoice:Id"                ← child-of (1:many)
```

**Multi-filter objects** (e.g., InvoiceLine with type filter):
```
Seq 3: InvoiceLine, InputFieldName=InvoiceId, FilterValue="Invoice:Id"
Seq 3: InvoiceLine, InputFieldName=Type,      FilterValue="\"Charge\""
```
Note: literal string filters use embedded quotes: `"\"Charge\""`.

### Field Mapping Items

Extract specific fields from queried objects:

| Field | Purpose | Example |
|-------|---------|---------|
| `InputFieldName` | Source path (colon-separated) | `Invoice:Account:BillingCity` |
| `OutputFieldName` | Key in Extract output | `BillingCity` |
| `OutputObjectName` | Always `json` | `json` |
| `OutputCreationSequence` | Usually `1` | `1` |

---

## Transform ODT — Item Types

### Pass-through Mappings

Simple field rename from Extract output to template token:

| Field | Purpose | Example |
|-------|---------|---------|
| `InputFieldName` | Key from Extract output | `BillingCity` |
| `OutputFieldName` | Template token name | `BillingCity` |
| `OutputObjectName` | Always `json` | `json` |
| `OutputCreationSequence` | `1` for simple mappings | `1` |

### Formula Items (Repeating Sections)

Build arrays for `{{#Section}}` tokens:

| Field | Purpose | Example |
|-------|---------|---------|
| `OutputFieldName` | `Formula` | `Formula` |
| `OutputObjectName` | `Formula` | `Formula` |
| `FormulaExpression` | Function call | `FUNCTION('invoice_docgen.InvoiceDocumentGeneration', 'InvoiceLineCustom', ...)` |
| `FormulaConverted` | RPN form (auto-generated on save — UI and API) | `\| ... FUNCTION` |
| `FormulaResultPath` | Output key name | `InvoiceLines` |
| `FormulaSequence` | Execution order | `1` |
| `OutputCreationSequence` | `0` (runs before mappings) | `0` |

### Object Output Items (Array Pass-through)

After a formula builds an array, map it to the template:

| Field | Purpose | Example |
|-------|---------|---------|
| `InputFieldName` | Formula result key | `InvoiceLines` |
| `OutputFieldName` | Template section name | `InvoiceLines` |
| `OutputObjectName` | `json` | `json` |
| `OutputFieldFormat` | `Object` (for arrays/objects) | `Object` |
| `OutputCreationSequence` | `1` | `1` |

---

## DocumentTemplate Record

| Field | Value | Notes |
|-------|-------|-------|
| `Name` | Template name | No underscores in API Name |
| `Type` | `MicrosoftWord` | For `.docx` templates |
| `TokenMappingType` | `JSON` | Always JSON for ODT approach |
| `TokenMappingMethodType` | `OmniDataTransform` | Links to ODT framework |
| `ExtractOmniDataTransformName` | Extract ODT name | Must match exactly |
| `MapperOmniDataTransformName` | Transform ODT name | Must match exactly |
| `UsageType` | `Invoice`, `Quote`, etc. | Object context |
| `Status` | `Active` / `Draft` | Must be Draft to edit |
| `IsActive` | `true` / `false` | Must be false to edit |
