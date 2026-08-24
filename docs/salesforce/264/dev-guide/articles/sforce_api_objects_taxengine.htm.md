---
page_id: sforce_api_objects_taxengine.htm
title: TaxEngine
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_taxengine.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_std_objects_parent.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# TaxEngine

Represents information about an instance of a tax engine provider as
         well as the merchant credentials for that specific instance. This object is available
      in API version 62.0 and later.

      

## Supported Calls

      
      

         `create()`, 
         `delete()`, 
         `describeLayout()`, 
         `describeSObjects()`, 
         `getDeleted()`,
         `getUpdated()`,
         `query()`, 
         `retrieve()`, 
         `undelete()`, 
         `update()`, 
         `upsert()`
      

      

      

## Special Access Rules

         
         

You need the Tax Admin permission set to access this object.

      

      

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
- 
- 
- 
- 
- 

                  

               

            
| Field | Details |
| --- | --- |
| CustomMetadataTypeApiName | **Type** string **Properties** Create, Filter, Group, Nillable, Sort, Update **Description** The API name of the custom metadata type that defines field mappings for tax callout requests and responses. The custom metadata type name is referenced by the tax engine to identify the metadata configuration to use. This field is available in API version 68.0 and later. |
| DecisionTableId | **Type** reference **Properties** Create, Filter, Group, Nillable, Sort, Update **Description** The ID of the decision table used by the revenue standard tax engine to calculate taxes. If not specified, the standard tax decision table is used by default. This field is available in API version 68.0 and later. This field is a relationship field. **Relationship Name** DecisionTable **Refers To** DecisionTable |
| Description | **Type** textarea **Properties** Create, Filter, Nillable, Sort, Update **Description** The description of an instance of the tax engine provider and merchant credential. |
| ExternalReference | **Type** string **Properties** Create, Filter, Group, idLookup, Nillable, Sort, Update **Description** Information about the external platform used for the tax engine. |
| LastReferencedDate | **Type** dateTime **Properties** Filter, Nillable, Sort **Description** The timestamp when the current user last accessed a tax engine record indirectly, for example, through a list view or related record. |
| LastViewedDate | **Type** dateTime **Properties** Filter, Nillable, Sort **Description** The timestamp when the current user last viewed a tax engine record. If this value is null, it’s possible that the user only accessed the tax engine record or a related list view (LastReferencedDate), but not viewed the tax engine record itself. |
| MerchantCredentialId | **Type** reference **Properties** Create, Filter, Group, Nillable, Sort, Update **Description** Required. The merchant credential setup object in Salesforce. The Tax Calculation API sends the merchant credential's information to the external tax engine that's used for tax calculation. This field is a relationship field. **Relationship Name** MerchantCredential **Refers To** NamedCredential |
| SellerCode | **Type** string **Properties** Create, Filter, Group, Nillable, Sort, Update **Description** Required. The seller code of the transaction for which the tax engine integration log was captured. |
| ShouldCaptureTaxesAtHeader | **Type** picklist **Properties** Create, Defaulted on create, Filter, Group, Sort, Update **Description** Required. Indicates whether taxes are captured at the header level (`true`) or not (`false`). The default value is `false`. Available in API version 66.0 and later. |
| Status | **Type** picklist **Properties** Create, Filter, Group, Restricted picklist, Sort, Update **Description** Required. The status of the tax engine record. Valid values are: `Active` `Inactive` |
| TaxEngineAddress | **Type** address **Properties** Filter **Description** Required. The compound form of the tax engine address. See [Address Compound Fields](https://developer.salesforce.com/docs/atlas.en-us.264.0.api.meta/api/compound_fields_address.htm) for details on compound address fields. This field is a read-only field. |
| TaxEngineName | **Type** string **Properties** Create, Filter, Group, idLookup, Sort, Update **Description** Required. The name of the tax engine record. |
| TaxEngineProviderId | **Type** reference **Properties** Create, Filter, Group, Nillable, Sort, Update **Description** Required. The tax engine provider that's related to the tax engine record. This field is a relationship field. **Relationship Name** TaxEngineProvider **Refers To** TaxEngineProvider |
| TaxPrvdAccountIdentifier | **Type** string **Properties** Create, Filter, Group, Nillable, Sort, Update **Description** The unique identifier of the external tax provider's account. Available in API version 63.0 and later. |
| Type | **Type** picklist **Properties** Create, Filter, Group, Nillable, Restricted picklist, Sort, Update **Description** The type of the tax engine that's used to calculate tax. Valid values are: `CommerceTaxExtension` `RevenueCloudTaxExtension` `StandardTaxEngine` `RevenueStandardTaxEngine`—Available in API version 66.0 and later. `StripeNative` Available in API versions 63.0 and later. |
