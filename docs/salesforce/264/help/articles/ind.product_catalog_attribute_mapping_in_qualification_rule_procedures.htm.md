---
article_id: ind.product_catalog_attribute_mapping_in_qualification_rule_procedures.htm
title: Attribute Mapping in Qualification Rule Procedures
source_url: https://help.salesforce.com/s/articleView?id=ind.product_catalog_attribute_mapping_in_qualification_rule_procedures.htm&type=5&release=264
release: 264
release_name: Winter '27
area: pcm
parent_article: ind.product_catalog_create_qual_rule_procedure_for_product.htm
fetched_at: 2026-11-23
---

# Attribute Mapping in Qualification Rule Procedures

In your qualification rule procedures, you must map specific attributes from the context definition to the corresponding decision table fields based on the type of the qualification element. In addition, you must map your custom attributes that must be used to evaluate qualification.

REQUIRED EDITIONS
View supported products and editions.

Here’s a table that lists the attributes that you must map based on the type of the qualification element.

TYPE	NODE NAME	ATTRIBUTE NAME	DESCRIPTION
Product Category Qualification or Disqualification	Category	CategoryID	Is mapped to the Category field of the input parameter of the custom element in the procedure.
IsCategoryQualified	Is mapped to the Qualified or Disqualified field of the output parameter of the custom element in the procedure. The product category is qualified when the value is True or Null, and disqualified when the value is False. The CategoryDisqualificationReason field populates the disqualification reason when this attribute is False.
CategoryDisqualificationReason	Is mapped to the Reason field of the output parameter of the custom element in the procedure.
CurrentDate	Is mapped to the EffectiveFromDate and EffectiveToDate field of the input parameter of the custom element in the procedure. The CurrentDate attribute is of the format ‘YYYY-MM-DD’.
Product Qualification or Disqualification	CategoryProduct	ProductId	Is mapped to the Product field of the input parameter of the custom element in the procedure.
RootProductId	Is mapped to the Root Product field of the input parameter of the custom element in the procedure.
ParentProductId	Is mapped to the Parent Product field of the input parameter of the custom element in the procedure.
IsQualified	Is mapped to the Qualified or Disqualified field of the output parameter of the custom element in the procedure. The product is qualified when the value is True or Null, and disqualified when the value is False. The Reason field stores the disqualification reason when this attribute is False.
Reason	Is mapped to the Reason field of the output parameter of the custom element in the procedure.
CurrentDate	Is mapped to the EffectiveFromDate and EffectiveToDate field of the input parameter of the custom element in the procedure. The CurrentDate attribute is of the format ‘YYYY-MM-DD’.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.product_catalog_attribute_mapping_in_qualification_rule_procedures.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
