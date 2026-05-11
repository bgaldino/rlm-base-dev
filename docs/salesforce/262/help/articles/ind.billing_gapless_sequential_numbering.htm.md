---
article_id: ind.billing_gapless_sequential_numbering.htm
title: Gapless Sequential Numbering
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_gapless_sequential_numbering.htm&type=5&release=262
release: 262
release_name: Summer '26
area: billing
fetched_at: 2026-05-11
---

# Gapless Sequential Numbering

For businesses that handle large volumes of transactions, assigning unique, gapless sequential numbers to invoice and credit memo records is essential for legal compliance, auditing, and reconciliation. Manual numbering introduces operational complexity and increases the risk of errors or fraudulent activity. Billing addresses this challenge by automating the assignment of unique identifiers according to the defined sequence policies.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions with the Revenue Cloud Billing license. Contact your Salesforce account executive for more information.
Key Terms

Before you define your sequence policies, review these concepts.

Sequential Numbering
This feature automatically generates unique, formatted, and sequential identifiers for posted invoice and credit memo records.
Sequence Policy
This configuration record is where you define specific rules for how a sequential number is generated and assigned to invoice and credit memo records.
Sequence Pattern
The structure of an invoice or a credit memo number that determines how it appears and includes components such as static text and dynamic placeholders. {SequenceValue} is a mandatory component for the sequence pattern.
Sequence Value
The unique, incrementing value that forms the core of the invoice or credit memo number. The system automatically updates this dynamic placeholder {SequenceValue} in the sequence pattern based on the sequence properties. For example, in the invoice number INV-2025-1001, the sequence value is 1001.
Sequence Pattern Value
This is the final, complete identifier that's generated and assigned to a record after all placeholders in the sequence pattern are resolved. For example, if the sequence pattern is US-{YYYY}-{SequenceValue}, the resolved value is US-2025–1001. The generated sequential pattern value is stamped to an invoice or a credit memo record and stored as the invoice or credit memo number.
Business Use Case: Create Unique Sequential Invoice Numbers

Global Electronics, a company that operates in different countries through multiple legal entities, faced a significant issue with its generic invoice numbers. The finance team couldn’t identify the legal entity responsible for a sale without manually checking customer accounts. This process was slow, prone to errors, and complicated their ability to analyze sales revenue. Additionally, their invoice numbers had unexplained gaps that resulted in traceability issues during auditing.

To eliminate this inefficiency, the company used sequence policies to automatically assign a unique, gapless invoice number based on the legal entity from which the products were sold. For example, an invoice for products sold from the U.S. office now carries a number like USA-2025-1001, indicating the country, year, and sequence value. An invoice for sales from Germany shows a number such as DE-12-2025-2001, indicating the country, month, year, and sequence value. An invoice for sales from India uses a number such as IN/12-02-2025/00123, indicating the country, date, month, year, and sequence value. Each invoice number is tailored to reflect the legal entity code and the specific numbering rules legally mandated for that region.

This automation transformed their financial tracking by eliminating manual data entry and reducing errors. Now, both the finance and sales teams have instant clarity, as the invoice number itself reflects the legal entity responsible for the sale and adheres to the regional legal regulations for invoice bookkeeping and auditing purposes.
