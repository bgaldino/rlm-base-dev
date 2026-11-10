/**
 * Unit tests for the In-App Learning framework controllers:
 * RLM_Learning_SectionBlockController, RLM_Learning_SectionBlockSequence,
 * RLM_Learning_DynamicLinkHelper, and RLM_Learning_UserInformation.
 *
 * Builds a minimal Page -> Section -> Block graph (with an Icon and a WebPage
 * DynamicLink) and exercises the happy paths plus the input-validation and
 * empty-result guards.
 *
 * The controllers run their queries and DML in USER_MODE. Every call that
 * touches the learning objects runs as a least-privilege "learner" holding only
 * the RLM_Learning permission set, so those calls do not depend on the
 * permissions of whoever runs the suite, and they prove the permission set is
 * enough. The setup-page map (custom metadata), FlowDefinitionView, Network
 * and Organization lookups run as the runner: they touch no learning object,
 * and RLM_Learning grants no access to that metadata, so running them as the
 * learner would test the learner's profile rather than the feature.
 *
 * The learner also owns the test content (as a content author would): with a
 * Public Read/Write sharing model, only a record's owner can delete it, and
 * re-sequencing a section deletes its junction rows.
 */
@IsTest
private class RLM_Learning_FrameworkTest {
  @TestSetup
  static void makeData() {
    User learner = createLearner();
    System.runAs(learner) {
      insertContent();
    }
  }

  static void insertContent() {
    Id sectionTopRt = rtId('RLM_Learning_Section__c', 'Top');
    Id sectionRightRt = rtId('RLM_Learning_Section__c', 'Right');
    Id webPageRt = rtId('RLM_Learning_DynamicLink__c', 'WebPage');

    RLM_Learning_Icon__c icon = new RLM_Learning_Icon__c(
      Name = 'TestIcon',
      RLM_Learning_Size__c = 'small',
      RLM_Learning_Type__c = 'utility:moneybag'
    );
    insert as system icon;

    RLM_Learning_Page__c page = new RLM_Learning_Page__c(
      Name = 'TestHome',
      RLM_Learning_Type__c = 'Home',
      RLM_Learning_Active__c = true
    );
    insert as system page;

    RLM_Learning_DynamicLink__c dl = new RLM_Learning_DynamicLink__c(
      Name = 'Test DynamicLink',
      RecordTypeId = webPageRt,
      RLM_Learning_Identity__c = 'TEST_DYN_LINK',
      RLM_Learning_Link__c = 'https://example.com'
    );
    insert as system dl;

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
    insert as system sec;

    // Second section with no blocks, to exercise the empty-blocks guard.
    RLM_Learning_Section__c secEmpty = new RLM_Learning_Section__c(
      Name = 'Test Empty Section',
      RecordTypeId = sectionRightRt,
      RLM_Learning_Page__c = page.Id,
      RLM_Learning_Active__c = true,
      RLM_Learning_Header__c = 'Empty'
    );
    insert as system secEmpty;

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
    insert as system blk;

    insert as system new RLM_Learning_SectionBlock__c(
      RLM_Learning_Section__c = sec.Id,
      RLM_Learning_Block__c = blk.Id,
      RLM_Learning_Order_Sequence__c = 1
    );
  }

  // ---- Learner user -------------------------------------------------------------

  static String learnerUsername() {
    return 'rlm.learning.tester.' + UserInfo.getOrganizationId() + '@example.com';
  }

  // A Minimum Access user (Standard User where that profile is absent) holding
  // only the feature's permission set.
  static User createLearner() {
    Profile leastPrivileged = [
      SELECT Id
      FROM Profile
      WHERE Name IN ('Minimum Access - Salesforce', 'Standard User')
      ORDER BY Name ASC
      LIMIT 1
    ];
    PermissionSet learning = [SELECT Id FROM PermissionSet WHERE Name = 'RLM_Learning' LIMIT 1];
    User learner = new User(
      ProfileId = leastPrivileged.Id,
      FirstName = 'Learning',
      LastName = 'Tester',
      Email = 'rlm.learning.tester@example.com',
      Username = learnerUsername(),
      Alias = 'rlmlrn',
      TimeZoneSidKey = 'America/Los_Angeles',
      LocaleSidKey = 'en_US',
      EmailEncodingKey = 'UTF-8',
      LanguageLocaleKey = 'en_US'
    );
    // Setup-object DML in its own runAs context avoids MIXED_DML with test data.
    System.runAs(new User(Id = UserInfo.getUserId())) {
      insert as system learner;
      insert as system new PermissionSetAssignment(AssigneeId = learner.Id, PermissionSetId = learning.Id);
    }
    return learner;
  }

