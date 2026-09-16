---
page_id: apex_connectapi_input_standalone_credit_memo_charge.htm
title: ConnectApi.StandaloneCreditMemoChargeInputRequest
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_connectapi_input_standalone_credit_memo_charge.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_apex_input_classes.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# ConnectApi.StandaloneCreditMemoChargeInputRequest

Input representation of the details of the charge lines of a credit memo.

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

- 
- 
- 

              

              

            

            
              

              

              

              

              

            

| Property | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `addresses` | [Credit Memo Addresses Input](./apex_connectapi_input_credit_memo_addresses.htm.md) | Details of the billing and shipping addresses. | Optional | 62.0 |
| `chargeAmount` | Double | Charge amount for the credit memo. | Required | 62.0 |
| `description` | String | Description of the created credit memo charge line. | Optional | 62.0 |
| `endDate` | String | End date of the credit memo charge line. | Optional | 62.0 |
| `isTaxOnlyCredit` | Boolean | Indicates whether the credit is for tax only (`true`) or not (`false`). | Optional | 62.0 |
| `productId` | String | ID of the product record that the credit memo is issued on. | Optional | 62.0 |
| `productName` | String | Name of the product that the credit memo is issued on. | Optional | 62.0 |
| `startDate` | String | Start date of the credit memo charge line. | Optional | 62.0 |
| `taxEffectiveDate` | String | Date from when the tax is applicable. | Optional | 62.0 |
| `taxes` | List[ConnectApi.StandaloneCreditMemoTaxInputRequest](./apex_connectapi_input_standalone_credit_memo_tax.htm.md) | List of credit memo tax lines. | Optional | 62.0 |
| `taxStrategy` | `ConnectApi.StandaloneTaxStrategyEnum` | Tax strategy to be applied to this credit memo charge line, child treatment lines, and tax lines. You can override the tax strategy at the individual credit memo lines or tax lines level. Valid values are: `Ignore`—Specifies that the creation of tax lines must be ignored. `Manual Override`—Specifies that the provided tax values must be considered for taxes. `Calculate`—Specifies that tax must be calculated by using the API. | Optional | 62.0 |
| `treatmentId` | String | ID of the tax treatment record that’s used to calculate tax. | Optional | 62.0 |
