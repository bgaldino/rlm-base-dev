---
article_id: ind.sf_contracts_integrate_salesforce_contracts_in_vlocity_managed_packages.htm
title: Integration of Salesforce Contracts in Vlocity Managed Packages
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_integrate_salesforce_contracts_in_vlocity_managed_packages.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
fetched_at: 2026-10-13
---

# Integration of Salesforce Contracts in Vlocity Managed Packages

The contract admin must complete a set of actions to integrate Salesforce Contracts in the orgs where Vlocity managed packages are installed. These actions include removal of Visualforce components from the Vlocity Contracts Page Layout and disabling of the Vlocity Contract State Model trigger.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, Professional, and Developer Editions

Prerequisites

Provision the required Salesforce Contracts licenses in the org.

Enable Salesforce Contracts.

Remove Visualforce Components from Vlocity Contract Lifecycle Management
For Salesforce Contracts to use Lighting Web Components when you generate and maintain contract documents, you must remove the document generation Visualforce component from the Vlocity Contract’s page layout.
Disable Vlocity State Models Trigger
To use the Salesforce Contracts features in an org, the contract admin must disable the Vlocity State Models trigger so that Salesforce Contracts can use the default Contract Lifecycle Management object state definitions. You must disable the trigger in the orgs where Omnistudiio licenses are provisioned first, followed by the installation of the Vlocity managed package (CME or INS).
Support for Template Designer in Core and Server-Side Document Generation
The combinations of managed packages that support the transition from the manage package designer to the document template designer in Salesforce core. In core, the designer is named Design Document Templates.
