public interface IResponse {
    String getRequestId();

    void addResponseItem(IResponseItem responseItem);
    List<IResponseItem> getResponseItems();

    boolean isAllSuccess();
    boolean isAnySuccess();

    String getErrorMessage();
    void setErrorMessage(String errorMessage);
}