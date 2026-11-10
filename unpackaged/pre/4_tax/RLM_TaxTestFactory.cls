/**
 * Test-only builders for the pre/4_tax adapter tests.
 *
 * The commercetax request constructors (CalculateTaxRequest, TaxLineItemRequest,
 * LineTaxAddressesRequest, TaxAddressRequest, TaxCustomerDetailsRequest,
 * TaxSellerDetailsRequest, TaxEngineContext) are documented as test-only: they throw
 * outside the Apex test context, so they may only be used from @IsTest code.
 *
 * The commercetax response classes have setters only. assertResponseField reads values back
 * from the platform's String.valueOf form of a response (for example
 * "...[status=Committed,taxTransactionType=Credit,...]"), so it depends on that undocumented
 * format. Accepted risk: if a release changes it, responseStringForm_matchesHelperPremise names
 * the cause; every String-form assertion fails with it.
 */
@IsTest
public with sharing class RLM_TaxTestFactory {

    public static final String CUSTOMER_CODE = 'CUST-001';
    public static final String SELLER_CODE = 'SELLER-01';
    public static final String TAX_CODE = 'P0000000';
    public static final String PRODUCT_CODE = 'QB-TEST-SKU';
    public static final String NAMED_URI = 'callout:RLM_Test_Tax_Engine';

    public static commercetax.TaxAddressRequest address(String street, String city, String state, String postalCode) {
        Double noCoordinate = null;
        return new commercetax.TaxAddressRequest(
            city, 'US', noCoordinate, noCoordinate, postalCode, state, street, 'LOC-' + postalCode);
    }

    /**
     * Ship From = San Francisco, Ship To = Seattle, Sold To (and Bill To) = Austin. The fifth
     * argument (taxEngineAddress) is set to Ship From.
     */
    public static commercetax.LineTaxAddressesRequest lineAddresses() {
        commercetax.TaxAddressRequest shipFrom = address('1 Market St', 'San Francisco', 'CA', '94105');
        commercetax.TaxAddressRequest shipTo = address('255 S King St', 'Seattle', 'WA', '98104');
        commercetax.TaxAddressRequest soldTo = address('100 Congress Ave', 'Austin', 'TX', '78701');
        return new commercetax.LineTaxAddressesRequest(shipFrom, shipTo, soldTo, soldTo, shipFrom);
    }

    /** A line with quantity 2, tax code P0000000 and the addresses above. */
    public static commercetax.TaxLineItemRequest line(Double amount, String lineNumber, Datetime effectiveDate) {
        Double quantity = 2;
        return new commercetax.TaxLineItemRequest(
            lineAddresses(), amount, 'Test line', PRODUCT_CODE, quantity, lineNumber, TAX_CODE, effectiveDate);
    }

    public static List<commercetax.TaxLineItemRequest> lines(Double amount) {
        return new List<commercetax.TaxLineItemRequest>{ line(amount, '1', null) };
    }

    /**
     * A request with customer code, seller code and USD; no account id, commit flag, dates, or tax
     * transaction type (RLM_CalculateTaxService requires one, so its success tests set it).
     */
    public static commercetax.CalculateTaxRequest request(
        commercetax.CalculateTaxType taxType,
        String documentCode,
        List<commercetax.TaxLineItemRequest> lineItems
    ) {
        commercetax.CalculateTaxRequest request = new commercetax.CalculateTaxRequest(taxType);
        request.documentCode = documentCode;
        request.lineItems = lineItems;
        request.customerDetails = new commercetax.TaxCustomerDetailsRequest(null, CUSTOMER_CODE, null, null);
        request.sellerDetails = new commercetax.TaxSellerDetailsRequest(SELLER_CODE);
        request.currencyIsoCode = 'USD';
        return request;
    }

    public static commercetax.TaxEngineContext context(commercetax.CalculateTaxRequest request) {
        return new commercetax.TaxEngineContext(request, commercetax.RequestType.CalculateTax, NAMED_URI);
    }

    /** RequestType has a single value (CalculateTax); a null type drives the adapters' fall-through branch. */
    public static commercetax.TaxEngineContext contextWithoutRequestType(commercetax.CalculateTaxRequest request) {
        commercetax.RequestType noType = null;
        return new commercetax.TaxEngineContext(request, noType, NAMED_URI);
    }

    /**
     * The commercetax response classes have setters only. Their String form lists the values an
     * adapter set (for example documentCode=DOC-1 or errorCode=404), so it is the read-back path.
     * An empty String prints as "field=" and an unset or null field as "field=<null>". Observed
     * exception: ErrorResponse prints a null error code as an empty one ("errorCode=").
     * responseStringForm_matchesHelperPremise below pins this format.
     */
    public static void assertResponseField(Object response, String field, String value, String message) {
        Assert.isTrue(countResponseField(response, field, value) > 0,
            message + ' Expected ' + field + '=' + value + ' in: ' + String.valueOf(response) + PREMISE_HINT);
    }

    /**
     * Asserts at least one field=<value> entry whose value matches valueRegex. Dates print like
     * "Fri Jun 15 12:00:00 GMT 2001" in the runner's time zone, so match a mid-year noon date by
     * its year (YEAR_2001) and a defaulted one by NOT_NULL.
     */
    public static void assertResponseFieldMatches(Object response, String field, String valueRegex, String message) {
        String described = String.valueOf(response);
        Pattern entry = Pattern.compile('(?<=[\\[,])' + Pattern.quote(field + '=') + '(' + valueRegex + ')(?=[,\\]])');
        Assert.isTrue(entry.matcher(described).find(),
            message + ' Expected ' + field + '=' + valueRegex + ' in: ' + described + PREMISE_HINT);
    }

    /** A date value of 2001 (see DATE_2001). */
    public static final String YEAR_2001 = '[^,\\]]*\\b2001\\b[^,\\]]*';
    /** Any value other than the platform's "<null>" marker. */
    public static final String NOT_NULL = '(?!<null>)[^,\\]]+';
    /** Mid-year noon GMT: the year cannot shift in any time zone. */
    public static final Datetime DATE_2001 = Datetime.newInstanceGmt(2001, 6, 15, 12, 0, 0);

    private static final String PREMISE_HINT =
        ' (If RLM_TaxTestFactory.responseStringForm_matchesHelperPremise also fails, the platform format changed:'
        + ' that test names the cause; every String-form assertion fails with it.)';

    /**
     * How many times field=value appears as a whole entry in one copy of the response (e.g. once
     * per line item). The String form prints the response's delegate once per "delegate=" label
     * (twice for a CalculateTaxResponse, observed), so the raw count is divided by that.
     */
    public static Integer countResponseField(Object response, String field, String value) {
        String described = String.valueOf(response);
        Pattern entry = Pattern.compile('(?<=[\\[,])' + Pattern.quote(field + '=' + value) + '(?=[,\\]])');
        Matcher matcher = entry.matcher(described);
        Integer count = 0;
        while (matcher.find()) {
            count++;
        }
        Integer copies = Math.max(1, described.countMatches('delegate='));
        Assert.areEqual(0, Math.mod(count, copies),
            'Every printed copy should list the same entries: ' + described + PREMISE_HINT);
        return count / copies;
    }

    /**
     * Premise for every response assertion in these tests: the platform's undocumented String form
     * of commercetax responses. If a release changes it, this test names the cause.
     */
    @IsTest
    static void responseStringForm_matchesHelperPremise() {
        // Line 1: null addresses, one tax detail with null imposition and jurisdiction, amounts,
        // and a 2001 effective date. Line 2 and the header carry non-null addresses.
        commercetax.TaxDetailsResponse taxDetail = new commercetax.TaxDetailsResponse();
        taxDetail.setImposition(null);
        taxDetail.setJurisdiction(null);
        Double lineAmount = 100;
        commercetax.AmountDetailsResponse amounts = new commercetax.AmountDetailsResponse();
        amounts.setTotalAmount(lineAmount);
        commercetax.LineItemResponse first = new commercetax.LineItemResponse();
        first.setLineNumber('1');
        first.setAddresses(null);
        first.setTaxes(new List<commercetax.TaxDetailsResponse>{ taxDetail });
        first.setAmountDetails(amounts);
        first.setEffectiveDate(DATE_2001);
        commercetax.LineItemResponse second = new commercetax.LineItemResponse();
        second.setLineNumber('2');
        second.setAddresses(new commercetax.AddressesResponse());
        commercetax.CalculateTaxResponse response = new commercetax.CalculateTaxResponse();
        response.setDocumentCode('PREMISE-1');
        response.setStatus(commercetax.TaxTransactionStatus.Committed);
        response.setTaxTransactionType(commercetax.TaxTransactionType.Credit);
        response.setTransactionDate(DATE_2001);
        response.setAddresses(new commercetax.AddressesResponse());
        response.setLineItems(new List<commercetax.LineItemResponse>{ first, second });

        commercetax.CalculateTaxResponse emptyResponse = new commercetax.CalculateTaxResponse();
        emptyResponse.setDocumentCode('');

        commercetax.ErrorResponse error = new commercetax.ErrorResponse(commercetax.ResultCode.TaxEngineError, null, 'm');

        Test.startTest();
        String described = String.valueOf(response);
        String errorDescribed = String.valueOf(error);
        Test.stopTest();

        // Nested line, tax, amount and address objects do not add delegate= labels.
        Assert.areEqual(2, described.countMatches('delegate='), 'A CalculateTaxResponse prints its delegate twice: ' + described);
        Assert.areEqual(1, countResponseField(response, 'addresses', '<null>'), 'Only line 1 has null addresses.');
        Assert.areEqual(1, countResponseField(response, 'imposition', '<null>'), 'A null imposition prints as <null>.');
        Assert.areEqual(1, countResponseField(response, 'jurisdiction', '<null>'), 'A null jurisdiction prints as <null>.');
        assertResponseFieldMatches(response, 'effectiveDate', YEAR_2001, 'A line effective date prints with its year.');
        Assert.areEqual(1, countResponseField(emptyResponse, 'documentCode', ''), 'An empty String prints as field=.');
        Assert.areEqual(1, countResponseField(emptyResponse, 'lineItems', '<null>'), 'Unset line items print as <null>.');
        Assert.areEqual(1, errorDescribed.countMatches('delegate='), 'An ErrorResponse prints its delegate once: ' + errorDescribed);
        Assert.areEqual(1, countResponseField(response, 'documentCode', 'PREMISE-1'), 'A String field prints as field=value.');
        Assert.areEqual(1, countResponseField(response, 'status', 'Committed'), 'An enum prints by name.');
        Assert.areEqual(1, countResponseField(response, 'taxTransactionType', 'Credit'), 'An enum prints by name.');
        Assert.areEqual(1, countResponseField(response, 'referenceEntityId', '<null>'), 'An unset field prints as <null>.');
        Assert.areEqual(1, countResponseField(response, 'lineNumber', '1'), 'Nested line items are listed.');
        Assert.areEqual(1, countResponseField(response, 'lineNumber', '2'), 'Each nested line item is listed once.');
        assertResponseFieldMatches(response, 'transactionDate', YEAR_2001, 'A date prints with its year.');
        Assert.areEqual(1, countResponseField(error, 'errorCode', ''), 'ErrorResponse prints a null error code as empty.');
        Assert.areEqual(1, countResponseField(error, 'errorMessage', 'm'), 'ErrorResponse prints its message.');
    }

    /** Records every request and answers with a fixed status and body. Never reaches the network. */
    public class RecordingHttpMock implements HttpCalloutMock {
        public List<HttpRequest> requests = new List<HttpRequest>();
        private Integer statusCode;
        private String body;

        public RecordingHttpMock(Integer statusCode, String body) {
            this.statusCode = statusCode;
            this.body = body;
        }

        public HttpResponse respond(HttpRequest request) {
            requests.add(request);
            HttpResponse response = new HttpResponse();
            response.setStatusCode(statusCode);
            response.setStatus(statusCode >= 200 && statusCode < 300 ? 'OK' : 'Error');
            response.setHeader('Content-Type', 'application/json');
            response.setBody(body);
            return response;
        }
    }
}
