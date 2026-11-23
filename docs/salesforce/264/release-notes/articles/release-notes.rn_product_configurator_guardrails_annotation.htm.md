---
article_id: release-notes.rn_product_configurator_guardrails_annotation.htm
title: Prevent Constraint Conflicts When Sharing Attributes and Relations
source_url: https://help.salesforce.com/s/articleView?id=release-notes.rn_product_configurator_guardrails_annotation.htm&type=5&release=264
release: 264
release_name: Winter '27
area: revenue
parent_article: release-notes.rn_product_configurator.htm
fetched_at: 2026-11-23
---

# Prevent Constraint Conflicts When Sharing Attributes and Relations

Prevent the constraint engine from altering specified attributes or relations when it satisfies a constraint. Use the guardrails annotation in a constraint to define protections at the constraint level, instead of on individual attributes and relations. Annotating the constraint prevents conflicts with other constraints that share the same elements.

Where: This change applies to Lightning Experience in Enterprise, Unlimited, and Developer editions of Revenue Cloud, with the Revenue Cloud Growth or the Revenue Cloud Advanced license.

How: Add the guardrails annotation to a constraint, and list the attributes or relations to protect.

SEE ALSO
Revenue Management Developer Guide: guardrail Annotation

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=release-notes.rn_product_configurator_guardrails_annotation.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
