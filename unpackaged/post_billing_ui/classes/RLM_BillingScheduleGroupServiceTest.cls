/**
 * Tests for RLM_BillingScheduleGroupService.
 *
 * The native standard-action invoke (createBillingSchedulesFromTrxn) is not run in
 * these tests: the create-via-API path is covered through the @TestVisible mock seam
 * (mockActionOutputs) plus direct coverage of the pure payload-build and result-parse
 * helpers, so the real invoke and its failed-result handling stay uncovered.
 * Validation guards are covered by asserting AuraHandledException on bad input.
 * The create tests do not observe the payload passed to the action, so the argument wiring
 * from createBillingScheduleGroupAndScheduleViaAPI into buildTransactionDetailsJson is
 * unverified (capturing it needs a production seam).
 * The System.runAs test creates its user through RLM_BillingUITestUsers, which takes a
 * Billing permission set license seat.
 * The other tests run as the deploying admin and read Account, BillingAccount,
 * AccountBillingAccount, Product2, LegalEntity and TaxTreatment in USER_MODE. On a
 * Release 264 org the System Administrator profile's ObjectPermissions grant read on all six
 * (read from the org, not from a test run). Only the two junction tests were run with
 * RLM_BillingUI unassigned from the admin, and both passed: the create test reads
 * BillingAccount and AccountBillingAccount, and the getAccountBillingInfo test reads Account
 * and BillingAccount (only its setup inserts the junction row).
 *
 * Payload (the create path sends what the modal chose): the legal entity (LegalEntityId__std), the
 * billing term when one is given (BillingTerm__std), the billing treatment that carries the chosen
 * Advance or Arrears timing for that legal entity (BillingTreatmentId__std; BillingType__std and
 * BillingTypePicklistTiming__std are rejected by the action, measured), and a shipping city
 * (ShippingCity__std: the account's, else the billingCity the caller submitted). The treatment query is replaced by
 * mockTreatmentCandidates in most tests; createViaAPI_treatmentQuery_* reads real records, and
 * lastTransactionDetails exposes the payload handed to the action. Still not sent: bill-to
 * contact, payment term (the action reads them from the records through the context mapping, as
 * measured earlier on a 264 org) and ParentTransactionId__std (Required for TermDefined only).
 * buildTransactionDetailsJson_mapsInputsToStandardContextFields pins the payload's exact key set.
 *
 * Fixed: a one-time charge from the Create Billing Schedule Group modal (billing term unit
 * 'OneTime', termSetting 'Evergreen' or a leftover 'Termed') is sent as SellingModelType__std
 * 'OneTime' with no EndDate__std, as the 264 developer guide requires. The service derives it from
 * the billing term unit. See the buildTransactionDetailsJson_oneTime* tests.
 *
 * Fixed: getAccountBillingInfo picks the account's default billing profile first, then the oldest
 * billing account (ORDER BY IsDefaultBillingProfile DESC, CreatedDate, Id), and
 * resolves one linked only through AccountBillingAccount; getLegalEntities/getTaxTreatments
 * offer only Active records; the create path rejects a null total price and a Termed
 * recurring create with no end date.
 */
@isTest
private class RLM_BillingScheduleGroupServiceTest {
    private static Id fakeId(Schema.SObjectType t) {
        return (Id) (t.getDescribe().getKeyPrefix() + '000000000000');
    }

    @isTest
    static void getAccountBillingInfo_nullArg_throws() {
        Boolean threw = false;
        try {
            RLM_BillingScheduleGroupService.getAccountBillingInfo(null);
        } catch (AuraHandledException e) {
            threw = true;
            Assert.areEqual('Account Id is required.', e.getMessage(), 'The page is told what is missing');
        }
        System.assert(threw, 'Expected AuraHandledException for null accountId');
    }

    @isTest
    static void getAccountBillingInfo_accountNotFound_throws() {
        Boolean threw = false;
        try {
            RLM_BillingScheduleGroupService.getAccountBillingInfo(fakeId(Account.SObjectType));
        } catch (AuraHandledException e) {
            threw = true;
            Assert.areEqual('Account not found.', e.getMessage(), 'The page is told the account is missing');
        }
        System.assert(threw, 'Expected AuraHandledException for missing account');
    }

    // A refused USER_MODE read reaches the page as a sentence naming what could not be read; the
    // query error stays on the cause. A user with no grants cannot read Account.
    @isTest
    static void getAccountBillingInfo_refusedAccountRead_namesWhatCouldNotBeRead() {
        Account acc = new Account(Name = 'RLM BSG Service Refused Read');
        insert acc;
        User u = RLM_BillingUITestUsers.create(new List<String>(), new List<String>());
        Boolean premise = false;
        AuraHandledException thrown;
        Test.startTest();
        System.runAs(u) {
            try {
                Database.query('SELECT Id, Name FROM Account LIMIT 1', AccessLevel.USER_MODE);
            } catch (QueryException e) {
                premise = true;
            }
            try {
                RLM_BillingScheduleGroupService.getAccountBillingInfo(acc.Id);
            } catch (AuraHandledException e) {
                thrown = e;
            }
        }
        Test.stopTest();
        Assert.isTrue(premise, 'PRECONDITION: a user with no grants cannot read Account.');
        Assert.isNotNull(thrown, 'A refused account read is reported, not returned as empty');
        Assert.areEqual(
            'You do not have access to read the account this screen needs. Contact your administrator.',
            thrown.getMessage(), 'The page is told what could not be read');
        Assert.isInstanceOfType(thrown.getCause(), QueryException.class, 'The query error is kept as the cause');
        AuraHandledException direct = RLM_BillingScheduleGroupService.readRefused(
            'the billing account', new QueryException('detail with field names'));
        Assert.areEqual(
            'You do not have access to read the billing account this screen needs. Contact your administrator.',
            direct.getMessage(), 'The sentence carries no query text');
    }

    @isTest
    static void describeErrors_listsEachCodeAndMessageForTheDebugLog() {
        Assert.areEqual('(no error detail)', RLM_BillingScheduleGroupService.describeErrors(null),
            'No errors still yields a log line');
        Assert.areEqual('(no error detail)',
            RLM_BillingScheduleGroupService.describeErrors(new List<Invocable.Action.Error>()),
            'An empty list still yields a log line');
    }

    @isTest
    static void createViaAPI_validationGuards() {
        // Null billing account -> throws before any query.
        System.assert(throwsViaApi(null), 'null billing account throws');
        // Valid-shaped but non-existent billing account -> "not found".
        System.assert(throwsViaApi(fakeId(BillingAccount.SObjectType)), 'missing billing account throws');
    }

    @isTest
    static void createViaAPI_happyPath_returnsRequestId() {
        Account a = new Account(Name = 'BSG ViaApi Acct');
        insert a;
        BillingAccount ba = new BillingAccount(Name = 'BSG ViaApi BA', AccountId = a.Id);
        insert ba;

        RLM_BillingScheduleGroupService.mockActionOutputs = new Map<String, Object>{
            'requestId' => 'REQ-PLACEHOLDER',
            'statusUrl' => '/services/data/v68.0/sobjects/AsyncOperationTracker/REQ-PLACEHOLDER'
        };
        seedTreatment();

        Test.startTest();
        RLM_BillingScheduleGroupService.CreateResult r =
            RLM_BillingScheduleGroupService.createBillingScheduleGroupAndScheduleViaAPI(
                ba.Id, 'Month', 12, 'Advance', 2, fakeId(LegalEntity.SObjectType),
                fakeId(TaxTreatment.SObjectType), 'USD', 10, 240, 'San Francisco',
                fakeId(Product2.SObjectType), 'Widget', Date.newInstance(2026, 1, 1),
                1, 1, 'Termed', Date.newInstance(2026, 12, 31)
            );
        Test.stopTest();

        Assert.areEqual('REQ-PLACEHOLDER', r.requestId, 'requestId surfaced from action output');
    }

    @isTest
    static void invokeAndParse_viaMockSeam() {
        RLM_BillingScheduleGroupService.mockActionOutputs = new Map<String, Object>{
            'requestId' => 'REQ-PLACEHOLDER',
            'statusUrl' => '/services/data/v68.0/sobjects/AsyncOperationTracker/REQ-PLACEHOLDER'
        };
        Map<String, Object> out =
            RLM_BillingScheduleGroupService.invokeStandaloneBillingScheduleCreate('{"Transaction":[]}');
        RLM_BillingScheduleGroupService.CreateResult r =
            RLM_BillingScheduleGroupService.parseCreateResult(out);
        Assert.areEqual('REQ-PLACEHOLDER', r.requestId);
        System.assert(r.statusUrl.contains('AsyncOperationTracker'), 'statusUrl mapped');
        System.assertNotEquals(null, r.apiResponse, 'apiResponse serialized');
    }

    @isTest
    static void parseCreateResult_handlesNullAndIds() {
        RLM_BillingScheduleGroupService.CreateResult empty =
            RLM_BillingScheduleGroupService.parseCreateResult(null);
        System.assertEquals(null, empty.requestId);

        Id anyId = fakeId(Account.SObjectType);
        Map<String, Object> out = new Map<String, Object>{
            'billingScheduleGroupId' => anyId,
            'billingScheduleIds' => new List<Object>{ anyId }
        };
        RLM_BillingScheduleGroupService.CreateResult r =
            RLM_BillingScheduleGroupService.parseCreateResult(out);
        System.assertEquals(anyId, r.billingScheduleGroupId);
        System.assertEquals(anyId, r.billingScheduleId);
    }

