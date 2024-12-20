public with sharing virtual class BaseResponseItem implements IResponseItem {
    private String requestItemId;
    private Boolean success;
    private List<String> responseMessages;

    public BaseResponseItem(String requestItemId) {
        this.responseMessages = new List<String>();
        this.requestItemId = requestItemId;
    }

    public void addResponseMessage(String responseMessage) {
        this.responseMessages.add(responseMessage);
    }

    @AuraEnabled
    public String getRequestItemId() {
        return this.requestItemId;
    }

    public void setSuccess(Boolean isSuccess) {
        this.success = isSuccess;
    }

    public Boolean isSuccess() {
        return this.success;
    }

    @AuraEnabled
    public Boolean getIsSuccess() {
        return this.success;
    }

    @AuraEnabled
    public List<String> getResponseMessages() {
        return this.responseMessages;
    }
}
