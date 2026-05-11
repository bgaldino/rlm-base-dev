---
article_id: ind.billing_credit_memos_void_recover.htm
title: Void or Recover Credit Memos
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_credit_memos_void_recover.htm&type=5&release=262
release: 262
release_name: Summer '26
area: billing
fetched_at: 2026-05-11
---

# Void or Recover Credit Memos

Fix credit memos that are Pending or Error status by recovering them. You can also void an unapplied posted credit memo and reverse the credit by creating a corresponding debit memo.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions with the Revenue Cloud Advanced license or the Revenue Cloud Billing license
USER PERMISSIONS NEEDED
To create credit memos:	

Billing Admin permission set

OR

Billing Operations User permission set

OR

Credit Memo Operations User permission set

Void Credit Memos
From the App Launcher, find and select Credit Memos.
Open the posted credit memo that you want to void.
Click Void Credit Memo.

You can void only an unapplied posted credit memo. After the credit memo is voided, the status of the credit memo changes from Posted to Voided. Billing creates a corresponding debit memo in Posted status to offset the credit amount for the ledger. If original credit memo includes a tax calculation, the debit memo includes the applicable tax details.

Recover Credit Memos
From the App Launcher, find and select Credit Memos.
Open the credit memo that’s in pending or error status.
Click Recover Credit Memo.

After you recover a credit memo, its status changes to Canceled.

If the original credit memo included tax, the credit memo moves to the Voided status. Billing automatically creates a corresponding debit memo in the Posted state to reverse the credit in the ledger. The debit memo includes all the original tax details and tax treatments. Billing reverses the tax interaction in the tax engine. Billing sets the debit memo’s invoice generation status to Not Applicable, so it isn’t invoiced.

NOTE To track the status of the void and recover actions, open the Related tab and review the Async Operation Tracker section.