    @isTest
    static void innerClasses_construct() {
        Id acc = fakeId(Account.SObjectType);
        RLM_BillingScheduleGroupService.LegalEntityOption le =
            new RLM_BillingScheduleGroupService.LegalEntityOption(acc, 'LE');
        RLM_BillingScheduleGroupService.TaxTreatmentOption tt =
            new RLM_BillingScheduleGroupService.TaxTreatmentOption(acc, 'TT');
        RLM_BillingScheduleGroupService.ProductOption po =
            new RLM_BillingScheduleGroupService.ProductOption(acc, 'Prod');
        RLM_BillingScheduleGroupService.PicklistOption pl =
            new RLM_BillingScheduleGroupService.PicklistOption('Label', 'Value');
        RLM_BillingScheduleGroupService.AccountInfo ai =
            new RLM_BillingScheduleGroupService.AccountInfo('Acct', acc, 'BA', 'City');
        System.assertEquals('LE', le.name);
        System.assertEquals('TT', tt.name);
        System.assertEquals('Prod', po.name);
        System.assertEquals('Value', pl.value);
        System.assertEquals('City', ai.billingCity);
    }

    // ---- getAccountBillingInfo ----

    @isTest
    static void getAccountBillingInfo_withBillingAccount_returnsAccountAndBillingDetails() {
        Account a = new Account(Name = 'BSG Info Acct', BillingCity = 'Austin');
        insert a;
        BillingAccount ba = new BillingAccount(Name = 'BSG Info BA', AccountId = a.Id);
        insert ba;

        Test.startTest();
        RLM_BillingScheduleGroupService.AccountInfo info =
            RLM_BillingScheduleGroupService.getAccountBillingInfo(a.Id);
        Test.stopTest();

        Assert.areEqual('BSG Info Acct', info.accountName, 'Account name surfaced.');
        Assert.areEqual(ba.Id, info.billingAccountId, 'The billing account linked to the account is returned.');
        Assert.areEqual('BSG Info BA', info.billingAccountName, 'Billing account name surfaced.');
        Assert.areEqual('Austin', info.billingCity, 'Billing city comes from the billing account\'s account.');
    }

    @isTest
    static void getAccountBillingInfo_withoutBillingAccount_returnsAccountNameOnly() {
        Account a = new Account(Name = 'BSG No BA Acct', BillingCity = 'Denver');
        insert a;

        Test.startTest();
        RLM_BillingScheduleGroupService.AccountInfo info =
            RLM_BillingScheduleGroupService.getAccountBillingInfo(a.Id);
        Test.stopTest();

        Assert.areEqual('BSG No BA Acct', info.accountName, 'Account name is returned without a billing account.');
        Assert.isNull(info.billingAccountId, 'No billing account -> no billing account id.');
        Assert.isNull(info.billingAccountName, 'No billing account -> no billing account name.');
        Assert.isNull(info.billingCity, 'Billing city is read through the billing account, so it is blank too.');
    }

    @isTest
    static void getAccountBillingInfo_junctionOnlyBillingAccount_isResolved() {
        Account a = new Account(Name = 'BSG Junction Acct', BillingCity = 'Lisbon');
        insert a;
        BillingAccount ba = new BillingAccount(Name = 'BSG Junction BA');
        insert ba;
        insert new AccountBillingAccount(AccountId = a.Id, BillingAccountId = ba.Id);
        Assert.isNull([SELECT AccountId FROM BillingAccount WHERE Id = :ba.Id].AccountId,
            'PRECONDITION: inserting the junction row does not set BillingAccount.AccountId.');

        Test.startTest();
        RLM_BillingScheduleGroupService.AccountInfo info =
            RLM_BillingScheduleGroupService.getAccountBillingInfo(a.Id);
        Test.stopTest();

        Assert.areEqual('BSG Junction Acct', info.accountName);
        Assert.areEqual(ba.Id, info.billingAccountId,
            'A billing account linked only through AccountBillingAccount is resolved.');
        Assert.areEqual('BSG Junction BA', info.billingAccountName);
        Assert.areEqual('Lisbon', info.billingCity,
            'The billing account has no owning account, so the city is the requesting account\'s; the modal sends it on create.');
    }

    // Among several billing accounts of the account, the one marked as the default billing profile wins
    // over an older one. The platform accepts that flag only on a billing account that has an account:
    // setting it on one without is refused, and AccountBillingAccount.IsDefaultBillingAccount is
    // deprecated and cannot be set to true, so a junction-only billing account has no default.
    @isTest
    static void getAccountBillingInfo_prefersTheDefaultBillingProfile() {
        Account a = new Account(Name = 'BSG Default Profile Acct');
        insert a;
        insert new BillingAccount(Name = 'BSG Older BA', AccountId = a.Id);
        BillingAccount defaultProfile = new BillingAccount(Name = 'BSG Default Profile BA', AccountId = a.Id, IsDefaultBillingProfile = true);
        insert defaultProfile;

        Test.startTest();
        RLM_BillingScheduleGroupService.AccountInfo info =
            RLM_BillingScheduleGroupService.getAccountBillingInfo(a.Id);
        Test.stopTest();

        Assert.areEqual(defaultProfile.Id, info.billingAccountId, 'The default billing profile is picked over an older billing account.');
    }

    // The role set that ships with the Billing UI must resolve a junction-only billing account:
    // this needs AccountBillingAccount read. Run as the role, not as an admin.
    @isTest
    static void getAccountBillingInfo_junctionOnlyBillingAccount_isResolvedForTheBillingRole() {
        Account a = new Account(Name = 'BSG Role Junction Acct');
        insert a;
        BillingAccount ba = new BillingAccount(Name = 'BSG Role Junction BA');
        insert ba;
        insert new AccountBillingAccount(AccountId = a.Id, BillingAccountId = ba.Id);
        User u = RLM_BillingUITestUsers.create(
            new List<String>{ 'RLM_BillingUI', 'RevenueLifecycleManagementBillingOperations' },
            new List<String>{ RLM_BillingUITestUsers.BILLING_PSL });
        // Record visibility is the org's sharing, not the role set; see grantViewAll.
        RLM_BillingUITestUsers.grantViewAll(u, new List<String>{ 'BillingAccount' });

        RLM_BillingScheduleGroupService.AccountInfo info;
        Test.startTest();
        System.runAs(u) {
            info = RLM_BillingScheduleGroupService.getAccountBillingInfo(a.Id);
        }
        Test.stopTest();

        Assert.areEqual(ba.Id, info.billingAccountId, 'The billing role resolves the linked billing account.');
        Assert.isFalse(info.billingLinkUnreadable, 'A readable link is not flagged as unreadable.');
    }

    // A user who can read Account and BillingAccount but not AccountBillingAccount still sees the
    // account, flagged as "billing account unreadable" rather than an empty result that reads as
    // "no billing account".
    @isTest
    static void getAccountBillingInfo_withoutAccessToTheBillingAccountLinks_flagsTheBillingAccountUnreadable() {
        Account a = new Account(Name = 'BSG No Link Access Acct');
        insert a;
        BillingAccount ba = new BillingAccount(Name = 'BSG No Link Access BA');
        insert ba;
        insert new AccountBillingAccount(AccountId = a.Id, BillingAccountId = ba.Id);

        // A billing user who reads Account and BillingAccount but not the link object. Provisioned
        // with the Billing license and the platform Billing access permission, which makes the Billing
        // objects visible; a custom set grants the two reads. A shipped Billing role set cannot stand
        // for this user: every one of them also reads AccountBillingAccount, and a plain read grant
        // on BillingAccount is not honoured without the access permission (both measured on a 264 org).
        User u = RLM_BillingUITestUsers.createWithBillingAccess(
            new List<String>{ RLM_BillingUITestUsers.BILLING_PSL },
            new List<String>{ 'Account' },
            new List<String>{ 'BillingAccount' },
            new List<String>{ 'Account.BillingAddress' });

        RLM_BillingScheduleGroupService.AccountInfo info;
        Test.startTest();
        System.runAs(u) {
            Assert.isFalse(userModeQueryFails('SELECT Id FROM BillingAccount LIMIT 1'),
                'PRECONDITION: the user can read BillingAccount (so the failure below is the link read).');
            Assert.isTrue(userModeQueryFails('SELECT Id FROM AccountBillingAccount LIMIT 1'),
                'PRECONDITION: the user cannot read AccountBillingAccount.');
            info = RLM_BillingScheduleGroupService.getAccountBillingInfo(a.Id);
        }
        Test.stopTest();

        Assert.areEqual(a.Name, info.accountName, 'The account name is still shown.');
        Assert.isNull(info.billingAccountId, 'No billing account is resolved without the link read.');
        Assert.isTrue(info.billingLinkUnreadable,
            'The result says the billing account could not be read, not that there is none.');
    }

    // The hidden-billing-account tests below branch on what the test user reads, so where billing
    // accounts are not private they do not check the hidden case. This test fails on an org-wide
    // default other than Private, so that gap shows instead of passing silently. It does not catch
    // a sharing rule that lets the test user read the billing account on a Private org.
    @isTest
    static void billingAccountsArePrivateByDefault() {
        String sharingModel = billingAccountSharingModel();
        Assert.areEqual('Private', sharingModel,
            'The org-wide default for billing accounts is ' + sharingModel + ', not Private: the tests of a '
            + 'billing account hidden by sharing rely on it and do not check the hidden case here.');
    }

