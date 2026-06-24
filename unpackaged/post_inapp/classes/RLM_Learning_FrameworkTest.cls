/**
 * Unit tests for the In-App Learning framework controllers:
 * RLM_Learning_SectionBlockController, RLM_Learning_SectionBlockSequence,
 * RLM_Learning_DynamicLinkHelper, and RLM_Learning_UserInformation.
 *
 * Builds a minimal Page -> Section -> Block graph (with an Icon and a WebPage
 * DynamicLink) and exercises the happy paths plus the input-validation and
 * empty-result guards.
 */
@IsTest
private class RLM_Learning_FrameworkTest {
  @TestSetup
  static void makeData() {
    Id sectionTopRt = rtId('RLM_Learning_Section__c', 'Top');
    Id sectionRightRt = rtId('RLM_Learning_Section__c', 'Right');
    Id webPageRt = rtId('RLM_Learning_DynamicLink__c', 'WebPage');

    RLM_Learning_Icon__c icon = new RLM_Learning_Icon__c(
      Name = 'TestIcon',
      RLM_Learning_Size__c = 'small',
      RLM_Learning_Type__c = 'utility:moneybag'
    );
    insert icon;

    RLM_Learning_Page__c page = new RLM_Learning_Page__c(
      Name = 'TestHome',
      RLM_Learning_Type__c = 'Home',
      RLM_Learning_Active__c = true
    );
    insert page;

    RLM_Learning_DynamicLink__c dl = new RLM_Learning_DynamicLink__c(
      Name = 'Test DynamicLink',
      RecordTypeId = webPageRt,
      RLM_Learning_Identity__c = 'TEST_DYN_LINK',
      RLM_Learning_Link__c = 'https://example.com'
    );
    insert dl;

    RLM_Learning_Section__c sec = new RLM_Learning_Section__c(
      Name = 'Test Section',
      RecordTypeId = sectionTopRt,
      RLM_Learning_Page__c = page.Id,
      RLM_Learning_Icon__c = icon.Id,
      RLM_Learning_Active__c = true,
      RLM_Learning_Header__c = 'H',
      RLM_Learning_Sub_Header__c = 'S',
      RLM_Learning_Video_Link__c = 'https://video.example.com'
    );
    insert sec;

    // Second section with no blocks, to exercise the empty-blocks guard.
    RLM_Learning_Section__c secEmpty = new RLM_Learning_Section__c(
      Name = 'Test Empty Section',
      RecordTypeId = sectionRightRt,
      RLM_Learning_Page__c = page.Id,
      RLM_Learning_Active__c = true,
      RLM_Learning_Header__c = 'Empty'
    );
    insert secEmpty;

    RLM_Learning_Block__c blk = new RLM_Learning_Block__c(
      Name = 'TestBlock',
      RLM_Learning_Active__c = true,
      RLM_Learning_Header__c = 'BH',
      RLM_Learning_Sub_Header__c = 'BS',
      RLM_Learning_ActionText__c = 'Go',
      RLM_Learning_Description__c = 'Desc',
      RLM_Learning_Icon__c = icon.Id,
      RLM_Learning_Action__c = dl.Id
    );
    insert blk;

    insert new RLM_Learning_SectionBlock__c(
      RLM_Learning_Section__c = sec.Id,
      RLM_Learning_Block__c = blk.Id,
      RLM_Learning_Order_Sequence__c = 1
    );
  }

  static Id rtId(String sobj, String dev) {
    return [
      SELECT Id
      FROM RecordType
      WHERE SObjectType = :sobj AND DeveloperName = :dev
      LIMIT 1
    ]
    .Id;
  }

  static RLM_Learning_Section__c sectionByHeader(String header) {
    return [
      SELECT Id
      FROM RLM_Learning_Section__c
      WHERE RLM_Learning_Header__c = :header
      LIMIT 1
    ];
  }

  // ---- SectionBlockController ------------------------------------------------

