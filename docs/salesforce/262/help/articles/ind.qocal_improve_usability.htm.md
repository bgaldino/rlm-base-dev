---
article_id: ind.qocal_improve_usability.htm
title: Add an Order Application Usage Type Automatically in Agentforce Revenue Management
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_improve_usability.htm&type=5&release=262
release: 262
release_name: Summer '26
area: transaction_mgmt
fetched_at: 2026-05-12
---

# Add an Order Application Usage Type Automatically in Agentforce Revenue Management

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
