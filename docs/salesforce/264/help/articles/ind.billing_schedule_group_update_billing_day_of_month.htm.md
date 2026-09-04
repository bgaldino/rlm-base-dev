---
article_id: ind.billing_schedule_group_update_billing_day_of_month.htm
title: Bill Day of Month
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_schedule_group_update_billing_day_of_month.htm&type=5&release=264
release: 264
release_name: Winter '27
area: billing
parent_article: ind.billing_schedule_group_update.htm
fetched_at: 2026-09-04
---

# Bill Day of Month

Bill day of the month is the day of the month on which a recurring billing process is scheduled to occur to generate invoices from billing schedules.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with the Revenue Cloud Advanced license or the Revenue Cloud Billing license
Eligibility Conditions for Updating Bill Day of Month

The bill day of month can be updated only if these conditions are met:

The billing term unit of the billing schedule group can't be Milestone Plan.
The billing method of the billing schedule group can't be Usage.
The status of any of the billing schedules related to the billing schedule group can't be Processing or Error.
Updating Bill Day of Month when Billing Type is Advance

If the bill day of month is updated when the billing type is Advance, the next billing date and the next charge date of the related billing schedules remain the same until invoices are generated for the first time. Updating the bill day of month results in these changes:

RESULT	EXAMPLE


When the target date is on the original next billing date:

When an invoice is generated for the first time, it's generated for a partial period. The start date of the partial billing period is the original next charge date and the end date is based on the updated bill day of month.
After invoices are generated for the first time, the next billing date and the next charge date are updated based on the updated bill day of month.
The subsequent invoice is generated for a complete period. The start date of the complete billing period is based on the updated bill day of month and the end date is one day before the next billing date.
	

The current month is January, the bill day of month is 17, and the billing frequency is monthly. So, the billing schedules have these values:

Next Billing Date: 01/17/2025
Next Charge Date: 01/17/2025

The billing operations user has updated the bill day of month to 25.

The target date for generating invoices is 01/17/2025. So, when an invoice is generated on 01/17/2025, it's generated for the partial period of 01/17/2025 to 01/24/2025.

The next billing date is then updated to 01/25/2025 and the next charge date is updated to 02/25/2025.

The subsequent invoice is generated for the period of 01/25/2025 to 02/24/2025.




When the target date is on the updated next billing date:

A partial invoice and a complete invoice are generated after the bill day of month is updated.
The start date of the partial billing period is the original next charge date and the end date is based on the updated bill day of month.
The start date of the complete billing period is based on the updated bill day of month and the end date is one day before the next billing date.
	

The current month is January, the bill day of month is 17, and the billing frequency is monthly. So, the billing schedules have these values:

Next Billing Date: 01/17/2025
Next Charge Date: 01/17/2025

The billing operations user has updated the bill day of month to 25.

The target date for generating invoices is 01/25/2024. So, when invoices are generated on 01/25/2025:

An invoice is generated for the partial period of 01/17/2025 to 01/24/2025.
An invoice is generated for the complete period of 01/25/2025 to 02/24/2025.

The next billing date is then updated to 02/25/2025 and the next charge date is updated to 02/25/2025.

Updating Bill Day of Month when Billing Type is Arrears

If the bill day of month is updated when the billing type is Arrears, it results in these changes:

The next billing date of the related billing schedules is updated immediately.
When invoices and billing period items are generated for the first time after the bill day of month is updated, they’re generated for a partial period.
Subsequent invoices and billing period items are generated for complete periods.

For example, let's assume that the current month is January, the bill day of month is 17, and the billing frequency is monthly. So, the billing schedules have these values:

Next Billing Date: 02/17/2025
Next Charge Date: 01/17/2025

The billing operations user has updated the bill day of month to 25.

The target date for generating invoices is 02/25/2025. So, when an invoices are generated on 02/25/2025: it's generated for the partial period of 01/17/2025 to 01/24/2025.

An invoice is generated for the partial period of 01/17/2025 to 01/24/2025.
An invoice is generated for the complete period of 01/25/2025 to 02/24/2025.

The next billing date is updated to 03/25/2025 and the next charge date is updated to 02/25/2025.

The subsequent invoice is generated for the period of 02/25/2025 to 03/24/2025.
