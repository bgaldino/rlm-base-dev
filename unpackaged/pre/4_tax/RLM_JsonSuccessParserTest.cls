@IsTest
private with sharing class RLM_JsonSuccessParserTest {

    // Every field each parser class maps. Each level (transaction, line, first detail, address,
    // summary, message) also carries an unmapped scalar, an unmapped object or array
    // (consumeObject) and a null value (VALUE_NULL skip), followed by at least one mapped field
    // (lines, details, rateType, taxRegionId, exemption, source) whose value must still be parsed.
    private static final String FULL_TRANSACTION = '{'
        + '"id": 123456,'
        + '"code": "DOC-PARSE-1",'
        + '"referenceCode": "REF-PARSE-1",'
        + '"companyId": 468039,'
        + '"date": "2026-01-15",'
        + '"taxDate": "2026-01-16",'
        + '"status": "Committed",'
        + '"type": "SalesInvoice",'
        + '"reconciled": true,'
        + '"totalAmount": 1000,'
        + '"totalExempt": 50,'
        + '"totalTax": 72.5,'
        + '"totalTaxable": 950,'
        + '"totalTaxCalculated": 72.5,'
        + '"adjustmentReason": "NotAdjusted",'
        + '"locked": false,'
        + '"version": 2,'
        + '"modifiedDate": "2026-01-16T10:00:00Z",'
        + '"modifiedUserId": 53894,'
        + '"description": null,'
        + '"customerVendorCode": "ignored-scalar",'
        + '"parameters": {"nested": {"deeper": [1, 2, {"x": 1}]}, "flag": true},'
        + '"invoiceMessages": [{"a": 1}, [2, 3]],'
        + '"lines": [{'
        +     '"id": 1,'
        +     '"transactionId": 123456,'
        +     '"lineNumber": "L-1",'
        +     '"discountAmount": 0,'
        +     '"exemptAmount": 50,'
        +     '"exemptCertId": 7,'
        +     '"isItemTaxable": true,'
        +     '"lineAmount": 1000,'
        +     '"quantity": 2,'
        +     '"reportingDate": "2026-01-16",'
        +     '"tax": 72.5,'
        +     '"taxableAmount": 950,'
        +     '"taxCalculated": 72.5,'
        +     '"taxCode": "P0000000",'
        +     '"taxDate": "2026-01-16",'
        +     '"taxIncluded": false,'
        +     '"itemCode": "QB-ITEM-1",'
        +     '"description": null,'
        +     '"taxOverrideType": "None",'
        +     '"taxOverride": {"type": "None", "reasons": ["a", {"b": 1}]},'
        +     '"nonPassthroughDetails": [],'
        +     '"details": [{'
        +         '"id": 11,'
        +         '"transactionLineId": 1,'
        +         '"transactionId": 123456,'
        +         '"country": "US",'
        +         '"region": "CA",'
        +         '"exemptAmount": 0,'
        +         '"jurisCode": "06",'
        +         '"jurisName": "CALIFORNIA",'
        +         '"stateAssignedNo": "38",'
        +         '"jurisType": "STA",'
        +         '"nonTaxableAmount": 0,'
        +         '"rate": 0.0725,'
        +         '"tax": 72.5,'
        +         '"taxableAmount": 950,'
        +         '"taxType": "Sales",'
        +         '"taxName": "CA STATE TAX",'
        +         '"taxAuthorityTypeId": 45,'
        +         '"taxCalculated": 72.5,'
        +         '"jurisdictionType": "State",'
        +         '"liabilityType": {"code": "Seller"},'
        +         '"unitOfBasis": null,'
        +         '"rateType": "General"'
        +     '}, {'
        +         '"id": 12,'
        +         '"jurisName": "SAN FRANCISCO"'
        +     '}]'
        + '}],'
        + '"addresses": [{'
        +     '"id": 21,'
        +     '"transactionId": 123456,'
        +     '"boundaryLevel": "Address",'
        +     '"line1": "255 S. King Street",'
        +     '"city": "Seattle",'
        +     '"region": "WA",'
        +     '"postalCode": "98104",'
        +     '"country": "US",'
        +     '"latitude": "47.59821",'
        +     '"validatedAddresses": [{"line1": "255 S KING ST", "geo": {"lat": 47.6}}],'
        +     '"line2": null,'
        +     '"taxRegionId": 2109700'
        + '}],'
        + '"summary": [{'
        +     '"country": "US",'
        +     '"region": "WA",'
        +     '"jurisType": "State",'
        +     '"jurisCode": "53",'
        +     '"jurisName": "WASHINGTON",'
        +     '"taxAuthorityType": 45,'
        +     '"stateAssignedNo": "1700",'
        +     '"taxType": "Sales",'
        +     '"taxName": "WA STATE TAX",'
        +     '"taxGroup": "Group-1",'
        +     '"rateType": "General",'
        +     '"taxable": 232,'
        +     '"rate": 0.065,'
        +     '"tax": 15.08,'
        +     '"taxCalculated": 15.08,'
        +     '"nonTaxable": 0,'
        +     '"taxSubType": "S",'
        +     '"rateTypeCode": {"value": "G"},'
        +     '"reportingTaxable": null,'
        +     '"exemption": 7'
        + '}],'
        + '"messages": [{'
        +     '"summary": "Address not geocoded",'
        +     '"details": "Address fell back to a zip centroid",'
        +     '"refersTo": "Addresses[0]",'
        +     '"severity": "Warning",'
        +     '"helpLink": "https://developer.avalara.com/",'
        +     '"extra": {"k": [1]},'
        +     '"code": null,'
        +     '"source": "Avalara.AvaTax.Services"'
        + '}]'
        + '}';

    /** Double fields compared to a decimal literal with a tolerance, independent of Double/Decimal promotion. */
    private static void assertClose(Decimal expected, Double actual, String label) {
        Assert.isNotNull(actual, label + ' should be parsed.');
        Assert.isTrue(Math.abs(Decimal.valueOf(actual) - expected) < 0.000001, label + ': expected ' + expected + ', got ' + actual);
    }

    @IsTest
    static void parse_fullTransaction_mapsHeaderFields() {
        Test.startTest();
        RLM_JsonSuccessParser parsed = RLM_JsonSuccessParser.parse(FULL_TRANSACTION);
        Test.stopTest();

        Assert.areEqual('123456', parsed.id, 'Numeric id is kept as text.');
        Assert.areEqual('DOC-PARSE-1', parsed.code, 'code');
        Assert.areEqual('REF-PARSE-1', parsed.referenceCode, 'referenceCode');
        Assert.areEqual(468039, parsed.companyId, 'companyId');
        Assert.areEqual('2026-01-15', parsed.transactionDate, 'The JSON "date" key maps to transactionDate.');
        Assert.areEqual('2026-01-16', parsed.taxDate, 'taxDate');
        Assert.areEqual('Committed', parsed.status, 'status');
        Assert.areEqual('SalesInvoice', parsed.type_Z, 'The JSON "type" key maps to type_Z.');
        Assert.areEqual(true, parsed.reconciled, 'reconciled');
        Assert.areEqual(1000, parsed.totalAmount, 'totalAmount');
        Assert.areEqual(50, parsed.totalExempt, 'totalExempt');
        assertClose(72.5, parsed.totalTax, 'totalTax');
        Assert.areEqual(950, parsed.totalTaxable, 'totalTaxable');
        assertClose(72.5, parsed.totalTaxCalculated, 'totalTaxCalculated');
        Assert.areEqual('NotAdjusted', parsed.adjustmentReason, 'adjustmentReason');
        Assert.areEqual(false, parsed.locked, 'locked');
        Assert.areEqual(2, parsed.version, 'version');
        Assert.areEqual('2026-01-16T10:00:00Z', parsed.modifiedDate, 'modifiedDate');
        Assert.areEqual(53894, parsed.modifiedUserId, 'modifiedUserId');
        Assert.areEqual(1, parsed.lines.size(), 'One line follows the skipped unmapped object and array.');
        Assert.areEqual(1, parsed.addresses.size(), 'addresses');
        Assert.areEqual(1, parsed.summary.size(), 'summary');
        Assert.areEqual(1, parsed.messages.size(), 'messages');
    }

    @IsTest
    static void parse_fullTransaction_mapsLinesAndDetails() {
        Test.startTest();
        RLM_JsonSuccessParser parsed = RLM_JsonSuccessParser.parse(FULL_TRANSACTION);
        Test.stopTest();

        RLM_JsonSuccessParser.Lines line = parsed.lines[0];
        Assert.areEqual('1', line.id, 'line.id');
        Assert.areEqual('123456', line.transactionId, 'line.transactionId');
        Assert.areEqual('L-1', line.lineNumber, 'line.lineNumber');
        Assert.areEqual(0, line.discountAmount, 'line.discountAmount');
        Assert.areEqual(50, line.exemptAmount, 'line.exemptAmount');
        Assert.areEqual(7, line.exemptCertId, 'line.exemptCertId');
        Assert.areEqual(true, line.isItemTaxable, 'line.isItemTaxable');
        Assert.areEqual(1000, line.lineAmount, 'line.lineAmount');
        assertClose(2, line.quantity, 'line.quantity');
        Assert.areEqual('2026-01-16', line.reportingDate, 'line.reportingDate');
        assertClose(72.5, line.tax, 'line.tax');
        Assert.areEqual(950, line.taxableAmount, 'line.taxableAmount');
        assertClose(72.5, line.taxCalculated, 'line.taxCalculated');
        Assert.areEqual('P0000000', line.taxCode, 'line.taxCode');
        Assert.areEqual('2026-01-16', line.taxDate, 'line.taxDate');
        Assert.areEqual(false, line.taxIncluded, 'line.taxIncluded');
        Assert.areEqual('QB-ITEM-1', line.itemCode, 'line.itemCode');
        Assert.areEqual(2, line.details.size(), 'Both details follow the skipped empty array.');

        RLM_JsonSuccessParser.Details detail = line.details[0];
        Assert.areEqual('11', detail.id, 'detail.id');
        Assert.areEqual('1', detail.transactionLineId, 'detail.transactionLineId');
        Assert.areEqual('123456', detail.transactionId, 'detail.transactionId');
        Assert.areEqual('US', detail.country, 'detail.country');
        Assert.areEqual('CA', detail.region, 'detail.region');
        Assert.areEqual(0, detail.exemptAmount, 'detail.exemptAmount');
        Assert.areEqual('06', detail.jurisCode, 'detail.jurisCode');
        Assert.areEqual('CALIFORNIA', detail.jurisName, 'detail.jurisName');
        Assert.areEqual('38', detail.stateAssignedNo, 'detail.stateAssignedNo');
        Assert.areEqual('STA', detail.jurisType, 'detail.jurisType');
        Assert.areEqual(0, detail.nonTaxableAmount, 'detail.nonTaxableAmount');
        assertClose(0.0725, detail.rate, 'detail.rate');
        assertClose(72.5, detail.tax, 'detail.tax');
        Assert.areEqual(950, detail.taxableAmount, 'detail.taxableAmount');
        Assert.areEqual('Sales', detail.taxType, 'detail.taxType');
        Assert.areEqual('CA STATE TAX', detail.taxName, 'detail.taxName');
        Assert.areEqual(45, detail.taxAuthorityTypeId, 'detail.taxAuthorityTypeId');
        assertClose(72.5, detail.taxCalculated, 'detail.taxCalculated');
        Assert.areEqual('General', detail.rateType, 'detail.rateType');

        RLM_JsonSuccessParser.Details sparse = line.details[1];
        Assert.areEqual('12', sparse.id, 'Second detail id');
        Assert.areEqual('SAN FRANCISCO', sparse.jurisName, 'Second detail jurisName');
        Assert.isNull(sparse.rate, 'Fields absent from the JSON stay null.');
    }

    @IsTest
    static void parse_fullTransaction_mapsAddressesSummaryAndMessages() {
        Test.startTest();
        RLM_JsonSuccessParser parsed = RLM_JsonSuccessParser.parse(FULL_TRANSACTION);
        Test.stopTest();

        RLM_JsonSuccessParser.Addresses address = parsed.addresses[0];
        Assert.areEqual('21', address.id, 'address.id');
        Assert.areEqual('123456', address.transactionId, 'address.transactionId');
        Assert.areEqual('Address', address.boundaryLevel, 'address.boundaryLevel');
        Assert.areEqual('255 S. King Street', address.line1, 'address.line1');
        Assert.areEqual('Seattle', address.city, 'address.city');
        Assert.areEqual('WA', address.region, 'address.region');
        Assert.areEqual('98104', address.postalCode, 'address.postalCode');
        Assert.areEqual('US', address.country, 'address.country');
        Assert.areEqual(2109700, address.taxRegionId, 'address.taxRegionId');

        RLM_JsonSuccessParser.Summary summary = parsed.summary[0];
        Assert.areEqual('US', summary.country, 'summary.country');
        Assert.areEqual('WA', summary.region, 'summary.region');
        Assert.areEqual('State', summary.jurisType, 'summary.jurisType');
        Assert.areEqual('53', summary.jurisCode, 'summary.jurisCode');
        Assert.areEqual('WASHINGTON', summary.jurisName, 'summary.jurisName');
        Assert.areEqual(45, summary.taxAuthorityType, 'summary.taxAuthorityType');
        Assert.areEqual('1700', summary.stateAssignedNo, 'summary.stateAssignedNo');
        Assert.areEqual('Sales', summary.taxType, 'summary.taxType');
        Assert.areEqual('WA STATE TAX', summary.taxName, 'summary.taxName');
        Assert.areEqual('Group-1', summary.taxGroup, 'summary.taxGroup');
        Assert.areEqual('General', summary.rateType, 'summary.rateType');
        Assert.areEqual(232, summary.taxable, 'summary.taxable');
        assertClose(0.065, summary.rate, 'summary.rate');
        assertClose(15.08, summary.tax, 'summary.tax');
        assertClose(15.08, summary.taxCalculated, 'summary.taxCalculated');
        Assert.areEqual(0, summary.nonTaxable, 'summary.nonTaxable');
        Assert.areEqual(7, summary.exemption, 'summary.exemption follows the skipped entries.');

        RLM_JsonSuccessParser.Messages message = parsed.messages[0];
        Assert.areEqual('Address not geocoded', message.summary, 'message.summary');
        Assert.areEqual('Address fell back to a zip centroid', message.details, 'message.details');
        Assert.areEqual('Addresses[0]', message.refersTo, 'message.refersTo');
        Assert.areEqual('Warning', message.severity, 'message.severity');
        Assert.areEqual('Avalara.AvaTax.Services', message.source, 'message.source');
    }

    @IsTest
    static void parse_emptyObject_leavesScalarsAndListsNull() {
        Test.startTest();
        RLM_JsonSuccessParser parsed = RLM_JsonSuccessParser.parse('{}');
        Test.stopTest();

        Assert.isNull(parsed.id, 'id');
        Assert.isNull(parsed.code, 'code');
        Assert.isNull(parsed.transactionDate, 'transactionDate');
        Assert.isNull(parsed.status, 'status');
        Assert.isNull(parsed.type_Z, 'type_Z');
        Assert.isNull(parsed.reconciled, 'reconciled');
        Assert.isNull(parsed.totalAmount, 'totalAmount');
        Assert.isNull(parsed.totalTax, 'totalTax');
        Assert.isNull(parsed.lines, 'lines are only created when the key is present.');
        Assert.isNull(parsed.addresses, 'addresses');
        Assert.isNull(parsed.summary, 'summary');
        Assert.isNull(parsed.messages, 'messages');
    }

    @IsTest
    static void parse_fractionalAmounts_truncatesIntegerFields() {
        Test.startTest();
        RLM_JsonSuccessParser parsed = RLM_JsonSuccessParser.parse(
            '{"totalAmount": 232.5, "lines": [{"lineAmount": 232.5, "taxCalculated": 23.43}]}');
        Test.stopTest();

        Assert.areEqual(232, parsed.totalAmount,
            'Known gap: Integer amount fields read with getIntegerValue truncate 232.5 to 232. '
            + 'Update this test when it is fixed.');
        Assert.areEqual(232, parsed.lines[0].lineAmount,
            'Known gap: Integer amount fields read with getIntegerValue truncate 232.5 to 232. '
            + 'Update this test when it is fixed.');
        Assert.isTrue(parsed.lines[0].taxCalculated == Double.valueOf('23.43'),
            'Double fields keep their fraction: ' + parsed.lines[0].taxCalculated);
    }

    @IsTest
    static void consumeObject_skipsNestedValueAndStopsOnItsClosingToken() {
        JSONParser parser = JSON.createParser('{"skip": {"a": [1, {"b": 2}], "c": {}}, "next": "kept"}');
        parser.nextToken(); // START_OBJECT
        parser.nextToken(); // FIELD_NAME "skip"
        parser.nextToken(); // START_OBJECT of the value to skip

        Test.startTest();
        RLM_JsonSuccessParser.consumeObject(parser);
        Test.stopTest();

        Assert.areEqual(JSONToken.END_OBJECT, parser.getCurrentToken(),
            'consumeObject should stop on the closing token of the skipped value.');
        Assert.areEqual(JSONToken.FIELD_NAME, parser.nextToken(), 'The next sibling field should follow.');
        Assert.areEqual('next', parser.getText(), 'The sibling after the skipped value is intact.');
    }
}
