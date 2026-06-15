---
page_id: cml_use_the_apex_debugging_log_file.htm
title: Use the Apex Debugging Log File
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/cml_use_the_apex_debugging_log_file.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Configurator
parent_page: cml_debugging_cml.htm
fetched_at: 2026-06-09
---

# Use the Apex Debugging Log File

To find possible reasons for the performance problems and identify solutions, look at
the RLM\_CONFIGURATOR\_STATS section of the log file.

See the values for Total Execution Time, Constraints Violation Stats, and ChoicePoint
Backtracking Stats.

For example, consider how the constraint engine performs with this sample constraint model.
In the constraint model, the value of the `volts`
variable is greater than 110/10000 (`volts = power/amps *
9999;`). The constraint engine must backtrack the `power` variable to find a value that satisfies the constraint, starting with
0.01, 0.02, and so on until it reaches a valid value.

```
relation laptops : Laptop[1..9999];
@(sequence = 1)
decimal(2) power = [0..500];
@(sequence = 1)
int amps = [1..5];
decimal(2)  volts = (power / amps) * laptops[Laptop];
constraint(volts > 110);
```

In the log file for this constraint model, see the execution statistics for Total Execution Time, Constraints Violation Stats, and ChoicePoint Backtracking Stats:

```
"rootId" : "ref_a67c6632_fa1f_40b4_8093_226a9ab8a4d0",
"Product" : "Laptop",
"Total Execution Time" : "676ms",
"Constraints Execution Stats" : "Distinct: 2 Total: 132006",
"Solving goal AndGoal([ConfigureComponentGoal(Laptop Laptop_0)]) took " : "677ms",
"Configurator Stats" : "Total Time 677ms",
"Number of Component" : "1",
"Number of Variables" : "4",
"Number of Constraints" : "1",
"Number of Backtracks" : "49500",
"Constraints Violation Stats" : "Distinct: 1 Total: 41250",
"IntComparison(GT,[DecimalVar(volts)])" : "41250",
"ChoicePoint Backtracking Stats" : "Distinct: 2 Total: 98999",
"VariableChoicePoint(DecimalVar(power))" : "49500",
"VariableChoicePoint(IntVar(amps))" : "49499"
```

Optimally, execution time for a constraint model is less than 100 milliseconds, with fewer
than 1,000 backtracks and no violations. Values for the constraint model example are
significantly higher, indicating that the constraint engine is performing inefficiently. To
improve performance in this example, reduce the domain of the power variable without
reducing the solution space. For example, define the domain as `[110..500]` instead of `[0..500]`. This change
reduces the number of backtracks the constraint engine performs to find a solution.
