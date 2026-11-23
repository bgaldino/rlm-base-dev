---
page_id: cml_debugging_cml.htm
title: Debugging Constraint Modeling Language (CML)
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/cml_debugging_cml.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Configurator
parent_page: cml_what_is_constraint_modeling_language.htm
fetched_at: 2026-11-23
---

# Debugging Constraint Modeling Language (CML)

For optimal performance with CML, follow the performance guidelines and use debug
logging to debug constraint models.

Follow these performance guidelines to prevent performance issues.

| Metric | Optimal | marginal | critical |
| --- | --- | --- | --- |
| Total Execution Time | <100 ms | 100 ms–1 s | >1 s (10 s = hard timeout) |
| Backtracks | <1,000 | 1,000–10,000 | >10,000 |
| Constraint Violations | 0 | 1–100 | >100 |

- Asset count impact: Configurations with 2,500 or more assets can experience noticeable
  evaluation delays. Keep asset counts below this threshold, or expect longer execution times
  as the count grows.
- OR-chain overload: Long chains of OR conditions force the engine to explore many
  alternative paths, which drives up backtracks and execution time. Refactor these rules using
  boolean intermediary variables that consolidate the conditions, so the engine evaluates a
  single flag instead of rechecking every branch.
- Domain range reduction: Narrow the range of values a variable can take to give the engine
  fewer possibilities to test, cut backtracks, and speed up constraint solving. Apply tighter
  bounds, remove unreachable values, and split broad domains into smaller sets so the solver
  converges faster.

To debug constraint models and troubleshoot performance issues, turn on debug logging in Apex
and set the debug log level to FINE. For more information on debug logging in Salesforce, see
these topics in Salesforce Help:

- [Set Up Debug Logging](https://help.salesforce.com/s/articleView?id=xcloud.code_add_users_debug_log.htm&language=en_US "HTML (New Window)")
- [Debug Log](https://developer.salesforce.com/docs/atlas.en-us.264.0.apexcode.meta/apexcode/apex_debugging_debug_log.htm "HTML (New Window)")
- [Debug Log Levels](https://help.salesforce.com/s/articleView?id=platform.code_setting_debug_log_levels.htm&language=en_US "HTML (New Window)")

Use the Apex log to get information about constraint rules engine performance when running a
constraint model, including performance degradation or unexpected behavior. To improve
performance, modify the constraint model based on information in the log.

For tips on writing trouble-free CML, see [Constraint Modeling Language (CML) Best
Practices](./cml_cml_best_practices.htm.md "To prevent performance degradation or unexpected behaviors when the constraint engine executes CML code, follow these practices when writing code.").

- **[About the Apex Debugging Log File](./cml_about_the_apex_debugging_log_file.htm.md)**  
  The Apex debugging log file contains three sections: RLM\_CONFIGURATOR\_BEGIN, RLM\_CONFIGURATOR\_STATS, and RLM\_CONFIGURATOR\_END.
- **[Use the Apex Debugging Log File](./cml_use_the_apex_debugging_log_file.htm.md)**  
  To find possible reasons for the performance problems and identify solutions, look at the RLM\_CONFIGURATOR\_STATS section of the log file.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/cml_debugging_cml.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
