---
article_id: ind.sf_contracts_fls_requirements_for_doc_gen.htm
title: FLS Requirements for Contract Document Generation
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_fls_requirements_for_doc_gen.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_setup_digital_experience_sites.htm
fetched_at: 2026-10-13
---

# FLS Requirements for Contract Document Generation

Contract document generation reads and writes fields on several objects during hydration, persistence, and locking. Without Field-Level Security (FLS) on the required fields, generation silently fails or produces incomplete documents. After you set up the community user, grant FLS on the user's profile or on a permission set assigned to them.

Where to Enable FLS

Open the community user's profile (Customer Community Plus User or Partner Community User) or a permission set assigned to that user, and grant FLS through Object Settings. Before you set FLS on individual fields, make sure the community user already has object-level access. See Set Field-Level Security for a Field on All Profiles, Set Field-Level Security for a Field on All Permission Sets, and Enable Object Permissions in Permission Sets.

Objects that Require FLS for Document Generation

Enable FLS on the required fields for each of these objects. Which fields are required depends on how document generation is configured. The admin identifies them based on the templates and processes in use.

Contract Document Version Content Document
Document Envelope
Document Generation Process
Document Recipient
Document Template
Document Template Content Document
Object State Definition
Object State Transition
Object State Value
Object State Action Definition
Object State Transition Action
Context Use Case Mapping
Specific Object Fields that Require FLS

Enable FLS on the Contract Type field for the Contract object.

Enable FLS on these fields for the Contract Document Version (CDV) object.

Created By Full Name
Creation Process Type
Document Template
Document Version Locked
Lock Type
Locked By User Name
