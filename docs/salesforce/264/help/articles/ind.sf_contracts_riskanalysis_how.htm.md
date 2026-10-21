---
article_id: ind.sf_contracts_riskanalysis_how.htm
title: How Contract Risk Analysis Works
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_riskanalysis_how.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_contract_documnet_actions_overview.htm
fetched_at: 2026-10-13
---

# How Contract Risk Analysis Works

Contract Risk Analysis compares each modified clause in a contract against your approved playbook. After a reviewer makes changes to a version of the contract, the author runs the analysis using the Microsoft 365 Word add-in. A generative AI model scores each modified clause, explains the risk, and recommends the mitigation content to add to the contract.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Performance editions.

Contract Risk Analysis is a runtime feature for the contract author. The author runs the analysis in the Microsoft 365 Word add-in after an internal or external reviewer adds changes to the contract document version. By using the tracked changes, Salesforce compares the current and previous text against your grounding document playbook, scores each modified clause, and recommends mitigation content to copy into the contract.

End-To-End Flow

Understanding the flow helps you troubleshoot missed matches and unexpected recommendations.

Trigger: The contract author opens a contract document version with the status InReview or InExternalReview in the Microsoft 365 Word add-in and clicks Run Risk Analysis.
Playbook lockup: Salesforce uses the contract's object and record type combination to find the matching playbook assignment. If Salesforce doesn't find a matching assignment, users can't initiate risk analysis.
Active version selection: Salesforce uses the Active version of the assigned playbook. Only one version is active per playbook at any time.
Change detection: Microsoft identifies modified clauses in the reviewed document, the changes introduced during internal or external review.
Hybrid search in Data 360: For each modified clause, Salesforce searches the playbook's indexed content in Data 360 by using hybrid (vector plus keyword) search. The search runs over the section-aware chunks created when you upload the version and returns the highest-scoring chunks.
LLM analysis: Salesforce passes the top-ranked chunks with their similarity scores into the LLM prompt. The model uses the retrieved playbook context to detect deviations, propose fallback language, and highlight escalation paths for the specific modified clause.
What the Risk Analysis Returns
Contract risk rating: The overall severity of the run, aggregated from the severities of all flagged clauses.
Modified clauses: Each changed section, clause, or paragraph, with its severity badge Critical, High, Medium, Low and a status of Flagged, Mitigated, or Reviewed.
Content changes: Side-by-side comparison of previous content, current content, and risk impact. Risk impact includes both the deviation and the potential business or legal exposure.
Recommended mitigation: Guidance from the playbook on how to rewrite the flagged content to align with your organization's standard terms.
Suggested changes: A ready-to-use clause draft. The author copies the text into the document and applies it manually.
Run history: A dropdown of prior runs on the same contract document version, up to 50 runs, so the author can compare findings across iterations.
Risk analysis summary: An overview page showing the overall risk level and a list of all changed clauses and sections, each with its associated risk badge. Available from the View Summary icon in the panel.
Completion notification: An in-app notification when the run completes, indicating whether the analysis succeeded, or failed.
NOTE To keep risk analysis results consistent and reliable:
Use consistent document formatting in each version so chunk boundaries stay stable across revisions.
Archive playbook versions rather than deleting them to preserve the audit trail.
Review each generative AI output before you apply it to the contract. This includes risk explanations, mitigation drafts, and playbook recommendations.
Set Up Contract Risk Analysis
Contract Risk Analysis compares each modified clause in a contract against your approved playbook. After a reviewer makes changes to a version of the contract, the author runs the analysis using the Microsoft 365 Word add-in. A generative AI model scores each modified clause, explains the risk, and recommends the mitigation content to add to the contract.
Analyze Contract Risks After a Review
After an internal or external reviewer adds changes to a contract document version, run a risk analysis to see how the modified clauses deviate from your approved playbook. Review the severity, and apply the recommended mitigation content.
