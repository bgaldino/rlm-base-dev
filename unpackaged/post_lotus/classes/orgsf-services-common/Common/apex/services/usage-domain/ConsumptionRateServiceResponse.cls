public with sharing class ConsumptionRateServiceResponse {

    public enum Status {
        SUCCESS,
        FAILURE
    }

    public String exceptionMessage { get; private set; }
    public ErrorCollector errorCollector { get; private set; }
    public Status status { get; private set; }
    public List<Object> consumptionRateRecords {get; private set;}

    @TestVisible
    private ConsumptionRateServiceResponse setExceptionMessage(String exceptionMessage) {
        this.exceptionMessage = exceptionMessage;
        return this;
    }

    @TestVisible
    private ConsumptionRateServiceResponse setStatus(Status status) {
        this.status = status;
        return this;
    }

    @TestVisible
    private ConsumptionRateServiceResponse setErrorCollector(ErrorCollector errorCollector) {
        this.errorCollector = errorCollector;
        return this;
    }

    @TestVisible
     private ConsumptionRateServiceResponse setConsumptionRateRecords (List<Object> consumptionRateRecords){
        this.consumptionRateRecords = consumptionRateRecords;
        return this;
    }

    public ConsumptionRateServiceResponse createExceptionResponse(String exceptionMessage, Status status) {
        return new ConsumptionRateServiceResponse().setExceptionMessage(exceptionMessage).setStatus(status);
    }

    public ConsumptionRateServiceResponse createErrorResponse(ErrorCollector errorCollector, Status status) {
        return new ConsumptionRateServiceResponse().setErrorCollector(errorCollector).setStatus(status);
    }

    public ConsumptionRateServiceResponse createSuccessResponse(Status status) {
        return new ConsumptionRateServiceResponse().setStatus(status);
    }

    public ConsumptionRateServiceResponse createSuccessResponse(Status status, List<Object> records){
        return new ConsumptionRateServiceResponse().setStatus(status).setConsumptionRateRecords(records);
    }
}
