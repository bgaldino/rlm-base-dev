@isTest
private class RLM_InvoiceTaxSummaryControllerTest {

    // The InvoiceLineTax query is live-only: its rows need an InvoiceLine, which a test cannot
    // create. toRows, which maps each aggregate group to a row, is tested with real AggregateResult
    // rows from an Account aggregate that uses the controller's three aliases.
    // Documented, not pinned (no InvoiceLineTax row can be created): the controller's
    // SUM(TaxAmount) ... GROUP BY TaxName, CurrencyIsoCode returns each total in the corporate
    // currency, but labels it with the group's CurrencyIsoCode, so a non-corporate tax line's
    // total would be shown under the wrong currency.

    // An InvoiceLineTax row needs an InvoiceLine, which cannot be created in Apex tests; a null id
    // and a well-formed but non-existent Invoice id both drive the empty aggregate path.
    @isTest
    static void getTaxSummaryByInvoice_nullId_returnsEmptyList() {
        Test.startTest();
        List<RLM_InvoiceTaxSummaryController.TaxSummaryRow> rows =
            RLM_InvoiceTaxSummaryController.getTaxSummaryByInvoice(null);
        Test.stopTest();
        System.assertNotEquals(null, rows, 'A non-null list should always be returned.');
        System.assertEquals(0, rows.size(), 'A null invoice id short-circuits to an empty list.');
    }

    @isTest
    static void getTaxSummaryByInvoice_unknownInvoice_returnsEmptyList() {
        Id fakeInvoice = Id.valueOf(Invoice.SObjectType.getDescribe().getKeyPrefix() + '000000000000');
        Test.startTest();
        List<RLM_InvoiceTaxSummaryController.TaxSummaryRow> rows =
            RLM_InvoiceTaxSummaryController.getTaxSummaryByInvoice(fakeInvoice);
        Test.stopTest();
        System.assertNotEquals(null, rows, 'A non-null list should always be returned.');
        System.assertEquals(0, rows.size(), 'No tax rows exist for a non-existent invoice.');
    }

    // The positive path as a billing operations user rather than the deploying admin
    // (RLM_BillingUI is assigned only after this bundle deploys): the user can run the tax
    // query's exact field list in USER_MODE, and an unknown invoice returns an empty list.
    @isTest
    static void getTaxSummaryByInvoice_billingOperationsUser_runsTheQuery() {
        User u = RLM_BillingUITestUsers.create(
            new List<String>{ 'RLM_BillingUI', 'RevenueLifecycleManagementBillingOperations' },
            new List<String>{ RLM_BillingUITestUsers.BILLING_PSL });
        Id fakeInvoice = Id.valueOf(Invoice.SObjectType.getDescribe().getKeyPrefix() + '000000000000');
        String readError;
        List<RLM_InvoiceTaxSummaryController.TaxSummaryRow> rows;
        Test.startTest();
        System.runAs(u) {
            try {
                Database.query(
                    'SELECT TaxName, TaxAmount, CurrencyIsoCode FROM InvoiceLineTax '
                    + 'WHERE InvoiceLine.InvoiceId != null LIMIT 1',
                    AccessLevel.USER_MODE);
            } catch (QueryException e) {
                readError = e.getMessage();
            }
            Assert.isNull(readError,
                'PRECONDITION: a billing operations user can run the tax query\'s fields: ' + readError);
            rows = RLM_InvoiceTaxSummaryController.getTaxSummaryByInvoice(fakeInvoice);
        }
        Test.stopTest();
        Assert.isNotNull(rows, 'The tax summary list is returned.');
        Assert.areEqual(0, rows.size(), 'No tax rows exist for a non-existent invoice.');
    }

