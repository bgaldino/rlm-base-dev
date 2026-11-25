@isTest
private class RLM_InvoiceTaxSummaryControllerTest {

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

    // toRows carries the mapping that getTaxSummaryByInvoice applies to each aggregate group.
    // The InvoiceLineTax query itself stays live-only (no InvoiceLine can be created in a test).
    // Documented, not pinned (no InvoiceLineTax row can be created): the controller's
    // SUM(TaxAmount) ... GROUP BY TaxName, CurrencyIsoCode returns each total in the corporate
    // currency, but labels it with the group's CurrencyIsoCode, so a non-corporate tax line's
    // total would be shown under the wrong currency.
    @isTest
    static void toRows_buildsOneRowPerGroupInOrder() {
        List<RLM_InvoiceTaxSummaryController.TaxSummaryRow> rows = RLM_InvoiceTaxSummaryController.toRows(
            new List<Map<String, Object>>{
                taxGroup('State Sales Tax', 12.50, 'EUR'),
                taxGroup('County Tax', 3.25, 'USD')
            });
        Assert.areEqual(2, rows.size(), 'One row per aggregate group.');
        Assert.areEqual('State Sales Tax', rows[0].taxName, 'Rows keep the given (query) order, not sorted again.');
        Assert.areEqual(12.50, rows[0].totalTaxAmount, 'The first group\'s total.');
        Assert.areEqual('EUR', rows[0].currencyIsoCode, 'The first group\'s currency.');
        Assert.areEqual('County Tax', rows[1].taxName, 'The second group\'s name.');
        Assert.areEqual(3.25, rows[1].totalTaxAmount, 'The second group\'s total.');
        Assert.areEqual('USD', rows[1].currencyIsoCode, 'The second group\'s currency.');
    }

    @isTest
    static void toRows_noGroupsReturnsAnEmptyList() {
        List<RLM_InvoiceTaxSummaryController.TaxSummaryRow> rows =
            RLM_InvoiceTaxSummaryController.toRows(new List<Map<String, Object>>());
        Assert.isNotNull(rows, 'A non-null list is returned.');
        Assert.areEqual(0, rows.size(), 'No groups, no rows.');
    }

    // A group whose TaxName is null still has the key, with a null value: the row keeps the null.
    @isTest
    static void toRows_aNullTaxNameIsKept() {
        List<RLM_InvoiceTaxSummaryController.TaxSummaryRow> rows = RLM_InvoiceTaxSummaryController.toRows(
            new List<Map<String, Object>>{ taxGroup(null, 1.00, 'USD') });
        Assert.areEqual(1, rows.size(), 'The group still makes a row.');
        Assert.isNull(rows[0].taxName, 'A null tax name stays null.');
        Assert.areEqual(1.00, rows[0].totalTaxAmount, 'The total is kept.');
    }

    // The maps come from AggregateResult.getPopulatedFieldsAsMap(), whose keys keep each alias's
    // case and are looked up case-sensitively. An Account aggregate with the controller's three
    // aliases checks that toRows reads a real AggregateResult's map, not only hand-built ones.
    @isTest
    static void toRows_readsTheMapOfARealAggregateResult() {
        insert new List<Account>{
            new Account(Name = 'RLM Tax Summary B', AnnualRevenue = 2),
            new Account(Name = 'RLM Tax Summary B', AnnualRevenue = 3),
            new Account(Name = 'RLM Tax Summary A', AnnualRevenue = 1.25)
        };
        List<Map<String, Object>> groups = new List<Map<String, Object>>();
        for (AggregateResult ar : [
            SELECT Name taxName, CurrencyIsoCode currencyIsoCode, SUM(AnnualRevenue) totalTaxAmount
            FROM Account
            WHERE Name LIKE 'RLM Tax Summary %'
            GROUP BY Name, CurrencyIsoCode
            ORDER BY Name, CurrencyIsoCode
        ]) {
            groups.add(ar.getPopulatedFieldsAsMap());
        }
        List<RLM_InvoiceTaxSummaryController.TaxSummaryRow> rows = RLM_InvoiceTaxSummaryController.toRows(groups);

        Assert.areEqual(2, rows.size(), 'One row per name.');
        Assert.areEqual('RLM Tax Summary A', rows[0].taxName, 'The alias taxName is read.');
        Assert.areEqual(1.25, rows[0].totalTaxAmount, 'The alias totalTaxAmount is read.');
        Assert.areEqual(UserInfo.getDefaultCurrency(), rows[0].currencyIsoCode,
            'The alias currencyIsoCode is read (a new Account takes the running user\'s currency).');
        Assert.areEqual('RLM Tax Summary B', rows[1].taxName, 'The second group\'s name.');
        Assert.areEqual(5, rows[1].totalTaxAmount, 'Two rows in one group are summed.');
    }

    private static Map<String, Object> taxGroup(String taxName, Decimal total, String currencyIsoCode) {
        return new Map<String, Object>{
            'taxName' => taxName,
            'totalTaxAmount' => total,
            'currencyIsoCode' => currencyIsoCode
        };
    }
}
