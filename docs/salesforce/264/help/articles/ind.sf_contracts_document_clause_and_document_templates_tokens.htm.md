---
article_id: ind.sf_contracts_document_clause_and_document_templates_tokens.htm
title: Tokens for Document Clauses and Document Templates
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_document_clause_and_document_templates_tokens.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_document_clause.htm
fetched_at: 2026-10-13
---

# Tokens for Document Clauses and Document Templates

Placeholder and merge tokens mark values that change in clause content. Clause tokens link document templates to specific clause versions in the library.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, Professional, and Developer Editions

Organizations reuse legal and commercial language from the Document Clause Library in contracts and other sales documents, such as quotes. To learn more, see Add a Special Term to a Quote. Tokens embedded in clause content help you manage dynamic content. On the other hand, clause tokens help you retain the latest version or specified version of the clause in the document template.

TIP You can reuse the same token name in more than one place, but every instance shares one value. To use different values, create unique token names, both at the document template level and within document clauses.
Tokens Inside Clause Content

Placeholder and merge tokens are content tokens. Clause designers add them to document clause content so part of the clause can change without rewriting the entire clause.

Merge tokens mark values that Salesforce fills from mapped Salesforce data when you generate a document, for example, through your template's token-mapping method. See Context Service for Document Generation. Use merge tokens when the clause includes data from Salesforce fields. Merge tokens use curly brackets, for example, {{CustomerName}}.

With placeholder tokens, users provide a value at run time. Designers can set a default value during clause creation. At generation, Salesforce inserts the default when one exists. Users who have edit rights to the document can change placeholder values in supported experiences, such as quote special terms or Microsoft 365 contract authoring. Placeholder tokens use double angle brackets, for example, <<EffectiveDate>>.

Reference Clauses in Document Templates

If document templates contain clause tokens, Salesforce Document Generation can reference them from the clause library to fetch the latest version or a configured version. Salesforce supports two types of clause tokens.

Clause Template Identifier: Copied into a document template in the format {{CL_<ClauseSetName>_<ClauseName>_<language>}}, this token resolves to a document clause's latest active version at document generation.
Clause Template Version Identifier: Copied into a document template in the format {{CL_<ClauseSetName>_<ClauseName>_<language>_<ClauseVersion>}}, this token resolves to one specific version of a document clause.
NOTE For successful document generation, preserve the clause token format exactly as it's derived from the document clause. Altering the clause token causes resolution failure, resulting in blank clause content that requires manual correction.
How Tokens Flow from the Clause Library to the Generated Document

Tokens follow the clause lifecycle: Design the clauses in your clause library, assemble the template, generate the document, then complete any remaining placeholder values during authoring.

Clause designers build library content and add content tokens, such as merge or placeholder tokens, where values can change.
Template designers assemble Microsoft 365 templates by manually inserting clause content, clause tokens, or both.
During document generation, Salesforce resolves merge tokens and clause tokens. If you set placeholder defaults, the system applies them, and users fill in any remaining placeholder values during supported authoring flows.
Data true-up tokens are supported within clauses. See Data True-Up Tokens in Document Templates.
