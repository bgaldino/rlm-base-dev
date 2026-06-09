---
page_id: cml_debugging_cml.htm
title: Debugging Constraint Modeling Language (CML)
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/cml_debugging_cml.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Configurator
parent_page: cml_what_is_constraint_modeling_language.htm
fetched_at: 2026-06-09
---

# Debugging Constraint Modeling Language (CML)

To debug constraint models and troubleshoot performance issues, enable debug logging in
Apex and set the debug log level to FINE.

For more information on debug logging in Salesforce, see these topics in Salesforce Help:

- [Set Up Debug Logging](https://help.salesforce.com/s/articleView?id=xcloud.code_add_users_debug_log.htm&language=en_US "HTML (New Window)")
- [Debug Log](https://developer.salesforce.com/docs/atlas.en-us.262.0.apexcode.meta/apexcode/apex_debugging_debug_log.htm "HTML (New Window)")
- [Debug Log Levels](https://help.salesforce.com/s/articleView?id=platform.code_setting_debug_log_levels.htm&language=en_US "HTML (New Window)")

Use the Apex log to get information about configurator engine performance when running a constraint model, including performance degradation or unexpected behavior. To improve performance, modify the constraint model based on information in the log.

For tips on writing trouble-free CML, see [Constraint Modeling Language (CML) Best
Practices](./cml_cml_best_practices.htm.md "To prevent performance degradation or unexpected behaviors when the constraint engine executes CML code, follow these practices when writing code.").

- **[About the Apex Debugging Log File](./cml_about_the_apex_debugging_log_file.htm.md)**  
  The Apex debugging log file contains three sections: RLM\_CONFIGURATOR\_BEGIN, RLM\_CONFIGURATOR\_STATS, and RLM\_CONFIGURATOR\_END.
- **[Use the Apex Debugging Log File](./cml_use_the_apex_debugging_log_file.htm.md)**  
  To find possible reasons for the performance problems and identify solutions, look at the RLM\_CONFIGURATOR\_STATS section of the log file.
