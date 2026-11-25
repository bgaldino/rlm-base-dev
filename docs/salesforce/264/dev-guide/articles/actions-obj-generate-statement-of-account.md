---
page_id: actions-obj-generate-statement-of-account
title: Generate Account Statement
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/actions-obj-generate-statement-of-account.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-invocable-actions-parent
legacy_page_id: actions_obj_generate_statement_of_account.htm
fetched_at: 2026-11-25
---

# Generate Account Statement

Generates a comprehensive account statement for a specified account with transaction history and balance information.

An account statement includes these details.

- Transaction History—List of all financial transactions, such as invoices, credit memos, debit memos, payments, and refunds, within a specified date range.

- Open Balances—Non-zero balances for invoices and other transactions.

- Account Summary—Aggregated totals including beginning balance, total charges, total payments, and ending balance.

- Multi-currency Support—Transactions across multiple currencies.

This action is available in API version 66.0 and later.

## Supported REST HTTP Methods

**URI:**`/services/data/v68.0/actions/standard/generateAccountStatement`

**Formats:** JSON, XML

**HTTP Methods:** POST

**Authentication:**`Authorization: Bearer TOKEN`

Where TOKEN is a placeholder for your OAuth access token.

## Inputs

| Input | Type | Description |
| --- | --- | --- |
| `accountId` | string | Required. ID of the account for which to generate the statement of account. |
| `associatedAccountIds` | string | List of associated account IDs from hierarchy to include in the statement. You can specify a maximum of 50 accounts. |
| `correlationId` | string | Correlation ID that tracks messages related to the request. These messages are logged in Splunk by the different services involved in the request. If this ID isn’t specified, a random Universally Unique Identifier (UUID) is created. |
| `customFields` | string | JSON string specifying custom fields to include in the statement. As a best practice, we recommend that you limit the number of custom fields up to 30 fields. Valid objects to specify the associated fields are `Invoice`, `CreditMemo`, `Payment`, `DebitMemo`, `Refund`, or `Account`. Available in API version 67.0 and later. |
| `documentTemplateId` | string | Document template ID to use for PDF generation. If you don’t specify a value, the default account statement template is used. |
| `shouldShowOpenBalancesOnly` | boolean | Indicates whether to show only accounts with non-zero balances (`true`) or complete transaction history within date range (`false`). |
| `sortBy` | string | Required. Criteria for sorting transactions. The default and valid value is `Date`. |
| `sortingOrder` | string | Sort order for transactions. Values are `Ascending` or `Descending`. The default value is `Desc`. |
| `startDate` | date | Required. The date from when the transaction history is to be considered in YYYY MM DD format. This parameter value is required when the `shouldShowOpenBalancesOnly` parameter value is `false`. The date must be within the last 90 days and can’t be in the future. |
| `transactionTypes` | string | List of transaction types to include in the statement. If you don’t specify a value or if it’s empty, all transaction types are included. Valid values are `All`, `Invoice`, `CreditMemo`, `Payment`, `DebitMemo`, or `Refund`. |

Example:

```
{"Invoice": ["field1", "field2"], "Account": {"base": ["field1"], "associated": ["field2"]}}
```

## Outputs

| Output | Type | Description |
| --- | --- | --- |
| `accountId` | string | ID of the account for which to generate the account statement. |
| `requestIdentifier` | string | Unique request identifier for tracking the async operation. |
| `statusUrl` | string | URL that tracks the status of the request and retrieves the generated document. |
| `templateId` | string | Document template ID that’s used for PDF generation. |

## Example

**POST**

This example shows a sample request for the Generate Account Statement action.

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

This example shows a sample response for the Generate Account Statement action.

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

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/actions-obj-generate-statement-of-account.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
