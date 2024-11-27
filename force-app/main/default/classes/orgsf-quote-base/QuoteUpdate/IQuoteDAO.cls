public interface IQuoteDAO {
    void quoteUpdate(List<Quote> request);
    List<Database.SaveResult> quoteUpdate(List<Quote> quotes, Boolean allorNone);
    List<Database.SaveResult> quoteInsert(List<Quote> request);
    List<Quote> getQuotesForSync(Set<Id> quoteIds);
    List<Quote> getAcceptedQuotesOnOppty(Id opptyId);
}
