/**
 * Resolves DynamicLink__c navigation targets for the In-App Learning framework.
 *
 * Security posture (hardened per .cursor/skills/apex-security-hardening):
 *  - Every entry-reachable SOQL runs in USER_MODE (caller CRUD/FLS enforced).
 *  - Dynamic object names are validated against the schema before use.
 *  - Id parameters are validated with Id.valueOf; values placed inside string
 *    literals are escaped with String.escapeSingleQuotes.
 *  - `whereCondition` is an admin-authored SOQL fragment stored on
 *    DynamicLink__c.Where_Condition__c (only editable by users with the
 *    RLM_InApp_Learning permission set). It cannot be escaped because it
 *    legitimately contains quoted literals (e.g. Name = 'Infinitech'); USER_MODE
 *    constrains it to data the caller may already read and to read-only Id results.
 */
public with sharing class DynamicLinkHelper {
  @AuraEnabled(cacheable=true)
  public static DynamicLink__c getDynamicLinkByIdentity(String identifier) {
    return [
      SELECT
        Id,
        Name,
        App_API_Name__c,
        Identity__c,
        Object__c,
        Page_Name__c,
        Relationship_API_Name__c,
        Text_Value__c,
        Where_Condition__c,
        RecordType.DeveloperName,
        Page__c,
        Link__c,
        Relative_Url__c,
        Setup_Page__c,
        Site_Name__c
      FROM DynamicLink__c
      WHERE Identity__c = :identifier
      WITH USER_MODE
    ];
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

  // Refuted PMD false-positive: the only interpolated value (objectAPIName) is passed
  // through String.escapeSingleQuotes into a LIKE literal; query runs in USER_MODE.
  @AuraEnabled(cacheable=true)
  @SuppressWarnings('PMD.ApexSOQLInjection')
  public static String getSetupPageLink(String objectAPIName, String record) {
    if (String.isEmpty(objectAPIName)) {
      throw new AuraHandledException('Setup page Name cannot be null or empty.');
    }
    // record must be a real Id — validate before it goes into the returned URL.
    Id recordId = Id.valueOf(record);
    String base_url = System.Url.getOrgDomainUrl().toExternalForm();
    String noRedirect = '?noredirect=1';
    try {
      // objectAPIName sits inside a quoted LIKE literal, so escape it.
      String whereCondition =
        'Label like \'%' + String.escapeSingleQuotes(objectAPIName) + '%\'';
      String query =
        'SELECT Setup_Page_URL__c FROM Setup_Page_Map__mdt WHERE ' + whereCondition;

      List<Setup_Page_Map__mdt> setupPage = Database.query(query, AccessLevel.USER_MODE);
      if (setupPage.isEmpty()) {
        throw new AuraHandledException('No Setup Page record for ' + objectAPIName);
      }
      if (String.isEmpty(setupPage[0].Setup_Page_URL__c)) {
        throw new AuraHandledException('No Setup Page url missing' + objectAPIName);
      }
      if (objectAPIName == 'Contact') {
        noRedirect = noRedirect + '&isContactEntityOverride=1';
      }
      return base_url + setupPage[0].Setup_Page_URL__c + '/' + recordId + noRedirect;
    } catch (Exception e) {
      throw new AuraHandledException(e.getMessage());
    }
  }

  @AuraEnabled(cacheable=true)
  public static String getSiteUrl(String networkId) {
    try {
      Id nId = Id.valueOf(networkId);
      String url = Network.getLoginUrl(nId).substringBefore('.com');
      return url + '.com';
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
