---
article_id: ind.um_usage_management_setup.htm
title: Set Up Usage Management in Agentforce Revenue Management
source_url: https://help.salesforce.com/s/articleView?id=ind.um_usage_management_setup.htm&type=5&release=262
release: 262
release_name: Summer '26
area: usage
fetched_at: 2026-05-11
---

# Set Up Usage Management in Agentforce Revenue Management

Usage Management provides the essential components for tracking and managing the consumption of your usage-based products. To implement this framework effectively, first set up usage management objects, such as usage resources, product usage grants, and their units of measure. This setup represents the foundational layer of your configuration and is a prerequisite for creating usage management policies. The policies ensure that consumption data can be accurately aggregated, grant policies can be correctly applied, and overall usage can be managed with efficiency.

NOTE Customers purchase sellable products. Usage grants, usage resources, and policies are defined for these sellable products. Salesforce uses the Usage Resources object for consumption data processing and the Usage Product object for invoicing consumption overages.
Choose Your Setup Path

You can set up your usage-based product via two paths. Review the supported product types and limitations before you begin.

SETUP PATH	RECOMMENDED FOR
Guided workflow	
First-time setup of anchor and pack products
Step-by-step validation with cross-object checks at each stage
Out-of-the-box default policies that reduce manual configuration

Manual configuration	
Commitment-based usage products—quantity, monetary, or token
Advanced users who need direct control over individual policy records
TIP If you're setting up a usage-based product for the first time, use the guided workflow. Before you start, review the record limits, supported policy types, and custom field constraints. See Guided Workflow Considerations and Limits.

Complete all of the following steps before continuing to use Usage Management.

Usage-Based Product Setup with Guided Workflow
A logical, sequential workflow guides you through a structured journey—creating a base product and resource definition, defining policy, linking Product Usage Grant (PUG), and setting rates. Finally, you can activate all records created through the journey with one click. It also simplifies the setup by providing preselected, out-of-the-box default policies.
Configure Usage Management Records Manually
Use manual configuration when your setup requires direct control over individual records or involves product types that the guided workflow doesn't support.
Validate Your Usage Product Setup
Run the product validator after you complete your usage management setup by using the guided workflow or manual configuration. The validator checks your configuration for errors and identifies the specific record to resolve before you activate them.
