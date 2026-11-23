---
article_id: ind.product_configurator_advanced.htm
title: Rules and Constraints in Configurator With Constraint Rules Engine
source_url: https://help.salesforce.com/s/articleView?id=ind.product_configurator_advanced.htm&type=5&release=264
release: 264
release_name: Winter '27
area: configurator
parent_article: ind.product_configurator_introduction.htm
fetched_at: 2026-11-23
---

# Rules and Constraints in Configurator With Constraint Rules Engine

To create configuration rules and constraints that can validate large and complex product configurations, use Constraint Rules Engine.

REQUIRED EDITIONS
NOTE Constraint Rules Engine services aren’t available in Government Cloud. For more information, contact your Salesforce account executive.
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud with the Revenue Cloud Growth license or the Revenue Cloud Advanced license
Use Constraint Builder With Constraint Rules Engine
Use Constraint Builder to create constraint models that manage complex configuration and validation for your products. Constraint models describe real-world entities and define their relationships with one another. Constraint Builder uses constraints in addition to if-then rules to customize complex products quickly and accurately.
Consolidation Strategies for Large Catalogs
When you model a large or complex catalog, decide whether to use a single constraint model for many products or several models with distinct product sets. Your choice affects performance, maintainability, and how teams share ownership.
Convert Rules from Business Rules Engine into CML Code
Export rules from Business Rules Engine, then convert them to CML code and import them into Constraint Rules Engine.
Sync Constraint Models with Product Definitions
Sync product definition changes from Product Catalog Management (PCM) to the constraint modeling language (CML) for a constraint model, to make sure that the CML reflects the latest product definition.
Run Rules with the Run Config Rules Action
Use the Run Config Rules invocable action to run Hide/Disable, Message, and Recommend rules.
SEE ALSO
Set Up Context Definitions

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.product_configurator_advanced.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
