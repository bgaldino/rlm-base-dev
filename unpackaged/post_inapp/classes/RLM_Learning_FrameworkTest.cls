/**
 * Unit tests for the In-App Learning framework controllers:
 * RLM_Learning_SectionBlockController, RLM_Learning_SectionBlockSequence,
 * RLM_Learning_DynamicLinkHelper, and RLM_Learning_UserInformation.
 *
 * Builds a minimal Page -> Section -> Block graph (with an Icon and a WebPage
 * DynamicLink) and exercises the happy paths plus the input-validation and
 * empty-result guards.
 *
 * Who runs what:
 *  - The controllers run their queries and DML in USER_MODE. The behavioural
 *    tests run as the test runner holding the RLM_Learning permission set:
 *    when the runner does not hold it, runnerWithLearning() assigns it in-test
 *    (rolled back with the test) and the calls run in a fresh runAs context so
 *    the grant applies. If the platform refuses that assignment the test fails;
 *    it is never skipped.
 *  - Input guards that throw before any USER_MODE query run as the runner,
 *    whatever the runner holds.
 *  - A separate least-privilege "learner" is a user on the
 *    "Minimum Access - Salesforce" profile (looked up by its English name)
 *    holding only RLM_Learning. learnerCannotResequenceRowsItDoesNotOwn and
 *    userInformation_paths use it, and learnerProfileGrantsNoLearningObjectAccess
 *    checks its profile. In the Apex test context user inserts are not limited
 *    by free seats (observed on a Release 264 org: 22 Minimum Access users
 *    inserted with 12 free seats). The learner is created lazily by learner(),
 *    only in the tests that use it, so a failure to create it affects only
 *    those tests. When it cannot be created (no Minimum Access profile,
 *    RLM_Learning missing, or LICENSE_LIMIT_EXCEEDED on the insert),
 *    learnerCannotResequenceRowsItDoesNotOwn returns early with a WARN
 *    "SKIPPED" debug line, the sentinel skips its assignment check, and
 *    userInformation_paths calls getName as the runner instead. Any other
 *    insert failure is rethrown and fails the test that asked for the learner.
 *
 * The runner owns the test content. Other users read it through the Public
 * Read/Write sharing model; a user can delete only the rows it owns, unless it
 * is above the owner in the role hierarchy or holds Modify All.
 *
 * Pinned known gaps:
 *  - Ownership. Re-sequencing a section deletes its junction rows, so a user
 *    who does not own them (for example a learner, for content an admin
 *    loaded) cannot re-sequence that section;
 *    learnerCannotResequenceRowsItDoesNotOwn pins this.
 *
 * Not covered here:
 *  - The learner's read access to Page, Section, Block, Icon and DynamicLink.
 *    The read-path tests run as the runner (normally an admin) plus
 *    RLM_Learning, and View/Modify All Data already supply object Read, so
 *    they do not prove RLM_Learning alone is enough to read the content.
 *  - Setup lookups. The setup-page map (custom metadata), FlowDefinitionView,
 *    Network and Organization lookups run as the runner here. In production
 *    they run as the learner, and RLM_Learning grants no custom-metadata-type
 *    access, so the learner's access to them is not tested.
 */
