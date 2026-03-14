global with sharing class RLM_JsonErrorParser
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
    public static RLM_JsonErrorParser parse(String json)
    {
        return (RLM_JsonErrorParser) System.JSON.deserialize(json, RLM_JsonErrorParser.class);
    }
}