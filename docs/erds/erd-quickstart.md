# ERD Quick Start Guide

## View Individual Domain Diagrams

Copy the content of any `.mermaid` file and paste it into:
- [Mermaid Live Editor](https://mermaid.live/)
- GitHub (preview in browser)
- VS Code with Mermaid extension

### Example: View PCM Diagram

```bash
cat docs/erds/pcm.mermaid
```

Then paste into Mermaid Live Editor.

## View the Interactive HTML Viewer

```bash
# Open in browser
open docs/erds/revenue-cloud-erd.html

# Or from command line
python3 -m http.server 8000
# Then visit http://localhost:8000/docs/erds/revenue-cloud-erd.html
```

## Features of the Interactive Viewer

| Feature | How to Use |
|---------|-----------|
| **Filter by Domain** | Check/uncheck boxes in left sidebar |
| **Search Objects** | Type in search box to highlight matching objects |
| **View Node Details** | Hover over any node (shows name, domain, relationship count) |
| **View Relationship Type** | Hover over connection lines |
| **Pan** | Click and drag the canvas |
| **Zoom** | Scroll wheel or pinch (touch devices) |
| **Reposition Nodes** | Click and drag individual nodes |

## Domain Diagram Descriptions

**Entities** is how many the diagram draws, **not** the domain's object count — a diagram
is organized around relationships, so it may draw fewer entities than its domain holds,
all of them, or one from another domain. For object counts see the Domain Overview table
in `.cursor/skills/revenue-cloud-data-model/SKILL.md`. Both are gated by
`tests/test_erd_doc_counts.py`.

| Domain | File | Entities | Purpose |
|--------|------|---------|---------|
| PCM | `pcm.mermaid` | 11 | Product definitions, attributes, classifications |
| Pricing | `pricing.mermaid` | 26 | Price books and pricing strategy |
| Rate Management | `rate-management.mermaid` | 11 | Rate cards and rating rules |
| Configurator | `configurator.mermaid` | 4 | Product configuration flows |
| Transaction Management | `transaction-management.mermaid` | 44 | Orders, assets, quotes, contracts |
| DRO | `dro.mermaid` | 29 | Dynamic revenue orchestration engine |
| Usage Management | `usage-management.mermaid` | 24 | Usage grants, tracking, policies |
| Billing | `billing.mermaid` | 72 | Invoicing, payments, tax, GL integration |
| Approvals | `approvals.mermaid` | 1 | Approval workflow submissions |

## Legend

### Relationship Symbols (Mermaid)

```
}o--||  = Many-to-one (Lookup)
||--o{  = One-to-many (Master-Detail)
||--||  = One-to-one
```

### Colors (in HTML Viewer)

Each domain has a distinct color for easy visual identification:
- PCM: Red
- Pricing: Teal
- Rate Management: Blue
- Configurator: Light Salmon
- Transaction Management: Light Green
- DRO: Yellow
- Usage Management: Purple
- Billing: Light Blue

## Common Queries

### "Which objects reference Product2?"

Open `revenue-cloud-erd.html`, search for "Product2", and observe all connected nodes.

### "What are all the billing-related objects?"

Open `billing.mermaid` to see all 72 entities in one diagram.

### "How do orders connect to invoices?"

Open `master.mermaid` to see the cross-domain flow: Order → BillingSchedule → Invoice.

### "What are the immediate dependencies of an Asset?"

Search for "Asset" in the HTML viewer; nodes directly connected are immediate dependencies.

## Regenerating ERDs

If `erd-data.json` changes, regenerate the HTML viewer:

```bash
python3 scripts/erd/build_erds.py
```

This rebuilds `revenue-cloud-erd.html` from current `erd-data.json` data. The Mermaid `.mermaid` files are relationship-focused summaries that may need manual updates if domain structure shifts significantly.

To refresh `erd-data.json` itself against a fresh org or new release, see `.cursor/skills/schema-validation/SKILL.md` for the full workflow.

---

For full documentation, see `README.md`.