    @isTest
    static void toRows_buildsOneRowPerGroupInTheGivenOrder() {
        String corporate = insertAccounts();
        List<RLM_InvoiceTaxSummaryController.TaxSummaryRow> rows = RLM_InvoiceTaxSummaryController.toRows([
            SELECT Name taxName, CurrencyIsoCode currencyIsoCode, SUM(AnnualRevenue) totalTaxAmount
            FROM Account
            WHERE Name LIKE 'RLM Tax Summary %'
            GROUP BY Name, CurrencyIsoCode
            ORDER BY Name DESC
        ]);
        Assert.areEqual(2, rows.size(), 'One row per group.');
        Assert.areEqual('RLM Tax Summary B', rows[0].taxName, 'Rows keep the given order, not re-sorted.');
        Assert.areEqual(5, rows[0].totalTaxAmount, 'The group\'s total: two accounts summed.');
        Assert.areEqual(corporate, rows[0].currencyIsoCode, 'The group\'s currency.');
        Assert.areEqual('RLM Tax Summary A', rows[1].taxName, 'The second group\'s name.');
        Assert.areEqual(1.25, rows[1].totalTaxAmount, 'The second group\'s total.');
        Assert.areEqual(corporate, rows[1].currencyIsoCode, 'The second group\'s currency.');
    }

    @isTest
    static void toRows_noGroupsReturnsAnEmptyList() {
        List<RLM_InvoiceTaxSummaryController.TaxSummaryRow> rows =
            RLM_InvoiceTaxSummaryController.toRows(new List<AggregateResult>());
        Assert.isNotNull(rows, 'A non-null list is returned.');
        Assert.areEqual(0, rows.size(), 'No groups, no rows.');
    }

    // A group whose grouped field is null (here Account.Industry, standing in for TaxName) gives a
    // row with a null name.
    @isTest
    static void toRows_aNullGroupNameIsKept() {
        insertAccounts();
        List<RLM_InvoiceTaxSummaryController.TaxSummaryRow> rows = RLM_InvoiceTaxSummaryController.toRows([
            SELECT Industry taxName, CurrencyIsoCode currencyIsoCode, SUM(AnnualRevenue) totalTaxAmount
            FROM Account
            WHERE Name LIKE 'RLM Tax Summary %'
            GROUP BY Industry, CurrencyIsoCode
        ]);
        Assert.areEqual(1, rows.size(), 'No account has an Industry: one group.');
        Assert.isNull(rows[0].taxName, 'A null group name stays null.');
        Assert.areEqual(6.25, rows[0].totalTaxAmount, 'The group\'s total.');
    }

    // An alias toRows reads but the query does not define is an error, not a blank row: a query
    // whose aliases drift from toRows fails loudly.
    @isTest
    static void toRows_aMissingAliasThrows() {
        insertAccounts();
        List<AggregateResult> groups = [
            SELECT Name name, CurrencyIsoCode currencyIsoCode, SUM(AnnualRevenue) totalTaxAmount
            FROM Account
            WHERE Name LIKE 'RLM Tax Summary %'
            GROUP BY Name, CurrencyIsoCode
        ];
        String error;
        try {
            RLM_InvoiceTaxSummaryController.toRows(groups);
        } catch (SObjectException e) {
            error = e.getMessage();
        }
        Assert.isNotNull(error, 'A missing alias throws.');
        Assert.isTrue(error.containsIgnoreCase('taxName'), 'The error names the missing alias: ' + error);
    }

    // Three accounts in the corporate currency, so SUM(AnnualRevenue) needs no conversion:
    // "RLM Tax Summary A" 1.25, "RLM Tax Summary B" 2 and 3. Returns the corporate currency code.
    private static String insertAccounts() {
        String corporate = [SELECT IsoCode FROM CurrencyType WHERE IsCorporate = true LIMIT 1].IsoCode;
        List<Account> accounts = new List<Account>{
            new Account(Name = 'RLM Tax Summary A', AnnualRevenue = 1.25),
            new Account(Name = 'RLM Tax Summary B', AnnualRevenue = 2),
            new Account(Name = 'RLM Tax Summary B', AnnualRevenue = 3)
        };
        for (Account a : accounts) {
            a.put('CurrencyIsoCode', corporate);
        }
        insert accounts;
        return corporate;
    }
}
