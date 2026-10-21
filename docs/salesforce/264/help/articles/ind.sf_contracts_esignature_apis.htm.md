---
article_id: ind.sf_contracts_esignature_apis.htm
title: E-Signature APIs
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_esignature_apis.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_na_1.htm
fetched_at: 2026-10-13
---

# E-Signature APIs

You can use the e-signature APIs independently to call the Salesforce Contracts functionalities without using the UI. These APIs are highly customizable. You can send one or more generated documents for e-signature. Your generated documents can be associated with either standard or custom objects.

To know about the required permissions, refer to Permission Sets For DocuSign.

To know about the Apex governor limits, refer to Execution Governors and Limits.

For information on e-signature API's, see E-signature Resources.

METHOD	DESCRIPTION
getRecipients	

Use this method to view a list of document recipients.

To add a custom logic via a custom class:

Create a global Apex class that implements ind_docgen_api.OpenInterface.

Add your logic inside the invokeMethod() method.

Add the class to your org.

Call the API using the customClass parameter in the URL. Example:

/connect/e-sign/recipients?sourceObjectId=<sourceObjectId>&recipientSelector=<recipientCustomClassName>

To customize how recipients are returned, implement the ind_docgen_api.OpenInterface interface in a global Apex class. Here’s a sample implementation that fetches all Contacts with the salutation "Mr.":

public class GetEsignRecipients implements ind_docgen_api.OpenInterface {

    private static final String ERROR_UNSUPPORTED = 'Unsupported method. Only method [getRecipients] is supported.';
    private static final String ERROR_NO_RECIPIENTS = 'Recipient data not found';

    public Boolean invokeMethod(String methodName, Map<String, Object> inputMap, Map<String, Object> outMap) {
        system.debug(inputMap);
        Boolean success;

        if (methodName == 'getRecipients') {
            success = getRecipients(inputMap, outMap);
        }  else {
            throw new CustomGetRecipientsException(ERROR_UNSUPPORTED);
        }

        System.debug('invokeMethod:outMap -> ' + outMap);
        System.debug('invokeMethod:success -> ' + success);
        return success;
    }

    private Boolean getRecipients(Map<String, Object> input, Map<String, Object> output) {
        Boolean success = false;

        Id sourceObjectId = (Id) input.get('sourceObjectId');
        
        List<Map<String, Object>> recipients = new List<Map<String, Object>>();
        
        Map<String, Object> recipient = new Map<String, Object>();
        recipient.put('name', 'John Peter');
        recipient.put('email', 'johnxxxx@gmail.com');
        recipient.put('id', '1');
        
        Map<String, Object> additionalFields = new Map<String, Object>();
        additionalFields.put('routingOrder', '1');
        additionalFields.put('routingNumber', '1');
        additionalFields.put('signerRole', '1');
        additionalFields.put('recipientType','Signer'); // Case Sensitive
        additionalFields.put('recipientLocale','English (U.S.)');
        //We need to send recipientLocale as same as What we see in the Salesforce UI While Manually Adding Recipient Locale 
        recipient.put('additionalFields', additionalFields);
        recipients.add(recipient);    
             
        output.put('recipients', recipients);
        
        success = true;
        System.debug('getRecipients:output -> ' + output);
        System.debug('getRecipients:success -> ' + success);
        
        return success;

    }
    
    class CustomGetRecipientsException extends Exception {

    }
}

recipientSelector and sourceObjectId are optional parameters. The sourceObjectId parameter is passed as input to the apex class and consumed as required.

To configure the custom class using metadata, add a record in the Electronic Signature Configuration object with these values:

Vendor: Docusign

Group Type: Group Type

Config Type: Recipients Custom class

Config Value: Your custom class name. >.


getDocuments	

Use this method to view a list of documents sent for e-signature.

If the IsAssociatedWithClm parameter is:

true – the API fetches contract documents.

false – the API fetches documents only from Notes and Attachments.

To add a custom logic via a custom class:

Create a global Apex class that implements ind_docgen_api.OpenInterface.

Add your logic inside the invokeMethod() method.

