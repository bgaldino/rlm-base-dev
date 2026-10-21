---
page_id: apex_class_industries_docgen_DocGenPermsAndAccessChecksService.htm
title: DocGenPermsAndAccessChecksService Class
source_url: https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/apex_class_industries_docgen_DocGenPermsAndAccessChecksService.htm
release: 264
release_name: Winter '27
deliverable: clm_developer_guide
section: Salesforce Contracts
parent_page: apex_namespace_industries_docgen.htm
fetched_at: 2026-10-13
---

# DocGenPermsAndAccessChecksService Class

The
      `DocGenPermsAndAccessChecksService` class contains
    methods to check permissions and settings related to document generation and integration
    features.

## Namespace

[industries_docgen](./apex_namespace_industries_docgen.htm.md)

## Example

```
industries_docgen.DocGenPermsAndAccessChecksService.isDesigner(UserInfo.getOrganizationId(), userInfo.getUserId(), 'DocGenDesigner');
industries_docgen.DocGenPermsAndAccessChecksService.isRuntimeUser(UserInfo.getOrganizationId(), userInfo.getUserId(), 'DocGenRuntimeUser');
industries_docgen.DocGenPermsAndAccessChecksService.isRuntimeCCUser(UserInfo.getOrganizationId(), userInfo.getUserId(),'DocGenRuntimeCCUser');
```

This
        Apex code sample checks whether a user has specific docgen permissions.

