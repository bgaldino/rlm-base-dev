/**
 * Tests for RLM_BillingScheduleGroupService.
 *
 * The native standard-action invoke (createBillingSchedulesFromTrxn) is not run in
 * these tests: the create-via-API path is covered through the @TestVisible mock seam
 * (mockActionOutputs) plus direct coverage of the pure payload-build and result-parse
 * helpers, so the real invoke and its failed-result handling stay uncovered.
 * Validation guards are covered by asserting AuraHandledException on bad input.
 * The System.runAs tests create their users through RLM_BillingUITestUsers, which takes a
 * Billing permission set license seat; createWithBillingAccess adds a permission set with only
 * the object and field grants a test names, so a refused read can be exercised.
 * The other tests run as the deploying admin and read Account, BillingAccount,
 * AccountBillingAccount, Product2, LegalEntity and TaxTreatment in USER_MODE. On a
 * Release 264 org the System Administrator profile's ObjectPermissions grant read on all six
 * (read from the org, not from a test run). The create path also reads CurrencyType, and
 * findBillingTreatmentId_* read BillingTreatment and BillingTreatmentItem, in USER_MODE.
 *
 * Payload (the create path sends what the modal chose): the legal entity (LegalEntityId__std), the
 * billing term when one is given (BillingTerm__std), the billing treatment that carries the chosen
 * Advance or Arrears timing for that legal entity (BillingTreatmentId__std; BillingType__std and
 * BillingTypePicklistTiming__std are rejected by the action, measured), and a shipping city
 * (ShippingCity__std: the account's, else the billingCity the caller submitted). The treatment
 * query is replaced by mockTreatmentCandidates in most tests; findBillingTreatmentId_* reads real
 * records, and lastTransactionDetails exposes the payload handed to the action. Still not sent: bill-to
 * contact, payment term (the action reads them from the records through the context mapping, as
 * measured earlier on a 264 org) and ParentTransactionId__std (Required for TermDefined only). The
 * action refuses a billing account with no bill-to contact, so create refuses it first (billToContact_*)
 * and every billing account that reaches the action in these tests carries one (billToContact()).
 * buildTransactionDetailsJson_mapsInputsToStandardContextFields pins the payload's exact key set.
 *
 * Fixed: a one-time charge from the Create Billing Schedule Group modal (billing term unit
 * 'OneTime', termSetting 'Evergreen' or a leftover 'Termed') is sent as SellingModelType__std
 * 'OneTime' with no EndDate__std, as the 264 developer guide requires. The service derives it from
 * the billing term unit. See the buildTransactionDetailsJson_oneTime* tests.
 *
 * Fixed: getAccountBillingInfo picks the account's default billing profile first, then the oldest
 * billing account (ORDER BY IsDefaultBillingProfile DESC, CreatedDate, Id), and
 * resolves one linked only through AccountBillingAccount; getLegalEntities offers only Active
 * records and getTaxTreatments only Active ones of the chosen legal entity; the create path
 * rejects a null total price and a Termed recurring create with no end date.
 */
@isTest
private class RLM_BillingScheduleGroupServiceTest {
    // The create path validates the charge currency against the org's active CurrencyType, so the tests
    // that reach it use the org's default currency; OTHER_CUR is any different code (candidates only).
    private static final String CUR = UserInfo.getDefaultCurrency();
    private static final String OTHER_CUR = CUR == 'EUR' ? 'GBP' : 'EUR';

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
        BillingAccount ba = new BillingAccount(Name = 'BSG ViaApi BA', AccountId = a.Id, BillToContactId = billToContact(a.Id));
        insert ba;

        RLM_BillingScheduleGroupService.mockActionOutputs = new Map<String, Object>{
            'requestId' => 'REQ-PLACEHOLDER',
            'statusUrl' => '/services/data/v68.0/sobjects/AsyncOperationTracker/REQ-PLACEHOLDER'
        };
        seedTreatment();