Add the class to your org.

Call the API using the customClass parameter in the URL. Example:

/connect/e-sign/documents?sourceObjectId=<sourceObjectId>&documentSelector=<customClassName>

To customize how documents are returned for eSignature, implement the ind_docgen_api.OpenInterface interface in a global Apex class. Here’s an example implementation that fetches documents from ContentVersion records linked to the given sourceObjectId:

public class GetEsignDocuments implements ind_docgen_api.OpenInterface {
    private static final String ERROR_UNSUPPORTED = 'Unsupported method. Only method [getDocuments] is supported.';

    public Boolean invokeMethod(String methodName, Map<String, Object> request, Map<String, Object> outMap) {
        Boolean success = true;
        if (methodName == 'getDocuments') {
            success = executeAction(request, outMap);
        } else {
             throw new CustomGetDocumentsException(ERROR_UNSUPPORTED);
         }
        return success;
    }

    private Boolean executeAction(Map<String, Object> inputMap, Map<String, Object> outMap) {
        Boolean success = false;
        System.debug('getDocuments:inputMap -> ' + inputMap);
        Id contractId = (Id)inputMap.get('sourceObjectId');
        
        // Fetch contract master document
        ContentDocument contentDocument = getMasterContractDocument(contractId);
        
        List<Map<String, Object>> documents = new List<Map<String, Object>>();
        Map<String, Object> document = new Map<String, Object>();
        document.put('fileExtension', contentDocument.FileExtension);
        document.put('name',contentDocument.Title);
        String contentVersionId = Id.valueOf(contentDocument.LatestPublishedVersionId);
        document.put('sourceId', contentVersionId);
        document.put('sourceType','Content');
        
        Map<String, String> additionalFields = new Map<String, String>();
        additionalFields.put('documentId', '1');
        document.put('additionalFields', additionalFields);
        documents.add(document);
        outMap.put('documents', documents);

        success = true;
        System.debug('getDocuments:outMap -> ' + outMap);
        System.debug('getDocuments:success -> ' + success);
        return success;
    }
    
    private ContentDocument getMasterContractDocument(Id contractId) {
        // Fetch latest contract document version
        ContractDocumentVersion latestCdv = [SELECT Id FROM ContractDocumentVersion WHERE contractId=:contractId ORDER BY VersionNumber DESC LIMIT 1];
        
        // Fetch latest contendocumentId associated with latest contract document version
        ContractDocVerContentDoc contractDoc = [SELECT ContentDocumentId FROM ContractDocVerContentDoc WHERE ContractDocumentVersionId=:latestCdv.Id LIMIT 1];
        
        // Load content document details
        ContentDocument contentDocument = [SELECT FileExtension, FileType, Id, LatestPublishedVersionId, Title FROM ContentDocument WHERE Id=:contractDoc.ContentDocumentId LIMIT 1];
        return contentDocument;    
    }

    class CustomGetDocumentsException extends Exception {

    }
}

documentSelector is an optional parameter.

To configure the custom class using metadata, add a record in the Electronic Signature Configuration object with these values:

Vendor: Docusign

Group Type: Group Type

Config Type: Documents Custom class

Config Value: Your custom class name.

You don't need to pass the custom class name in the API URL.


getNotificationSettings	

Use this method to view reminder and expiration notification settings. The sourceObjectId is a mandatory parameter that returns the respective notification settings for an object.

The API reads the notification settings from these configuration settings:

If only the DocGen permissions are enabled, the API reads the notification settings from the Electronic Signature Envelope Config setting.

If both the DocGen and CLM (Salesforce Contracts) permissions are enabled, and the object type is contract, then API reads the notification settings from the Contract Type Config settings.

If both the DocGen and CLM (Salesforce Contracts) permissions are enabled, and the object type is not contract, the API reads the notification settings from the Electronic Signature Envelope Config settings.


sendEnvelope	Use this method to enable a new DocuSign transaction.
voidEnvelope	Use this method to expire or void envelopes associated with an object.
updateEnvelope	Use this method to send an ad hoc request to DocuSign to update the envelope status.
