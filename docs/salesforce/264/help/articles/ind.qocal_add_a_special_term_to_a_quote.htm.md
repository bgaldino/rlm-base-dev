---
article_id: ind.qocal_add_a_special_term_to_a_quote.htm
title: Add a Special Term to a Quote
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_add_a_special_term_to_a_quote.htm&type=5&release=264
release: 264
release_name: Winter '27
area: transaction_mgmt
parent_article: ind.qocal_manage_contracts_in_revenue_lifecycle_management.htm
fetched_at: 2026-09-04
---

# Add a Special Term to a Quote

Search the Document Clause Library and insert an active clause as a quote special term. Resolve any placeholder tokens, then save so that the term stays relevant to your quote.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Management (formerly Revenue Cloud) where Transaction Management is enabled
USER PERMISSIONS
NEEDED
To create, edit, and search document clause sets and document clauses:	

ClauseUser

OR

ClauseDesignerUser

OR

ClauseDigitalExperienceUser

NOTE
You can add active document clauses with placeholder tokens or no tokens only.
You can't add the same document clause more than one time as a special term on the same quote.
To add the quote special terms on your quote, see Customize Related Lists.
On the quote, go to the Quote Special Terms related list.
Click Add.
In the Search Terms from Clause Library window, filter by clause set, clause, or category, and select a document clause.
Review Language, Category, and Clause Type.
Click Insert.
NOTE While adding a clause to a quote with rich text, the number of characters, including default values and HTML tags, can't exceed 131,000 characters.
If the term includes placeholder tokens, enter values in the token panel, and then click Apply.
Save your changes.

After all placeholders are resolved, you can edit the term content on the quote. After special terms are on the quote, you can generate a quote document that includes those terms. To carry out document generation, create a document template with repeating tokens and map these repeating tokens to Quote Special Terms by using Context Definition & mappings. The Core Omniscript is available for document generation.

See Also

Salesforce Help: Create a Document Clause

Salesforce Help: Example: Generating a Proposal from a Quote by Using Context Service
