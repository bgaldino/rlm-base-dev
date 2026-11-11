---
article_id: ind.sf_contracts_system_administration_for_salesforce_contracts.htm
title: System Administration and Set Up for ​Salesforce Contracts
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_system_administration_for_salesforce_contracts.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
fetched_at: 2026-10-13
---

# System Administration and Set Up for ​Salesforce Contracts

Configure the core components of Salesforce Contracts, including contract types, contract type config settings, state models and transitions, Context Service field mappings, and Microsoft 365 integration.

Contract Types, Contract Record Types, and Contract Type Configs
Contract record types, contract types, and contract type configs work together to control how contracts behave throughout their lifecycle.
Contract Type Config Settings
Contract type config settings control behaviors such as document attachment formats and default template associations when contracts are created or updated.
State Models and Transitions in Salesforce Contracts
State models define the stages a contract moves through during its lifecycle and the allowed transitions between those stages. Salesforce Contracts includes a default state model. Extend it with custom states and transitions to match your business process.
Configure Contract Creation and Updates for Salesforce Contracts
Set up the field mappings that control how contract records are created and updated from source objects such as opportunities, orders, quotes, and custom objects.
Ways to Set Up Microsoft 365 and Azure Integration with Salesforce
Salesforce recommends using guided setup to integrate Microsoft 365 and Azure. Guided Setup provides a step-by-step, automated process that simplifies configuration and reduces errors. If you want to set up the integration manually, use the manual setup to configure each step with minimum privileges.
Configure E-Signature
System admin must integrate DocuSign with Salesforce Contracts for users to be able to email a copy of the document to sign at the recipient's convenience.
Document Clause Library
The Document Clause Library is a central repository of preapproved and prebuilt standardized template clauses that you can use to build contracts and other legal documents. Having all legal language in a single repository expedites document creation and enables the sales team to send out contracts without contacting the legal team for every deal.
Contract Approval Processes in Salesforce Contracts
Salesforce Contracts supports two approval mechanisms, the advanced approvals and the standard Salesforce approval process. The standard approval process is the default and runs when advanced approval isn’t configured.
Configure Document Generation Notifications for Salesforce Contracts
You can notify your users with timely email and in-app notifications for server-side document generation. In-app notifications are available by default and you can enable or disable the email notifications.
Use Custom Document Template Filtering for Salesforce Contracts
Using custom logic, you can filter the templates you want to display for a contract. You can configure a filtering class for each contract type. Only the set of templates that match the custom logic displays in the templates dropdown under the generate action in the Documents tab of a contract.
Document Generation Settings for Salesforce Contracts
Understand the impact of the general setting options you select for the document generation users in your organization.
Obligation Management Configuration
Achieve compliance, fulfill contractual commitments, and proactively mitigate risks by using the Obligation Management feature in Salesforce Contracts.
Set Up Digital Experience Sites for Salesforce Contracts
Configure Experience Cloud sites so that external partners and customers can view contract documents, check e-signature status, and access signed contracts.
Design and Configure Document Templates for Salesforce Contracts
Document templates define the structure, layout, and dynamic content of the contract documents that Salesforce Contracts generates.
Create Contract Type Config to Compare Contract Versions
To enable existing customers to compare contract versions, create the Compare Contract Versions Enabled setting in the contract type configuration and set its value to Yes. For new customers, this setting is pre-configured, but its default value is set to No. You must set it to Yes to compare contract versions.
Enable Salesforce Contracts Console App
From Setup, the Salesforce admin has to make the Salesforce Contracts Console App visible for profiles. Users can then access the app from the App Launcher.
View 'Is Associated With CLM'
The Is Associated With CLM field is associated with the Contract object. It indicates whether the contract record is created using the Salesforce Contracts application. The Is Associated With CLM field is automatically enabled when you create, import, or check out a contract document version from UI or using APIs.
Set Up Document Playbook
Document Playbook gives your legal and contract teams a single reusable source of negotiation guidelines that Salesforce Contracts uses during risk analysis. When a contract author runs risk analysis, Salesforce matches each modified clause against the active playbook version and flags deviations, nonstandard language, fallback positions, and escalation paths so that reviews align with company policy. Set up licenses, Data 360 indexing, and sharing so that designers can create document playbooks and contract authors can use playbook guidance during risk analysis.
