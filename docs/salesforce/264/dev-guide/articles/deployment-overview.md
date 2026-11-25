---
page_id: deployment-overview
title: Revenue Management Deployment
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/deployment-overview.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Revenue Management Deployment
legacy_page_id: deployment_overview.htm
fetched_at: 2026-11-25
---

# Revenue Management Deployment

This section provides a clear roadmap for accurately and efficiently deploying Revenue Management objects and metadata between development, staging, sandbox, and production orgs.

Developing and maintaining complex business applications on the platform requires a structured approach to managing changes and deployments. This is especially true for Revenue Management, which involves a complex data model and metadata components.

The interconnected nature of Revenue Management’s architecture requires a meticulous and well-defined development operations (DevOps) process. Without it, organizations face significant risks, including data corruption, deployment failures, and disruption to critical business processes.

## Who This Section Is For

This section is intended for advanced users who are familiar with Salesforce development, established DevOps concepts, and Salesforce administration.

## What’s Not Included

- 

This section doesn’t include information about data migration from external or legacy systems.

- 

There’s no built-in, Revenue Management-specific deployment tool. Select the Salesforce or third-party deployment tools appropriate for your use case.

- 

Every Salesforce implementation is unique. This guide doesn’t address how to deploy your custom objects, fields, Apex classes, metadata, Lightning Web Components (LWCs), and so on.

- 

**[Deployment Workflows and Sequence](./deployment-workflows-and-sequence.md)**

A typical dev ops cycle involves managing test orgs, sandboxes, and a production org. Your deployment workflow can be a simple deployment of all setup and data from a development org to production. Or, it can be much more complex, involving multiple staging and testing orgs before any changes are sent to production.

- 

**[Deployment Considerations](./deployment-considerations.md)**

In any deployment scenario, you must understand all dependencies and prerequisites related to your planned changes.

- 

**[Global Unique ID Setup](./deployment-global-uid-setup.md)**

The establishment of a Global Unique ID (GUID) column on all objects during day-one initialization is a recommended practice for Salesforce DevOps.

- 

**[Managing Component States](./deployment-managing-component-states.md)**

Manage activation, versioning, and dependencies for components and objects as part of your deployment plan. A successful deployment makes sure that the system executes the intended, final, and active logic, preventing failures caused by stale or inactive component dependencies.

- 

**[Post-Deployment Steps](./post-deployment-steps.md)**

Most deployments require that you take some actions after the deployment to the target org is complete to ensure proper functionality and data integrity.

- 

**[Deployment Scenarios](./deployment-scenarios.md)**

Learn about specific deployment scenarios including new environment setup, refreshes, retiring records, deploying patches, and many more.

- 

**[Object Deployment Reference](./deployment-appendix-a.md)**

Get to know the object deployment sequence and associated properties.

- 

**[Metadata Deployment Reference](./deployment-appendix-b.md)**

Get to know the metadata deployment sequence and associated details.

- 

**[Additional Deployment Information](./deployment-appendix-c.md)**

Get to know additional deployment information for each Revenue Management feature domain, ensuring successful deployments and migrations.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/deployment-overview.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
