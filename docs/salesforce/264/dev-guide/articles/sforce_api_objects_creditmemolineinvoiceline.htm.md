---
page_id: sforce_api_objects_creditmemolineinvoiceline.htm
title: CreditMemoLineInvoiceLine
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_creditmemolineinvoiceline.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_std_objects_parent.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# CreditMemoLineInvoiceLine

Represents a junction between a credit memo line and an invoice
         line. This object is available in API version 62.0 and later.

      
         

#### Important

Where possible, we changed noninclusive terms to align with our
            company value of Equality. We maintained certain terms to avoid any effect on customer
            implementations.

      

      

## Supported Calls

      
      

         `describeLayout()`, 
         `describeSObjects()`, 
         `getDeleted()`,
         `getUpdated()`,
         `query()`, 
         `retrieve()`, 
         `update()`
      

      

      

## Special Access Rules

         
         

You need the Credit Memo Operations User permission set to access this object.

      

      

## Fields

         
         

               
               
            
               
                  

                  

               

            

            
                  
                     

                     

: 

: 

: 

                  

                  
                     

                     

: 

: 

: 

                  

                  
                     

                     

: 

: 

: 

                  

                  
                     

                     

: 

: 

: 
: 

: 

: 

                  

                  
                     

                     

: 

: 

: 

                  

                  
                     

                     

: 

: 

: 

                  

                  
                     

                     

: 

: 

: 

                  

                  
                     

                     

: 

: 

: 
: 

                  

                  
                     

                     

: 

: 

: 

                  

                  
                     

                     

: 

: 

: 
: 

: 

: 

: 

                  

                  
                     

                     

: 

: 

: 
: 

: 

: 

                  

                  
                     

                     

: 

: 

: 
: 

: 

: 

                  

                  
                     

                     

: 

: 

: 
: 

: 

: 

                  

                  
                     

                     

: 

: 

: 
: 

: 

: 

                  

                  
                     

                     

: 

: 

: 
: 
- 
- 
- 

                  

                  
                     

                     

: 

: 

: 
: 
- 
- 

                  

                  
                     

                     

: 

: 

: 

                  

                  
                     

                     

: 

: 

: 
: 
- 
- 
- 

                  

            

            
| Field | Details |
| --- | --- |
| Amount | **Type** currency **Properties** Filter, Sort **Description** Required. The amount that's been applied to or unapplied from the invoice line. |
| AppliedDateTime | **Type** dateTime **Properties** Filter, Nillable, Sort **Description** The date and time when the credit memo line was applied to the invoice line. |
| CreditMemoLineBalance | **Type** currency **Properties** Filter, Nillable, Sort **Description** The balance of the credit memo line after it's applied to or unapplied from the invoice line. |
| CreditMemoLineId | **Type** reference **Properties** Filter, Group, Sort **Description** Required. The ID of the credit memo line record that's applied to or unapplied from the invoice line. This field is a relationship field. **Relationship Name** CreditMemoLine **Refers To** CreditMemoLine |
| CreditMemoLineInvoiceLineNumber | **Type** string **Properties** Autonumber, Defaulted on create, Filter, idLookup, Sort **Description** Required. An auto-generated number identifying the credit memo line invoice line. |
| Description | **Type** textarea **Properties** Filter, Group, Nillable, Sort, Update **Description** Additional details about the credit memo line invoice line. |
| EffectiveDateTime | **Type** dateTime **Properties** Filter, Nillable, Sort **Description** The date and time when the credit memo line's application to or unapplication from the invoice line becomes effective. |
| ImpactAmount | **Type** currency **Properties** Filter, Nillable, Sort **Description** The credit memo line invoice line’s financial impact against the customer’s accounts receivable. If the credit memo line invoice line's type is `Applied`, the impact amount is the negative equivalent of the credit memo line invoice line's amount. Otherwise, the impact amount is equal to the credit memo line invoice line's amount. This field is a calculated field. |
| InvoiceLineBalance | **Type** currency **Properties** Filter, Nillable, Sort **Description** The balance of the invoice line after the credit memo line was applied or unapplied. |
| InvoiceLineId | **Type** reference **Properties** Filter, Group, Sort **Description** Required. The ID of the invoice line record to which the credit memo line has been applied or unapplied. This field is a relationship field. **Relationship Name** InvoiceLine **Relationship Type** Master-detail **Refers To** InvoiceLine (the master object) |
| InvoiceLineTaxId | **Type** reference **Properties** Create, Filter, Group, Nillable, Sort **Description** The invoice line tax record to which the credit memo line was applied or unapplied. This field is available in API version 68.0 and later. This field is a relationship field. **Relationship Name** InvoiceLineTax **Refers To** InvoiceLineTax |
| LegalEntityAccountingPeriodId | **Type** reference **Properties** Filter, Group, Nillable, Sort, Update **Description** The ID of the legal entity accounting period record related to the credit memo line invoice line. This field is a relationship field. **Relationship Name** LegalEntityAccountingPeriod **Refers To** LegalEntyAccountingPeriod |
| LegalEntityId | **Type** reference **Properties** Filter, Group, Nillable, Sort, Update **Description** The ID of the legal entity record related to the credit memo line invoice line. This field is a relationship field. **Relationship Name** LegalEntity **Refers To** LegalEntity |
| RelatedCrMemoLineInvcLineId | **Type** reference **Properties** Filter, Group, Nillable, Sort **Description** The ID of the related credit memo line invoice line record of the type `Applied` when the credit memo line invoice line's type is `Unapplied`. This field is a relationship field. **Relationship Name** RelatedCrMemoLineInvcLine **Refers To** CreditMemoLineInvoiceLine |
| SettlementType | **Type** picklist **Properties** Create, Filter, Group, Nillable, Restricted picklist, Sort **Description** Specifies the type of amount settled by the credit memo line that’s applied to the invoice line. This field is available in API version 68.0 and later. Valid values are: `Balance` `Charge` `Tax` |
| Type | **Type** picklist **Properties** Filter, Group, Restricted picklist, Sort **Description** Required. Specifies whether the credit memo line has been applied to or unapplied from the invoice line. Valid values are: `Applied` `Unapplied` |
| UnappliedDateTime | **Type** dateTime **Properties** Filter, Nillable, Sort **Description** The date and time when the credit memo line was unapplied from the invoice line. |
| UnappliedStatus | **Type** picklist **Properties** Filter, Group, Restricted picklist, Sort **Description** Required. Specifies whether the credit memo line has been unapplied from the invoice line. Valid values are: `NA` `No` `Yes` |
