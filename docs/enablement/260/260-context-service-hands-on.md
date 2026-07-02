---
release_version: 260
release_name: "Spring '26"
api_version: 66.0
area: "Context Service"
document_version: 0.1
status: draft
last_updated: 2026-05-06
authors:
  - Brian Galdino
data_shape: qb
prerequisites:
  - "`cci flow run prepare_rlm_org` completed against the target org"
  - "Context Service enabled (Setup → Context Definitions)"
  - "Standard context definitions provisioned (e.g., `SalesTransactionContext`, `RateManagementContext`, `RatingDiscoveryContext`)"
sources:
  - "https://help.salesforce.com/s/articleView?id=ind.context_service.htm&type=5 — Salesforce Help: Context Service product documentation"
  - "docs/salesforce/260/revenue-cloud-spring-26-2026-01-15.pdf — master Help compendium § Context Service Upgrade Guidance (pp 119–120) + § Known Issues for Spring '26 → Context Service Known Issues (pp 121+)"
  - "docs/enablement/258/Context service - Winter '26 Rev Cloud - External.pdf — 258 Context Service exercise"
  - ".cursor/skills/release-enablement/authoring-patterns.md"
---

# Revenue Cloud — Context Service

**Enablement Exercises** · Version 0.1 (draft), Spring '26

> **Branding note:** Salesforce has rebranded *Revenue Cloud* as *Agentforce Revenue Management* in Spring '26. This exercise series continues to use "Revenue Cloud" throughout 260 to match what users see in the product UI.

> **Foundational capability:** Context Service is a **cross-cloud platform feature**, not Revenue-Cloud-specific. It provides the data abstraction layer that Pricing procedures, Rating procedures, Configurator, and other Revenue Cloud capabilities depend on. The Salesforce Help product docs for Context Service live at `https://help.salesforce.com/s/articleView?id=ind.context_service.htm&type=5` (under Industries Clouds) and apply to any industry cloud where Context Service is enabled.

> Org / data shape: QuantumBit (`qb`). These exercises assume an org provisioned by `rlm-base-dev`'s `prepare_rlm_org` flow with the QuantumBit catalog and standard context definitions provisioned.

---

## Status of this document

🚧 **DRAFT — features verified against 258 carry-forward content + 260 master PDF upgrade guidance + Salesforce Help docs.** Spring '26 is largely a **stability/upgrade release** for Context Service. The 258 features (Extending, Syncing, Packaging, Seamless updates) carry forward; 260's net-new content is concentrated in upgrade guidance and known-issue resolutions for extended context definitions, with no major new feature additions documented at the time of this draft.

> **Note on source coverage:** Unlike Pricing, PCM, and other Revenue Cloud-area exercises, Context Service is not a dedicated feature section in the master Revenue Cloud PDF. Source content is split across (a) the cross-cloud Context Service product docs at help.salesforce.com, (b) the master PDF Upgrade Guidance section, and (c) Spring '26 Known Issues. Author should verify against PM if there are 260-specific Context Service features not captured here.

---

## What is Context Service?

> Sourced from Salesforce Help: `ind.context_service.htm`

Context Service simplifies the sharing and consumption of business application data. Acting as a **generic module** between applications and procedures, it enables retrieval and use of data across various industry clouds at every step of the process.

**How applications use it:** when an application sends a data request, the context fetches and loads all necessary data from the database, then distributes the required data to specific processes to fulfill the request. This eliminates redundant input collection and optimizes data access for performance.

**Editions:** Available in Lightning Experience for Developer, Enterprise, Professional, and Unlimited editions for Industries clouds where Context Service is enabled.

### Core concepts (from Salesforce Help docs)

| Concept | Definition |
|---|---|
| **Context Definition** | A logical data model abstraction. Standard context definitions are shipped with each Salesforce cloud; custom (extended) context definitions inherit from standards and can be customized. |
| **Node** | One logical entity within a context definition. Mappable to real entities, data model objects, and other objects. Nodes can have relationships between themselves. |
| **Context Tag** | A string that uniquely points to a node or attribute within a context definition. Unique within a context definition. |
| **Standard Context Definition** | Salesforce-provided definition (e.g., `SalesTransactionContext`, `RateManagementContext`, `RatingDiscoveryContext`). |
| **Extended Context Definition** | Custom definition built by extending a standard one. Inherits standard metadata + custom additions. Auto-upgrades when the parent standard updates. |

### Why Revenue Cloud depends on Context Service

| Revenue Cloud Capability | Context Definition Used |
|---|---|
| Salesforce Pricing | `SalesTransactionContext` (most common); customer-extended variants for enterprise scenarios |
| Rate Management | `RateManagementContext` |
| Rating Discovery Procedures | `RatingDiscoveryContext` |
| Product Configurator | Configurator-specific context definitions for option/component data |
| DRO | `CMESalesTransactionContext` for CME-DRO Interop (260 Feature 5 in DRO exercise) |

