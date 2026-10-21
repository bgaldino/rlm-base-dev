---
article_id: ind.sf_contracts_clause_gen_ptbuilder_modify.htm
title: Customize Clause Generation in Contracts AI
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_clause_gen_ptbuilder_modify.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_clause_generation_enable.htm
fetched_at: 2026-10-13
---

# Customize Clause Generation in Contracts AI

To tailor the generated clause content, modify the standard prompt template by using Prompt Builder. This step is optional and intended for advanced use cases for using Prompt Builder.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Professional, Enterprise, Unlimited, and Developer Editions
USER PERMISSIONS NEEDED
To modify the prompt template:	

CLM Admin User

AND

Contract AI Clause Designer

AND

Prompt Template Manager

Before you begin:

Make sure that Clause Generation org pref is turned on.
Make sure that Prompt Builder and Einstein licenses are enabled in your org.
Configure an extraction template and validate the results at least one time.
From Setup, in the Quick Find box, enter Prompt Builder, and then select Prompt Builder.
Open the Document Clause Generation prompt template.
Save the template as a new version.
Add instructions to the template, such as contextual guidance to generate clauses as per your requirements.
Use the model selector to change the LLM model.
To review your changes, such as clause name and content, click Preview.
(Optional) To refine the results, enter prompt instructions for clause generation in the User Query field, and then click Preview.
If needed, change the LLM model and then click Preview to view the updated results.
After you’re satisfied with the results, save the prompt template and then activate it.
