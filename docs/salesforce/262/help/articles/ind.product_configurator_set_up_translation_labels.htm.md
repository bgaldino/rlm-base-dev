---
article_id: ind.product_configurator_set_up_translation_labels.htm
title: Set Up Custom Labels for Run-Time Message Translation
source_url: https://help.salesforce.com/s/articleView?id=ind.product_configurator_set_up_translation_labels.htm&type=5&release=262
release: 262
release_name: Summer '26
area: configurator
fetched_at: 2026-05-12
---

# Set Up Custom Labels for Run-Time Message Translation

Enable translations for run-time messages defined in your constraint model by creating unique, translatable custom labels for the messages. The labels you set up replace the original static message text in the CML to facilitate translation. During run time, the messages appear in different languages, based on the sales reps’ locale and the translation settings of their Salesforce org. With this support, sales reps can see important configuration information in their local languages, which accelerates troubleshooting and improves usability.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions of Revenue Cloud with the Revenue Cloud Growth license or the Revenue Cloud Advanced license
USER PERMISSIONS NEEDED
To create or edit a constraint model:	Product Configuration Constraints Designer permission set
To create and manage custom labels:	Customize Application

Before creating custom labels:

Enable translations in your org by enabling Translation Workbench and adding the languages for which you want to support translations.
Save your constraint model with the messages you want to translate. The Add Labels button is enabled only after you save your model. All the run-time messages defined in your saved constraint model are extracted and listed for custom label definition.
From the App Launcher, find and select Constraint Models.
From the constraint models list view page, click the model you want to add custom labels for.
In the constraint model details page, select the version of the model you want to open.
On the Constraint Builder, click Add Labels.
In the Add Translation Labels for Messages window, specify a unique custom label for each message that you want to translate.
Messages that don’t have a custom label associated with them aren’t translated to the user’s chosen language during run time.
Custom labels must start with a letter and contain only alphanumeric characters and underscores. Labels are case-insensitive.

The custom labels that you assign to the messages replace the message text in your CML code. Manage all future changes to these labels from the Custom Labels page in Setup. See Custom Labels.

Reuse Existing Custom Labels

If you have existing custom labels that you want to reuse in your constraint model, add the label reference by using the type-ahead functionality or by providing the full label syntax in the CML Editor or Visual Builder.

In the Visual Builder, search for and select the custom label from the Run-time Message field on the constraint components.
In the CML Editor, use the $Label.labelName syntax to reference a custom label in your CML code.
