public class PlaceQuoteServiceResponse {

    public Id quoteId;
    public String requestIdentifier;
    public List<ResponseError> responseError;
    public String statusURL;
    public Boolean success;
    
    public class ResponseError {
        public String errorCode;
        public String message;
        public String referenceId;
    }
}
