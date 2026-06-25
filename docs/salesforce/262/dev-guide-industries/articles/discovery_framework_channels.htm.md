---
page_id: discovery_framework_channels.htm
title: Supported Metadata Channels
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/discovery_framework_channels.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Discovery Framework
parent_page: discovery_framework_metadata_api_parent.htm
fetched_at: 2026-06-25
---

# Supported Metadata Channels

In Discovery Framework, you can create questions and question sets to categorize
questions, and you can move such a dataset across multiple orgs. A metadata wrapper is
automatically created for these objects.

Metadata APIs provide ways to package those datasets and move them across orgs. There are
multiple ways to export or import datasets from one org to another. Each way is a metadata
channel that provides some specific features with the import or export. The public metadata
API is the basic way in which metadata is serialized so that clients can read, edit, and
deploy the data into the same or another organization. Exposure in the public metadata API
is a prerequisite for these channels.

[Second-Generation Managed Packages](https://developer.salesforce.com/docs/atlas.en-us.pkg2_dev.meta/pkg2_dev/sfdx_dev_dev2gp.htm "HTML (New Window)")
:   Managed packages are used by Salesforce partners to distribute and sell
    applications to customers.

[Unlocked Packaging](https://developer.salesforce.com/docs/atlas.en-us.262.0.sfdx_dev.meta/sfdx_dev/sfdx_dev_unlocked_pkg_before.htm "HTML (New Window)")
:   Unlocked packages are especially suited for internal business apps. You can use
    unlocked packages to organize your existing metadata, package an app, extend an app
    that you’ve purchased from AppExchange, or package new metadata.

[Unmanaged Package](https://developer.salesforce.com/docs/atlas.en-us.pkg1_dev.meta/pkg1_dev/sharing_apps.htm "HTML (New Window)")
:   Unmanaged packages are typically used to distribute open-source projects or
    application templates to provide developers with the basic building blocks for an
    application.

[Change Sets](https://help.salesforce.com/s/articleView?id=platform.changesets.htm&type=5&language=en_US "HTML (New Window)")
:   Use change sets to send customizations from one Salesforce org to another. For
    example, you can create and test a new object in a sandbox org, then send it to your
    production org using a change set.

[Salesforce CLI](https://developer.salesforce.com/docs/atlas.en-us.262.0.api_meta.meta/api_meta/meta_rest_deploy_enable_cli.htm "HTML (New Window)")
:   Salesforce CLI is the client-side tool at the center of the modern Salesforce
    developer experience. It’s a command-line interface that simplifies development and
    build automation when working with Salesforce orgs. Use it to create and manage orgs,
    synchronize metadata to and from orgs, create and install packages, and more.

[Source Control Integration/Source-Driven Development](https://developer.salesforce.com/docs/atlas.en-us.262.0.sfdx_dev.meta/sfdx_dev/sfdx_dev_scratch_orgs_def_file_config_values.htm "HTML (New Window)")
:   A scratch org is a source-driven and disposable deployment of Salesforce code and
    metadata. A scratch org is fully configurable, allowing developers to emulate
    different Salesforce editions with different features and preferences.

## Usage

When importing or exporting the Discovery Framework metadata APIs types across the
supported channels, we recommend that you review these considerations:

- When you deploy metadata with a managed package, the namespace is inserted in setup and
  platform objects.
- When a dataset is deployed using a change set, the created setup object record has the
  namespace of the target org only. The created platform object record has the Null
  namespace.
- When deploying a beta or released version of the managed package in a target org, the
  installation creates both setup and platform objects for AssessmentQuestion and
  AssessmentQuestionSets. The setup object and developerName of the platform object for
  AssessmentQuestion and AssessmentQuestionSets are not editable in a target org. Assessment
  questions in Beta packages are also not editable.
- You can update or upgrade a released version of the managed package. Setup and platform
  objects for AssessmentQuestion and AssessmentQuestionSets are updated if there are changes
  in the upgraded version.
- Uninstalling the beta version of the managed package deletes the metadata from the
  target org. Setup objects are deleted for AssessmentQuestion and
  AssessmentQuestionSets.
- When using a scratch org,
  - Create the scratch org definition
    with:

    ```
    {
      "orgName": "Sample Org",
      "edition": "developer",
      "features": [
        "ASSESSMENTS"
      ],
      "settings": {
        "industriesSettings": {
          "enableIndustriesAssessment": true,
          "enableDiscoveryFrameworkMetadata": true
        }
      }
    }
    ```
  - Enabling Discovery Framework (ASSESSMENTS) enables both AssessmentQuestion and
    AssessmentQuestionSet and enabling enableDiscoveryFrameworkMetadata enables the
    metadata for both AssessmentQuestion and AssessmentQuestionSet.
  - Add the Assessment to the page layout. See [Page Layouts](https://help.salesforce.com/s/articleView?id=platform.customize_layout.htm&type=5&language=en_US "HTML (New Window)") in Salesforce Help for
    more information.
- Deploying or retrieving the OmniScript metadata API for Discovery Framework is supported
  only in Change Sets, Salesforce CLI, Source Control Integration/Source-Driven Development,
  and public metadata API channels only.
- To avoid deployment errors, do not combine Setup objects and non-setup objects in a
  single transaction. For example, deploy Apex Class and Platform BPOs, such as
  AssessmentQuestion and ExpressionSets separately. See [Deploying OmniStudio Components with Other Objects Causes an
  Exception](https://help.salesforce.com/s/articleView?id=002890891&type=1&language=en_US)
