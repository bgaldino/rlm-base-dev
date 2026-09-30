---
article_id: release-notes.rn_salesforce_contracts.htm
title: Salesforce Contracts
source_url: https://help.salesforce.com/s/articleView?id=release-notes.rn_salesforce_contracts.htm&type=5&release=264
release: 264
release_name: Winter '27
area: revenue
parent_article: release-notes.rn_revenue.htm
fetched_at: 2026-09-30
---

# Salesforce Contracts

Improve contract governance by bringing existing business guidelines and rules into Salesforce Contracts with document playbooks. Run a risk analysis to identify deviations from your guidelines in redlined contracts. Simplify contract operations by reducing runtime user permission requirements and track recipient signing progress for document envelopes. Salesforce Contracts is now available in Government Cloud environments. Add clauses from your clause library to quotes as Quote Special Terms.

Apply Contract Governance Policies Consistently with Document Playbooks
Put your standard contract governance policies to work without starting from scratch. Upload your existing rule definitions in PDF, DOCX, or XLSX format, and Salesforce Contracts stores each file as a versioned document playbook. Manage the playbook lifecycle by creating, activating, archiving, and deleting versions as your policies evolve. Customize contract governance to your business by designing unique playbooks for each contract record type.
Reduce Contract Risks by Analyzing Every Redline with AI
Identify and classify risks in redlined contracts by comparing changes against your document playbook directly from the Microsoft 365 Word add-in. Review modified clauses, detect deviations from your company standards, see clause-level risk findings with an overall risk rating (critical, high, medium, or low), and get recommended mitigation suggestions. Rerun the risk analysis after each round of edits to see how the contract changes affect the overall risk rating.
Protect Sensitive Setup Data by Removing Elevated Permissions from Runtime Users
Your runtime users can now perform contract lifecycle operations without the View Setup and Configuration permission. Previously, they needed this elevated permission to access org-level setup data for contract lifecycle tasks, such as creating and editing documents in the Microsoft 365 Word add-in, creating contracts from quotes, and managing electronic signatures. The user experience remains unchanged while sensitive setup configuration data stays protected.
Track Recipient Signing Progress for Document Envelopes
Know exactly where a contract is in the signing process and keep deals on track. Update an envelope's status to view each recipient's signing progress for the contract.
Author Contracts in Government Cloud
Government agencies and public sector organizations can now author, route, and generate contracts in Salesforce environments using Salesforce Contracts. Before enabling, work with your Salesforce account executive to confirm that the Context Service and Document Processing Engine are onboarded in your Salesforce org.
Add Clauses to Quotes from Your Clause Library
Before generating a document, sales reps can now search and add pre-approved clauses to quotes, such as standard warranty disclaimers, payment terms, delivery conditions. Reps can then customize standard language with deal-specific details. Choose which clauses are available by adding them to the Quote Special Terms component in your Quote page layout.
Use Salesforce Contracts with Lightning Platform Licenses
Now you can pair Salesforce Contracts with Lightning Platform Starter or Lightning Platform Plus, reducing licensing costs for organizations that need contract lifecycle management without full CRM capabilities. Some Salesforce Contracts capabilities depend on features that aren't included with Lightning Platform licenses. Previously, Salesforce Contracts required a Core CRM license, such as Sales Cloud or Service Cloud.
New and Changed Objects in Document Generation and Contracts
Do more with these new and changed Document Generation and Contracts objects.
New Connect REST APIs in Salesforce Contracts
Bring AI-assisted risk review and playbook standards into your contract workflows. Start an asynchronous risk analysis for a contract document version and a poll for its findings. Also, create a playbook version from a content document, and retrieve the playbook content chunks that best match a passage of contract text.
