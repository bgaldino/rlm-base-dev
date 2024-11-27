public interface IRequest {
    String getRequestId();

    void addRequestItem(IRequestItem requestItem);
    List<IRequestItem> getRequestItems();
}