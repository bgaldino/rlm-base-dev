public with sharing class QuoteService extends AbstractQuoteService {
    private QuoteServiceRequestProcessor requestProcessor;
    private QuoteServiceRequestValidator requestValidator;
    private ErrorCollector errorCollector;
    private IQuoteDAO quoteDAO;
    private IQuoteBaseQuery quoteBaseQuery;
    private IAccountLocationService accountLocationService;

    public QuoteService() {
        this(
            new QuoteServiceRequestProcessor(),
            new QuoteServiceRequestValidator(),
            (IQuoteDAO) ServiceRegistry.getInstance('IQuoteDAO'),
            (IQuoteBaseQuery) ServiceRegistry.getInstance('IQuoteBaseQuery'),
            (IAccountLocationService) ServiceRegistry.getInstance('IAccountLocationService')
        );
    }

    public QuoteService(
        QuoteServiceRequestProcessor requestProcessor,
        QuoteServiceRequestValidator requestValidator,
        IQuoteDAO quoteDAO,
        IQuoteBaseQuery quoteBaseQuery,
        IAccountLocationService accountLocationService
    ) {
        this.requestProcessor = requestProcessor;
        this.requestValidator = requestValidator;
        this.quoteDAO = quoteDAO;
        this.quoteBaseQuery = quoteBaseQuery;
        this.accountLocationService = accountLocationService;
        this.errorCollector = new ErrorCollector();
    }

    public override QuoteServiceResponse updateQuote(QuoteServiceRequest request) {
        try {
            validateRequest(request);
            if (!getErrorCollector().hasError()) {
                requestProcessor.quoteUpdate(request);
            }
            return getServiceResponse();
        } catch (Exception ex) {
            return getExceptionResponse(ex);
        }
    }

    public override BaseResponse updateAddress(BaseRequest request) {
        BaseResponse response = new BaseResponse(request);

        Map<String, BaseResponseItem> responseItems = new Map<String, BaseResponseItem>();
        Map<Id, Quote> quotesToSave = new Map<Id, Quote>();
        Map<Id, Set<String>> quoteIdToRequestItemIdMap = new Map<Id, Set<String>>();
        Map<Id, Set<QuoteAddressRequestItem>> addressesToSaveToAccountMap = new Map<Id, Set<QuoteAddressRequestItem>>();

        for (IRequestItem requestItem : request.getRequestItems()) {
            QuoteAddressRequestItem addressRequestItem = (QuoteAddressRequestItem) requestItem;

            QuoteAddressHelper.populateResponseItems(addressRequestItem, responseItems);
            if (!responseItems.get(addressRequestItem.getRequestItemId()).isSuccess()) {
                continue;
            }
            QuoteAddressHelper.mapQuoteObject(addressRequestItem, quotesToSave, quoteIdToRequestItemIdMap);
            QuoteAddressHelper.mapAddressesToSaveToAccount(addressRequestItem, addressesToSaveToAccountMap);
        }

        if (quotesToSave.values() != null && quotesToSave.values().size() > 0) {
            List<Database.SaveResult> saveResult = this.quoteDAO.quoteUpdate(quotesToSave.values(), false);
            QuoteAddressHelper.mapSaveResults(saveResult, quoteIdToRequestItemIdMap, responseItems);
        }

        try {
            if (addressesToSaveToAccountMap.keySet().size() > 0) {
                List<Quote> quotes = this.quoteBaseQuery.getQuote(addressesToSaveToAccountMap.keySet());
                QuoteAddressHelper.populateAccountIdsOnRequests(quotes, addressesToSaveToAccountMap);
                IRequest accountLocationServiceRequest = QuoteAddressHelper.createAccountLocationServiceRequest(request, addressesToSaveToAccountMap);
                IResponse accountLocationServiceResponse = this.accountLocationService.associateLocations(accountLocationServiceRequest);
                QuoteAddressHelper.processAccountLocationServiceResponse(accountLocationServiceResponse, responseItems);
            }
        } catch (Exception e) {
            //Add the exception as a warning message to the response items, but don't fail it entirely.
            for (BaseResponseItem responseItem : responseItems.values()) {
                responseItem.addResponseMessage(e.getMessage());
            }
        }

        response.addResponseItems(responseItems.values());
        return response;
    }

    private void validateRequest(QuoteServiceRequest request) {
        this.requestValidator.validateRequest(request, getErrorCollector());
    }

    private QuoteServiceResponse getServiceResponse() {
        if (getErrorCollector().hasError()) {
            return new QuoteServiceResponse().createErrorResponse(getErrorCollector(), QuoteServiceResponse.Status.FAILURE);
        }
        return new QuoteServiceResponse().createSuccessResponse(QuoteServiceResponse.Status.SUCCESS);
    }

    private QuoteServiceResponse getExceptionResponse(Exception ex) {
        String errorMessage = 'Exception during Quote Service call :: ' + ex.getMessage();
        return new QuoteServiceResponse().createResponse(errorMessage, QuoteServiceResponse.Status.FAILURE);
    }

    public ErrorCollector getErrorCollector() {
        return this.errorCollector;
    }
}
