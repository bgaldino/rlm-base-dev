public with sharing class QuoteLineServiceResponse{
    public Enum Status {SUCCESS, FAILURE}
    public String exceptionMessage {get; private set;}
    public ErrorCollector errorCollector {get; private set;}
    public Status status {get; private set;}
    
    private QuoteLineServiceResponse setExceptionMessage (String exceptionMessage){
        this.exceptionMessage = exceptionMessage;
        return this;
    }
    
    private QuoteLineServiceResponse setStatus (Status status) {
        this.status = status;
        return this;
    }
    
    private QuoteLineServiceResponse setErrorCollector (ErrorCollector errorCollector) {
        this.errorCollector = errorCollector;
        return this;
    }
    
    public QuoteLineServiceResponse createExceptionResponse(String exceptionMessage, Status status){
       return new QuoteLineServiceResponse().setExceptionMessage(exceptionMessage).setStatus(status); 
    }
    
    public QuoteLineServiceResponse createErrorResponse(ErrorCollector errorCollector, Status status){
       return new QuoteLineServiceResponse().setErrorCollector(errorCollector).setStatus(status); 
    }
    
    public QuoteLineServiceResponse createSuccessResponse(Status status){
       return new QuoteLineServiceResponse().setStatus(status); 
    }
}