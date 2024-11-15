public interface IQuoteLineService{
    QuoteLineServiceResponse createQuoteLines (QuoteLineServiceRequest request);
    QuoteLineServiceResponse updateQuoteLines (QuoteLineServiceRequest request);
    QuoteLineServiceResponse deleteQuoteLines (QuoteLineServiceRequest request);
}