@IsTest
private with sharing class RLM_AvalaraJSONBuilderTest {

    private static Map<String, Object> asMap(Object value) {
        return (Map<String, Object>) value;
    }

    private static Decimal toDecimal(Object value) {
        return Decimal.valueOf(String.valueOf(value));
    }

    private static Map<String, Object> build(commercetax.CalculateTaxRequest request) {
        String payload = RLM_AvalaraJSONBuilder.getInstance().frameJsonForGetTaxOrderItem(request);
        Assert.isTrue(String.isNotBlank(payload), 'The builder should return a JSON document.');
        return (Map<String, Object>) JSON.deserializeUntyped(payload);
    }

    @IsTest
    static void getInstance_returnsTheSameInstance() {
        Test.startTest();
        RLM_AvalaraJSONBuilder first = RLM_AvalaraJSONBuilder.getInstance();
        RLM_AvalaraJSONBuilder second = RLM_AvalaraJSONBuilder.getInstance();
        Test.stopTest();

        Assert.isNotNull(first, 'getInstance should create an instance.');
        Assert.isTrue(first === second, 'getInstance should return the cached singleton.');
    }

    @IsTest
    static void estimatedRequest_withCodesAndDates_buildsSalesOrder() {
        Datetime effective = Datetime.newInstanceGmt(2026, 1, 15, 12, 0, 0);
        Datetime lineEffective = Datetime.newInstanceGmt(2026, 1, 20, 12, 0, 0);
        commercetax.CalculateTaxRequest request = RLM_TaxTestFactory.request(
            commercetax.CalculateTaxType.Estimated,
            'DOC-100',
            new List<commercetax.TaxLineItemRequest>{ RLM_TaxTestFactory.line(200, 'L1', lineEffective) });
        request.isCommit = false;
        request.effectiveDate = effective;

        Test.startTest();
        Map<String, Object> body = build(request);
        Test.stopTest();

        Assert.areEqual('SalesOrder', body.get('type'), 'Estimated tax maps to an Avalara SalesOrder.');
        Assert.areEqual(RLM_TaxTestFactory.SELLER_CODE, body.get('companyCode'), 'The seller code is the company code.');
        Assert.areEqual(false, body.get('commit'), 'An explicit isCommit=false is written.');
        Assert.areEqual('DOC-100', body.get('code'), 'The document code is the Avalara code.');
        Assert.areEqual(RLM_TaxTestFactory.CUSTOMER_CODE, body.get('customerCode'), 'The customer code is used as is.');
        Assert.isTrue(String.valueOf(body.get('date')).startsWith('2026-01-15'),
            'The request effective date is the transaction date: ' + body.get('date'));

        List<Object> lines = (List<Object>) body.get('lines');
        Assert.areEqual(1, lines.size(), 'One JSON line per request line.');
        Map<String, Object> line = asMap(lines[0]);
        Assert.areEqual('L1', line.get('number'), 'The line number is written.');
        Assert.isTrue(toDecimal(line.get('quantity')) == 2, 'quantity: ' + line.get('quantity'));
        Assert.isTrue(toDecimal(line.get('amount')) == 200, 'amount: ' + line.get('amount'));
        Assert.areEqual(RLM_TaxTestFactory.TAX_CODE, line.get('taxCode'), 'taxCode');

        Map<String, Object> addresses = asMap(line.get('addresses'));
        Map<String, Object> shipFrom = asMap(addresses.get('ShipFrom'));
        Assert.areEqual('1 Market St', shipFrom.get('line1'), 'ShipFrom.line1 is the street.');
        Assert.areEqual('1 Market St', shipFrom.get('line2'),
            'Known gap: line2 repeats the street instead of a second address line. Update this test when it is fixed.');
        Assert.areEqual('San Francisco', shipFrom.get('city'), 'ShipFrom.city');
        Assert.areEqual('CA', shipFrom.get('region'), 'ShipFrom.region is the state.');
        Assert.areEqual('US', shipFrom.get('country'), 'ShipFrom.country');
        Assert.areEqual('94105', shipFrom.get('postalCode'), 'ShipFrom.postalCode');
        Map<String, Object> shipTo = asMap(addresses.get('ShipTo'));
        Assert.areEqual('Seattle', shipTo.get('city'), 'ShipTo.city');
        Assert.areEqual('WA', shipTo.get('region'), 'ShipTo.region');
        Map<String, Object> origin = asMap(addresses.get('pointOfOrderOrigin'));
        Assert.areEqual('Austin', origin.get('city'), 'The Sold To address is the point of order origin.');
        Assert.areEqual('78701', origin.get('postalCode'), 'pointOfOrderOrigin.postalCode');
        String payload = JSON.serialize(body);
        Assert.isFalse(payload.contains('Denver'), 'The Bill To address is not sent.');
        Assert.isFalse(payload.contains('Chicago'), 'The tax engine address is not sent.');

        // Pins current behaviour: the builder writes taxOverride before closing the addresses
        // object, so the block lands inside "addresses", not on the line itself.
        Assert.isFalse(line.containsKey('taxOverride'),
            'Known gap: taxOverride is not written at line level. Update this test when it is fixed.');
        Map<String, Object> taxOverride = asMap(addresses.get('taxOverride'));
        Assert.isNotNull(taxOverride,
            'Known gap: taxOverride is written inside addresses. Update this test when it is fixed.');
        Assert.isTrue(String.valueOf(taxOverride.get('taxDate')).startsWith('2026-01-20'),
            'The taxOverride carries the line effective date: ' + taxOverride.get('taxDate'));
    }

    @IsTest
    static void actualRequest_withAccountAndNoSeller_usesAccountNameAndDefaults() {
        Account customer = new Account(Name = 'Avalara Builder Test Customer');
        insert customer;

        commercetax.CalculateTaxRequest request = new commercetax.CalculateTaxRequest(commercetax.CalculateTaxType.Actual);
        request.customerDetails = new commercetax.TaxCustomerDetailsRequest(String.valueOf(customer.Id), null, null, null);
        request.sellerDetails = null;
        request.documentCode = null;
        request.referenceEntityId = 'REF-ENTITY-1';
        request.isCommit = true;
        request.effectiveDate = null;
        request.lineItems = new List<commercetax.TaxLineItemRequest>{
            RLM_TaxTestFactory.line(150, null, null),
            RLM_TaxTestFactory.line(50, null, null)
        };

        Date todayBeforeBuild = Date.today();
        Test.startTest();
        Map<String, Object> body = build(request);
        Test.stopTest();

        Assert.areEqual('SalesInvoice', body.get('type'), 'Actual tax maps to an Avalara SalesInvoice.');
        Assert.areEqual('billing2', body.get('companyCode'), 'No seller details fall back to the billing2 company.');
        Assert.areEqual(true, body.get('commit'), 'isCommit=true is written.');
        Assert.areEqual('REF-ENTITY-1', body.get('code'), 'The reference entity id is the code when no document code is set.');
        Assert.areEqual('Avalara Builder Test Customer', body.get('customerCode'),
            'With no customer code the account name is looked up.');
        // Today, or tomorrow if the build ran across midnight.
        Set<String> acceptedDates = new Set<String>{
            String.valueOf(todayBeforeBuild), String.valueOf(todayBeforeBuild.addDays(1))
        };
        Assert.isTrue(acceptedDates.contains(String.valueOf(body.get('date'))),
            'No effective date defaults to today: ' + body.get('date'));

        List<Object> lines = (List<Object>) body.get('lines');
        Assert.areEqual(2, lines.size(), 'Every request line is written once.');
        Map<String, Object> first = asMap(lines[0]);
        Assert.isFalse(first.containsKey('number'), 'A null line number is omitted.');
        Assert.isTrue(toDecimal(first.get('amount')) == 150, 'First line amount: ' + first.get('amount'));
        Assert.isTrue(toDecimal(asMap(lines[1]).get('amount')) == 50, 'Second line amount');
        Assert.isFalse(JSON.serialize(body).contains('taxOverride'), 'No line effective date means no taxOverride.');
    }

    @IsTest
    static void request_withoutCommitCodesOrAccountId_omitsFieldsAndUsesCustomerCode() {
        commercetax.CalculateTaxRequest request = RLM_TaxTestFactory.request(
            commercetax.CalculateTaxType.Estimated, null, RLM_TaxTestFactory.lines(100));
        request.customerDetails = new commercetax.TaxCustomerDetailsRequest('', 'CUST-EMPTY-ACCOUNT', null, null);
        request.isCommit = null;
        request.referenceEntityId = null;

        Test.startTest();
        Map<String, Object> body = build(request);
        Test.stopTest();

        Assert.isFalse(body.containsKey('commit'), 'A null isCommit is omitted.');
        Assert.isFalse(body.containsKey('code'), 'No document code and no reference entity means no code.');
        Assert.areEqual('CUST-EMPTY-ACCOUNT', body.get('customerCode'),
            'An empty account id is ignored and the customer code is used.');
    }

    @IsTest
    static void request_withoutCustomerDetails_rethrowsNullPointer() {
        commercetax.CalculateTaxRequest request = RLM_TaxTestFactory.request(
            commercetax.CalculateTaxType.Estimated, 'DOC-NPE', RLM_TaxTestFactory.lines(100));
        request.customerDetails = null;

        Exception caught;
        Test.startTest();
        try {
            RLM_AvalaraJSONBuilder.getInstance().frameJsonForGetTaxOrderItem(request);
        } catch (Exception e) {
            caught = e;
        }
        Test.stopTest();

        Assert.isNotNull(caught,
            'Known gap: missing customer details are not guarded and throw a raw NullPointerException. '
            + 'Update this test when it is fixed.');
        Assert.isInstanceOfType(caught, NullPointerException.class,
            'Known gap: missing customer details are not guarded and throw a raw NullPointerException. '
            + 'Update this test when it is fixed. ' + caught);
    }

    @IsTest
    static void request_withMalformedAccountId_rethrowsStringException() {
        commercetax.CalculateTaxRequest request = RLM_TaxTestFactory.request(
            commercetax.CalculateTaxType.Estimated, 'DOC-BAD-ID', RLM_TaxTestFactory.lines(100));
        request.customerDetails = new commercetax.TaxCustomerDetailsRequest('not-an-id', null, null, null);

        Exception caught;
        Test.startTest();
        try {
            RLM_AvalaraJSONBuilder.getInstance().frameJsonForGetTaxOrderItem(request);
        } catch (Exception e) {
            caught = e;
        }
        Test.stopTest();

        Assert.isNotNull(caught,
            'Known gap: a malformed account id is not validated and Id.valueOf throws a raw StringException. '
            + 'Update this test when it is fixed.');
        Assert.isInstanceOfType(caught, StringException.class,
            'Known gap: a malformed account id is not validated and Id.valueOf throws a raw StringException. '
            + 'Update this test when it is fixed. ' + caught);
    }
}
