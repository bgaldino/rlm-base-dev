public class QuoteLine {
    public String quoteLineId;
    public Id quoteId;
    public Id product2Id;
    public Id pricebookEntryId;
    public Integer quantity;
    public String billingFrequency;
    public Decimal unitPrice;
    public Date startDate;
    public Integer subscriptionTerm;
    public Decimal discount;
    public Integer approvalLevel;
    public Id tenantId;
    public Id basedOnId;
    public Integer sortOrder;
    public String approvalMatrix;
    public Integer effectiveQuantity;
    public Double effectiveDiscount;

    public QuoteLine() {}

    public QuoteLine(QuoteLineItem qli) {
        this.quoteLineId = qli.Id;
        this.quoteId = qli.QuoteId;
        this.product2Id = qli.Product2Id;
        this.pricebookEntryId = qli.PricebookEntryId;
        this.quantity = Integer.valueOf(qli.Quantity);
        this.billingFrequency = qli.BillingFrequency;
        this.unitPrice = qli.UnitPrice;
        this.startDate = qli.StartDate;
        this.subscriptionTerm = qli.SubscriptionTerm;
        this.discount = qli.Discount;
        this.tenantId = qli.Tenant__c;
        this.basedOnId = qli.Product2.BasedOnId;
        this.approvalLevel = Integer.valueOf(qli.ApprovalLevel__c);
        this.sortOrder = Integer.valueOf(qli.SortOrder);
        this.approvalMatrix = qli.Product2.ApprovalMatrix__c;
        this.effectiveQuantity = Integer.valueOf(qli.EffectiveQuantity__c);
        this.effectiveDiscount = qli.EffectiveDiscount__c;
    }
}