    private static String billingAccountSharingModel() {
        return [
            SELECT InternalSharingModel FROM EntityDefinition WHERE QualifiedApiName = 'BillingAccount'
        ].InternalSharingModel;
    }

    // A billing account that sharing hides from the user, linked to the account or owned by it: one
    // exists, so the result is flagged unreadable, not "none". Billing accounts are private by default
    // (measured on a fresh 264 org), but a test cannot change the org-wide default or remove a sharing
    // rule. So each case branches on what the test user can actually read: a hidden billing account
    // must be flagged unreadable, a readable one must be returned. Both are real outcomes, so no org
    // passes the test without checking something.
    @isTest
    static void getAccountBillingInfo_linkToABillingAccountHiddenBySharing_flagsTheBillingAccountUnreadable() {
        Account a = new Account(Name = 'BSG Hidden BA Acct');
        insert a;
        BillingAccount ba = new BillingAccount(Name = 'BSG Hidden BA');
        insert ba;
        insert new AccountBillingAccount(AccountId = a.Id, BillingAccountId = ba.Id);
        assertHiddenOrReturned(a, ba, true);
    }

    @isTest
    static void getAccountBillingInfo_ownBillingAccountHiddenBySharing_flagsTheBillingAccountUnreadable() {
        Account a = new Account(Name = 'BSG Hidden Own BA Acct');
        insert a;
        BillingAccount ba = new BillingAccount(Name = 'BSG Hidden Own BA', AccountId = a.Id);
        insert ba;
        assertHiddenOrReturned(a, ba, false);
    }

    // linked: the billing account reaches the account through an AccountBillingAccount link, which the
    // user must be able to read (the service relies on the link following the account's sharing).
    private static void assertHiddenOrReturned(Account a, BillingAccount ba, Boolean linked) {
        String sharingModel = billingAccountSharingModel();
        User u = RLM_BillingUITestUsers.create(
            new List<String>{ 'RLM_BillingUI', 'RevenueLifecycleManagementBillingOperations' },
            new List<String>{ RLM_BillingUITestUsers.BILLING_PSL });

        RLM_BillingScheduleGroupService.AccountInfo info;
        Test.startTest();
        Boolean hidden;
        System.runAs(u) {
            if (linked) {
                Assert.areEqual(1, [SELECT COUNT() FROM AccountBillingAccount WHERE AccountId = :a.Id WITH USER_MODE],
                    'PRECONDITION: the user reads the link (it follows the account\'s sharing).');
            }
            hidden = [SELECT COUNT() FROM BillingAccount WHERE Id = :ba.Id WITH USER_MODE] == 0;
            info = RLM_BillingScheduleGroupService.getAccountBillingInfo(a.Id);
        }
        Test.stopTest();

        Assert.areEqual(a.Name, info.accountName, 'The account name is still shown.');
        if (hidden) {
            Assert.isNull(info.billingAccountId, 'The hidden billing account is not returned.');
            Assert.isNull(info.billingAccountName, 'Nothing of the hidden billing account is returned.');
            Assert.isTrue(info.billingLinkUnreadable,
                'A billing account hidden by sharing (org-wide default ' + sharingModel + ') is not reported as none.');
        } else {
            Assert.areEqual(ba.Id, info.billingAccountId, 'A readable billing account is returned.');
            Assert.isFalse(info.billingLinkUnreadable, 'A readable billing account is not flagged.');
        }
    }

    // The account's own billing account comes before a linked one: when sharing hides the account's
    // own, a readable linked billing account is not picked in its place (the hidden one may be the
    // account's default billing profile). The linked one is shared with the user so it is readable
    // whatever the org-wide default; the account's own is hidden only where billing accounts are
    // private, and returned otherwise.
    @isTest
    static void getAccountBillingInfo_ownHiddenAndLinkedReadable_doesNotPickTheLinkedOne() {
        Account a = new Account(Name = 'BSG Own Hidden Linked Readable Acct');
        insert a;
        BillingAccount own = new BillingAccount(Name = 'BSG Own Hidden', AccountId = a.Id);
        BillingAccount linkedBa = new BillingAccount(Name = 'BSG Linked Readable');
        insert new List<BillingAccount>{ own, linkedBa };
        insert new AccountBillingAccount(AccountId = a.Id, BillingAccountId = linkedBa.Id);
        User u = RLM_BillingUITestUsers.create(
            new List<String>{ 'RLM_BillingUI', 'RevenueLifecycleManagementBillingOperations' },
            new List<String>{ RLM_BillingUITestUsers.BILLING_PSL });
        Boolean billingAccountsPrivate = billingAccountSharingModel() == 'Private';
        if (billingAccountsPrivate) {
            insert new BillingAccountShare(ParentId = linkedBa.Id, UserOrGroupId = u.Id, AccessLevel = 'Read');
        }

        RLM_BillingScheduleGroupService.AccountInfo info;
        Boolean ownHidden;
        Test.startTest();
        System.runAs(u) {
            Assert.areEqual(1, [SELECT COUNT() FROM BillingAccount WHERE Id = :linkedBa.Id WITH USER_MODE],
                'PRECONDITION: the user reads the linked billing account.');
            ownHidden = [SELECT COUNT() FROM BillingAccount WHERE Id = :own.Id WITH USER_MODE] == 0;
            info = RLM_BillingScheduleGroupService.getAccountBillingInfo(a.Id);
        }
        Test.stopTest();

        Assert.areNotEqual(linkedBa.Id, info.billingAccountId,
            'A linked billing account is not picked in place of the account\'s own.');
        if (ownHidden) {
            Assert.isNull(info.billingAccountId, 'The hidden billing account is not returned.');
            Assert.isTrue(info.billingLinkUnreadable, 'The hidden billing account of the account is flagged.');
        } else {
            Assert.areEqual(own.Id, info.billingAccountId, 'The account\'s own billing account is returned.');
            Assert.isFalse(info.billingLinkUnreadable, 'A readable billing account is not flagged.');
        }
    }

    // The existence check past sharing only runs when the user's own read finds nothing: an account
    // with no billing account at all is still "none" for a billing user.
    @isTest
    static void getAccountBillingInfo_noBillingAccountForTheBillingRole_isNone() {
        Account a = new Account(Name = 'BSG No BA Role Acct');
        insert a;
        User u = RLM_BillingUITestUsers.create(
            new List<String>{ 'RLM_BillingUI', 'RevenueLifecycleManagementBillingOperations' },
            new List<String>{ RLM_BillingUITestUsers.BILLING_PSL });

        RLM_BillingScheduleGroupService.AccountInfo info;
        Test.startTest();
        System.runAs(u) {
            info = RLM_BillingScheduleGroupService.getAccountBillingInfo(a.Id);
        }
        Test.stopTest();

        Assert.isNull(info.billingAccountId, 'No billing account.');
        Assert.isFalse(info.billingLinkUnreadable, 'No billing account is reported as none, not unreadable.');
    }

    private static Boolean userModeQueryFails(String soql) {
        try {
            Database.query(soql, AccessLevel.USER_MODE);
            return false;
        } catch (Exception e) {
            return true;
        }
    }

    // ---- option queries ----

    @isTest
    static void getProducts_returnsActiveSoftwareProductsSortedByName() {
        Product2 zeta = new Product2(Name = 'BSG Zeta Software', Family = 'Software', IsActive = true);
        Product2 alpha = new Product2(Name = 'BSG Alpha Software', Family = 'Software', IsActive = true);
        Product2 inactive = new Product2(Name = 'BSG Inactive Software', Family = 'Software', IsActive = false);
        Product2 noFamily = new Product2(Name = 'BSG No Family', IsActive = true);
        insert new List<Product2>{ zeta, alpha, inactive, noFamily };

        Test.startTest();
        List<RLM_BillingScheduleGroupService.ProductOption> options =
            RLM_BillingScheduleGroupService.getProducts();
        Test.stopTest();

        Assert.areEqual(2, options.size(), 'Only active products in the Software family are offered.');
        Assert.areEqual(alpha.Id, options[0].id, 'Options are sorted by name.');
        Assert.areEqual('BSG Alpha Software', options[0].name);
        Assert.areEqual(zeta.Id, options[1].id);
        Assert.areEqual('BSG Zeta Software', options[1].name);
    }

    // Product2 has no record sharing, so this proves a billing role can run the USER_MODE
    // product query (object read plus Name/IsActive/Family) without depending on OWD.
    // Beyond RLM_BillingUIAccessTest, it shows the real service call succeeds for the role and
    // returns the expected option shape.
    @isTest
    static void getProducts_asBillingRole_returnsTheProducts() {
        Product2 prod = new Product2(Name = 'BSG Role Software', Family = 'Software', IsActive = true);
        insert prod;
        User u = RLM_BillingUITestUsers.create(
            new List<String>{ 'RLM_BillingUI', 'RevenueLifecycleManagementBillingOperations' },
            new List<String>{ RLM_BillingUITestUsers.BILLING_PSL });

        List<RLM_BillingScheduleGroupService.ProductOption> options;
        Test.startTest();
        System.runAs(u) {
            options = RLM_BillingScheduleGroupService.getProducts();
        }
        Test.stopTest();

        Assert.areEqual(1, options.size(), 'The billing role sees the active Software product.');
        Assert.areEqual(prod.Id, options[0].id);
    }

