public with sharing class QuoteAddressHelper {
    public static final List<String> VALID_ADDRESS_TYPES = new List<String>{ 'Delivery', 'Billing' };

    public static void populateResponseItems(QuoteAddressRequestItem addressRequestItem, Map<String, BaseResponseItem> responseItems) {
        if (String.isBlank(addressRequestItem.getRequestItemId())) {
            addressRequestItem.setRequestItemId(UUID.randomUUID().toString());
        }

        BaseResponseItem responseItem = new BaseResponseItem(addressRequestItem.getRequestItemId());
        responseItem.setSuccess(false);
        responseItems.put(addressRequestItem.getRequestItemId(), responseItem);
        validateRequest(addressRequestItem, responseItem);

    }

    public static void validateRequest(QuoteAddressRequestItem requestItem, BaseResponseItem responseItem) {
        if (String.isBlank(requestItem.quoteId)) {
            responseItem.addResponseMessage('Quote Id cannot be blank');
        }

        if (requestItem.accountAddress == null) {
            responseItem.addResponseMessage('Account Address cannot be null');
            responseItem.setSuccess(false);
            return;
        }

        if (requestItem.saveToAccount == true && String.isBlank(requestItem.accountAddress.name)) {
            responseItem.addResponseMessage('Name cannot be blank when also adding to the account.');
        }

        if (String.isBlank(requestItem.accountAddress.addressType)) {
            responseItem.addResponseMessage('Address Type cannot be blank');
        } else if (!VALID_ADDRESS_TYPES.contains(requestItem.accountAddress.addressType)) {
            responseItem.addResponseMessage('Address Type must be Delivery or Billing');
        }


        if (String.isBlank(requestItem.accountAddress.country)) {
            responseItem.addResponseMessage('Country cannot be blank');
        }

        responseItem.setSuccess(responseItem.getResponseMessages().size() == 0);
    }

    public static void mapQuoteObject(
        QuoteAddressRequestItem quoteAddressRequestItem,
        Map<Id, Quote> quoteMap,
        Map<Id, Set<String>> quoteIdToRequestItemIdMap
    ) {
        if (!quoteMap.containsKey(quoteAddressRequestItem.quoteId)) {
            Quote quote = new Quote(Id = quoteAddressRequestItem.quoteId);
            quoteMap.put(quote.Id, quote);
        }
        Quote quote = quoteMap.get(quoteAddressRequestItem.quoteId);

        if (!quoteIdToRequestItemIdMap.containsKey(quoteAddressRequestItem.quoteId)) {
            quoteIdToRequestItemIdMap.put(quote.Id, new Set<String>());
        }
        quoteIdToRequestItemIdMap.get(quote.Id).add(quoteAddressRequestItem.getRequestItemId());

        String addressPrefix = quoteAddressRequestItem.accountAddress.addressType == 'Billing' ? 'Billing' : 'Shipping';
        List<String> parameters = new List<String>{ addressPrefix };

        quote.put(String.format('{0}Street', parameters), quoteAddressRequestItem.accountAddress.street);
        quote.put(String.format('{0}City', parameters), quoteAddressRequestItem.accountAddress.city);
        quote.put(String.format('{0}State', parameters), quoteAddressRequestItem.accountAddress.state);
        quote.put(String.format('{0}PostalCode', parameters), quoteAddressRequestItem.accountAddress.postalCode);
        quote.put(String.format('{0}Country', parameters), quoteAddressRequestItem.accountAddress.country);
        quote.put(String.format('{0}Name', parameters), quoteAddressRequestItem.accountAddress.name);

        if (quoteAddressRequestItem.accountAddress.additionalFields != null && quoteAddressRequestItem.accountAddress.additionalFields.size() > 0) {
            quote.put(String.format('{0}AddressJSON__c', parameters), JSON.serialize(quoteAddressRequestItem.accountAddress.additionalFields, true));
        }
    }

    public static void mapSaveResults(
        List<Database.SaveResult> saveResults,
        Map<Id, Set<String>> quoteIdToRequestItemIdMap,
        Map<String, BaseResponseItem> responseItems
    ) {
        for (Database.SaveResult saveResult : saveResults) {
            for (String requestItemId : quoteIdToRequestItemIdMap.get(saveResult.getId())) {
                addDatabaseErrorsToResponse(responseItems.get(requestItemId), saveResult);
            }
        }
    }

    private static void addDatabaseErrorsToResponse(BaseResponseItem responseItem, Database.SaveResult saveResult) {
        responseItem.setSuccess(saveResult.isSuccess());

        for (Database.Error err : saveResult.getErrors()) {
            responseItem.addResponseMessage(
                String.format('{0}: {1}. Fields: {2}', new List<String>{ err.getStatusCode().toString(), err.getMessage(), err.getFields().toString() })
            );
        }
    }

    public static void mapAddressesToSaveToAccount(
        QuoteAddressRequestItem quoteAddressRequestItem,
        Map<Id, Set<QuoteAddressRequestItem>> addressesToSaveToAccountMap
    ) {
        if (!quoteAddressRequestItem.saveToAccount) {
            return;
        }

        if (!addressesToSaveToAccountMap.containsKey(quoteAddressRequestItem.quoteId)) {
            addressesToSaveToAccountMap.put(quoteAddressRequestItem.quoteId, new Set<QuoteAddressRequestItem>());
        }
        addressesToSaveToAccountMap.get(quoteAddressRequestItem.quoteId).add(quoteAddressRequestItem);
    }

    public static void populateAccountIdsOnRequests(List<Quote> quotes, Map<Id, Set<QuoteAddressRequestItem>> addressesToSaveToAccountMap) {
        for (Quote quote : quotes) {
            if (!addressesToSaveToAccountMap.containsKey(quote.Id)) {
                continue;
            }
            for (QuoteAddressRequestItem quoteAddressRequestItem : addressesToSaveToAccountMap.get(quote.Id)) {
                quoteAddressRequestItem.accountAddress.accountId = quote.Opportunity.AccountId;
            }
        }
    }

    public static IRequest createAccountLocationServiceRequest(IRequest originalRequest, Map<Id, Set<QuoteAddressRequestItem>> addressesToSaveToAccountMap) {
        BaseRequest request = new BaseRequest(originalRequest.getRequestId());

        for (Id quoteId : addressesToSaveToAccountMap.keySet()) {
            for (QuoteAddressRequestItem quoteAddressRequestItem : addressesToSaveToAccountMap.get(quoteId)) {
                CreateAcctLocationRequestItem acctLocationRequestItem = new CreateAcctLocationRequestItem();
                acctLocationRequestItem.setRequestItemId(quoteAddressRequestItem.getRequestItemId());
                acctLocationRequestItem.accountAddress = quoteAddressRequestItem.accountAddress;
                request.addRequestItem(acctLocationRequestItem);
            }
        }

        return request;
    }

    public static void processAccountLocationServiceResponse(IResponse acctLocationServiceResponse, Map<String, BaseResponseItem> responseItems) {
        //Apply overall error if there is one
        if (String.isNotBlank(acctLocationServiceResponse.getErrorMessage())) {
            for (BaseResponseItem responseItem : responseItems.values()) {
                responseItem.addResponseMessage(acctLocationServiceResponse.getErrorMessage());
            }
        }

        for (IResponseItem acctLocationServiceResponseItem : acctLocationServiceResponse.getResponseItems()) {
            if (!acctLocationServiceResponseItem.isSuccess() && responseItems.containsKey(acctLocationServiceResponseItem.getRequestItemId())) {
                List<String> responseMessages = acctLocationServiceResponseItem.getResponseMessages() != null
                    ? acctLocationServiceResponseItem.getResponseMessages()
                    : new List<String>();
                responseItems.get(acctLocationServiceResponseItem.getRequestItemId())
                    .addResponseMessage('Failed to create Associated Location for Account. Reasons:' + String.join(responseMessages, ', '));
            }
        }
    }
}
