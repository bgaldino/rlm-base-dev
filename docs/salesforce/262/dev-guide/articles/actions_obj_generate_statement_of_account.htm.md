---
page_id: actions_obj_generate_statement_of_account.htm
title: Generate Account Statement
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/actions_obj_generate_statement_of_account.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_invocable_actions_parent.htm
fetched_at: 2026-06-09
---

# Generate Account Statement

Generates a comprehensive account statement for a specified account
with transaction history and balance information.

An account statement includes these details.

- Transaction History—List of all financial transactions, such as invoices, credit
  memos, debit memos, payments, and refunds, within a specified date range.
- Open Balances—Non-zero balances for invoices and other transactions.
- Account Summary—Aggregated totals including beginning balance, total charges,
  total payments, and ending balance.
- Multi-currency Support—Transactions across multiple currencies.

This action is available in API version 66.0 and later.

## Supported REST HTTP Methods

URI
:   `/services/data/v67.0/actions/standard/generateAccountStatement`

Formats
:   JSON, XML

HTTP Methods
:   POST

Authentication
:   `Authorization:
    Bearertoken`

## Inputs

| Input | Details |
| --- | --- |
| accountId | Type  string  Description  Required. ID of the account for which to generate the statement of account. |
| associatedAccountIds | Type  string  Description  List of associated account IDs from hierarchy to include in the statement. You can specify a maximum of 50 accounts. |
| correlationId | Type  string  Description  Correlation ID that tracks messages related to the request. These messages are logged in Splunk by the different services involved in the request. If this ID isn’t specified, a random Universally Unique Identifier (UUID) is created. |
| customFields | Type  string  Description  JSON string specifying custom fields to include in the statement. As a best practice, we recommend that you limit the number of custom fields up to 30 fields. Valid objects to specify the associated fields are:   - ```   Invoice   ``` - ```   CreditMemo   ``` - ```   Payment   ``` - ```   DebitMemo   ``` - ```   Refund   ``` - ```   Account   ```  Here's the expected format. ``` {"Invoice": ["field1", "field2"], "Account": {"base": ["field1"], "associated": ["field2"]}} ``` Available in API version 67.0 and later. |
| documentTemplateId | Type  string  Description  Document template ID to use for PDF generation. If you don’t specify a value, the default account statement template is used. |
| shouldShowOpenBalancesOnly | Type  boolean  Description  Indicates whether to show only accounts with non-zero balances (`true`) or complete transaction history within date range (`false`). |
| sortBy | Type  string  Description  Required. Criteria for sorting transactions. The default and valid value is `Date`. |
| sortingOrder | Type  string  Description  Sort order for transactions. Valid values are:   - `Ascending` - `Descending`  The default value is `Desc`. |
| startDate | Type  date  Description  Required. The date from when the transaction history is to be considered in YYYY MM DD format. This parameter value is required when the `shouldShowOpenBalancesOnly` parameter value is `false`. The date must be within the last 90 days and can't be in the future. |
| transactionTypes | Type  string  Description  List of transaction types to include in the statement. If you don’t specify a value or if it’s empty, all transaction types are included. Valid values are:   - `All` - `Invoice` - `CreditMemo` - `Payment` - `DebitMemo` - `Refund` |

## Outputs

| Output | Details |
| --- | --- |
| accountId | Type  string  Description  ID of the account for which to generate the account statement. |
| requestIdentifier | Type  string  Description  Unique request identifier for tracking the async operation. |
| statusUrl | Type  string  Description  URL that tracks the status of the request and retrieves the generated document. |
| templateId | Type  string  Description  Document template ID that’s used for PDF generation. |

## Example

POST
:   This example shows a sample request for the Generate Account Statement
    action.

    ```
    {
      "inputs": [
        {
          "accountId": "001000000000001AAA",
          "shouldShowOpenBalancesOnly": false,
          "startDate": "2025-01-01",
          "transactionTypes": [
            "All"
          ],
          "sortBy": "Date",
          "sortingOrder": "Descending",
          "associatedAccountIds": [
            "001000000000002AAA",
            "001000000000003AAA"
          ],
          "documentTemplateId": "a0T000000000001AAA",
          "customFields": "{\"Invoice\": [\"TotalAmountWithTax\"], \"Account\": {\"base\": [\"Phone\", \"Fax\"], \"associated\": [\"Website\"]}}}"
        }
      ]
    }
    ```
:   This example shows a sample response for the Generate Account Statement
    action.

    ```
    {
      "accountId": "001AAC0001O5W9pYBF",
      "errors": [],
      "requestIdentifier": "3267407f-0c96-4b8a-a8e0-bb7a71c91a2f",
      "statusUrl": "16PAAC000008AIM",
      "success": true,
      "templateId": "2dtAAC000002oiIYBQ"
    }
    ```
