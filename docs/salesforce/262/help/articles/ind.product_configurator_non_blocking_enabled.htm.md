---
article_id: ind.product_configurator_non_blocking_enabled.htm
title: Enable Non-Blocking Behavior in the Configurator
source_url: https://help.salesforce.com/s/articleView?id=ind.product_configurator_non_blocking_enabled.htm&type=5&release=262
release: 262
release_name: Summer '26
area: configurator
fetched_at: 2026-05-12
---

# Enable Non-Blocking Behavior in the Configurator

Enable non-blocking behavior so that configurator users can change multiple attribute and option values on a product asynchronously. The configuration page loads the changes without waiting for the constraint engine to process each setting individually. After processing is complete, the user can save the configuration.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions of Revenue Cloud with the Revenue Cloud Growth license or the Revenue Cloud Advanced license
USER PERMISSIONS NEEDED
To enable non-blocking behavior:	Product Configuration Constraints Designer permission set

When you turn on Non Blocking Enabled, if the configurator user selects values for attributes or options that violate rules on the constraint model, a warning message appears. For most rules, the constraint engine overrides the user selection that violates a rule, and replaces it with a valid value. For hide/disable rules, the value that the user selects overrides the constraint engine, even if the value violates the rule.

From Setup, in the Quick Find box, enter Flow, and then select Flows.
Open your product configurator flow.
Edit the screen element and select the Product Configurator Data Manager component.
To enable non-blocking behavior, for the Non Blocking Enabled attribute, select {!$GlobalConstant.True}.
If you’re using the default Configurator flow, continue to step 6. For a custom flow, repeat steps 3-4 to set the Non Blocking Enabled attribute for all the screen components.
When you've finished setting the attribute values, select Done.
To activate the changes, select Save as New Version, then select Activate.
