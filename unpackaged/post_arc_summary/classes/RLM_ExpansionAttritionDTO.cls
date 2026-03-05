public class RLM_ExpansionAttritionDTO {

    @AuraEnabled public String assetId;
    @AuraEnabled public String assetName;
    @AuraEnabled public Decimal previousAmount;
    @AuraEnabled public Decimal currentAmount;
    @AuraEnabled public Decimal changeAmount;
    @AuraEnabled public String changeType;
    @AuraEnabled public String assetActionType;

    public RLM_ExpansionAttritionDTO(
        String assetId,
        String assetName,
        Decimal previousAmount,
        Decimal currentAmount,
        Decimal changeAmount,
        String changeType,
        String assetActionType
    ) {
        this.assetId = assetId;
        this.assetName = assetName;
        this.previousAmount = previousAmount;
        this.currentAmount = currentAmount;
        this.changeAmount = changeAmount;
        this.changeType = changeType;
        this.assetActionType = assetActionType;
    }
}