@IsTest
private class RLM_Learning_FrameworkTest {
  @TestSetup
  static void makeData() {
    insertContent();
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

  // ---- Runner with RLM_Learning -------------------------------------------------

  // The running user, holding RLM_Learning: assigned here (and rolled back with
  // the test) when it is not already held. Run the calls under test inside
  // System.runAs(<this user>) so the in-test assignment is in effect. A refused
  // assignment fails the test with the platform's status code.
  static User runnerWithLearning() {
    List<PermissionSet> sets = [SELECT Id FROM PermissionSet WHERE Name = 'RLM_Learning' LIMIT 1];
    Assert.isFalse(sets.isEmpty(), 'PRECONDITION: the RLM_Learning permission set ships in this bundle.');
    Id me = UserInfo.getUserId();
    Id setId = sets[0].Id;
    if ([SELECT COUNT() FROM PermissionSetAssignment WHERE AssigneeId = :me AND PermissionSetId = :setId] == 0) {
      Database.SaveResult saved;
      System.runAs(new User(Id = me)) {
        saved = Database.insert(
          new PermissionSetAssignment(AssigneeId = me, PermissionSetId = setId),
          false,
          AccessLevel.SYSTEM_MODE
        );
      }
      if (!saved.isSuccess()) {
        Database.Error error = saved.getErrors()[0];
        Assert.fail(
          'RLM_Learning could not be assigned to the running user: ' +
          error.getStatusCode() + ' ' + error.getMessage()
        );
      }
    }
    return new User(Id = me);
  }

  // ---- Least-privilege learner ----------------------------------------------------

  // Fixed marker the tests find the learner by (with its RLM_Learning
  // assignment). The username itself is random, so concurrent runs of this
  // class cannot collide on DUPLICATE_USERNAME.
  static final String LEARNER_LAST_NAME = 'RLMLearningTestLearner';
  static final String LEARNER_ALIAS = 'rlmlrn';

  static List<Profile> minimumAccessProfile() {
    return [SELECT Id FROM Profile WHERE Name = 'Minimum Access - Salesforce' LIMIT 1];
  }

  // A Minimum Access user holding only the feature's permission set, or nothing
  // when the profile or permission set is missing or the platform reports
  // LICENSE_LIMIT_EXCEEDED. Any other insert failure is rethrown. Never a
  // broader profile: the sentinel test proves this profile grants nothing on
  // the learning objects.
  static void createLearner() {
    List<Profile> profiles = minimumAccessProfile();
    List<PermissionSet> sets = [SELECT Id FROM PermissionSet WHERE Name = 'RLM_Learning' LIMIT 1];
    if (profiles.isEmpty() || sets.isEmpty()) {
      return;
    }
    User learner = new User(
      ProfileId = profiles[0].Id,
      FirstName = 'Learning',
      LastName = LEARNER_LAST_NAME,
      // The runner's own address, so an Allowed Email Domains list cannot
      // reject the insert; the username stays random.
      Email = UserInfo.getUserEmail(),
      Username = 'rlm.learning.tester.' + String.valueOf(Crypto.getRandomInteger()).remove('-') +
        '.' + UserInfo.getOrganizationId() + '@example.com',
      Alias = LEARNER_ALIAS,
      TimeZoneSidKey = 'America/Los_Angeles',
      LocaleSidKey = 'en_US',
      EmailEncodingKey = 'UTF-8',
      LanguageLocaleKey = 'en_US'
    );
    // Setup-object DML in its own runAs context avoids MIXED_DML with test data.
    // Both inserts succeed or neither stays, so no learner exists without its
    // permission set.
    System.runAs(new User(Id = UserInfo.getUserId())) {
      Savepoint beforeLearner = Database.setSavepoint();
      try {
        insert as system learner;
        insert as system new PermissionSetAssignment(AssigneeId = learner.Id, PermissionSetId = sets[0].Id);
      } catch (DmlException e) {
        Database.rollback(beforeLearner);
        if (e.getDmlType(0) != StatusCode.LICENSE_LIMIT_EXCEEDED) {
          throw e;
        }
      }
    }
  }

  // The learner, created on first use in this test, or null (with a WARN
  // "SKIPPED" line) when it cannot be created.
  // Also null (with a WARN) when the learner holds permission sets beyond
  // RLM_Learning, for example through org automation, because it would no
  // longer be least-privilege.
  static User learner() {
    User found = findLearner();
    if (found == null) {
      createLearner();
      found = findLearner();
    }
    if (found == null) {
      System.debug(
        LoggingLevel.WARN,
        'SKIPPED: least-privilege learner could not be created (no Minimum Access profile, ' +
        'RLM_Learning missing, or LICENSE_LIMIT_EXCEEDED on the user insert)'
      );
      return null;
    }
    Id learnerId = found.Id;
    Integer sets = [
      SELECT COUNT()
      FROM PermissionSetAssignment
      WHERE AssigneeId = :learnerId AND PermissionSet.IsOwnedByProfile = FALSE
    ];
    if (sets != 1) {
      System.debug(LoggingLevel.WARN, 'SKIPPED: the learner holds permission sets beyond RLM_Learning');
      return null;
    }
    return found;
  }

  // Found by its fixed markers only, so the sentinel can catch a learner that
  // is missing its RLM_Learning assignment.
  static User findLearner() {
    List<User> found = [
      SELECT Id, FirstName, ProfileId
      FROM User
      WHERE LastName = :LEARNER_LAST_NAME AND Alias = :LEARNER_ALIAS
      LIMIT 1
    ];
    return found.isEmpty() ? null : found[0];
  }

  // Every custom object the learning content is stored in.
  static final List<String> LEARNING_OBJECTS = new List<String>{
    'RLM_Learning_Block__c',
    'RLM_Learning_DynamicLink__c',
    'RLM_Learning_Icon__c',
    'RLM_Learning_Page__c',
    'RLM_Learning_Section__c',
    'RLM_Learning_SectionBlock__c'
  };

  // Sentinel for the learner tests: the Minimum Access profile grants no access
  // to any learning object and cannot view or modify all data, so what the
  // learner can do comes from the RLM_Learning permission set. The profile is
  // checked directly; the assignment check needs the learner.
  @IsTest
  static void learnerProfileGrantsNoLearningObjectAccess() {
    List<Profile> profiles = minimumAccessProfile();
    if (profiles.isEmpty()) {
      System.debug(LoggingLevel.WARN, 'SKIPPED: no Minimum Access - Salesforce profile in this org');
      return;
    }
    Id profileId = profiles[0].Id;
    Profile profile = [
      SELECT PermissionsViewAllData, PermissionsModifyAllData
      FROM Profile
      WHERE Id = :profileId
    ];
    Assert.isFalse(profile.PermissionsViewAllData, 'PRECONDITION: the learner profile cannot View All Data.');
    Assert.isFalse(profile.PermissionsModifyAllData, 'PRECONDITION: the learner profile cannot Modify All Data.');

    List<String> granted = new List<String>();
    for (ObjectPermissions op : [
      SELECT SobjectType, PermissionsRead, PermissionsCreate, PermissionsEdit, PermissionsDelete
      FROM ObjectPermissions
      WHERE
        Parent.IsOwnedByProfile = TRUE
        AND Parent.ProfileId = :profileId
        AND SobjectType IN :LEARNING_OBJECTS
    ]) {
      if (op.PermissionsRead || op.PermissionsCreate || op.PermissionsEdit || op.PermissionsDelete) {
        granted.add(
          op.SobjectType + ' (R=' + op.PermissionsRead + ' C=' + op.PermissionsCreate +
          ' E=' + op.PermissionsEdit + ' D=' + op.PermissionsDelete + ')'
        );
      }
    }
    Assert.isTrue(
      granted.isEmpty(),
      'PRECONDITION: the learner profile grants no learning-object access; granted: ' + granted
    );

    // learner() creates the learner; it is read back with findLearner() so a
    // learner missing its RLM_Learning assignment fails here rather than
    // being skipped by learner()'s own assignment check.
    learner();
    User learnerUser = findLearner();
    if (learnerUser == null) {
      return; // assignment check skipped visibly: see learner()
    }
    Assert.areEqual(profileId, learnerUser.ProfileId, 'the learner is on the Minimum Access profile');
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

  // ---- Data helpers -------------------------------------------------------------
  //
  // Fixture reads and writes on the learning objects are explicitly system mode
  // (WITH SYSTEM_MODE / "as system"). Observed on an API 68.0 org: with these
  // statements written plainly and the runner not holding RLM_Learning, 14 of
  // 29 tests failed, every one in a fixture statement, with "No such column
  // 'RLM_Learning_Header__c' on entity 'RLM_Learning_Section__c'" or
  // "Operation failed due to fields being inaccessible on Sobject
  // RLM_Learning_Block__c". Only the calls under test run with the grant.

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
    User runner = runnerWithLearning();
    List<Map<String, Object>> res;
    Test.startTest();
    System.runAs(runner) {
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
    User runner = runnerWithLearning();
    Id pageId = homePage().Id;
    List<Map<String, Object>> res;
    System.runAs(runner) {
      res = RLM_Learning_SectionBlockController.getSectionsWithBlocksByPageId('Top', pageId);
    }
    Assert.areEqual(1, res.size(), 'one active Top section on the page');
    Assert.areEqual('H', ((RLM_Learning_Section__c) res[0].get('section')).RLM_Learning_Header__c);
  }

  @IsTest
  static void getSectionWithBlockBySectionId_happyPath() {
    User runner = runnerWithLearning();
    Id secId = sectionByHeader('H').Id;
    List<Map<String, Object>> res;
    System.runAs(runner) {
      res = RLM_Learning_SectionBlockController.getSectionWithBlockBySectionId(secId);
    }
    Assert.isFalse(res.isEmpty(), 'expected a result');
    Assert.isNotNull(res[0].get('block'), 'block present');
  }

  @IsTest
  static void getSectionsByType_returnsOnlyActiveSectionsAndBlocks() {
    User runner = runnerWithLearning();
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
    System.runAs(runner) {
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
    User runner = runnerWithLearning();
    Id linkId = testLink().Id;
    Id blockId = testBlock().Id;

    List<Map<String, Object>> res;
    Test.startTest();
    System.runAs(runner) {
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
    User runner = runnerWithLearning();
    RLM_Learning_Block__c plain = newBlock('Plain Block', true, null);
    insert as system plain;
    insert as system new RLM_Learning_SectionBlock__c(
      RLM_Learning_Section__c = sectionByHeader('Empty').Id,
      RLM_Learning_Block__c = plain.Id,
      RLM_Learning_Order_Sequence__c = 1
    );

    List<Map<String, Object>> res;
    Test.startTest();
    System.runAs(runner) {
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
    User runner = runnerWithLearning();
    Id linkId = testLink().Id;
    Id blockId = testBlock().Id;
    Id secId = sectionByHeader('H').Id;

    List<Map<String, Object>> res;
    Test.startTest();
    System.runAs(runner) {
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
    User runner = runnerWithLearning();
    Id emptyId = sectionByHeader('Empty').Id;
    Id pageId = homePage().Id;
    List<RLM_Learning_Section__c> rightSections;
    Boolean threw = false;
    System.runAs(runner) {
      rightSections = RLM_Learning_SectionBlockController.getSectionsByPageId('Right', pageId);
      try {
        RLM_Learning_SectionBlockController.getSectionWithBlockBySectionId(emptyId);
      } catch (AuraHandledException e) {
        threw = true;
      }
    }
    // PRECONDITION: the section is readable, active and has no blocks, so only
    // the no-blocks exit can explain the error.
    Assert.areEqual(1, rightSections.size(), 'PRECONDITION: one active Right section.');
    Assert.areEqual(emptyId, rightSections[0].Id, 'PRECONDITION: it is the Empty section.');
    Assert.isTrue(rightSections[0].SectionBlocks__r.isEmpty(), 'PRECONDITION: it has no blocks.');
    Assert.isTrue(threw, 'expected guard exception for a section with no blocks');
  }

  // Input guards that throw before any USER_MODE query, so they run as the
  // runner, whatever the runner holds. Each call must throw without running a
  // query. The getSectionsWithBlocksBy* wrappers repeat the guards of the
  // method they delegate to, so a failure there means both the wrapper's guard
  // and the delegated method's guard stopped throwing; removing the wrapper's
  // guard alone is not detectable here.
  @IsTest
  static void controller_validationErrors() {
    Id pageId = homePage().Id;
    List<String> notThrown = new List<String>();
    List<String> afterQuery = new List<String>();
    Integer queries;
    queries = Limits.getQueries();
    try {
      RLM_Learning_SectionBlockController.getSectionsByType('', 'Home');
      notThrown.add('getSectionsByType(blank type)');
    } catch (AuraHandledException e) {
      if (Limits.getQueries() != queries) {
        afterQuery.add('getSectionsByType(blank type)');
      }
    }
    queries = Limits.getQueries();
    try {
      RLM_Learning_SectionBlockController.getSectionsByType('Top', '');
      notThrown.add('getSectionsByType(blank page type)');
    } catch (AuraHandledException e) {
      if (Limits.getQueries() != queries) {
        afterQuery.add('getSectionsByType(blank page type)');
      }
    }
    queries = Limits.getQueries();
    try {
      RLM_Learning_SectionBlockController.getSectionsByPageId('', pageId);
      notThrown.add('getSectionsByPageId(blank type)');
    } catch (AuraHandledException e) {
      if (Limits.getQueries() != queries) {
        afterQuery.add('getSectionsByPageId(blank type)');
      }
    }
    queries = Limits.getQueries();
    try {
      RLM_Learning_SectionBlockController.getSectionsByPageId('Top', '');
      notThrown.add('getSectionsByPageId(blank page id)');
    } catch (AuraHandledException e) {
      if (Limits.getQueries() != queries) {
        afterQuery.add('getSectionsByPageId(blank page id)');
      }
    }
    queries = Limits.getQueries();
    try {
      RLM_Learning_SectionBlockController.getSectionsByPageId('Top', 'not-an-id');
      notThrown.add('getSectionsByPageId(malformed page id)');
    } catch (AuraHandledException e) {
      if (Limits.getQueries() != queries) {
        afterQuery.add('getSectionsByPageId(malformed page id)');
      }
    }
    queries = Limits.getQueries();
    try {
      RLM_Learning_SectionBlockController.getSectionWithBlockBySectionId('');
      notThrown.add('getSectionWithBlockBySectionId(blank id)');
    } catch (AuraHandledException e) {
      if (Limits.getQueries() != queries) {
        afterQuery.add('getSectionWithBlockBySectionId(blank id)');
      }
    }
    queries = Limits.getQueries();
    try {
      RLM_Learning_SectionBlockController.getSectionWithBlockBySectionId('not-an-id');
      notThrown.add('getSectionWithBlockBySectionId(malformed id)');
    } catch (AuraHandledException e) {
      if (Limits.getQueries() != queries) {
        afterQuery.add('getSectionWithBlockBySectionId(malformed id)');
      }
    }
    queries = Limits.getQueries();
    try {
      RLM_Learning_SectionBlockController.getSectionsWithBlocksByType('', 'Home');
      notThrown.add('getSectionsWithBlocksByType(blank type)');
    } catch (AuraHandledException e) {
      if (Limits.getQueries() != queries) {
        afterQuery.add('getSectionsWithBlocksByType(blank type)');
      }
    }
    queries = Limits.getQueries();
    try {
      RLM_Learning_SectionBlockController.getSectionsWithBlocksByType('Top', '');
      notThrown.add('getSectionsWithBlocksByType(blank page type)');
    } catch (AuraHandledException e) {
      if (Limits.getQueries() != queries) {
        afterQuery.add('getSectionsWithBlocksByType(blank page type)');
      }
    }
    queries = Limits.getQueries();
    try {
      RLM_Learning_SectionBlockController.getSectionsWithBlocksByPageId('', pageId);
      notThrown.add('getSectionsWithBlocksByPageId(blank type)');
    } catch (AuraHandledException e) {
      if (Limits.getQueries() != queries) {
        afterQuery.add('getSectionsWithBlocksByPageId(blank type)');
      }
    }
    queries = Limits.getQueries();
    try {
      RLM_Learning_SectionBlockController.getSectionsWithBlocksByPageId('Top', '');
      notThrown.add('getSectionsWithBlocksByPageId(blank page id)');
    } catch (AuraHandledException e) {
      if (Limits.getQueries() != queries) {
        afterQuery.add('getSectionsWithBlocksByPageId(blank page id)');
      }
    }
    Assert.isTrue(notThrown.isEmpty(), 'these calls did not throw: ' + notThrown);
    Assert.isTrue(afterQuery.isEmpty(), 'these calls threw only after running a query: ' + afterQuery);
  }

  @IsTest
  static void getSectionsByType_requiresExactlyOneActivePage() {
    User runner = runnerWithLearning();
    // Only an inactive Detail page exists: no active page for the type.
    insert as system new RLM_Learning_Page__c(
      Name = 'Inactive Detail',
      RLM_Learning_Type__c = 'Detail',
      RLM_Learning_Active__c = false
    );
    Boolean noActivePage = false;
    System.runAs(runner) {
      try {
        RLM_Learning_SectionBlockController.getSectionsByType('Top', 'Detail');
      } catch (AuraHandledException e) {
        noActivePage = true;
      }
    }
    Assert.isTrue(noActivePage, 'expected an error when no active page has the type');

    // A second active Home page makes the type ambiguous.
    Integer withOneHomePage;
    System.runAs(runner) {
      withOneHomePage = RLM_Learning_SectionBlockController.getSectionsByType('Top', 'Home').size();
    }
    Assert.areEqual(1, withOneHomePage, 'PRECONDITION: one active Home page resolves.');
    insert as system new RLM_Learning_Page__c(
      Name = 'Second Home',
      RLM_Learning_Type__c = 'Home',
      RLM_Learning_Active__c = true
    );
    Boolean ambiguous = false;
    System.runAs(runner) {
      try {
        RLM_Learning_SectionBlockController.getSectionsByType('Top', 'Home');
      } catch (AuraHandledException e) {
        ambiguous = true;
      }
    }
    Assert.isTrue(ambiguous, 'expected an error when two active pages share the type');
  }

  @IsTest
  static void getSectionWithBlockBySectionId_inactiveSectionThrows() {
    User runner = runnerWithLearning();
    RLM_Learning_Section__c sec = sectionByHeader('H');
    Integer whileActive;
    System.runAs(runner) {
      whileActive = RLM_Learning_SectionBlockController.getSectionWithBlockBySectionId(sec.Id).size();
    }
    Assert.areEqual(1, whileActive, 'PRECONDITION: the section resolves while it is active.');
    sec.RLM_Learning_Active__c = false;
    update as system sec;
    Boolean threw = false;
    System.runAs(runner) {
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
    User runner = runnerWithLearning();
    Id secId = sectionByHeader('H').Id;
    Id blockId = testBlock().Id;
    Boolean hasBlocks;
    Integer before;
    Integer after;

    Test.startTest();
    System.runAs(runner) {
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
    User runner = runnerWithLearning();
    // Inserted out of name order: 'AA Active Block' sorts first but is created last.
    insert as system new List<RLM_Learning_Block__c>{
      newBlock('ZZ Active Block', true, null),
      newBlock('AB Inactive Block', false, null),
      newBlock('AA Active Block', true, null)
    };

    List<RLM_Learning_Block__c> blocks;
    Test.startTest();
    System.runAs(runner) {
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
    User runner = runnerWithLearning();
    Id secId = sectionByHeader('H').Id;
    Id firstId = testBlock().Id;
    RLM_Learning_Block__c second = newBlock('Second Block', true, null);
    insert as system second;

    List<RLM_Learning_SectionBlock__c> rows;
    Test.startTest();
    System.runAs(runner) {
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
    User runner = runnerWithLearning();
    Id populatedId = sectionByHeader('H').Id;
    Id emptyId = sectionByHeader('Empty').Id;
    Id blockId = testBlock().Id;
    Integer beforeClearing;
    Integer afterClearing;
    Integer afterAdd;

    Test.startTest();
    System.runAs(runner) {
      beforeClearing = RLM_Learning_SectionBlockSequence.getBlocksForSection(populatedId).size();
      RLM_Learning_SectionBlockSequence.updateSectionBlocks(populatedId, new List<String>());
      afterClearing = RLM_Learning_SectionBlockSequence.getBlocksForSection(populatedId).size();
      RLM_Learning_SectionBlockSequence.updateSectionBlocks(emptyId, new List<String>{ blockId });
      afterAdd = RLM_Learning_SectionBlockSequence.getBlocksForSection(emptyId).size();
    }
    Test.stopTest();

    Assert.areEqual(1, beforeClearing, 'PRECONDITION: the section has a row before it is cleared.');
    Assert.areEqual(0, afterClearing, 'an empty list removes every row from the section');
    Assert.areEqual(1, afterAdd, 'a block can be added to a section that had none');
  }

  // Input guards that throw before any USER_MODE query or DML, so they run as
  // the runner, whatever the runner holds. Each call must throw without running
  // a query.
  @IsTest
  static void sectionBlockSequence_validationErrors() {
    Id secId = sectionByHeader('H').Id;
    List<String> notThrown = new List<String>();
    List<String> afterQuery = new List<String>();
    Integer queries;
    queries = Limits.getQueries();
    try {
      RLM_Learning_SectionBlockSequence.getBlocksForSection('');
      notThrown.add('getBlocksForSection(blank id)');
    } catch (AuraHandledException e) {
      if (Limits.getQueries() != queries) {
        afterQuery.add('getBlocksForSection(blank id)');
      }
    }
    queries = Limits.getQueries();
    try {
      RLM_Learning_SectionBlockSequence.getBlocksForSection('not-an-id');
      notThrown.add('getBlocksForSection(malformed id)');
    } catch (AuraHandledException e) {
      if (Limits.getQueries() != queries) {
        afterQuery.add('getBlocksForSection(malformed id)');
      }
    }
    queries = Limits.getQueries();
    try {
      RLM_Learning_SectionBlockSequence.updateSectionBlocks('', new List<String>());
      notThrown.add('updateSectionBlocks(blank section id)');
    } catch (AuraHandledException e) {
      if (Limits.getQueries() != queries) {
        afterQuery.add('updateSectionBlocks(blank section id)');
      }
    }
    queries = Limits.getQueries();
    try {
      RLM_Learning_SectionBlockSequence.updateSectionBlocks(secId, null);
      notThrown.add('updateSectionBlocks(null block ids)');
    } catch (AuraHandledException e) {
      if (Limits.getQueries() != queries) {
        afterQuery.add('updateSectionBlocks(null block ids)');
      }
    }
    queries = Limits.getQueries();
    try {
      RLM_Learning_SectionBlockSequence.updateSectionBlocks('not-an-id', new List<String>());
      notThrown.add('updateSectionBlocks(malformed section id)');
    } catch (AuraHandledException e) {
      if (Limits.getQueries() != queries) {
        afterQuery.add('updateSectionBlocks(malformed section id)');
      }
    }
    queries = Limits.getQueries();
    try {
      RLM_Learning_SectionBlockSequence.updateSectionBlocks(secId, new List<String>{ 'not-an-id' });
      notThrown.add('updateSectionBlocks(malformed block id)');
    } catch (AuraHandledException e) {
      if (Limits.getQueries() != queries) {
        afterQuery.add('updateSectionBlocks(malformed block id)');
      }
    }
    Assert.isTrue(notThrown.isEmpty(), 'these calls did not throw: ' + notThrown);
    Assert.isTrue(afterQuery.isEmpty(), 'these calls threw only after running a query: ' + afterQuery);
  }

  // A well-formed Id of the wrong object reaches the insert, which fails; the
  // DML error is surfaced as an AuraHandledException. The same call with a
  // valid block Id succeeds first, so only the wrong-object Id explains it.
  @IsTest
  static void updateSectionBlocks_rejectsAnIdOfTheWrongObject() {
    User runner = runnerWithLearning();
    Id secId = sectionByHeader('H').Id;
    Id blockId = testBlock().Id;
    Boolean threw = false;
    Integer withValidBlock;
    System.runAs(runner) {
      RLM_Learning_SectionBlockSequence.updateSectionBlocks(secId, new List<String>{ blockId });
      withValidBlock = RLM_Learning_SectionBlockSequence.getBlocksForSection(secId).size();
      try {
        RLM_Learning_SectionBlockSequence.updateSectionBlocks(secId, new List<String>{ secId });
      } catch (AuraHandledException e) {
        threw = true;
      }
    }
    Assert.areEqual(1, withValidBlock, 'PRECONDITION: the same call with a valid block Id succeeds.');
    Assert.isTrue(threw, 'a section Id passed as a block Id should fail the insert');
  }

  // Known gap: re-sequencing deletes the section's junction rows in USER_MODE,
  // and with a Public Read/Write sharing model only a row's owner can delete
  // it. A learner therefore cannot re-sequence a section whose rows someone
  // else (here the runner, as an admin load would) created.
  @IsTest
  static void learnerCannotResequenceRowsItDoesNotOwn() {
    User learnerUser = learner();
    if (learnerUser == null) {
      return; // skipped visibly: see learner()
    }
    Id emptyId = sectionByHeader('Empty').Id;
    Id blockId = testBlock().Id;
    RLM_Learning_SectionBlock__c othersRow = new RLM_Learning_SectionBlock__c(
      RLM_Learning_Section__c = emptyId,
      RLM_Learning_Block__c = blockId,
      RLM_Learning_Order_Sequence__c = 1
    );
    insert as system othersRow;
    Assert.areNotEqual(
      learnerUser.Id,
      [SELECT OwnerId FROM RLM_Learning_SectionBlock__c WHERE Id = :othersRow.Id WITH SYSTEM_MODE].OwnerId,
      'PRECONDITION: the learner does not own the existing row.'
    );

    Test.startTest();
    System.runAs(learnerUser) {
      try {
        RLM_Learning_SectionBlockSequence.updateSectionBlocks(emptyId, new List<String>{ blockId });
        Assert.fail(
          'Known gap: updateSectionBlocks throws an AuraHandledException when the learner does not own ' +
          'the section\'s junction rows; update this test when it is fixed.'
        );
      } catch (AuraHandledException e) {
        // Expected today. The row count and the ownership control below are the
        // evidence that ownership, and nothing else, blocked the call.
      }
    }
    Test.stopTest();

    Assert.areEqual(
      1,
      [SELECT COUNT() FROM RLM_Learning_SectionBlock__c WHERE RLM_Learning_Section__c = :emptyId WITH SYSTEM_MODE],
      'the failed re-sequence leaves the existing row in place'
    );

    // Control: once the learner owns the same row, the same call succeeds, so
    // ownership is what blocked it.
    update as system new RLM_Learning_SectionBlock__c(Id = othersRow.Id, OwnerId = learnerUser.Id);
    System.runAs(learnerUser) {
      RLM_Learning_SectionBlockSequence.updateSectionBlocks(emptyId, new List<String>{ blockId });
    }
    List<RLM_Learning_SectionBlock__c> after = [
      SELECT Id, RLM_Learning_Block__c
      FROM RLM_Learning_SectionBlock__c
      WHERE RLM_Learning_Section__c = :emptyId
      WITH SYSTEM_MODE
    ];
    Assert.areEqual(1, after.size(), 'the owner re-sequences the section');
    Assert.areNotEqual(othersRow.Id, after[0].Id, 'the old row was replaced');
    Assert.areEqual(blockId, after[0].RLM_Learning_Block__c);
  }

  // ---- DynamicLinkHelper: learning objects ------------------------------------

  @IsTest
  static void dynamicLinkHelper_happyPaths() {
    User runner = runnerWithLearning();
    RLM_Learning_DynamicLink__c link;
    Integer pages;
    System.runAs(runner) {
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

  // Input guards that throw before any USER_MODE query, so they run as the
  // runner, whatever the runner holds. Each call must throw, and all but the
  // getSetupPageLink calls must throw without running a query. getSetupPageLink
  // only queries custom metadata with no long-text fields, which
  // Limits.getQueries() does not count, so for it the query check could never
  // fail; those calls are plain must-throw checks.
  @IsTest
  static void dynamicLinkHelper_guards() {
    List<String> notThrown = new List<String>();
    List<String> afterQuery = new List<String>();
    Integer queries;
    queries = Limits.getQueries();
    try {
      RLM_Learning_DynamicLinkHelper.getDynamicLinkByIdentity('');
      notThrown.add('getDynamicLinkByIdentity(blank)');
    } catch (AuraHandledException e) {
      if (Limits.getQueries() != queries) {
        afterQuery.add('getDynamicLinkByIdentity(blank)');
      }
    }
    queries = Limits.getQueries();
    try {
      RLM_Learning_DynamicLinkHelper.getObjectIdFromQuery('', '');
      notThrown.add('getObjectIdFromQuery(blank object)');
    } catch (AuraHandledException e) {
      if (Limits.getQueries() != queries) {
        afterQuery.add('getObjectIdFromQuery(blank object)');
      }
    }
    queries = Limits.getQueries();
    try {
      RLM_Learning_DynamicLinkHelper.getObjectIdFromQuery('RLM_Learning_Page__c', '');
      notThrown.add('getObjectIdFromQuery(blank where)');
    } catch (AuraHandledException e) {
      if (Limits.getQueries() != queries) {
        afterQuery.add('getObjectIdFromQuery(blank where)');
      }
    }
    queries = Limits.getQueries();
    try {
      RLM_Learning_DynamicLinkHelper.getObjectIdFromQuery('Not_A_Real_Object__x', 'Id != null');
      notThrown.add('getObjectIdFromQuery(unknown object)');
    } catch (AuraHandledException e) {
      if (Limits.getQueries() != queries) {
        afterQuery.add('getObjectIdFromQuery(unknown object)');
      }
    }
    try {
      RLM_Learning_DynamicLinkHelper.getSetupPageLink('', 'x');
      notThrown.add('getSetupPageLink(blank page)');
    } catch (AuraHandledException e) {
      // expected
    }
    try {
      RLM_Learning_DynamicLinkHelper.getSetupPageLink('User', '');
      notThrown.add('getSetupPageLink(blank record id)');
    } catch (AuraHandledException e) {
      // expected
    }
    try {
      RLM_Learning_DynamicLinkHelper.getSetupPageLink('User', 'not-an-id');
      notThrown.add('getSetupPageLink(malformed record id)');
    } catch (AuraHandledException e) {
      // expected
    }
    queries = Limits.getQueries();
    try {
      RLM_Learning_DynamicLinkHelper.getRecordIdFromDynamicLinkType('UnsupportedType', 'Id != null');
      notThrown.add('getRecordIdFromDynamicLinkType(unsupported type)');
    } catch (AuraHandledException e) {
      if (Limits.getQueries() != queries) {
        afterQuery.add('getRecordIdFromDynamicLinkType(unsupported type)');
      }
    }
    queries = Limits.getQueries();
    try {
      RLM_Learning_DynamicLinkHelper.getRecordIdFromDynamicLinkType('', 'Id != null');
      notThrown.add('getRecordIdFromDynamicLinkType(blank type)');
    } catch (AuraHandledException e) {
      if (Limits.getQueries() != queries) {
        afterQuery.add('getRecordIdFromDynamicLinkType(blank type)');
      }
    }
    queries = Limits.getQueries();
    try {
      RLM_Learning_DynamicLinkHelper.getRecordIdFromDynamicLinkType('FlowRecordPage', '');
      notThrown.add('getRecordIdFromDynamicLinkType(blank where)');
    } catch (AuraHandledException e) {
      if (Limits.getQueries() != queries) {
        afterQuery.add('getRecordIdFromDynamicLinkType(blank where)');
      }
    }
    Assert.isTrue(notThrown.isEmpty(), 'these calls did not throw: ' + notThrown);
    Assert.isTrue(afterQuery.isEmpty(), 'these calls threw only after running a query: ' + afterQuery);
  }

  // An unknown identity reaches the USER_MODE query, so it runs with the grant.
  @IsTest
  static void getDynamicLinkByIdentity_rejectsAnUnknownIdentity() {
    User runner = runnerWithLearning();
    Boolean missingIdentity = false;
    System.runAs(runner) {
      try {
        RLM_Learning_DynamicLinkHelper.getDynamicLinkByIdentity('NO_SUCH_IDENTITY');
      } catch (AuraHandledException e) {
        missingIdentity = true;
      }
    }
    Assert.isTrue(missingIdentity, 'an identity with no dynamic link should throw');
  }

  @IsTest
  static void getObjectIdFromQuery_returnsMatchingIdsAndWrapsQueryErrors() {
    User runner = runnerWithLearning();
    Id pageId = homePage().Id;
    List<SObject> rows;
    Boolean malformedThrew = false;
    System.runAs(runner) {
      rows = RLM_Learning_DynamicLinkHelper.getObjectIdFromQuery(
        'RLM_Learning_Page__c',
        'RLM_Learning_Type__c = \'Home\''
      );
      try {
        RLM_Learning_DynamicLinkHelper.getObjectIdFromQuery('RLM_Learning_Page__c', 'Name =');
      } catch (AuraHandledException e) {
        malformedThrew = true;
      }
    }
    Assert.areEqual(1, rows.size());
    Assert.areEqual(pageId, rows[0].Id);
    Assert.isTrue(malformedThrew, 'a malformed where condition is wrapped in an AuraHandledException');
  }

  // ---- DynamicLinkHelper: setup and platform lookups (no learning objects) -----

  // Each remaining dynamic-SOQL branch (FlowRecordPage is covered by
  // getRecordIdFromDynamicLinkType_flowLookup) queries objects that exist only
  // when their feature is enabled: Surveys, Data Processing Engine, and
  // Experience Cloud (Network). Where a branch's objects exist and are readable
  // by the running user, it runs with a condition that matches nothing and must
  // return an empty list without error. Otherwise that branch is skipped
  // visibly (a WARN debug line).
  @IsTest
  static void getRecordIdFromDynamicLinkType_queriesEachFeatureBranch_whenItsObjectsExist() {
    List<String> branches = new List<String>{ 'SurveyRecordPage', 'DPERecordPage', 'CommunityPage' };
    Map<String, List<String>> objectsByBranch = new Map<String, List<String>>{
      'SurveyRecordPage' => new List<String>{ 'Survey', 'SurveyVersion' },
      'DPERecordPage' => new List<String>{ 'BatchCalcJobDefinition' },
      'CommunityPage' => new List<String>{ 'Network' }
    };
    Map<String, Schema.SObjectType> globalDescribe = Schema.getGlobalDescribe();

    for (String branch : branches) {
      String missing = null;
      for (String objectName : objectsByBranch.get(branch)) {
        if (
          !globalDescribe.containsKey(objectName) ||
          !globalDescribe.get(objectName).getDescribe().isAccessible()
        ) {
          missing = objectName;
          break;
        }
      }
      if (missing != null) {
        System.debug(
          LoggingLevel.WARN,
          'SKIPPED: ' + missing + ' not present or not readable by the running user; ' +
          branch + ' branch not verified'
        );
        continue;
      }
      List<SObject> rows = RLM_Learning_DynamicLinkHelper.getRecordIdFromDynamicLinkType(
        branch,
        'Id = null'
      );
      Assert.isTrue(rows.isEmpty(), branch + ' runs its query and matches nothing: ' + rows);
    }
  }

  @IsTest
  static void getSetupPageLink_appendsNoRedirectToAnExistingQueryString() {
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
  }

  @IsTest
  static void getSetupPageLink_buildsUserUrlAndRejectsAnUnmappedPage() {
    Id userId = UserInfo.getUserId();
    String expected =
      System.Url.getOrgDomainUrl().toExternalForm() +
      '/lightning/setup/ManageUsers/page?address=/' +
      userId +
      '&noredirect=1';
    Assert.areEqual(expected, RLM_Learning_DynamicLinkHelper.getSetupPageLink('User', userId));

    // The blank and malformed record-id guards are in dynamicLinkHelper_guards.
    // An unmapped setup page is rejected after its metadata lookup finds nothing.
    Boolean unmappedRejected = false;
    try {
      RLM_Learning_DynamicLinkHelper.getSetupPageLink('NoSuchSetupPage', userId);
    } catch (AuraHandledException e) {
      unmappedRejected = true;
    }
    Assert.isTrue(unmappedRejected, 'an unmapped setup page is rejected');
  }

  // Flow definitions are metadata, visible in tests; any active, unmanaged one
  // will do (the first by API name, for a stable choice). This bundle ships no
  // flow and flows deploy inactive in production, so when none is active the
  // found-flow checks are skipped visibly; the no-match check always runs.
  @IsTest
  static void getRecordIdFromDynamicLinkType_flowLookup() {
    List<FlowDefinitionView> activeFlows = [
      SELECT ApiName, ActiveVersionId
      FROM FlowDefinitionView
      WHERE ActiveVersionId != null AND NamespacePrefix = null
      ORDER BY ApiName
      LIMIT 1
    ];
    if (activeFlows.isEmpty()) {
      System.debug(
        LoggingLevel.WARN,
        'SKIPPED: no active unmanaged flow in this org; FlowRecordPage lookup not verified'
      );
    } else {
      List<SObject> found = RLM_Learning_DynamicLinkHelper.getRecordIdFromDynamicLinkType(
        'FlowRecordPage',
        'ApiName = \'' + String.escapeSingleQuotes(activeFlows[0].ApiName) + '\' AND NamespacePrefix = null'
      );
      Assert.areEqual(1, found.size(), 'the named flow is found');
      Assert.areEqual(activeFlows[0].ActiveVersionId, found[0].get('ActiveVersionId'),
        'a FlowRecordPage link resolves to the active version');
    }

    List<SObject> none = RLM_Learning_DynamicLinkHelper.getRecordIdFromDynamicLinkType(
      'FlowRecordPage',
      'ApiName = \'RLM_No_Such_Flow_For_Test\''
    );
    Assert.isTrue(none.isEmpty(), 'no flow has that API name');
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

  // A well-formed Id with no site behind it is rejected in every org. When the
  // org also has an Experience Cloud site with a login URL (the prm flag deploys
  // the "rlm" site; the billing portal bundle deploys another), that site's
  // base URL is an absolute prefix of its login URL with the "/s/..." login
  // path removed. Otherwise the trimming check is skipped visibly (a WARN
  // debug line).
  @IsTest
  static void getSiteUrl_rejectsAMissingSite_andTrimsTheLoginPath_whenTheOrgHasASite() {
    Boolean missingRejected = false;
    try {
      RLM_Learning_DynamicLinkHelper.getSiteUrl('0DB000000000001');
    } catch (AuraHandledException e) {
      missingRejected = true;
    }
    Assert.isTrue(missingRejected, 'a network Id with no site behind it is rejected');

    // Network is exposed only with Digital Experiences, so it is queried
    // dynamically: a static reference would not compile without it.
    List<SObject> networks = Schema.getGlobalDescribe().containsKey('Network')
      ? Database.query('SELECT Id FROM Network ORDER BY Name')
      : new List<SObject>();
    Id siteId = null;
    String loginUrl = null;
    for (SObject candidate : networks) {
      try {
        loginUrl = Network.getLoginUrl(candidate.Id);
      } catch (Exception e) {
        loginUrl = null; // this network has no usable login URL; try the next
      }
      if (loginUrl != null) {
        siteId = candidate.Id;
        break;
      }
    }
    if (loginUrl == null) {
      System.debug(
        LoggingLevel.WARN,
        'SKIPPED: no Experience Cloud site in this org, or no site has a login URL; ' +
        'getSiteUrl trimming not verified'
      );
      return;
    }

    String siteUrl = RLM_Learning_DynamicLinkHelper.getSiteUrl(siteId);

    Assert.isTrue(siteUrl.startsWith('http'), 'an absolute URL: ' + siteUrl);
    Assert.isTrue(loginUrl.startsWith(siteUrl), 'a prefix of the login URL: ' + siteUrl);
    Assert.isFalse(siteUrl.contains('/s/'), 'the login path is removed: ' + siteUrl);
  }

  // ---- UserInformation -------------------------------------------------------

  @IsTest
  static void userInformation_paths() {
    // getExpiryDays returns null exactly when the org has no trial expiry, and
    // otherwise the days left, clamped at zero (or one more, if the date
    // changed between the call and the check).
    // (Part-of-day greeting moved to the client; no Apex getTiming/timingForHour.)
    // getExpiryDays runs as the runner. getName runs as the learner when one
    // exists, so its result is a known first name. Without a learner it runs as
    // the runner and must return the runner's first name (not the last or full
    // name).
    Datetime trialExpiry = [SELECT TrialExpirationDate FROM Organization LIMIT 1].TrialExpirationDate;
    User learnerUser = learner();

    String name;
    Test.startTest();
    if (learnerUser != null) {
      System.runAs(learnerUser) {
        name = RLM_Learning_UserInformation.getName();
      }
    } else {
      name = RLM_Learning_UserInformation.getName();
    }
    Integer expiryDays = RLM_Learning_UserInformation.getExpiryDays();
    Test.stopTest();

    if (learnerUser != null) {
      Assert.areEqual('Learning', name, 'greets the learner by first name');
    } else if (String.isBlank(UserInfo.getFirstName())) {
      System.debug(LoggingLevel.WARN, 'SKIPPED: the runner has no first name; greeting not verified');
    } else {
      Assert.areEqual(UserInfo.getFirstName(), name, 'greets the runner by first name');
    }
    if (trialExpiry == null) {
      Assert.isNull(expiryDays, 'no trial expiry means no countdown');
    } else {
      Integer daysLeft = Math.max(0, Date.today().daysBetween(trialExpiry.date()));
      Assert.isTrue(
        expiryDays == daysLeft || expiryDays == daysLeft + 1,
        'the days left in the trial, clamped at zero: expected ' + daysLeft + ', got ' + expiryDays
      );
    }
  }
}
