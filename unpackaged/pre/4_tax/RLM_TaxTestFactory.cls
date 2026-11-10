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
 * "...[status=Committed,taxTransactionType=Credit,...]"), so it depends on that format.
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

    /** Ship From = San Francisco, Ship To = Seattle, Sold To (and Bill To) = Austin. */
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

    /** A request with customer code, seller code and USD; no account id, commit flag or dates. */
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
     * Use it for stable code and enum fields only, not for dates (their text depends on the time zone).
     * An empty String prints as "field=" and an unset or null field as "field=<null>". Observed
     * exception: ErrorResponse prints a null error code as an empty one ("errorCode=").
     */
    public static void assertResponseField(Object response, String field, String value, String message) {
        Assert.isTrue(countResponseField(response, field, value) > 0,
            message + ' Expected ' + field + '=' + value + ' in: ' + String.valueOf(response));
    }

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
        Assert.areEqual(0, Math.mod(count, copies), 'Every printed copy should list the same entries: ' + described);
        return count / copies;
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
