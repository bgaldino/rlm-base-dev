@isTest
public class RLM_AI_ProductConfigTestDataFactory {
    public class QuoteFixture {
        public Id quoteId;
        public Id quoteLineItemId;
        public String productName;
    }

    public static QuoteFixture createQuoteFixture(String productName) {
        Account acct = new Account(Name = 'RLM AI Test Account');
        insert acct;

        Opportunity opp = new Opportunity(
            Name = 'RLM AI Test Opportunity',
            AccountId = acct.Id,
            StageName = 'Prospecting',
            CloseDate = Date.today().addDays(30)
        );
        insert opp;

        Id standardPbId = Test.getStandardPricebookId();

        Product2 product = new Product2(
            Name = productName,
            IsActive = true
        );
        insert product;

        PricebookEntry pbe = new PricebookEntry(
            Pricebook2Id = standardPbId,
            Product2Id = product.Id,
            UnitPrice = 100,
            IsActive = true
        );
        insert pbe;

        Quote q = new Quote(
            Name = 'RLM AI Test Quote',
            OpportunityId = opp.Id,
            Pricebook2Id = standardPbId,
            Status = 'Draft'
        );
        insert q;

        QuoteLineItem qli = new QuoteLineItem(
            QuoteId = q.Id,
            PricebookEntryId = pbe.Id,
            Quantity = 1,
            UnitPrice = 100
        );
        insert qli;

        QuoteFixture fixture = new QuoteFixture();
        fixture.quoteId = q.Id;
        fixture.quoteLineItemId = qli.Id;
        fixture.productName = product.Name;
        return fixture;
    }
}