    @isTest
    static void getLegalEntities_returnsActiveSortedByName() {
        LegalEntity zulu = new LegalEntity(Name = 'BSG LE Zulu', Status = 'Active');
        LegalEntity alpha = new LegalEntity(Name = 'BSG LE Alpha', Status = 'Active');
        LegalEntity mike = new LegalEntity(Name = 'BSG LE Mike', Status = 'Inactive');
        insert new List<LegalEntity>{ zulu, alpha, mike };

        Test.startTest();
        List<RLM_BillingScheduleGroupService.LegalEntityOption> options =
            RLM_BillingScheduleGroupService.getLegalEntities();
        Test.stopTest();

        Assert.areEqual(2, options.size(), 'Inactive legal entities are not offered.');
        Assert.areEqual(alpha.Id, options[0].id, 'Options are sorted by name.');
        Assert.areEqual('BSG LE Alpha', options[0].name);
        Assert.areEqual(zulu.Id, options[1].id);
        Assert.areEqual('BSG LE Zulu', options[1].name);
    }

    @isTest
    static void getTaxTreatments_returnsActiveSortedByName() {
        // Two treatments on one legal entity with no tax policy or product code collided on
        // TaxTreatment's unique key, so each gets its own legal entity.
        // The Active treatment is the control; the Draft ones must be filtered out.
        LegalEntity le1 = new LegalEntity(Name = 'BSG TT LE 1', Status = 'Active');
        LegalEntity le2 = new LegalEntity(Name = 'BSG TT LE 2', Status = 'Active');
        LegalEntity le3 = new LegalEntity(Name = 'BSG TT LE 3', Status = 'Active');
        insert new List<LegalEntity>{ le1, le2, le3 };
        TaxTreatment ttSecond = new TaxTreatment(Name = 'BSG TT Second', Status = 'Draft', LegalEntityId = le1.Id);
        TaxTreatment ttFirst = new TaxTreatment(Name = 'BSG TT First', Status = 'Draft', LegalEntityId = le2.Id);
        TaxTreatment ttActive = new TaxTreatment(Name = 'BSG TT Active', Status = 'Active', LegalEntityId = le3.Id);
        insert new List<TaxTreatment>{ ttSecond, ttFirst, ttActive };

        Test.startTest();
        List<RLM_BillingScheduleGroupService.TaxTreatmentOption> options =
            RLM_BillingScheduleGroupService.getTaxTreatments();
        Test.stopTest();

        Set<Id> returned = new Set<Id>();
        for (RLM_BillingScheduleGroupService.TaxTreatmentOption o : options) {
            returned.add(o.id);
        }
        Assert.isTrue(returned.contains(ttActive.Id), 'The Active tax treatment is returned (control).');
        Assert.areEqual(1, options.size(), 'Draft tax treatments are not offered.');
        Assert.areEqual(ttActive.Id, options[0].id);
        Assert.areEqual('BSG TT Active', options[0].name);
    }

    @isTest
    static void optionQueries_noRecords_returnEmptyLists() {
        Test.startTest();
        List<RLM_BillingScheduleGroupService.LegalEntityOption> les =
            RLM_BillingScheduleGroupService.getLegalEntities();
        List<RLM_BillingScheduleGroupService.TaxTreatmentOption> tts =
            RLM_BillingScheduleGroupService.getTaxTreatments();
        List<RLM_BillingScheduleGroupService.ProductOption> prods =
            RLM_BillingScheduleGroupService.getProducts();
        Test.stopTest();

        Assert.isTrue(les.isEmpty(), 'No legal entities -> empty list, not null.');
        Assert.isTrue(tts.isEmpty(), 'No tax treatments -> empty list, not null.');
        Assert.isTrue(prods.isEmpty(), 'No products -> empty list, not null.');
    }

    // The expected options are built from the same BillingSchedule describe the service reads,
    // so these tests prove the describe source is used (labels, values and order). What rules
    // out the hard-coded fallback (not exercised) is the non-empty precondition in
    // picklistLabelsAndValues: the service falls back only when that same describe is empty.
    @isTest
    static void billingTermUnitOptions_comeFromTheBillingSchedulePicklist() {
        List<String> expected = picklistLabelsAndValues('BillingTermUnit');
        Test.startTest();
        List<RLM_BillingScheduleGroupService.PicklistOption> options =
            RLM_BillingScheduleGroupService.getBillingScheduleBillingTermUnitOptions();
        Test.stopTest();

        assertOptions(expected, options);
    }

    @isTest
    static void pricingTermUnitOptions_comeFromTheBillingSchedulePicklist() {
        List<String> expected = picklistLabelsAndValues('PricingTermUnit');
        Test.startTest();
        List<RLM_BillingScheduleGroupService.PicklistOption> options =
            RLM_BillingScheduleGroupService.getPricingTermUnitOptions();
        Test.stopTest();

        assertOptions(expected, options);
    }

    // ---- createBillingScheduleGroupAndScheduleViaAPI ----

    // Every input guard after the account is resolved, flipped one at a time from inputs that
    // pass. The baseline call proves the defaults are valid, so each rejection is caused by
    // the one input that changed.
    @isTest
    static void createViaAPI_rejectsEachInvalidInput() {
        Id baId = insertBillingAccount('BSG Guards');
        RLM_BillingScheduleGroupService.mockActionOutputs = new Map<String, Object>{ 'requestId' => 'REQ-OK' };

        Map<String, CreateArgs> invalidInputs = new Map<String, CreateArgs>();
        CreateArgs a;
        a = new CreateArgs(baId); a.billingTermUnit = null;       invalidInputs.put('null billing term unit', a);
        a = new CreateArgs(baId); a.billingTermUnit = '  ';       invalidInputs.put('blank billing term unit', a);
        a = new CreateArgs(baId); a.quantity = null;              invalidInputs.put('null quantity', a);
        a = new CreateArgs(baId); a.quantity = -1;                invalidInputs.put('negative quantity', a);
        a = new CreateArgs(baId); a.legalEntityId = null;         invalidInputs.put('null legal entity', a);
        a = new CreateArgs(baId); a.taxTreatmentId = null;        invalidInputs.put('null tax treatment', a);
        a = new CreateArgs(baId); a.currencyIsoCode = '';         invalidInputs.put('blank currency', a);
        a = new CreateArgs(baId); a.unitPrice = null;             invalidInputs.put('null unit price', a);
        a = new CreateArgs(baId); a.unitPrice = -0.01;            invalidInputs.put('negative unit price', a);
        a = new CreateArgs(baId); a.billingCity = ' ';            invalidInputs.put('blank billing city', a);
        a = new CreateArgs(baId); a.productId = null;             invalidInputs.put('null product', a);
        a = new CreateArgs(baId); a.startDate = null;             invalidInputs.put('null start date', a);
        a = new CreateArgs(baId); a.billingDayOfMonth = null;     invalidInputs.put('null billing day', a);
        a = new CreateArgs(baId); a.billingDayOfMonth = 0;        invalidInputs.put('billing day 0', a);
        a = new CreateArgs(baId); a.billingDayOfMonth = 32;       invalidInputs.put('billing day 32', a);
        a = new CreateArgs(baId); a.billingStartMonth = null;     invalidInputs.put('null start month', a);
        a = new CreateArgs(baId); a.billingStartMonth = 0;        invalidInputs.put('start month 0', a);
        a = new CreateArgs(baId); a.billingStartMonth = 13;       invalidInputs.put('start month 13', a);

        List<String> accepted = new List<String>();
        Test.startTest();
        Assert.areEqual('REQ-OK', new CreateArgs(baId).call().requestId, 'PRECONDITION: the default inputs are valid.');
        for (String label : invalidInputs.keySet()) {
            if (!throwsAura(invalidInputs.get(label))) {
                accepted.add(label);
            }
        }
        Test.stopTest();

        Assert.isTrue(accepted.isEmpty(), 'Invalid input was accepted: ' + String.join(accepted, ', '));
    }

    @isTest
    static void createViaAPI_acceptsBoundaryValues() {
        Id baId = insertBillingAccount('BSG Boundaries');
        RLM_BillingScheduleGroupService.mockActionOutputs = new Map<String, Object>{ 'requestId' => 'REQ-EDGE' };

        Map<String, CreateArgs> edges = new Map<String, CreateArgs>();
        CreateArgs a;
        a = new CreateArgs(baId); a.quantity = 0; a.unitPrice = 0;                  edges.put('zero quantity and price', a);
        a = new CreateArgs(baId); a.billingDayOfMonth = 1; a.billingStartMonth = 12; edges.put('day 1, month 12', a);
        a = new CreateArgs(baId); a.billingDayOfMonth = 31; a.billingStartMonth = 1; edges.put('day 31, month 1', a);

        List<String> rejected = new List<String>();
        Test.startTest();
        for (String label : edges.keySet()) {
            if (throwsAura(edges.get(label))) {
                rejected.add(label);
            }
        }
        Test.stopTest();

        Assert.isTrue(rejected.isEmpty(), 'Boundary values were rejected: ' + String.join(rejected, ', '));
    }