- 
**[DocGenPermsAndAccessChecksService Methods](./apex_class_industries_docgen_DocGenPermsAndAccessChecksService.htm.md#apex_industries_docgen_DocGenPermsAndAccessChecksService_methods)**  

#### See Also

- [*
             Salesforce Help
            *: Permission Set Licenses for Omnistudio Document Generation](https://help.salesforce.com/s/articleView?id=ind.doc_gen_Permission_Set_Licenses_for_OmniStudio_DocGen.htm&language=en_US)

## DocGenPermsAndAccessChecksService Methods

The following are methods for `DocGenPermsAndAccessChecksService`.

- 
**[hasDocGenMetadataSetting(orgId, orgPreference)](./apex_class_industries_docgen_DocGenPermsAndAccessChecksService.htm.md#apex_industries_docgen_DocGenPermsAndAccessChecksService_hasDocGenMetadataSetting)**  

Checks whether the DocGen metadata setting is enabled for the org (`true`) or not (`false`).

- 
**[hasDocGenOrgPerm(orgId, orgPermission)](./apex_class_industries_docgen_DocGenPermsAndAccessChecksService.htm.md#apex_industries_docgen_DocGenPermsAndAccessChecksService_hasDocGenOrgPerm)**  

Checks whether the org has the DocGen permission (`true`) or not (`false`).

- 
**[hasMS365IntegrationSettingOrgPerm(orgId, orgPermission)](./apex_class_industries_docgen_DocGenPermsAndAccessChecksService.htm.md#apex_industries_docgen_DocGenPermsAndAccessChecksService_hasMS365IntegrationSettingOrgPerm)**  

Checks whether the org has a Microsoft 365 integration setting permission enabled       (`true`) or not (`false`).

- 
**[hasOmnistudioOrgPerm(orgId, orgPermission)](./apex_class_industries_docgen_DocGenPermsAndAccessChecksService.htm.md#apex_industries_docgen_DocGenPermsAndAccessChecksService_hasOmniStudioOrgPerm)**  

Checks whether the org has Omnistudio permission enabled (`true`) or not (`false`).

- 
**[isDesigner(orgId, userId, userPerm)](./apex_class_industries_docgen_DocGenPermsAndAccessChecksService.htm.md#apex_industries_docgen_DocGenPermsAndAccessChecksService_isDesigner)**  

Checks whether the user has designer permissions enabled (`true`) or not (`false`).

- 
**[isRuntimeCCUser(orgId, userId, userPerm)](./apex_class_industries_docgen_DocGenPermsAndAccessChecksService.htm.md#apex_industries_docgen_DocGenPermsAndAccessChecksService_isRuntimeCCUser)**  

Checks whether the user has runtime customer community user permissions (`true`) or not (`false`).

- 
**[isRuntimeUser(orgId, userId, userPerm)](./apex_class_industries_docgen_DocGenPermsAndAccessChecksService.htm.md#apex_industries_docgen_DocGenPermsAndAccessChecksService_isRuntimeUser)**  

Checks whether the user has runtime user permissions (`true`) or not (`false`).

### hasDocGenMetadataSetting(orgId, orgPreference)

Checks whether the DocGen metadata setting is enabled for the org (`true`) or not (`false`).

#### Signature

`public static Boolean hasDocGenMetadataSetting(String orgId, String orgPreference)`

#### Parameters

        
- 
**orgId**: Type: String ID of the org.

        
- 
**orgPreference**: Type: String Name of the DocGen metadata setting.

      

#### Return Value

Type: Boolean

### hasDocGenOrgPerm(orgId, orgPermission)

Checks whether the org has the DocGen permission (`true`) or not (`false`).

#### Signature

`public static Boolean hasDocGenOrgPerm(String orgId, String orgPermission)`

#### Parameters

- 
**orgId**: Type: String ID of the org.

- 
**orgPermission**: Type: String Name of the permission.

#### Return Value

Type: Boolean

  

### hasMS365IntegrationSettingOrgPerm(orgId,
    orgPermission)

  
  
  
Checks whether the org has a Microsoft 365 integration setting permission enabled
      (`true`) or not (`false`).

    

#### Signature

      
      

`public static Boolean hasMS365InetgrationSettingOrgPerm(String
          orgId, String orgPermission)`

      
    

    

#### Parameters

      
      
        
- 
**orgId**: Type: String ID of the org.

        
- 
**orgPermission**: Type: String Name of the permission.

      

    

    

#### Return Value

      
      

Type: Boolean

    

  

### hasOmnistudioOrgPerm(orgId, orgPermission)

Checks whether the org has Omnistudio permission enabled (`true`) or not (`false`).

#### Signature

`public static Boolean hasOmnistudioOrgPerm(String orgId, String
                    orgPermission)`

#### Parameters

- 
**orgId**: Type: String ID of the org.

- 
**orgPermission**: Type: String Name of the Omnistudio permission.

#### Return Value

Type: Boolean

### isDesigner(orgId, userId, userPerm)

Checks whether the user has designer permissions enabled (`true`) or not (`false`).

#### Signature

`public static Boolean isDesigner(String orgId, String userId, String userPerm)`

#### Parameters

- 
**orgId**: Type: String ID of the org.

- 
**userId**: Type: String ID of the user.

- 
**userPerm**: Type: String Name of the user permission to check for designer
                        status.

#### Return Value

Type: Boolean

### isRuntimeCCUser(orgId, userId, userPerm)

Checks whether the user has runtime customer community user permissions (`true`) or not (`false`).

#### Signature

`public static Boolean isRuntimeCCUser(String orgId, String userId, String userPerm)`

#### Parameters

- 
**orgId**: Type: String ID of the org.

- 
**userId**: Type: String ID of the user.

- 
**userPerm**: Type: String Name of the user permission to check for runtime customer community user
            status.

#### Return Value

Type: Boolean

### isRuntimeUser(orgId, userId, userPerm)

Checks whether the user has runtime user permissions (`true`) or not (`false`).

#### Signature

`public static Boolean isRuntimeUser(String orgId, String userId, String userPerm)`

#### Parameters

- 
**orgId**: Type: String ID of the org.

- 
**userId**: Type: String ID of the user.

- 
**userPerm**: Type: String Name of the user permission to check for runtime user status.

#### Return Value

Type: Boolean
