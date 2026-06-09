---
page_id: connect_resources_generate_account_statement.htm
title: Generate Account Statement (POST)
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_generate_account_statement.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_resources.htm
fetched_at: 2026-06-09
---

# Generate Account Statement (POST)

Generate comprehensive account statement with transaction history and
balance information.

An account statement includes these details.

- Transaction History—List of all financial transactions, such as invoices, credit
  memos, debit memos, payments, and refunds, within a specified date range.
- Open Balances—Non-zero balances for invoices and other transactions.
- Account Summary—Aggregated totals including beginning balance, total charges,
  total payments, and ending balance.
- Multi-currency Support—Transactions across multiple currencies.

Resource
:   ```
    /revenue/billing/accounts/accountId/statement
    ```

Resource example
:   ```
    https://yourInstance.salesforce.com/services/data/v67.0/revenue/billing/accounts/accountId/statement
    ```

Available version
:   66.0

HTTP methods
:   POST

Request body for POST
:   JSON example
    :   ```
        {
          "shouldShowOpenBalancesOnly": false,
          "startDate": "2025-09-01",
          "transactionTypes": {
            "transactionTypes": [
              "Invoice"
            ]
          },
          "sortBy": "DueDate",
          "sortingOrder": "Ascending",
          "associatedAccountIds": {
            "associatedAccountIds": [
              "001xx000003DGb5AAG",
              "001xx000003DGb6AAG"
            ]
          },
          "documentTemplateId": "0TRxx000000002YGAQ",
          "correlationId": "monthly-statement-sept-2025",
          "customFields": "{\"Invoice\": [\"TotalAmountWithTax\"], \"Account\": {\"base\": [\"Phone\", \"Fax\"], \"associated\": [\"Website\"]}}}"
        }
        ```

    Properties
    :   | Name | Type | Description | Required or Optional | Available Version |
        | --- | --- | --- | --- | --- |
        | `associatedAccountIds` | String[] | List of associated account IDs from hierarchy to include in the statement. You can specify up to 50 accounts. | Optional | 66.0 |
        | `correlationId` | String | Correlation ID for tracking the request across systems. | Optional | 66.0 |
        | `customFields` | String | JSON string specifying custom fields to include in the statement. As a best practice, we recommend that you limit the number of custom fields up to 30 fields. Valid objects to specify the associated fields are:   - ```   Invoice   ``` - ```   CreditMemo   ``` - ```   Payment   ``` - ```   DebitMemo   ``` - ```   Refund   ``` - ```   Account   ```  Here's the expected format. ``` {"Invoice": ["field1", "field2"], "Account": {"base": ["field1"], "associated": ["field2"]}} ``` | Optional | 67.0 |
        | `documentTemplateId` | String | Document template ID to use for PDF generation. If you don’t specify a value, the system auto-resolves by using the default template. | Optional | 66.0 |
        | `shouldShowOpenBalancesOnly` | Boolean | Indicates whether to show open balances only (`true`) or not (`false`). If set to `true`, the API shows only accounts with non-zero balances. If set to `false`, this API shows complete transaction history within the date range from the start date. | Optional | 66.0 |
        | `sortBy` | String | Criteria for sorting transactions. The default and valid value is `Date`. | Optional | 66.0 |
        | `sortingOrder` | String | Sort order for transactions. Valid values are:   - `Ascending` - `Descending`  The default value is `Descending`. | Optional | 66.0 |
        | `startDate` | String | Start date for the transaction history. The required format is `YYYY-MM-DD`. The system processes records up to 90 days from this date. | Required | 66.0 |
        | `transactionTypes` | String[] | List of transaction types to include in the statement. If you don’t specify a value or the value is empty, all transaction types are included. Valid values are:   - `All` - `CreditMemo` - `DebitMemo` - `Invoice` - `Payment` - `Refund` | Optional | 66.0 |

Response body for POST
:   [Account Statement
    Response](./connect_responses_statement_of_account_output.htm.md "Output representation of the details of the generated account statement with async tracking details.")
