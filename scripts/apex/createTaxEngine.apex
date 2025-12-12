// Define the variables for the endpoint
String baseUrl = URL.getOrgDomainUrl().toExternalForm();
String apiVersion = 'v66.0'; // Update to the correct API version as needed

// Query for the ApexClass with the name 'RC_MockTaxAdapter'
ApexClass mockTaxAdapterClass = [SELECT Id, Name FROM ApexClass WHERE Name = 'RC_MockTaxAdapter' LIMIT 1];

// Query for the NamedCredential with the name 'RLM_MockTax'
NamedCredential namedCredential = [SELECT Id, DeveloperName FROM NamedCredential WHERE DeveloperName = 'RLM_MockTax' LIMIT 1];

// Check if the ApexClass and NamedCredential were found
if (mockTaxAdapterClass != null && namedCredential != null) {
    // Prepare the JSON payload for the TaxEngineProvider
    String taxEngineProviderPayload = JSON.serialize(new Map<String, Object>{
        'DeveloperName' => mockTaxAdapterClass.Name,
        'MasterLabel' => mockTaxAdapterClass.Name,
        'ApexAdapterId' => mockTaxAdapterClass.Id
    });
    
    // Create an HTTP request to create the TaxEngineProvider
    HttpRequest req = new HttpRequest();
    req.setEndpoint(baseUrl + '/services/data/' + apiVersion + '/sobjects/TaxEngineProvider/');
    req.setMethod('POST');
    req.setHeader('Authorization', 'Bearer ' + UserInfo.getSessionId());
    req.setHeader('Content-Type', 'application/json');
    req.setBody(taxEngineProviderPayload);
    
    // Send the request
    Http http = new Http();
    HttpResponse res = http.send(req);

    // Check the response status and handle errors if any
    if (res.getStatusCode() == 201) {
        // Successfully created the TaxEngineProvider
        Map<String, Object> responseBody = (Map<String, Object>)JSON.deserializeUntyped(res.getBody());
        String taxEngineProviderId = (String)responseBody.get('id');
        System.debug('Created TaxEngineProvider record with ID: ' + taxEngineProviderId);
        
        // Prepare the TaxEngine payload
        TaxEngine taxEngine = new TaxEngine();
        taxEngine.TaxEngineName = mockTaxAdapterClass.Name;
        taxEngine.MerchantCredentialId = namedCredential.Id;
        taxEngine.TaxEngineProviderId = taxEngineProviderId;
        taxEngine.SellerCode = 'Billing2';
        taxEngine.TaxEngineCity = 'San Francisco';
        taxEngine.TaxEngineCountry = 'United States';
        taxEngine.TaxEnginePostalCode = '94105';
        taxEngine.TaxEngineState = 'California';
        taxEngine.Status = 'Active';
        
        // Insert the TaxEngine record
        insert taxEngine;
        System.debug('Created TaxEngine record with ID: ' + taxEngine.Id);
        
    } else {
        // Log the error response
        System.debug('Failed to create TaxEngineProvider: ' + res.getBody());
    }
} else {
    if (mockTaxAdapterClass == null) {
        System.debug('ApexClass with the name "RC_MockTaxAdapter" not found.');
    }
    if (namedCredential == null) {
        System.debug('NamedCredential with the name "RLM_MockTax" not found.');
    }
}