**Implication:** Customers who extend any of these for custom business logic must follow Context Service upgrade guidance every release — see `Upgrade Guidance` section below.

---

## Carry-forward inventory (from prior releases)

| Feature | Introduced in | Reference | 260 status |
|---|---|---|---|
| Extending a Context Definition | 258 | `docs/enablement/258/Context service - Winter '26 Rev Cloud - External.pdf` | 🔄 **enhanced** in 260 — sync semantics + deployment limitations clarified (see Upgrade Guidance) |
| Sync Extended Definitions | 258 | same | 🔄 **enhanced** in 260 — sync now requires Context Service Admin permissions in some scenarios |
| Packaging and Deployment of Context Definitions | 258 | same | 🔄 **enhanced** in 260 — deployment scenarios now explicitly limited (see Upgrade Guidance) |
| Seamless Context Definition Updates | 258 | same | ✅ no change |

> *Note:* All 258 carry-forward features remain valid for 260, but their behavior is more constrained in 260. The "🔄 enhanced" markers reflect tighter operational guidelines rather than new capabilities.

---

## Upgrade Guidance from Winter '26

> **Critical for any customer with extended context definitions.** Source: master PDF "Upgrade Guidance for Spring '26" → Context Service section (pp 119–120).

### Why Spring '26 needs an upgrade pass for Context Service

When you upgrade to Spring '26, **automatic upgrade** of context definitions runs. **Custom artifacts** in extended context definitions can conflict with artifacts in their parent standard context definition — preventing a clean auto-upgrade. If extended definitions don't work accurately after the Salesforce upgrade, the auto-sync didn't complete and manual sync is required.

### Upgrade of Extended Context Definitions

If extended context definitions don't work accurately after upgrading to Spring '26, **complete the sync manually**:

1. From Setup, in the Quick Find box, find and select **Context Definitions**.
2. Open the **Custom Definitions** tab.
3. For each affected extended context definition, click **Sync Now** to complete the sync process.

### Auto-sync failure scenarios + workarounds

| Scenario | Workaround |
|---|---|
| User running auto-sync lacks copy-records permissions | Have an administrator with **Context Service Admin** permissions run the sync via Sync Now |
| Maximum limits for attributes / nodes exceeded | Either delete unused nodes/attributes to free space, or contact Salesforce Support |
| Context definitions are corrupted due to invalid mapping records | Reach out to Salesforce Support for help |

### Deployment of Extended Context Definitions — what's NOT supported

Spring '26 explicitly clarifies these unsupported deployment scenarios:

| Scenario | Why it fails / Required action |
|---|---|
| Deploy from current Spring '26 release org → older release org (e.g., Winter '26) | **Backward deployment unsupported.** Cannot deploy 260-source context definitions to a 258 target. |
| Modify (update / delete) existing custom nodes/attributes when context definition is **active** | **Deactivate first, modify, reactivate.** Active state blocks modification. |
| Activation/deactivation as a deployment package action | **Unsupported.** Will fail the deployment. Activate/deactivate as a separate manual step in the target org, outside the deployment process. |
| Changing default status of a context mapping as a deployment package action | **Unsupported.** Will fail the deployment. Change default status manually as a separate step. |

### Recommended sandbox-to-production upgrade flow

1. Upgrade your **sandbox** org to Spring '26.
2. Manually **sync** your custom extended context definitions via **Sync Now** on the Custom Definitions tab.
3. **Test** all feature functionality and make changes to your extended context definitions as needed.
4. Upgrade your **production** orgs to Spring '26.
5. **Package and deploy** your extended context definitions from your sandbox org to your production org.

> Per the Rate and Usage Management upgrade guidance, customers who specifically extended `RateManagementContext` or `RatingDiscoveryContext` must additionally follow the **Synchronize Custom Context Definitions for Rate Discovery and Rating Procedures** step. → See `260-usage-management-hands-on.md` § Upgrade Guidance from Winter '26.

---

## Known Issues for Spring '26

> Source: master PDF "Known Issues and Limitations for Spring '26" → Context Service Known Issues (p 121+).

### Permission Set Changes

[NEEDS REVIEW — pull specific permission set issue text from master PDF p 121+ and any documented workaround. Initial extraction surfaced the section header but not full content.]

---

## Release Overview

Spring '26 Context Service does **not introduce new feature areas**. The release focuses on:

1. **Upgrade-flow improvements** for extended context definitions (Sync Now mechanics, permission requirements)
2. **Deployment scenario clarifications** — explicit documentation of unsupported deployment patterns (backward, active-state modification, activation as deploy action)
3. **Sandbox-to-production guidance** — formal recommended sequence for extended-definition upgrades

