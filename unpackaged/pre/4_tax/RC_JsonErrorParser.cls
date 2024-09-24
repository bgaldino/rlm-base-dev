global with sharing class RC_JsonErrorParser
{
    public cls_error error;
    
    public class cls_error
    {
        public String code; 
        public String message;
        public String target;
        public cls_details[] details;
    }
    
    public class cls_details
    {
        public String code;
        public String message;
        public String description;
        public String faultCode;
        public String helpLink;
        public String severity;
    }
    public static RC_JsonErrorParser parse(String json)
    {
        return (RC_JsonErrorParser) System.JSON.deserialize(json, RC_JsonErrorParser.class);
    }
}