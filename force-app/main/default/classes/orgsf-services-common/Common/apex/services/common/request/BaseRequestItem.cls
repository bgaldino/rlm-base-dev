public with sharing abstract class BaseRequestItem implements IRequestItem {
    private String requestItemId;

    public String getRequestItemId() {
        return this.requestItemId;
    }

    public void setRequestItemId(String requestItemId) {
        this.requestItemId = requestItemId;
    }
}