---
article_id: ind.dro_use_context_definitions.htm
title: Turn On Context Definitions
source_url: https://help.salesforce.com/s/articleView?id=ind.dro_use_context_definitions.htm&type=5&release=262
release: 262
release_name: Summer '26
area: dro
fetched_at: 2026-05-12
---

# Turn On Context Definitions

Context definitions ensure efficient data access at every step of the orchestration process. A context definition includes a structure that defines the nodes, its attributes, and context tags.

REQUIRED EDITIONS
USER PERMISSIONS NEEDED
To create and view context definitions:	

DRO Admin User permission set

In order to view context definitions on your org:

Enable the Salesforce Dynamic Revenue Orchestrator (DRO) admin user licenses.
Enable the Context Service platform license, Context Service Access.
Turn on Context Definitions.

To turn on context definitions:

 From Setup, in the Quick Find box, enter Context Service, and then select Context Service Settings. 
To load the predefined context definitions, turn on the toggle next to Context Definitions.
IMPORTANT The Salesforce DRO solution comes with its own predefined context definitions that are used to map sales transactions to objects and Order. However, if you want to customize parts of this context definition for reuse, extend or clone it and make modifications.

All the context definitions, predefined or created by you, can be viewed on the Context Definitions page. To view the Context Definitions page, from Setup, in the Quick Find box, enter Context Service, then select Context Definitions.

SEE ALSO
Trailhead:: Context Service Basics
Context Definitions
