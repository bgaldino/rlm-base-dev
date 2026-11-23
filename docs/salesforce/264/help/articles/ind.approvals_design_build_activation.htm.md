---
article_id: ind.approvals_design_build_activation.htm
title: Design, Build, and Activation
source_url: https://help.salesforce.com/s/articleView?id=ind.approvals_design_build_activation.htm&type=5&release=264
release: 264
release_name: Winter '27
area: approvals
parent_article: ind.approvals_advanced_approvals_considerations.htm
fetched_at: 2026-11-23
---

# Design, Build, and Activation

This section covers rules, constraints, and errors you might encounter while designing, building, and activating your approval processes.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions where Advanced Approvals is enabled
Activating a Flow

You can’t activate an approval flow that has validation errors. Errors are listed on the Flow Builder Error tab.

Create, Update, and Delete Operations

You can’t use the sObject APIs to perform create, update, and delete (CUD) operations on a standard field for an approval object. Instead, update approval records using the available invocable actions or by designing alternate flows. However, you can use the APIs to update custom fields.

Apex Trigger Update Restriction

All triggers must be updated to avoid any create, update, and delete operations on standard approval fields, as these operations will fail. However, you can use triggers to update custom fields.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.approvals_design_build_activation.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
