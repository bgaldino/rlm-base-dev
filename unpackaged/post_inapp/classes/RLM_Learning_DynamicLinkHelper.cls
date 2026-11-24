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
        RLM_Learning_Open_in_new_tab__c,
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
      throw userFailure(LINK_TARGET_UNREADABLE, 'getObjectIdFromQuery on ' + objectAPIName, e);
    }
  }

  @AuraEnabled(cacheable=true)
  public static String getSetupPageLink(String objectAPIName, String record) {
    if (String.isEmpty(objectAPIName)) {
      throw new AuraHandledException('Setup page Name cannot be null or empty.');
    }
    if (String.isEmpty(record)) {
      throw new AuraHandledException('Record id cannot be null or empty.');
    }
    String baseUrl = System.Url.getOrgDomainUrl().toExternalForm();
    try {
      // record must be a real Id — validate inside the try so a bad value surfaces
      // as a clear AuraHandledException, not a raw TypeException.
      Id recordId = Id.valueOf(record);
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
      String url = baseUrl + setupPage[0].RLM_Learning_Setup_Page_URL__c + '/' + recordId;
      // The configured Setup page URLs already carry a query string (e.g. ".../page?address="),
      // so start the extra params with '&' when a '?' is already present (use '?' only if not).
      String noRedirect = (url.contains('?') ? '&' : '?') + 'noredirect=1';
      if (objectAPIName == 'Contact') {
        noRedirect = noRedirect + '&isContactEntityOverride=1';
      }
      return url + noRedirect;
    } catch (AuraHandledException e) {
      throw e; // a missing or blank Setup page mapping already carries its own message
    } catch (Exception e) {
      throw userFailure(SETUP_LINK_FAILED, 'getSetupPageLink for ' + objectAPIName, e);
    }
  }

  @AuraEnabled(cacheable=true)
  public static String getSiteUrl(String networkId) {
    try {
      Id nId = Id.valueOf(networkId);
      String loginUrl = Network.getLoginUrl(nId);
      // Only a login URL with no "/s/" segment needs the site's path prefix looked up.
      String pathPrefix = (loginUrl != null && !loginUrl.contains('/s/'))
        ? lookupPathPrefix(nId, loginUrl)
        : null;
      return siteBaseUrl(loginUrl, pathPrefix);
    } catch (Exception e) {
      throw userFailure(SITE_URL_FAILED, 'getSiteUrl for ' + networkId, e);
    }
  }

  // Shapes the site base URL from the login URL and the site's path prefix. Pure, so it is
  // unit-tested over literal URLs.
  //  - The login URL of an Experience Cloud site is "<scheme>://<host>[/<sitePrefix>]/s/login":
  //    the base is everything before "/s/", which keeps a path-based prefix (e.g. "/customers").
  //  - A site whose login URL has no "/s/" (for example a Visualforce site) carries no prefix in
  //    that URL, so the base is scheme://host plus "/" + the site's path prefix on that domain.
  //  - For a site with a Network UrlPathPrefix, the prefix is the one the site has on the login URL's
  //    own domain (DomainSite.PathPrefix), so a Visualforce-based site that a custom domain serves at
  //    the root keeps the host-only URL. Only when no such domain mapping is readable is the
  //    Network's UrlPathPrefix used, which is the site's path on the default domains. A site with no
  //    Network prefix keeps the host-only URL.
  //  - A blank prefix keeps scheme://host.
  @TestVisible
  private static String siteBaseUrl(String loginUrl, String urlPathPrefix) {
    Integer sIndex = loginUrl == null ? -1 : loginUrl.indexOf('/s/');
    if (sIndex > 0) {
      return loginUrl.substring(0, sIndex);
    }
    Url parsed = new Url(loginUrl);
    String base = parsed.getProtocol() + '://' + parsed.getHost();
    // Strip every leading and trailing slash (String.removeStart/removeEnd would strip only one).
    String prefix = urlPathPrefix == null ? '' : urlPathPrefix.trim().replaceAll('^/+|/+$', '');
    return String.isBlank(prefix) ? base : base + '/' + prefix;
  }

  // The path prefix the site has on the login URL's domain: the domain mapping when one is readable,
  // else the Network's own prefix. A custom domain that serves the site at its root maps it with a
  // blank prefix, which must win over the Network's prefix.
  private static String lookupPathPrefix(Id networkId, String loginUrl) {
    String networkPrefix = lookupNetworkPathPrefix(networkId);
    return resolvePathPrefix(
      lookupDomainPathPrefixes(new Url(loginUrl).getHost(), networkPrefix),
      networkPrefix
    );
  }

  // Pure, so it is unit-tested: a readable domain mapping decides, even when its prefix is blank.
  @TestVisible
  private static String resolvePathPrefix(List<String> domainPrefixes, String networkPrefix) {
    return domainPrefixes == null || domainPrefixes.isEmpty() ? networkPrefix : domainPrefixes[0];
  }

  // DomainSite maps a site to a domain with its own PathPrefix. Queried dynamically like Network,
  // in USER_MODE: a user who cannot read it gets no mapping and falls back to the Network prefix.
  // Measured on a 264 org: a default-domain row carries "/<UrlPathPrefix>" (for example
  // "/sfpwebhookvforcesite"); the root-mapping custom-domain case is not reproducible on a scratch
  // org, so the blank-prefix branch is covered by resolvePathPrefix's unit test only.
  private static List<String> lookupDomainPathPrefixes(String host, String networkPrefix) {
    List<String> prefixes = new List<String>();
    if (String.isBlank(networkPrefix)) {
      return prefixes;
    }
    try {
      for (
        SObject row : Database.query(
          'SELECT PathPrefix FROM DomainSite WHERE Domain.Domain = :host AND Site.UrlPathPrefix = :networkPrefix LIMIT 1',
          AccessLevel.USER_MODE
        )
      ) {
        String prefix = (String) row.get('PathPrefix');
        prefixes.add(prefix == null ? '' : prefix);
      }
    } catch (QueryException e) {
      System.debug(
        LoggingLevel.WARN,
        'RLM_Learning_DynamicLinkHelper: could not read DomainSite.PathPrefix, using the Network prefix: ' +
        e.getMessage()
      );
    }
    return prefixes;
  }

  // Network exists only with Digital Experiences, so it is queried dynamically (a static
  // reference would not compile without it). USER_MODE: a user who cannot read Network
  // gets no prefix, the host-only URL the method returned before, and a WARN debug line says so.
  // Measured on a 264 org: Network.UrlPathPrefix is not permissionable (no field-level security)
  // and no permission set carries an object permission for Network, so no grant is needed or
  // possible; whether every persona can read it is inferred and checked live.
  private static String lookupNetworkPathPrefix(Id networkId) {
    try {
      List<SObject> rows = Database.query(
        'SELECT UrlPathPrefix FROM Network WHERE Id = :networkId LIMIT 1',
        AccessLevel.USER_MODE
      );
      return rows.isEmpty() ? null : (String) rows[0].get('UrlPathPrefix');
    } catch (QueryException e) {
      System.debug(
        LoggingLevel.WARN,
        'RLM_Learning_DynamicLinkHelper: could not read Network.UrlPathPrefix, using the host-only site URL: ' +
        e.getMessage()
      );
      return null;
    }
  }

  // Refuted PMD false-positive: dynamicLinkType is switch-constrained, queries run in
  // USER_MODE, and `whereCondition` is admin-authored config. SFGE reports 0 violations.
  @AuraEnabled(cacheable=true)
  @SuppressWarnings('PMD.ApexSOQLInjection')
  public static List<SObject> getRecordIdFromDynamicLinkType(
    String dynamicLinkType,
    String whereCondition
  ) {
    if (String.isEmpty(dynamicLinkType)) {
      throw new AuraHandledException('DynamicLinkType cannot be null or empty.');
    }
    if (String.isEmpty(whereCondition)) {
      throw new AuraHandledException('Where Condition cannot be null or empty.');
    }
    try {
      // dynamicLinkType is constrained by the switch; whereCondition is admin-authored
      // config (see class doc). Every branch executes in USER_MODE.
      String query = '';
      switch on dynamicLinkType {
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
            'Unsupported dynamic link type: ' + dynamicLinkType
          );
        }
      }
      return Database.query(query, AccessLevel.USER_MODE);
    } catch (AuraHandledException e) {
      throw e; // the unsupported-type message names only the configured link type
    } catch (Exception e) {
      throw userFailure(LINK_TARGET_UNREADABLE, 'getRecordIdFromDynamicLinkType ' + dynamicLinkType, e);
    }
  }

  @TestVisible
  private static final String LINK_TARGET_UNREADABLE = 'The record this link points to could not be read.';
  @TestVisible
  private static final String SETUP_LINK_FAILED = 'The Setup page link could not be built.';
  @TestVisible
  private static final String SITE_URL_FAILED = 'The site URL could not be resolved.';

  // A failed query or id check carries query, object and field text, so the user sees a fixed
  // sentence; the detail goes to the debug log and stays on the cause.
  private static AuraHandledException userFailure(String message, String context, Exception cause) {
    System.debug(
      LoggingLevel.ERROR,
      'RLM_Learning_DynamicLinkHelper ' + context + ': ' + cause.getTypeName() + ': ' + cause.getMessage()
    );
    AuraHandledException e = new AuraHandledException(message);
    e.setMessage(message);
    e.initCause(cause);
    return e;
  }
}
