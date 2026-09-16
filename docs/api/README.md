# Revenue Cloud API Reference Viewer

Self-contained HTML viewer for the Revenue Cloud Business API reference documentation.

The reference content is re-extracted from the Release 264 (Winter '27, v68.0) developer guide — 148 endpoints across 9 API domains. 264 is pre-GA, so treat a live 264 org as ground truth over the guide. The downloadable Postman collection JSON under `postman/` is still the prior (v66.0) baseline and is being regenerated against a live 264 org.

## Usage

Open `index.html` directly in any browser — no build step, no server required. Works offline and on GitHub Pages.

## What it contains

All content from the source markdown files in `postman/docs/`:

| Tab | Source file |
|-----|-------------|
| Overview | `postman/README.md` |
| PCM | `postman/docs/pcm-business-apis-reference.md` |
| Product Discovery | `postman/docs/product-discovery-apis-reference.md` |
| Product Configurator | `postman/docs/product-configurator-apis-reference.md` |
| Pricing | `postman/docs/pricing-business-apis-v68.md` |
| Rate Management | `postman/docs/rate-management-apis-reference.md` |
| Transaction Management | `postman/docs/transaction-management-apis-reference.md` |
| Usage Management | `postman/docs/usage-management-apis-reference.md` |
| Billing | `postman/docs/billing-business-apis-reference.md` + `billing-apis-quick-reference.md` |
| Context Service | `postman/docs/context-service-apis-reference.md` |

## Features

- Full-text client-side search across all endpoints
- Dark/light theme toggle (default dark)
- Collapsible endpoint cards with request body field tables
- HTTP method badges (GET, POST, PUT, PATCH, DELETE)
- Sidebar navigation with per-domain section links

## Regenerating

If the source markdown files in `postman/docs/` are updated, regenerate `index.html` by re-running the build prompt with Claude Code. The file is fully self-contained — all content and styles are embedded inline.
