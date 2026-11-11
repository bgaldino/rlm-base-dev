---
article_id: ind.sf_contracts_limitations_for_clause_and_content_tokens.htm
title: Limitations for Clause and Content Tokens
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_limitations_for_clause_and_content_tokens.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_document_clause.htm
fetched_at: 2026-10-13
---

# Limitations for Clause and Content Tokens

Review the limits for clause tokens in document templates and content tokens in document clauses before designing clauses or templates.

For token behaviors that differ between contract authoring and document generation, see Considerations for Tokens across Contract Authoring and Document Generation.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, Professional, and Developer Editions
Clause Token Limitations
A document template supports up to 100 unique clause tokens. Repeated instances of the same token count as one.
Salesforce doesn't validate clause tokens at design time. If a clause token doesn't resolve to a valid clause at run time, the token renders blank.
A document clause can't contain another clause token. For example, don't use a clause token ({{CL_}}) in place of a merge token inside clause content. Clause-within-clause isn't supported.
Content Token Limitations
A document clause supports up to 10 unique content tokens. Placeholder and merge tokens share that limit. Repeated instances of the same token count as one.
A placeholder default value can be up to 255 characters. Placeholder tokens support these value types.
String: Use any text value.
Currency: Use non-negative values. Currency conversion isn't supported.
Percentage: Use non-negative values up to 2 decimal places.
Date: Displays in ISO format in clause content, not the user's locale date format.
Separate placeholder tokens with text or other content. Adjacent placeholder tokens aren't supported.
Token values can't contain <<, >>, {{, or }}. Salesforce reserves these characters for token keys.
Salesforce validates that every token is referenced in the clause content before you save. If a token isn't referenced, reference it in the content or remove it.
Merge tokens don't support loop tokens or conditional tokens.
Within a Non-Formatted clause, only plain-text tokens are retained. Rich text, Data True-Up, image, and hyperlink tokens aren't retained.
