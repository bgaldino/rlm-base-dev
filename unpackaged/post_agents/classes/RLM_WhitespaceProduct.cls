@JsonAccess(serializable='always' deserializable='always')
global with sharing class RLM_WhitespaceProduct {
    @AuraEnabled @InvocableVariable
    global String productId;

    @AuraEnabled @InvocableVariable
    global String productName;

    @AuraEnabled @InvocableVariable
    global String productFamily;

    @AuraEnabled @InvocableVariable
    global Integer adoptionCount;

    @AuraEnabled @InvocableVariable
    global Integer peerCount;

    @AuraEnabled @InvocableVariable
    global Integer adoptionPercent;

    public RLM_WhitespaceProduct() {}

    public RLM_WhitespaceProduct(Id prodId, String name, String family, Integer adoption, Integer peers) {
        this.productId = String.valueOf(prodId);
        this.productName = name;
        this.productFamily = family != null ? family : 'General';
        this.adoptionCount = adoption;
        this.peerCount = peers;
        this.adoptionPercent = peers > 0 ? Integer.valueOf((Decimal.valueOf(adoption) / peers * 100).setScale(0)) : 0;
    }
}
