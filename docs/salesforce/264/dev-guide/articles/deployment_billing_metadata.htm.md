---
page_id: deployment_billing_metadata.htm
title: Billing Metadata
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/deployment_billing_metadata.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Revenue Management Deployment
parent_page: deployment_appendix_B.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Billing Metadata

This table provides the metadata deployment reference for Billing in Revenue Management,
    including setup paths and configuration details.

    

        
        
        
        
        
          
            

            

            

            

          

        

        
          
            

            

            

            

          

          
            

            

            

            

          

          
            

            

            

            

          

          
            

            

            

            

          

          
            

            

            

            

          

          
            

            

            

            

          

          
            

            

            

            

          

          
            

            

            

            

          

          
            

            

            

            

          

          
            

            

            

            

          

          
            

            

            

            

          

          
            

            

            

            

          

          
            

            

            

            

          

          
            

            

            

            

          

          
            

            

            

            

          

          
            

            

            

            

          

          
            

            

            

            

          

          
            

            

            

            

          

          
            

            

            

            

          

          
            

            

            

            

          

          
            

            

            

            

          

          
            

            

            

            

          

          
            

            

            

            

          

          
            

            

            

            

          

          
            

            

            

            

          

          
            

            

            

            

          

          
            

            

            

            

          

          
            

            

            

            

          

          
            

            

            

            

          

          
            

            

            

            

          

          
            

            

            

            

          

          
            

            

            

            

          

          
            

            

            

            

          

          
            

            

            

            

          

          
            

            

            

            

          

        

      
| Type | Label | Setup Path | Details |
| --- | --- | --- | --- |
| Setup | Context Service | Context Service > Context Service Settings |  |
| Setup | Data Pipeline | Setup > Feature Settings > Analytics > Data Pipeline |  |
| Permission Set Assignment | Billing Admin | Setup > Users > Permission Sets |  |
| Setup | Enable Billing | Setup > Feature Settings > Billing > Billing Settings |  |
| Setup | Document Generation |  |  |
| Setup | Create Transaction Journals for Transactions | Setup > Feature Settings > Billing > Billing Settings |  |
| Setup | Apply Credits to Posted Invoices | Setup > Feature Settings > Billing > Billing Settings |  |
| Setup | Enable Foreign Exchange Transaction Journal |  |  |
| Setup | Apply Credits to Posted Invoices | Setup > Feature Settings > Billing > Billing Settings |  |
| Setup | Configure Email Delivery Settings | Setup > Feature Settings > Billing > Billing Settings |  |
| Setup | Configure Gapless Sequential Numbering for Billing | Setup > Feature Settings > Billing > Billing Settings |  |
| Setup | Store Transaction Amounts in Corporate Currency | Setup > Feature Settings > Billing > Billing Settings |  |
| Setup | Create Payment Schedules and Payment Schedule Items | Setup > Feature Settings > Billing > Billing Settings |  |
| Setup | Share Payment Accounts | Setup > Feature Settings > Billing > Billing Settings |  |
| Setup | Convert Negative Invoice Lines to Credit Memo Lines | Setup > Feature Settings > Billing > Billing Settings |  |
| Setup | Credit and Payment Application Level | Setup > Feature Settings > Billing > Billing Settings |  |
| Setup | Select Default Credit Memo Flow | Setup > Feature Settings > Billing > Billing Settings |  |
| Permission Sets | Data Pipeline User | Setup > Users > Permission Sets |  |
| Permission Sets | Billing Admin | Setup > Users > Permission Sets |  |
| Permission Sets | Context Service Admin | Setup > Users > Permission Sets |  |
| Permission Sets | Tableau Next Admin | Setup > Users > Permission Sets | For Analytics Dashboard Enabling |
| Permission Sets | Data Cloud Admin | Setup > Users > Permission Sets | For Analytics Dashboard Enabling |
| Permission Sets | BillingAdvanced​PaymentAdministrator | Setup > Users > Permission Sets |  |
| Permission Sets | RevenueLifecycle​ManagementBilling​CustomerService | Setup > Users > Permission Sets |  |
| Permission Sets | BillingAdvancedPaymentOperations | Setup > Users > Permission Sets |  |
| Permission Sets | RevenueLifecycle​ManagementBilling​CreditMemo​Operations | Setup > Users > Permission Sets |  |
| Setup | Default Invoice Template |  |  |
| Setup | FX Gain/Loss Account Lookups |  |  |
| Setup | Context Definition |  |  |
| Setup | Context Mapping |  |  |
| Setup | Intra Context Custom Mapping |  |  |
| Setup | Default DPE Definition to Close Legal Entity Accounting Periods |  |  |
| Setup | Default Invoice Preview Template |  |  |
| Setup | Default Invoice Email Template |  |  |
| Setup | Default Credit Memo Flow |  |  |
