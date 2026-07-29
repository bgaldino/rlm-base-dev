/**
 * Persists typed-name signature demo data on Contract.
 */
public with sharing class RLM_HomeServices_ContractSigningCtrl {
    @AuraEnabled
    public static void saveTypedSignature(Id contractId, String typedName) {
        if (contractId == null) {
            throw new AuraHandledException('Contract Id is required.');
        }
        if (String.isBlank(typedName)) {
            throw new AuraHandledException('Please type your name to sign.');
        }
        String trimmed = typedName.trim();
        if (trimmed.length() > 255) {
            throw new AuraHandledException('Signature text is too long.');
        }

        Contract c = new Contract(
            Id = contractId,
            RLM_HomeServices_TypedSignature__c = trimmed,
            RLM_HomeServices_SignedDateTime__c = System.now()
        );
        update c;
    }
}