        Test.startTest();
        RLM_BillingScheduleGroupService.CreateResult r =
            RLM_BillingScheduleGroupService.createBillingScheduleGroupAndScheduleViaAPI(
                ba.Id, 'Month', 12, 'Advance', 2, activeLegalEntityId(),
                activeTaxTreatmentId(), CUR, 10, 240, 'San Francisco',
                softwareProductId(), 'Widget', Date.newInstance(2026, 1, 1),
                1, 1, 'Termed', Date.newInstance(2026, 12, 31), null
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
        Assert.areEqual('Austin', info.billingCity, 'Billing city comes from the requested account.');
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
        Assert.isNull(info.billingCity, 'No billing account resolved -> no city is returned.');
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
    static void getTaxTreatments_returnsActiveOfTheChosenEntity() {
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
            RLM_BillingScheduleGroupService.getTaxTreatments(le3.Id);
        List<RLM_BillingScheduleGroupService.TaxTreatmentOption> draftEntity =
            RLM_BillingScheduleGroupService.getTaxTreatments(le1.Id);
        List<RLM_BillingScheduleGroupService.TaxTreatmentOption> noEntity =
            RLM_BillingScheduleGroupService.getTaxTreatments(null);
        Test.stopTest();

        Assert.isTrue(draftEntity.isEmpty(), 'An entity whose only treatment is Draft offers none.');
        Assert.isTrue(noEntity.isEmpty(), 'No legal entity chosen offers no treatment.');
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
            RLM_BillingScheduleGroupService.getTaxTreatments(fakeId(LegalEntity.SObjectType));
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
    // junction row is what lets the create through, and the payload carries the linked account.
    @isTest
    static void createViaAPI_billingAccountLinkedThroughJunction_isAccepted() {
        Account a = new Account(Name = 'BSG Junction Create Acct');
        insert a;
        BillingAccount ba = new BillingAccount(Name = 'BSG Junction Create BA', BillToContactId = billToContact(a.Id));
        insert ba;
        insert new AccountBillingAccount(AccountId = a.Id, BillingAccountId = ba.Id);
        Assert.isNull([SELECT AccountId FROM BillingAccount WHERE Id = :ba.Id].AccountId,
            'PRECONDITION: inserting the junction row does not set BillingAccount.AccountId.');
        RLM_BillingScheduleGroupService.mockActionOutputs = new Map<String, Object>{ 'requestId' => 'REQ-JN' };

        Test.startTest();
        RLM_BillingScheduleGroupService.CreateResult r = new CreateArgs(ba.Id).call();
        Test.stopTest();

        Assert.areEqual('REQ-JN', r.requestId, 'A billing account linked through the junction row is accepted.');
        Assert.areEqual(String.valueOf(a.Id),
            onlyTransaction(RLM_BillingScheduleGroupService.lastTransactionDetails).get('AccountId__std'),
            'The linked account is the account sent.');
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

    // ---- bill-to contact ----

    // The create action refuses a billing account with no bill-to contact (REQUIRED_FIELD_MISSING
    // billToContact, measured on a 264 org), and the user then got only the generic failure sentence.
    // getAccountBillingInfo flags it so the modal blocks Create, and create refuses it with the same
    // sentence before the action is called. The control call with a contact set passes, so the refusal
    // is the missing contact alone.
    @isTest
    static void billToContact_missing_isFlaggedAndRefusedBeforeTheAction() {
        Account a = new Account(Name = 'BSG No Bill To Acct', BillingCity = 'Austin');
        insert a;
        BillingAccount ba = new BillingAccount(Name = 'BSG No Bill To BA', AccountId = a.Id);
        insert ba;
        RLM_BillingScheduleGroupService.mockActionOutputs = new Map<String, Object>{ 'requestId' => 'REQ-BT' };

        Test.startTest();
        RLM_BillingScheduleGroupService.AccountInfo before = RLM_BillingScheduleGroupService.getAccountBillingInfo(a.Id);
        AuraHandledException refused;
        try {
            new CreateArgs(ba.Id).call();
        } catch (AuraHandledException e) {
            refused = e;
        }
        String detailsWithoutContact = RLM_BillingScheduleGroupService.lastTransactionDetails;
        ba.BillToContactId = billToContact(a.Id);
        update ba;
        RLM_BillingScheduleGroupService.AccountInfo after = RLM_BillingScheduleGroupService.getAccountBillingInfo(a.Id);
        RLM_BillingScheduleGroupService.CreateResult control = new CreateArgs(ba.Id).call();
        Test.stopTest();

        Assert.areEqual(ba.Id, before.billingAccountId, 'PRECONDITION: the billing account is found.');
        Assert.isTrue(before.billToContactMissing, 'A billing account with no bill-to contact is flagged.');
        Assert.isNotNull(refused, 'Create refuses a billing account with no bill-to contact.');
        Assert.areEqual(RLM_BillingScheduleGroupService.BILL_TO_CONTACT_MISSING_MESSAGE, refused.getMessage(),
            'The refusal says what is missing and where to add it.');
        Assert.areEqual(
            'The billing account has no Bill To Contact. Add one to the billing account before creating a billing schedule group.',
            refused.getMessage(), 'The sentence the modal shows too.');
        Assert.isNull(detailsWithoutContact, 'Nothing reached the action.');
        Assert.isFalse(after.billToContactMissing, 'A billing account with a bill-to contact is not flagged.');
        Assert.areEqual('REQ-BT', control.requestId, 'With a bill-to contact the same call reaches the action.');
    }

    // No billing account: nothing to flag.
    @isTest
    static void billToContact_noBillingAccount_isNotFlagged() {
        Account a = new Account(Name = 'BSG No BA Bill To Acct');
        insert a;
        Test.startTest();
        RLM_BillingScheduleGroupService.AccountInfo info = RLM_BillingScheduleGroupService.getAccountBillingInfo(a.Id);
        Test.stopTest();
        Assert.isNull(info.billingAccountId, 'PRECONDITION: no billing account.');
        Assert.isFalse(info.billToContactMissing, 'With no billing account the bill-to contact is not flagged.');
    }

    // BillToContactId is permissionable: a user who reads the billing account but not that field gets a
    // sentence naming the bill-to contact, not the generic failure and not a raw QueryException. The
    // second user holds the field read RLM_BillingUI grants, and the same call returns the flag.
    // Measured on a 264 org: the field read alone is not enough, it also needs Contact read (which
    // RLM_BillingUI grants); without it the select is refused as if the field were not granted.
    @isTest
    static void billToContact_fieldReadRefused_namesTheBillToContact() {
        Account a = new Account(Name = 'BSG Bill To FLS Acct', BillingCity = 'Austin');
        insert a;
        BillingAccount ba = new BillingAccount(Name = 'BSG Bill To FLS BA', AccountId = a.Id);
        insert ba;
        List<String> psl = new List<String>{ RLM_BillingUITestUsers.BILLING_PSL };
        User noFieldRead = RLM_BillingUITestUsers.createWithBillingAccess(psl, new List<String>{ 'Contact' },
            new List<String>{ 'BillingAccount', 'Account' }, new List<String>{ 'Account.BillingAddress' });
        User fieldRead = RLM_BillingUITestUsers.createWithBillingAccess(psl, new List<String>{ 'Contact' },
            new List<String>{ 'BillingAccount', 'Account' },
            new List<String>{ 'Account.BillingAddress', 'BillingAccount.BillToContactId' });

        AuraHandledException refused;
        RLM_BillingScheduleGroupService.AccountInfo granted;
        Test.startTest();
        System.runAs(noFieldRead) {
            Assert.isFalse(userModeQueryFails('SELECT Id FROM BillingAccount LIMIT 1'),
                'PRECONDITION: the user reads BillingAccount.');
            Assert.isTrue(userModeQueryFails('SELECT BillToContactId FROM BillingAccount LIMIT 1'),
                'PRECONDITION: the user cannot read BillingAccount.BillToContactId.');
            try {
                RLM_BillingScheduleGroupService.getAccountBillingInfo(a.Id);
            } catch (AuraHandledException e) {
                refused = e;
            }
        }
        System.runAs(fieldRead) {
            Assert.isFalse(userModeQueryFails('SELECT BillToContactId FROM BillingAccount LIMIT 1'),
                'PRECONDITION: with the field grant and Contact read the user reads BillToContactId.');
            granted = RLM_BillingScheduleGroupService.getAccountBillingInfo(a.Id);
        }
        Test.stopTest();

        Assert.isNotNull(refused, 'A refused bill-to contact read is reported.');
        Assert.areEqual(
            'You do not have access to read the bill-to contact of the billing account this screen needs. Contact your administrator.',
            refused.getMessage(), 'It names the field that could not be read.');
        Assert.isInstanceOfType(refused.getCause(), QueryException.class, 'The query error is kept as the cause');
        Assert.areEqual(ba.Id, granted.billingAccountId, 'With the field read the billing account is returned.');
        Assert.isTrue(granted.billToContactMissing, 'And its missing bill-to contact is flagged.');
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
        BillingAccount ba = new BillingAccount(Name = 'BSG Payload BA', AccountId = a.Id, BillToContactId = billToContact(a.Id));
        insert ba;
        Id leId = activeLegalEntityId();
        Id trId = fakeId(BillingTreatment.SObjectType);
        RLM_BillingScheduleGroupService.mockActionOutputs = new Map<String, Object>{ 'requestId' => 'REQ-P' };
        RLM_BillingScheduleGroupService.mockTreatmentCandidates = candidates(
            new RLM_BillingScheduleGroupService.TreatmentCandidate(trId, 'Arrears', CUR));
        CreateArgs args = new CreateArgs(ba.Id);
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
            'No active billing treatment bills in arrears in ' + CUR + ' for legal entity ' + TEST_LEGAL_ENTITY + '. '
            + 'Choose another legal entity, timing or currency, or ask your administrator to set one up.',
            thrown.getMessage());
        Assert.isNull(RLM_BillingScheduleGroupService.lastTransactionDetails, 'Nothing reached the action.');
    }

    @isTest
    static void createViaAPI_timingRules() {
        Id baId = insertBillingAccount('BSG Timing');
        RLM_BillingScheduleGroupService.mockActionOutputs = new Map<String, Object>{ 'requestId' => 'REQ-T' };
        Id oneTimeTreatment = fakeId(BillingTreatment.SObjectType);
        RLM_BillingScheduleGroupService.mockTreatmentCandidates = candidates(
            new RLM_BillingScheduleGroupService.TreatmentCandidate(oneTimeTreatment, 'Advance', CUR));

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
        Assert.areEqual(String.valueOf(oneTimeTreatment), txn.get('BillingTreatmentId__std'),
            'A one-time charge with no timing still sends the legal entity treatment in its currency.');
        Assert.isFalse(txn.containsKey('BillingTerm__std'), 'No billing term given, none sent.');
    }

    @isTest
    static void createViaAPI_noTreatmentInTheChargeCurrency_isRefusedNamingCurrency() {
        Id baId = insertBillingAccount('BSG Other Currency');
        RLM_BillingScheduleGroupService.mockActionOutputs = new Map<String, Object>{ 'requestId' => 'REQ-C' };
        RLM_BillingScheduleGroupService.mockTreatmentCandidates = candidates(
            new RLM_BillingScheduleGroupService.TreatmentCandidate(fakeId(BillingTreatment.SObjectType), 'Arrears', OTHER_CUR));
        CreateArgs args = new CreateArgs(baId);
        args.billingType = 'Arrears';
        args.currencyIsoCode = CUR;

        AuraHandledException thrown;
        Test.startTest();
        try {
            args.call();
        } catch (AuraHandledException e) {
            thrown = e;
        }
        Test.stopTest();

        Assert.isNotNull(thrown, 'A treatment in another currency is refused, not paired with the charge.');
        Assert.isTrue(thrown.getMessage().contains('arrears in ' + CUR), 'The message names the timing and currency.');
        Assert.isNull(RLM_BillingScheduleGroupService.lastTransactionDetails, 'Nothing reached the action.');
    }

    @isTest
    static void createViaAPI_oneTimeNoTreatmentInTheChargeCurrency_isRefusedWithoutATimingWord() {
        Id baId = insertBillingAccount('BSG One-Time Other Currency');
        RLM_BillingScheduleGroupService.mockActionOutputs = new Map<String, Object>{ 'requestId' => 'REQ-OC' };
        RLM_BillingScheduleGroupService.mockTreatmentCandidates = candidates(
            new RLM_BillingScheduleGroupService.TreatmentCandidate(fakeId(BillingTreatment.SObjectType), 'Advance', OTHER_CUR));
        CreateArgs args = new CreateArgs(baId);
        args.billingTermUnit = 'OneTime';
        args.billingType = null;
        args.billingTerm = null;
        args.termSetting = 'Evergreen';
        args.endDate = null;
        args.currencyIsoCode = CUR;

        AuraHandledException thrown;
        Test.startTest();
        try {
            args.call();
        } catch (AuraHandledException e) {
            thrown = e;
        }
        Test.stopTest();

        Assert.isNotNull(thrown, 'A one-time charge with only another currency treatment is refused.');
        Assert.areEqual(
            'No active billing treatment bills in ' + CUR + ' for legal entity ' + TEST_LEGAL_ENTITY + '. '
            + 'Choose another legal entity or currency, or ask your administrator to set one up.',
            thrown.getMessage(), 'No timing word for a one-time charge, in either sentence.');
        Assert.isNull(RLM_BillingScheduleGroupService.lastTransactionDetails, 'Nothing reached the action.');
    }

    @isTest
    static void chooseTreatment_oneTime_prefersAdvanceOnlyThenArrearsOnlyThenMixed() {
        String prefix = BillingTreatment.SObjectType.getDescribe().getKeyPrefix();
        Id mixed = Id.valueOf(prefix + '000000000001');
        Id arrearsOnly = Id.valueOf(prefix + '000000000002');
        Id advanceOnly = Id.valueOf(prefix + '000000000003');
        Id otherCurrencyAdvance = Id.valueOf(prefix + '000000000004');
        RLM_BillingScheduleGroupService.TreatmentCandidate mixedArrears =
            new RLM_BillingScheduleGroupService.TreatmentCandidate(mixed, 'Arrears', 'USD');
        RLM_BillingScheduleGroupService.TreatmentCandidate mixedAdvance =
            new RLM_BillingScheduleGroupService.TreatmentCandidate(mixed, 'Advance', 'USD');
        RLM_BillingScheduleGroupService.TreatmentCandidate arrearsRow =
            new RLM_BillingScheduleGroupService.TreatmentCandidate(arrearsOnly, 'Arrears', 'USD');
        RLM_BillingScheduleGroupService.TreatmentCandidate advanceRow =
            new RLM_BillingScheduleGroupService.TreatmentCandidate(advanceOnly, 'Advance', 'USD');
        RLM_BillingScheduleGroupService.TreatmentCandidate otherRow =
            new RLM_BillingScheduleGroupService.TreatmentCandidate(otherCurrencyAdvance, 'Advance', 'EUR');
        List<RLM_BillingScheduleGroupService.TreatmentCandidate> all = new List<RLM_BillingScheduleGroupService.TreatmentCandidate>{
            otherRow, mixedArrears, mixedAdvance, arrearsRow, advanceRow
        };
        Assert.areEqual(advanceOnly, RLM_BillingScheduleGroupService.chooseTreatment(all, true, null, 'USD').chosen,
            'An Advance-only treatment beats an older mixed one and an Arrears-only one.');
        Assert.areEqual(arrearsOnly, RLM_BillingScheduleGroupService.chooseTreatment(
            new List<RLM_BillingScheduleGroupService.TreatmentCandidate>{ mixedArrears, mixedAdvance, arrearsRow }, true, null, 'USD').chosen,
            'With no Advance-only treatment, an Arrears-only one beats a mixed one.');
        Assert.areEqual(mixed, RLM_BillingScheduleGroupService.chooseTreatment(
            new List<RLM_BillingScheduleGroupService.TreatmentCandidate>{ mixedArrears, mixedAdvance }, true, null, 'USD').chosen,
            'A mixed treatment is the last resort.');
        Assert.isNull(RLM_BillingScheduleGroupService.chooseTreatment(all, true, null, 'GBP').chosen, 'No treatment in the currency.');
    }

    @isTest
    static void chooseTreatment_onlyAmbiguousFits_reportsTheSkippedTreatment() {
        Id ambiguous = fakeId(BillingTreatment.SObjectType);
        List<RLM_BillingScheduleGroupService.TreatmentCandidate> rows = new List<RLM_BillingScheduleGroupService.TreatmentCandidate>{
            new RLM_BillingScheduleGroupService.TreatmentCandidate(ambiguous, 'Arrears', 'USD'),
            new RLM_BillingScheduleGroupService.TreatmentCandidate(ambiguous, 'Advance', 'USD')
        };
        RLM_BillingScheduleGroupService.TreatmentChoice choice =
            RLM_BillingScheduleGroupService.chooseTreatment(rows, false, 'Arrears', 'USD');
        Assert.isNull(choice.chosen, 'The only candidate is ambiguous, so none is chosen.');
        Assert.areEqual(ambiguous, choice.skippedAmbiguous, 'The skipped treatment is reported.');
        Assert.isNull(RLM_BillingScheduleGroupService.chooseTreatment(rows, false, 'Arrears', 'EUR').skippedAmbiguous,
            'An ambiguous treatment in another currency is not reported.');
        Assert.areEqual(ambiguous, RLM_BillingScheduleGroupService.chooseTreatment(rows, true, null, 'USD').chosen,
            'For a one-time charge the same treatment is fine.');
    }

    @isTest
    static void createViaAPI_onlyAnAmbiguousTreatment_isRefusedAsNeedingASplit() {
        Id baId = insertBillingAccount('BSG Ambiguous');
        RLM_BillingScheduleGroupService.mockActionOutputs = new Map<String, Object>{ 'requestId' => 'REQ-AM' };
        Id ambiguous = fakeId(BillingTreatment.SObjectType);
        RLM_BillingScheduleGroupService.mockTreatmentCandidates = new List<RLM_BillingScheduleGroupService.TreatmentCandidate>{
            new RLM_BillingScheduleGroupService.TreatmentCandidate(ambiguous, 'Arrears', CUR),
            new RLM_BillingScheduleGroupService.TreatmentCandidate(ambiguous, 'Advance', CUR)
        };
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

        Assert.isNotNull(thrown, 'A treatment with both timings is refused for a recurring charge.');
        Assert.areEqual(
            'The billing treatment of legal entity ' + TEST_LEGAL_ENTITY + ' has items in both advance and arrears, so it '
            + 'cannot be matched to arrears in ' + CUR + '. Split it into one treatment per timing, or choose another '
            + 'legal entity or currency.',
            thrown.getMessage(), 'The message says why, not that none exists.');
        Assert.isNull(RLM_BillingScheduleGroupService.lastTransactionDetails, 'Nothing reached the action.');
    }

    // The picker offers only active legal entities the user can see; an id that is neither is refused
    // before the treatment lookup, which would otherwise answer for it.
    @isTest
    static void createViaAPI_legalEntityInactiveOrNotFound_isRefused() {
        Id baId = insertBillingAccount('BSG Legal Entity Refused');
        RLM_BillingScheduleGroupService.mockActionOutputs = new Map<String, Object>{ 'requestId' => 'REQ-LE' };
        LegalEntity inactive = new LegalEntity(Name = 'BSG Inactive LE', Status = 'Inactive');
        insert inactive;
        Map<String, Id> cases = new Map<String, Id>{
            'An inactive legal entity' => inactive.Id,
            'A legal entity that does not exist' => fakeId(LegalEntity.SObjectType)
        };

        Test.startTest();
        for (String label : cases.keySet()) {
            CreateArgs args = new CreateArgs(baId);
            args.legalEntityId = cases.get(label);
            AuraHandledException thrown;
            try {
                args.call();
            } catch (AuraHandledException e) {
                thrown = e;
            }
            Assert.isNotNull(thrown, label + ' is refused.');
            Assert.areEqual(
                'The legal entity was not found, is not active, or is not visible to you. Choose another legal entity.',
                thrown.getMessage(), label + ' gets the legal entity refusal.');
        }
        Test.stopTest();

        Assert.isNull(RLM_BillingScheduleGroupService.lastTransactionDetails, 'Nothing reached the action.');
    }

    @isTest
    static void createViaAPI_oneTimeIgnoresATimingSent() {
        Id baId = insertBillingAccount('BSG One-Time Timing');
        RLM_BillingScheduleGroupService.mockActionOutputs = new Map<String, Object>{ 'requestId' => 'REQ-OT' };
        Id arrears = fakeId(BillingTreatment.SObjectType);
        Id advance = Id.valueOf(BillingTreatment.SObjectType.getDescribe().getKeyPrefix() + '000000000001');
        RLM_BillingScheduleGroupService.mockTreatmentCandidates = new List<RLM_BillingScheduleGroupService.TreatmentCandidate>{
            new RLM_BillingScheduleGroupService.TreatmentCandidate(arrears, 'Arrears', CUR),
            new RLM_BillingScheduleGroupService.TreatmentCandidate(advance, 'Advance', CUR)
        };
        CreateArgs args = new CreateArgs(baId);
        args.billingTermUnit = 'OneTime';
        args.billingType = 'Arrears';
        args.billingTerm = null;
        args.termSetting = 'Evergreen';
        args.endDate = null;

        Test.startTest();
        args.call();
        Test.stopTest();

        Assert.areEqual(String.valueOf(advance),
            onlyTransaction(RLM_BillingScheduleGroupService.lastTransactionDetails).get('BillingTreatmentId__std'),
            'A one-time charge takes the one-time rule\'s treatment (Advance preferred); the timing sent is ignored.');
    }

    @isTest
    static void createViaAPI_inactiveOrUnknownCurrency_isRefusedBeforeTheTreatmentLookup() {
        Id baId = insertBillingAccount('BSG Bad Currency');
        RLM_BillingScheduleGroupService.mockActionOutputs = new Map<String, Object>{ 'requestId' => 'REQ-BC' };
        // A lookup that ran first would find nothing and give another message, so the message proves the order.
        RLM_BillingScheduleGroupService.mockTreatmentCandidates =
            new List<RLM_BillingScheduleGroupService.TreatmentCandidate>();
        CreateArgs args = new CreateArgs(baId);
        args.currencyIsoCode = 'ZZZ';

        AuraHandledException thrown;
        Test.startTest();
        try {
            args.call();
        } catch (AuraHandledException e) {
            thrown = e;
        }
        Test.stopTest();

        Assert.isNotNull(thrown, 'A currency that is not an active CurrencyType is refused.');
        Assert.areEqual('Currency ZZZ is not an active currency in this org. Choose another currency.', thrown.getMessage());
        Assert.isNull(RLM_BillingScheduleGroupService.lastTransactionDetails, 'Nothing reached the action.');
    }

    // The account page the modal opened on is the account sent when it is linked to the billing account,
    // whether the billing account is its own or reaches it through AccountBillingAccount.
    @isTest
    static void createViaAPI_pageAccount_isTheAccountSentWhenLinked() {
        Account own = new Account(Name = 'BSG Page Own', ShippingCity = 'Own City');
        Account linked = new Account(Name = 'BSG Page Linked', ShippingCity = 'Linked City');
        Account unrelated = new Account(Name = 'BSG Page Unrelated', ShippingCity = 'Other City');
        insert new List<Account>{ own, linked, unrelated };
        BillingAccount ba = new BillingAccount(Name = 'BSG Page BA', AccountId = own.Id, BillToContactId = billToContact(own.Id));
        insert ba;
        insert new AccountBillingAccount(AccountId = linked.Id, BillingAccountId = ba.Id);
        RLM_BillingScheduleGroupService.mockActionOutputs = new Map<String, Object>{ 'requestId' => 'REQ-PG' };

        Test.startTest();
        CreateArgs viaLink = new CreateArgs(ba.Id);
        viaLink.pageAccountId = linked.Id;
        viaLink.call();
        Map<String, Object> linkedTxn = onlyTransaction(RLM_BillingScheduleGroupService.lastTransactionDetails);

        CreateArgs viaOwn = new CreateArgs(ba.Id);
        viaOwn.pageAccountId = own.Id;
        viaOwn.call();
        Map<String, Object> ownTxn = onlyTransaction(RLM_BillingScheduleGroupService.lastTransactionDetails);

        CreateArgs viaUnrelated = new CreateArgs(ba.Id);
        viaUnrelated.pageAccountId = unrelated.Id;
        AuraHandledException unrelatedRefusal;
        try {
            viaUnrelated.call();
        } catch (AuraHandledException e) {
            unrelatedRefusal = e;
        }
        Test.stopTest();

        Assert.areEqual(String.valueOf(linked.Id), linkedTxn.get('AccountId__std'), 'The linked page account is sent.');
        Assert.areEqual('Linked City', linkedTxn.get('ShippingCity__std'), 'Its shipping city is read.');
        Assert.areEqual(String.valueOf(own.Id), ownTxn.get('AccountId__std'), 'The billing account\'s own account stays.');
        Assert.areEqual('Own City', ownTxn.get('ShippingCity__std'));
        Assert.isNotNull(unrelatedRefusal, 'A readable page account with no link to the billing account is refused.');
        Assert.isTrue(unrelatedRefusal.getMessage().contains('is not linked'), unrelatedRefusal.getMessage());
    }

    // A billing account owned by another account is reached from the page account through a link: the
    // billing city the modal shows and submits is the page account's, the account create sends.
    @isTest
    static void getAccountBillingInfoThenCreate_linkedPageAccount_usesThePageAccountsCity() {
        Account owner = new Account(Name = 'BSG Owner', BillingCity = 'Owner City', ShippingCity = 'Owner Ship');
        Account page = new Account(Name = 'BSG Page', BillingCity = 'Page City', ShippingCity = 'Page Ship');
        insert new List<Account>{ owner, page };
        BillingAccount ba = new BillingAccount(Name = 'BSG Owned BA', AccountId = owner.Id, BillToContactId = billToContact(owner.Id));
        insert ba;
        insert new AccountBillingAccount(AccountId = page.Id, BillingAccountId = ba.Id);
        RLM_BillingScheduleGroupService.mockActionOutputs = new Map<String, Object>{ 'requestId' => 'REQ-LC' };

        Test.startTest();
        RLM_BillingScheduleGroupService.AccountInfo info = RLM_BillingScheduleGroupService.getAccountBillingInfo(page.Id);
        CreateArgs args = new CreateArgs(info.billingAccountId);
        args.billingCity = info.billingCity;
        args.pageAccountId = page.Id;
        args.call();
        Test.stopTest();

        Assert.areEqual(ba.Id, info.billingAccountId, 'The linked billing account is found.');
        Assert.areEqual('Page City', info.billingCity, 'The page account\'s city, not the owner\'s.');
        Map<String, Object> txn = onlyTransaction(RLM_BillingScheduleGroupService.lastTransactionDetails);
        Assert.areEqual(String.valueOf(page.Id), txn.get('AccountId__std'));
        Assert.areEqual('Page City', txn.get('BillingCity__std'));
        Assert.areEqual('Page Ship', txn.get('ShippingCity__std'));
    }

    // A page account the user cannot find refuses create instead of being ignored.
    @isTest
    static void createViaAPI_pageAccountNotFound_isRefused() {
        Account own = new Account(Name = 'BSG Own For Missing Page');
        insert own;
        BillingAccount ba = new BillingAccount(Name = 'BSG Missing Page BA', AccountId = own.Id);
        insert ba;
        RLM_BillingScheduleGroupService.mockActionOutputs = new Map<String, Object>{ 'requestId' => 'REQ-NR' };
        CreateArgs args = new CreateArgs(ba.Id);
        args.pageAccountId = fakeId(Account.SObjectType);

        AuraHandledException thrown;
        Test.startTest();
        try {
            args.call();
        } catch (AuraHandledException e) {
            thrown = e;
        }
        Test.stopTest();

        Assert.isNotNull(thrown, 'A page account that is not found is refused.');
        Assert.areEqual('The account you opened this from was not found or is not visible to you.', thrown.getMessage());
        Assert.isNull(RLM_BillingScheduleGroupService.lastTransactionDetails, 'Nothing reached the action.');
    }

    // A user with BillingAccount but no Account read, with a linked page account: create is refused with a
    // handled message, not a raw QueryException. The refusal comes at the billing account read (it selects
    // AccountId), before the page-account read, so the page-account catch is defensive (measured here).
    // Account read is what that select needs: a second user with Account read and no field rows selects it.
    @isTest
    static void createViaAPI_noAccountRead_isRefusedAtTheBillingAccount() {
        Account own = new Account(Name = 'BSG Own Page Read Refused');
        Account page = new Account(Name = 'BSG Page Read Refused');
        insert new List<Account>{ own, page };
        BillingAccount ba = new BillingAccount(Name = 'BSG Page Read Refused BA', AccountId = own.Id);
        insert ba;
        insert new AccountBillingAccount(AccountId = page.Id, BillingAccountId = ba.Id);
        User u = RLM_BillingUITestUsers.createWithBillingAccess(
            new List<String>{ RLM_BillingUITestUsers.BILLING_PSL },
            new List<String>(),
            new List<String>{ 'BillingAccount' },
            new List<String>());
        User withAccountRead = RLM_BillingUITestUsers.createWithBillingAccess(
            new List<String>{ RLM_BillingUITestUsers.BILLING_PSL },
            new List<String>(),
            new List<String>{ 'BillingAccount', 'Account' },
            new List<String>());
        CreateArgs args = new CreateArgs(ba.Id);
        args.pageAccountId = page.Id;

        AuraHandledException thrown;
        Test.startTest();
        System.runAs(u) {
            Assert.isTrue(userModeQueryFails('SELECT Id FROM Account LIMIT 1'),
                'PRECONDITION: the user cannot read Account.');
            Assert.isFalse(userModeQueryFails('SELECT Id FROM BillingAccount LIMIT 1'),
                'PRECONDITION: the user can read BillingAccount (so the failure below is the AccountId select).');
            Assert.isTrue(userModeQueryFails('SELECT AccountId FROM BillingAccount LIMIT 1'),
                'PRECONDITION: selecting BillingAccount.AccountId needs Account read.');
            try {
                args.call();
            } catch (AuraHandledException e) {
                thrown = e;
            }
        }
        System.runAs(withAccountRead) {
            Assert.isFalse(userModeQueryFails('SELECT AccountId FROM BillingAccount LIMIT 1'),
                'PRECONDITION: with Account read (and no field rows) the AccountId select succeeds.');
        }
        Test.stopTest();

        Assert.isNotNull(thrown, 'No Account read refuses create.');
        Assert.isTrue(thrown.getMessage().contains('read the billing account this screen needs'),
            'It names the billing account read: ' + thrown.getMessage());
        Assert.isNull(RLM_BillingScheduleGroupService.lastTransactionDetails, 'Nothing reached the action.');
    }

    // A refused read of the account links refuses create when the page account is not the owner: the
    // city came from the page account, so the owner's account must not be sent silently.
    @isTest
    static void createViaAPI_pageAccountLinkReadRefused_isRefused() {
        Account own = new Account(Name = 'BSG Own Link Refused');
        Account page = new Account(Name = 'BSG Page Link Refused');
        insert new List<Account>{ own, page };
        BillingAccount ba = new BillingAccount(Name = 'BSG Link Refused BA', AccountId = own.Id);
        insert ba;
        insert new AccountBillingAccount(AccountId = page.Id, BillingAccountId = ba.Id);
        User u = RLM_BillingUITestUsers.createWithBillingAccess(
            new List<String>{ RLM_BillingUITestUsers.BILLING_PSL },
            new List<String>(),
            new List<String>{ 'BillingAccount', 'Account' },
            new List<String>{ 'Account.BillingAddress' });
        CreateArgs args = new CreateArgs(ba.Id);
        args.pageAccountId = page.Id;

        AuraHandledException thrown;
        Test.startTest();
        System.runAs(u) {
            Assert.isTrue(userModeQueryFails('SELECT Id FROM AccountBillingAccount LIMIT 1'),
                'PRECONDITION: the user cannot read AccountBillingAccount.');
            try {
                args.call();
            } catch (AuraHandledException e) {
                thrown = e;
            }
        }
        Test.stopTest();

        Assert.isNotNull(thrown, 'A refused link read refuses create.');
        Assert.isTrue(thrown.getMessage().contains('the account links'), 'It names the read: ' + thrown.getMessage());
        Assert.isNull(RLM_BillingScheduleGroupService.lastTransactionDetails, 'Nothing reached the action.');
    }

    // A billing account with no account of its own, for a user who cannot read the links, refuses at
    // the page-account link check when a page account is sent.
    @isTest
    static void createViaAPI_pageAccountLinkReadRefused_isRefusedAtThePageAccountCheck() {
        Account page = new Account(Name = 'BSG Page No Own');
        insert page;
        BillingAccount ba = new BillingAccount(Name = 'BSG No Own Account BA');
        insert ba;
        insert new AccountBillingAccount(AccountId = page.Id, BillingAccountId = ba.Id);
        User u = RLM_BillingUITestUsers.createWithBillingAccess(
            new List<String>{ RLM_BillingUITestUsers.BILLING_PSL },
            new List<String>(),
            new List<String>{ 'BillingAccount', 'Account' },
            new List<String>{ 'Account.BillingAddress' });
        CreateArgs args = new CreateArgs(ba.Id);
        args.pageAccountId = page.Id;

        AuraHandledException thrown;
        Test.startTest();
        System.runAs(u) {
            try {
                args.call();
            } catch (AuraHandledException e) {
                thrown = e;
            }
        }
        Test.stopTest();

        Assert.isNotNull(thrown, 'No own account and no readable links refuses create.');
        Assert.isTrue(thrown.getMessage().contains('the account links'), 'It is the page-account link read: ' + thrown.getMessage());
        Assert.isNull(RLM_BillingScheduleGroupService.lastTransactionDetails, 'Nothing reached the action.');
    }

    // The same user with no page account: the billing account has no account of its own, so the oldest
    // link is read, and that read is refused.
    @isTest
    static void createViaAPI_noOwnAccountNoPageAccountAndLinksRefused_isRefused() {
        Account linked = new Account(Name = 'BSG Linked No Own');
        insert linked;
        BillingAccount ba = new BillingAccount(Name = 'BSG No Own No Page BA');
        insert ba;
        insert new AccountBillingAccount(AccountId = linked.Id, BillingAccountId = ba.Id);
        User u = RLM_BillingUITestUsers.createWithBillingAccess(
            new List<String>{ RLM_BillingUITestUsers.BILLING_PSL },
            new List<String>(),
            new List<String>{ 'BillingAccount', 'Account' },
            new List<String>{ 'Account.BillingAddress' });
        CreateArgs args = new CreateArgs(ba.Id);

        AuraHandledException thrown;
        Test.startTest();
        System.runAs(u) {
            Assert.isTrue(userModeQueryFails('SELECT Id FROM AccountBillingAccount LIMIT 1'),
                'PRECONDITION: the user cannot read AccountBillingAccount.');
            try {
                args.call();
            } catch (AuraHandledException e) {
                thrown = e;
            }
        }
        Test.stopTest();

        Assert.isNotNull(thrown, 'No own account, no page account and no readable links refuses create.');
        Assert.isTrue(thrown.getMessage().contains('the links between the billing account and its accounts'),
            'It is the oldest-link read: ' + thrown.getMessage());
        Assert.isNull(RLM_BillingScheduleGroupService.lastTransactionDetails, 'Nothing reached the action.');
    }

    // Legal entities are private by default (measured on a 264 org). The hidden case of the legal
    // entity read test relies on it: on another org-wide default that case is not checked, so this test
    // fails there instead of letting that gap pass silently. It does not catch a sharing rule that lets
    // the test user read the legal entity on a Private org.
    @isTest
    static void legalEntitiesArePrivateByDefault() {
        String sharingModel = [
            SELECT InternalSharingModel FROM EntityDefinition WHERE QualifiedApiName = 'LegalEntity'
        ].InternalSharingModel;
        Assert.areEqual('Private', sharingModel,
            'The org-wide default for legal entities is ' + sharingModel + ', not Private: the legal '
            + 'entity read test relies on it and does not check the hidden case here.');
    }

    // The legal entity read runs as the user, on an entity the admin owns. With no LegalEntity read it
    // is refused and named. With read but no sharing it is refused as not visible where legal entities
    // are private (else it passes; see legalEntitiesArePrivateByDefault). With view-all it passes and
    // the call reaches the action.
    @isTest
    static void createViaAPI_legalEntityRead_refusedHiddenOrVisible() {
        Account a = new Account(Name = 'BSG LE Read Acct');
        insert a;
        BillingAccount ba = new BillingAccount(Name = 'BSG LE Read BA', AccountId = a.Id, BillToContactId = billToContact(a.Id));
        insert ba;
        User noRead = RLM_BillingUITestUsers.createWithBillingAccess(
            new List<String>{ RLM_BillingUITestUsers.BILLING_PSL },
            new List<String>(),
            new List<String>{ 'BillingAccount', 'Account' },
            new List<String>{ 'Account.BillingAddress', 'Account.ShippingAddress' });
        User readNoSharing = RLM_BillingUITestUsers.createWithBillingAccess(
            new List<String>{ RLM_BillingUITestUsers.BILLING_PSL },
            new List<String>{ 'LegalEntity', 'Product2', 'Contact' },
            new List<String>{ 'BillingAccount', 'Account', 'TaxTreatment' },
            new List<String>{ 'Account.BillingAddress', 'Account.ShippingAddress', 'LegalEntity.Status',
                'Product2.Family', 'BillingAccount.BillToContactId' });
        User viewAll = RLM_BillingUITestUsers.createWithBillingAccess(
            new List<String>{ RLM_BillingUITestUsers.BILLING_PSL },
            new List<String>{ 'Product2', 'Contact' },
            new List<String>{ 'BillingAccount', 'Account', 'LegalEntity', 'TaxTreatment' },
            new List<String>{ 'Account.BillingAddress', 'Account.ShippingAddress', 'LegalEntity.Status',
                'Product2.Family', 'BillingAccount.BillToContactId' });
        CreateArgs args = new CreateArgs(ba.Id);
        RLM_BillingScheduleGroupService.mockActionOutputs = new Map<String, Object>{ 'requestId' => 'REQ-LE' };

        AuraHandledException refused;
        AuraHandledException hidden;
        Boolean visibleWithoutSharing;
        String detailsWithoutSharing;
        AuraHandledException viewAllError;
        String detailsViewAll;
        Test.startTest();
        System.runAs(noRead) {
            Assert.isTrue(userModeQueryFails('SELECT Id FROM LegalEntity LIMIT 1'),
                'PRECONDITION: the user cannot read LegalEntity.');
            try {
                args.call();
            } catch (AuraHandledException e) {
                refused = e;
            }
        }
        System.runAs(readNoSharing) {
            visibleWithoutSharing =
                ![SELECT Id FROM LegalEntity WHERE Id = :args.legalEntityId WITH USER_MODE].isEmpty();
            try {
                args.call();
            } catch (AuraHandledException e) {
                hidden = e;
            }
            detailsWithoutSharing = RLM_BillingScheduleGroupService.lastTransactionDetails;
        }
        RLM_BillingScheduleGroupService.lastTransactionDetails = null;
        System.runAs(viewAll) {
            try {
                args.call();
            } catch (AuraHandledException e) {
                viewAllError = e;
            }
            detailsViewAll = RLM_BillingScheduleGroupService.lastTransactionDetails;
        }
        Test.stopTest();

        Assert.isNotNull(refused, 'No LegalEntity read refuses create.');
        Assert.isTrue(refused.getMessage().contains('read the legal entity this screen needs'),
            'It names the legal entity read: ' + refused.getMessage());
        if (visibleWithoutSharing) {
            Assert.isNull(hidden, 'A legal entity the user can see passes the read: '
                + (hidden == null ? null : hidden.getMessage()));
            Assert.isNotNull(detailsWithoutSharing, 'The visible-entity call reached the action.');
        } else {
            Assert.isNotNull(hidden, 'A legal entity hidden by sharing refuses create.');
            Assert.areEqual(
                'The legal entity was not found, is not active, or is not visible to you. Choose another legal entity.',
                hidden.getMessage(), 'It says the legal entity is not visible.');
            Assert.isNull(detailsWithoutSharing, 'Nothing reached the action.');
        }
        Assert.isNull(viewAllError, 'With view-all the legal entity read passes: '
            + (viewAllError == null ? null : viewAllError.getMessage()));
        Map<String, Object> txn = onlyTransaction(detailsViewAll);
        Assert.areEqual(String.valueOf(args.legalEntityId), txn.get('LegalEntityId__std'),
            'The view-all call reached the action with the legal entity.');
    }

    private static final String TT_REFUSAL =
        'The tax treatment was not found, is not active, is not visible to you, or is not a tax treatment '
        + 'of the chosen legal entity. Choose another tax treatment.';
    private static final String PRODUCT_REFUSAL =
        'The product was not found, is not active, is not offered for billing schedules, or is not '
        + 'visible to you. Choose another product.';

    private static AuraHandledException refusedCreate(CreateArgs args) {
        try {
            args.call();
        } catch (AuraHandledException e) {
            return e;
        }
        return null;
    }

    // The picker offers only active treatments of the chosen legal entity; any other id, or one of
    // another entity, is refused before the action is called.
    @isTest
    static void createViaAPI_taxTreatmentNotOffered_isRefused() {
        Id baId = insertBillingAccount('BSG TT Refused');
        RLM_BillingScheduleGroupService.mockActionOutputs = new Map<String, Object>{ 'requestId' => 'REQ-TT' };
        // One treatment per legal entity (unique key), so each case has its own entity.
        LegalEntity leDraft = new LegalEntity(Name = 'BSG TT Draft LE', Status = 'Active');
        insert leDraft;
        TaxTreatment draft = new TaxTreatment(Name = 'BSG TT Draft', Status = 'Draft', LegalEntityId = leDraft.Id);
        insert draft;

        CreateArgs inactive = new CreateArgs(baId);
        inactive.legalEntityId = leDraft.Id;
        inactive.taxTreatmentId = draft.Id;
        CreateArgs missing = new CreateArgs(baId);
        missing.taxTreatmentId = fakeId(TaxTreatment.SObjectType);
        // An Active treatment, but of another legal entity than the one submitted.
        LegalEntity leOther = new LegalEntity(Name = 'BSG TT Other LE', Status = 'Active');
        insert leOther;
        TaxTreatment otherEntity = new TaxTreatment(
            Name = 'BSG TT Other Entity', Status = 'Active', LegalEntityId = leOther.Id);
        insert otherEntity;
        CreateArgs wrongEntity = new CreateArgs(baId);
        wrongEntity.taxTreatmentId = otherEntity.Id;
        Assert.areNotEqual(wrongEntity.legalEntityId, leOther.Id, 'PRECONDITION: the entities differ.');
        Map<String, CreateArgs> cases = new Map<String, CreateArgs>{
            'An inactive tax treatment' => inactive,
            'A tax treatment that does not exist' => missing,
            'An active tax treatment of another legal entity' => wrongEntity
        };

        Test.startTest();
        for (String label : cases.keySet()) {
            AuraHandledException thrown = refusedCreate(cases.get(label));
            Assert.isNotNull(thrown, label + ' is refused.');
            Assert.areEqual(TT_REFUSAL, thrown.getMessage(), label + ' gets the tax treatment refusal.');
        }
        Test.stopTest();

        Assert.isNull(RLM_BillingScheduleGroupService.lastTransactionDetails, 'Nothing reached the action.');
    }

    // The picker offers only active products of the Software family; any other id is refused.
    @isTest
    static void createViaAPI_productNotOffered_isRefused() {
        Id baId = insertBillingAccount('BSG Product Refused');
        RLM_BillingScheduleGroupService.mockActionOutputs = new Map<String, Object>{ 'requestId' => 'REQ-PR' };
        Product2 inactive = new Product2(Name = 'BSG Inactive Software', IsActive = false, Family = 'Software');
        Product2 otherFamily = new Product2(Name = 'BSG Hardware', IsActive = true, Family = 'Hardware');
        insert new List<Product2>{ inactive, otherFamily };
        Map<String, Id> cases = new Map<String, Id>{
            'An inactive product' => inactive.Id,
            'A product outside the Software family' => otherFamily.Id,
            'A product that does not exist' => fakeId(Product2.SObjectType)
        };

        Test.startTest();
        for (String label : cases.keySet()) {
            CreateArgs args = new CreateArgs(baId);
            args.productId = cases.get(label);
            AuraHandledException thrown = refusedCreate(args);
            Assert.isNotNull(thrown, label + ' is refused.');
            Assert.areEqual(PRODUCT_REFUSAL, thrown.getMessage(), label + ' gets the product refusal.');
        }
        Test.stopTest();

        Assert.isNull(RLM_BillingScheduleGroupService.lastTransactionDetails, 'Nothing reached the action.');
    }

    // The tax treatment and product reads run as the user, on records the admin owns. With no read on
    // the object the refusal names it. With read but no sharing, a record hidden by sharing is refused
    // as not visible (where the org-wide default hides it; otherwise it passes). With view-all both pass
    // and the call reaches the action.
    @isTest
    static void createViaAPI_taxTreatmentAndProductRead_refusedHiddenOrVisible() {
        Account a = new Account(Name = 'BSG Picker Read Acct');
        insert a;
        BillingAccount ba = new BillingAccount(Name = 'BSG Picker Read BA', AccountId = a.Id, BillToContactId = billToContact(a.Id));
        insert ba;
        List<String> fields = new List<String>{
            'Account.BillingAddress', 'Account.ShippingAddress', 'LegalEntity.Status',
            'Product2.Family', 'BillingAccount.BillToContactId' };
        List<String> psl = new List<String>{ RLM_BillingUITestUsers.BILLING_PSL };
        User noTaxTreatmentRead = RLM_BillingUITestUsers.createWithBillingAccess(psl, new List<String>{ 'Product2' },
            new List<String>{ 'BillingAccount', 'Account', 'LegalEntity' }, fields);
        User noProductRead = RLM_BillingUITestUsers.createWithBillingAccess(psl, new List<String>(),
            new List<String>{ 'BillingAccount', 'Account', 'LegalEntity', 'TaxTreatment' }, fields);
        User readNoSharing = RLM_BillingUITestUsers.createWithBillingAccess(psl,
            new List<String>{ 'TaxTreatment', 'Product2', 'Contact' },
            new List<String>{ 'BillingAccount', 'Account', 'LegalEntity' }, fields);
        User viewAll = RLM_BillingUITestUsers.createWithBillingAccess(psl, new List<String>{ 'Product2', 'Contact' },
            new List<String>{ 'BillingAccount', 'Account', 'LegalEntity', 'TaxTreatment' }, fields);
        CreateArgs args = new CreateArgs(ba.Id);
        RLM_BillingScheduleGroupService.mockActionOutputs = new Map<String, Object>{ 'requestId' => 'REQ-PK' };

        AuraHandledException noTtError;
        AuraHandledException noProductError;
        AuraHandledException sharedError;
        Boolean ttVisible;
        Boolean productVisible;
        String detailsShared;
        AuraHandledException viewAllError;
        String detailsViewAll;
        Test.startTest();
        System.runAs(noTaxTreatmentRead) {
            Assert.isTrue(userModeQueryFails('SELECT Id FROM TaxTreatment LIMIT 1'),
                'PRECONDITION: the user cannot read TaxTreatment.');
            noTtError = refusedCreate(args);
        }
        System.runAs(noProductRead) {
            Assert.isTrue(userModeQueryFails('SELECT Id FROM Product2 LIMIT 1'),
                'PRECONDITION: the user cannot read Product2.');
            noProductError = refusedCreate(args);
        }
        System.runAs(readNoSharing) {
            ttVisible = ![SELECT Id FROM TaxTreatment WHERE Id = :args.taxTreatmentId WITH USER_MODE].isEmpty();
            productVisible = ![SELECT Id FROM Product2 WHERE Id = :args.productId WITH USER_MODE].isEmpty();
            sharedError = refusedCreate(args);
            detailsShared = RLM_BillingScheduleGroupService.lastTransactionDetails;
        }
        RLM_BillingScheduleGroupService.lastTransactionDetails = null;
        System.runAs(viewAll) {
            viewAllError = refusedCreate(args);
            detailsViewAll = RLM_BillingScheduleGroupService.lastTransactionDetails;
        }
        Test.stopTest();

        Assert.isNotNull(noTtError, 'No TaxTreatment read refuses create.');
        Assert.isTrue(noTtError.getMessage().contains('read the tax treatment this screen needs'),
            'It names the tax treatment read: ' + noTtError.getMessage());
        Assert.isNotNull(noProductError, 'No Product2 read refuses create.');
        Assert.isTrue(noProductError.getMessage().contains('read the product this screen needs'),
            'It names the product read: ' + noProductError.getMessage());
        if (ttVisible && productVisible) {
            Assert.isNull(sharedError, 'Records the user can see pass: '
                + (sharedError == null ? null : sharedError.getMessage()));
            Assert.isNotNull(detailsShared, 'The visible-records call reached the action.');
        } else {
            Assert.isNotNull(sharedError, 'A record hidden by sharing refuses create.');
            Assert.areEqual(ttVisible ? PRODUCT_REFUSAL : TT_REFUSAL, sharedError.getMessage(),
                'It says the hidden record is not visible.');
            Assert.isNull(detailsShared, 'Nothing reached the action.');
        }
        Assert.isNull(viewAllError, 'With view-all both reads pass: '
            + (viewAllError == null ? null : viewAllError.getMessage()));
        Map<String, Object> txn = onlyTransaction(detailsViewAll);
        Assert.areEqual(String.valueOf(args.taxTreatmentId), txn.get('TaxTreatmentId__std'),
            'The view-all call reached the action with the tax treatment.');
        Assert.areEqual(String.valueOf(args.productId), txn.get('ProductId__std'),
            'The view-all call reached the action with the product.');
    }

    // The real query's cap and truncation message, through a small injected cap. Three Advance-only
    // treatments of one entity, cap 2: the read returns a third row, so it was cut off; asking for Arrears
    // finds nothing and says so (not "no treatment"); asking for Advance, or for a one-time charge (an
    // Advance-only choice is accepted from a cut-off read), still finds one of them. At cap 3 the same read
    // is complete and the plain message returns. Which two are read is the query's order, so the
    // assertions do not depend on it. The query's currency filter is exercised by
    // findBillingTreatmentId_otherCurrencyRows_doNotUseUpTheCap, and only when the org has a second active
    // currency.
    @isTest
    static void findBillingTreatmentId_pastTheCap_saysTheLookupWasCutOff() {
        LegalEntity le = new LegalEntity(Name = 'BSG Cap LE', Status = 'Active');
        insert le;
        String cur = UserInfo.getDefaultCurrency();
        List<BillingTreatment> ts = new List<BillingTreatment>();
        for (Integer i = 1; i <= 3; i++) {
            ts.add(new BillingTreatment(
                Name = 'BSG Cap T' + i, LegalEntityId = le.Id, Status = 'Draft', ExcludeFromBilling = 'No',
                CurrencyIsoCode = cur));
        }
        insert ts;
        List<BillingTreatmentItem> its = new List<BillingTreatmentItem>();
        for (BillingTreatment t : ts) {
            its.add(new BillingTreatmentItem(
                Name = 'BSG Cap Item ' + t.Name, BillingTreatmentId = t.Id, BillingType = 'Advance',
                Controller = 'BillingScheduleGroup', Status = 'Draft', Type = 'Remainder', ProcessingOrder = 1,
                Sequencing = 'Manual', Handling0Amount = 'CreateInvoice'));
        }
        insert its;
        // Re-read for the update: the inserted records carry fields the update refuses to write back.
        List<BillingTreatmentItem> toActivate = [
            SELECT Id FROM BillingTreatmentItem WHERE BillingTreatmentId IN :new Map<Id, BillingTreatment>(ts).keySet()];
        for (BillingTreatmentItem item : toActivate) {
            item.Status = 'Active';
        }
        update toActivate;
        for (BillingTreatment t : ts) {
            t.Status = 'Active';
        }
        update ts;
        Set<Id> treatmentIds = new Map<Id, BillingTreatment>(ts).keySet();

        RLM_BillingScheduleGroupService.ITEM_READ_CAP = 2;
        Test.startTest();
        AuraHandledException cutOff;
        try {
            RLM_BillingScheduleGroupService.findBillingTreatmentId(le.Id, le.Name, false, 'Arrears', cur);
        } catch (AuraHandledException e) {
            cutOff = e;
        }
        Id foundAdvance = RLM_BillingScheduleGroupService.findBillingTreatmentId(le.Id, le.Name, false, 'Advance', cur);
        Id foundOneTime = RLM_BillingScheduleGroupService.findBillingTreatmentId(le.Id, le.Name, true, null, cur);
        RLM_BillingScheduleGroupService.ITEM_READ_CAP = 1000;
        AuraHandledException none;
        try {
            RLM_BillingScheduleGroupService.findBillingTreatmentId(le.Id, le.Name, false, 'Arrears', cur);
        } catch (AuraHandledException e) {
            none = e;
        }
        Test.stopTest();

        Assert.isNotNull(cutOff);
        Assert.isTrue(cutOff.getMessage().contains('cut off at 2 items, so a matching treatment may not have been seen'), cutOff.getMessage());
        Assert.isTrue(treatmentIds.contains(foundAdvance), 'A treatment read before the cap is still found.');
        Assert.isTrue(treatmentIds.contains(foundOneTime), 'A one-time charge takes an Advance-only choice from a cut-off read.');
        Assert.isNotNull(none);
        Assert.isTrue(none.getMessage().startsWith('No active billing treatment bills in arrears'),
            'Under the cap the message is the plain one: ' + none.getMessage());

        // Exactly as many items as the cap is a complete read, not a cut-off one.
        RLM_BillingScheduleGroupService.ITEM_READ_CAP = 3;
        AuraHandledException atCap;
        try {
            RLM_BillingScheduleGroupService.findBillingTreatmentId(le.Id, le.Name, false, 'Arrears', cur);
        } catch (AuraHandledException e) {
            atCap = e;
        }
        RLM_BillingScheduleGroupService.ITEM_READ_CAP = 1000;
        Assert.isNotNull(atCap);
        Assert.isTrue(atCap.getMessage().startsWith('No active billing treatment bills in arrears'),
            'A read of exactly the cap is complete: ' + atCap.getMessage());
    }

    // The query filters on the charge currency, so another currency's items do not count against the cap.
    // Cap 1 over an other-currency Arrears treatment (created first, so read first if unfiltered) and one
    // Arrears treatment in the charge currency: filtered, the read is the one row and complete; unfiltered,
    // it would be cut off before the fit. Needs a second active currency, which the module's orgs have
    // (it needs a multi-currency org; the 264 scratch runs had seven active currencies).
    @isTest
    static void findBillingTreatmentId_otherCurrencyRows_doNotUseUpTheCap() {
        String cur = UserInfo.getDefaultCurrency();
        List<CurrencyType> others = [SELECT IsoCode FROM CurrencyType WHERE IsActive = true AND IsoCode != :cur LIMIT 1];
        Assert.isFalse(others.isEmpty(),
            'PRECONDITION: a second active currency, or the currency filter cannot be told apart.');
        LegalEntity le = new LegalEntity(Name = 'BSG Cap Currency LE', Status = 'Active');
        insert le;
        BillingTreatment otherCurrency = new BillingTreatment(
            Name = 'BSG CapCur Other', LegalEntityId = le.Id, Status = 'Draft', ExcludeFromBilling = 'No',
            CurrencyIsoCode = others[0].IsoCode);
        insert otherCurrency;
        BillingTreatment fit = new BillingTreatment(
            Name = 'BSG CapCur Fit', LegalEntityId = le.Id, Status = 'Draft', ExcludeFromBilling = 'No',
            CurrencyIsoCode = cur);
        insert fit;
        List<BillingTreatment> ts = new List<BillingTreatment>{ otherCurrency, fit };
        List<BillingTreatmentItem> its = new List<BillingTreatmentItem>();
        for (BillingTreatment t : ts) {
            its.add(new BillingTreatmentItem(
                Name = 'BSG CapCur Item ' + t.Name, BillingTreatmentId = t.Id, BillingType = 'Arrears',
                Controller = 'BillingScheduleGroup', Status = 'Draft', Type = 'Remainder', ProcessingOrder = 1,
                Sequencing = 'Manual', Handling0Amount = 'CreateInvoice'));
        }
        insert its;
        List<BillingTreatmentItem> toActivate = [
            SELECT Id FROM BillingTreatmentItem WHERE BillingTreatmentId IN :new Map<Id, BillingTreatment>(ts).keySet()];
        for (BillingTreatmentItem item : toActivate) {
            item.Status = 'Active';
        }
        update toActivate;
        for (BillingTreatment t : ts) {
            t.Status = 'Active';
        }
        update ts;

        RLM_BillingScheduleGroupService.ITEM_READ_CAP = 1;
        Test.startTest();
        Id found = RLM_BillingScheduleGroupService.findBillingTreatmentId(le.Id, le.Name, false, 'Arrears', cur);
        Test.stopTest();

        Assert.areEqual(fit.Id, found, 'The other currency\'s row is filtered out by the query, so the read is complete.');
    }

    // The extra row past the cap belongs to a different treatment, so the last treatment kept is complete
    // and still matches. Cap 2 over T1 Arrears-only, T2 and T3 Advance-only: Advance finds T2 (the oldest
    // fit), where "drop the last treatment whenever the read was cut off" would have refused it.
    @isTest
    static void findBillingTreatmentId_extraRowOfAnotherTreatment_keepsTheLastTreatmentRead() {
        LegalEntity le = new LegalEntity(Name = 'BSG Cap Keep LE', Status = 'Active');
        insert le;
        String cur = UserInfo.getDefaultCurrency();
        BillingTreatment t1 = insertActiveTreatment(le, 'BSG Cap Keep T1', 'Arrears', cur);
        BillingTreatment t2 = insertActiveTreatment(le, 'BSG Cap Keep T2', 'Advance', cur);
        insertActiveTreatment(le, 'BSG Cap Keep T3', 'Advance', cur);

        RLM_BillingScheduleGroupService.ITEM_READ_CAP = 2;
        Test.startTest();
        Id found = RLM_BillingScheduleGroupService.findBillingTreatmentId(le.Id, le.Name, false, 'Advance', cur);
        RLM_BillingScheduleGroupService.ITEM_READ_CAP = 1000;
        Test.stopTest();

        Assert.areEqual(t2.Id, found, 'The last treatment read is complete and is the oldest Advance fit.');
        Assert.areNotEqual(t1.Id, found);
    }

    // A one-time charge prefers an Advance-only treatment, which may lie past the cap: a cut-off read
    // that holds only an Arrears-only treatment is refused rather than taken.
    @isTest
    static void findBillingTreatmentId_oneTimeCutOffWithOnlyArrears_isRefused() {
        LegalEntity le = new LegalEntity(Name = 'BSG Cap OneTime LE', Status = 'Active');
        insert le;
        String cur = UserInfo.getDefaultCurrency();
        insertActiveTreatment(le, 'BSG Cap OneTime T1', 'Arrears', cur);
        insertActiveTreatment(le, 'BSG Cap OneTime T2', 'Advance', cur);

        RLM_BillingScheduleGroupService.ITEM_READ_CAP = 1;
        Test.startTest();
        AuraHandledException cutOff;
        try {
            RLM_BillingScheduleGroupService.findBillingTreatmentId(le.Id, le.Name, true, null, cur);
        } catch (AuraHandledException e) {
            cutOff = e;
        }
        RLM_BillingScheduleGroupService.ITEM_READ_CAP = 1000;
        Test.stopTest();

        Assert.isNotNull(cutOff, 'An Arrears-only choice from a cut-off read is not taken for a one-time charge.');
        Assert.isTrue(cutOff.getMessage().contains('cut off at 1 item,'), cutOff.getMessage());
        Assert.isTrue(cutOff.getMessage().contains('Advance-only treatment, which a one-time charge prefers'),
            'The refusal says why the seen treatment was not taken: ' + cutOff.getMessage());
    }

    // The same rule for a mixed choice: cap 2 over T1 mixed and T2 Advance-only. The extra row is T2's, so
    // T1 is kept and is the one-time choice, but it is not Advance-only and the read was cut off.
    @isTest
    static void findBillingTreatmentId_oneTimeCutOffWithOnlyMixed_isRefused() {
        LegalEntity le = new LegalEntity(Name = 'BSG Cap OneTime Mixed LE', Status = 'Active');
        insert le;
        String cur = UserInfo.getDefaultCurrency();
        insertActiveMixedTreatment(le, 'BSG Cap OneTime Mixed T1', cur);
        insertActiveTreatment(le, 'BSG Cap OneTime Mixed T2', 'Advance', cur);

        RLM_BillingScheduleGroupService.ITEM_READ_CAP = 2;
        Test.startTest();
        AuraHandledException cutOff;
        try {
            RLM_BillingScheduleGroupService.findBillingTreatmentId(le.Id, le.Name, true, null, cur);
        } catch (AuraHandledException e) {
            cutOff = e;
        }
        RLM_BillingScheduleGroupService.ITEM_READ_CAP = 1000;
        Test.stopTest();

        Assert.isNotNull(cutOff, 'A mixed choice from a cut-off read is not taken for a one-time charge.');
        Assert.isTrue(cutOff.getMessage().contains('cut off at 2 items,'), cutOff.getMessage());
        Assert.isTrue(cutOff.getMessage().contains('Advance-only treatment, which a one-time charge prefers'),
            'T1 was kept and chosen, then refused as not Advance-only: ' + cutOff.getMessage());
    }

    // The cut-off message also says a mixed treatment was skipped when one was read whole. Cap 2 over T1
    // mixed (an Advance and an Arrears item) and T2 Advance-only: the extra row is T2's, so T1 is kept,
    // and asking for Arrears skips it as ambiguous and finds nothing else.
    @isTest
    static void findBillingTreatmentId_cutOffWithAMixedTreatmentRead_saysItWasSkipped() {
        LegalEntity le = new LegalEntity(Name = 'BSG Cap Skip LE', Status = 'Active');
        insert le;
        String cur = UserInfo.getDefaultCurrency();
        insertActiveMixedTreatment(le, 'BSG Cap Skip T1', cur);
        insertActiveTreatment(le, 'BSG Cap Skip T2', 'Advance', cur);

        RLM_BillingScheduleGroupService.ITEM_READ_CAP = 2;
        Test.startTest();
        AuraHandledException cutOff;
        try {
            RLM_BillingScheduleGroupService.findBillingTreatmentId(le.Id, le.Name, false, 'Arrears', cur);
        } catch (AuraHandledException e) {
            cutOff = e;
        }
        RLM_BillingScheduleGroupService.ITEM_READ_CAP = 1000;
        Test.stopTest();

        Assert.isNotNull(cutOff);
        Assert.isTrue(cutOff.getMessage().contains('cut off at 2 items,'), cutOff.getMessage());
        Assert.isTrue(cutOff.getMessage().contains('was also skipped'), cutOff.getMessage());
    }

    // One active treatment of the entity with a single active item of the timing.
    private static BillingTreatment insertActiveTreatment(LegalEntity le, String name, String billingType, String cur) {
        BillingTreatment t = new BillingTreatment(
            Name = name, LegalEntityId = le.Id, Status = 'Draft', ExcludeFromBilling = 'No', CurrencyIsoCode = cur);
        insert t;
        insert new BillingTreatmentItem(
            Name = name + ' Item', BillingTreatmentId = t.Id, BillingType = billingType,
            Controller = 'BillingScheduleGroup', Status = 'Draft', Type = 'Remainder', ProcessingOrder = 1,
            Sequencing = 'Manual', Handling0Amount = 'CreateInvoice');
        List<BillingTreatmentItem> items = [SELECT Id FROM BillingTreatmentItem WHERE BillingTreatmentId = :t.Id];
        for (BillingTreatmentItem item : items) {
            item.Status = 'Active';
        }
        update items;
        t.Status = 'Active';
        update t;
        return t;
    }

    // One active treatment of the entity with an Advance (Percentage) and an Arrears (Remainder) item.
    private static BillingTreatment insertActiveMixedTreatment(LegalEntity le, String name, String cur) {
        BillingTreatment t = new BillingTreatment(
            Name = name, LegalEntityId = le.Id, Status = 'Draft', ExcludeFromBilling = 'No', CurrencyIsoCode = cur);
        insert t;
        insert new List<BillingTreatmentItem>{
            new BillingTreatmentItem(
                Name = name + ' Adv', BillingTreatmentId = t.Id, BillingType = 'Advance',
                Controller = 'BillingScheduleGroup', Status = 'Draft', Type = 'Percentage', Percentage = 50,
                ProcessingOrder = 1, Sequencing = 'Manual', Handling0Amount = 'CreateInvoice'),
            new BillingTreatmentItem(
                Name = name + ' Arr', BillingTreatmentId = t.Id, BillingType = 'Arrears',
                Controller = 'BillingScheduleGroup', Status = 'Draft', Type = 'Remainder', ProcessingOrder = 2,
                Sequencing = 'Manual', Handling0Amount = 'CreateInvoice')
        };
        List<BillingTreatmentItem> items = [SELECT Id FROM BillingTreatmentItem WHERE BillingTreatmentId = :t.Id];
        for (BillingTreatmentItem item : items) {
            item.Status = 'Active';
        }
        update items;
        t.Status = 'Active';
        update t;
        return t;
    }

    // A mixed treatment cut by the cap must not look single-timing: one treatment with an Advance and an
    // Arrears item, cap 1. The read sees one row and one more, so the treatment is dropped and both timings
    // get the cut-off message (kept, it would match whichever timing its one seen row had).
    @isTest
    static void findBillingTreatmentId_mixedTreatmentCutByTheCap_isNeverMatched() {
        LegalEntity le = new LegalEntity(Name = 'BSG Cap Mixed LE', Status = 'Active');
        insert le;
        String cur = UserInfo.getDefaultCurrency();
        insertActiveMixedTreatment(le, 'BSG Cap Mixed', cur);

        RLM_BillingScheduleGroupService.ITEM_READ_CAP = 1;
        Test.startTest();
        List<String> messages = new List<String>();
        for (String timing : new List<String>{ 'Advance', 'Arrears' }) {
            try {
                RLM_BillingScheduleGroupService.findBillingTreatmentId(le.Id, le.Name, false, timing, cur);
                messages.add('matched');
            } catch (AuraHandledException e) {
                messages.add(e.getMessage());
            }
        }
        RLM_BillingScheduleGroupService.ITEM_READ_CAP = 1000;
        Test.stopTest();

        for (String message : messages) {
            Assert.isTrue(message.contains('cut off at 1 item,'), 'A cut mixed treatment is never matched: ' + message);
        }
    }

    // Dropping a treatment removes every row of it and leaves the others.
    @isTest
    static void dropTreatment_removesEveryRowOfThatTreatmentOnly() {
        Id t1 = (Id) (BillingTreatment.SObjectType.getDescribe().getKeyPrefix() + '000000000001');
        Id t2 = (Id) (BillingTreatment.SObjectType.getDescribe().getKeyPrefix() + '000000000002');
        List<RLM_BillingScheduleGroupService.TreatmentCandidate> rows = new List<RLM_BillingScheduleGroupService.TreatmentCandidate>{
            new RLM_BillingScheduleGroupService.TreatmentCandidate(t1, 'Advance', CUR),
            new RLM_BillingScheduleGroupService.TreatmentCandidate(t2, 'Advance', CUR),
            new RLM_BillingScheduleGroupService.TreatmentCandidate(t2, 'Arrears', CUR)
        };

        List<RLM_BillingScheduleGroupService.TreatmentCandidate> kept = RLM_BillingScheduleGroupService.dropTreatment(rows, t2);

        Assert.areEqual(1, kept.size());
        Assert.areEqual(t1, kept[0].treatmentId);
        Assert.areEqual(3, rows.size(), 'The input list is not changed.');
    }

    @isTest
    static void itemReadCap_isTheDocumented1000() {
        Assert.areEqual(1000, RLM_BillingScheduleGroupService.ITEM_READ_CAP, 'The cap is the documented 1000.');
    }

    // With no own account, the page account wins over the oldest link.
    @isTest
    static void createViaAPI_pageAccount_winsOverTheOldestLink() {
        Account oldest = new Account(Name = 'BSG Oldest Link');
        Account page = new Account(Name = 'BSG Page Link');
        insert new List<Account>{ oldest, page };
        BillingAccount ba = new BillingAccount(Name = 'BSG Two Links BA', BillToContactId = billToContact(page.Id));
        insert ba;
        insert new AccountBillingAccount(AccountId = oldest.Id, BillingAccountId = ba.Id);
        insert new AccountBillingAccount(AccountId = page.Id, BillingAccountId = ba.Id);
        RLM_BillingScheduleGroupService.mockActionOutputs = new Map<String, Object>{ 'requestId' => 'REQ-PL' };

        Test.startTest();
        CreateArgs withPage = new CreateArgs(ba.Id);
        withPage.pageAccountId = page.Id;
        withPage.call();
        Map<String, Object> pageTxn = onlyTransaction(RLM_BillingScheduleGroupService.lastTransactionDetails);
        new CreateArgs(ba.Id).call();
        Map<String, Object> defaultTxn = onlyTransaction(RLM_BillingScheduleGroupService.lastTransactionDetails);
        Test.stopTest();

        Assert.areEqual(String.valueOf(page.Id), pageTxn.get('AccountId__std'), 'The page account is sent.');
        Assert.areEqual(String.valueOf(oldest.Id), defaultTxn.get('AccountId__std'),
            'With no page account the oldest link is used, as before.');
    }

    @isTest
    static void chooseTreatment_firstInTimingAndCurrency_skipsAmbiguousAndDedupes() {
        Id ambiguous = fakeId(BillingTreatment.SObjectType);
        Id advanceOnly = Id.valueOf(BillingTreatment.SObjectType.getDescribe().getKeyPrefix() + '000000000001');
        Id arrears = Id.valueOf(BillingTreatment.SObjectType.getDescribe().getKeyPrefix() + '000000000002');
        Id eur = Id.valueOf(BillingTreatment.SObjectType.getDescribe().getKeyPrefix() + '000000000003');
        List<RLM_BillingScheduleGroupService.TreatmentCandidate> rows = new List<RLM_BillingScheduleGroupService.TreatmentCandidate>{
            new RLM_BillingScheduleGroupService.TreatmentCandidate(ambiguous, 'Arrears', 'USD'),
            new RLM_BillingScheduleGroupService.TreatmentCandidate(ambiguous, 'Advance', 'USD'),
            new RLM_BillingScheduleGroupService.TreatmentCandidate(eur, 'Arrears', 'EUR'),
            new RLM_BillingScheduleGroupService.TreatmentCandidate(arrears, 'Arrears', 'USD'),
            new RLM_BillingScheduleGroupService.TreatmentCandidate(arrears, 'Arrears', 'USD'),
            new RLM_BillingScheduleGroupService.TreatmentCandidate(advanceOnly, 'Advance', 'USD')
        };
        Assert.areEqual(arrears, RLM_BillingScheduleGroupService.chooseTreatment(rows, false, 'Arrears', 'USD').chosen,
            'A treatment with both timings is skipped; a repeated item does not make one ambiguous.');
        Assert.areEqual(advanceOnly, RLM_BillingScheduleGroupService.chooseTreatment(rows, false, 'Advance', 'USD').chosen);
        Assert.areEqual(eur, RLM_BillingScheduleGroupService.chooseTreatment(rows, false, 'Arrears', 'EUR').chosen,
            'The charge currency picks the treatment.');
        Assert.isNull(RLM_BillingScheduleGroupService.chooseTreatment(rows, false, 'Arrears', 'GBP').chosen,
            'No treatment in the charge currency, no match.');
        Assert.isNull(RLM_BillingScheduleGroupService.chooseTreatment(
            new List<RLM_BillingScheduleGroupService.TreatmentCandidate>(), false, 'Arrears', 'USD').chosen, 'No candidates, no treatment.');
    }

    // Reads real records: the treatment is found through its legal entity and the timing of its
    // active item. Setup is the least that the platform accepts; if it is refused the failure names
    // the record, so this is a precondition and not a skip.
    @isTest
    static void findBillingTreatmentId_findsTheTreatmentOfTheEntityForTheTimingAndCurrency() {
        LegalEntity le = new LegalEntity(Name = 'BSG TQ LE', Status = 'Active');
        LegalEntity other = new LegalEntity(Name = 'BSG TQ Other LE', Status = 'Active');
        insert new List<LegalEntity>{ le, other };
        String cur = UserInfo.getDefaultCurrency();
        // Another active currency, when the org has one: a treatment in it is created first, so it would be
        // chosen if the currency were ignored. Without one, the currency filter is not exercised here: the
        // query's filter is covered by findBillingTreatmentId_otherCurrencyRows_doNotUseUpTheCap and
        // chooseTreatment's by the chooseTreatment tests (with candidates).
        List<CurrencyType> others = [SELECT IsoCode FROM CurrencyType WHERE IsActive = true AND IsoCode != :cur LIMIT 1];
        BillingTreatment otherCurrency = null;
        if (!others.isEmpty()) {
            otherCurrency = new BillingTreatment(
                Name = 'BSG TQ Other Currency', LegalEntityId = le.Id, Status = 'Draft', ExcludeFromBilling = 'No',
                CurrencyIsoCode = others[0].IsoCode);
            insert otherCurrency;
            insert new BillingTreatmentItem(
                Name = 'BSG TQ Other Currency Item', BillingTreatmentId = otherCurrency.Id, BillingType = 'Arrears',
                Controller = 'BillingScheduleGroup', Status = 'Draft', Type = 'Remainder', ProcessingOrder = 1,
                Sequencing = 'Manual', Handling0Amount = 'CreateInvoice');
        }
        BillingTreatment advance = new BillingTreatment(
            Name = 'BSG TQ Advance', LegalEntityId = le.Id, Status = 'Draft', ExcludeFromBilling = 'No',
            CurrencyIsoCode = cur);
        BillingTreatment arrears = new BillingTreatment(
            Name = 'BSG TQ Arrears', LegalEntityId = le.Id, Status = 'Draft', ExcludeFromBilling = 'No',
            CurrencyIsoCode = cur);
        BillingTreatment otherArrears = new BillingTreatment(
            Name = 'BSG TQ Other Arrears', LegalEntityId = other.Id, Status = 'Draft', ExcludeFromBilling = 'No',
            CurrencyIsoCode = cur);
        insert new List<BillingTreatment>{ advance, arrears, otherArrears };
        insert new List<BillingTreatmentItem>{
            new BillingTreatmentItem(
                Name = 'BSG TQ Advance Item', BillingTreatmentId = advance.Id, BillingType = 'Advance',
                Controller = 'BillingScheduleGroup', Status = 'Draft', Type = 'Remainder', ProcessingOrder = 1,
                Sequencing = 'Manual', Handling0Amount = 'CreateInvoice'),
            new BillingTreatmentItem(
                Name = 'BSG TQ Arrears Item', BillingTreatmentId = arrears.Id, BillingType = 'Arrears',
                Controller = 'BillingScheduleGroup', Status = 'Draft', Type = 'Remainder', ProcessingOrder = 1,
                Sequencing = 'Manual', Handling0Amount = 'CreateInvoice'),
            new BillingTreatmentItem(
                Name = 'BSG TQ Other Item', BillingTreatmentId = otherArrears.Id, BillingType = 'Arrears',
                Controller = 'BillingScheduleGroup', Status = 'Draft', Type = 'Remainder', ProcessingOrder = 1,
                Sequencing = 'Manual', Handling0Amount = 'CreateInvoice')
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
        Id foundArrears = RLM_BillingScheduleGroupService.findBillingTreatmentId(le.Id, le.Name, false, 'Arrears', cur);
        Id foundAdvance = RLM_BillingScheduleGroupService.findBillingTreatmentId(le.Id, le.Name, false, 'Advance', cur);
        Id foundOneTime = RLM_BillingScheduleGroupService.findBillingTreatmentId(le.Id, le.Name, true, null, cur);
        Test.stopTest();

        Assert.areEqual(arrears.Id, foundArrears, 'The chosen entity\'s Arrears treatment is found, not another entity\'s.');
        Assert.areEqual(advance.Id, foundAdvance, 'The Advance treatment of the same entity is found for Advance.');
        Assert.areEqual(advance.Id, foundOneTime, 'A one-time charge takes the Advance treatment in the currency.');
    }

    // A treatment with items in both timings that is the only fit: the refusal names it (quoted), and a
    // one-time charge falls back to it. A fresh legal entity keeps it apart from the other test's records.
    // The two-item setup (Percentage then Remainder) activates on 264 (measured by this test, 2026-11-26).
    @isTest
    static void findBillingTreatmentId_onlyAMixedTreatment_isRefusedByNameAndUsedForOneTime() {
        LegalEntity le = new LegalEntity(Name = 'BSG TQM LE', Status = 'Active');
        insert le;
        BillingTreatment mixed = new BillingTreatment(
            Name = 'BSG TQM Mixed', LegalEntityId = le.Id, Status = 'Draft', ExcludeFromBilling = 'No',
            CurrencyIsoCode = CUR);
        insert mixed;
        insert new List<BillingTreatmentItem>{
            new BillingTreatmentItem(
                Name = 'BSG TQM Advance Item', BillingTreatmentId = mixed.Id, BillingType = 'Advance',
                Controller = 'BillingScheduleGroup', Status = 'Draft', Type = 'Percentage', Percentage = 50,
                ProcessingOrder = 1, Sequencing = 'Manual', Handling0Amount = 'CreateInvoice'),
            new BillingTreatmentItem(
                Name = 'BSG TQM Arrears Item', BillingTreatmentId = mixed.Id, BillingType = 'Arrears',
                Controller = 'BillingScheduleGroup', Status = 'Draft', Type = 'Remainder', ProcessingOrder = 2,
                Sequencing = 'Manual', Handling0Amount = 'CreateInvoice')
        };
        List<BillingTreatmentItem> items = [SELECT Id FROM BillingTreatmentItem WHERE Name LIKE 'BSG TQM%'];
        for (BillingTreatmentItem item : items) {
            item.Status = 'Active';
        }
        update items;
        mixed.Status = 'Active';
        update mixed;

        AuraHandledException thrown;
        Test.startTest();
        try {
            RLM_BillingScheduleGroupService.findBillingTreatmentId(le.Id, le.Name, false, 'Arrears', CUR);
        } catch (AuraHandledException e) {
            thrown = e;
        }
        Id oneTime = RLM_BillingScheduleGroupService.findBillingTreatmentId(le.Id, le.Name, true, null, CUR);
        Test.stopTest();

        Assert.isNotNull(thrown, 'A treatment with both timings is refused for a recurring charge.');
        Assert.areEqual(
            'The billing treatment \'BSG TQM Mixed\' has items in both advance and arrears, so it cannot be matched to arrears in '
            + CUR + '. Split it into one treatment per timing, or choose another legal entity or currency.',
            thrown.getMessage(), 'The readable name is quoted.');
        Assert.areEqual(mixed.Id, oneTime, 'A one-time charge falls back to a mixed treatment when it is the only fit.');
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
        public Id legalEntityId = activeLegalEntityId();
        public Id taxTreatmentId = activeTaxTreatmentId();
        public String currencyIsoCode = UserInfo.getDefaultCurrency();
        public Decimal unitPrice = 10;
        public Decimal totalPrice = 240;
        public String billingCity = 'San Francisco';
        public Id productId = softwareProductId();
        public String productName = 'Widget';
        public Date startDate = Date.newInstance(2026, 1, 1);
        public Integer billingDayOfMonth = 1;
        public Integer billingStartMonth = 1;
        public String termSetting = 'Termed';
        public Date endDate = Date.newInstance(2026, 12, 31);
        public Id pageAccountId = null;

        public CreateArgs(Id billingAccountId) {
            this.billingAccountId = billingAccountId;
        }

        public RLM_BillingScheduleGroupService.CreateResult call() {
            seedTreatment();
            return RLM_BillingScheduleGroupService.createBillingScheduleGroupAndScheduleViaAPI(
                billingAccountId, billingTermUnit, billingTerm, billingType, quantity, legalEntityId,
                taxTreatmentId, currencyIsoCode, unitPrice, totalPrice, billingCity, productId,
                productName, startDate, billingDayOfMonth, billingStartMonth, termSetting, endDate, pageAccountId
            );
        }
    }

    // The create path reads the legal entity (active and visible to the user) before the treatment
    // lookup, so a create call needs a real one: one per test, made on first use.
    private static final String TEST_LEGAL_ENTITY = 'BSG Test LE';
    private static Id testLegalEntityId;
    private static Id activeLegalEntityId() {
        if (testLegalEntityId == null) {
            LegalEntity le = new LegalEntity(Name = TEST_LEGAL_ENTITY, Status = 'Active');
            insert le;
            testLegalEntityId = le.Id;
        }
        return testLegalEntityId;
    }

    // The tax treatment and product the pickers offer (getTaxTreatments: active; getProducts: active,
    // Software family), the treatment on the test legal entity: one per test, made on first use.
    private static Id testTaxTreatmentId;
    private static Id activeTaxTreatmentId() {
        if (testTaxTreatmentId == null) {
            TaxTreatment tt = new TaxTreatment(
                Name = 'BSG Test TT', Status = 'Active', LegalEntityId = activeLegalEntityId());
            insert tt;
            testTaxTreatmentId = tt.Id;
        }
        return testTaxTreatmentId;
    }

    private static Id testProductId;
    private static Id softwareProductId() {
        if (testProductId == null) {
            Product2 p = new Product2(Name = 'BSG Test Software', IsActive = true, Family = 'Software');
            insert p;
            testProductId = p.Id;
        }
        return testProductId;
    }

    // A treatment the lookup finds, unless a test has set its own candidates.
    private static void seedTreatment() {
        if (RLM_BillingScheduleGroupService.mockTreatmentCandidates == null) {
            RLM_BillingScheduleGroupService.mockTreatmentCandidates = candidates(
                new RLM_BillingScheduleGroupService.TreatmentCandidate(
                    fakeId(BillingTreatment.SObjectType), 'Advance', CUR));
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
        BillingAccount ba = new BillingAccount(Name = name + ' BA', AccountId = a.Id, BillToContactId = billToContact(a.Id));
        insert ba;
        return ba.Id;
    }

    // A contact to set as a billing account's bill-to contact: the create action refuses a billing
    // account without one (REQUIRED_FIELD_MISSING billToContact), and so does the service before it.
    private static Id billToContact(Id accountId) {
        Contact c = new Contact(LastName = 'BSG Bill To', AccountId = accountId);
        insert c;
        return c.Id;
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
                fakeId(TaxTreatment.SObjectType), CUR, 10, 10, 'San Francisco',
                fakeId(Product2.SObjectType), 'Widget', Date.today(), 1, 1, 'Evergreen', null, null
            );
            return false;
        } catch (AuraHandledException e) {
            return true;
        }
    }
}
