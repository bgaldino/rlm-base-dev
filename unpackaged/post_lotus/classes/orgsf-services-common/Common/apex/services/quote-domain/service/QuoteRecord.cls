public class QuoteRecord {
    public Id quoteId { get; set; }
    public String importStatus { get; set; }
    public Datetime importCompletionDate { get; set; }
    public String rejectReason { get; set; }
    public String status { get; set; }
    public String substatus { get; set; }
    public Boolean hasProductRuleErrors { get; set; }
    public Date autoRollDate { get; set; }
}
