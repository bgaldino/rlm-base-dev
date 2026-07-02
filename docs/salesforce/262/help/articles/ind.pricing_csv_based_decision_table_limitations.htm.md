---
article_id: ind.pricing_csv_based_decision_table_limitations.htm
title: CSV-Based Decision Table Limitations
source_url: https://help.salesforce.com/s/articleView?id=ind.pricing_csv_based_decision_table_limitations.htm&type=5&release=262
release: 262
release_name: Summer '26
area: pricing
fetched_at: 2026-05-12
---

# CSV-Based Decision Table Limitations

Before configuring a CSV-Based Decision Table, keep these points in mind.

Salesforce Pricing doesn’t support CSV-based decision tables with pricing discovery.
Salesforce Pricing doesn’t recommend or support creating multiple versions for CSV-based decision tables. If multiple versions are created, Salesforce Pricing reads the decision table CSV version that is active on the current date.
You can’t use CSV-based decision tables with the Attribute-Based Price element or with the Price Tracking element’s Save operation. However, the Get operation continues to work.
The Enable Multiple Output Resolution checkbox isn’t supported. Don’t enable this function when you use a CSV-based decision table.
The real-time option isn’t supported for handling CSV data on a quote.
SOQL queries aren’t supported with CSV-based decision tables.
Salesforce Pricing doesn’t provide standard CSV files with this feature. Download the sample template from your specific decision table version, and populate it manually.
Salesforce Pricing doesn’t pass a custom date value to CSV-based decision tables. It uses the current system date and time. If multiple versions are valid on the current date, the highest-ranked version is selected.
CSV-based decision tables support only Datetime, Text, Boolean, and Number data types. Currency isn’t supported as an input rule variable parameter.
Previously created CSV-based decision tables remain unversioned. These tables continue to work in pricing procedures, but built-in versioning isn’t available for them.
SEE ALSO
Decision Table