For 258 carry-forward features (Extending, Syncing, Packaging, Seamless updates), see the 258 Context Service exercise PDF. The 260 cycle adds operational guardrails around those existing capabilities; readers comfortable with 258 functionality only need to read the **Upgrade Guidance** section above.

---

## QuantumBit data reference for Context Service

The QB data plan provisions the standard context definitions used by other Revenue Cloud capabilities. No QB-specific custom (extended) context definitions are loaded — customers extending these for QB-specific business logic do so during their implementation.

### Standard Context Definitions Used by QB

| Context Definition | Used by |
|---|---|
| `SalesTransactionContext` | QB Pricing procedures (default), QB Configurator, Transaction Management |
| `RateManagementContext` | QB usage rating (extended in customer implementations) |
| `RatingDiscoveryContext` | QB rate discovery procedures |
| `CMESalesTransactionContext` | DRO + CME Interop scenarios (260 DRO Feature 5) |

### Sample Context Service walkthrough scenarios (for an extended customer setup)

1. **Extend a standard context definition** (carry-forward 258 — see 258 exercise) — add a custom node for a customer-specific data source.
2. **Sync the extension** when a Salesforce release ships — practice the manual Sync Now flow per the 260 upgrade guidance.
3. **Package and deploy** the extended definition from sandbox to production using the recommended sandbox-to-prod flow above.
4. **Verify** the extended definition powers downstream Pricing/Rating/Configurator procedures correctly post-deployment.

---

## Cross-Area: Rate and Usage Management Synchronization

> **Primary home:** `260-usage-management-hands-on.md` § Upgrade Guidance from Winter '26.

If you've extended the `RateManagementContext` or `RatingDiscoveryContext` definitions, you must synchronize them after upgrading to Spring '26. This is a **specific case** of the general Context Service upgrade guidance above, called out separately in the Rate and Usage Management upgrade section because Rating procedures break runtime if the extension isn't synced.

→ **Full steps:** `docs/enablement/260/260-usage-management-hands-on.md` § Upgrade Guidance from Winter '26 → Synchronize Custom Context Definitions.

---

## Cross-Area: DRO + CME Sales Transaction Context

> **Primary home:** `260-dynamic-revenue-orchestration-hands-on.md` § Feature 5 (CME Interop).

The 260 DRO + CME managed package interop (now GA) requires customers to **create and activate the `CMESalesTransaction` context definition** as part of the setup. Customers extending this definition follow the same 260 upgrade guidance as any other extended context definition.

→ **Full setup:** `docs/enablement/260/260-dynamic-revenue-orchestration-hands-on.md` § Feature 5.

---

## Open questions for author / PM

1. **Net-new 260 Context Service features** — confirm with PM whether Spring '26 introduces any feature additions beyond the upgrade-and-deployment improvements documented here. The master PDF and Salesforce Help docs don't surface obvious new features, but PM may have internal items.
2. **Context Service-specific 260 release notes URL** — the URL pattern `release-notes.rn_context_service_intro.htm?release=260` returns 404. Confirm whether a 260 release notes page exists at a different URL or whether Context Service updates are embedded in product release notes (Pricing, Rate Management) only.
3. **Permission Set Changes known issue (p 121+)** — pull the full text of this known issue from master PDF; it's flagged but content not yet extracted.
4. **Context Service Limits** — the Salesforce Help TOC includes a "Context Service Limits" page (`ind.context_service_limits` likely). Should the 260 exercise call out limits relevant to extended definitions (max nodes, max attributes, etc.)?
5. **Demo URLs** — Context Service typically doesn't have feature-specific demos in Solution Overview decks. Confirm whether 260 changes that.
6. **Extended definition deployment via Metadata API** — does the 260 deployment guidance apply to all deployment mechanisms (change sets, unmanaged packages, Metadata API), or specifically to one pathway? Worth clarifying.
7. **`rlm-base-dev` Context Service handling** — does `prepare_rlm_org` provision any custom extended context definitions for QB scenarios, or are all definitions standard? Affects walkthrough scenarios.
8. **Forward-look to 262** — Summer '26 release notes should clarify whether Context Service gets new features in the next cycle. Worth a forward-look note in the eventual `status: review` pass.

---

## Footer (rendered at end of distribution PDF)

© Copyright 2000–2026 Salesforce, Inc. All rights reserved. Salesforce is a registered trademark of Salesforce, Inc., as are other names and marks.

---

Sources:
- [Context Service product documentation](https://help.salesforce.com/s/articleView?id=ind.context_service.htm&type=5)
- [Context Service (Generally Available) — release notes (246 / earlier release reference)](https://help.salesforce.com/s/articleView?id=release-notes.rn_context_service_intro.htm&language=en_US&release=246&type=5)
