---
article_id: ind.sf_contracts_additional_post_install_set_ups.htm
title: Additional Set Up for Salesforce Contracts
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_additional_post_install_set_ups.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_post-install_steps_for_salesforce_contracts_winter_23.htm
fetched_at: 2026-10-13
---

# Additional Set Up for Salesforce Contracts

The post installation steps includes a additional setups such as setting up partner communities, reorder contract statuses, integrate docusign with Salesforce Contracts and so on.

Optional: Set Up Partner Communities

Set up your partner community user to access the same Salesforce Contracts functionality as your internal end users. To set up Partner Communities, see Setup Salesforce Contracts Partner Community User.

Optional: Object State Transition

State model consists of references to a base object and its states. A state model can be applied to Opportunity, Quote, Order, Contract, or any standard object or custom object. The Salesforce Contracts application uses state models to transition contracts from one state to another. State Transition determines the valid transition between two states.

For example, a valid state transition for a contract object is from the Draft to In Approval Process. You can modify the state transitions as per your business needs. For more information, see Default Object State Transition.

Optional: Map Record Type to a Contract Type

If you create a Contract Type and Record Type, you must map the record type to the contract type. For instance:

Create Contract Record Type.

Create Contract Type and Map to a Contract Record Type.

Optional: Configure Salesforce Contracts Analytics

Salesforce Contracts Analytics is a CRM Analytics powered solution that provides data-driven dashboards to analyze the data from various contract stages from creation to negotiation and approval.

With additional Salesforce Contracts Analytics licenses, you can can gain valuable insights into their contract lifecycles, facilitating better decision making and improved contract management practices. See Salesforce Contracts Analytics Post-Installation Steps and Permission Set Licenses for Salesforce Contracts Analytics.

Optional: Configure Clause Category

The Document Clause Library is a central repository of preapproved and prebuilt standardized template clauses that you can use to build contracts and other legal documents. When creating a clause set, you must select the category for the clause set to categorize your clauses. The system admin must define the clause categories for clauses in the setup. See Configure Clause Category.

Optional: Integrate Microsoft 365 Azure Account with Salesforce

The Salesforce Contracts Connector for Word add-in app is a quick and efficient way to design and maintain document templates and also, create, and edit contract documents using the Word features in Microsoft 365. See Integrate Microsoft 365 and Azure with Salesforce Contracts Manually.

Optional: Obligation Management

Salesforce Contracts includes built-in obligation management capabilities. A contract can have one or more obligations associated with it. You can access the obligations associated with a contract from the contract's record page or access all the available obligations from the obligations object. See Obligation Management Configuration and Obligation Management.

Optional: Enable Customer Community Plus for Salesforce Contracts Setting

For the Customer Community Plus users to access contracts via APIs, their org must be provisioned with the Customer Community Plus licenses. Also, Salesforce admins must enable the Customer Community Plus for Salesforce Contracts setting. See Enable Customer Community Plus for Salesforce Contracts Setting.

Optional: Use Context Service to Create and Update Contracts

Contract admins can use the user-friendly mapping interface to create and update contracts from objects. Use Context Service as an integrated method to streamline operations across various use cases. Use Context Service to simplify the sharing and consumption of business application data. Context Service acts as a generic module and forms a layer between applications and procedures, enabling easy retrieval and use of data across various Salesforce clouds at every step of the process. See Configure Context Service to Create and Update Contracts.

After Upgrading: Re-Enable Salesforce Contracts Connector for Word (Microsoft 365)

If you use Microsoft 365 Word features, re-enable the Salesforce Contracts Connector for Word (Microsoft 365) setting after upgrading to the latest version. See Document Generation Settings for Salesforce Contracts.