  @IsTest
  static void getSectionsWithBlocksByType_returnsResolvedGraph() {
    Test.startTest();
    List<Map<String, Object>> res = RLM_Learning_SectionBlockController.getSectionsWithBlocksByType(
      'Top',
      'Home'
    );
    Test.stopTest();
    Assert.isFalse(res.isEmpty(), 'expected at least one section');
    Map<String, Object> m = res[0];
    Assert.isNotNull(m.get('section'), 'section present');
    Assert.isNotNull(m.get('blocks'), 'blocks present');
    Assert.isNotNull(m.get('dynamicLinks'), 'dynamicLinks present');
    Assert.isFalse(
      ((List<Object>) m.get('dynamicLinks')).isEmpty(),
      'dynamic link resolved'
    );
  }

  @IsTest
  static void getSectionsWithBlocksByPageId_returnsSections() {
    RLM_Learning_Page__c p = [
      SELECT Id
      FROM RLM_Learning_Page__c
      WHERE Name = 'TestHome'
      LIMIT 1
    ];
    List<Map<String, Object>> res = RLM_Learning_SectionBlockController.getSectionsWithBlocksByPageId(
      'Top',
      p.Id
    );
    Assert.isFalse(res.isEmpty(), 'expected sections by page id');
  }

  @IsTest
  static void getSectionWithBlockBySectionId_happyPath() {
    List<Map<String, Object>> res = RLM_Learning_SectionBlockController.getSectionWithBlockBySectionId(
      sectionByHeader('H').Id
    );
    Assert.isFalse(res.isEmpty(), 'expected a result');
    Assert.isNotNull(res[0].get('block'), 'block present');
  }

  @IsTest
  static void getSectionWithBlockBySectionId_noBlocksThrows() {
    Boolean threw = false;
    try {
      RLM_Learning_SectionBlockController.getSectionWithBlockBySectionId(
        sectionByHeader('Empty').Id
      );
    } catch (AuraHandledException e) {
      threw = true;
    }
    Assert.isTrue(threw, 'expected guard exception for a section with no blocks');
  }

  @IsTest
  static void controller_validationErrors() {
    Boolean a = false, b = false, c = false;
    try {
      RLM_Learning_SectionBlockController.getSectionsByType('', 'Home');
    } catch (AuraHandledException e) {
      a = true;
    }
    try {
      RLM_Learning_SectionBlockController.getSectionsByPageId('Top', '');
    } catch (AuraHandledException e) {
      b = true;
    }
    try {
      RLM_Learning_SectionBlockController.getSectionWithBlockBySectionId('');
    } catch (AuraHandledException e) {
      c = true;
    }
    Assert.isTrue(a && b && c, 'each missing-arg call should throw');
  }

  // ---- SectionBlockSequence --------------------------------------------------

  @IsTest
  static void sectionBlockSequence_crud() {
    Id secId = sectionByHeader('H').Id;
    RLM_Learning_Block__c blk = [
      SELECT Id
      FROM RLM_Learning_Block__c
      WHERE Name = 'TestBlock'
      LIMIT 1
    ];

    Test.startTest();
    Assert.isFalse(
      RLM_Learning_SectionBlockSequence.getAllBlocks().isEmpty(),
      'expected blocks'
    );
    Assert.areEqual(
      1,
      RLM_Learning_SectionBlockSequence.getBlocksForSection(secId).size(),
      'one junction before update'
    );
    RLM_Learning_SectionBlockSequence.updateSectionBlocks(
      secId,
      new List<String>{ blk.Id }
    );
    Test.stopTest();

    Assert.areEqual(
      1,
      RLM_Learning_SectionBlockSequence.getBlocksForSection(secId).size(),
      'still one junction after re-set (no duplicates)'
    );
  }

  @IsTest
  static void updateSectionBlocks_validationErrors() {
    Boolean a = false, b = false;
    try {
      RLM_Learning_SectionBlockSequence.updateSectionBlocks('', new List<String>());
    } catch (AuraHandledException e) {
      a = true;
    }
    try {
      RLM_Learning_SectionBlockSequence.updateSectionBlocks(
        sectionByHeader('H').Id,
        null
      );
    } catch (AuraHandledException e) {
      b = true;
    }
    Assert.isTrue(a && b, 'blank sectionId and null blockIds should each throw');
  }

  // ---- DynamicLinkHelper -----------------------------------------------------

