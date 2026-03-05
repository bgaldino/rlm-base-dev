public class RLM_QuoteSummaryDTO {

    @AuraEnabled public Decimal subtotal;
    @AuraEnabled public Decimal discount;
    @AuraEnabled public Decimal total;

    public RLM_QuoteSummaryDTO(
        Decimal subtotal,
        Decimal discount,
        Decimal total
    ) {
        this.subtotal = subtotal;
        this.discount = discount;
        this.total = total;
    }
}
