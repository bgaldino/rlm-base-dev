global class RC_CalculateTaxService {
    // ============================================================================
    // CONSTANT 
    // ============================================================================
    private static final String AVALARA_ENDPOINT_URL_SANDBOX = 'https://sandbox-rest.avatax.com/api/v2';
    // Avalara Endpoint URL Production
    private static final String AVALARA_ENDPOINT_URL_PRODUCTION = 'https://rest.avatax.com/api/v2';
    private static final String TEST_REQUEST_BODY = '{  "id": -1,  "code": "00000131",  "companyId": -1,  "date": "2017-02-03T00:00:00",  "taxDate": "2017-02-03T00:00:00",  "status": "Temporary",  "type": "SalesOrder",  "reconciled": false,  "totalAmount": 4000,  "totalExempt": 0,  "totalTax": 290,  "totalTaxable": 4000,  "totalTaxCalculated": 290,  "adjustmentReason": "NotAdjusted",  "locked": false,  "version": 1,  "modifiedDate": "2017-02-03T12:18:18.7347388Z",  "modifiedUserId": 53894,  "lines": [    {      "id": -1,      "transactionId": -1,      "lineNumber": "80241000000jNDCAA2",      "discountAmount": 0,      "exemptAmount": 0,      "exemptCertId": 0,      "isItemTaxable": true,      "lineAmount": 1000,      "reportingDate": "2017-02-03T00:00:00",      "tax": 72.5,      "taxableAmount": 1000,      "taxCalculated": 72.5,      "taxCode": "P0000000",      "taxDate": "2017-02-03T00:00:00",      "taxIncluded": false,      "details": [        {          "id": -1,          "transactionLineId": -1,          "transactionId": -1,          "country": "US",          "region": "CA",          "exemptAmount": 0,          "jurisCode": "06",          "jurisName": "CALIFORNIA",          "stateAssignedNo": "",          "jurisType": "STA",          "nonTaxableAmount": 0,          "rate": 0.06,          "tax": 60,          "taxableAmount": 1000,          "taxType": "Sales",          "taxName": "CA STATE TAX",          "taxAuthorityTypeId": 45,          "taxCalculated": 60,          "rateType": "General"        },        {          "id": -1,          "transactionLineId": -1,          "transactionId": -1,          "country": "US",          "region": "CA",          "exemptAmount": 0,          "jurisCode": "075",          "jurisName": "SAN FRANCISCO",          "stateAssignedNo": "",          "jurisType": "CTY",          "nonTaxableAmount": 0,          "rate": 0.0025,          "tax": 2.5,          "taxableAmount": 1000,          "taxType": "Sales",          "taxName": "CA COUNTY TAX",          "taxAuthorityTypeId": 45,          "taxCalculated": 2.5,          "rateType": "General"        },        {          "id": -1,          "transactionLineId": -1,          "transactionId": -1,          "country": "US",          "region": "CA",          "exemptAmount": 0,          "jurisCode": "EMTV0",          "jurisName": "SAN FRANCISCO CO LOCAL TAX SL",          "stateAssignedNo": "38",          "jurisType": "STJ",          "nonTaxableAmount": 0,          "rate": 0.01,          "tax": 10,          "taxableAmount": 1000,          "taxType": "Sales",          "taxName": "CA SPECIAL TAX",          "taxAuthorityTypeId": 45,          "taxCalculated": 10,          "rateType": "General"        }      ]    }  ]}';
    
    private static String getTestResponseString(){
    
     List<String> jsonResponse = new List<String> {
                                    '"id": 0',
                                    '"code": "testDocCode1231245984"',
                                    '"companyId": 468039',
                                    '"date": "2020-07-15"',
                                    '"paymentDate": "2020-07-15"',
                                    '"status": "Temporary"',
                                    '"type": "SalesOrder"',
                                    '"customerVendorCode": "testDocCode1234"',
                                    '"customerCode": "testDocCode1234"',
                                    '"reconciled": false',
                                    '"totalAmount": 232',
                                    '"totalExempt": 0',
                                    '"totalDiscount": 0',
                                    '"totalTax": 23.43',
                                    '"totalTaxable": 232',
                                    '"totalTaxCalculated": 23.43',
                                    '"adjustmentReason": "NotAdjusted"',
                                    '"locked": false',
                                    '"version": 1',
                                    '"exchangeRateEffectiveDate": "2020-07-15"',
                                    '"exchangeRate": 1',
                                    '"modifiedDate": "2020-08-13T11:19:20.4836636Z"',
                                    '"modifiedUserId": 53894',
                                    '"taxDate": "2020-07-15T00:00:00"',
                                    '"lines": [{"id": 0,"transactionId": 0,"lineNumber": "1","discountAmount": 0,"exemptAmount": 0,"exemptCertId": 0,"isItemTaxable": true,"itemCode": "","lineAmount": 232,"quantity": 1,"reportingDate": "2020-07-15","tax": 23.43,"taxableAmount": 232,"taxCalculated": 23.43,"taxCode": "P0000000","taxCodeId": 8087,"taxDate": "2020-07-15","taxOverrideType": "None","taxOverrideAmount": 0,"taxIncluded": false,"details": [{"id": 0,"transactionLineId": 0,"transactionId": 0,"country": "US","region": "WA","exemptAmount": 0,"jurisCode": "53","jurisName": "WASHINGTON","stateAssignedNo": "","jurisType": "STA","jurisdictionType": "State","nonTaxableAmount": 0,"rate": 0.065,"tax": 15.08,"taxableAmount": 232,"taxType": "Sales","taxSubTypeId": "S","taxName": "WA STATE TAX","taxAuthorityTypeId": 45,"taxCalculated": 15.08,"rateType": "General","rateTypeCode": "G","unitOfBasis": "PerCurrencyUnit","isNonPassThru": false,"isFee": false},{"id": 0,"transactionLineId": 0,"transactionId": 0,"country": "US","region": "WA","exemptAmount": 0,"jurisCode": "033","jurisName": "KING","stateAssignedNo": "1700","jurisType": "CTY","jurisdictionType": "County","nonTaxableAmount": 0,"rate": 0,"tax": 0,"taxableAmount": 232,"taxType": "Sales","taxSubTypeId": "S","taxName": "WA COUNTY TAX","taxAuthorityTypeId": 45,"taxCalculated": 0,"rateType": "General","rateTypeCode": "G","unitOfBasis": "PerCurrencyUnit","isNonPassThru": false,"isFee": false}],"nonPassthroughDetails": [],"hsCode": "","costInsuranceFreight": 0,"vatCode": "","vatNumberTypeId": 0}]',
                                    '"addresses": [{"id": 0,"transactionId": 0,"boundaryLevel": "Address","line1": "255 S. King Street","line2": "","line3": "","city": "Seattle","region": "WA","postalCode": "98104","country": "US","taxRegionId": 2109700,"latitude": "47.59821","longitude": "-122.33108"}]',
                                    '"summary": [{"country": "US","region": "WA","jurisType": "State","jurisCode": "53","jurisName": "WASHINGTON","taxAuthorityType": 45,"stateAssignedNo": "","taxType": "Sales","taxSubType": "S","taxName": "WA STATE TAX","rateType": "General","taxable": 232,"rate": 0.065,"tax": 15.08,"taxCalculated": 15.08,"nonTaxable": 0,"exemption": 0},{"country": "US","region": "WA","jurisType": "County","jurisCode": "033","jurisName": "KING","taxAuthorityType": 45,"stateAssignedNo": "1700","taxType": "Sales","taxSubType": "S","taxName": "WA COUNTY TAX","rateType": "General","taxable": 232,"rate": 0,"tax": 0,"taxCalculated": 0,"nonTaxable": 0,"exemption": 0}]'
                                };
            return '{' + String.join(jsonResponse, ',') + '}';
        }
    
    public static commercetax.TaxEngineResponse getTax(commercetax.TaxEngineContext taxEngineContext) 
    { 
        commercetax.CalculateTaxRequest request = (commercetax.CalculateTaxRequest)taxEngineContext.getRequest();
        commercetax.calculatetaxtype requestType = request.taxtype;
        string referenceEntity = request.ReferenceEntityId;
        try{
            List<commercetax.TaxLineItemRequest> listOfLines = request.lineItems;
            if(!listOfLines.isEmpty()){
                RC_HttpService sendHttpRequest = new RC_HttpService();
                sendHttpRequest.addHeader('Content-type', 'application/json');
                String requestBody = RC_AvalaraJSONBuilder.getInstance().frameJsonForGetTaxOrderItem(request);
                sendHttpRequest.post('/transactions/create',requestBody);
                //system.debug('Request '+requestBody);
                String responseString = '';
                if(Test.isRunningTest()){
                    responseString = getTestResponseString();
                } else{
                    responseString = sendHttpRequest.getResponse().getBody();
                }
                //system.debug(sendHttpRequest.getResponse());
                //system.debug('response'+responseString);
                //responseString = TEST_REQUEST_BODY;
                system.debug('Heap size used ' +Limits.getHeapSize());
                
                if(!responseString.contains('error'))
                {
                    commercetax.CalculateTaxResponse response = new commercetax.CalculateTaxResponse();
                    RC_JsonSuccessParser jsonSuccessParserClass = RC_JsonSuccessParser.parse(responseString);
                    response.setTaxTransactionType(request.taxTransactionType);
                    response.setDocumentCode(jsonSuccessParserClass.code);
                    response.setReferenceDocumentCode(jsonSuccessParserClass.referenceCode);
                    if(jsonSuccessParserClass.status == 'Temporary')  {
                        response.setStatus(commercetax.TaxTransactionStatus.Uncommitted);
                    }
                    if(jsonSuccessParserClass.status == 'Committed') {
                        response.setStatus(commercetax.TaxTransactionStatus.Committed);
                    }
                    response.setTaxType(requestType);
                    commercetax.AmountDetailsResponse headerAmountResponse = new commercetax.AmountDetailsResponse();
                    headerAmountResponse.setTotalAmountWithTax(jsonSuccessParserClass.totalAmount + jsonSuccessParserClass.totaltax);
                    headerAmountResponse.setExemptAmount(jsonSuccessParserClass.totalExempt);
                    headerAmountResponse.setTotalAmount(jsonSuccessParserClass.totalAmount);
                    headerAmountResponse.setTaxAmount(jsonSuccessParserClass.totalTax);
                    response.setAmountDetails(headerAmountResponse);
                    response.setStatusDescription(jsonSuccessParserClass.adjustmentReason);
                    response.setEffectiveDate(date.valueof(jsonSuccessParserClass.taxDate));
                    response.setTransactionDate(date.valueof(jsonSuccessParserClass.transactionDate));
                    response.setReferenceEntityId(referenceEntity);
                    response.setTaxTransactionId(jsonSuccessParserClass.id);
                    response.setCurrencyIsoCode(request.currencyIsoCode);
                    List<commercetax.LineItemResponse> lineItemResponses = new List<commercetax.LineItemResponse>();
                    for(RC_JsonSuccessParser.Lines linesToProcess: jsonSuccessParserClass.lines)
                    {
                        commercetax.LineItemResponse lineItemResponse = new commercetax.LineItemResponse();
                        Double rateCalculated = 0.0;
                        List<commercetax.TaxDetailsResponse> taxDetailsResponses = new List<commercetax.TaxDetailsResponse>();
                        for(RC_JsonSuccessParser.details linesDetails : linesToProcess.details)
                        {
                            commercetax.TaxDetailsResponse taxDetailsResponse = new commercetax.TaxDetailsResponse();
                            if(linesDetails.exemptAmount != 0){
                                taxDetailsResponse.setExemptAmount(linesDetails.exemptAmount);
                                taxDetailsResponse.setExemptReason('Some reason we dont know');
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
                                    rateCalculated += linesDetails.rate; 
                                taxDetailsResponse.setRate(rateCalculated);
                                taxDetailsResponse.setTax(linesDetails.taxCalculated);
                                taxDetailsResponse.setTaxableAmount(linesDetails.taxableAmount);
                                taxDetailsResponse.setTaxAuthorityTypeId(String.valueOf(linesDetails.taxAuthorityTypeId));
                                taxDetailsResponse.setTaxId(linesDetails.id);
                                taxDetailsResponse.setTaxRegionId(linesDetails.region);
                                taxDetailsResponses.add(taxDetailsResponse);    
                            
                        }
                            lineItemResponse.setTaxes(taxDetailsResponses);
                            lineItemResponse.setEffectiveDate(date.valueof(linesToProcess.taxDate));
                            lineItemResponse.setIsTaxable(true);
                                commercetax.AmountDetailsResponse amountResponse = new commercetax.AmountDetailsResponse();
                                amountResponse.setTaxAmount(linesToProcess.taxCalculated);
                                amountResponse.setTotalAmount(linesToProcess.lineAmount);
                                amountResponse.setTotalAmountWithTax(linesToProcess.lineAmount+linesToProcess.taxCalculated);
                                amountResponse.setExemptAmount(linesToProcess.exemptAmount);
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
                    RC_JsonErrorParser jsonErrorParserClass = RC_JsonErrorParser.parse(responseString);
                    String message = null;
                    if(String.isNotBlank(jsonErrorParserClass.error.message))
                    {
                       message=jsonErrorParserClass.error.message;
                    }else{
                           String errorMessage = '';
                            for(RC_JsonErrorParser.cls_details messageString : jsonErrorParserClass.error.details)
                            {
                                if(String.isNotBlank(messageString.message) )
                                {
                                    errorMessage = messageString.message;
                                }
                            }
                            message = errorMessage; 
                        }
                     return new commercetax.ErrorResponse(commercetax.resultcode.TaxEngineError, '501', message);

                }
            }else return null;
        }
        catch (Exception e) 
        {
            throw e; 
        }
    }
}