  @IsTest
  static void dynamicLinkHelper_happyPaths() {
    Assert.isNotNull(
      RLM_Learning_DynamicLinkHelper.getDynamicLinkByIdentity('TEST_DYN_LINK'),
      'dynamic link by identity'
    );
    Assert.areEqual(
      1,
      RLM_Learning_DynamicLinkHelper.getObjectIdFromQuery(
          'RLM_Learning_Page__c',
          'Name = \'TestHome\''
        )
        .size(),
      'object id from query'
    );
  }

  @IsTest
  static void dynamicLinkHelper_guards() {
    Boolean blankObj = false, unknownObj = false, blankSetup = false, badType = false;
    Boolean blankIdentity = false, missingIdentity = false;
    try {
      RLM_Learning_DynamicLinkHelper.getDynamicLinkByIdentity('');
    } catch (AuraHandledException e) {
      blankIdentity = true;
    }
    try {
      RLM_Learning_DynamicLinkHelper.getDynamicLinkByIdentity('NO_SUCH_IDENTITY');
    } catch (AuraHandledException e) {
      missingIdentity = true;
    }
    try {
      RLM_Learning_DynamicLinkHelper.getObjectIdFromQuery('', '');
    } catch (AuraHandledException e) {
      blankObj = true;
    }
    try {
      RLM_Learning_DynamicLinkHelper.getObjectIdFromQuery(
        'Not_A_Real_Object__x',
        'Id != null'
      );
    } catch (AuraHandledException e) {
      unknownObj = true;
    }
    try {
      RLM_Learning_DynamicLinkHelper.getSetupPageLink('', 'x');
    } catch (AuraHandledException e) {
      blankSetup = true;
    }
    try {
      RLM_Learning_DynamicLinkHelper.getRecordIdFromDynamicLinkType(
        'UnsupportedType',
        'Id != null'
      );
    } catch (AuraHandledException e) {
      badType = true;
    }
    Assert.isTrue(
      blankObj && unknownObj && blankSetup && badType && blankIdentity && missingIdentity,
      'each helper guard should throw'
    );
  }

  @IsTest
  static void dynamicLinkHelper_branchCoverage() {
    // Exercise the remaining dynamic-SOQL branches. Some query objects/features
    // that may be absent in a scratch org; we only require the branch to execute
    // (it either returns a list or surfaces as an AuraHandledException).
    for (
      String t : new List<String>{
        'SurveyRecordPage',
        'FlowRecordPage',
        'DPERecordPage',
        'CommunityPage'
      }
    ) {
      try {
        RLM_Learning_DynamicLinkHelper.getRecordIdFromDynamicLinkType(
          t,
          'Id != null'
        );
      } catch (Exception e) {
        // feature/data may be absent in a scratch org — branch still executed
      }
    }
    // The PermissionSet Setup_Page_Map record ships with this feature, so this resolves
    // to a real URL — assert the query string is well-formed (the configured URL already
    // has "?address=", so noredirect must be appended with "&", not a second "?").
    PermissionSet ps = [SELECT Id FROM PermissionSet LIMIT 1];
    String setupUrl = RLM_Learning_DynamicLinkHelper.getSetupPageLink(
      'PermissionSet',
      ps.Id
    );
    Assert.isTrue(
      setupUrl.contains('&noredirect=1'),
      'noredirect must be appended with & when the URL already has a query string: ' +
        setupUrl
    );
    Assert.isFalse(
      setupUrl.contains('?noredirect=1'),
      'noredirect must not introduce a second "?": ' + setupUrl
    );
    try {
      RLM_Learning_DynamicLinkHelper.getSiteUrl('0DB000000000001AAA');
    } catch (Exception e) {
      // no such network is acceptable
    }
  }

  // ---- UserInformation -------------------------------------------------------

  @IsTest
  static void userInformation_paths() {
    // None should throw; getExpiryDays returns null on non-trial orgs.
    RLM_Learning_UserInformation.getName();
    Assert.isNotNull(
      RLM_Learning_UserInformation.getTiming(),
      'timing returned'
    );
    RLM_Learning_UserInformation.getExpiryDays();
    // Cover all time-of-day branches deterministically.
    Assert.areEqual(
      'Morning',
      RLM_Learning_UserInformation.timingForHour(9)
    );
    Assert.areEqual(
      'Afternoon',
      RLM_Learning_UserInformation.timingForHour(13)
    );
    Assert.areEqual(
      'Evening',
      RLM_Learning_UserInformation.timingForHour(20)
    );
  }
}
