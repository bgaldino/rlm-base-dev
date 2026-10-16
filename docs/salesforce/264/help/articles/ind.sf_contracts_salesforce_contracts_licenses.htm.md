---
article_id: ind.sf_contracts_salesforce_contracts_licenses.htm
title: Salesforce Contracts Licenses
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_salesforce_contracts_licenses.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_post-install_steps_for_salesforce_contracts_winter_23.htm
fetched_at: 2026-10-13
---

# Salesforce Contracts Licenses

Salesforce Contracts requires specific add-on licenses and permission sets to grant users the appropriate level of access.

Each Salesforce Contracts add-on license includes a corresponding platform license and permission set license. Assign permission sets based on each user's role — for example, administrators who configure contract types and state models need different permissions than users who create and negotiate contracts.

Salesforce Contracts Analytics and Contracts AI each require separate permission set licenses in addition to the core Salesforce Contracts license.

Personas and Permission Set Licenses for Salesforce Contracts
Permission set licenses give users incremental access to features that aren't included in their user licenses. Users can be assigned any number of permission set licenses. Personas define what different types of users can do in Salesforce Contracts. Each persona is mapped to specific responsibilities and permission sets that determine the level of access a user has.
Permission Sets Combination for Salesforce Contracts
Many of the tasks requires that you understand permission set combinations. The section provides a detailed mapping of the Salesforce Contracts personas with the required permissions sets.
Permission Set Licenses for Salesforce Contracts Analytics
Either Revenue Intelligence PSL or CRM Analytics Plus PSL must be available alongside CLM Analytics PSL, which is bundled with all Industry Analytics SKUs. Your subscription determines which PSLs are accessible for user assignment.
Permission Set Licenses for Contracts AI
You need a combination of licenses to use Contracts AI.
Permission Set Licenses for Document Playbook
The Document Playbook User permission set license provisions Document Playbook for both designers and users. Assign the Document Playbook Add-On with your existing Salesforce Contracts subscription to enable document playbook.
Add Salesforce Contracts Licenses and Install Omnistudio Package
Add the required Salesforce Contracts licenses to your org. If your implementation uses Omniscript-driven state transitions, Omnistudio document generation, or Data Mapper integrations, also install the Omnistudio package.
