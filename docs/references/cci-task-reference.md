# CumulusCI Task Reference

This document reformats `cci task run --help` into grouped Markdown tables by task category.

## Usage

```bash
cci task run <task_name> [TASK_OPTIONS...]
cci task info <task_name>
```

## Quick Jump

- [Metadata Transformations](#metadata-transformations)
- [Salesforce Users](#salesforce-users)
- [Salesforce](#salesforce)
- [Salesforce Preflight Checks](#salesforce-preflight-checks)
- [Other](#other)
- [Utilities](#utilities)
- [Data Operations](#data-operations)
- [Salesforce Communities](#salesforce-communities)
- [Setup](#setup)
- [Salesforce Packages](#salesforce-packages)
- [Salesforce Metadata](#salesforce-metadata)
- [Marketing Cloud](#marketing-cloud)
- [OmniStudio](#omnistudio)
- [Revenue Lifecycle Management](#revenue-lifecycle-management)
- [Salesforce DX](#salesforce-dx)
- [GitHub](#github)
- [Release Operations](#release-operations)
- [Push Upgrades](#push-upgrades)
- [Salesforce Bulk API](#salesforce-bulk-api)
- [Robot Framework](#robot-framework)
- [Sample Data](#sample-data)
- [NPSP/EDA](#npspeda)
- [E2E Testing](#e2e-testing)
- [UX Personalization](#ux-personalization)
- [Partner Relationship Management](#partner-relationship-management)
- [Data Maintenance](#data-maintenance)
- [Data Management - Extract](#data-management---extract)
- [Data Management - Idempotency](#data-management---idempotency)
---

## Metadata Transformations

| Task | Description |
|---|---|
| `activate_flow` | Activates Flows identified by a given list of Developer Names |
| `add_fields_to_field_set` | Adds specified fields to a given field set. |
| `add_page_layout_fields` | Adds specified Fields or Visualforce Pages to a Page Layout. |
| `add_page_layout_related_lists` | Adds specified Related List to one or more Page Layouts. |
| `add_permission_set_perms` | Adds specified Apex class access and Field-Level Security to a Permission Set. |
| `add_picklist_entries` | Adds specified picklist entries to a custom picklist field. |
| `add_profile_ip_ranges` | Adds (or optionally replaces) IP Login Ranges to the specified Profiles. |
| `add_record_action_list_item` | Adds the specified 'Record' context Lightning button/action to the provided page layout. |
| `add_remote_site_settings` | Adds the specified RemoteSiteSettings records to an org. |
| `add_standard_value_set_entries` | Adds specified picklist entries to a Standard Value Set. |
| `assign_compact_layout` | Assigns the Compact Layout specified in the 'value' option to the Custom Objects in 'api_names' option. |
| `create_permission_set` | Creates a Permission Set with specified User Permissions and assigns it to the running user. |
| `deactivate_flow` | deactivates Flows identified by a given list of Developer Names |
| `set_duplicate_rule_status` | Sets the active status of Duplicate Rules. |
| `set_field_help_text` | Sets specified fields' Help Text values. |
| `set_object_settings` | Enable and disable object level settings on standard and custom objects |
| `set_organization_wide_defaults` | Sets the Organization-Wide Defaults for specific sObjects, and waits for sharing recalculation to complete. |
| `update_metadata_first_child_text` | Updates the text of the first child of Metadata with matching tag.  Adds a child for tag if it does not exist. |

---

## Salesforce Users

| Task | Description |
|---|---|
| `assign_permission_set_groups` | Assigns specified Permission Set Groups to the current user, if not already assigned. |
| `assign_permission_set_licenses` | Assigns specified Permission Set Licenses to the current user, if not already assigned. |
| `assign_permission_sets` | Assigns specified Permission Sets to the current user, if not already assigned. |
| `upload_user_profile_photo` | Uploads a profile photo for a specified or default User. |

---

## Salesforce

| Task | Description |
|---|---|
| `batch_apex_wait` | Waits on a batch apex or queueable apex job to finish. |
| `custom_settings_value_wait` | Waits for a specific field value on the specified custom settings object and field |
| `execute_anon` | Execute anonymous apex via the tooling api. |
| `run_tests` | Runs all apex tests |
| `unschedule_apex` | Unschedule all scheduled apex jobs (CronTriggers). |

---

## Salesforce Preflight Checks

| Task | Description |
|---|---|
| `check_advanced_currency_management` | Runs as a preflight check to determine whether Advanced Currency Management is active (True result means the feature is active). |
| `check_chatter_enabled` | Runs as a preflight check to validate Chatter is enabled. |
| `check_components` | Check if common components exist in the target org based on provided deploy paths or those from a plan/flow. |
| `check_dataset_load` | Runs as a preflight check to determine whether dataset can be loaded successfully. |
| `check_enhanced_notes_enabled` | Preflight check to validate that Enhanced Notes are enabled. |
| `check_my_domain_active` | Runs as a preflight check to determine whether My Domain is active. |
| `check_org_settings_value` | Runs as a preflight check to validate organization settings. |
| `check_org_wide_defaults` | Runs as a preflight check to validate Organization-Wide Defaults. |
| `check_sobject_permissions` | Runs as a preflight check to determine whether specific sObjects are permissioned as desired (options are required). |
| `check_sobjects_available` | Runs as a preflight check to determine whether specific sObjects are available. |
| `get_assignable_licenses` | Retrieves a list of the currently assignable license definition keys based on unused licenses |
| `get_assignable_permission_sets` | Retrieves a list of the currently assignable Permission Sets based on unused associated user licenses |
| `get_assigned_permission_set_licenses` | Retrieves a list of the developer names of any Permission Set Licenses assigned to the running user. |
| `get_assigned_permission_sets` | Retrieves a list of the developer names of any permission sets assigned to the running user. |
| `get_available_licenses` | Retrieves a list of the currently available license definition keys |
| `get_available_permission_set_licenses` | Retrieves a list of the currently available Permission Set License definition keys |
| `get_available_permission_sets` | Retrieves a list of the currently available Permission Sets |
| `get_existing_record_types` | Retrieves all Record Types in the org as a dict, with sObject names as keys and lists of Developer Names as values. |
| `get_existing_sites` | Retrieves a list of any existing Experience Cloud site names in the org. |
| `get_installed_packages` | Retrieves a list of the currently installed managed package namespaces and their versions |

---

## Other

| Task | Description |
|---|---|
| `create_partner_central` | Create Partner Central Community |
| `create_payments_webhook` | Create Salesforce Payments Webhook |
| `deploy_docgen_odt_seed` | Seed-insert minimal OmniDataTransform shell records (RLMQuoteExtractBasic, RLMQuoteTransformBasic, RLMQuoteProposalExtract, RLMQuoteProposalTransform) before the full DocGen deploy. Salesforce rejects INSERT of ODTs that reference custom formula fields in inputFieldName (-692085439) but accepts UPDATE of existing records. This step creates the ODT stubs so the subsequent deploy_post_docgen runs as an UPDATE. |
| `deploy_docgen_qli_fields` | Deploy RLM_ProductName__c formula field on QuoteLineItem before the main DocGen metadata deploy. The OmniDataTransform records reference this field in inputFieldName; Salesforce validates field existence on INSERT (fresh org), so it must exist before the ODTs are deployed. QuoteLineItem has no object-meta.xml, so the whole directory is safe to deploy early. |
| `deploy_docgen_seller_fields` | Deploy RLM_Seller_*__c, RLM_Account_Name__c, and RLM_Sales_Rep_Name__c formula fields on Quote before the main DocGen metadata deploy. The OmniDataTransform records reference these custom fields by name; Salesforce validates field existence on INSERT (fresh org), so the fields must exist before the ODTs are deployed. Targets only the Quote fields subdirectory to avoid the Quote object-meta.xml action overrides, which reference flexipages not yet deployed at this stage. |
| `deploy_post_approvals` | Deploy Advanced Approvals metadata: Quote/QuoteLineItem fields, RLM_Payment_Terms GVS, PathAssistant, quickAction, flows (RLM_Quote_Smart_Approval, RLM_Quote_Approval_Data), Apex class, and permission set. EmailTemplatePage FlexiPages (including RLM_Quote_Record_Page) are excluded via .forceignore — EmailTemplatePage type cannot be deployed via Metadata API (platform restriction); Lightning Email Templates are created separately by create_approval_email_templates. |
| `deploy_post_billing` | Deploy Billing Metadata |
| `deploy_post_commerce` | Deploy Commerce Metadata (e.g. Commerce decision table flows) |
| `deploy_post_constraints` | Deploy Constraints Metadata |
| `deploy_post_docgen` | Deploy Document Generation Metadata |
| `deploy_post_guidedselling` | Deploy Guided Selling Metadata |
| `deploy_post_payments` | Deploy Payments Metadata |
| `deploy_post_payments_settings` | Deploy Payments Settings |
| `deploy_post_payments_site` | Deploy Payments site settings only |
| `deploy_post_prm` | Deploy Partner Relationship Management Metadata |
| `deploy_post_procedureplans` | Deploy Procedure Plans Metadata |
| `deploy_post_procedureplans_classes` | Deploy Procedure Plans Classes |
| `deploy_post_procedureplans_objects` | Deploy Procedure Plans Objects |
| `deploy_post_procedureplans_permission` | Deploy Procedure Plans |
| `sets` | Permissionsets |
| `deploy_post_tso` | Deploy Trialforce Source Org Metadata (App Launcher now deploys |
| `via` | prepare_ux/assemble_and_deploy_ux) |
| `deploy_post_utils` | Deploy Utils Metadata |
| `deploy_quantumbit` | Deploy QuantumBit Metadata |
| `deploy_sharing_rules` | Deploy Sharing Rules |
| `enable_analytics_replication` | Enable CRM Analytics replication via browser automation (Robot/Selenium, Analytics Settings VF iframe) |
| `ensure_pricing_schedules` | Ensure pricing schedules exist before expression sets |
| `generate_data_dictionary` | Create a data dictionary for the project in CSV format. |
| `retrieve_tasks` | Retrieves the tasks under the particular category or group |
| `retrieve_unpackaged` | Retrieve the contents of a package.xml file. |

---

## Utilities

| Task | Description |
|---|---|
| `command` | Run an arbitrary command |
| `log` | Log a line at the info level. |
| `util_sleep` | Sleeps for N seconds |

---

## Data Operations

| Task | Description |
|---|---|
| `composite_request` | Execute a series of REST API requests in a single call |
| `create_bulk_data_permission_set` | Creates a Permission Set with the Hard Delete and Set Audit Fields user permissions. NOTE: the org setting to allow Set Audit Fields must be turned on. |
| `delete_data` | Query existing data for a specific sObject and perform a Bulk API delete of all matching records. |
| `extract_dataset` | Extract a sample dataset using the bulk API. |
| `generate_and_load_from_yaml` |  |
| `generate_dataset_mapping` | Create a mapping for extracting data from an org. |
| `insert_record` | Inserts a record of any sObject using the REST API |
| `load_custom_settings` | Load Custom Settings specified in a YAML file to the target org |
| `load_dataset` | Load a SQL dataset using the bulk API. |
| `snowfakery` | Generate and load data from a Snowfakery |
| `recipe` |  |
| `update_data` | Update records of an sObject matching a where-clause. |

---

## Salesforce Communities

| Task | Description |
|---|---|
| `create_community` | Creates a Community in the target org using the Connect API |
| `create_network_member_groups` | Creates NetworkMemberGroup records which grant access to an Experience Site (Community) for specified Profiles or Permission Sets |
| `list_communities` | Lists Communities for the current org using the Connect API. |
| `list_community_templates` | Prints the Community Templates available to the current org |
| `publish_community` | Publishes a Community in the target org using the Connect API |

---

## Setup

| Task | Description |
|---|---|
| `connected_app` | Creates the Connected App needed to use persistent orgs in the CumulusCI keychain |

---

## Salesforce Packages

| Task | Description |
|---|---|
| `create_package` | Creates a package in the target org with the default package name for the project |
| `create_package_version` | Uploads a 2nd-generation package (2GP) version |
| `install_managed` | Install the latest managed production release |
| `install_managed_beta` | Installs the latest managed beta release |
| `uninstall_managed` | Uninstalls the managed version of the package |
| `update_dependencies` | Installs all dependencies in project__dependencies into the target org |

---

## Salesforce Metadata

| Task | Description |
|---|---|
| `create_blank_profile` | Creates a blank profile, or a profile with no permissions |
| `create_managed_src` | Modifies the src directory for managed deployment.  Strips //cumulusci-managed from all Apex |
| `code` |  |
| `create_unmanaged_ee_src` | Modifies the src directory for unmanaged deployment to an EE org |
| `deploy` | Deploys the src directory of the repository to the org |
| `deploy_post` | Deploys all metadata bundles under |
| `unpackaged/post/` |  |
| `deploy_qa_config` | Deploys configuration for QA. |
| `describe_metadatatypes` | Retrieves the metadata types supported by the org based on the api |
| `version` |  |
| `enable_einstein_prediction` | Enable an Einstein Prediction Builder prediction. |
| `ensure_record_types` | Ensure that a default Record Type is extant on the given standard sObject (custom objects are not supported). If Record Types are already present, do nothing. |
| `list_changes` | List the changes from a scratch org |
| `list_files` | Display documents that has been uploaded to a library in Salesforce CRM Content or Salesforce Files. |
| `list_metadata_types` | Prints the metadata types in a |
| `project` |  |
| `list_nonsource_trackable_components` | List the components of non source trackable Metadata types. |
| `list_nonsource_trackable_metadatatyp` | Returns non source trackable metadata |
| `es` | types supported by org |
| `meta_xml_apiversion` | Set the API version in ``*meta.xml`` |
| `files` |  |
| `meta_xml_dependencies` | Set the version for dependent |
| `packages` |  |
| `remove_metadata_xml_elements` | Remove specified XML elements from one or more metadata files |
| `retrieve_changes` | Retrieve changed components from a scratch org |
| `retrieve_files` | Retrieve documents that have been uploaded to a library in Salesforce CRM Content or Salesforce Files. |
| `retrieve_nonsource_trackable` | Retrieves the non source trackable components filtered |
| `retrieve_packaged` | Retrieves the packaged metadata from the org |
| `retrieve_profile` | Given a list of profiles, the task retrieves all complete profiles along with their associated dependencies for all permissionable entities - ApexClass, ApexPage, CustomApplications, CustomObjects, CustomPermissions, CustomTabs, ExternalDataSources and Flows |
| `retrieve_qa_config` | Retrieves the current changes in the scratch org into unpackaged/config/qa |
| `retrieve_src` | Retrieves the packaged metadata into the src directory |
| `revert_managed_src` | Reverts the changes from |
| `create_managed_src` |  |
| `revert_unmanaged_ee_src` | Reverts the changes from |
| `create_unmanaged_ee_src` |  |
| `snapshot_changes` | Tell SFDX source tracking to ignore previous changes in a scratch org |
| `strip_unwanted_components` | Removes components from src folder which are not mentioned in given package.xml file |
| `uninstall_packaged` | Uninstalls all deleteable metadata in the package in the target org |
| `uninstall_packaged_incremental` | Deletes any metadata from the package in the target org not in the local |
| `workspace` |  |
| `uninstall_post` | Uninstalls the unpackaged/post |
| `bundles` |  |
| `uninstall_pre` | Uninstalls the unpackaged/pre bundles |
| `uninstall_src` | Uninstalls all metadata in the local src directory |
| `update_admin_profile` | Retrieves, edits, and redeploys the Admin.profile with full FLS perms for all objects/fields |
| `update_package_xml` | Updates src/package.xml with metadata in src/ |
| `upload_files` | Upload documents (files) to a Salesforce org. |

---

## Marketing Cloud

| Task | Description |
|---|---|
| `deploy_marketing_cloud_package` | Deploys a package zip file to a Marketing Cloud Tenant via the Marketing Cloud Package Manager API. |
| `marketing_cloud_create_subscriber_att` | Creates a Subscriber Attribute via |
| `ribute` | the Marketing Cloud SOAP API. |
| `marketing_cloud_create_user` | Creates a new User via the Marketing Cloud SOAP API. |
| `marketing_cloud_get_user_info` | Return user info retrieved from the /userinfo endpoint of the Marketing Cloud REST API. |
| `marketing_cloud_update_user_role` | Assigns a Role to an existing User via the Marketing Cloud SOAP API. |

---

## OmniStudio

| Task | Description |
|---|---|
| `deploy_omni_studio_site_settings` | Deploys remote site settings needed for OmniStudio. |
| `vlocity_pack_deploy` | Executes the `vlocity packDeploy` command against an org |
| `vlocity_pack_export` | Executes the `vlocity packExport` command against an org |

---

## Revenue Lifecycle Management

| Task | Description |
|---|---|
| `activate_and_deploy_expression_sets` | Activate and Deploy Expression Sets |
| `activate_billing_records` | Activate Billing Records |
| `activate_decision_tables` | Activate selected Decision Tables via API |
| `activate_default_payment_term` | Activate Default Payment Term |
| `activate_docgen_templates` | Activate the latest version of each RLM_ OmniStudio DocumentTemplate. DocumentTemplates always deploy as inactive; this script finds the highest version per template name and sets IsActive = true. |
| `activate_expression_sets` | Activate expression set versions via Tooling API |
| `activate_price_adjustment_schedules` | Activate Price Adjustment Schedules |
| `activate_procedure_plan_expression_se` | Activate Procedure Plan expression |
| `ts` | set versions (RLM_Price_Distribution_Procedure; RLM_DefaultPricingProcedure is activated by the main activate_expression_sets task) |
| `activate_procedure_plan_version` | Activate the ProcedurePlanDefinitionVersion after sections and options have been |
| `inserted` |  |
| `activate_rates` | Activate Rates |
| `activate_rating_records` | Activate Rating Records |
| `activate_tax_records` | Activate Tax Records |
| `apply_context_constraint_engine_node_` | Apply ConstraintEngineNodeStatus |
| `status` | mappings to Sales Transaction |
| `context` |  |
| `apply_context_docgen` | Creates and configures the RLM_QuoteDocGenContext context definition for Context Service document templates. Defines Quote node (AccountName, BillingStreet/City/State/PostalCode, SalesRep, QuoteNumber, CreatedDate, ExpirationDate, GrandTotal) and Line child node (ProductName, Quantity, ListPrice, Discount, NetUnitPrice, NetTotalPrice) mapped via QuoteDocGenMapping to Quote and QuoteLineItem SObjects. |
| `apply_context_ramp_mode` | Adds RampMode__c (SalesTransactionItem) and GroupRampMode__c (SalesTransactionGroup) context attributes to the Sales Transaction context definition and maps them to QuoteLineItem.RLM_RampMode__c and QuoteLineGroup.RLM_RampMode__c (QuoteEntitiesMapping) and OrderItem.RLM_RampMode__c and OrderItemGroup.RLM_RampMode__c (OrderEntitiesMapping). |
| `assign_permission_set_groups_tolerant` | Assign Permission Set Groups with tolerance for permission warnings |
| `cleanup_settings_for_dev` | Clean up settings files before deployment (removes fields unsupported in the target org) |
| `configure_revenue_settings` | Configure Revenue Settings page defaults: Pricing Procedure, Usage Rating, Instant Pricing toggle, Create Orders from Quote flow, and optionally Manage Assets flow (Robot test). Must run after all data/metadata is deployed and before decision table refresh. |
| `create_approval_email_templates` | Create Lightning Email Templates for RLM Approval notifications from the dataset CSV. Reads EmailTemplate.csv |
| `from` | datasets/sfdmu/qb/en-US/qb-approvals / and creates SFX-type (Lightning) EmailTemplate records in the target org, then links them to ApprovalAlertContentDef records. Idempotent: skips templates that already exist. Required before insert_qb_approvals_data. EmailTemplatePage FlexiPages cannot be deployed via Metadata API (platform restriction). |
| `create_billing_portal` | Create Self-Service Billing Portal community (Experience Cloud site). |
| `create_docgen_library` | Create DocGen Library |
| `create_dro_rule_library` | Create DRO Rule Library |
| `create_procedure_plan_definition` | Create Procedure Plan Definition via Connect API (idempotent) |
| `create_rule_library` | Create Rule Library |
| `create_tax_engine` | Create Tax Engine |
| `deactivate_decision_tables` | Deactivate Decision Tables (required before updating active decision tables) |
| `deactivate_expression_sets` | Deactivate expression set versions via Tooling API |
| `deploy_agents` | Deploy Agentforce Agent Configurations |
| `deploy_agents_bots` | Deploy Agentforce Agent Bots |
| `deploy_agents_flows` | Deploy Agentforce Agent Flows deploy_agents_genAiFunctions            Deploy Agentforce Agent Functions deploy_agents_genAiPlanners             Deploy Agentforce Agent Planner Bundles deploy_agents_genAiPlugins              Deploy Agentforce Agent Plugins |
| `deploy_agents_permissionsets` | Deploy Agentforce Agent Permissionsets |
| `deploy_agents_settings` | Deploy Agentforce Agent Settings |
| `deploy_billing_id_settings` | Deploy Billing Settings with org-specific record IDs (resolved via XPath transform queries at deploy time) |
| `deploy_billing_template_settings` | Re-enable Invoice Email/PDF toggles to trigger default template auto-creation (cycle step 3) |
| `deploy_context_definitions` | Deploy Context Definitions |
| `deploy_decision_tables` | Deploy Decision Tables |
| `deploy_expression_sets` | Deploy Expression Sets |
| `deploy_full` | Deploy all metadata |
| `deploy_org_settings` | Deploy Org Settings |
| `deploy_permissions` | Deploy Permission Set Groups |
| `deploy_post_billing_portal` | Deploy Billing Portal site metadata (experiences, themes, etc.) from unpackaged/post_billing_portal. Run when billing_portal_deploy is true after create_billing_portal. |
| `deploy_post_billing_ui` | Deploy Billing UI metadata from unpackaged/post_billing_ui: 17 LWC components (rlmBillingCaseMetrics, rlmBillingScheduleGroupHierarchy, rlmBillingStatus, rlmBsgConsolidatedTimeline, rlmBsgSchedulesTimeline, rlmCollectionRuleBuilder, rlmCollectionsDashboard, rlmDisputeDetails, rlmInvoiceAging, rlmInvoiceAgingChart, rlmInvoiceHealth, rlmInvoiceProductSummary, rlmInvoiceTaxSummary, rlmInvoiceTransactionJournals, rlmPaymentsData, rlmSplitInvoicesCards, rlmSplitInvoicesView), 11 Apex controllers, 1 flow (RLM_Generate_Statement_of_Account), 2 Order custom fields (RLM_Billing_Arrangement__c, RLM_Billing_Profile__c), 2 InvoiceLine custom fields (RLM_Charge_Type__c formula, RLM_Attributes__c rich text), 2 quick actions (Account.RLM_Generate_Account_Statem ent, Invoice.RLM_Payment_Link), the RLM_InvoiceCardLogo static resource, and the RLM_BillingUI permission set (field access + Apex class access + RunFlow). Flexipages for billing_ui are deployed via assemble_and_deploy_ux (billing_ui feature flag). |
| `deploy_post_collections` | Deploy Collections metadata from unpackaged/post_collections (flows, objects, omniUiCard, permissionsets, queues, quickActions, tabs, timelineObjectDefinitions). Flexipages and applications for collections are deployed via assemble_and_deploy_ux (prepare_ux flow) — they are excluded here via .forceignore. |
| `deploy_post_personas` | Deploy persona metadata (profiles, permission set groups, permission sets) from unpackaged/post_personas. |
| `deploy_post_ramp_builder` | Deploy all Ramp Schedule Builder (Create Ramp Schedule V4) metadata under unpackaged/post_ramp_builder: RLM_RampMode__c (Picklist) on QuoteLineGroup, QuoteLineItem, OrderItemGroup, and OrderItem; RLM_UpliftPercent__c (Percent) on QuoteLineGroup only; Lightning Message Channel (RLM_RampScheduleChannel); Apex classes and test classes (RLM_RampScheduleFlowAction, RLM_RampScheduleService, RLM_RampScheduleValidator, RLM_RampScheduleRequest, RLM_RampScheduleResponse, RLM_RampScheduleFlowException, RLM_RampMigrationQueueable, RLM_RampScheduleStatusController, RLM_QuoteLineItemDiscountUpliftHandl er, RLM_QuoteLineItemRampModeHandler, RLM_QuoteLineItemRampHandler, and test classes); RLM_QuoteLineItemRampTrigger trigger; six LWC bundles (rlmRampScheduleFlowModalAction, rlmRampScheduleForm, rlmRampScheduleTrialSection, rlmRampSchedulePreviewTable, rlmRampScheduleStatus, rlmRampRefreshPage); the RLM_Create_Ramp_Schedule_V4 screen flow; the Quote.RLM_Create_Ramp_Schedule_V4 quick action; and the RLM_RampSchedule permission set (grants FLS on all custom fields and class access for all production Apex classes). |
| `deploy_pre` | Deploy Pre-deployment Metadata |
| `enable_constraints_settings` | Set Default Transaction Type, Asset Context for Product Configurator, and enable Constraints Engine toggle on Revenue Settings (Robot test). Required before CML constraint data import. |
| `enable_document_builder_toggle` | Enable the Document Builder toggle on Revenue Settings (Robot test with sf org open). Run before deploy_post_docgen when the org does not have Document Builder enabled via metadata. |
| `enable_timeline` | Enable the Timeline feature toggle at Setup → Feature Settings → Timeline (Robot/Selenium). Required before billing_ui flexipages that reference industries_common:timeline can be deployed. Once enabled, this toggle cannot be disabled. |
| `exclude_active_decision_tables` | Exclude active decision tables from deployment (TODO: implement proper deactivation) |
| `export_cml` | Export constraint model data (ESDV, ESC, reference objects, blob) from org to local directory |
| `extend_context_asset` | Extend Standard Asset Context |
| `extend_context_billing` | Extend Standard Billing Context |
| `extend_context_cart` | Extend Standard Cart Context |
| `extend_context_collection_plan_segmen` | Extend Standard Collection Plan |
| `t` | Segment Context Definition |
| `extend_context_contracts` | Extend Standard Contracts Context Definition |
| `extend_context_contracts_extraction` | Extend Standard Contracts Extraction Context Definition |
| `extend_context_fulfillment_asset` | Extend Standard Fulfillment Asset Context Definition |
| `extend_context_product_discovery` | Extend Standard Product Discovery Context |
| `extend_context_rate_management` | Extend Standard Rate Management Context Definition |
| `extend_context_rating_discovery` | Extend Standard Rating Discovery Context Definition |
| `extend_context_sales_transaction` | Extend Standard Sales Transaction Context |
| `extend_standard_context` | Extend a standard context definition and optionally apply a plan |
| `fix_document_template_binaries` | Corrects DocumentTemplate ContentDocument binaries after a batch metadata deploy. Salesforce metadata API bug: all DocumentTemplates deployed in a single batch receive the same ContentDocument binary (first alphabetically). This task uploads the correct .dt binary from the repo for each RLM_ template, replacing the wrong ContentDocument content. Run after deploy_post_docgen + activate_docgen_templates. |
| `import_cml` | Import constraint model metadata, ESC associations, and ConstraintModel blob into org |
| `insert_billing_data` | Insert QuantumBit Billing Data |
| `insert_clm_data` | Insert CLM Data |
| `insert_clm_data_prod` | Insert CLM Data to Production |
| `insert_procedure_plan_data` | Insert Procedure Plan data (sections in pass 1, options with expression set links in pass 2) |
| `insert_q3_billing_data` | Insert Q3 Billing Data |
| `insert_q3_data` | Insert Q3 Data |
| `insert_q3_dro_data_prod` | Insert Q3 DRO Data to Production |
| `insert_q3_dro_data_scratch` | Insert Q3 DRO Data to Scratch |
| `insert_q3_rates_data` | Insert Q3 Rates Data |
| `insert_q3_rating_data` | Insert Q3 Rating Data |
| `insert_q3_tax_data` | Insert Q3 Tax Data |
| `insert_qb_approvals_data` | Insert QuantumBit Approvals data via SFDMU (EmailTemplate, Group/User Readonly, GroupMember for CEO users in Manager/Director/VP groups, ApprovalAlertContentDef). Runtime materialization of User/GroupMember CSVs from the target org. Requires post_approvals metadata and create_approval_email_templates first. EmailTemplatePage FlexiPages excluded from deploy (platform restriction). |
| `insert_qb_constraints_component_data` | Insert QuantumBit Constraints Product Related Component Data |
| `insert_qb_constraints_product_data` | Insert QuantumBit Constraints Product Data |
| `insert_qb_dro_data` | Insert QuantumBit DRO Data (scratch and prod; AssignedTo resolved from target org) |
| `insert_qb_guidedselling_data` | Insert QuantumBit Guided Selling Data |
| `insert_qb_rates_data` | Insert QuantumBit Rates Data |
| `insert_qb_rating_data` | Insert QuantumBit Rating Data |
| `insert_qb_transactionprocessingtypes_` | Insert QuantumBit Transaction |
| `data` | Processing Types Data |
| `insert_quantumbit_pcm_data` | Insert QuantumBit Data |
| `insert_quantumbit_pricing_data` | Insert QuantumBit Data |
| `insert_quantumbit_prm_data` | Insert QuantumBit PRM data using a 2-pass SFDMU plan. Pass 1 upserts partner Accounts, ChannelProgram, and ChannelProgramLevel. Pass 2 enables IsPartner on Accounts (not createable, only updateable) and upserts ChannelProgramMember linking partners to program levels. |
| `insert_quantumbit_product_image_data` | Insert QuantumBit Product Image Data |
| `insert_scratch_data` | Insert Scratch Data |
| `insert_tax_data` | Insert QuantumBit Tax Data |
| `load_sfdmu_data` | Load SFDMU Data |
| `manage_context_definition` | Modify context definitions via Context Service (connect) endpoints |
| `manage_decision_tables` | Decision Table management: list (with UsageType), query, refresh, activate, deactivate, validate_lists (compare org to project list anchors) |
| `manage_expression_sets` | Comprehensive Expression Set management (list, query, manage versions) |
| `manage_flows` | Comprehensive Flow management (list, query, activate, deactivate) |
| `manage_transaction_processing_types` | Manage TransactionProcessingType entries via Tooling API |
| `patch_payments_site_for_deploy` | Patch Payments_Webhook.site-meta.xml with the org's actual admin username before deploy. Required because siteAdmin and siteGuestRecordDefaultOwner are immutable after site creation and the committed XML contains a placeholder username. |
| `post_process_extraction` | Post-process extracted CSVs into import-ready format |
| `query_billing_state` | Query billing record state (PaymentTerm, BillingTreatment, BillingPolicy, BillingTreatmentItem) for validation; check debug logs for output. |
| `recalculate_permission_set_groups` | Recalculate permission set groups and wait for Updated status |
| `reconfigure_pricing_discovery` | Reconfigure the autoproc Salesforce_Default_Pricing_Discovery _Procedure expression set: fix context definition, set rank and start date, and reactivate. When the autoproc expression set does not exist (e.g. tso=true orgs), activates the fallback RLM_DefaultPricingDiscoveryProcedure instead. Required before decision table refresh. |
| `refresh_dt_asset` | Refresh Asset Decision Tables |
| `refresh_dt_commerce` | Refresh Commerce Decision Tables (when commerce flag is true) |
| `refresh_dt_default_pricing` | Refresh Default Pricing Decision Tables |
| `refresh_dt_pricing_discovery` | Refresh Pricing Discovery Decision Tables |
| `refresh_dt_rating` | Refresh Rating Decision Tables |
| `refresh_dt_rating_discovery` | Refresh Rating Discovery Decision Tables |
| `restore_decision_tables` | Restore skipped decision tables after deploy |
| `revert_payments_site_after_deploy` | Restore the placeholder siteAdmin and siteGuestRecordDefaultOwner in Payments_Webhook.site-meta.xml after deploy_post_payments_site so the repo never stores the target org's real username. Run AFTER deploy_post_payments_site. |
| `stamp_git_commit` | Stamps the current git commit hash, branch, timestamp, org definition, dirty-tree flag, and active feature flags into the org as a Custom Metadata Type record (RLM_Build_Info__mdt.Latest). Non-fatal: deploy failures are logged as warnings so this task never breaks a completed flow. |
| `sync_pricing_data` | Sync Pricing Data |
| `update_product_fulfillment_decomp_rul` | Update ProductFulfillmentDecompRule |
| `es` | after DRO load. TEMPORARY FIX (260 bug) ExecuteOnRuleId not created on INSERT; re-save triggers ruleset generation. See scripts/apex/updateProductFulfillmen tDecompRules.apex. |
| `validate_billing_structure` | Validate that every BillingTreatment has BillingPolicyId set. Run after data load to verify structure before activation. |
| `validate_cml` | Validate CML file structure, annotations, and ESC association |
| `coverage` |  |
| `validate_setup` | Validate the local developer setup for rlm-base-dev. Checks Python, CumulusCI, Salesforce CLI, SFDMU plugin version (v5+ required), Node.js, Robot Framework, SeleniumLibrary, webdriver-manager, Chrome/Chromium, ChromeDriver, and urllib3. When auto_fix=true the SFDMU plugin is automatically installed or updated to the required version. Run without an org: cci task run validate_setup |

---

## Salesforce DX

| Task | Description |
|---|---|
| `dx` | Execute an arbitrary Salesforce DX command against an org. Use the 'command' option to specify the command, such as 'package install' |
| `dx_convert_from` | Converts force-app directory in sfdx format into metadata format under src |
| `dx_convert_to` | Converts src directory metadata format into sfdx format under force-app |
| `org_settings` | Apply org settings from a scratch org definition file or |
| `dict` |  |

---

## GitHub

| Task | Description |
|---|---|
| `gather_release_notes` | Generates release notes by getting the latest release of each repository |
| `github_automerge_feature` | Merges the latest commit on a source branch to all child branches. |
| `github_automerge_main` | Merges the latest commit on the main branch into all open feature branches |
| `github_clone_tag` | Clones a github tag under a new name. |
| `github_copy_subtree` | Copies one or more subtrees from the project repository for a given release to a target repository, with the option to include release notes. |
| `github_package_data` | Look up 2gp package dependencies for a version id recorded in a commit status. |
| `github_parent_pr_notes` | Merges the description of a child pull request to the respective parent's pull request (if one exists). |
| `github_pull_requests` | Lists open pull requests in project Github |
| `repository` |  |
| `github_release` | Creates a Github release for a given managed package version number |
| `github_release_notes` | Generates release notes by parsing pull request bodies of merged pull requests between two tags |
| `github_release_report` | Parses GitHub release notes to report various |
| `info` |  |

---

## Release Operations

| Task | Description |
|---|---|
| `metadeploy_publish` | Publish a release to the MetaDeploy web installer |
| `promote_package_version` | Promote a 2gp package so that it can be installed in a production org |
| `upload_beta` | Uploads a beta release of the metadata currently in the packaging org |
| `upload_production` | Uploads a production release of the metadata currently in the packaging org |

---

## Push Upgrades

| Task | Description |
|---|---|
| `push_all` | Schedules a push upgrade of a package version to all |
| `subscribers` |  |
| `push_failure_report` | Produce a CSV report of the failed and otherwise anomalous push jobs. |
| `push_list` | Schedules a push upgrade of a package version to all orgs listed in the specified file |
| `push_qa` | Schedules a push upgrade of a package version to all orgs listed in push/orgs_qa.txt |
| `push_sandbox` | Schedules a push upgrade of a package version to sandbox orgs |
| `push_trial` | Schedules a push upgrade of a package version to Trialforce Template orgs listed in push/orgs_trial.txt |

---

## Salesforce Bulk API

| Task | Description |
|---|---|
| `query` | Queries the connected org |

---

## Robot Framework

| Task | Description |
|---|---|
| `robot` | Runs a Robot Framework test from a .robot file |
| `robot_libdoc` | Generates documentation for project keyword files |
| `robot_testdoc` | Generates html documentation of your Robot test suite and writes to tests/test_suite. |

---

## Sample Data

| Task | Description |
|---|---|
| `capture_sample_data` | Load a saved sample dataset (experimental) |
| `load_sample_data` | Load a saved sample dataset  (experimental) |

---

## NPSP/EDA

| Task | Description |
|---|---|
| `disable_tdtm_trigger_handlers` | Disable specified TDTM trigger handlers |
| `restore_tdtm_trigger_handlers` | Restore status of TDTM trigger handlers |

---

## E2E Testing

| Task | Description |
|---|---|
| `robot_e2e` | Run the full Quote-to-Order UI test (headless Chrome). Validates the complete sales workflow: Reset Account → Create Opportunity → Create Quote → Browse Catalogs → Add Products → Create Order → Activate Order → Verify Assets. Requires a provisioned org with qb=true (run prepare_rlm_org first). |
| `robot_e2e_debug` | Run the full Quote-to-Order UI test in headed Chrome with CDP debugging on port 9222. Same flow as robot_e2e but visible browser for development and debugging. Connect via chrome://inspect. Use -o pause_for_recording true to add pause points for DOM inspection. |
| `robot_order_from_quote` | Add products via Browse Catalogs, create and activate an Order, and verify Assets (UI automation, headed Chrome). Part 2 of the modular Quote-to-Order flow. If no QUOTE_ID is provided, creates a fresh Quote automatically. |
| `robot_reset_account` | Reset the test Account via the RLM_Reset_Account QuickAction (UI automation). Clears transactional data (Opportunities, Quotes, Orders, Assets) so E2E tests can re-run from a clean state. Runs in headed Chrome. |
| `robot_setup_quote` | Reset Account and create an Opportunity + Quote (UI automation, headed Chrome). Part 1 of the modular Quote-to-Order flow. Can be run standalone to prepare a Quote for other tests. |

---

## UX Personalization

| Task | Description |
|---|---|
| `assemble_and_deploy_ux` | Assembles feature-conditional UX metadata (flexipages, layouts, applications, app menus, profiles) from base templates and YAML patch files in templates/. Writes assembled SFDX-format output to unpackaged/post_ux/ (git-tracked) and deploys in a single sf project deploy start call. Supports granular invocation via metadata_type and metadata_name options for development and debugging. |
| `reorder_app_launcher` | Applies a priority order to the App Launcher. The Python task queries all AppMenuItem records via the Salesforce REST API (SOQL), builds a priority-ordered ApplicationId list (priority_app_labels first, remaining apps after in their current relative order), and passes the list to a Robot Framework test. The Robot test navigates to the Lightning home page and calls Aura AppLauncherController/saveOrder via synchronous XHR — no modal or DOM scraping required. Required on Trialforce-based orgs where the Metadata API cannot deploy an AppSwitcher containing managed ConnectedApp or Network entries and AppMenuItem.SortOrder is platform read-only via all other APIs. |

---

## Partner Relationship Management

| Task | Description |
|---|---|
| `deploy_post_prm_tso` | Deploy TSO-only PRM experience overlay containing the View Vouchers page (requires Referral and Voucher objects enabled in TSO orgs). |
| `patch_network_email_for_deploy` | Replace the placeholder emailSenderAddress in rlm.network-meta.xml with the Network's actual current EmailSenderAddress (immutable after creation) so deploy_post_prm succeeds. Repo stores a non-PII placeholder; run revert_network_email_after_deploy after deploy. |
| `revert_network_email_after_deploy` | Restore the placeholder emailSenderAddress in rlm.network-meta.xml after deploy_post_prm so the repo never persists the target org's email. |

---

## Data Maintenance

| Task | Description |
|---|---|
| `delete_draft_billing_records` | Delete all draft billing-related records (BillingTreatmentItem, BillingTreatment, BillingPolicy, PaymentTermItem, PaymentTerm) in dependency order. Use before re-running the billing data plan to avoid duplicates. |
| `delete_qb_rates_data` | Delete all qb-rates data (RateAdjustmentByTier, RateCardEntry, PriceBookRateCard, RateCard) in dependency order. Use before re-running insert_qb_rates_data or test_qb_rates_idempotency to clear duplicates. |
| `delete_qb_rating_data` | Delete all qb-rating data (PUG, PURP, PUR, RatingFrequencyPolicy, UsageGrantRolloverPolicy, etc.) in dependency order. Use before re-running insert_qb_rating_data to clear duplicates. |
| `delete_quantumbit_pricing_data` | Delete all Insert-operation records from the qb-pricing plan (PricebookEntryDerivedPrice, PricebookEntry, BundleBasedAdjustment, AttributeBasedAdjustment, AttributeAdjustmentCondition, PriceAdjustmentTier) in reverse plan order (children first). Shape-agnostic: clears all records of each type regardless of which data shape populated them. Run before insert_quantumbit_pricing_data when layering multiple pricing shapes. Note: CostBookEntry is currently excluded (empty CSV) and will not be deleted. |

---

## Data Management - Extract

| Task | Description |
|---|---|
| `extract_qb_approvals_data` | Extract qb-approvals (EmailTemplate, Group, User, GroupMember, ApprovalAlertContentDef) from org to CSV. Output in datasets/sfdmu/extractions/qb-approvals/<timestamp>. Runs post-process by default; re-import-ready CSVs in <timestamp>/processed/. Use run_post_process false to skip. |
| `extract_qb_billing_data` | Extract qb-billing (billing policies, treatments, payment terms) from org to CSV. Output in |
| `datasets/sfdmu/extractions/qb-billing` | /<timestamp>. Runs post-process by default; re-import-ready CSVs in <timestamp>/processed/. Use run_post_process false to skip. |
| `extract_qb_clm_data` | Extract qb-clm from org to CSV. Output in datasets/sfdmu/extractions/qb-clm/<ti mestamp>. Runs post-process by default; re-import-ready CSVs in <timestamp>/processed/. Use run_post_process false to skip. |
| `extract_qb_dro_data` | Extract qb-dro from org to CSV. Output in datasets/sfdmu/extractions/qb-dro/<ti mestamp>. Runs post-process by default; re-import-ready CSVs in <timestamp>/processed/. Use run_post_process false to skip. |
| `extract_qb_guidedselling_data` | Extract qb-guidedselling from org to CSV. Output in |
| `datasets/sfdmu/extractions/qb-guideds` | elling/<timestamp>. Runs post-process by default; re-import-ready CSVs in <timestamp>/processed/. Use run_post_process false to skip. |
| `extract_qb_pcm_data` | Extract qb-pcm (product catalog) from org to CSV. Output in datasets/sfdmu/extractions/qb-pcm/<ti mestamp>. Runs post-process by default; re-import-ready CSVs in <timestamp>/processed/. Use run_post_process false to skip. |
| `extract_qb_pricing_data` | Extract qb-pricing from org to CSV. Output in |
| `datasets/sfdmu/extractions/qb-pricing` | /<timestamp>. Runs post-process by default; re-import-ready CSVs in <timestamp>/processed/. Use run_post_process false to skip. |
| `extract_qb_prm_data` | Extract qb-prm (partner relationship management) from org to CSV. Output |
| `in` | datasets/sfdmu/extractions/qb-prm/<ti mestamp>. Runs post-process by default; re-import-ready CSVs in <timestamp>/processed/. Use run_post_process false to skip. |
| `extract_qb_product_images_data` | Extract qb-product-images from org to CSV. Output in |
| `datasets/sfdmu/extractions/qb-product` | -images/<timestamp>. Runs post-process by default; re-import-ready CSVs in <timestamp>/processed/. Use run_post_process false to skip. |
| `extract_qb_rates_data` | Extract qb-rates from org to CSV. Output in datasets/sfdmu/extractions/qb-rates/< timestamp>. Runs post-process by default; re-import-ready CSVs in <timestamp>/processed/. Use run_post_process false to skip. |
| `extract_qb_rating_data` | Extract qb-rating from org to CSV. Output in |
| `datasets/sfdmu/extractions/qb-rating/` | <timestamp>. Runs post-process by default; re-import-ready CSVs in <timestamp>/processed/. Use run_post_process false to skip. |
| `extract_qb_tax_data` | Extract qb-tax (tax policies and treatments) from org to CSV. Output |
| `in` | datasets/sfdmu/extractions/qb-tax/<ti mestamp>. Runs post-process by default; re-import-ready CSVs in <timestamp>/processed/. Use run_post_process false to skip. |
| `extract_qb_transactionprocessingtype` | Extract qb-transactionprocessingtypes |
| `s_data` | from org to CSV. Output in |
| `datasets/sfdmu/extractions/qb-transac` | tionprocessingtypes/<timestamp>. Runs post-process by default; re-import-ready CSVs in <timestamp>/processed/. Use run_post_process false to skip. |

---

## Data Management - Idempotency

| Task | Description |
|---|---|
| `test_qb_approvals_idempotency` | Idempotency test for qb-approvals (EmailTemplate, Group/User, GroupMember, ApprovalAlertContentDef). |
| `test_qb_clm_idempotency` | Idempotency test for qb-clm. |
| `test_qb_dro_idempotency` | Idempotency test for qb-dro. Note: plan uses dynamic_assigned_to_user for load; test runs without it (scratch org user may differ). |
| `test_qb_guidedselling_idempotency` | Idempotency test for qb-guidedselling. |
| `test_qb_pcm_idempotency` | Idempotency test for qb-pcm (product catalog). Uses extraction roundtrip by default (extract -> post-process -> load) and writes to datasets/sfdmu/extractions/qb-pcm/<ti mestamp>. |
| `test_qb_pricing_idempotency` | Idempotency test for qb-pricing (load twice from source, assert no new records). |
| `test_qb_prm_idempotency` | Idempotency test for qb-prm (partner relationship management). |
| `test_qb_product_images_idempotency` | Idempotency test for qb-product-images. |
| `test_qb_rates_idempotency` | Idempotency test for qb-rates. Runs the plan twice from source CSVs and asserts no record count increase. NOTE: extraction roundtrip is not supported for qb-rates because SFDMU v5 cannot properly extract 2-hop traversal fields in RABT composite keys (RateCardEntry.RateCard.Name extracts as #N/A), breaking FK resolution on re-import. |
| `test_qb_rating_idempotency` | Idempotency test for qb-rating. Uses extraction roundtrip (extract -> post-process -> load from processed dir) to validate that extracted CSVs can be re-imported without adding records. Persists extraction output |
| `to` |  |
| `datasets/sfdmu/extractions/qb-rating/` | <timestamp>. |
| `test_qb_transactionprocessingtypes_i` | Idempotency test for |
| `dempotency` | qb-transactionprocessingtypes. Usage: cci task run <task_name> [TASK_OPTIONS...] See above for a complete list of available tasks. Use cci task info <task_name> to get more information about a task and its options. |

---

## Notes

- Run `cci task info <task_name>` for full option details.
- Source: current `cci task run --help` output.
