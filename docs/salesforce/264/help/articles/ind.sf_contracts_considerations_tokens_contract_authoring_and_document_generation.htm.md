---
article_id: ind.sf_contracts_considerations_tokens_contract_authoring_and_document_generation.htm
title: Considerations for Tokens Across Contract Authoring and Document Generation
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_considerations_tokens_contract_authoring_and_document_generation.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_document_clause.htm
fetched_at: 2026-10-13
---

# Considerations for Tokens Across Contract Authoring and Document Generation

Review these considerations before you add content tokens to document clauses, place clause tokens in templates, or insert clauses during Microsoft 365 contract authoring.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, Professional, and Developer Editions
Contract Authoring

When contract authoring in Microsoft 365, you can insert only document clauses that contain plain text, placeholder tokens, or both. Clauses that contain merge tokens or Data True-Up tokens aren't eligible for insertion. Merge token values resolve from recorded data at document generation.

In Salesforce Contracts for Word add-in:

Placeholder and Data True-Up token values are editable.
Merge token values are read-only.
Clause and token content use content controls. Authors typically change placeholder values in the add-in.

Content control locks vary by template type.

Microsoft 365 Word templates: Use the add-in to change placeholder and Data True-Up token values. For External Review, Salesforce unlocks content controls so reviewers can edit outside the add-in.
Microsoft Word templates: Content controls are unlocked by default. Users can download the document and edit content where needed. When you download a document for External Review, Salesforce unlocks content controls. Internal Review continues to use the accept or reject options, as supported.
Document Generation
If a merge token isn't mapped, for example, through Context Service or your template's token-mapping method, Salesforce doesn't fill that value at generation. That merges token content appears blank in the generated document.
Clause tokens such as {{CL_...}} are supported for document templates up to 25 MB. Large file storage (LFS) templates aren't supported.
If a placeholder token has no default value and no value is supplied at generation, the placeholder can remain in the generated document in its original format, for example, <<Name>>.
If the same document clause appears more than one time in a template or contract document, Salesforce treats it as one reference. Edits to that clause's placeholder values apply to every instance in the document.
