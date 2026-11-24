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
    // when the response can be mapped. Without it a missing value throws a raw exception out of the
    // tax engine call.
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

    @TestVisible private static final Integer DEBUG_BODY_LENGTH = 2000;

    // Every message this class returns is one of the fixed sentences above. Measured on a 264 org, the
    // message of an ErrorResponse is shown as written: the Connect calculate tax API returns it to the
    // caller, and the tax engine interaction log stores it. So every error return logs its detail here
    // for the administrator instead: what went wrong and, where the body is the only diagnostic (an
    // error or unreadable response), the start of that body. A success body that fails a check is not
    // logged: it echoes the transaction back, customer address included, and the check names the value.
    @TestVisible private static String lastDebugDetail;

    private static void debugEngineDetail(String what) {
        lastDebugDetail = what;
        System.debug(LoggingLevel.ERROR, 'RLM_CalculateTaxService ' + lastDebugDetail);
    }

    private static void debugEngineDetail(String what, String body) {
        debugEngineDetail(what + '; body: ' + (String.isBlank(body) ? '(empty)' : body.abbreviate(DEBUG_BODY_LENGTH)));
    }

    // The body as untyped JSON, or null when it is not valid JSON.
    @TestVisible
    private static Object parseBodyOrNull(String body) {
        if (String.isBlank(body)) {
            return null;
        }
        try {
            return JSON.deserializeUntyped(body);
        } catch (JSONException e) {
            return null;
        }
    }

    // The parser reads money as Decimal; the platform response setters take Double.
    private static Double toDouble(Decimal value) {
        return value == null ? null : value.doubleValue();
    }

    public static commercetax.TaxEngineResponse getTax(commercetax.TaxEngineContext taxEngineContext) 
    { 
        commercetax.CalculateTaxRequest request = (commercetax.CalculateTaxRequest)taxEngineContext.getRequest();
        commercetax.calculatetaxtype requestType = request.taxtype;
        string referenceEntity = request.ReferenceEntityId;
        try{
            List<commercetax.TaxLineItemRequest> listOfLines = request.lineItems;
            if(listOfLines != null && !listOfLines.isEmpty()){
                RLM_HttpService sendHttpRequest = new RLM_HttpService();
                sendHttpRequest.addHeader('Content-type', 'application/json');
                String requestBody = RLM_AvalaraJSONBuilder.getInstance().frameJsonForGetTaxOrderItem(request);
                sendHttpRequest.post('/transactions/create',requestBody);
                //system.debug('Request '+requestBody);
                HttpResponse httpResponse = sendHttpRequest.getResponse();
                if(httpResponse == null) {
                    // RLM_HttpService swallows a failed callout and leaves no response (it logs the cause).
                    debugEngineDetail('no response');
                    return new commercetax.ErrorResponse(commercetax.resultcode.TaxEngineError, '503', NO_RESPONSE_MESSAGE);
                }
                String responseString = bodyOrNull(httpResponse);
                system.debug('Heap size used ' +Limits.getHeapSize());

                // The HTTP status is checked before the body: a response outside 2xx is an error whose
                // code is that status, never a success body, even when the body is empty. Its message is
                // a fixed sentence naming the status; the body, which may carry the engine's own error
                // text, goes to the debug log.
                Integer statusCode = httpResponse.getStatusCode();
                if(statusCode < 200 || statusCode > 299) {
                    debugEngineDetail('HTTP status ' + statusCode, responseString);
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
                    debugEngineDetail('response is not a JSON object', responseString);
                    return new commercetax.ErrorResponse(commercetax.resultcode.TaxEngineError, '502', UNREADABLE_RESPONSE_MESSAGE);
                }
                Object errorValue = ((Map<String, Object>) parsedBody).get('error');
                if(errorValue == null)
                {
                    commercetax.CalculateTaxResponse response = new commercetax.CalculateTaxResponse();
                    RLM_JsonSuccessParser jsonSuccessParserClass;
                    try {
                        jsonSuccessParserClass = RLM_JsonSuccessParser.parse(responseString);
                    } catch (JSONException e) {
                        debugEngineDetail('response does not fit the success parser: ' + e.getMessage());
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
                    // As for a non-2xx status above, the body with the engine's own text goes to the debug log.
                    debugEngineDetail('engine error', responseString);
                    return new commercetax.ErrorResponse(commercetax.resultcode.TaxEngineError, '501', ENGINE_ERROR_MESSAGE);
                }
            }else return null;
        }
        catch (Exception e) 
        {
            throw e; 
        }
    }
}