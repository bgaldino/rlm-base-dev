// ============================================================================================= 
//  Object: HttpService
//  Company: Salesforce
//  Author: Ravi Shankar
//  Purpose: Http Generic Class 
public with sharing class RC_HttpService 
{   
    // Attribute to implement singleton pattern for Order Product Service class
    private static RC_HttpService httpServiceInstance;
    
    // VARIABLES
    
    private HttpResponse httpResponse;
    private Map<String,String> mapOfHeaderParameter = new Map<String,String>();
    private enum Method {GET, POST}
    
    /**
    * @name getInstance
    * @description get an Instance of Service class
    * @params NA
    * @return Http Service Class Instance
    */ 
    public static RC_HttpService getInstance() 
    {
        if (NULL == httpServiceInstance) 
        {
            httpServiceInstance =  new RC_HttpService();  
        }
        return httpServiceInstance;
    }
    
    /**
    * @name get
    * @description Get Method to get a HTTP request
    */    
    public void get(String endPoint) 
    {
        send(newRequest(Method.GET, endPoint));
    }
    
    /**
    * @name post
    * @description Post Method to Post a HTTP request
    */ 
    public void post(String path, String requestBody)
    {
       String endPoint = 'callout:commerce.tax.TaxTypedNamedCredential:test'+path;
        send(newRequest(Method.POST, endPoint, requestBody));
    }
    
    /**
    * @name addHeader
    * @description addHeader Methods to add all the defualt Header's required fo rthe request
    */
    public void addHeader(String name, String value)
    {
        mapOfHeaderParameter.put(name, value);
    }
    
    /**
    * @name setHeader
    * @description setHeader Methods to set setHeader for the request
    */
    private void setHeader(HttpRequest request) 
    {
        for(String headerValue : mapOfHeaderParameter.keySet())
        {
            request.setHeader(headerValue, mapOfHeaderParameter.get(headerValue));
        }
    }
    /**
    * @name newRequest
    * @description newRequest Methods to make a new request
    */
    private HttpRequest newRequest(Method method, String endPoint)
    {
        return newRequest(method, endPoint, NULL);
    }
    
    /**
    * @name newRequest
    * @description newRequest Methods to make a new request
    */
    private HttpRequest newRequest(Method method, String endPoint, String requestBody) 
    {
        HttpRequest request = new HttpRequest();
        request.setMethod(Method.name());
        setHeader(request);
        request.setEndpoint(endPoint);
        if (String.isNotBlank(requestBody)) 
        {
            request.setBody(requestBody);
        }   
        request.setTimeout(120000);
        return request;
    }
    
    /**
    * @name send
    * @description send Methods to send a request
    */
    private void send(HttpRequest request) 
    {
        try 
        {
            Http http = new Http();
            httpResponse = http.send(request);
        }
        catch(System.CalloutException e) 
        {
            system.debug('callout exception happened' + e.getMessage());
        }
        catch(Exception e) 
        {
            system.debug('callout did not happen' + e.getMessage());
        }
    }
    
    /**
    * @name getResponse
    * @description getResponse Method to get the Response
    */
    public HttpResponse getResponse()
    {
        return httpResponse;
    }
    
    /**
    * @name getResponseToString
    * @description getResponse Method to get the Responses
    */
    public String getResponseToString()
    {
        return getResponse().toString();
    }
}