@isTest
private class RLM_SplitInvoicesControllerTest {

    @isTest
    static void getCurrentInvoiceBillingInfo_blankAndUnknown_returnsEmptyInfo() {
        Id fakeInvoice = fakeId('Invoice', 0);
        Test.startTest();
        RLM_SplitInvoicesController.CurrentInvoiceBillingInfo blank =
            RLM_SplitInvoicesController.getCurrentInvoiceBillingInfo('');
        RLM_SplitInvoicesController.CurrentInvoiceBillingInfo unknown =
            RLM_SplitInvoicesController.getCurrentInvoiceBillingInfo(fakeInvoice);
        Test.stopTest();
        System.assertNotEquals(null, blank, 'A non-null info wrapper should be returned for blank input.');
        System.assertNotEquals(null, unknown, 'A non-null info wrapper should be returned for an unknown invoice.');
        System.assertEquals(null, unknown.billingArrangementName,
            'No arrangement name resolves for a non-existent invoice.');
    }

    @isTest
    static void getInvoicesByCorrelation_blankAndUnknown_returnsEmptyList() {
        Test.startTest();
        List<RLM_SplitInvoicesController.InvoiceRow> blank =
            RLM_SplitInvoicesController.getInvoicesByCorrelation('');
        System.assertEquals(0, blank.size(), 'Blank correlation id yields an empty list.');

        // The correlation query must run: it once selected BillingArrangement, which is not an
        // Invoice field, and failed with "No such column" on every call.
        List<RLM_SplitInvoicesController.InvoiceRow> unknown =
            RLM_SplitInvoicesController.getInvoicesByCorrelation('RLM-NO-SUCH-CORRELATION');
        System.assertEquals(0, unknown.size(), 'Unknown correlation id yields an empty list.');
        Test.stopTest();
    }

    @isTest
    static void getRelatedNames_resolvesAccountAndToleratesNulls() {
        Account acc = new Account(Name = 'RLM Split Invoices Test');
        insert acc;

        Test.startTest();
        RLM_SplitInvoicesController.RelatedNamesResult result =
            RLM_SplitInvoicesController.getRelatedNames(
                new List<String>{ acc.Id }, null, null, null);
        Test.stopTest();

        System.assertNotEquals(null, result, 'A non-null result should be returned.');
        System.assertEquals('RLM Split Invoices Test', result.accountNames.get(acc.Id),
            'Account name should resolve by id.');
        System.assertEquals(0, result.arrangementNames.size(), 'Null arrangement ids resolve to an empty map.');
    }

    // Contacts resolve by name, and an object with no Name field (Case) yields an empty map
    // instead of failing the other lists.
    @isTest
    static void getRelatedNames_resolvesContactsAndToleratesNamelessObjects() {
        Account acc = new Account(Name = 'RLM Split Invoices Contact Test');
        insert acc;
        Contact con = new Contact(FirstName = 'Ana', LastName = 'Rivera', AccountId = acc.Id);
        insert con;
        Case c = new Case(AccountId = acc.Id, Subject = 'RLM split invoices case');
        insert c;
        // Name order depends on the locale, so compare against the stored full name.
        String contactName = [SELECT Name FROM Contact WHERE Id = :con.Id].Name;

        Test.startTest();
        RLM_SplitInvoicesController.RelatedNamesResult result =
            RLM_SplitInvoicesController.getRelatedNames(
                new List<String>{ acc.Id }, null, new List<String>{ c.Id }, new List<String>{ con.Id });
        Test.stopTest();

        Assert.areEqual('RLM Split Invoices Contact Test', result.accountNames.get(acc.Id),
            'The account resolves by name.');
        Assert.areEqual(contactName, result.contactNames.get(con.Id),
            'The contact list, resolved after the failing Case list, still resolves to its full name.');
        Assert.isTrue(result.profileNames.isEmpty(),
            'An object without a Name field resolves to an empty map rather than an error.');
    }

    // A list holding only blank ids resolves to an empty map without running a query.
    @isTest
    static void getRelatedNames_blankIds_resolveToNothingWithoutAQuery() {
        Test.startTest();
        Integer queriesBefore = Limits.getQueries();
        RLM_SplitInvoicesController.RelatedNamesResult result =
            RLM_SplitInvoicesController.getRelatedNames(null, new List<String>{ '', null }, null, null);
        Integer queriesAfter = Limits.getQueries();
        Test.stopTest();

        Assert.isTrue(result.arrangementNames.isEmpty(), 'Blank ids resolve to an empty map.');
        Assert.areEqual(queriesBefore, queriesAfter, 'Blank ids must not run a query.');
    }

