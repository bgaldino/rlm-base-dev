@IsTest
private class RLM_HomeServices_ProductImagesTest {
  private static Map<String, Id> createScenario() {
    Account account = new Account(Name = 'Product Image Test Account');
    insert account;

    Id standardPricebookId = Test.getStandardPricebookId();
    Product2 product = new Product2(
      Name = 'Product Image Test Service',
      ProductCode = 'HS-IMAGE-TEST',
      IsActive = true,
      DisplayUrl = '/resource/HS_IMAGE_TEST',
      RLM_HomeServices_DisplayInSelfService__c = true
    );
    insert product;

    PricebookEntry pricebookEntry = new PricebookEntry(
      Pricebook2Id = standardPricebookId,
      Product2Id = product.Id,
      UnitPrice = 125,
      IsActive = true
    );
    insert pricebookEntry;

    Opportunity opportunity = new Opportunity(
      Name = 'Product Image Test Opportunity',
      AccountId = account.Id,
      StageName = 'Prospecting',
      CloseDate = Date.today().addMonths(1),
      Amount = 125,
      Pricebook2Id = standardPricebookId
    );
    insert opportunity;

    Quote quote = new Quote(
      Name = 'Product Image Test Quote',
      OpportunityId = opportunity.Id,
      Pricebook2Id = standardPricebookId,
      Status = 'Draft'
    );
    insert quote;

    QuoteLineItem lineItem = new QuoteLineItem(
      QuoteId = quote.Id,
      PricebookEntryId = pricebookEntry.Id,
      Product2Id = product.Id,
      Quantity = 1,
      UnitPrice = 125
    );
    insert lineItem;

    return new Map<String, Id>{
      'account' => account.Id,
      'lineItem' => lineItem.Id,
      'pricebook' => standardPricebookId,
      'product' => product.Id
    };
  }

  @IsTest
  static void productCarouselReturnsDisplayUrl() {
    Map<String, Id> ids = createScenario();
    Product2 noImageProduct = new Product2(
      Name = 'Product Without Image',
      ProductCode = 'HS-NO-IMAGE',
      IsActive = true,
      RLM_HomeServices_DisplayInSelfService__c = true
    );
    insert noImageProduct;
    insert new PricebookEntry(
      Pricebook2Id = ids.get('pricebook'),
      Product2Id = noImageProduct.Id,
      UnitPrice = 50,
      IsActive = true
    );

    Test.startTest();
    List<RLM_HomeServices_ProductCarouselCtrl.ProductCard> cards = RLM_HomeServices_ProductCarouselCtrl.getProducts();
    Test.stopTest();

    Map<String, RLM_HomeServices_ProductCarouselCtrl.ProductCard> cardsByProductId = new Map<String, RLM_HomeServices_ProductCarouselCtrl.ProductCard>();
    for (RLM_HomeServices_ProductCarouselCtrl.ProductCard card : cards) {
      cardsByProductId.put(card.productId, card);
    }

    System.assertEquals(
      2,
      cards.size(),
      'Both self-service products should be returned.'
    );
    System.assertEquals(
      '/resource/HS_IMAGE_TEST',
      cardsByProductId.get(String.valueOf(ids.get('product'))).displayUrl,
      'DisplayUrl should be the single image source.'
    );
    System.assertEquals(
      null,
      cardsByProductId.get(String.valueOf(noImageProduct.Id)).displayUrl,
      'A missing DisplayUrl should remain null for the shared resolver.'
    );
  }

  @IsTest
  static void prospectValueCardReturnsDisplayUrlAndStableLineKey() {
    Map<String, Id> ids = createScenario();

    Test.startTest();
    RLM_HomeServices_ProspectValueCardCtrl.ProspectData data = RLM_HomeServices_ProspectValueCardCtrl.getProspectData(
      String.valueOf(ids.get('account'))
    );
    Test.stopTest();

    System.assertEquals(
      1,
      data.lineItems.size(),
      'The quote line should be returned.'
    );
    System.assertEquals(
      String.valueOf(ids.get('lineItem')),
      data.lineItems[0].lineItemId,
      'The quote line id should provide a stable LWC key.'
    );
    System.assertEquals(
      '/resource/HS_IMAGE_TEST',
      data.lineItems[0].displayUrl,
      'DisplayUrl should be the single image source.'
    );
  }

  @IsTest
  static void prospectValueCardRejectsInvalidAccountId() {
    Test.startTest();
    RLM_HomeServices_ProspectValueCardCtrl.ProspectData data = RLM_HomeServices_ProspectValueCardCtrl.getProspectData(
      'not-an-id'
    );
    Test.stopTest();

    System.assertEquals(
      0,
      data.lineItems.size(),
      'Invalid account ids should return an empty result.'
    );
  }
}