    @isTest
    static void createViaAPI_termedWithoutEndDate_isRejected() {
        Id baId = insertBillingAccount('BSG Termed No End');
        RLM_BillingScheduleGroupService.mockActionOutputs = new Map<String, Object>{ 'requestId' => 'REQ-GAP' };
        CreateArgs args = new CreateArgs(baId);
        args.termSetting = 'Termed';
        args.endDate = null;

        Test.startTest();
        Boolean rejected = throwsAura(args);
        Test.stopTest();

        Assert.isTrue(rejected, 'A Termed recurring create with no end date is rejected.');
    }

    @isTest
    static void createViaAPI_nullTotalPrice_isRejected() {
        Id baId = insertBillingAccount('BSG Null Total');
        RLM_BillingScheduleGroupService.mockActionOutputs = new Map<String, Object>{ 'requestId' => 'REQ-GAP' };
        CreateArgs args = new CreateArgs(baId);
        args.totalPrice = null;

        Test.startTest();
        Boolean rejected = throwsAura(args);
        Test.stopTest();

        Assert.isTrue(rejected, 'A null total price is rejected (TotalPrice__std is required).');
    }

    @isTest
    static void createViaAPI_mapsSynchronousOutputs() {
        Id baId = insertBillingAccount('BSG Outputs');
        Id bsgId = fakeId(BillingScheduleGroup.SObjectType);
        Id bsId = fakeId(BillingSchedule.SObjectType);
        RLM_BillingScheduleGroupService.mockActionOutputs = new Map<String, Object>{
            'requestId' => 'REQ-1',
            'statusUrl' => '/services/data/v68.0/sobjects/AsyncOperationTracker/REQ-1',
            'billingScheduleGroupId' => bsgId,
            'billingScheduleId' => bsId
        };

        Test.startTest();
        RLM_BillingScheduleGroupService.CreateResult r = new CreateArgs(baId).call();
        Test.stopTest();

        Assert.areEqual('REQ-1', r.requestId);
        Assert.areEqual('/services/data/v68.0/sobjects/AsyncOperationTracker/REQ-1', r.statusUrl);
        Assert.areEqual(bsgId, r.billingScheduleGroupId, 'A synchronous BSG id is passed through.');
        Assert.areEqual(bsId, r.billingScheduleId, 'A synchronous schedule id is passed through.');
        Map<String, Object> echoed = (Map<String, Object>) System.JSON.deserializeUntyped(r.apiResponse);
        Assert.areEqual('REQ-1', echoed.get('requestId'), 'apiResponse is the serialized action output.');
    }

    // A billing account with no AccountId but an AccountBillingAccount row is accepted. The
    // orphan test below is the same input without the junction row, which is rejected, so the
    // junction row is what lets the create through. The mock does not capture the payload, so
    // which account id is sent is not observed.
    @isTest
    static void createViaAPI_billingAccountLinkedThroughJunction_isAccepted() {
        Account a = new Account(Name = 'BSG Junction Create Acct');
        insert a;
        BillingAccount ba = new BillingAccount(Name = 'BSG Junction Create BA');
        insert ba;
        insert new AccountBillingAccount(AccountId = a.Id, BillingAccountId = ba.Id);
        Assert.isNull([SELECT AccountId FROM BillingAccount WHERE Id = :ba.Id].AccountId,
            'PRECONDITION: inserting the junction row does not set BillingAccount.AccountId.');
        RLM_BillingScheduleGroupService.mockActionOutputs = new Map<String, Object>{ 'requestId' => 'REQ-JN' };

        Test.startTest();
        RLM_BillingScheduleGroupService.CreateResult r = new CreateArgs(ba.Id).call();
        Test.stopTest();

        Assert.areEqual('REQ-JN', r.requestId, 'A billing account linked through the junction row is accepted.');
    }

    // A billing account with no AccountId resolves its account through AccountBillingAccount;
    // with no junction row either, the create must refuse rather than send a null account.
    // The premises pin that it is that guard: the billing account is found (so not "not
    // found"), its AccountId is null and no junction row exists. A positive control with the
    // same defaults and a billing account that has an Account is accepted, so the rejection
    // comes from the missing account alone.
    @isTest
    static void createViaAPI_billingAccountWithoutAccount_throws() {
        BillingAccount orphan = new BillingAccount(Name = 'BSG Orphan BA');
        insert orphan;
        RLM_BillingScheduleGroupService.mockActionOutputs = new Map<String, Object>{ 'requestId' => 'REQ-CONTROL' };

        List<BillingAccount> found = [
            SELECT Id, AccountId FROM BillingAccount WHERE Id = :orphan.Id WITH USER_MODE
        ];
        Integer junctionRows = [
            SELECT COUNT() FROM AccountBillingAccount WHERE BillingAccountId = :orphan.Id WITH USER_MODE
        ];
        Assert.areEqual(1, found.size(), 'PRECONDITION: the billing account is readable in USER_MODE.');
        Assert.isNull(found[0].AccountId, 'PRECONDITION: the billing account has no AccountId.');
        Assert.areEqual(0, junctionRows, 'PRECONDITION: no AccountBillingAccount row links it to an account.');

        Id controlBaId = insertBillingAccount('BSG Orphan Control');

        Test.startTest();
        RLM_BillingScheduleGroupService.CreateResult control = new CreateArgs(controlBaId).call();
        Boolean threw = throwsAura(new CreateArgs(orphan.Id));
        Test.stopTest();

        Assert.areEqual('REQ-CONTROL', control.requestId,
            'PRECONDITION: the same defaults with a billing account that has an Account are accepted.');
        Assert.isTrue(threw, 'A billing account with no resolvable account must be rejected.');
    }

    // ---- payload builder ----

    @isTest
    static void buildTransactionDetailsJson_mapsInputsToStandardContextFields() {
        Id accId = fakeId(Account.SObjectType);
        Id baId = fakeId(BillingAccount.SObjectType);
        Id ttId = fakeId(TaxTreatment.SObjectType);
        Id prodId = fakeId(Product2.SObjectType);
        Id leId = fakeId(LegalEntity.SObjectType);
        Id trId = fakeId(BillingTreatment.SObjectType);

        // Quantity, unit price and total are deliberately inconsistent: 3 x 12.5 x 12 months =
        // 450, so 451 cannot be derived. The builder passes each through as given.
        Map<String, Object> txn = onlyTransaction(RLM_BillingScheduleGroupService.buildTransactionDetailsJson(
            accId, baId, 'Month', 3, leId, ttId,
            'EUR', 12.5, 451, 'Lisbon', prodId, 'Widget Pro',
            Date.newInstance(2026, 4, 7), 7, 4, 'Termed', Date.newInstance(2027, 4, 6), 7, trId, 'Porto'
        ));

        // The exact key set is pinned: any key added or removed fails here. ParentTransactionId__std,
        // bill-to contact and payment term are deliberately absent (see the class header).
        Set<String> expectedKeys = new Set<String>{
            'TransactionId__std', 'SellingModelType__std', 'ProductId__std', 'ProductName__std',
            'StartDate__std', 'EndDate__std', 'PeriodBoundary__std', 'BillingDayOfMonth__std',
            'BillingStartMonth__std', 'UnitPrice__std', 'Quantity__std', 'TotalPrice__std',
            'TaxTreatmentId__std', 'LegalEntityId__std', 'AccountId__std', 'BillingProfileId__std',
            'BillingCity__std', 'ShippingCity__std', 'BillingTermUnit__std', 'BillingActionType__std',
            'CurrencyIsoCode__std', 'BillingTerm__std', 'BillingTreatmentId__std'
        };
        Set<String> added = new Set<String>(txn.keySet());
        added.removeAll(expectedKeys);
        Set<String> missing = new Set<String>(expectedKeys);
        missing.removeAll(txn.keySet());
        Assert.isTrue(added.isEmpty(), 'Unexpected payload keys: ' + added);
        Assert.isTrue(missing.isEmpty(), 'An expected payload key was removed (regression): ' + missing);
        Assert.isFalse(txn.containsKey('BillingType__std') || txn.containsKey('BillingTypePicklistTiming__std'),
            'The action rejects the timing tags (Invalid tag attribute name key); timing goes through the treatment.');

        Assert.isTrue(String.valueOf(txn.get('TransactionId__std')).startsWith('txn_'), 'Generated transaction id.');
        Assert.areEqual('TermDefined', txn.get('SellingModelType__std'), 'Termed maps to TermDefined.');
        Assert.areEqual(String.valueOf(prodId), txn.get('ProductId__std'));
        Assert.areEqual('Widget Pro', txn.get('ProductName__std'));
        Assert.areEqual('2026-04-07', txn.get('StartDate__std'));
        Assert.areEqual('2027-04-06', txn.get('EndDate__std'), 'A termed schedule carries its end date.');
        Assert.areEqual('Anniversary', txn.get('PeriodBoundary__std'));
        Assert.areEqual(7, txn.get('BillingDayOfMonth__std'));
        Assert.areEqual(4, txn.get('BillingStartMonth__std'));
        Assert.areEqual(Decimal.valueOf('12.5'), toDecimal(txn.get('UnitPrice__std')));
        Assert.areEqual(Decimal.valueOf('3'), toDecimal(txn.get('Quantity__std')));
        Assert.areEqual(Decimal.valueOf('451'), toDecimal(txn.get('TotalPrice__std')));
        Assert.areEqual(String.valueOf(ttId), txn.get('TaxTreatmentId__std'));
        Assert.areEqual(String.valueOf(accId), txn.get('AccountId__std'));
        Assert.areEqual(String.valueOf(baId), txn.get('BillingProfileId__std'),
            'The billing account is sent as the billing profile.');
        Assert.areEqual('Lisbon', txn.get('BillingCity__std'));
        Assert.areEqual('Month', txn.get('BillingTermUnit__std'));
        Assert.areEqual('Add', txn.get('BillingActionType__std'));
        Assert.areEqual('EUR', txn.get('CurrencyIsoCode__std'));
        Assert.areEqual(String.valueOf(leId), txn.get('LegalEntityId__std'), 'The chosen legal entity is sent.');
        Assert.areEqual(7, txn.get('BillingTerm__std'), 'The billing term is sent.');
        Assert.areEqual(String.valueOf(trId), txn.get('BillingTreatmentId__std'), 'The billing treatment is sent.');
        Assert.areEqual('Porto', txn.get('ShippingCity__std'), 'The shipping city is sent.');
    }

