---
article_id: ind.dro_technical_bundles.htm
title: Technical Bundles
source_url: https://help.salesforce.com/s/articleView?id=ind.dro_technical_bundles.htm&type=5&release=264
release: 264
release_name: Winter '27
area: dro
parent_article: ind.dro_dynamic_revenue_orchestrator_concepts_and_references.htm
fetched_at: 2026-11-23
---

# Technical Bundles

Technical bundles organize related fulfillment line items into a hierarchy under a single root. This grouping keeps related products together so they follow consistent fulfillment actions throughout their lifecycle.

REQUIRED EDITIONS
Available in: Enterprise, Unlimited, and Developer Editions

Technical bundles use decomposition rules and order lineage to keep related products grouped during fulfillment. As shown in the diagram, the Premium AI Workspace Bundle commercial product decomposes into a technical bundle. The root, AI Workspace Technical Bundle, groups three fulfillment tasks — Compute Provisioning, Vector Storage, and Identity Provisioning — in a single Fulfillment Order.

Technical bundles are generated as a Fulfillment Order Line Item (FOLI) bundle only when every component in the bundle has a decomposition rule that qualifies during order decomposition.
A child product is nested under a parent only if its lineage traces back to that parent. To establish this hierarchy, the system checks catalog relationships. If a child's source product decomposes into one of its possible parents, the relationship is established. If no immediate match is found, the system searches up the order hierarchy for the nearest valid ancestor to act as the parent.
To keep the bundle structure in an Amend, Renew, and Cancel (ARC) order, every decomposition rule in the parent-child chain must qualify. If a decomposition rule for a middle node does not qualify, the bundle hierarchy splits, and the generated FOLIs do not respect the original bundle structure.
FOLI records are consolidated when multiple products within a technical bundle share the same decomposition rule.
Bundled FOLI records are assigned to a single fulfillment order to ensure technical dependencies remain unified for downstream systems.
NOTE Parent FOLI actions are determined by bubbling up the actions assigned to their child components:
If a parent item has a Cancel action but at least one child remains active, the parent action is updated to Amend.
If a parent item has a No Change action but a child is assigned a Cancel or Amend action, the parent action is updated to Amend to make sure that the parent reflects the changes to its components.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.dro_technical_bundles.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
