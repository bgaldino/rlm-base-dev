---
page_id: meta_omniinteractionconfig.htm
title: OmniInteractionConfig
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/meta_omniinteractionconfig.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Omnistudio
parent_page: omnistudio_metadata_api_parent.htm
fetched_at: 2026-06-25
---

# OmniInteractionConfig

Represents configuration settings for
Omnistudio.

## Parent Type

This type extends the [Metadata](https://developer.salesforce.com/docs/atlas.en-us.262.0.api_meta.meta/api_meta/metadata.htm "HTML (New Window)")
metadata type and inherits its fullName field.

## File Suffix and Directory Location

OmniInteractionConfig components have the suffix
.omniInteractionConfig and are stored in the
OmniInteractionConfig folder.

## Version

OmniInteractionConfig components are available in API version 51.0 and later.

## Special Access Rules

OmniInteractionConfig is available if your org has the Omnistudio platform license and
related add-on and user licenses.

## Fields

| Field Name | Field Type | Description |
| --- | --- | --- |
| masterLabel | string | Required. The name of the setting. |
| value | string | Required. The value of the setting. |

## Declarative Metadata Sample Definition

The following is an example of an OmniInteractionConfig component.

```
<?xml version="1.0" encoding="UTF-8"?>
<OmniInteractionConfig xmlns="http://soap.sforce.com/2021/10/metadata">
   <masterLabel>TheFirstInstalledOmniPackage</masterLabel>
   <value>omnistudio</value>
</OmniInteractionConfig>
```

The following is an example `package.xml` that references the previous
definition.

```
<?xml version="1.0" encoding="UTF-8"?>
<Package xmlns="http://soap.sforce.com/2021/10/metadata">
    <types>
        <members>*</members>
        <name>OmniInteractionConfig</name>
    </types>
    <version>51.0</version>
</Package>
```

## Wildcard Support in the Manifest File

This metadata type supports the wildcard character `*`
(asterisk) in the package.xml manifest file. For information about
using the manifest file, see [Deploying and
Retrieving Metadata with the Zip File](https://developer.salesforce.com/docs/atlas.en-us.262.0.api_meta.meta/api_meta/file_based_zip_file.htm "HTML (New Window)").

## Usage

Settings configured using OmniInteractionConfig include:

![Important](/docs/resources/img/en-us/262.0?doc_id=images%2Ficon_note_important.png&folder=industries_reference)

#### Important

During the week of February 2, 2026, Salesforce enables the
AdvancedOmnistudioAccessCheck,
ApexClassCheckForIP, ApexClassCheck,
EnforceDMFLSAndDataEncryption, and
EnableQueryWithFLS settings by default to enhance org security.
Review and prepare your configuration for a seamless transition and to prevent potential
service interruptions.

- `AdvancedOmnistudioAccessCheck`—If set to `true`, performs advanced security checks for Omnistudio for
  Managed Packages to enhance data protection by enforcing stricter validation of access and
  permissions. These checks validate object-level access, field-level security, and Apex
  class permissions for all users, including guest, authenticated, and non-authenticated
  users, across Omnistudio components. See [Advanced Security Checks for Omnistudio for Managed
  Packages](https://help.salesforce.com/s/articleView?id=xcloud.os_advanced_security_updates_overview.htm&type=5&language=en_US).
- `ApexClassCheckForIP`—If set to `true`, strengthens security checks for Omnistudio for
  Managed Packages by enforcing Apex class access checks during Integration Procedure
  execution. This enhancement makes sure that users have the required permissions to run
  custom Apex classes referenced within Integration Procedures. See [Advanced Apex Class Check for Integration Procedures in
  Omnistudio for Managed Packages](https://help.salesforce.com/s/articleView?id=xcloud.os_ip_advanced_apex_class_check.htm&type=5&language=en_US).
- `ApexClassCheck`—Enable access to the `VlocityOpenInterface` Apex class that's used by remote
  action APIs for a user profile. Configure an Apex class permissions checker to make sure
  that users require explicit access to the Apex class that administers the remote action
  called from an Omniscript, Flexcard, or REST API. Checks Apex classes assigned to a
  profile and controls access. If the Omnistudio license isn’t available in your Salesforce
  org (for example, if you have installed Omnistudio as part of the CME or Insurance managed
  package), set the `ApexClassCheck` configuration to
  `true`. See [Add an Apex Class Permissions Checker](https://help.salesforce.com/s/articleView?id=xcloud.os_standard_add_an_apex_class_permissions_checker.htm&language=en_US&type=5).
- `CheckCachedMetadataRecordSecurity`—If set to `true`, performs a record-level security check for cached
  data in Data Mappers and Integration Procedures.
- `DefaultRequiredPermission`—The Custom Permission a
  user must have to run Data Mappers and Integration Procedures.
- `DocuSignAccountId`—The API Account ID from
  DocuSign's Apps and Keys page.
- `DocuSignNamedCredential`—The named credential for
  connecting to DocuSign. Set the value to `DocuSign`.
- `EnableQueryWithFLS`—Construct text-based search
  queries against the search index with Salesforce Object Search Language (SOSL). By using a
  single query, you can search text, email, and phone fields for multiple objects to which
  you have access, including custom objects. SOSL queries are encrypted so the query
  information isn’t visible on the client side. To enforce field-level security for an SOSL
  query, add the `EnableQueryWithFLS` Omni Interaction
  Configuration and set it to `true`. See [Set Up a Data Source on a Flexcard](https://help.salesforce.com/s/articleView?id=xcloud.os_configure_a_data_source_on_a_flexcard_35864.htm&language=en_US&type=5).
- `EnforceDMFLSAndDataEncryption`—If set to `true`, this setting enforces field-level security for all
  Data Mappers and displays encrypted fields in plain text only for users with the View
  Encrypted Data permission. This configuration also enforces object-level security. If set
  to true, Data Mappers run in the user context instead of the system context. The system
  respects the object and field-level permissions of the running user so that they only see
  the data they have access to. See [Security for Omnistudio Data Mappers and Integration
  Procedures](https://help.salesforce.com/s/articleView?id=xcloud.os_security_for_dataraptors_and_integration_procedures_48147.htm&language=en_US&type=5).
- `InstalledIndustryPackage`—If present, lists the namespace of the Salesforce
  Industries managed package that was installed. Values are `vlocity_cmt`, `vlocity_ins`, or `vlocity_ps`. Read-only.
- `newportZipUrl`—The relative URL (without the
  hostname) for the static resource that contains custom Newport styles for FlexCards.
- `OmniAnalyticsTrackingDebug`—If set to `true`, includes debugging data in Omnistudio Tracking
  Service records.
- `PerformAdvancedCheck`—If set to `true`, this configuration enables specific access to the
  `VlocityOpenInterface` Apex class used by remote
  action APIs for a user’s permission set or permission set group. This check is dependent
  on the `ApexClassCheck` and can only work if the
  `ApexClassCheck` setting is also set to `true`.
- `RetainDesignerSettingOnUpgrade`—If you're using the
  Standard Runtime and Package Designer, and you upgrade the package installation in your
  org, the designer switches to Standard Designer by default. To retain your preferred
  designer after the upgrade, set the `RetainDesignerSettingOnUpgrade` configuration to `true`.

  ![Note](/docs/resources/img/en-us/262.0?doc_id=images%2Ficon_note.png&folder=industries_reference)

  #### Note

  If you have enabled the Omnistudio standard designer by turning the
  Managed Package Designer setting off, you don’t require this configuration. This is only
  applicable to orgs that use the managed package designer with the standard
  runtime.
- `RollbackDRChanges`—If set to `true`, rolls back Data Mapper functionality changes. Use it
  if an upgrade causes some Data Mappers to stop working.
- `SkipUserProfileOnOSLoad`—If set to `true`, it doesn’t retrieve the user profile information when
  the Omniscript loads. If set to `false` or if the
  configuration is not available, it retrieves the user profile information when the
  Omniscript loads.
- `TheFirstInstalledOmniPackage`—Lists the namespace of
  the managed package that was installed first, which determines whether new or legacy
  Omnistudio features are available. Values are `omnistudio` for new features, or `vlocity_cmt`, `vlocity_ins`, or `vlocity_ps` for legacy features. Read-only.
- `Track_`component—If set to
  `true`, enables tracking for a component or component
  type in the Omnistudio Tracking Service.
- `TurnOffScaleCache`—If set to `true`, turns off the Scale Cache that Data Mappers and
  Integration Procedures use.
- `UserLocaleDateTime`—If set to `true`, processes date, time, and datetime field inputs using
  the user’s specific locale format rather than the standard list of predefined formats. Use
  it to ensure field inputs align with regional user expectations. See [Configure Date and Time Settings in Data
  Mappers](https://help.salesforce.com/s/articleView?id=xcloud.os_omni_interaction_config.htm&type=5&language=en_US).
- `EnableParentCompile`—If set to `true`, ensures metadata consistency and prevents migration
  failures for nested components. Use it to automate the compilation of parent elements and
  avoid manual rework during the migration process. See [Omnistudio Migration Prerequisites](https://help.salesforce.com/s/articleView?id=xcloud.os_migrate_oma_prereq.htm&type=5&language=en_US).
