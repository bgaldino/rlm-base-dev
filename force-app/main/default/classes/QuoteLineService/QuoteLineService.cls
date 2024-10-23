public with sharing class QuoteLineService implements IQuoteLineService{
    
    private QuoteLineServiceRequestProcessor requestProcessor;
    private ErrorCollector errorCollector;
    IApprovalLevelService approvalLevelService;

    public QuoteLineService(){
        this(new QuoteLineServiceRequestProcessor());
    }
    
    public QuoteLineService(QuoteLineServiceRequestProcessor requestProcessor){
        this.requestProcessor = requestProcessor;
        this.errorCollector = new ErrorCollector();
        this.approvalLevelService = (IApprovalLevelService) ServiceRegistry.getInstance('IApprovalLevelService');
    }

    public QuoteLineServiceResponse createQuoteLines(QuoteLineServiceRequest request){
        try {
            validateRequest(request, DMLOperation.OP_INSERT);
            if(!getErrorCollector().hasError()){
                requestProcessor.insertLines(request);
                System.debug(request.quoteId);
            }
            return getServiceResponse();
        } catch(Exception ex){
            return getExceptionResponse(ex);
        }
    }
    
    public QuoteLineServiceResponse updateQuoteLines(QuoteLineServiceRequest request){
        try {
            validateRequest(request, DMLOperation.OP_UPDATE);
            if(!getErrorCollector().hasError()){
                requestProcessor.updateLines(request);
            }
            return getServiceResponse();
        } catch(Exception ex){
            return getExceptionResponse(ex);
        }
    }
    
    public QuoteLineServiceResponse deleteQuoteLines(QuoteLineServiceRequest request){
        try {
            validateRequest(request, DMLOperation.OP_DELETE);
            if(!getErrorCollector().hasError()){
                requestProcessor.deleteLines(request);
            }
            return getServiceResponse();
        } catch(Exception ex){
            return getExceptionResponse(ex);
        }
    }
    
    private void validateRequest(QuoteLineServiceRequest request, DMLOperation op){
        new QuoteLineServiceRequestValidator().validateRequest(request, op, getErrorCollector());
    }
    
    private QuoteLineServiceResponse getServiceResponse(){
        if(getErrorCollector().hasError()){
            return new QuoteLineServiceResponse().createErrorResponse(getErrorCollector(), QuoteLineServiceResponse.Status.FAILURE);
        }
        return new QuoteLineServiceResponse().createSuccessResponse(QuoteLineServiceResponse.Status.SUCCESS);
    }
    
    private QuoteLineServiceResponse getExceptionResponse(Exception ex){
       String exceptionMessage = 'Exception during Quote Line Service call :: ' + ex.getMessage();
       return new QuoteLineServiceResponse().createExceptionResponse(exceptionMessage, QuoteLineServiceResponse.Status.FAILURE);
    }
    
    public ErrorCollector getErrorCollector(){
        return this.errorCollector;
    }
}