public class RLM_AmendmentRenewalDTO {

    @AuraEnabled public Decimal subtotal;
    @AuraEnabled public Decimal discount;
    @AuraEnabled public Decimal total;
    @AuraEnabled public String originalActionType;
    @AuraEnabled public Decimal renewalAmount;
    @AuraEnabled public Decimal expansionAmount;
    @AuraEnabled public Decimal attritionAmount;
    @AuraEnabled public Decimal netNewAddsAmount;
    @AuraEnabled public Decimal netChange;

    public RLM_AmendmentRenewalDTO(
        Decimal subtotal,
        Decimal discount,
        Decimal total,
        String originalActionType,
        Decimal renewalAmount,
        Decimal expansionAmount,
        Decimal attritionAmount,
        Decimal netNewAddsAmount,
        Decimal netChange
    ) {
        this.subtotal = subtotal;
        this.discount = discount;
        this.total = total;
        this.originalActionType = originalActionType;
        this.renewalAmount = renewalAmount;
        this.expansionAmount = expansionAmount;
        this.attritionAmount = attritionAmount;
        this.netNewAddsAmount = netNewAddsAmount;
        this.netChange = netChange;
    }
}
