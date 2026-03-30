# Revenue Cloud v66.0 Entity Relationship Diagrams

This directory contains comprehensive entity relationship diagrams (ERDs) for the Revenue Cloud Base Foundations project, generated from the RLM JSON schema files.

## Generated Files

### Individual Domain Mermaid Diagrams

Detailed ERDs for each domain, suitable for documentation and analysis:

- **pcm.mermaid** — Product Catalog Management (11 objects)
  - Product hierarchy, attributes, classifications, and qualifications
  
- **pricing.mermaid** — Salesforce Pricing (14 objects)
  - Price books, price book entries, and adjustment logic
  
- **rate-management.mermaid** — Rate Management (15 objects)
  - Rate cards, rate card entries, and rate lookup data
  
- **configurator.mermaid** — Product Configurator (4 objects)
  - Product configuration flows, rules, and assignments
  
- **transaction-management.mermaid** — Transaction Management (37 objects)
  - Assets, asset state periods, orders, order items, quotes, approvals
  - Contract items, pricing details, and related transaction records
  
- **dro.mermaid** — Dynamic Revenue Orchestrator (27 objects)
  - DRO transactions, message sets, outbound messages, and orchestration rules
  
- **usage-management.mermaid** — Usage Management (22 objects)
  - Product usage grants, usage resources, usage records, and policies
  
- **billing.mermaid** — Billing (54 objects)
  - Billing accounts, schedules, treatments, invoices, credit/debit memos
  - Payment schedules, tax treatment, and general ledger integration

### Master Diagram

- **master.mermaid** — High-level cross-domain relationships
  - Shows key objects from each domain as nodes
  - Illustrates critical cross-domain relationships (e.g., OrderItem → Product2, Invoice → BillingSchedule → Order)
  - Suitable for architecture documentation and executive summaries

### Interactive HTML Viewer

- **revenue-cloud-erd.html** — Force-directed graph with full field detail
  - 213 objects, 2,835 fields, 351 relationships across 9 domains
  - **Features:**
    - Click any object node to see all fields (type, description, refersTo links)
    - Fields grouped into Relationship Fields, Data Fields, and Related Objects sections
    - Collapsible field sections with clickable refersTo navigation
    - Domain filtering via colored toggle pills
    - Object search (filters sidebar list and graph simultaneously)
    - Zoom/pan, drag nodes, fit-to-view, label/link toggles
    - Hover tooltips with domain, field count, and click prompt
    - Node size proportional to field count (sqrt scale)
    - Domain color coding with legend
  - Data sourced from v260 developer guide PDF (all chapters extracted)
  - Self-contained (D3.js v7 CDN only external dependency)

- **erd-data.json** — Complete extracted data (213 objects, fields, relationships)
  - Machine-readable JSON for custom tooling or regeneration
  - Fields include type, description, and refersTo metadata

## How to Use

### Viewing Mermaid Diagrams

Mermaid files can be viewed in several ways:

1. **GitHub** — Automatically renders `.mermaid` files in browser
2. **Mermaid Live Editor** — https://mermaid.live/
   - Copy-paste diagram content from `.mermaid` files
3. **VS Code** — Install "Markdown Preview Mermaid Support" extension
4. **Local Preview** — Use any Markdown preview that supports Mermaid

### Using the Interactive HTML Viewer

1. Open `revenue-cloud-erd.html` in any modern web browser
2. No installation or build required
3. Use the sidebar to:
   - Filter domains (checkboxes)
   - Search for objects (text input)
   - View statistics
4. Interact with the graph:
   - Hover over nodes to see details
   - Click and drag to pan
   - Scroll to zoom in/out
   - Drag nodes to reposition

## Understanding Relationship Types

### Mermaid Notation

- `}o--||` — Many-to-one (child → parent, typically a Lookup field)
- `||--o{` — One-to-many (parent → child, Master-Detail)
- `||--||` — One-to-one

### Salesforce Relationship Types

- **Lookup** — Optional relationship; child can exist without parent
- **Master-Detail** — Required relationship; child cannot exist without parent
- **Polymorphic** — Field can reference multiple object types (e.g., OwnerId)

## Statistics

- **Total Objects:** 213
- **Total Fields:** 2,835
- **Total Relationships:** 351 (unique cross-object lookups)
- **Total Domains:** 9 (PCM, Pricing, Rates, Configurator, Transactions, Approvals, DRO, Usage, Billing)

## Diagram Layout Strategy

### Domain Diagrams
- Show all objects within a domain and their internal relationships
- Include key field names for context
- Suitable for:
  - Feature documentation
  - Developer onboarding
  - Data model reviews
  - Feature-specific architecture discussions

### Master Diagram
- High-level view showing only key objects per domain
- Shows critical cross-domain relationships
- Suitable for:
  - Executive presentations
  - System architecture documentation
  - Data flow overview
  - Integration planning

### Interactive Viewer
- Full-featured force-directed graph with all objects
- Suitable for:
  - Live exploration and discovery
  - Complex relationship analysis
  - Impact analysis (understanding connected objects)
  - Training and demos

## Maintenance

The interactive HTML and data JSON were generated by extracting all Standard Object field definitions from the v260 Revenue Cloud Developer Guide PDF using `extract_fields_v2.py` and merged extraction scripts. The Mermaid domain files are relationship-focused summaries.

To regenerate:
1. Field data: Re-run the extraction scripts against the PDF
2. HTML: Rebuild from `erd-data.json` using the HTML generator script
3. Mermaid: Update manually or regenerate from `erd-data.json`

---

**Generated:** 2026-03-26  
**Revenue Cloud Version:** v66.0 (Spring '26)  
**API Version:** v66.0
