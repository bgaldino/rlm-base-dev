public with sharing class InvocableGetFieldNamesByObject {
   @InvocableMethod (label='RCA Describe Fields' description='Receive Object API Name, Return List of Fields' category='CustomRCA')
   public static List<ApiResponse> createHeadlessBody(List<ApiRequest> reqs) { 
        List<ApiResponse> resps = new List<ApiResponse>();
        ApiResponse resp = new ApiResponse();
        resp.fieldNames = new List<Account>();

        for (ApiRequest r : reqs) {
            // Describe the object to get its fields
            Map<String, Schema.SObjectType> globalDescribe = Schema.getGlobalDescribe();
            
            if (!globalDescribe.containsKey(r.objectName)) {
                resp.status = 404;
                throw new IllegalArgumentException('Invalid object name: ' + r.objectName);
            }

            Schema.SObjectType objType = globalDescribe.get(r.objectName);
            Schema.DescribeSObjectResult describeResult = objType.getDescribe();

            // Get all field names
            Map<String, Schema.SObjectField> fieldsMap = describeResult.fields.getMap();
            List<String> fieldNames = new List<String>();
            

            for(SObjectField field:fieldsMap.values()){
                String name = field.getDescribe().getName();
                fieldNames.add(name);
             }

             fieldNames.sort(); // Alphabetical sort

            for (String fieldName : fieldNames) {
                Schema.DescribeFieldResult fieldDesc = fieldsMap.get(fieldName).getDescribe();
                Account acc = new Account();
                acc.Name = fieldName;
                acc.Description = fieldDesc.getType().name(); 
                resp.fieldNames.add(acc);
            }
            resp.status = 200;
    }
    resps.add(resp);
    return resps;
    
    }

    public class ApiResponse {
        @InvocableVariable(label='Result')
        public Integer status;
        @InvocableVariable(label='Field Names')
        public List<Account> fieldNames;
    }

    public class ApiRequest {
        @InvocableVariable(label='Object Name')
        public String objectName;
    }
}