  // PRECONDITION for every learner test: the learner's profile grants no
  // access to the learning objects, so what the learner can do comes from the
  // RLM_Learning permission set.
  @IsTest
  static void learnerProfileGrantsNoLearningObjectAccess() {
    User learnerUser = [SELECT Id, ProfileId FROM User WHERE Username = :learnerUsername() LIMIT 1];
    Assert.areEqual(
      0,
      [
        SELECT COUNT()
        FROM ObjectPermissions
        WHERE
          Parent.IsOwnedByProfile = TRUE
          AND Parent.ProfileId = :learnerUser.ProfileId
          AND SobjectType = 'RLM_Learning_Block__c'
          AND PermissionsRead = TRUE
      ],
      'PRECONDITION: the learner profile does not grant Read on RLM_Learning_Block__c.'
    );
    Assert.areEqual(
      1,
      [
        SELECT COUNT()
        FROM PermissionSetAssignment
        WHERE AssigneeId = :learnerUser.Id AND PermissionSet.Name = 'RLM_Learning'
      ],
      'the learner holds the RLM_Learning permission set'
    );
  }

  static User learner() {
    return [SELECT Id, FirstName FROM User WHERE Username = :learnerUsername() LIMIT 1];
  }

  // ---- Data helpers -------------------------------------------------------------
  //
  // Fixture reads and writes on the learning objects are explicitly system mode
  // (WITH SYSTEM_MODE / "as system"): at this API version a plain statement
  // enforces the runner's field access, which would make the suite depend on
  // the runner holding RLM_Learning. Only the calls under test run as the
  // learner.

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
      WITH SYSTEM_MODE
      LIMIT 1
    ];
  }

  static RLM_Learning_Page__c homePage() {
    return [SELECT Id FROM RLM_Learning_Page__c WHERE Name = 'TestHome' WITH SYSTEM_MODE LIMIT 1];
  }

  static RLM_Learning_Block__c testBlock() {
    return [SELECT Id FROM RLM_Learning_Block__c WHERE Name = 'TestBlock' WITH SYSTEM_MODE LIMIT 1];
  }

  static RLM_Learning_DynamicLink__c testLink() {
    return [
      SELECT Id
      FROM RLM_Learning_DynamicLink__c
      WHERE RLM_Learning_Identity__c = 'TEST_DYN_LINK'
      WITH SYSTEM_MODE
      LIMIT 1
    ];
  }

  static RLM_Learning_Block__c newBlock(String name, Boolean active, Id actionId) {
    return new RLM_Learning_Block__c(
      Name = name,
      RLM_Learning_Active__c = active,
      RLM_Learning_Header__c = name + ' header',
      RLM_Learning_Action__c = actionId
    );
  }

  // ---- SectionBlockController: results ----------------------------------------

  @IsTest
  static void getSectionsWithBlocksByType_returnsResolvedGraph() {
    List<Map<String, Object>> res;
    Test.startTest();
    System.runAs(learner()) {
      res = RLM_Learning_SectionBlockController.getSectionsWithBlocksByType('Top', 'Home');
    }
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
    Id pageId = homePage().Id;
    List<Map<String, Object>> res;
    System.runAs(learner()) {
      res = RLM_Learning_SectionBlockController.getSectionsWithBlocksByPageId('Top', pageId);
    }
    Assert.isFalse(res.isEmpty(), 'expected sections by page id');
  }

  @IsTest
  static void getSectionWithBlockBySectionId_happyPath() {
    Id secId = sectionByHeader('H').Id;
    List<Map<String, Object>> res;
    System.runAs(learner()) {
      res = RLM_Learning_SectionBlockController.getSectionWithBlockBySectionId(secId);
    }
    Assert.isFalse(res.isEmpty(), 'expected a result');
    Assert.isNotNull(res[0].get('block'), 'block present');
  }

  @IsTest
  static void getSectionsByType_returnsOnlyActiveSectionsAndBlocks() {
    RLM_Learning_Section__c sec = sectionByHeader('H');
    RLM_Learning_Block__c inactive = newBlock('Inactive Block', false, null);
    insert as system inactive;
    insert as system new RLM_Learning_SectionBlock__c(
      RLM_Learning_Section__c = sec.Id,
      RLM_Learning_Block__c = inactive.Id,
      RLM_Learning_Order_Sequence__c = 2
    );
    insert as system new RLM_Learning_Section__c(
      Name = 'Inactive Top Section',
      RecordTypeId = rtId('RLM_Learning_Section__c', 'Top'),
      RLM_Learning_Page__c = homePage().Id,
      RLM_Learning_Active__c = false,
      RLM_Learning_Header__c = 'Inactive'
    );

    List<RLM_Learning_Section__c> sections;
    Test.startTest();
    System.runAs(learner()) {
      sections = RLM_Learning_SectionBlockController.getSectionsByType('Top', 'Home');
    }
    Test.stopTest();

    Assert.areEqual(1, sections.size(), 'only the active Top section on the Home page');
    Assert.areEqual('H', sections[0].RLM_Learning_Header__c);
    Assert.areEqual('S', sections[0].RLM_Learning_Sub_Header__c);
    Assert.areEqual('utility:moneybag', sections[0].RLM_Learning_Icon__r.RLM_Learning_Type__c);
    Assert.areEqual(1, sections[0].SectionBlocks__r.size(), 'inactive blocks are filtered out');
    Assert.areEqual(
      'BH',
      sections[0].SectionBlocks__r[0].RLM_Learning_Block__r.RLM_Learning_Header__c
    );
  }

  @IsTest
  static void getSectionsWithBlocksByType_mapsBlockFieldsAndLinks() {
    Id linkId = testLink().Id;
    Id blockId = testBlock().Id;

    List<Map<String, Object>> res;
    Test.startTest();
    System.runAs(learner()) {
      res = RLM_Learning_SectionBlockController.getSectionsWithBlocksByType('Top', 'Home');
    }
    Test.stopTest();

    Assert.areEqual(1, res.size(), 'one active Top section');
    RLM_Learning_Section__c section = (RLM_Learning_Section__c) res[0].get('section');
    Assert.areEqual('H', section.RLM_Learning_Header__c);

    List<Map<String, Object>> blocks = (List<Map<String, Object>>) res[0].get('blocks');
    Assert.areEqual(1, blocks.size());
    Map<String, Object> block = blocks[0];
    Assert.areEqual(blockId, block.get('blockId'));
    Assert.areEqual('BH', block.get('header'));
    Assert.areEqual('BS', block.get('subHeader'));
    Assert.areEqual('utility:moneybag', block.get('icon'));
    Assert.areEqual('small', block.get('iconSize'));
    Assert.areEqual(linkId, block.get('action'));
    Assert.areEqual('Go', block.get('actionText'));
    Assert.areEqual('Desc', block.get('description'));

    List<RLM_Learning_DynamicLink__c> links = (List<RLM_Learning_DynamicLink__c>) res[0]
      .get('dynamicLinks');
    Assert.areEqual(1, links.size(), 'the block action resolves to its dynamic link');
    Assert.areEqual(linkId, links[0].Id);
    Assert.areEqual('https://example.com', links[0].RLM_Learning_Link__c);
    Assert.areEqual('WebPage', links[0].RecordType.DeveloperName);
  }

  @IsTest
  static void getSectionsWithBlocksByType_blockWithoutActionHasNoLinks() {
    RLM_Learning_Block__c plain = newBlock('Plain Block', true, null);
    insert as system plain;
    insert as system new RLM_Learning_SectionBlock__c(
      RLM_Learning_Section__c = sectionByHeader('Empty').Id,
      RLM_Learning_Block__c = plain.Id,
      RLM_Learning_Order_Sequence__c = 1
    );

    List<Map<String, Object>> res;
    Test.startTest();
    System.runAs(learner()) {
      res = RLM_Learning_SectionBlockController.getSectionsWithBlocksByType('Right', 'Home');
    }
    Test.stopTest();

    Assert.areEqual(1, res.size(), 'one active Right section');
    List<Map<String, Object>> blocks = (List<Map<String, Object>>) res[0].get('blocks');
    Assert.areEqual(1, blocks.size());
    Assert.isNull(blocks[0].get('action'), 'the block has no action');
    Assert.isNull(blocks[0].get('icon'), 'a block without an icon maps to a null icon');
    Assert.isTrue(
      ((List<RLM_Learning_DynamicLink__c>) res[0].get('dynamicLinks')).isEmpty(),
      'no action means no dynamic links'
    );
  }

  @IsTest
  static void getSectionWithBlockBySectionId_mapsFirstBlockAndLink() {
    Id linkId = testLink().Id;
    Id blockId = testBlock().Id;
    Id secId = sectionByHeader('H').Id;

    List<Map<String, Object>> res;
    Test.startTest();
    System.runAs(learner()) {
      res = RLM_Learning_SectionBlockController.getSectionWithBlockBySectionId(secId);
    }
    Test.stopTest();

    Assert.areEqual(1, res.size());
    Assert.areEqual(
      'H',
      ((RLM_Learning_Section__c) res[0].get('section')).RLM_Learning_Header__c
    );
    Map<String, Object> block = (Map<String, Object>) res[0].get('block');
    Assert.areEqual(blockId, block.get('blockId'));
    Assert.areEqual('BH', block.get('header'));
    Assert.areEqual('small', block.get('iconSize'));
    Assert.areEqual(linkId, block.get('action'));
    List<RLM_Learning_DynamicLink__c> links = (List<RLM_Learning_DynamicLink__c>) res[0]
      .get('dynamicLinks');
    Assert.areEqual(1, links.size());
    Assert.areEqual(linkId, links[0].Id);
  }

  // ---- SectionBlockController: guards -----------------------------------------

  @IsTest
  static void getSectionWithBlockBySectionId_noBlocksThrows() {
    Id emptyId = sectionByHeader('Empty').Id;
    Boolean threw = false;
    System.runAs(learner()) {
      try {
        RLM_Learning_SectionBlockController.getSectionWithBlockBySectionId(emptyId);
      } catch (AuraHandledException e) {
        threw = true;
      }
    }
    Assert.isTrue(threw, 'expected guard exception for a section with no blocks');
  }

  @IsTest
  static void controller_validationErrors() {
    Boolean a = false, b = false, c = false;
    System.runAs(learner()) {
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
    }
    Assert.isTrue(a && b && c, 'each missing-arg call should throw');
  }

  @IsTest
  static void getSectionsByType_requiresExactlyOneActivePage() {
    // Only an inactive Detail page exists: no active page for the type.
    insert as system new RLM_Learning_Page__c(
      Name = 'Inactive Detail',
      RLM_Learning_Type__c = 'Detail',
      RLM_Learning_Active__c = false
    );
    Boolean noActivePage = false;
    System.runAs(learner()) {
      try {
        RLM_Learning_SectionBlockController.getSectionsByType('Top', 'Detail');
      } catch (AuraHandledException e) {
        noActivePage = true;
      }
    }
    Assert.isTrue(noActivePage, 'expected an error when no active page has the type');

    // A second active Home page makes the type ambiguous.
    Integer withOneHomePage;
    System.runAs(learner()) {
      withOneHomePage = RLM_Learning_SectionBlockController.getSectionsByType('Top', 'Home').size();
    }
    Assert.areEqual(1, withOneHomePage, 'PRECONDITION: one active Home page resolves.');
    insert as system new RLM_Learning_Page__c(
      Name = 'Second Home',
      RLM_Learning_Type__c = 'Home',
      RLM_Learning_Active__c = true
    );
    Boolean ambiguous = false;
    System.runAs(learner()) {
      try {
        RLM_Learning_SectionBlockController.getSectionsByType('Top', 'Home');
      } catch (AuraHandledException e) {
        ambiguous = true;
      }
    }
    Assert.isTrue(ambiguous, 'expected an error when two active pages share the type');
  }

  @IsTest
  static void controller_moreValidationErrors() {
    Id pageId = homePage().Id;
    Integer thrown = 0;
    System.runAs(learner()) {
      try {
        RLM_Learning_SectionBlockController.getSectionsByType('Top', '');
      } catch (AuraHandledException e) {
        thrown++;
      }
      try {
        RLM_Learning_SectionBlockController.getSectionsByPageId('', pageId);
      } catch (AuraHandledException e) {
        thrown++;
      }
      try {
        RLM_Learning_SectionBlockController.getSectionsByPageId('Top', 'not-an-id');
      } catch (AuraHandledException e) {
        thrown++;
      }
      try {
        RLM_Learning_SectionBlockController.getSectionWithBlockBySectionId('not-an-id');
      } catch (AuraHandledException e) {
        thrown++;
      }
      try {
        RLM_Learning_SectionBlockController.getSectionsWithBlocksByType('', 'Home');
      } catch (AuraHandledException e) {
        thrown++;
      }
      try {
        RLM_Learning_SectionBlockController.getSectionsWithBlocksByType('Top', '');
      } catch (AuraHandledException e) {
        thrown++;
      }
      try {
        RLM_Learning_SectionBlockController.getSectionsWithBlocksByPageId('', pageId);
      } catch (AuraHandledException e) {
        thrown++;
      }
      try {
        RLM_Learning_SectionBlockController.getSectionsWithBlocksByPageId('Top', '');
      } catch (AuraHandledException e) {
        thrown++;
      }
    }
    Assert.areEqual(8, thrown, 'each blank or malformed argument should throw');
  }

  @IsTest
  static void getSectionWithBlockBySectionId_inactiveSectionThrows() {
    RLM_Learning_Section__c sec = sectionByHeader('H');
    Integer whileActive;
    System.runAs(learner()) {
      whileActive = RLM_Learning_SectionBlockController.getSectionWithBlockBySectionId(sec.Id).size();
    }
    Assert.areEqual(1, whileActive, 'PRECONDITION: the section resolves while it is active.');
    sec.RLM_Learning_Active__c = false;
    update as system sec;
    Boolean threw = false;
    System.runAs(learner()) {
      try {
        RLM_Learning_SectionBlockController.getSectionWithBlockBySectionId(sec.Id);
      } catch (AuraHandledException e) {
        threw = true;
      }
    }
    Assert.isTrue(threw, 'expected an error for an inactive section');
  }

  // ---- SectionBlockSequence ---------------------------------------------------

  @IsTest
  static void sectionBlockSequence_crud() {
    Id secId = sectionByHeader('H').Id;
    Id blockId = testBlock().Id;
    Boolean hasBlocks;
    Integer before;
    Integer after;

    Test.startTest();
    System.runAs(learner()) {
      hasBlocks = !RLM_Learning_SectionBlockSequence.getAllBlocks().isEmpty();
      before = RLM_Learning_SectionBlockSequence.getBlocksForSection(secId).size();
      RLM_Learning_SectionBlockSequence.updateSectionBlocks(secId, new List<String>{ blockId });
      after = RLM_Learning_SectionBlockSequence.getBlocksForSection(secId).size();
    }
    Test.stopTest();

    Assert.isTrue(hasBlocks, 'expected blocks');
    Assert.areEqual(1, before, 'one junction before update');
    Assert.areEqual(1, after, 'still one junction after re-set (no duplicates)');
  }

  @IsTest
  static void getAllBlocks_returnsActiveBlocksInNameOrder() {
    // Inserted out of name order: 'AA Active Block' sorts first but is created last.
    insert as system new List<RLM_Learning_Block__c>{
      newBlock('ZZ Active Block', true, null),
      newBlock('AB Inactive Block', false, null),
      newBlock('AA Active Block', true, null)
    };

    List<RLM_Learning_Block__c> blocks;
    Test.startTest();
    System.runAs(learner()) {
      blocks = RLM_Learning_SectionBlockSequence.getAllBlocks();
    }
    Test.stopTest();

    List<String> names = new List<String>();
    for (RLM_Learning_Block__c b : blocks) {
      names.add(b.Name);
    }
    Assert.areEqual(
      new List<String>{ 'AA Active Block', 'TestBlock', 'ZZ Active Block' },
      names,
      'active blocks only, ordered by name'
    );
  }

  @IsTest
  static void updateSectionBlocks_replacesAndReorders() {
    Id secId = sectionByHeader('H').Id;
    Id firstId = testBlock().Id;
    RLM_Learning_Block__c second = newBlock('Second Block', true, null);
    insert as system second;

    List<RLM_Learning_SectionBlock__c> rows;
    Test.startTest();
    System.runAs(learner()) {
      RLM_Learning_SectionBlockSequence.updateSectionBlocks(
        secId,
        new List<String>{ second.Id, firstId }
      );
      rows = RLM_Learning_SectionBlockSequence.getBlocksForSection(secId);
    }
    Test.stopTest();

    Assert.areEqual(2, rows.size(), 'the old junction is replaced, not duplicated');
    Assert.areEqual(second.Id, rows[0].RLM_Learning_Block__c, 'new first block');
    Assert.areEqual(firstId, rows[1].RLM_Learning_Block__c, 'original block moved second');
    List<RLM_Learning_SectionBlock__c> ordered = [
      SELECT RLM_Learning_Order_Sequence__c
      FROM RLM_Learning_SectionBlock__c
      WHERE RLM_Learning_Section__c = :secId
      WITH SYSTEM_MODE
      ORDER BY RLM_Learning_Order_Sequence__c ASC
    ];
    Assert.areEqual(1, ordered[0].RLM_Learning_Order_Sequence__c.intValue());
    Assert.areEqual(2, ordered[1].RLM_Learning_Order_Sequence__c.intValue());
  }

  @IsTest
  static void updateSectionBlocks_onEmptySection() {
    Id emptyId = sectionByHeader('Empty').Id;
    Id blockId = testBlock().Id;
    Integer afterEmptyList;
    Integer afterAdd;

    Test.startTest();
    System.runAs(learner()) {
      RLM_Learning_SectionBlockSequence.updateSectionBlocks(emptyId, new List<String>());
      afterEmptyList = RLM_Learning_SectionBlockSequence.getBlocksForSection(emptyId).size();
      RLM_Learning_SectionBlockSequence.updateSectionBlocks(emptyId, new List<String>{ blockId });
      afterAdd = RLM_Learning_SectionBlockSequence.getBlocksForSection(emptyId).size();
    }
    Test.stopTest();

    Assert.areEqual(0, afterEmptyList, 'an empty list leaves the section empty');
    Assert.areEqual(1, afterAdd, 'a block can be added to a section that had none');
  }

  @IsTest
  static void updateSectionBlocks_validationErrors() {
    Id secId = sectionByHeader('H').Id;
    Boolean a = false, b = false;
    System.runAs(learner()) {
      try {
        RLM_Learning_SectionBlockSequence.updateSectionBlocks('', new List<String>());
      } catch (AuraHandledException e) {
        a = true;
      }
      try {
        RLM_Learning_SectionBlockSequence.updateSectionBlocks(secId, null);
      } catch (AuraHandledException e) {
        b = true;
      }
    }
    Assert.isTrue(a && b, 'blank sectionId and null blockIds should each throw');
  }

  @IsTest
  static void sectionBlockSequence_moreValidationErrors() {
    Id secId = sectionByHeader('H').Id;
    Integer thrown = 0;
    System.runAs(learner()) {
      try {
        RLM_Learning_SectionBlockSequence.getBlocksForSection('');
      } catch (AuraHandledException e) {
        thrown++;
      }
      try {
        RLM_Learning_SectionBlockSequence.getBlocksForSection('not-an-id');
      } catch (AuraHandledException e) {
        thrown++;
      }
      try {
        RLM_Learning_SectionBlockSequence.updateSectionBlocks('not-an-id', new List<String>());
      } catch (AuraHandledException e) {
        thrown++;
      }
      try {
        RLM_Learning_SectionBlockSequence.updateSectionBlocks(
          secId,
          new List<String>{ 'not-an-id' }
        );
      } catch (AuraHandledException e) {
        thrown++;
      }
      // A well-formed Id of the wrong object fails the insert; the DML error is
      // surfaced as an AuraHandledException. Run last: the delete already ran.
      try {
        RLM_Learning_SectionBlockSequence.updateSectionBlocks(secId, new List<String>{ secId });
      } catch (AuraHandledException e) {
        thrown++;
      }
    }
    Assert.areEqual(5, thrown, 'each malformed or wrong-object Id should throw');
  }

  // ---- DynamicLinkHelper: learning objects (run as the learner) ---------------

  @IsTest
  static void dynamicLinkHelper_happyPaths() {
    RLM_Learning_DynamicLink__c link;
    Integer pages;
    System.runAs(learner()) {
      link = RLM_Learning_DynamicLinkHelper.getDynamicLinkByIdentity('TEST_DYN_LINK');
      pages = RLM_Learning_DynamicLinkHelper.getObjectIdFromQuery(
          'RLM_Learning_Page__c',
          'Name = \'TestHome\''
        )
        .size();
    }
    Assert.isNotNull(link, 'dynamic link by identity');
    Assert.areEqual('https://example.com', link.RLM_Learning_Link__c);
    Assert.areEqual(1, pages, 'object id from query');
  }

  @IsTest
  static void dynamicLinkHelper_guards() {
    Boolean blankObj = false, unknownObj = false, blankSetup = false, badType = false;
    Boolean blankIdentity = false, missingIdentity = false;
    System.runAs(learner()) {
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
        RLM_Learning_DynamicLinkHelper.getObjectIdFromQuery('Not_A_Real_Object__x', 'Id != null');
      } catch (AuraHandledException e) {
        unknownObj = true;
      }
      try {
        RLM_Learning_DynamicLinkHelper.getSetupPageLink('', 'x');
      } catch (AuraHandledException e) {
        blankSetup = true;
      }
      try {
        RLM_Learning_DynamicLinkHelper.getRecordIdFromDynamicLinkType('UnsupportedType', 'Id != null');
      } catch (AuraHandledException e) {
        badType = true;
      }
    }
    Assert.isTrue(
      blankObj && unknownObj && blankSetup && badType && blankIdentity && missingIdentity,
      'each helper guard should throw'
    );
  }

  @IsTest
  static void getObjectIdFromQuery_returnsMatchingIdsAndWrapsQueryErrors() {
    Id pageId = homePage().Id;
    List<SObject> rows;
    Integer thrown = 0;
    System.runAs(learner()) {
      rows = RLM_Learning_DynamicLinkHelper.getObjectIdFromQuery(
        'RLM_Learning_Page__c',
        'RLM_Learning_Type__c = \'Home\''
      );
      try {
        RLM_Learning_DynamicLinkHelper.getObjectIdFromQuery('RLM_Learning_Page__c', '');
      } catch (AuraHandledException e) {
        thrown++;
      }
      try {
        RLM_Learning_DynamicLinkHelper.getObjectIdFromQuery('RLM_Learning_Page__c', 'Name =');
      } catch (AuraHandledException e) {
        thrown++;
      }
    }
    Assert.areEqual(1, rows.size());
    Assert.areEqual(pageId, rows[0].Id);
    Assert.areEqual(2, thrown, 'a blank or malformed where condition should throw');
  }

  // ---- DynamicLinkHelper: setup and platform lookups (no learning objects) -----

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

  @IsTest
  static void getSetupPageLink_buildsUserUrlAndRejectsBadInput() {
    Id userId = UserInfo.getUserId();
    String expected =
      System.Url.getOrgDomainUrl().toExternalForm() +
      '/lightning/setup/ManageUsers/page?address=/' +
      userId +
      '&noredirect=1';
    Assert.areEqual(expected, RLM_Learning_DynamicLinkHelper.getSetupPageLink('User', userId));

    Integer thrown = 0;
    try {
      RLM_Learning_DynamicLinkHelper.getSetupPageLink('User', '');
    } catch (AuraHandledException e) {
      thrown++;
    }
    try {
      RLM_Learning_DynamicLinkHelper.getSetupPageLink('User', 'not-an-id');
    } catch (AuraHandledException e) {
      thrown++;
    }
    try {
      RLM_Learning_DynamicLinkHelper.getSetupPageLink('NoSuchSetupPage', userId);
    } catch (AuraHandledException e) {
      thrown++;
    }
    Assert.areEqual(3, thrown, 'blank, malformed, or unmapped input should throw');
  }

  @IsTest
  static void getRecordIdFromDynamicLinkType_guardsAndFlowLookup() {
    // Flow definitions are metadata, visible in tests; any active, unmanaged
    // one will do (the first by API name, for a stable choice).
    List<FlowDefinitionView> activeFlows = [
      SELECT ApiName, ActiveVersionId
      FROM FlowDefinitionView
      WHERE ActiveVersionId != null AND NamespacePrefix = null
      ORDER BY ApiName
      LIMIT 1
    ];
    Assert.isFalse(activeFlows.isEmpty(), 'PRECONDITION: the org has an active flow.');
    List<SObject> found = RLM_Learning_DynamicLinkHelper.getRecordIdFromDynamicLinkType(
      'FlowRecordPage',
      'ApiName = \'' + String.escapeSingleQuotes(activeFlows[0].ApiName) + '\''
    );
    Assert.areEqual(1, found.size(), 'the named flow is found');
    Assert.areEqual(activeFlows[0].ActiveVersionId, found[0].get('ActiveVersionId'),
      'a FlowRecordPage link resolves to the active version');

    List<SObject> none = RLM_Learning_DynamicLinkHelper.getRecordIdFromDynamicLinkType(
      'FlowRecordPage',
      'ApiName = \'RLM_No_Such_Flow_For_Test\''
    );
    Assert.isTrue(none.isEmpty(), 'no flow has that API name');

    Integer thrown = 0;
    try {
      RLM_Learning_DynamicLinkHelper.getRecordIdFromDynamicLinkType('', 'Id != null');
    } catch (AuraHandledException e) {
      thrown++;
    }
    try {
      RLM_Learning_DynamicLinkHelper.getRecordIdFromDynamicLinkType('FlowRecordPage', '');
    } catch (AuraHandledException e) {
      thrown++;
    }
    Assert.areEqual(2, thrown, 'a blank type or where condition should throw');
  }

  @IsTest
  static void getSiteUrl_rejectsMalformedNetworkId() {
    Boolean threw = false;
    try {
      RLM_Learning_DynamicLinkHelper.getSiteUrl('not-an-id');
    } catch (AuraHandledException e) {
      threw = true;
    }
    Assert.isTrue(threw, 'expected an error for a malformed network id');
  }

  // A well-formed Id with no site behind it is rejected in every org. Where the
  // org also has an Experience Cloud site (only builds with a site feature
  // enabled), that site's base URL is an absolute prefix of its login URL with
  // the "/s/..." login path removed.
  @IsTest
  static void getSiteUrl_rejectsAMissingSite_andTrimsTheLoginPathOfAnExistingOne() {
    Boolean missingRejected = false;
    try {
      RLM_Learning_DynamicLinkHelper.getSiteUrl('0DB000000000001');
    } catch (AuraHandledException e) {
      missingRejected = true;
    }
    Assert.isTrue(missingRejected, 'a network Id with no site behind it is rejected');

    List<Network> networks = [SELECT Id FROM Network LIMIT 1];
    String loginUrl = networks.isEmpty() ? null : Network.getLoginUrl(networks[0].Id);
    if (loginUrl == null) {
      return; // no site in this build: only the rejection above applies
    }

    String siteUrl = RLM_Learning_DynamicLinkHelper.getSiteUrl(networks[0].Id);

    Assert.isTrue(siteUrl.startsWith('http'), 'an absolute URL: ' + siteUrl);
    Assert.isTrue(loginUrl.startsWith(siteUrl), 'a prefix of the login URL: ' + siteUrl);
    Assert.isFalse(siteUrl.contains('/s/'), 'the login path is removed: ' + siteUrl);
  }

  // ---- UserInformation -------------------------------------------------------

  @IsTest
  static void userInformation_paths() {
    // getExpiryDays returns null exactly when the org has no trial expiry, and
    // otherwise a non-negative count no larger than the days left (plus one for
    // a date boundary crossed during the test).
    // (Part-of-day greeting moved to the client; no Apex getTiming/timingForHour.)
    Datetime trialExpiry = [SELECT TrialExpirationDate FROM Organization LIMIT 1].TrialExpirationDate;
    User learnerUser = learner();

    String name;
    Integer expiryDays;
    Test.startTest();
    System.runAs(learnerUser) {
      name = RLM_Learning_UserInformation.getName();
    }
    expiryDays = RLM_Learning_UserInformation.getExpiryDays();
    Test.stopTest();

    Assert.areEqual(learnerUser.FirstName, name, 'greets the running user by first name');
    if (trialExpiry == null) {
      Assert.isNull(expiryDays, 'no trial expiry means no countdown');
    } else {
      Integer upperBound = Math.max(0, Date.today().daysBetween(trialExpiry.date())) + 1;
      Assert.isNotNull(expiryDays, 'a trial expiry yields a countdown');
      Assert.isTrue(expiryDays >= 0, 'never negative: ' + expiryDays);
      Assert.isTrue(expiryDays <= upperBound, 'no more than the days left: ' + expiryDays);
    }
  }
}
