@isTest
private class RLM_InvoiceTaxSummaryControllerTest {

    // The InvoiceLineTax query returns no rows in a test (see the first test's note), so toRows,
    // which maps each aggregate group to a row, is tested with real AggregateResult rows from
    // Account aggregates aliased like the controller's query.
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

    // Industry stands in for the currency column, so two groups share a name: toRows keeps every
    // group as its own row and never merges rows by name.
    @isTest
    static void toRows_buildsOneRowPerGroupInTheGivenOrder() {
        insertAccounts();
        List<RLM_InvoiceTaxSummaryController.TaxSummaryRow> rows = RLM_InvoiceTaxSummaryController.toRows([
            SELECT Name taxName, Industry currencyIsoCode, SUM(AnnualRevenue) totalTaxAmount
            FROM Account
            WHERE Name LIKE 'RLM Tax Summary %'
            GROUP BY Name, Industry
            ORDER BY Name DESC, SUM(AnnualRevenue)
        ]);
        Assert.areEqual(3, rows.size(), 'One row per group, including two groups with the same name.');
        Assert.areEqual('RLM Tax Summary B', rows[0].taxName, 'Rows keep the given order, not re-sorted.');
        Assert.areEqual('Energy', rows[0].currencyIsoCode, 'The first group\'s second key.');
        Assert.areEqual(-2, rows[0].totalTaxAmount, 'The first group\'s total, sign kept (a credit).');
        Assert.areEqual('RLM Tax Summary B', rows[1].taxName, 'The same name again, as its own row.');
        Assert.areEqual('Banking', rows[1].currencyIsoCode, 'The second group\'s second key.');
        Assert.areEqual(2, rows[1].totalTaxAmount, 'The second group\'s total.');
        Assert.areEqual('RLM Tax Summary A', rows[2].taxName, 'The third group\'s name.');
        Assert.areEqual('Banking', rows[2].currencyIsoCode, 'The third group\'s second key.');
        Assert.areEqual(1.25, rows[2].totalTaxAmount, 'The third group\'s total, fraction kept.');
    }

    // With the real CurrencyIsoCode column (the query's GROUP BY puts both B accounts in one group),
    // the row carries the group's real currency code and total. The two amounts net to zero, and
    // a zero total is still a row.
    @isTest
    static void toRows_readsTheRealCurrencyColumn() {
        String corporate = insertAccounts();
        List<RLM_InvoiceTaxSummaryController.TaxSummaryRow> rows = RLM_InvoiceTaxSummaryController.toRows([
            SELECT Name taxName, CurrencyIsoCode currencyIsoCode, SUM(AnnualRevenue) totalTaxAmount
            FROM Account
            WHERE Name = 'RLM Tax Summary B'
            GROUP BY Name, CurrencyIsoCode
        ]);
        Assert.areEqual(1, rows.size(), 'One group.');
        Assert.areEqual(0, rows[0].totalTaxAmount, 'The group\'s total: 2 and -2 net to zero.');
        Assert.areEqual(corporate, rows[0].currencyIsoCode, 'The group\'s currency.');
    }

    @isTest
    static void toRows_noGroupsReturnsAnEmptyList() {
        List<RLM_InvoiceTaxSummaryController.TaxSummaryRow> rows =
            RLM_InvoiceTaxSummaryController.toRows(new List<AggregateResult>());
        Assert.isNotNull(rows, 'A non-null list is returned.');
        Assert.areEqual(0, rows.size(), 'No groups, no rows.');
    }

    // A group whose grouped field is null (here Account.AccountNumber, which these accounts leave
    // blank, standing in for TaxName) gives a row with a null name.
    @isTest
    static void toRows_aNullGroupNameIsKept() {
        insertAccounts();
        List<RLM_InvoiceTaxSummaryController.TaxSummaryRow> rows = RLM_InvoiceTaxSummaryController.toRows([
            SELECT AccountNumber taxName, CurrencyIsoCode currencyIsoCode, SUM(AnnualRevenue) totalTaxAmount
            FROM Account
            WHERE Name LIKE 'RLM Tax Summary %'
            GROUP BY AccountNumber, CurrencyIsoCode
        ]);
        Assert.areEqual(1, rows.size(), 'No account has an AccountNumber: one group.');
        Assert.isNull(rows[0].taxName, 'A null group name stays null.');
        Assert.areEqual(1.25, rows[0].totalTaxAmount, 'The group\'s total.');
    }

    // A group whose amounts are all null has a null SUM: the row keeps the null total.
    @isTest
    static void toRows_aNullTotalIsKept() {
        insert new Account(Name = 'RLM Tax Summary No Revenue');
        List<RLM_InvoiceTaxSummaryController.TaxSummaryRow> rows = RLM_InvoiceTaxSummaryController.toRows([
            SELECT Name taxName, CurrencyIsoCode currencyIsoCode, SUM(AnnualRevenue) totalTaxAmount
            FROM Account
            WHERE Name = 'RLM Tax Summary No Revenue'
            GROUP BY Name, CurrencyIsoCode
        ]);
        Assert.areEqual(1, rows.size(), 'One group.');
        Assert.areEqual('RLM Tax Summary No Revenue', rows[0].taxName, 'The group\'s name.');
        Assert.isNull(rows[0].totalTaxAmount, 'A null total stays null.');
    }

    // An alias toRows reads but the query does not define is an error, not a blank row, so a
    // controller query whose aliases drift from toRows fails loudly at run time, on the first
    // invoice with tax lines. (No test runs the controller's own query with rows, so this does
    // not catch such a drift in CI.)
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
    // "RLM Tax Summary A" 1.25 (Banking), "RLM Tax Summary B" 2 (Banking) and -2 (Energy).
    // AnnualRevenue is Currency(18, 0), but an Apex insert keeps the fraction (measured on a 264
    // build); the 1.25 is there so a toRows that rounds the total fails.
    // Returns the corporate currency code.
    private static String insertAccounts() {
        String corporate = [SELECT IsoCode FROM CurrencyType WHERE IsCorporate = true LIMIT 1].IsoCode;
        List<Account> accounts = new List<Account>{
            new Account(Name = 'RLM Tax Summary A', AnnualRevenue = 1.25, Industry = 'Banking'),
            new Account(Name = 'RLM Tax Summary B', AnnualRevenue = 2, Industry = 'Banking'),
            new Account(Name = 'RLM Tax Summary B', AnnualRevenue = -2, Industry = 'Energy')
        };
        for (Account a : accounts) {
            a.CurrencyIsoCode = corporate;
        }
        insert accounts;
        return corporate;
    }
}
