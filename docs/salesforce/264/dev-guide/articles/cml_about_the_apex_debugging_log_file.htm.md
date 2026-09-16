---
page_id: cml_about_the_apex_debugging_log_file.htm
title: About the Apex Debugging Log File
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/cml_about_the_apex_debugging_log_file.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Configurator
parent_page: cml_debugging_cml.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# About the Apex Debugging Log File

The Apex debugging log file contains three sections: RLM_CONFIGURATOR_BEGIN,
    RLM_CONFIGURATOR_STATS, and RLM_CONFIGURATOR_END.

    

## RLM_CONFIGURATOR_BEGIN

      
      

JSON representation of the request payload to ExecuteConstraintsRESTService.

      

```
"contextProperties" : { },
"rootLineItems" : [ {
  "attributes" : { },
  "properties" : {  },
  "ruleActions" : null,
  "attributeDomains" : { },
  "portDomainsToHide" : { },
  "lineItems" : [ {} ]
} ],
"orgId" : "00Dxx0000006H2F"
}
```

    

    

## RLM_CONFIGURATOR_STATS

      
      

Key statistics of the request execution by the constraint engine, as in this example.

      

```
"rootId" : "0QLxx0000004D1uGAE",  //Root ID that is being configured
"Product" : "SFDC License",  //Root product name
"Total Execution Time" : "2ms",  //Total solver time
"Constraints Execution Stats" : "Distinct: 18 Total: 70",  //Number of distinct and total constraint satisfaction attempts
"Solving goal AndGoal([ConfigureComponentGoal(RootProduct RootProduct_0)]) took " : "2ms",  //Total solver time for the goal
"Configurator Stats" : "Total Time 2ms",  //Total time
"Number of Component" : "6",  //Number of components instantiated
"Number of Variables" : "42",  //Number of variables instantiated
"Number of Constraints" : "13",  //Number of constraints instantiated
"Number of Backtracks" : "0",  //Number of backtracks solver did for the last choice point
"Constraints Violation Stats" : "Distinct: 0 Total: 0",  //Distinct and total number of constraint violations followed by a list of top 10
"ChoicePoint Backtracking Stats" : "Distinct: 0 Total: 0"  // Distinct and total number of backtracked choice points followed by a list of top 10
}
```

    

    

## RLM_CONFIGURATOR_END

      
      

JSON representation of the response payload from ExecuteConstraintsRESTService.

      

```
"id" : "0QLxx0000004D1uGAE",
"rootId" : null,
"parentId" : null,
"cfgStatus" : "User",
"name" : "RootProduct",
"relation" : null,
"source" : "SalesTransaction.SalesTransactionItem",
"qty" : 1,
"actionCode" : null,
"modelName" : "Support_instance_variable_in_CML",
"productId" : "01txx0000006iP2AAI",
"productRelatedComponentId" : null,
"attributes" : {},  "properties" : {},
"ruleActions" : [ {} ],   "attributeDomains" : {},  "portDomainsToHide" : {},
"lineItems" : [ {} ]
}
```