    // The modal marks a one-time charge by billing term unit, not termSetting (it sends only
    // 'Evergreen' or 'Termed'), so the 'OneTime' case covers the service's termSetting
    // pass-through branch for other values.
    @isTest
    static void buildTransactionDetailsJson_sellingModel_termSettingBranches() {
        Assert.areEqual('Evergreen', sellingModelFor('Evergreen'), 'Evergreen passes through.');
        Assert.areEqual('OneTime', sellingModelFor('OneTime'),
            'Pass-through branch: any other non-blank setting is sent as given.');
        Assert.areEqual('Evergreen', sellingModelFor(null), 'No term setting defaults to Evergreen.');
        Assert.areEqual('Evergreen', sellingModelFor('  '), 'A blank term setting defaults to Evergreen.');
    }

    @isTest
    static void buildTransactionDetailsJson_termedWithoutEndDate_omitsEndDate() {
        Map<String, Object> txn = onlyTransaction(RLM_BillingScheduleGroupService.buildTransactionDetailsJson(
            fakeId(Account.SObjectType), fakeId(BillingAccount.SObjectType), 'Month', 1,
            fakeId(LegalEntity.SObjectType), fakeId(TaxTreatment.SObjectType), 'USD', 10, 120,
            'Boston', fakeId(Product2.SObjectType), 'Widget', Date.newInstance(2026, 1, 1), 1, 1,
            'Termed', null, null, null, 'Boston'
        ));
        Assert.areEqual('TermDefined', txn.get('SellingModelType__std'));
        Assert.isFalse(txn.containsKey('EndDate__std'),
            'The builder sends no EndDate__std when none is given.');
    }

    // What the modal sends for a one-time charge: handleChargeTypeChange sets
    // billingTermUnitPicklist 'OneTime' and leaves termSetting at its default, 'Evergreen'
    // (rlmBillingScheduleGroupModal.js, termSetting = 'Evergreen').
    @isTest
    static void buildTransactionDetailsJson_oneTimeChargeFromModal_isSentAsOneTime() {
        Map<String, Object> txn = onlyTransaction(RLM_BillingScheduleGroupService.buildTransactionDetailsJson(
            fakeId(Account.SObjectType), fakeId(BillingAccount.SObjectType), 'OneTime', 1,
            fakeId(LegalEntity.SObjectType), fakeId(TaxTreatment.SObjectType), 'USD', 10, 10,
            'Boston', fakeId(Product2.SObjectType), 'Widget', Date.newInstance(2026, 1, 1), 1, 1,
            'Evergreen', null, null, null, 'Boston'
        ));
        Assert.areEqual('OneTime', txn.get('BillingTermUnit__std'), 'The one-time unit is sent as given.');
        Assert.areEqual('OneTime', txn.get('SellingModelType__std'),
            'A one-time charge from the modal (billing term unit OneTime, termSetting Evergreen) '
            + 'is sent as SellingModelType__std OneTime.');
        Assert.isFalse(txn.containsKey('EndDate__std'), 'A one-time charge sends no end date.');
    }

    // The modal path Recurring -> Termed (which sets endDate) -> One Time: handleChargeTypeChange
    // sets billingTermUnitPicklist 'OneTime' but keeps termSetting 'Termed' and the old endDate.
    @isTest
    static void buildTransactionDetailsJson_oneTimeAfterTermedFromModal_isSentAsOneTimeWithoutEndDate() {
        Map<String, Object> txn = onlyTransaction(RLM_BillingScheduleGroupService.buildTransactionDetailsJson(
            fakeId(Account.SObjectType), fakeId(BillingAccount.SObjectType), 'OneTime', 1,
            fakeId(LegalEntity.SObjectType), fakeId(TaxTreatment.SObjectType), 'USD', 10, 10,
            'Boston', fakeId(Product2.SObjectType), 'Widget', Date.newInstance(2026, 1, 1), 1, 1,
            'Termed', Date.newInstance(2026, 12, 31), null, null, 'Boston'
        ));
        Assert.areEqual('OneTime', txn.get('BillingTermUnit__std'), 'The one-time unit is sent as given.');
        Assert.areEqual('OneTime', txn.get('SellingModelType__std'),
            'A one-time charge chosen after Termed is sent as SellingModelType__std OneTime.');
        Assert.isFalse(txn.containsKey('EndDate__std'),
            'The end date left over from Termed is not sent for a one-time charge.');
    }

    @isTest
    static void buildTransactionDetailsJson_evergreenAndPassThroughSendTotalButNoEndDate() {
        // TotalPrice__std is required for every new-sale selling model; only TermDefined has an
        // end date, so a supplied one is ignored for the others. The modal marks a one-time
        // charge by billing term unit, not termSetting; the 'OneTime' case here covers the
        // service's termSetting pass-through branch.
        for (String termSetting : new List<String>{ 'Evergreen', 'OneTime' }) {
            Map<String, Object> txn = onlyTransaction(RLM_BillingScheduleGroupService.buildTransactionDetailsJson(
                fakeId(Account.SObjectType), fakeId(BillingAccount.SObjectType), 'Month', 1,
                fakeId(LegalEntity.SObjectType), fakeId(TaxTreatment.SObjectType), 'USD', 10, 75,
                'Boston', fakeId(Product2.SObjectType), 'Widget', Date.newInstance(2026, 1, 1), 1, 1,
                termSetting, Date.newInstance(2026, 12, 31), null, null, 'Boston'
            ));
            Assert.areEqual(Decimal.valueOf('75'), toDecimal(txn.get('TotalPrice__std')),
                termSetting + ' sends the total price.');
            Assert.isFalse(txn.containsKey('EndDate__std'), termSetting + ' sends no end date.');
        }
    }

    @isTest
    static void formatIsoDate_keepsTwoDigitMonthAndDay() {
        Assert.areEqual('2026-12-31', RLM_BillingScheduleGroupService.formatIsoDate(Date.newInstance(2026, 12, 31)));
        Assert.areEqual('2027-01-09', RLM_BillingScheduleGroupService.formatIsoDate(Date.newInstance(2027, 1, 9)));
    }


    // ---- what the create path sends from the modal's choices ----

    @isTest
    static void createViaAPI_sendsEntityTermTreatmentAndShippingCity() {
        Account a = new Account(Name = 'BSG Payload Acct', ShippingCity = 'Austin', BillingCity = 'Denver');
        insert a;
        BillingAccount ba = new BillingAccount(Name = 'BSG Payload BA', AccountId = a.Id);
        insert ba;
        Id leId = fakeId(LegalEntity.SObjectType);
        Id trId = fakeId(BillingTreatment.SObjectType);
        RLM_BillingScheduleGroupService.mockActionOutputs = new Map<String, Object>{ 'requestId' => 'REQ-P' };
        RLM_BillingScheduleGroupService.mockTreatmentCandidates = candidates(
            new RLM_BillingScheduleGroupService.TreatmentCandidate(trId, 'Arrears', 'USD'));
        CreateArgs args = new CreateArgs(ba.Id);
        args.legalEntityId = leId;
        args.billingTerm = 7;
        args.billingType = 'Arrears';

        Test.startTest();
        args.call();
        Test.stopTest();

        Map<String, Object> txn = onlyTransaction(RLM_BillingScheduleGroupService.lastTransactionDetails);
        Assert.areEqual(String.valueOf(leId), txn.get('LegalEntityId__std'), 'The chosen legal entity reaches the action.');
        Assert.areEqual(7, txn.get('BillingTerm__std'), 'The chosen billing term reaches the action.');
        Assert.areEqual(String.valueOf(trId), txn.get('BillingTreatmentId__std'), 'The treatment for the chosen timing reaches the action.');
        Assert.areEqual('Austin', txn.get('ShippingCity__std'), 'The account shipping city is sent.');
        Assert.areEqual('San Francisco', txn.get('BillingCity__std'), 'The billing city is still sent.');
        Assert.isFalse(txn.containsKey('BillingType__std') || txn.containsKey('BillingTypePicklistTiming__std'),
            'The rejected timing tags are never sent.');
    }

