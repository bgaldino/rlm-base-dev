---
article_id: ind.sf_contracts_riskanalysis_analyze.htm
title: Analyze Contract Risks After a Review
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_riskanalysis_analyze.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_riskanalysis_how.htm
fetched_at: 2026-10-13
---

# Analyze Contract Risks After a Review

After an internal or external reviewer adds changes to a contract document version, run a risk analysis to see how the modified clauses deviate from your approved playbook. Review the severity, and apply the recommended mitigation content.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Performance editions.
USER PERMISSIONS NEEDED
To open a contract document version in Microsoft 365 Word:	Microsoft 365 Word User
To run the contract risk analysis:	

Microsoft 365 Word User

AND

Contracts AI User

AND

Document Playbook User

AND

Prompt Template User


To check in the updated contract document version:	CLM Runtime User
TIP Risk analysis evaluates only the clauses with tracked changes. If you accept a change before running the analysis, it’s no longer detected as a modification.

Contract Risk Analysis tracks your progress in two ways as you work through flagged clauses: through mitigation status and through reruns. As you resolve clauses, your risk view narrows to what's still outstanding rather than what you've already addressed. Each new contract document version that you check in supports a fresh, separate run. You can track how the risk profile changes across runs within the same version.

Before you begin:

You're the contract author for the Contract Document Version (CDV) and hold the required permission sets.
An internal or external review cycle is in place. Risk analysis runs on the returned, checked-in version, not on a per-review draft. See Contract Review in Microsoft 365. The returned, updated version is checked in with status InReview or InExternalReview.
A playbook assignment exists for the contract's object and record type combination, and its Active version is fully indexed into Data 360.
In the Microsoft 365 Word add-in, open the reviewed contract document.
Before you run risk analysis, press Ctrl+S to save the document and make sure your latest edits sync to the checked-in version. If your changes were made recently, wait 15–30 seconds for the sync to complete before starting the run. Otherwise, recent edits can be left out of the analysis.
Click the Risk Analysis icon.
In the Risk Analysis panel, click Run Risk Analysis.
You can't start a new risk analysis while another analysis is in progress on the same contract document version. Wait for the current analysis to finish.
In the panel header, click the refresh icon to check status and view results.
When the run completes, the panel populates with the results.
In the results view, review Contract Risk Rating.
The rating summarizes the highest-severity clauses in the run and shows one of these values: Critical, High, Medium, or Low.
To review the flagged clauses.
From the Clauses tab, use the severity filter to narrow the modified clauses list.
Select a severity value to show only clauses at that severity.
Click a flagged clause to see details.

The clause details expand and show:

SECTION	DESCRIPTION
Content Changes	Side-by-side table with Previous Content, Current Content, and Risk Impact. A short explanation of the legal or business risk that the change introduces.
Recommended Mitigation	AI-drafted text for the flagged content to mitigate identified risks in this contract document version. Each flagged clause has a mitigation review status (Flagged, Mitigated, or Undo) that updates as the author reviews and acts on it.
Suggested Changes	Standard content from your document playbook that mitigates the identified risk.
Playbook Recommendation	The recommended content from your playbook.
Click a clause to review the recommended mitigation and the suggested changes.
To copy the recommended content into the contract document, click the copy icon.
Copying doesn't change the clause or its status. You still apply the change yourself.
Paste the copied content into the contract document and edit it as needed.
To change the clause’s risk status to reviewed, click Mark as Reviewed.
Reviewed clauses are excluded from future runs unless you edit that clause content again. To revisit a reviewed clause, click Undo. The status changes back to Flagged. You can also click View Summary for a rolled-up view of risk findings across the whole document.
Run additional analyses as you revise.
Make changes to the document and check in a new contract document version.
Click Run Again to start a new risk run on the latest version.
Prior runs remain available from the Run dropdown (Run 1, Run 2, and so on) with the run date shown next to the selected run.
If the Active version of the assigned playbook changes after your last risk analysis, click Run Again to rerun with the updated playbook version.
Use the runs dropdown to compare results across revisions of the same contract.
