public class RLM_SegmentSummaryDTO {

    @AuraEnabled public String rampId;
    @AuraEnabled public String segmentId;
    @AuraEnabled public String segmentLabel;
    @AuraEnabled public Decimal subtotal;
    @AuraEnabled public Decimal discount;
    @AuraEnabled public Decimal total;

    public RLM_SegmentSummaryDTO(
        String rampId,
        String segmentId,
        String segmentLabel,
        Decimal subtotal,
        Decimal discount,
        Decimal total
    ) {
        this.rampId = rampId;
        this.segmentId = segmentId;
        this.segmentLabel = segmentLabel;
        this.subtotal = subtotal;
        this.discount = discount;
        this.total = total;
    }
}
