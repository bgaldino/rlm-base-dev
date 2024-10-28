public with sharing virtual class BaseRequest implements IRequest {
    private String requestId;
    private List<IRequestItem> requestItems = new List<IRequestItem>();

    public BaseRequest() {
        this.requestId = UUID.randomUUID().toString();
    }

    public BaseRequest(String requestId) {
        this.requestId = requestId;
    }

    public String getRequestId() {
        return this.requestId;
    }

    public void addRequestItem(IRequestItem requestItem) {
        this.requestItems.add(requestItem);
    }

    public void addRequestItems(List<IRequestItem> requestItems) {
        this.requestItems.addAll(requestItems);
    }

    public List<IRequestItem> getRequestItems() {
        return this.requestItems;
    }
}
