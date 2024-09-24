global virtual class RC_MockTaxAdapter implements commercetax.TaxEngineAdapter {

    global commercetax.TaxEngineResponse processRequest(commercetax.TaxEngineContext taxEngineContext) {
        commercetax.RequestType requestType = taxEngineContext.getRequestType();
        commercetax.CalculateTaxRequest request = (commercetax.CalculateTaxRequest)taxEngineContext.getRequest();
        if(request.documentCode == null) {
            return new commercetax.ErrorResponse(commercetax.resultcode.TaxEngineError, '404', 'documentCode  is mandatory');
        }
        if(request.documentCode == 'TaxEngineError') {
            return new commercetax.ErrorResponse(commercetax.resultcode.TaxEngineError, '504', 'documentCode  - not supported');
        }
        if(request.documentCode == 'simulateUnhandledExceptionInAdapter') {
            Integer foo = 5/0 ;
        }
        if(request.documentCode == 'simulateValidationFailureInAdapter') {
            return new commercetax.ErrorResponse(commercetax.resultcode.TaxEngineError, '400', 'validations for documentCode failed in adapter');
        }
        if(request.documentCode == 'simulateMalformedErrorInAdapter') {
                    return new commercetax.ErrorResponse(commercetax.resultcode.TaxEngineError, null, 'malformed adapter error response');
        }
        if(request.documentCode == 'simulateTaxEngineProcessFailure') {
            return new commercetax.ErrorResponse(commercetax.resultcode.TaxEngineError, '500', 'Tax Engine couldnt process your request');
        }

        if(requestType == commercetax.RequestType.CalculateTax){
            commercetax.calculatetaxtype type = request.taxtype;
            String docCode='';
            if(request.DocumentCode == 'simulateEmptyDocumentCode')
                docCode = '';
            else if(request.DocumentCode != null)
                docCode =request.DocumentCode;             
            else if(request.ReferenceEntityId != null) docCode = request.ReferenceEntityId;
            else docCode =  String.valueOf(getRandomInteger(0,2147483647));
            commercetax.CalculateTaxResponse response = new commercetax.CalculateTaxResponse();
            if(request.isCommit == true) {
                response.setStatus(commercetax.TaxTransactionStatus.Committed);
            } else {
                response.setStatus(commercetax.TaxTransactionStatus.Uncommitted);
            }
            response.setDocumentCode(docCode);
            response.setReferenceDocumentCode(request.referenceDocumentCode);
            response.setTaxType(type);
            response.setStatusDescription('statusDescription');
            if(request.sellerDetails.code == 'testSellerCode') {
                response.setDescription('SellerCode fetched from TaxEngine entity');
            }
            else {
                response.setDescription('description');
            }
           response.setEffectiveDate(system.now());
           if(request.transactionDate == null) {
              response.setTransactionDate(system.now());
           } else {
              response.setTransactionDate(request.transactionDate);
           }
           if(request.taxTransactionType == null) {
               response.setTaxTransactionType(commercetax.TaxTransactionType.Debit);
           } else {
               response.setTaxTransactionType(request.taxTransactionType);
           }

            if(request.currencyIsoCode == null || request.currencyIsoCode == '') {
               response.setCurrencyIsoCode('USD');
            } else {
               response.setCurrencyIsoCode(request.currencyIsoCode);
            }
            response.setReferenceEntityId(request.ReferenceEntityId);
            Double totalTax = 0.0;
            Double totalAmount = 0.0;
            List<commercetax.LineItemResponse> lineItemResponses = new List<commercetax.LineItemResponse>();
            for(Commercetax.TaxLineItemRequest lineItem : request.lineItems){
                commercetax.AddressesResponse addressesRes = new commercetax.AddressesResponse();
                if(request.DocumentCode == 'SetsNullForResponseWithoutException'){
	                addressesRes.setShipFrom(null);
	                addressesRes.setShipTO(null);
	                addressesRes.setSoldTo(null);
                }else{
	                commercetax.AddressResponse addRes = new commercetax.AddressResponse();
	                addRes.setLocationCode('locationCode');
	                addressesRes.setShipFrom(addRes);
	                addressesRes.setShipTO(addRes);
	                addressesRes.setSoldTo(addRes);
                }
                commercetax.LineItemResponse lineItemResponse = new commercetax.LineItemResponse();
                Double totalLineTax = 0;
                List<commercetax.TaxDetailsResponse> taxDetailsResponses = new List<commercetax.TaxDetailsResponse>();
                for(integer i =0;i<1;i++){
                    Double rate  = 0.1;
                    Double taxableAmount = lineItem.amount;
                    commercetax.TaxDetailsResponse taxDetailsResponse = new commercetax.TaxDetailsResponse();
                    taxDetailsResponse.setRate(rate);
                    taxDetailsResponse.setTaxableAmount(taxableAmount);
                    Double tax = taxableAmount*rate;
                    totalLineTax+=tax;
                    taxDetailsResponse.setTax(taxableAmount*rate);
                    taxDetailsResponse.setExemptAmount(0);
                    taxDetailsResponse.setExemptReason('exemptReason');
                    taxDetailsResponse.setTaxRegionId('taxRegionId');
                    taxDetailsResponse.setTaxId(String.valueOf(getRandomInteger(0,2323233)));
                    taxDetailsResponse.setSerCode('serCode');
                    taxDetailsResponse.setTaxAuthorityTypeId('taxAuthorityTypeId');
                    if(request.DocumentCode == 'SetsNullForResponseWithoutException'){
						taxDetailsResponse.setImposition(null);	
	            	}else{
	                    commercetax.ImpositionResponse imposition = new commercetax.ImpositionResponse();
                        imposition.setSubType('subtype');
                        imposition.setType('type');
						taxDetailsResponse.setImposition(imposition);	            	
					}
	            	
                    if(request.DocumentCode == 'SetsNullForResponseWithoutException'){
	                	taxDetailsResponse.setJurisdiction(null);
	            	}else{
		            	commercetax.JurisdictionResponse jurisdiction = new commercetax.JurisdictionResponse();
                        jurisdiction.setCountry('country');
                        jurisdiction.setRegion('region');
                        jurisdiction.setName('name');
                        jurisdiction.setStateAssignedNumber('stateAssignedNo');
                        jurisdiction.setId('id');
                        jurisdiction.setLevel('level');
                        taxDetailsResponse.setJurisdiction(jurisdiction);
	            	}
            	
                    taxDetailsResponses.add(taxDetailsResponse);
                }
                lineItemResponse.setTaxes(taxDetailsResponses);
                totalTax +=totalLineTax;
                totalAmount+=lineItem.amount;
                
                if(request.DocumentCode == 'SetsNullForResponseWithException'){
	                lineItemResponse.setAmountDetails(null);
            	}else{
	                commercetax.AmountDetailsResponse amountResponse = new commercetax.AmountDetailsResponse();
	                amountResponse.setTotalAmountWithTax(totalTax+totalAmount);
	                amountResponse.setExemptAmount(0);
	                amountResponse.setTotalAmount(totalAmount);
	                amountResponse.setTaxAmount(totalTax);
	                lineItemResponse.setAmountDetails(amountResponse);
	            }
                lineItemResponse.setEffectiveDate(system.now());
                lineItemResponse.setTaxCode(lineItem.taxCode);
                lineItemResponse.setProductCode(lineItem.ProductCode);
                lineItemResponse.setLineNumber(lineItem.linenumber);
                lineItemResponse.setIsTaxable(true);
                lineItemResponse.setQuantity(lineItem.quantity);
                if(request.DocumentCode == 'SetsNullForResponseWithoutException'){
					lineItemResponse.setAddresses(null);
            	}else{
            		lineItemResponse.setAddresses(addressesRes);
                }
            	lineItemResponses.add(lineItemResponse);
            }
			if(request.DocumentCode == 'SetsNullForResponseWithException'){
				lineItemResponses.add(null);
            }
	        if(request.documentCode == 'nolines') {
	            // logic to skip adding lines to response
	        } else {
	                response.setLineItems(lineItemResponses);
	        }
            if(request.DocumentCode == 'SetsNullForResponseWithException'){
            	response.setAmountDetails(null);
            }else{
            	commercetax.AmountDetailsResponse headerAmountResponse = new commercetax.AmountDetailsResponse();
                headerAmountResponse.setTotalAmountWithTax(totalTax+totalAmount);
                headerAmountResponse.setExemptAmount(0);
                headerAmountResponse.setTotalAmount(totalAmount);
                headerAmountResponse.setTaxAmount(totalTax);
                response.setAmountDetails(headerAmountResponse);
	            }
            commercetax.AddressesResponse addressesRes = new commercetax.AddressesResponse();
            commercetax.AddressResponse addRes = new commercetax.AddressResponse();
            addRes.setLocationCode('locationCode');
            addressesRes.setShipFrom(addRes);
            addRes.setLocationCode('locationCode');
            addressesRes.setShipTO(addRes);
            addRes.setLocationCode('locationCode');
            addressesRes.setSoldTo(addRes);
            response.setAddresses(addressesRes);
            return response;

        }
        else
            return null;
    }

    public static Integer getRandomInteger(Integer min, Integer max)
    {
        return min + (Integer.valueOf(Math.random()) * (max - min));
    }
}
