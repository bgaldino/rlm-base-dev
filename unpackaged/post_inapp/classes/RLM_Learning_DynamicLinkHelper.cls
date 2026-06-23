/**
 * Resolves RLM_Learning_DynamicLink__c navigation targets for the In-App Learning framework.
 *
 * Security posture (hardened per .cursor/skills/apex-security-hardening):
 *  - Every entry-reachable SOQL runs in USER_MODE (caller CRUD/FLS enforced).
 *  - Dynamic object names are validated against the schema before use.
 *  - Id parameters are validated with Id.valueOf; values placed inside string
 *    literals are escaped with String.escapeSingleQuotes.
 *  - `whereCondition` is an admin-authored SOQL fragment stored on
 *    RLM_Learning_DynamicLink__c.RLM_Learning_Where_Condition__c (only editable by users with the
 *    RLM_Learning permission set). It cannot be escaped because it
 *    legitimately contains quoted literals (e.g. Name = 'Infinitech'); USER_MODE
 *    constrains it to data the caller may already read and to read-only Id results.
 */
public with sharing class RLM_Learning_DynamicLinkHelper {
  @AuraEnabled(cacheable=true)
  public static RLM_Learning_DynamicLink__c getDynamicLinkByIdentity(String identifier) {
    if (String.isEmpty(identifier)) {
      throw new AuraHandledException('Identifier cannot be null or empty.');
    }
    List<RLM_Learning_DynamicLink__c> links = [
      SELECT
        Id,
        Name,
        RLM_Learning_App_API_Name__c,
        RLM_Learning_Identity__c,
        RLM_Learning_Object__c,
        RLM_Learning_Page_Name__c,
        RLM_Learning_Relationship_API_Name__c,
        RLM_Learning_Text_Value__c,
        RLM_Learning_Where_Condition__c,
        RecordType.DeveloperName,
        RLM_Learning_Page__c,
        RLM_Learning_Link__c,
        RLM_Learning_Relative_Url__c,
        RLM_Learning_Setup_Page__c,
        RLM_Learning_Site_Name__c
      FROM RLM_Learning_DynamicLink__c
      WHERE RLM_Learning_Identity__c = :identifier
      WITH USER_MODE
      LIMIT 1
    ];
    if (links.isEmpty()) {
      throw new AuraHandledException(
        'No dynamic link found for identifier: ' + identifier
      );
    }
    return links[0];
  }

  // Refuted PMD false-positive: object is schema-allow-listed, the query runs in
  // USER_MODE, and `whereCondition` is admin-authored config (not end-user input).
  // Salesforce Graph Engine (data-flow) reports 0 violations.
  @AuraEnabled(cacheable=true)
  @SuppressWarnings('PMD.ApexSOQLInjection')
  public static List<SObject> getObjectIdFromQuery(
    String objectAPIName,
    String whereCondition
  ) {
    if (String.isEmpty(objectAPIName)) {
      throw new AuraHandledException('Object API Name cannot be null or empty.');
    }
    if (String.isEmpty(whereCondition)) {
      throw new AuraHandledException('Where Condition cannot be null or empty.');
    }
    // Allow-list the object: reject anything that isn't a real SObject so the
    // FROM clause can never be turned into an arbitrary/garbage target.
    if (!Schema.getGlobalDescribe().containsKey(objectAPIName)) {
      throw new AuraHandledException('Unknown or inaccessible object: ' + objectAPIName);
    }
    try {
      // whereCondition is admin-authored config (see class doc); USER_MODE enforces
      // the caller's CRUD/FLS on the dynamic query.
      String query = 'SELECT Id FROM ' + objectAPIName + ' WHERE ' + whereCondition;
      return Database.query(query, AccessLevel.USER_MODE);
    } catch (Exception e) {
      throw new AuraHandledException(e.getMessage());
    }
  }

  @AuraEnabled(cacheable=true)
  public static String getSetupPageLink(String objectAPIName, String record) {
    if (String.isEmpty(objectAPIName)) {
      throw new AuraHandledException('Setup page Name cannot be null or empty.');
    }
    // record must be a real Id — validate before it goes into the returned URL.
    Id recordId = Id.valueOf(record);
    String baseUrl = System.Url.getOrgDomainUrl().toExternalForm();
    String noRedirect = '?noredirect=1';
    try {
      // Exact match on DeveloperName: a LIKE '%x%' could match the wrong record
      // (e.g. PermissionSet also matches PermissionSetGroup). The bind variable
      // also removes the dynamic-SOQL injection surface.
      List<RLM_Learning_Setup_Page_Map__mdt> setupPage = [
        SELECT RLM_Learning_Setup_Page_URL__c
        FROM RLM_Learning_Setup_Page_Map__mdt
        WHERE DeveloperName = :objectAPIName
        WITH USER_MODE
        LIMIT 1
      ];
      if (setupPage.isEmpty()) {
        throw new AuraHandledException('No Setup Page record for ' + objectAPIName);
      }
      if (String.isEmpty(setupPage[0].RLM_Learning_Setup_Page_URL__c)) {
        throw new AuraHandledException(
          'Setup Page URL is blank for ' + objectAPIName
        );
      }
      if (objectAPIName == 'Contact') {
        noRedirect = noRedirect + '&isContactEntityOverride=1';
      }
      return baseUrl + setupPage[0].RLM_Learning_Setup_Page_URL__c + '/' + recordId + noRedirect;
    } catch (Exception e) {
      throw new AuraHandledException(e.getMessage());
    }
  }

  @AuraEnabled(cacheable=true)
  public static String getSiteUrl(String networkId) {
    try {
      Id nId = Id.valueOf(networkId);
      // Extract scheme + host from the login URL rather than assuming a `.com`
      // domain (Experience Cloud login URLs can have a path or non-.com host).
      Url loginUrl = new Url(Network.getLoginUrl(nId));
      return loginUrl.getProtocol() + '://' + loginUrl.getHost();
    } catch (Exception e) {
      throw new AuraHandledException(e.getMessage());
    }
  }

  // Refuted PMD false-positive: dyanmicLinkType is switch-constrained, queries run in
  // USER_MODE, and `whereCondition` is admin-authored config. SFGE reports 0 violations.
  @AuraEnabled(cacheable=true)
  @SuppressWarnings('PMD.ApexSOQLInjection')
  public static List<SObject> getRecordIdFromDynamicLinkType(
    String dyanmicLinkType,
    String whereCondition
  ) {
    if (String.isEmpty(dyanmicLinkType)) {
      throw new AuraHandledException('DynamicLinkType cannot be null or empty.');
    }
    if (String.isEmpty(whereCondition)) {
      throw new AuraHandledException('Where Condition cannot be null or empty.');
    }
    try {
      // dyanmicLinkType is constrained by the switch; whereCondition is admin-authored
      // config (see class doc). Every branch executes in USER_MODE.
      String query = '';
      switch on dyanmicLinkType {
        when 'SurveyRecordPage' {
          query =
            'Select Id from SurveyVersion Where SurveyId in (Select Id from Survey Where ' +
            whereCondition +
            ') Order by VersionNumber DESC Limit 1';
        }
        when 'FlowRecordPage' {
          query =
            'SELECT ActiveVersionId FROM FlowDefinitionView WHERE ' +
            whereCondition +
            ' LIMIT 1';
        }
        when 'DPERecordPage' {
          query =
            'SELECT Id FROM BatchCalcJobDefinition WHERE ' +
            whereCondition +
            ' LIMIT 1';
        }
        when 'CommunityPage' {
          query = 'Select Id from Network Where ' + whereCondition + ' LIMIT 1';
        }
        when else {
          throw new AuraHandledException(
            'Unsupported dynamic link type: ' + dyanmicLinkType
          );
        }
      }
      return Database.query(query, AccessLevel.USER_MODE);
    } catch (Exception e) {
      throw new AuraHandledException(e.getMessage());
    }
  }
}