    @isTest
    static void createViaAPI_noShippingCity_fallsBackToTheBillingCity() {
        Id baId = insertBillingAccount('BSG Ship Fallback');
        RLM_BillingScheduleGroupService.mockActionOutputs = new Map<String, Object>{ 'requestId' => 'REQ-S' };

        Test.startTest();
        new CreateArgs(baId).call();
        Test.stopTest();

        Map<String, Object> txn = onlyTransaction(RLM_BillingScheduleGroupService.lastTransactionDetails);
        Assert.areEqual('San Francisco', txn.get('ShippingCity__std'),
            'With no account shipping city the billing city is sent as the shipping city.');
    }

    @isTest
    static void resolveShippingCity_prefersShippingThenTheSubmittedBillingCity() {
        Assert.areEqual('Austin', RLM_BillingScheduleGroupService.resolveShippingCity('Austin', 'Denver'));
        Assert.areEqual('Denver', RLM_BillingScheduleGroupService.resolveShippingCity(null, 'Denver'));
        Assert.areEqual('Denver', RLM_BillingScheduleGroupService.resolveShippingCity('  ', 'Denver'));
    }

    @isTest
    static void createViaAPI_noTreatmentForTheEntityAndTiming_isRefusedWithAMessage() {
        Id baId = insertBillingAccount('BSG No Treatment');
        RLM_BillingScheduleGroupService.mockActionOutputs = new Map<String, Object>{ 'requestId' => 'REQ-N' };
        RLM_BillingScheduleGroupService.mockTreatmentCandidates =
            new List<RLM_BillingScheduleGroupService.TreatmentCandidate>();
        CreateArgs args = new CreateArgs(baId);
        args.billingType = 'Arrears';

        AuraHandledException thrown;
        Test.startTest();
        try {
            args.call();
        } catch (AuraHandledException e) {
            thrown = e;
        }
        Test.stopTest();

        Assert.isNotNull(thrown, 'A timing with no treatment is refused instead of silently using the org default.');
        Assert.areEqual(
            'No active billing treatment bills in Arrears in USD for legal entity the selected legal entity. '
            + 'Choose another legal entity, timing or currency, or ask your administrator to set one up.',
            thrown.getMessage());
        Assert.isNull(RLM_BillingScheduleGroupService.lastTransactionDetails, 'Nothing reached the action.');
    }

    @isTest
    static void createViaAPI_timingRules() {
        Id baId = insertBillingAccount('BSG Timing');
        RLM_BillingScheduleGroupService.mockActionOutputs = new Map<String, Object>{ 'requestId' => 'REQ-T' };

        CreateArgs recurringNoTiming = new CreateArgs(baId);
        recurringNoTiming.billingType = null;
        CreateArgs badTiming = new CreateArgs(baId);
        badTiming.billingType = 'None';
        CreateArgs badTerm = new CreateArgs(baId);
        badTerm.billingTerm = 0;
        CreateArgs oneTime = new CreateArgs(baId);
        oneTime.billingTermUnit = 'OneTime';
        oneTime.billingType = null;
        oneTime.billingTerm = null;
        oneTime.termSetting = 'Evergreen';
        oneTime.endDate = null;

        Test.startTest();
        Assert.isTrue(throwsAura(recurringNoTiming), 'A recurring charge needs a timing.');
        Assert.isTrue(throwsAura(badTiming), 'Only Advance and Arrears are accepted.');
        Assert.isTrue(throwsAura(badTerm), 'A billing term below 1 is refused.');
        Assert.isFalse(throwsAura(oneTime), 'A one-time charge offers no timing and needs none.');
        Test.stopTest();

        Map<String, Object> txn = onlyTransaction(RLM_BillingScheduleGroupService.lastTransactionDetails);
        Assert.isFalse(txn.containsKey('BillingTreatmentId__std'),
            'A one-time charge with no timing sends no treatment, so the org default applies.');
        Assert.isFalse(txn.containsKey('BillingTerm__std'), 'No billing term given, none sent.');
    }

    @isTest
    static void createViaAPI_noTreatmentInTheChargeCurrency_isRefusedNamingCurrency() {
        Id baId = insertBillingAccount('BSG Other Currency');
        RLM_BillingScheduleGroupService.mockActionOutputs = new Map<String, Object>{ 'requestId' => 'REQ-C' };
        RLM_BillingScheduleGroupService.mockTreatmentCandidates = candidates(
            new RLM_BillingScheduleGroupService.TreatmentCandidate(fakeId(BillingTreatment.SObjectType), 'Arrears', 'EUR'));
        CreateArgs args = new CreateArgs(baId);
        args.billingType = 'Arrears';
        args.currencyIsoCode = 'USD';

        AuraHandledException thrown;
        Test.startTest();
        try {
            args.call();
        } catch (AuraHandledException e) {
            thrown = e;
        }
        Test.stopTest();

        Assert.isNotNull(thrown, 'A treatment in another currency is refused, not paired with the charge.');
        Assert.isTrue(thrown.getMessage().contains('Arrears in USD'), 'The message names the timing and currency.');
        Assert.isNull(RLM_BillingScheduleGroupService.lastTransactionDetails, 'Nothing reached the action.');
    }

    @isTest
    static void chooseTreatment_firstInTimingAndCurrency_skipsAmbiguousAndDedupes() {
        Id ambiguous = fakeId(BillingTreatment.SObjectType);
        Id both = Id.valueOf(BillingTreatment.SObjectType.getDescribe().getKeyPrefix() + '000000000001');
        Id arrears = Id.valueOf(BillingTreatment.SObjectType.getDescribe().getKeyPrefix() + '000000000002');
        Id eur = Id.valueOf(BillingTreatment.SObjectType.getDescribe().getKeyPrefix() + '000000000003');
        List<RLM_BillingScheduleGroupService.TreatmentCandidate> rows = new List<RLM_BillingScheduleGroupService.TreatmentCandidate>{
            new RLM_BillingScheduleGroupService.TreatmentCandidate(ambiguous, 'Arrears', 'USD'),
            new RLM_BillingScheduleGroupService.TreatmentCandidate(ambiguous, 'Advance', 'USD'),
            new RLM_BillingScheduleGroupService.TreatmentCandidate(eur, 'Arrears', 'EUR'),
            new RLM_BillingScheduleGroupService.TreatmentCandidate(arrears, 'Arrears', 'USD'),
            new RLM_BillingScheduleGroupService.TreatmentCandidate(arrears, 'Arrears', 'USD'),
            new RLM_BillingScheduleGroupService.TreatmentCandidate(both, 'Advance', 'USD')
        };
        Assert.areEqual(arrears, RLM_BillingScheduleGroupService.chooseTreatment(rows, 'Arrears', 'USD'),
            'A treatment with both timings is skipped; a repeated item does not make one ambiguous.');
        Assert.areEqual(both, RLM_BillingScheduleGroupService.chooseTreatment(rows, 'Advance', 'USD'));
        Assert.areEqual(eur, RLM_BillingScheduleGroupService.chooseTreatment(rows, 'Arrears', 'EUR'),
            'The charge currency picks the treatment.');
        Assert.isNull(RLM_BillingScheduleGroupService.chooseTreatment(rows, 'Arrears', 'GBP'),
            'No treatment in the charge currency, no match.');
        Assert.isNull(RLM_BillingScheduleGroupService.chooseTreatment(
            new List<RLM_BillingScheduleGroupService.TreatmentCandidate>(), 'Arrears', 'USD'), 'No candidates, no treatment.');
    }

    // Reads real records: the treatment is found through its legal entity and the timing of its
    // active item. Setup is the least that the platform accepts; if it is refused the failure names
    // the record, so this is a precondition and not a skip.
    @isTest
    static void createViaAPI_treatmentQuery_findsTheTreatmentOfTheEntityForTheTiming() {
        LegalEntity le = new LegalEntity(Name = 'BSG TQ LE', Status = 'Active');
        LegalEntity other = new LegalEntity(Name = 'BSG TQ Other LE', Status = 'Active');
        insert new List<LegalEntity>{ le, other };
        String cur = UserInfo.getDefaultCurrency();
        BillingTreatment advance = new BillingTreatment(Name = 'BSG TQ Advance', LegalEntityId = le.Id, Status = 'Draft', ExcludeFromBilling = 'No', CurrencyIsoCode = cur);
        BillingTreatment arrears = new BillingTreatment(Name = 'BSG TQ Arrears', LegalEntityId = le.Id, Status = 'Draft', ExcludeFromBilling = 'No', CurrencyIsoCode = cur);
        BillingTreatment otherArrears = new BillingTreatment(Name = 'BSG TQ Other Arrears', LegalEntityId = other.Id, Status = 'Draft', ExcludeFromBilling = 'No', CurrencyIsoCode = cur);
        insert new List<BillingTreatment>{ advance, arrears, otherArrears };
        insert new List<BillingTreatmentItem>{
            new BillingTreatmentItem(Name = 'BSG TQ Advance Item', BillingTreatmentId = advance.Id, BillingType = 'Advance', Controller = 'BillingScheduleGroup', Status = 'Draft', Type = 'Remainder', ProcessingOrder = 1, Sequencing = 'Manual', Handling0Amount = 'CreateInvoice'),
            new BillingTreatmentItem(Name = 'BSG TQ Arrears Item', BillingTreatmentId = arrears.Id, BillingType = 'Arrears', Controller = 'BillingScheduleGroup', Status = 'Draft', Type = 'Remainder', ProcessingOrder = 1, Sequencing = 'Manual', Handling0Amount = 'CreateInvoice'),
            new BillingTreatmentItem(Name = 'BSG TQ Other Item', BillingTreatmentId = otherArrears.Id, BillingType = 'Arrears', Controller = 'BillingScheduleGroup', Status = 'Draft', Type = 'Remainder', ProcessingOrder = 1, Sequencing = 'Manual', Handling0Amount = 'CreateInvoice')
        };
        List<BillingTreatmentItem> items = [SELECT Id FROM BillingTreatmentItem WHERE Name LIKE 'BSG TQ%'];
        for (BillingTreatmentItem item : items) {
            item.Status = 'Active';
        }
        update items;
        List<BillingTreatment> treatments = [SELECT Id FROM BillingTreatment WHERE Name LIKE 'BSG TQ%'];
        for (BillingTreatment t : treatments) {
            t.Status = 'Active';
        }
        update treatments;

        Test.startTest();
        Id foundArrears = RLM_BillingScheduleGroupService.findBillingTreatmentId(le.Id, 'Arrears', cur);
        Id foundAdvance = RLM_BillingScheduleGroupService.findBillingTreatmentId(le.Id, 'Advance', cur);
        Test.stopTest();

        Assert.areEqual(arrears.Id, foundArrears, 'The chosen entity\'s Arrears treatment is found, not another entity\'s.');
        Assert.areEqual(advance.Id, foundAdvance, 'The Advance treatment of the same entity is found for Advance.');
    }

