public with sharing class QuoteServiceResponse {
    public String errorMessage { get; private set; }
    public enum Status {
        SUCCESS,
        FAILURE
    }
    public ErrorCollector errorCollector { get; private set; }
    public Status status { get; private set; }

    public QuoteServiceResponse setErrorMessage(String message) {
        this.errorMessage = message;
        return this;
    }

    public QuoteServiceResponse setStatus(Status status) {
        this.status = status;
        return this;
    }

    private QuoteServiceResponse setErrorCollector(ErrorCollector errorCollector) {
        this.errorCollector = errorCollector;
        return this;
    }

    public QuoteServiceResponse createResponse(String message, Status status) {
        return new QuoteServiceResponse().setErrorMessage(message).setStatus(status);
    }

    public QuoteServiceResponse createErrorResponse(ErrorCollector errorCollector, Status status) {
        return new QuoteServiceResponse().setErrorCollector(errorCollector).setStatus(status);
    }

    public QuoteServiceResponse createSuccessResponse(Status status) {
        return new QuoteServiceResponse().setStatus(status);
    }
}
