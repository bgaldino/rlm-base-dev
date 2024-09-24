@RestResource(urlMapping='/QuantumBitTenantEnvironment/*')
global class RLM_TenantProvisioningAPI {
    
    @HttpGet
    global static RLM_ProvisioningResponse getTenantInfo(){
        RestRequest req = RestContext.request;
        String tenantId = req.RequestURI.substring(req.requestURI.lastIndexOf('/')+1);
        RLM_ProvisioningResponse provisioningInfo = new RLM_ProvisioningResponse();
        RLM_Tenant_Environment__c te = [SELECT Id, Name, Tenant_ID__c FROM RLM_Tenant_Environment__c WHERE Id =: tenantId LIMIT 1];
        provisioningInfo.tenantIdentifier = te.Tenant_ID__c;
        provisioningInfo.tenantProvisioningStatus = te.Status__c;

        return provisioningInfo;
    }

    @HttpPost
    global static String createNewTenant(String orderId){
        Order o = [SELECT Id, AccountId, Account.Name FROM Order WHERE Id =: orderId LIMIT 1];
        List<OrderItem> ois = [SELECT Id, OrderId, RLM_Tenant_Environment__c 
                                FROM OrderItem
                                WHERE (OrderId =: o.Id AND RLM_Tenant_Environment__c = null)];

        RLM_Tenant_Environment__c te = new RLM_Tenant_Environment__c();

        if(ois.size() > 0){
            
            te.RLM_Account__c = o.AccountId;
            te.Tenant_ID__c = String.valueOf(o.Account.Name) + String.valueOf(o.Id);
            te.Status__c = 'Awaiting Provisioning';

            database.insert(te);

            system.debug('Tenant Environment ' + te.Id + ' inserted');

        }

        return te.Id;
    }

    @HttpPatch
    global static void activateTenant(){
        RestRequest req = RestContext.request;
        String tenantId = req.RequestURI.substring(req.requestURI.lastIndexOf('/')+1);
        RLM_Tenant_Environment__c te = [SELECT Id, Name, Status__c 
                                        FROM RLM_Tenant_Environment__c 
                                        WHERE Id =: tenantId LIMIT 1];
        te.Status__c = 'Active';

        database.update(te);
    }


    global class RLM_ProvisioningResponse{
        public String tenantIdentifier;
        public String tenantProvisioningStatus;
    }

}