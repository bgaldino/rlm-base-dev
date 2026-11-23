---
article_id: ind.collections_create_configure_external_client_app.htm
title: Create and Configure an External Client App
source_url: https://help.salesforce.com/s/articleView?id=ind.collections_create_configure_external_client_app.htm&type=5&release=264
release: 264
release_name: Winter '27
area: collections
parent_article: ind.collections_compliance_setup.htm
fetched_at: 2026-11-23
---

# Create and Configure an External Client App

Create an external client app that enables a compliance application to integrate with Salesforce by using the relevant API. External client apps provide single sign-on (SSO) and use OAuth protocols to authorize third-party apps.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: View product and edition availability.
USER PERMISSIONS NEEDED
To create local external client apps:	Create, edit, and delete External Client Apps
Create a local external client app, and enter these values for the parameters.
In the Basic Information section, select Localas the distribution state.
In the API section, select OAuth.
In the API section, enter a callback URL. Provide the API end point of the compliance application.
For example, https://orgfeature.cumuluscapital.com/services/data/v64.0/connect/compliance/procedure/CollectionsAndRecovery
Set the other parameters based on your business requirements, and save your changes.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.collections_create_configure_external_client_app.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
