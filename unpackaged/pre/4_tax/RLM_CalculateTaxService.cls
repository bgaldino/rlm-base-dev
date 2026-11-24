global class RLM_CalculateTaxService {
    // ============================================================================
    // CONSTANT 
    // ============================================================================
    private static final String AVALARA_ENDPOINT_URL_SANDBOX = 'https://sandbox-rest.avatax.com/api/v2';
    // Avalara Endpoint URL Production
    private static final String AVALARA_ENDPOINT_URL_PRODUCTION = 'https://rest.avatax.com/api/v2';
    @TestVisible private static final String NO_RESPONSE_MESSAGE = 'The tax engine returned no response.';

    @TestVisible
    private static String bodyOrNull(HttpResponse response) {
        return response == null ? null : response.getBody();
    }

    @TestVisible private static final String INCOMPLETE_RESPONSE_MESSAGE = 'The tax engine response is incomplete.';

    // Names the first value getTax needs that the engine response left out (a null total, a blank date,
    // or a line without its taxable flag, which the platform setter cannot take as null), or returns null
    // when the response can be mapped. Without it a missing value would reach a platform setter and end
    // as the general adapter error below instead of naming the field.
    @TestVisible
    private static String missingResponseValue(RLM_JsonSuccessParser parsed) {
        if (parsed.totalAmount == null) { return 'totalAmount'; }
        if (parsed.totalTax == null) { return 'totalTax'; }
        if (String.isBlank(parsed.taxDate)) { return 'taxDate'; }
        if (String.isBlank(parsed.transactionDate)) { return 'date'; }
        if (parsed.lines != null) {
            for (RLM_JsonSuccessParser.Lines line : parsed.lines) {
                if (line.lineAmount == null) { return 'lineAmount'; }
                if (line.taxCalculated == null) { return 'taxCalculated'; }
                if (String.isBlank(line.taxDate)) { return 'line taxDate'; }
                // The engine states per line whether the item was taxed (AvaTax isItemTaxable). The line
                // response needs that answer and there is no documented default, so a line without it
                // is incomplete rather than assumed taxable.
                if (line.isItemTaxable == null) { return 'isItemTaxable'; }
            }
        }
        return null;
    }

    @TestVisible private static final String INVALID_DATE_MESSAGE = 'The tax engine response has an invalid date.';

    // Names the first date the response carries that Date.valueOf cannot read, or null when all parse.
    // Date.valueOf throws TypeException for text that is not a date; any other exception it raises is
    // treated the same way, so no date text can throw out of getTax.
    @TestVisible
    private static String invalidResponseDate(RLM_JsonSuccessParser parsed) {
        if (!isDate(parsed.taxDate)) { return 'taxDate'; }
        if (!isDate(parsed.transactionDate)) { return 'date'; }
        if (parsed.lines != null) {
            for (RLM_JsonSuccessParser.Lines line : parsed.lines) {
                if (!isDate(line.taxDate)) { return 'line taxDate'; }
            }
        }
        return null;
    }

    private static Boolean isDate(String value) {
        try {
            Date.valueOf(value);
            return true;
        } catch (Exception e) {
            return false;
        }
    }

    @TestVisible private static final String UNREADABLE_RESPONSE_MESSAGE = 'The tax engine response could not be read.';
    @TestVisible private static final String HTTP_ERROR_PREFIX = 'The tax engine returned HTTP status ';
    @TestVisible private static final String ENGINE_ERROR_MESSAGE =
        'The tax engine could not calculate the tax. Ask your administrator to check the tax engine setup.';
    @TestVisible private static final String ADAPTER_ERROR_MESSAGE =
        'The tax could not be calculated because of an error in the tax adapter. Ask your administrator to check the tax engine setup.';

    // Every message this class returns is one of the fixed sentences above. Measured on a 264 org, the
    // message of an ErrorResponse is shown as written: the Connect calculate tax API returns it to the
    // caller, and the tax engine interaction log stores it. So every error return logs its detail here
    // for the administrator instead: what went wrong and, for an engine error, the engine's error codes.
    // No response body is logged: a success body echoes the transaction back, customer address
    // included, and an error body's message text can quote the request's values. The codes (the
    // error's code and each detail's code and refersTo) name the kind of error and the request field it
    // concerns, not a value. An unreadable body is logged only as unreadable.
    @TestVisible private static String lastDebugDetail;

    private static void debugEngineDetail(String what) {
        lastDebugDetail = what;
        System.debug(LoggingLevel.ERROR, 'RLM_CalculateTaxService ' + lastDebugDetail);
    }

    // The engine's error codes from a body parsed untyped: "code: X; details: Y (refersTo Z), ...", or a
    // note that the body has none. Only the code and refersTo strings are read; nothing else in the
    // body is logged.
    @TestVisible
    private static String engineErrorCodes(Object parsedBody) {
        if (parsedBody == null) {
            return 'body empty or not JSON';
        }
        Object error = parsedBody instanceof Map<String, Object> ? ((Map<String, Object>) parsedBody).get('error') : null;
        if (!(error instanceof Map<String, Object>)) {
            return 'no error codes in the body';
        }
        Map<String, Object> errorMap = (Map<String, Object>) error;
        List<String> parts = new List<String>{ 'code: ' + codeText(errorMap.get('code')) };
        Object details = errorMap.get('details');
        if (details instanceof List<Object>) {
            List<String> detailCodes = new List<String>();
            for (Object detail : (List<Object>) details) {
                if (detail instanceof Map<String, Object>) {
                    Map<String, Object> detailMap = (Map<String, Object>) detail;
                    String entry = codeText(detailMap.get('code'));
                    if (detailMap.get('refersTo') != null) {
                        entry += ' (refersTo ' + refersToText(detailMap.get('refersTo')) + ')';
                    }
                    detailCodes.add(entry);
                }
            }
            if (!detailCodes.isEmpty()) {
                parts.add('details: ' + String.join(detailCodes, ', '));
            }
        }
        return String.join(parts, '; ');
    }

    // Only values shaped like what AvaTax puts in these fields are logged. An error code must be an
    // error name: a capital letter, then letters only (GetTaxError, InvalidAddress). A refersTo must
    // be a field path: words of letters, each word optionally ending in one digit (line1) and
    // optionally indexed, joined by dots (Addresses[0], Lines[1].quantity, Addresses.ShipTo.Line1).
    // Anything else is not logged: not a string, text with spaces, a hyphen, or a run of digits
    // outside an index, such as a VAT id (GB123456789), a postal code (94105, SW1A1AA) or a customer
    // code (CUST-00123). Letters alone still pass, so a name put in one of these fields, as one word
    // (Acme) or dotted (Jane.Doe in a refersTo), would be logged, and so would an all-caps value
    // (ACME, or a region or country code such as WA or GB) and a short refersTo value of letters
    // ending in one digit (SW1, CUST1); AvaTax does not put values there.
    private static String codeText(Object value) {
        return identifierText(value, ERROR_CODE_SHAPE);
    }

    private static String refersToText(Object value) {
        return identifierText(value, FIELD_PATH_SHAPE);
    }

    private static final String ERROR_CODE_SHAPE = '[A-Z][A-Za-z]+';
    private static final String FIELD_PATH_SHAPE = '[A-Za-z]+[0-9]?(\\[[0-9]+\\])?(\\.[A-Za-z]+[0-9]?(\\[[0-9]+\\])?)*';

    private static String identifierText(Object value, String shape) {
        if (!(value instanceof String)) {
            return '(none)';
        }
        String text = (String) value;
        if (text.length() > CODE_LENGTH_LIMIT) {
            return '(not logged: too long)';
        }
        return Pattern.matches(shape, text) ? text : '(not logged: not a code)';
    }

    @TestVisible private static final Integer CODE_LENGTH_LIMIT = 100;

    // Names the first list in a success body that is not a list of objects (lines, addresses, summary,
    // messages, or a line's details), or returns null when each is absent, null or a list of objects.
    // The success parser refuses such a body too; this check runs first so the log names the field. A
    // body with the same key twice is checked here by its last value only; the parser still refuses
    // it if any value is of the wrong shape, logged as a parser failure.
    @TestVisible
    private static String misshapenResponseField(Map<String, Object> body) {
        for (String field : new List<String>{ 'lines', 'addresses', 'summary', 'messages' }) {
            if (!isListOfObjects(body.get(field))) {
                return field;
            }
        }
        if (body.get('lines') != null) {
            for (Object line : (List<Object>) body.get('lines')) {
                if (!isListOfObjects(((Map<String, Object>) line).get('details'))) {
                    return 'line details';
                }
            }
        }
        return null;
    }

    private static Boolean isListOfObjects(Object value) {
        if (value == null) {
            return true;
        }
        if (!(value instanceof List<Object>)) {
            return false;
        }
        for (Object element : (List<Object>) value) {
            if (!(element instanceof Map<String, Object>)) {
                return false;
            }
        }
        return true;
    }

    // The body as untyped JSON, or null when it cannot be read.
    @TestVisible
    private static Object parseBodyOrNull(String body) {
        if (String.isBlank(body)) {
            return null;
        }
        try {
            return JSON.deserializeUntyped(body);
        } catch (Exception e) {
            // Any failure to read the body, not only a JSONException, counts as no body, so a response
            // outside 2xx still returns its own status rather than the general adapter error.
            return null;
        }
    }

    // The parser reads money as Decimal; the platform response setters take Double.
    private static Double toDouble(Decimal value) {
        return value == null ? null : value.doubleValue();
    }

    public static commercetax.TaxEngineResponse getTax(commercetax.TaxEngineContext taxEngineContext) 
    { 
        try{
            commercetax.CalculateTaxRequest request = (commercetax.CalculateTaxRequest)taxEngineContext.getRequest();
            commercetax.calculatetaxtype requestType = request.taxtype;
            string referenceEntity = request.ReferenceEntityId;
            List<commercetax.TaxLineItemRequest> listOfLines = request.lineItems;
            if(listOfLines != null && !listOfLines.isEmpty()){
                RLM_HttpService sendHttpRequest = new RLM_HttpService();
                sendHttpRequest.addHeader('Content-type', 'application/json');
                String requestBody = RLM_AvalaraJSONBuilder.getInstance().frameJsonForGetTaxOrderItem(request);
                sendHttpRequest.post('/transactions/create',requestBody);
                HttpResponse httpResponse = sendHttpRequest.getResponse();
                if(httpResponse == null) {
                    // RLM_HttpService swallows a failed callout and leaves no response (it logs only the exception type).
                    debugEngineDetail('no response');
                    return new commercetax.ErrorResponse(commercetax.resultcode.TaxEngineError, '503', NO_RESPONSE_MESSAGE);
                }
                String responseString = bodyOrNull(httpResponse);
                system.debug('Heap size used ' +Limits.getHeapSize());

                // The HTTP status is checked before the body: a response outside 2xx is an error whose
                // code is that status, never a success body, even when the body is empty. Its message is
                // a fixed sentence naming the status; the engine's error codes, if the body has any, go
                // to the debug log.
                Integer statusCode = httpResponse.getStatusCode();
                if(statusCode < 200 || statusCode > 299) {
                    debugEngineDetail('HTTP status ' + statusCode + '; ' + engineErrorCodes(parseBodyOrNull(responseString)));
                    return new commercetax.ErrorResponse(commercetax.resultcode.TaxEngineError, String.valueOf(statusCode), HTTP_ERROR_PREFIX + statusCode + '.');
                }
                // A 2xx body that is empty, not a JSON object, or whose fields do not fit the success parser
                // (for example "totalAmount":"abc"), returns the 502 unreadable response. That includes a
                // 204 No Content on purpose: a tax calculation that returns no result has not calculated
                // the tax, so it is a failure, not a success with nothing in it.
                // Route on the body's top-level "error" key, not on the text "error" anywhere in it: a
                // successful body can carry the word in a tax name or a reason.
                Object parsedBody = parseBodyOrNull(responseString);
                if(!(parsedBody instanceof Map<String, Object>)) {
                    debugEngineDetail('response is not a JSON object');
                    return new commercetax.ErrorResponse(commercetax.resultcode.TaxEngineError, '502', UNREADABLE_RESPONSE_MESSAGE);
                }
                Object errorValue = ((Map<String, Object>) parsedBody).get('error');
                if(errorValue == null)
                {
                    String misshapen = misshapenResponseField((Map<String, Object>) parsedBody);
                    if(misshapen != null) {
                        debugEngineDetail('response field not a list of objects: ' + misshapen);
                        return new commercetax.ErrorResponse(commercetax.resultcode.TaxEngineError, '502', UNREADABLE_RESPONSE_MESSAGE);
                    }
                    commercetax.CalculateTaxResponse response = new commercetax.CalculateTaxResponse();
                    RLM_JsonSuccessParser jsonSuccessParserClass;
                    try {
                        jsonSuccessParserClass = RLM_JsonSuccessParser.parse(responseString);
                    } catch (JSONException e) {
                        // Only the type is logged: a platform JSONException message can quote the token
                        // it refused, which is a value from the response.
                        debugEngineDetail('response does not fit the success parser: ' + e.getTypeName());
                        return new commercetax.ErrorResponse(commercetax.resultcode.TaxEngineError, '502', UNREADABLE_RESPONSE_MESSAGE);
                    }
                    String missing = missingResponseValue(jsonSuccessParserClass);
                    if(missing != null) {
                        debugEngineDetail('response value missing: ' + missing);
                        return new commercetax.ErrorResponse(commercetax.resultcode.TaxEngineError, '502', INCOMPLETE_RESPONSE_MESSAGE);
                    }
                    String invalidDate = invalidResponseDate(jsonSuccessParserClass);
                    if(invalidDate != null) {
                        debugEngineDetail('response value not a date: ' + invalidDate);
                        return new commercetax.ErrorResponse(commercetax.resultcode.TaxEngineError, '502', INVALID_DATE_MESSAGE);
                    }
                    response.setTaxTransactionType(request.taxTransactionType);
                    response.setDocumentCode(jsonSuccessParserClass.code);
                    response.setReferenceDocumentCode(jsonSuccessParserClass.referenceCode);
                    // Only Temporary and Committed are mapped. Any other engine status (AvaTax also
                    // documents Saved, Posted, Adjusted and Cancelled, among others) leaves the response
                    // status unset rather than guessing a platform status for it.
                    if(jsonSuccessParserClass.status == 'Temporary')  {
                        response.setStatus(commercetax.TaxTransactionStatus.Uncommitted);
                    }
                    if(jsonSuccessParserClass.status == 'Committed') {
                        response.setStatus(commercetax.TaxTransactionStatus.Committed);
                    }
                    response.setTaxType(requestType);
                    commercetax.AmountDetailsResponse headerAmountResponse = new commercetax.AmountDetailsResponse();
                    headerAmountResponse.setTotalAmountWithTax(toDouble(jsonSuccessParserClass.totalAmount) + jsonSuccessParserClass.totaltax);
                    headerAmountResponse.setExemptAmount(toDouble(jsonSuccessParserClass.totalExempt));
                    headerAmountResponse.setTotalAmount(toDouble(jsonSuccessParserClass.totalAmount));
                    headerAmountResponse.setTaxAmount(jsonSuccessParserClass.totalTax);
                    response.setAmountDetails(headerAmountResponse);
                    response.setStatusDescription(jsonSuccessParserClass.adjustmentReason);
                    response.setEffectiveDate(date.valueof(jsonSuccessParserClass.taxDate));
                    response.setTransactionDate(date.valueof(jsonSuccessParserClass.transactionDate));
                    response.setReferenceEntityId(referenceEntity);
                    response.setTaxTransactionId(jsonSuccessParserClass.id);
                    response.setCurrencyIsoCode(request.currencyIsoCode);
                    List<commercetax.LineItemResponse> lineItemResponses = new List<commercetax.LineItemResponse>();
                    for(RLM_JsonSuccessParser.Lines linesToProcess: jsonSuccessParserClass.lines == null ? new List<RLM_JsonSuccessParser.Lines>() : jsonSuccessParserClass.lines)
                    {
                        commercetax.LineItemResponse lineItemResponse = new commercetax.LineItemResponse();
                        List<commercetax.TaxDetailsResponse> taxDetailsResponses = new List<commercetax.TaxDetailsResponse>();
                        for(RLM_JsonSuccessParser.details linesDetails : linesToProcess.details == null ? new List<RLM_JsonSuccessParser.details>() : linesToProcess.details)
                        {
                            commercetax.TaxDetailsResponse taxDetailsResponse = new commercetax.TaxDetailsResponse();
                            // A detail with no exempt amount (null) is not exempt, like one with 0.
                            if(linesDetails.exemptAmount != null && linesDetails.exemptAmount != 0){
                                taxDetailsResponse.setExemptAmount(toDouble(linesDetails.exemptAmount));
                            }
                                commercetax.ImpositionResponse imposition = new commercetax.ImpositionResponse();
                                    imposition.setSubType(linesDetails.taxName);
                                    imposition.setType(linesDetails.ratetype);
                                    imposition.setSubType(linesDetails.taxName);
                                    taxDetailsResponse.setImposition(imposition);
                                commercetax.JurisdictionResponse jurisdiction = new commercetax.JurisdictionResponse();
                                    jurisdiction.setCountry(linesDetails.country);
                                    jurisdiction.setRegion(linesDetails.region);
                                    jurisdiction.setName(linesDetails.jurisName);
                                    jurisdiction.setStateAssignedNumber(linesDetails.stateAssignedNo);
                                    jurisdiction.setId(linesDetails.jurisCode);
                                    jurisdiction.setLevel(linesDetails.jurisType);
                                    taxDetailsResponse.setJurisdiction(jurisdiction);
                                taxDetailsResponse.setRate(linesDetails.rate); // each detail keeps its own rate
                                taxDetailsResponse.setTax(linesDetails.taxCalculated);
                                taxDetailsResponse.setTaxableAmount(toDouble(linesDetails.taxableAmount));
                                taxDetailsResponse.setTaxAuthorityTypeId(String.valueOf(linesDetails.taxAuthorityTypeId));
                                taxDetailsResponse.setTaxId(linesDetails.id);
                                taxDetailsResponse.setTaxRegionId(linesDetails.region);
                                taxDetailsResponses.add(taxDetailsResponse);    
                            
                        }
                            lineItemResponse.setTaxes(taxDetailsResponses);
                            lineItemResponse.setEffectiveDate(date.valueof(linesToProcess.taxDate));
                                commercetax.AmountDetailsResponse amountResponse = new commercetax.AmountDetailsResponse();
                                amountResponse.setTaxAmount(linesToProcess.taxCalculated);
                                amountResponse.setTotalAmount(toDouble(linesToProcess.lineAmount));
                                amountResponse.setTotalAmountWithTax(toDouble(linesToProcess.lineAmount)+linesToProcess.taxCalculated);
                                amountResponse.setExemptAmount(toDouble(linesToProcess.exemptAmount));
                                lineItemResponse.setAmountDetails(amountResponse);
                            lineItemResponse.setIsTaxable(linesToProcess.isItemTaxable);
                            lineItemResponse.setProductCode(linesToProcess.itemCode);
                            lineItemResponse.setTaxCode(linesToProcess.taxCode);
                            lineItemResponse.setLineNumber(linesToProcess.lineNumber);
                            lineItemResponse.setQuantity(linesToProcess.quantity);
                            lineItemResponses.add(lineItemResponse);
                    }
                    response.setLineItems(lineItemResponses);
                    return response;
                }
                else
                {
                    // As for a non-2xx status above, the engine's error codes go to the debug log.
                    debugEngineDetail('engine error; ' + engineErrorCodes(parsedBody));
                    return new commercetax.ErrorResponse(commercetax.resultcode.TaxEngineError, '501', ENGINE_ERROR_MESSAGE);
                }
            }else return null;
        }
        catch (Exception e)
        {
            // Any other fault (a request the adapter cannot read or frame, or a response value a
            // platform setter refuses) is returned as an error with a fixed sentence, like the engine
            // errors above, rather than thrown out of the tax engine call. Its type and where it was
            // thrown go to the debug log; its message does not, as some messages quote the value they
            // refused. A limit exception cannot be caught and still ends the transaction.
            debugEngineDetail('adapter error: ' + e.getTypeName() + ' at ' + e.getStackTraceString());
            return new commercetax.ErrorResponse(commercetax.resultcode.TaxEngineError, '500', ADAPTER_ERROR_MESSAGE);
        }
    }
}