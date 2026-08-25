---
page_id: sforce_api_objects_invoicebatchruncriteria.htm
title: InvoiceBatchRunCriteria
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_invoicebatchruncriteria.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_std_objects_parent.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# InvoiceBatchRunCriteria

Represents a batch processing job and its required criteria in
         Billing. During an invoice batch run, all billing schedules that meet the specified
         criteria are processed, resulting in the generation of invoices. This object is
      available in API version 62.0 and later.

      

## Supported Calls

      
      

         `describeLayout()`, 
         `describeSObjects()`, 
         `getDeleted()`,
         `getUpdated()`,
         `query()`, 
         `retrieve()`
      

      

      

## Special Access Rules

         
         

You need the Billing Admin permission set to access this object.

      

      

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
- 
- 

                  

                  
                     

                     

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

                  

               

            
| Field | Details |
| --- | --- |
| BillingCycleCount | **Type** int **Properties** Filter, Group, Nillable, Sort **Description** The number of billing periods to process per billing schedule. Billing schedules are invoiced for the specified number of billing periods, regardless of a target date. This field is available in API version 68.0 and later. |
| Comments | **Type** textarea **Properties** Filter, Nillable, Sort **Description** Additional notes or comments for the invoice batch run criteria. |
| CriteriaExpression | **Type** textarea **Properties** Filter, Nillable, Sort **Description** The formula that specifies criteria for filtering the billing schedules. For example, you can filter billing schedules by the currency code. |
| CriteriaMatchType | **Type** picklist **Properties** Defaulted on create, Filter, Group, Restricted picklist, Sort **Description** Required. The type of matching criteria required for the batch. Valid value is `MatchAll`. The default value is `MatchAll`. |
| ExpectedInvoiceStatus | **Type** picklist **Properties** Filter, Group, Nillable, Restricted picklist, Sort **Description** The type of invoice a batch run generates. Valid values are: `Draft` `Posted` |
| InvoiceBatchRunCriteriaNumber | **Type** string **Properties** Autonumber, Defaulted on create, Filter, idLookup, Sort **Description** Required. The auto-generated reference number for the invoice batch run criteria. |
| InvoiceDate | **Type** date **Properties** Filter, Group, Nillable, Sort **Description** The date displayed on the invoice. This date is also used for tax calculations. |
| InvoiceDateOffset | **Type** int **Properties** Filter, Group, Nillable, Sort **Description** The offset that's applied to the target date to calculate the invoice date. |
| IsInvoiceDateFromRunDate | **Type** boolean **Properties** Defaulted on create, Filter, Group, Sort **Description** Required. Indicates whether the invoice date is derived from the run date (`true`) or not (`false`). The default value is `false`. Available in API version 63.0 and later. |
| OwnerId | **Type** reference **Properties** Filter, Group, Sort **Description** Required. The ID of the user who created the invoice batch run criteria. This field is a polymorphic relationship field. **Relationship Name** Owner **Refers To** Group, User |
| ShouldCatchUpBillRun | **Type** boolean **Properties** Defaulted on create, Filter, Group, Sort **Description** Required. Indicates whether the invoice batch run advances billing schedules to a target date without generating invoices for prior billing periods (`true`) or not (`false`). This field is available in API version 68.0 and later. The default value is `false`. |
| ShouldRecalculateAllForecastLn | **Type** boolean **Properties** Defaulted on create, Filter, Group, Sort **Description** Required. Indicates whether to include all billing schedules in the billing forecast run (`true`) or not (`false`). This field is available in API version 68.0 and later. The default value is `false`. |
| TargetDate | **Type** date **Properties** Filter, Group, Nillable, Sort **Description** The target date for the invoice run. Billing schedules having the next billing date on or before this date will be picked up for invoicing. |
| TargetDateDayOfMonth | **Type** int **Properties** Filter, Group, Nillable, Sort **Description** The day of the month to be used as the target date. Billing schedules with next billing date on or before this target date are selected for invoice generation. For example, if this value is set to the 10th, all schedules with a next billing date of 10th of the corresponding month or earlier are included in the invoice batch run. This field is available in API version 68.0 and later. |
| TargetDateMonthOffset | **Type** int **Properties** Filter, Group, Nillable, Sort **Description** The number of months offset applied to the scheduled run date to calculate the target date. A value of 0 uses the current month, a positive value offsets forward, and a negative value offsets backward. For example, if the run date is 10th July and Target Day of Month is 15, then Target Date would be 15th July if Target Month Offset is 0, 15th August if Target Month Offset is 1, and so on. This field is available in API version 68.0 and later. |
| TargetDateOffset | **Type** int **Properties** Filter, Group, Nillable, Sort **Description** The offset that's applied to the next run date to calculate the target date. |
