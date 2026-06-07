---
article_id: ind.approvals_design_build_activation.htm
title: Design, Build, and Activation
source_url: https://help.salesforce.com/s/articleView?id=ind.approvals_design_build_activation.htm&type=5&release=262
release: 262
release_name: Summer '26
area: approvals
fetched_at: 2026-05-12
---

# Design, Build, and Activation

This section covers rules, constraints, and errors you might encounter while designing, building, and activating your approval processes.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions where Advanced Approvals is enabled
Activating a Flow

You can’t activate an approval flow that has validation errors. Errors are listed on the Flow Builder Error tab.

Create, Update, and Delete Operations

You can’t use the sObject APIs to perform create, update, and delete (CUD) operations on a standard field for an approval object. Instead, update approval records using the available invocable actions or by designing alternate flows. However, you can use the APIs to update custom fields.

Apex Trigger Update Restriction

All triggers must be updated to avoid any create, update, and delete operations on standard approval fields, as these operations will fail. However, you can use triggers to update custom fields.
