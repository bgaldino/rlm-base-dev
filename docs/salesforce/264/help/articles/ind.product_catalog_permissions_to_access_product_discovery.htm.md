---
article_id: ind.product_catalog_permissions_to_access_product_discovery.htm
title: Assign Product Discovery Permissions
source_url: https://help.salesforce.com/s/articleView?id=ind.product_catalog_permissions_to_access_product_discovery.htm&type=5&release=264
release: 264
release_name: Winter '27
area: pcm
parent_article: ind.qocal_product_discovery_setup.htm
fetched_at: 2026-11-23
---

# Assign Product Discovery Permissions

To provide users access to Product Discovery data and components, assign the necessary permissions and data access.

REQUIRED EDITIONS
View supported products and editions.
Permissions for Authenticated Users

Authenticated users means both customers with a portal account, and your internal users who need access to Product Discovery.

For internal Salesforce Lightning Console users, and for customers and partners with Experience Cloud accounts, assign the respective Product Catalog Management permission set. See Product Catalog Management Permission Set Licenses.

To provide access to use Guided Product Selection, assign the OmniStudio User permission set in addition to the Product Catalog Management permission set.

NOTE The permission set is available only after Guided Product Selection is set up. Guided Product Selection is available only to Salesforce Lightning Service Console users.
Permissions for Guest Users

Guest users are customer portal visitors who don't have an active portal account.

To the guest user profile, provide the necessary administrative permissions, general user permissions, object and field-level permissions, and data access.

Assign these administrative permissions.
Salesforce Pricing: Run time user
Context Service Run time user
API Enabled
Assign these general user permissions.
Allow access to Product Discovery
Grant users access to Industries Interaction Calculation features
Run Decision Matrices
Run Expression Sets
View Product Catalog for Customer Community User
View Product Catalog via API for Customer Community User
To use Guided Product Selection, select ‘Enables consumers and partners to execute OmniScripts, DRs, Cards through a Community or off platform’
Assign read access to these standard objects. Then for each of these standard objects, edit field-level security and provide read access to all the fields.
Attribute Categories
Attribute Category Attributes
Attribute Definitions
Attribute Picklists
Attribute Picklist Excluded Values
Attribute Picklist Values
Catalogs
Categories
To use qualification or pricing:
Decision Matrices
Decision Matrix Columns
Decision Matrix Column Ranges
Decision Matrix Rows
Decision Matrix Versions
Expression Sets
Expression Set Versions
To use pricing, Price Books
Products
Product Attribute Definitions
Product Category Disqualifications
Product Category Products
Product Category Qualifications
Product Classifications
Product Classification Attributes
Product Component Groups
Product Component Group Overrides
Product Disqualifications
Product Qualifications
Product Related Component Overrides
Product Relationship Types
Product Selling Models
Product Specification Record Types
Product Specification Type
To use ramp deals, Product Ramp Segment
NOTE The Product Ramp Segment object is available only when you have Revenue Cloud and Ramp Deals enabled.
To use usage-based pricing, Unit Of Measure
NOTE The Unit of Measure object is available only when you have Revenue Cloud and Ramp Deals enabled.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.product_catalog_permissions_to_access_product_discovery.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
