---
article_id: ind.product_configurator_model_large_catalogs.htm
title: Consolidation Strategies for Large Catalogs
source_url: https://help.salesforce.com/s/articleView?id=ind.product_configurator_model_large_catalogs.htm&type=5&release=264
release: 264
release_name: Winter '27
area: configurator
parent_article: ind.product_configurator_advanced.htm
fetched_at: 2026-11-23
---

# Consolidation Strategies for Large Catalogs

When you model a large or complex catalog, decide whether to use a single constraint model for many products or several models with distinct product sets. Your choice affects performance, maintainability, and how teams share ownership.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud with the Revenue Cloud Growth license or the Revenue Cloud Advanced license
Plan Your Modeling Approach

As your catalog grows, how you divide products across constraint models becomes a key design decision. A constraint model can hold many products, relationships, and rules, but every model has size and performance boundaries. Select an approach that keeps each model within its limits and matches how you organize your products and teams. Use a single large model that contains many products and their shared rules, or multiple models with each scoped to a distinct set of products.

When to Use a Single Model

Consider a single constraint model when:

Products share many of the same rules, options, and relationships, and you want to define that shared logic once.
Rules must span products, such as a compatibility or exclusion rule between items that customers often buy together.
The full set of products, attributes, and rules fits comfortably within the constraint model size and execution limits.
A single team owns the products and the modeling logic.

A single model reduces duplication and keeps cross-product rules in one place. As the model approaches its limits, compile and evaluation times increase, so monitor its size as you add content.

When to Use Multiple Models

Consider multiple constraint models, each with a distinct product set, when:

Product lines are largely independent and rarely need rules that reference products in another line.
The combined content would exceed the constraint model size limit or push evaluation time toward the maximum.
Different teams own different product lines and need to work and release independently.
You want to limit the blast radius of a change so that editing one product line doesn't risk validation for unrelated products.

Multiple models keep each model smaller, faster to evaluate, and easier to maintain. The trade-off is that rules can't span models, and shared logic must be defined in each model where it applies.

Guidelines for Dividing a Large Catalog
Group products by shared rules rather than by catalog hierarchy alone. Products that constrain one another belong in the same model.
Keep each model well within the size limit so you have room to grow. Splitting a model after it becomes too large is more work than planning boundaries early.
Factor out reusable structures with relationships and associations so common patterns are easier to maintain. See Variables, Relationships, and Associations.
Align model boundaries with team ownership when several teams maintain the catalog.
Watch evaluation time as models grow. If configuration validation slows down, consider splitting the model along product lines that don't share rules.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.product_configurator_model_large_catalogs.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
