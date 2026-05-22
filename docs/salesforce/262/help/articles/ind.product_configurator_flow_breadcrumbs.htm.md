---
article_id: ind.product_configurator_flow_breadcrumbs.htm
title: Breadcrumbs
source_url: https://help.salesforce.com/s/articleView?id=ind.product_configurator_flow_breadcrumbs.htm&type=5&release=262
release: 262
release_name: Summer '26
area: configurator
fetched_at: 2026-05-12
---

# Breadcrumbs

Breadcrumbs shows the navigation path through the product bundle hierarchy in Product Configurator. The component displays clickable breadcrumb links so users can move between levels, such as root product → option group → option. Breadcrumbs has no output properties and doesn’t listen to any events.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions of Revenue Cloud with the Revenue Cloud Growth license or the Revenue Cloud Advanced license
Breadcrumbs Responsibilities
Show breadcrumbs of the current path through the bundle hierarchy
Provide clickable breadcrumbs for users to go to a specific level
Use an overflow menu when a bundle hierarchy has four or more breadcrumb levels
Show the search bar when multiple searchable products exist
Publish Lightning Message Service (LMS) navigation events to Data Manager when a breadcrumb is clicked
Breadcrumbs API Name

S01_BreadCrumbs

Input Properties

Breadcrumbs accepts data from parent or flow component properties, set by users.

PROPERTY	TYPE	REQUIRED	DESCRIPTION
navigationRoute	Array	No	Current navigation path
searchInfo	Array	No	Searchable products for the catalog. Shows the search bar when more than one product is available.
isApiInProgress	Boolean	No	Whether an API call is in progress. Locks the component while the call runs.
isNonBlockingEnabled	Boolean	No	Whether non-blocking mode is turned on.
Types of Events Breadcrumbs Fires

Breadcrumbs fires the LMS event shown in this table.

EVENT ACTION	WHEN IS IT FIRED	PURPOSE
navigate	User clicks a breadcrumb link	Go to selected root product
