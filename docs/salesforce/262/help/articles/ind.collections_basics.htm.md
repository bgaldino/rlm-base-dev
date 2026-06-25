---
article_id: ind.collections_basics.htm
title: Collections and Recovery Basics
source_url: https://help.salesforce.com/s/articleView?id=ind.collections_basics.htm&type=5&release=262
release: 262
release_name: Summer '26
area: collections
parent_article: ind.collections.htm
fetched_at: 2026-06-21
---

# Collections and Recovery Basics

Get to know the key elements of Collections.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: View product and edition availability.
User Personas in Collections
Collections Specialist: Frontline staff responsible for contacting borrowers or collection customers. Makes phone calls, sends emails, and negotiates payment plans with borrowers. A collections specialist’s main goal is to achieve high recovery rates, maintain professionalism, and adhere to company policies and legal guidelines.
Collections Manager (also known as Collections Supervisor): Oversees the entire collections process and team. Develops collection strategies, assigns collection plans to collections specialists, monitors performance, and ensures compliance with regulations. A collections manager’s main goal is to optimize resource allocation, improve collection efficiency, and increase the likelihood of successful debt recovery.
Promise to Pay

A promise to pay is a commitment by the delinquent borrower or customer to pay the overdue amount by a certain date. The Create Promise to Pay prebuilt action is shipped with the Collections feature. A collections specialist can trigger this action from a collection plan record details page to obtain a promise to pay commitment from a customer and to record details, such as the choice between full or partial payment, payment schedule, and whether the payment involves a single or multiple transactions. This action creates the payment schedule and payment schedule items according to the customer’s promise to pay details.

Collection Plan Segment

A collection plan segment is a categorized group of debtors or collection accounts that share similar characteristics, such as the overdue amount, the type of debt, the length of delinquency, or the expected likelihood of recovery. These segments help collection managers tailor their strategies and prioritize their efforts more effectively, making debt collection more targeted and efficient.

There are various approaches to determine a segment for a collection plan. For example, you can determine a segment based on days past due.

0—30 days: An early stage in the collection process and the collection activities in this segment typically involve sending emails, and making reminder calls.
31—60 days past due: A middle stage in the collection process and the collection activities in this segment typically involve more frequent and assertive communication.
61—90 days past due: The last step in the collection process. This stage usually involves sending formal letters, threats of legal action, or referring the debt to a recovery agency.
90+ days past due: The collection activities in this segment typically involve legal action or intensive recovery efforts.

The Collections feature includes the prebuilt event orchestration procedure, DetermineCollectionPlanSegment. This procedure helps you automatically update the collection plan segment for collection plan records in bulk. The procedure references various prebuilt Business Rules Engine components, such as context definition, decision matrix, and actionable event orchestration expression set. Clone and configure these components according to your business needs.

Direct Debit Request

The MuleSoft integration helps your collections specialist request a direct debit to the core banking system with a bulk action called Request Direct Debit. When a mandated direct debit fails, the account enters a collections list due to an outstanding balance. The Request Direct Debit action on an actionable list page helps collections specialists quickly request a new debit from the customer’s account, helping to expedite the collection process and improve overall cash flow.
