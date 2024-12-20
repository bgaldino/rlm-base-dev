public with sharing virtual class BaseResponse implements IResponse {
    private String requestId;
    private List<IResponseItem> responseItems = new List<IResponseItem>();
    private String errorMessage;

    public BaseResponse() {
        this.requestId = null;
    }

    public BaseResponse(IRequest request) {
        this.requestId = request.getRequestId();
    }

    @AuraEnabled
    public String getRequestId() {
        return this.requestId;
    }

    public void addResponseItem(IResponseItem responseItem) {
        this.responseItems.add(responseItem);
    }

    public void addResponseItems(List<IResponseItem> responseItems) {
        this.responseItems.addAll(responseItems);
    }

    @AuraEnabled
    public List<IResponseItem> getResponseItems() {
        return this.responseItems;
    }

    public boolean isAllSuccess() {
        if (responseItems.isEmpty()) {
            return false;
        }
        for (IResponseItem responseItem : responseItems) {
            if (!responseItem.isSuccess()) {
                return false;
            }
        }
        return true;
    }

    @AuraEnabled
    public boolean getIsAllSuccess() {
        return this.isAllSuccess();
    }

    public boolean isAnySuccess() {
        for (IResponseItem responseItem : responseItems) {
            if (responseItem.isSuccess()) {
                return true;
            }
        }
        return false;
    }

    @AuraEnabled
    public boolean getIsAnySuccess() {
        return this.isAnySuccess();
    }

    @AuraEnabled
    public String getErrorMessage() {
        return this.errorMessage;
    }

    public void setErrorMessage(String errorMessage) {
        this.errorMessage = errorMessage;
    }
}
