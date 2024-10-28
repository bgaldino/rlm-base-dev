public Interface IResponseItem {
    String getRequestItemId();

    void setSuccess(Boolean isSuccess);
    Boolean isSuccess();

    List<String> getResponseMessages();
    void addResponseMessage(String responseMessage);
}