    // InvoiceRow maps a queried invoice, including the names on its three lookups. Invoices
    // are not insertable, so the row is built from an invoice deserialized with its
    // relationships, the shape the correlation query returns.
    @isTest
    static void invoiceRow_mapsFieldsAndLookupNames() {
        Id invoiceId = fakeId('Invoice', 1);
        Id accountId = fakeId('Account', 1);
        Id arrangementId = fakeId('BillingArrangement', 1);
        Id profileId = fakeId('BillingAccount', 1);
        Date invoiceDate = Date.newInstance(2026, 1, 15);
        SObject inv = invoiceFromJson(new Map<String, Object>{
            'attributes' => new Map<String, Object>{ 'type' => 'Invoice' },
            'Id' => invoiceId,
            'DocumentNumber' => 'INV-0001',
            'InvoiceDate' => invoiceDate,
            'Balance' => 250,
            'Status' => 'Posted',
            'BillingAccountId' => accountId,
            'BillingAccount' => related('Account', accountId, 'RLM Split Account'),
            'BillingArrangementId' => arrangementId,
            'BillingArrangement' => related('BillingArrangement', arrangementId, 'RLM Split Arrangement'),
            'BillingProfileId' => profileId,
            'BillingProfile' => related('BillingAccount', profileId, 'RLM Split Profile'),
            'BillingArrangementVerNumber' => 3
        });

        Test.startTest();
        RLM_SplitInvoicesController.InvoiceRow row = new RLM_SplitInvoicesController.InvoiceRow(inv);
        Test.stopTest();

        Assert.areEqual(String.valueOf(invoiceId), String.valueOf(row.Id), 'Invoice id.');
        Assert.areEqual('INV-0001', row.DocumentNumber, 'Document number.');
        Assert.areEqual(invoiceDate, row.InvoiceDate, 'Invoice date.');
        Assert.areEqual(250, row.Balance, 'Balance.');
        Assert.areEqual('Posted', row.Status, 'Status.');
        Assert.areEqual(String.valueOf(accountId), row.billingAccountId, 'Billing account id.');
        Assert.areEqual('RLM Split Account', row.billingAccountName, 'Billing account name.');
        Assert.areEqual(String.valueOf(arrangementId), row.billingArrangementId, 'Billing arrangement id.');
        Assert.areEqual('RLM Split Arrangement', row.billingArrangementName, 'Billing arrangement name.');
        Assert.areEqual(String.valueOf(profileId), row.billingProfileId, 'Billing profile id.');
        Assert.areEqual('RLM Split Profile', row.billingProfileName, 'Billing profile name.');
        Assert.areEqual('3', row.billingArrangementVerNumber, 'The version number is shown as text.');
    }

    // An invoice with no lookups set leaves every id and name null rather than failing.
    @isTest
    static void invoiceRow_withoutLookups_leavesIdsAndNamesNull() {
        SObject inv = invoiceFromJson(new Map<String, Object>{
            'attributes' => new Map<String, Object>{ 'type' => 'Invoice' },
            'Id' => fakeId('Invoice', 2),
            'Status' => 'Draft'
        });

        Test.startTest();
        RLM_SplitInvoicesController.InvoiceRow row = new RLM_SplitInvoicesController.InvoiceRow(inv);
        Test.stopTest();

        Assert.areEqual('Draft', row.Status, 'Status.');
        Assert.isNull(row.billingAccountId, 'No billing account id.');
        Assert.isNull(row.billingAccountName, 'No billing account name.');
        Assert.isNull(row.billingArrangementId, 'No billing arrangement id.');
        Assert.isNull(row.billingArrangementName, 'No billing arrangement name.');
        Assert.isNull(row.billingProfileId, 'No billing profile id.');
        Assert.isNull(row.billingProfileName, 'No billing profile name.');
        Assert.isNull(row.billingArrangementVerNumber, 'No version number.');
    }

    // For an admin an unknown correlation id is an empty list (see above). A user who cannot
    // read invoices gets a handled error from the correlation list instead, while the billing
    // info call still returns rather than throwing.
    @isTest
    static void userWithoutInvoiceAccess_getsAHandledListErrorAndInfoWithoutThrowing() {
        // Minimum Access with no license or permission set: no billing object is readable.
        User u = RLM_BillingUITestUsers.create(new List<String>(), new List<String>());
        Id fakeInvoice = fakeId('Invoice', 3);
        Boolean premise = false;
        Boolean listThrew = false;
        RLM_SplitInvoicesController.CurrentInvoiceBillingInfo info;
        Test.startTest();
        System.runAs(u) {
            try {
                Database.query('SELECT Id FROM Invoice LIMIT 1', AccessLevel.USER_MODE);
            } catch (QueryException e) {
                premise = true;
            }
            try {
                RLM_SplitInvoicesController.getInvoicesByCorrelation('RLM-NO-ACCESS');
            } catch (AuraHandledException e) {
                listThrew = true;
            }
            info = RLM_SplitInvoicesController.getCurrentInvoiceBillingInfo(fakeInvoice);
        }
        Test.stopTest();
        Assert.isTrue(premise, 'PRECONDITION: this user must be unable to read Invoice.');
        Assert.isTrue(listThrew, 'An unreadable invoice query must surface as an AuraHandledException.');
        // Reaching here means the billing info call returned instead of throwing; it degrades
        // to an empty info.
        Assert.isNotNull(info, 'The billing info call returns an info object.');
        Assert.isNull(info.billingArrangementName, 'The returned info is empty: no arrangement name.');
        Assert.isNull(info.billingArrangementVerNumber, 'The returned info is empty: no version number.');
    }

    private static Id fakeId(String objectName, Integer n) {
        String prefix = Schema.getGlobalDescribe().get(objectName).getDescribe().getKeyPrefix();
        return Id.valueOf(prefix + String.valueOf(n).leftPad(12, '0'));
    }

    private static Map<String, Object> related(String objectName, Id recordId, String name) {
        return new Map<String, Object>{
            'attributes' => new Map<String, Object>{ 'type' => objectName },
            'Id' => recordId,
            'Name' => name
        };
    }

    // Read-only fields and relationships cannot be set on a constructed sObject; JSON can.
    private static SObject invoiceFromJson(Map<String, Object> fields) {
        return (SObject) JSON.deserialize(JSON.serialize(fields), Invoice.class);
    }
}
