---
article_id: ind.qocal_improve_usability.htm
title: Add an Order Application Usage Type Automatically in Revenue Cloud
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_improve_usability.htm&type=5&release=264
release: 264
release_name: Winter '27
area: transaction_mgmt
parent_article: ind.qocal_manage_orders_in_revenue_lifecycle_management.htm
fetched_at: 2026-11-23
---

# Add an Order Application Usage Type Automatically in Revenue Cloud

Simplify order creation by using an Apex trigger to populate the Application Usage Type field . This field establishes the application context for the record. For all new orders, it creates an AppUsageAssignments record of type RevenueLifecycleManagement.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud where Transaction Management is enabled
Apex Trigger Sample for Application Usage

Use this sample code snippet to populate the AppUsageType field with RevenueLifecycleManagement.

trigger RlmOrderTriggerSample on Order(after insert) {
    List<AppUsageAssignment> assignments = new List <AppUsageAssignment>();
    for (Order ord: Trigger.New) {
        // Do further filtering as necessary
        AppUsageAssignment aua = new AppUsageAssignment(
            RecordId = ord.Id,
            AppUsageType = 'RevenueLifecycleManagement'
        );
        assignments.add(aua);
    }
    insert assignments;
}

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.qocal_improve_usability.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