    // ---- result parser ----

    @isTest
    static void parseCreateResult_prefersSingleScheduleIdOverList() {
        Id single = fakeId(BillingSchedule.SObjectType);
        Id other = Id.valueOf(BillingSchedule.SObjectType.getDescribe().getKeyPrefix() + '000000000001');
        RLM_BillingScheduleGroupService.CreateResult r = RLM_BillingScheduleGroupService.parseCreateResult(
            new Map<String, Object>{
                'billingScheduleId' => single,
                'billingScheduleIds' => new List<Object>{ other }
            });
        Assert.areEqual(single, r.billingScheduleId, 'billingScheduleId wins when both are present.');
    }

    @isTest
    static void parseCreateResult_ignoresEmptyOrNonListScheduleIds() {
        RLM_BillingScheduleGroupService.CreateResult emptyList = RLM_BillingScheduleGroupService.parseCreateResult(
            new Map<String, Object>{ 'billingScheduleIds' => new List<Object>() });
        Assert.isNull(emptyList.billingScheduleId, 'An empty id list yields no schedule id.');

        RLM_BillingScheduleGroupService.CreateResult notAList = RLM_BillingScheduleGroupService.parseCreateResult(
            new Map<String, Object>{ 'billingScheduleIds' => 'not-a-list' });
        Assert.isNull(notAList.billingScheduleId, 'A non-list value yields no schedule id.');
    }

    @isTest
    static void parseCreateResult_emptyOutputs_leavesFieldsNullButEchoesResponse() {
        RLM_BillingScheduleGroupService.CreateResult r =
            RLM_BillingScheduleGroupService.parseCreateResult(new Map<String, Object>());
        Assert.isNull(r.requestId);
        Assert.isNull(r.statusUrl);
        Assert.isNull(r.billingScheduleGroupId);
        Assert.isNull(r.billingScheduleId);
        Assert.areEqual('{}', r.apiResponse, 'The (empty) action output is still echoed.');
    }

    // ---- helpers ----

    // Inputs for createBillingScheduleGroupAndScheduleViaAPI that pass every guard; a test
    // overrides one field to drive one guard.
    private class CreateArgs {
        public Id billingAccountId;
        public String billingTermUnit = 'Month';
        public Integer billingTerm = 12;
        public String billingType = 'Advance';
        public Decimal quantity = 2;
        public Id legalEntityId = fakeId(LegalEntity.SObjectType);
        public Id taxTreatmentId = fakeId(TaxTreatment.SObjectType);
        public String currencyIsoCode = 'USD';
        public Decimal unitPrice = 10;
        public Decimal totalPrice = 240;
        public String billingCity = 'San Francisco';
        public Id productId = fakeId(Product2.SObjectType);
        public String productName = 'Widget';
        public Date startDate = Date.newInstance(2026, 1, 1);
        public Integer billingDayOfMonth = 1;
        public Integer billingStartMonth = 1;
        public String termSetting = 'Termed';
        public Date endDate = Date.newInstance(2026, 12, 31);

        public CreateArgs(Id billingAccountId) {
            this.billingAccountId = billingAccountId;
        }

        public RLM_BillingScheduleGroupService.CreateResult call() {
            seedTreatment();
            return RLM_BillingScheduleGroupService.createBillingScheduleGroupAndScheduleViaAPI(
                billingAccountId, billingTermUnit, billingTerm, billingType, quantity, legalEntityId,
                taxTreatmentId, currencyIsoCode, unitPrice, totalPrice, billingCity, productId,
                productName, startDate, billingDayOfMonth, billingStartMonth, termSetting, endDate
            );
        }
    }

    // A treatment the lookup finds, unless a test has set its own candidates.
    private static void seedTreatment() {
        if (RLM_BillingScheduleGroupService.mockTreatmentCandidates == null) {
            RLM_BillingScheduleGroupService.mockTreatmentCandidates = candidates(
                new RLM_BillingScheduleGroupService.TreatmentCandidate(
                    fakeId(BillingTreatment.SObjectType), 'Advance', 'USD'));
        }
    }

    private static List<RLM_BillingScheduleGroupService.TreatmentCandidate> candidates(
            RLM_BillingScheduleGroupService.TreatmentCandidate one) {
        return new List<RLM_BillingScheduleGroupService.TreatmentCandidate>{ one };
    }

    private static Boolean throwsAura(CreateArgs args) {
        try {
            args.call();
            return false;
        } catch (AuraHandledException e) {
            return true;
        }
    }

    private static Id insertBillingAccount(String name) {
        Account a = new Account(Name = name + ' Acct');
        insert a;
        BillingAccount ba = new BillingAccount(Name = name + ' BA', AccountId = a.Id);
        insert ba;
        return ba.Id;
    }

    private static Map<String, Object> onlyTransaction(String payload) {
        Map<String, Object> wrapper = (Map<String, Object>) System.JSON.deserializeUntyped(payload);
        List<Object> txns = (List<Object>) wrapper.get('Transaction');
        Assert.areEqual(1, txns.size(), 'The payload carries exactly one transaction.');
        return (Map<String, Object>) txns[0];
    }

    private static String sellingModelFor(String termSetting) {
        Map<String, Object> txn = onlyTransaction(RLM_BillingScheduleGroupService.buildTransactionDetailsJson(
            fakeId(Account.SObjectType), fakeId(BillingAccount.SObjectType), 'Month', 1,
            fakeId(LegalEntity.SObjectType), fakeId(TaxTreatment.SObjectType), 'USD', 10, 10,
            'Boston', fakeId(Product2.SObjectType), 'Widget', Date.newInstance(2026, 1, 1), 1, 1,
            termSetting, null, null, null, 'Boston'
        ));
        return (String) txn.get('SellingModelType__std');
    }

    // deserializeUntyped returns whole numbers as Integer and fractions as Decimal.
    private static Decimal toDecimal(Object value) {
        return value == null ? null : Decimal.valueOf(String.valueOf(value));
    }

    // The BillingSchedule field's picklist entries as "label|value", in describe order. The
    // field and its values ship with the Billing license, so both are preconditions.
    private static List<String> picklistLabelsAndValues(String fieldApi) {
        Map<String, Schema.SObjectField> fields = BillingSchedule.SObjectType.getDescribe().fields.getMap();
        Assert.isTrue(fields.containsKey(fieldApi), 'PRECONDITION: BillingSchedule.' + fieldApi + ' exists.');
        List<String> entries = new List<String>();
        for (Schema.PicklistEntry pe : fields.get(fieldApi).getDescribe().getPicklistValues()) {
            entries.add(pe.getLabel() + '|' + pe.getValue());
        }
        Assert.isFalse(entries.isEmpty(), 'PRECONDITION: BillingSchedule.' + fieldApi + ' has picklist values.');
        return entries;
    }

    private static void assertOptions(List<String> expected,
            List<RLM_BillingScheduleGroupService.PicklistOption> actual) {
        List<String> actualEntries = new List<String>();
        for (RLM_BillingScheduleGroupService.PicklistOption o : actual) {
            actualEntries.add(o.label + '|' + o.value);
        }
        Assert.areEqual(expected, actualEntries, 'Option labels and values must match the picklist, in order.');
    }

    private static Boolean throwsViaApi(Id billingAccountId) {
        seedTreatment();
        try {
            RLM_BillingScheduleGroupService.createBillingScheduleGroupAndScheduleViaAPI(
                billingAccountId, 'Month', 1, 'Advance', 1, fakeId(LegalEntity.SObjectType),
                fakeId(TaxTreatment.SObjectType), 'USD', 10, 10, 'San Francisco',
                fakeId(Product2.SObjectType), 'Widget', Date.today(), 1, 1, 'Evergreen', null
            );
            return false;
        } catch (AuraHandledException e) {
            return true;
        }
    }
}
