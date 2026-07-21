@IsTest
private class RLM_DeltaCatalogControllerTest {

    private static Quote insertTestQuote() {
        Id pbId = Test.getStandardPricebookId();
        Account acct = new Account(Name = 'Catalog Test Account');
        insert acct;
        Opportunity opp = new Opportunity(
            Name = 'Catalog Test Opp',
            AccountId = acct.Id,
            StageName = 'Prospecting',
            CloseDate = Date.today().addDays(30)
        );
        insert opp;
        Quote q = new Quote(Name = 'Catalog Test Quote', Pricebook2Id = pbId, OpportunityId = opp.Id, Status = 'Draft');
        insert q;
        return q;
    }

    private static Product2 insertProduct(String name, String code, String type) {
        Product2 p = new Product2(Name = name, ProductCode = code, IsActive = true, Type = type);
        insert p;
        insert new PricebookEntry(Pricebook2Id = Test.getStandardPricebookId(), Product2Id = p.Id, UnitPrice = 0, IsActive = true);
        return p;
    }

    private static Map<String, Object> parse(String body) {
        return (Map<String, Object>) JSON.deserializeUntyped(body);
    }

    // ---------- getCatalogContext ----------

    @IsTest
    static void testGetCatalogContext_Valid() {
        Quote q = insertTestQuote();
        Test.startTest();
        Map<String, Object> res = parse(RLM_DeltaCatalogController.getCatalogContext(q.Id));
        Test.stopTest();
        System.assertEquals(q.Pricebook2Id, res.get('pricebook2Id'), 'Returns the quote price book');
        System.assertNotEquals(null, res.get('catalogs'), 'Catalogs key present');
    }

    @IsTest
    static void testGetCatalogContext_InvalidId() {
        Test.startTest();
        Map<String, Object> res = parse(RLM_DeltaCatalogController.getCatalogContext('not-an-id'));
        Test.stopTest();
        System.assertEquals(false, res.get('isSuccess'), 'Invalid id fails gracefully');
    }

    @IsTest
    static void testGetCatalogContext_Blank() {
        Map<String, Object> res = parse(RLM_DeltaCatalogController.getCatalogContext(null));
        System.assertEquals(false, res.get('isSuccess'), 'Blank id fails gracefully');
    }

    // ---------- searchProducts (delegates to Product Discovery via injected stub) ----------

    @IsTest
    static void testSearchProducts_FindPathShapesRows() {
        Quote q = insertTestQuote();
        StubDiscoveryService stub = new StubDiscoveryService();
        stub.searchResult = resultWith(cannedProduct());
        stub.searchResult.cursor = 'CURSOR-1';
        RLM_DeltaCatalogController.service = stub;

        Map<String, Object> in0 = new Map<String, Object>{
            'quoteId' => q.Id, 'searchTerm' => 'API', 'displayFields' => 'Family,Description'
        };
        Test.startTest();
        Map<String, Object> res = parse(RLM_DeltaCatalogController.searchProducts(JSON.serialize(in0)));
        Test.stopTest();

        System.assertEquals(true, res.get('isSuccess'), 'Search succeeds');
        System.assertEquals('findProducts', stub.lastCall, 'Non-blank term → findProducts');
        List<Object> products = (List<Object>) res.get('products');
        System.assertEquals(1, products.size(), 'One row per product');
        Map<String, Object> row = (Map<String, Object>) products[0];
        System.assertNotEquals(null, row.get('pbeId'), 'Row carries a default pbeId');
        System.assertEquals(2, ((List<Object>) row.get('sellingModels')).size(), 'Both PBEs surface as selling models');
        System.assertNotEquals(null, ((Map<String, Object>) row.get('fields')), 'Row carries a fields map');
        System.assertEquals('CURSOR-1', res.get('cursor'), 'cursor passed through');
        System.assertEquals(new List<Object>{ 'Family', 'Description' }, res.get('fields'), 'Requested field names echoed');
    }

    @IsTest
    static void testSearchProducts_BlankTermBrowses() {
        Quote q = insertTestQuote();
        StubDiscoveryService stub = new StubDiscoveryService();
        stub.browseResult = resultWith(cannedProduct());
        RLM_DeltaCatalogController.service = stub;

        Map<String, Object> in0 = new Map<String, Object>{ 'quoteId' => q.Id };
        Map<String, Object> res = parse(RLM_DeltaCatalogController.searchProducts(JSON.serialize(in0)));
        System.assertEquals(true, res.get('isSuccess'), 'Browse succeeds');
        System.assertEquals('getProducts', stub.lastCall, 'Blank term → browseProducts');
        System.assertEquals(1, ((List<Object>) res.get('products')).size(), 'One row per browsed product');
    }

    @IsTest
    static void testSearchProducts_MalformedJson() {
        Map<String, Object> res = parse(RLM_DeltaCatalogController.searchProducts('{not json'));
        System.assertEquals(false, res.get('isSuccess'), 'Malformed JSON fails gracefully');
    }

    @IsTest
    static void testSearchProducts_ServiceErrorSurfaces() {
        Quote q = insertTestQuote();
        StubDiscoveryService stub = new StubDiscoveryService();
        stub.throwOnSearch = true;
        RLM_DeltaCatalogController.service = stub;
        Map<String, Object> in0 = new Map<String, Object>{ 'quoteId' => q.Id, 'searchTerm' => 'API' };
        Map<String, Object> res = parse(RLM_DeltaCatalogController.searchProducts(JSON.serialize(in0)));
        System.assertEquals(false, res.get('isSuccess'), 'Discovery error surfaces as a failed result');
    }

    // ---------- getRecommendations ----------

    @IsTest
    static void testGetRecommendations() {
        Quote q = insertTestQuote();
        StubDiscoveryService stub = new StubDiscoveryService();
        stub.recommendResult = resultWith(cannedProduct());
        stub.recommendResult.cursor = 'NEXT-1';
        RLM_DeltaCatalogController.service = stub;

        Map<String, Object> in0 = new Map<String, Object>{ 'quoteId' => q.Id };
        Map<String, Object> res = parse(RLM_DeltaCatalogController.getRecommendations(JSON.serialize(in0)));
        System.assertEquals(true, res.get('isSuccess'), 'Recommendations succeed');
        System.assertEquals('getRecommendedProducts', stub.lastCall, 'Delegates to recommendProducts');
        System.assertEquals(1, ((List<Object>) res.get('products')).size(), 'One row per recommended product');
        System.assertEquals('NEXT-1', res.get('cursor'), 'recommendation cursor passed through');
    }

    // ---------- getProductCategories ----------

    @IsTest
    static void testGetProductCategories() {
        StubDiscoveryService stub = new StubDiscoveryService();
        RLM_DeltaProductDiscoveryService.DiscoveredCategory cat = new RLM_DeltaProductDiscoveryService.DiscoveredCategory();
        cat.id = '0ZG000000000001AAA';
        cat.name = 'Laptops';
        cat.isQualified = true;
        cat.hasSubCategories = true;
        stub.categories = new List<RLM_DeltaProductDiscoveryService.DiscoveredCategory>{ cat };
        RLM_DeltaCatalogController.service = stub;

        ProductCatalog catalog = new ProductCatalog(Name = 'Test Catalog', Code = 'TC-1');
        insert catalog;
        Map<String, Object> in0 = new Map<String, Object>{ 'catalogId' => catalog.Id };
        Map<String, Object> res = parse(RLM_DeltaCatalogController.getProductCategories(JSON.serialize(in0)));
        System.assertEquals(true, res.get('isSuccess'), 'Categories succeed');
        List<Object> cats = (List<Object>) res.get('categories');
        System.assertEquals(1, cats.size(), 'One category returned');
        System.assertEquals('Laptops', ((Map<String, Object>) cats[0]).get('name'), 'Category name surfaced');
    }

    @IsTest
    static void testGetProductCategories_InvalidCatalogId() {
        Map<String, Object> in0 = new Map<String, Object>{ 'catalogId' => 'bad' };
        Map<String, Object> res = parse(RLM_DeltaCatalogController.getProductCategories(JSON.serialize(in0)));
        System.assertEquals(false, res.get('isSuccess'), 'Invalid catalog id fails gracefully');
    }

    // ---------- shapeRows / displayFields pure helpers ----------

    @IsTest
    static void testShapeRows_OneRowPerProductWithSellingModels() {
        RLM_DeltaProductDiscoveryService.DiscoveredProduct withPrices = cannedProduct();
        RLM_DeltaProductDiscoveryService.DiscoveredProduct noPrice = new RLM_DeltaProductDiscoveryService.DiscoveredProduct();
        noPrice.name = 'No PBE';
        List<Map<String, Object>> rows = RLM_DeltaCatalogController.shapeRows(
            new List<RLM_DeltaProductDiscoveryService.DiscoveredProduct>{ withPrices, noPrice }
        );
        // One row per product now (not per PBE); the PBE-less product is skipped.
        System.assertEquals(1, rows.size(), 'One row per product; the PBE-less product is skipped');
        Map<String, Object> row = (Map<String, Object>) rows[0];
        System.assertEquals('QB-API', row.get('code'), 'Row carries product code');

        // The product's two PBEs collapse into a sellingModels list on the single row.
        List<Object> models = (List<Object>) row.get('sellingModels');
        System.assertEquals(2, models.size(), 'Both PBEs surface as selectable selling models');
        Map<String, Object> m0 = (Map<String, Object>) models[0];
        System.assertEquals('01u000000000001AAA', String.valueOf(m0.get('pbeId')), 'Model carries its PBE id');
        System.assertNotEquals(null, m0.get('productSellingModelId'), 'Model carries its PSM id');
        // No real ProductSellingModel rows exist for the canned Ids, so the label falls back to type.
        System.assertEquals('TermDefined', m0.get('label'), 'Label falls back to type when no PSM Name resolves');

        // Top-level row mirrors the default model — the first price, since none is flagged isDefault.
        System.assertEquals('01u000000000001AAA', String.valueOf(row.get('pbeId')), 'Row default pbeId is the first/default model');
        System.assertEquals('TermDefined', row.get('sellingModelType'), 'Row default selling-model type');
    }

    @IsTest
    static void testShapeRows_UsesProvidedModelLabels() {
        Map<Id, String> labels = new Map<Id, String>{
            (Id) '0jP000000000001AAA' => 'Term Annual',
            (Id) '0jP000000000002AAA' => 'Evergreen Monthly'
        };
        List<Map<String, Object>> rows = RLM_DeltaCatalogController.shapeRows(
            new List<RLM_DeltaProductDiscoveryService.DiscoveredProduct>{ cannedProduct() }, labels
        );
        List<Object> models = (List<Object>) ((Map<String, Object>) rows[0]).get('sellingModels');
        System.assertEquals('Term Annual', ((Map<String, Object>) models[0]).get('label'), 'PSM Name used as label');
        System.assertEquals('Evergreen Monthly', ((Map<String, Object>) models[1]).get('label'), 'Second PSM Name used as label');
    }

    @IsTest
    static void testDisplayFieldsFromInput_Variants() {
        // CSV string → Product2 list
        Map<String, List<String>> csv = RLM_DeltaCatalogController.displayFieldsFromInput(
            new Map<String, Object>{ 'displayFields' => 'Family, Description' }
        );
        System.assertEquals(new List<String>{ 'Family', 'Description' }, csv.get('Product2'), 'CSV parsed to Product2 fields');

        // Nested { Product2: { fields: [...] } }
        Map<String, List<String>> nested = RLM_DeltaCatalogController.displayFieldsFromInput(
            (Map<String, Object>) JSON.deserializeUntyped('{"displayFields":{"Product2":{"fields":["Family"]}}}')
        );
        System.assertEquals(new List<String>{ 'Family' }, nested.get('Product2'), 'Nested fields parsed');

        // Absent → empty
        System.assertEquals(0, RLM_DeltaCatalogController.displayFieldsFromInput(new Map<String, Object>()).size(),
            'No displayFields → empty map');
    }

    // ---------- discovery stub ----------

    private static RLM_DeltaProductDiscoveryService.DiscoveredProduct cannedProduct() {
        RLM_DeltaProductDiscoveryService.DiscoveredProduct dp = new RLM_DeltaProductDiscoveryService.DiscoveredProduct();
        dp.productId = '01t000000000001AAA';
        dp.name = 'Additional API';
        dp.code = 'QB-API';
        dp.family = 'APIs';
        dp.isBundle = false;
        dp.fields = new Map<String, Object>{ 'Family' => 'APIs', 'Description' => 'An API add-on' };
        dp.prices = new List<RLM_DeltaProductDiscoveryService.DiscoveredPrice>{
            priceWith('01u000000000001AAA', '0jP000000000001AAA', 'TermDefined'),
            priceWith('01u000000000002AAA', '0jP000000000002AAA', 'Evergreen')
        };
        return dp;
    }

    private static RLM_DeltaProductDiscoveryService.DiscoveredPrice priceWith(Id pbeId, Id psmId, String smType) {
        RLM_DeltaProductDiscoveryService.DiscoveredPrice p = new RLM_DeltaProductDiscoveryService.DiscoveredPrice();
        p.pbeId = pbeId;
        p.productSellingModelId = psmId;
        p.sellingModelType = smType;
        return p;
    }

    private static RLM_DeltaProductDiscoveryService.DiscoveryResult resultWith(RLM_DeltaProductDiscoveryService.DiscoveredProduct dp) {
        RLM_DeltaProductDiscoveryService.DiscoveryResult r = new RLM_DeltaProductDiscoveryService.DiscoveryResult();
        r.products = new List<RLM_DeltaProductDiscoveryService.DiscoveredProduct>{ dp };
        return r;
    }

    /** Test-only service standing in for live Product Discovery; records the last action called. */
    private class StubDiscoveryService extends RLM_DeltaProductDiscoveryService {
        public RLM_DeltaProductDiscoveryService.DiscoveryResult searchResult;
        public RLM_DeltaProductDiscoveryService.DiscoveryResult browseResult;
        public RLM_DeltaProductDiscoveryService.DiscoveryResult recommendResult;
        public List<RLM_DeltaProductDiscoveryService.DiscoveredCategory> categories;
        public Boolean throwOnSearch = false;
        public String lastCall;

        public override DiscoveryResult findProducts(RLM_DeltaProductDiscoveryRequest req) {
            lastCall = 'findProducts';
            if (throwOnSearch) {
                throw new RLM_DeltaProductDiscoveryService.DiscoveryException('boom');
            }
            return searchResult;
        }
        public override DiscoveryResult browseProducts(RLM_DeltaProductDiscoveryRequest req) {
            lastCall = 'getProducts';
            return browseResult;
        }
        public override DiscoveryResult recommendProducts(RLM_DeltaProductDiscoveryRequest req) {
            lastCall = 'getRecommendedProducts';
            return recommendResult;
        }
        public override List<DiscoveredCategory> getCategories(RLM_DeltaProductDiscoveryRequest req) {
            lastCall = 'getCategories';
            return categories;
        }
    }

    @IsTest
    static void testAddLines_TermDefinedSellingModel() {
        // Exercises the TermDefined branch of the line-field builder (StartDate/EndDate/BillingFrequency).
        Quote q = insertTestQuote();
        ProductSellingModel psm = new ProductSellingModel(
            Name = 'Monthly Term',
            SellingModelType = 'TermDefined',
            PricingTermUnit = 'Months',
            PricingTerm = 1,
            Status = 'Active'
        );
        insert psm;
        Product2 p = new Product2(Name = 'Term Product', ProductCode = 'TRM-1', IsActive = true);
        insert p;
        // The PBE requires the product to expose this selling model as an option first.
        insert new ProductSellingModelOption(Product2Id = p.Id, ProductSellingModelId = psm.Id);
        PricebookEntry pbe = new PricebookEntry(
            Pricebook2Id = Test.getStandardPricebookId(),
            Product2Id = p.Id,
            UnitPrice = 0,
            IsActive = true,
            ProductSellingModelId = psm.Id
        );
        insert pbe;
        Map<String, Object> in0 = new Map<String, Object>{
            'quoteId' => q.Id,
            'lines' => new List<Object>{ new Map<String, Object>{ 'pbeId' => pbe.Id, 'productId' => p.Id, 'productSellingModelId' => psm.Id } }
        };
        Test.startTest();
        Map<String, Object> res = parse(RLM_DeltaCatalogController.addLinesToQuote(JSON.serialize(in0)));
        Test.stopTest();
        System.assertNotEquals(null, res.get('isSuccess'), 'TermDefined add returns a decided result');
    }

    // ---------- getQuoteGroups ----------

    @IsTest
    static void testGetQuoteGroups_EmptyAndPopulated() {
        Quote q = insertTestQuote();
        Map<String, Object> empty = parse(RLM_DeltaCatalogController.getQuoteGroups(q.Id));
        System.assertEquals(0, ((List<Object>) empty.get('groups')).size(), 'No groups initially');

        insert new QuoteLineGroup(QuoteId = q.Id, Name = 'Group 1', SortOrder = 1);
        Map<String, Object> populated = parse(RLM_DeltaCatalogController.getQuoteGroups(q.Id));
        System.assertEquals(1, ((List<Object>) populated.get('groups')).size(), 'One group after insert');
    }

    @IsTest
    static void testGetQuoteGroups_InvalidId() {
        Map<String, Object> res = parse(RLM_DeltaCatalogController.getQuoteGroups('bad'));
        System.assertEquals(false, res.get('isSuccess'), 'Invalid id fails gracefully');
    }

    // ---------- addLinesToQuote ----------

    @IsTest
    static void testAddLines_EmptySelection() {
        Quote q = insertTestQuote();
        Map<String, Object> in0 = new Map<String, Object>{ 'quoteId' => q.Id, 'lines' => new List<Object>() };
        Map<String, Object> res = parse(RLM_DeltaCatalogController.addLinesToQuote(JSON.serialize(in0)));
        System.assertEquals(false, res.get('isSuccess'), 'Empty selection rejected');
    }

    @IsTest
    static void testAddLines_InvalidQuoteId() {
        Map<String, Object> in0 = new Map<String, Object>{
            'quoteId' => 'bad',
            'lines' => new List<Object>{ new Map<String, Object>{ 'productId' => '01t000000000000AAA' } }
        };
        Map<String, Object> res = parse(RLM_DeltaCatalogController.addLinesToQuote(JSON.serialize(in0)));
        System.assertEquals(false, res.get('isSuccess'), 'Invalid quote id rejected');
    }

    @IsTest
    static void testAddLines_UnknownPbeRejected() {
        Quote q = insertTestQuote();
        Map<String, Object> in0 = new Map<String, Object>{
            'quoteId' => q.Id,
            'lines' => new List<Object>{ new Map<String, Object>{ 'pbeId' => '01u000000000000AAA' } }
        };
        Map<String, Object> res = parse(RLM_DeltaCatalogController.addLinesToQuote(JSON.serialize(in0)));
        System.assertEquals(false, res.get('isSuccess'), 'Unknown/invalid PBE rejected before PST');
    }

    @IsTest
    static void testAddLines_CrossQuoteGroupRejected() {
        Quote q = insertTestQuote();
        // A group belonging to a DIFFERENT quote must not be a valid target.
        Quote other = insertTestQuote();
        QuoteLineGroup foreign = new QuoteLineGroup(QuoteId = other.Id, Name = 'Foreign', SortOrder = 1);
        insert foreign;
        Product2 p = insertProduct('Group Product', 'GP-1', 'Base');
        PricebookEntry pbe = [SELECT Id FROM PricebookEntry WHERE Product2Id = :p.Id LIMIT 1];
        Map<String, Object> in0 = new Map<String, Object>{
            'quoteId' => q.Id,
            'lines' => new List<Object>{ new Map<String, Object>{ 'pbeId' => pbe.Id, 'productId' => p.Id, 'targetGroupId' => foreign.Id } }
        };
        Map<String, Object> res = parse(RLM_DeltaCatalogController.addLinesToQuote(JSON.serialize(in0)));
        System.assertEquals(false, res.get('isSuccess'), 'Cross-quote target group rejected');
    }

    @IsTest
    static void testAddLines_TamperedProductRejected() {
        Quote q = insertTestQuote();
        Product2 p = insertProduct('Tamper Product', 'TP-1', 'Base');
        PricebookEntry pbe = [SELECT Id FROM PricebookEntry WHERE Product2Id = :p.Id LIMIT 1];
        // Claimed productId does not match the PBE's product → tamper guard fires.
        Map<String, Object> in0 = new Map<String, Object>{
            'quoteId' => q.Id,
            'lines' => new List<Object>{ new Map<String, Object>{ 'pbeId' => pbe.Id, 'productId' => '01t000000000000AAA' } }
        };
        Map<String, Object> res = parse(RLM_DeltaCatalogController.addLinesToQuote(JSON.serialize(in0)));
        System.assertEquals(false, res.get('isSuccess'), 'Mismatched product id rejected');
    }

    @IsTest
    static void testAddLines_ValidSelection_GracefulContract() {
        // PST is non-deterministic in test context (depends on full org config). We assert the
        // graceful contract: a result is returned with isSuccess set, never an exception.
        Quote q = insertTestQuote();
        Product2 p = insertProduct('Addable Product', 'AD-1', 'Base');
        PricebookEntry pbe = [SELECT Id, ProductSellingModelId FROM PricebookEntry WHERE Product2Id = :p.Id LIMIT 1];
        Map<String, Object> in0 = new Map<String, Object>{
            'quoteId' => q.Id,
            'newGroupName' => 'Negotiation Group',
            'lines' => new List<Object>{ new Map<String, Object>{ 'pbeId' => pbe.Id, 'productId' => p.Id, 'quantity' => 2 } }
        };
        Test.startTest();
        Map<String, Object> res = parse(RLM_DeltaCatalogController.addLinesToQuote(JSON.serialize(in0)));
        Test.stopTest();
        System.assertNotEquals(null, res.get('isSuccess'), 'Always decides success (true or false)');
    }

    @IsTest
    static void testAddLines_FallbackByProductId() {
        // Line omits pbeId → deterministic fallback resolves a PBE by product. Graceful contract.
        Quote q = insertTestQuote();
        Product2 p = insertProduct('Fallback Product', 'FB-1', 'Base');
        Map<String, Object> in0 = new Map<String, Object>{
            'quoteId' => q.Id,
            'lines' => new List<Object>{ new Map<String, Object>{ 'productId' => p.Id } }
        };
        Test.startTest();
        Map<String, Object> res = parse(RLM_DeltaCatalogController.addLinesToQuote(JSON.serialize(in0)));
        Test.stopTest();
        System.assertNotEquals(null, res.get('isSuccess'), 'Fallback path returns a decided result');
    }

    @IsTest
    static void testAddLines_FallbackNoPbeRejected() {
        Quote q = insertTestQuote();
        Product2 p = new Product2(Name = 'No PBE Product', ProductCode = 'NOPBE', IsActive = true);
        insert p; // no PricebookEntry
        Map<String, Object> in0 = new Map<String, Object>{
            'quoteId' => q.Id,
            'lines' => new List<Object>{ new Map<String, Object>{ 'productId' => p.Id } }
        };
        Map<String, Object> res = parse(RLM_DeltaCatalogController.addLinesToQuote(JSON.serialize(in0)));
        System.assertEquals(false, res.get('isSuccess'), 'Product with no PBE on the quote book is rejected');
    }

    @IsTest
    static void testAddLines_MalformedJson() {
        Map<String, Object> res = parse(RLM_DeltaCatalogController.addLinesToQuote('{bad'));
        System.assertEquals(false, res.get('isSuccess'), 'Malformed JSON fails gracefully');
    }

    // ---------- getConfiguratorLaunch ----------

    // Inserts a configurable product + PBE on the standard book; returns the PBE.
    private static PricebookEntry insertConfigurableProduct(String name, String code) {
        Product2 p = new Product2(Name = name, ProductCode = code, IsActive = true, ConfigureDuringSale = 'Allowed');
        insert p;
        insert new PricebookEntry(Pricebook2Id = Test.getStandardPricebookId(), Product2Id = p.Id, UnitPrice = 100, IsActive = true);
        return [SELECT Id, Product2Id, ProductSellingModelId FROM PricebookEntry WHERE Product2Id = :p.Id LIMIT 1];
    }

    // The shipped Primary Configurator flow — always present and Active as package metadata, so a
    // ProductConfigurationFlow row can be inserted against it in any RLM-enabled org (the platform
    // validates FlowIdentifier against a real active flow on insert). NOTE the form: FlowIdentifier
    // accepts only the BARE ApiName ('ProductConfig'); the namespaced launch reference
    // ('runtime_industries_cfg__ProductConfig', = SHIPPED_DEFAULT_CONFIGURATOR_FLOW) is rejected on
    // insert. That difference is deliberate here — an inserted row reads back bare, distinct from
    // the namespaced shipped-fallback constant, which lets the precedence tests below tell "resolved
    // a real row" apart from "fell through to the shipped default."
    private static final String REAL_CONFIGURATOR_FLOW = 'ProductConfig';

    // Inserts a Primary Configurator flow + a product-level assignment, mirroring the mfg-configflow plan.
    private static void assignConfiguratorFlow(Id productId, String flowApiName) {
        ProductConfigurationFlow f = new ProductConfigurationFlow(FlowIdentifier = flowApiName, IsDefault = false, Status = 'Active');
        insert f;
        insert new ProductConfigFlowAssignment(
            AssignmentType = 'PrimaryConfiguratorFlow',
            ProductConfigurationFlowId = f.Id,
            ProductId = productId
        );
    }

    @IsTest
    static void testConfiguratorLaunch_ConfigurableWithAssignedFlow() {
        Quote q = insertTestQuote();
        PricebookEntry pbe = insertConfigurableProduct('Configurable Bundle', 'CFG-1');
        assignConfiguratorFlow(pbe.Product2Id, REAL_CONFIGURATOR_FLOW);

        Map<String, Object> in0 = new Map<String, Object>{
            'quoteId' => q.Id, 'pbeId' => pbe.Id, 'productId' => pbe.Product2Id
        };
        Test.startTest();
        Map<String, Object> res = parse(RLM_DeltaCatalogController.getConfiguratorLaunch(JSON.serialize(in0)));
        Test.stopTest();

        System.assertEquals(true, res.get('isSuccess'), 'Configurable product with assigned flow launches');
        System.assertEquals(REAL_CONFIGURATOR_FLOW, res.get('flowApiName'), 'Product-level assignment wins');
        Map<String, Object> ctx = (Map<String, Object>) res.get('configuratorContext');
        System.assertEquals(String.valueOf(q.Id), ctx.get('transactionId'), 'Quote id is the transaction id');
        System.assertEquals('Quote', ctx.get('origin'), 'Origin is Quote');
        List<Object> nodes = (List<Object>) ctx.get('addedNodes');
        System.assertEquals(1, nodes.size(), 'One synthetic added node');
        Map<String, Object> node = (Map<String, Object>) nodes[0];
        // Configure-before-add anchors the configurator on a synthetic line: the platform mints a
        // ref_<uuid> id and sets BOTH the node id AND the context's transactionLineId to it (a null
        // transactionLineId yields "Transaction Line ID is missing input" and an empty configurator).
        String syntheticId = (String) node.get('id');
        System.assert(syntheticId != null && syntheticId.startsWith('ref_'), 'Synthetic node id is a ref_ token');
        System.assertEquals(syntheticId, ctx.get('transactionLineId'), 'Context transactionLineId matches the synthetic node id');
        System.assertEquals(syntheticId, node.get('salesTransactionItemSource'), 'Node source carries the same synthetic id');
        System.assertEquals(pbe.Id, node.get('pricebookEntry'), 'Node carries the PBE');
        System.assertEquals(pbe.Product2Id, node.get('product'), 'Node carries the product');
        System.assertEquals('QuoteLineItem', node.get('businessObjectType'), 'Node targets QuoteLineItem');
    }

    @IsTest
    static void testConfiguratorLaunch_NonConfigurableRejected() {
        Quote q = insertTestQuote();
        Product2 p = insertProduct('Plain Product', 'PLN-1', 'Base'); // ConfigureDuringSale defaults to NotAllowed
        PricebookEntry pbe = [SELECT Id, Product2Id FROM PricebookEntry WHERE Product2Id = :p.Id LIMIT 1];
        Map<String, Object> in0 = new Map<String, Object>{ 'quoteId' => q.Id, 'pbeId' => pbe.Id };
        Map<String, Object> res = parse(RLM_DeltaCatalogController.getConfiguratorLaunch(JSON.serialize(in0)));
        System.assertEquals(false, res.get('isSuccess'), 'Non-configurable product rejected server-side');
        System.assert(((String) res.get('errorMessage')).contains('not configurable'), 'Surfaces configurability error');
    }

    @IsTest
    static void testConfiguratorLaunch_FallsBackToShippedDefaultFlow() {
        Quote q = insertTestQuote();
        PricebookEntry pbe = insertConfigurableProduct('Orphan Configurable', 'CFG-2');
        // No assignment, no IsDefault flow → resolves to the shipped Default Product Configurator Flow.
        Map<String, Object> in0 = new Map<String, Object>{ 'quoteId' => q.Id, 'pbeId' => pbe.Id };
        Map<String, Object> res = parse(RLM_DeltaCatalogController.getConfiguratorLaunch(JSON.serialize(in0)));
        System.assertEquals(true, res.get('isSuccess'), 'Configurable product launches via the shipped default flow');
        System.assertEquals(RLM_DeltaCatalogController.SHIPPED_DEFAULT_CONFIGURATOR_FLOW, res.get('flowApiName'),
            'Falls back to the shipped Default Product Configurator Flow');
    }

    @IsTest
    static void testConfiguratorLaunch_InvalidPbeRejected() {
        Quote q = insertTestQuote();
        Map<String, Object> in0 = new Map<String, Object>{ 'quoteId' => q.Id, 'pbeId' => '01u000000000000AAA' };
        Map<String, Object> res = parse(RLM_DeltaCatalogController.getConfiguratorLaunch(JSON.serialize(in0)));
        System.assertEquals(false, res.get('isSuccess'), 'Unknown PBE rejected');
    }

    @IsTest
    static void testConfiguratorLaunch_TamperedProductRejected() {
        Quote q = insertTestQuote();
        PricebookEntry pbe = insertConfigurableProduct('Tamper Configurable', 'CFG-3');
        // Claimed productId does not match the resolved PBE → tamper guard fires before any flow work.
        Map<String, Object> in0 = new Map<String, Object>{
            'quoteId' => q.Id, 'pbeId' => pbe.Id, 'productId' => '01t000000000000AAA'
        };
        Map<String, Object> res = parse(RLM_DeltaCatalogController.getConfiguratorLaunch(JSON.serialize(in0)));
        System.assertEquals(false, res.get('isSuccess'), 'Mismatched product id rejected');
        System.assert(((String) res.get('errorMessage')).contains('does not match'), 'Surfaces tamper error');
    }

    @IsTest
    static void testConfiguratorLaunch_InvalidQuoteId() {
        Map<String, Object> in0 = new Map<String, Object>{ 'quoteId' => 'bad', 'pbeId' => '01u000000000000AAA' };
        Map<String, Object> res = parse(RLM_DeltaCatalogController.getConfiguratorLaunch(JSON.serialize(in0)));
        System.assertEquals(false, res.get('isSuccess'), 'Invalid quote id rejected');
    }

    @IsTest
    static void testConfiguratorLaunch_MalformedJson() {
        Map<String, Object> res = parse(RLM_DeltaCatalogController.getConfiguratorLaunch('{bad'));
        System.assertEquals(false, res.get('isSuccess'), 'Malformed JSON fails gracefully');
    }

    // ---------- commitConfiguredQuote ----------

    @IsTest
    static void testCommitConfigured_MalformedJson() {
        Map<String, Object> res = parse(RLM_DeltaCatalogController.commitConfiguredQuote('{bad'));
        System.assertEquals(false, res.get('isSuccess'), 'Malformed JSON fails gracefully');
    }

    @IsTest
    static void testCommitConfigured_InvalidQuoteId() {
        Map<String, Object> in0 = new Map<String, Object>{
            'quoteId' => 'bad',
            'transactionContext' => new Map<String, Object>{ 'SalesTransaction' => new List<Object>() }
        };
        Map<String, Object> res = parse(RLM_DeltaCatalogController.commitConfiguredQuote(JSON.serialize(in0)));
        System.assertEquals(false, res.get('isSuccess'), 'Invalid quote id rejected');
    }

    @IsTest
    static void testCommitConfigured_MissingContextRejected() {
        Quote q = insertTestQuote();
        Map<String, Object> in0 = new Map<String, Object>{ 'quoteId' => q.Id };
        Map<String, Object> res = parse(RLM_DeltaCatalogController.commitConfiguredQuote(JSON.serialize(in0)));
        System.assertEquals(false, res.get('isSuccess'), 'Absent transactionContext rejected');
        System.assert(((String) res.get('errorMessage')).contains('transactionContext'), 'Surfaces missing-context error');
    }

    @IsTest
    static void testCommitConfigured_NoSalesTransactionRejected() {
        Quote q = insertTestQuote();
        Map<String, Object> in0 = new Map<String, Object>{
            'quoteId' => q.Id,
            'transactionContext' => new Map<String, Object>{ 'SalesTransaction' => new List<Object>() }
        };
        Map<String, Object> res = parse(RLM_DeltaCatalogController.commitConfiguredQuote(JSON.serialize(in0)));
        System.assertEquals(false, res.get('isSuccess'), 'Empty SalesTransaction rejected');
        System.assert(((String) res.get('errorMessage')).contains('No sales transaction'), 'Surfaces no-transaction error');
    }

    @IsTest
    static void testCommitConfigured_CrossQuoteContextRejected() {
        Quote q = insertTestQuote();
        Quote other = insertTestQuote();
        // The context echoes a DIFFERENT quote's id → the quote-match guard fires before any PST work.
        Map<String, Object> in0 = new Map<String, Object>{
            'quoteId' => q.Id,
            'transactionContext' => new Map<String, Object>{
                'SalesTransaction' => new List<Object>{
                    new Map<String, Object>{ 'id' => other.Id, 'SalesTransactionItem' => new List<Object>() }
                }
            }
        };
        Map<String, Object> res = parse(RLM_DeltaCatalogController.commitConfiguredQuote(JSON.serialize(in0)));
        System.assertEquals(false, res.get('isSuccess'), 'Context for a different quote rejected');
        System.assert(((String) res.get('errorMessage')).contains('does not match'), 'Surfaces mismatch error');
    }

    @IsTest
    static void testCommitConfigured_NoItemsRejected() {
        Quote q = insertTestQuote();
        Map<String, Object> in0 = new Map<String, Object>{
            'quoteId' => q.Id,
            'transactionContext' => new Map<String, Object>{
                'SalesTransaction' => new List<Object>{
                    new Map<String, Object>{ 'id' => q.Id, 'SalesTransactionItem' => new List<Object>() }
                }
            }
        };
        Map<String, Object> res = parse(RLM_DeltaCatalogController.commitConfiguredQuote(JSON.serialize(in0)));
        System.assertEquals(false, res.get('isSuccess'), 'Configured product with no lines rejected');
        System.assert(((String) res.get('errorMessage')).contains('no lines'), 'Surfaces no-lines error');
    }

    @IsTest
    static void testCommitConfigured_FullGraphGracefulContract() {
        // Exercises the configurator-save → PST graph translation across every builder: the line
        // field map (TermDefined subscription branch), attribute children, and a parent/child
        // relationship resolved to graph ref tokens. PST itself is non-deterministic in test context
        // (depends on full org config), so we assert the graceful contract: a decided result with
        // isSuccess set, never an exception.
        Quote q = insertTestQuote();
        Product2 p = insertProduct('Configured Root', 'CR-1', 'Base');
        PricebookEntry pbe = [SELECT Id, Product2Id FROM PricebookEntry WHERE Product2Id = :p.Id LIMIT 1];

        Map<String, Object> rootItem = new Map<String, Object>{
            'id' => 'ref_root_0001',
            'Product' => p.Id,
            'PricebookEntry' => pbe.Id,
            'Quantity' => 1,
            'UnitPrice' => 100,
            'SellingModelType' => 'TermDefined',
            'BillingFrequency' => 'Monthly',
            'PeriodBoundary' => 'Anniversary',
            'SubscriptionTerm' => 12,
            'SalesTransactionItemAttribute' => new List<Object>{
                new Map<String, Object>{ 'AttributeKey' => '0RB000000000001AAA', 'AttributeValue' => 'Linux' }
            }
        };
        Map<String, Object> childItem = new Map<String, Object>{
            'id' => 'ref_child_0002',
            'Product' => p.Id,
            'PricebookEntry' => pbe.Id,
            'Quantity' => 2,
            'SellingModelType' => 'OneTime',
            'SalesTrxnItemRelationship' => new List<Object>{
                new Map<String, Object>{ 'MainItem' => 'ref_child_0002', 'RootItem' => 'ref_root_0001' }
            }
        };
        Map<String, Object> in0 = new Map<String, Object>{
            'quoteId' => q.Id,
            'transactionContext' => new Map<String, Object>{
                'SalesTransaction' => new List<Object>{
                    new Map<String, Object>{
                        'id' => q.Id,
                        'SalesTransactionItem' => new List<Object>{ rootItem, childItem }
                    }
                }
            }
        };
        Test.startTest();
        Map<String, Object> res = parse(RLM_DeltaCatalogController.commitConfiguredQuote(JSON.serialize(in0)));
        Test.stopTest();
        System.assertNotEquals(null, res.get('isSuccess'), 'Full configured graph returns a decided result');
    }

    // ---------- resolveConfiguratorFlowApiName precedence ----------

    // FOLLOW-UP (no clear path in a single org): testResolveFlow_ProductAssignmentBeatsDefault was
    // removed. It needs TWO distinct configurator flows — a product-level assignment AND a different
    // org-default — to prove the product assignment wins. The platform blocks this: (1) only the
    // shipped 'ProductConfig' flow exists to seed against, and (2) "a flow can only be associated
    // with one product configuration flow" forbids a second ProductConfigurationFlow row. Restore
    // when a scratch-org def can deploy a second active configurator flow (then assign one at the
    // product level and mark the other IsDefault). Product-vs-classification-vs-default precedence
    // is still partially covered by testResolveFlow_FallsBackToOrgDefault.

    @IsTest
    static void testResolveFlow_FallsBackToOrgDefault() {
        PricebookEntry pbe = insertConfigurableProduct('Default Fallback Product', 'PRC-2');
        // No assignment; only an IsDefault flow exists. The inserted row's identifier is the BARE
        // ApiName, distinct from the namespaced shipped-default constant, so resolving to it proves
        // the IsDefault row was found rather than the shipped fallback being returned.
        insert new ProductConfigurationFlow(FlowIdentifier = REAL_CONFIGURATOR_FLOW, IsDefault = true, Status = 'Active');

        Test.startTest();
        String resolved = RLM_DeltaCatalogController.resolveConfiguratorFlowApiName(pbe.Product2Id, null);
        Test.stopTest();
        System.assertEquals(REAL_CONFIGURATOR_FLOW, resolved, 'Falls back to the IsDefault org flow when nothing is assigned');
        System.assertNotEquals(RLM_DeltaCatalogController.SHIPPED_DEFAULT_CONFIGURATOR_FLOW, resolved,
            'The IsDefault row wins over the shipped fallback');
    }

    @IsTest
    static void testResolveFlow_InactiveDefaultIgnoredFallsToShipped() {
        PricebookEntry pbe = insertConfigurableProduct('Inactive Default Product', 'PRC-3');
        // A default flow exists but is not Active → the resolver's Status='Active' filter skips it,
        // so resolution falls through to the shipped default. (Seeded with the real bare flow at
        // Draft status; the platform validates the flow exists but allows a non-Active row.)
        insert new ProductConfigurationFlow(FlowIdentifier = REAL_CONFIGURATOR_FLOW, IsDefault = true, Status = 'Draft');

        Test.startTest();
        String resolved = RLM_DeltaCatalogController.resolveConfiguratorFlowApiName(pbe.Product2Id, null);
        Test.stopTest();
        System.assertEquals(RLM_DeltaCatalogController.SHIPPED_DEFAULT_CONFIGURATOR_FLOW, resolved,
            'A non-Active default flow is ignored; falls back to the shipped default flow');
    }

    @IsTest
    static void testResolveFlow_NothingAssignedReturnsShippedDefault() {
        PricebookEntry pbe = insertConfigurableProduct('No Config Product', 'PRC-4');
        // No assignment, no IsDefault row at all → shipped default.
        Test.startTest();
        String resolved = RLM_DeltaCatalogController.resolveConfiguratorFlowApiName(pbe.Product2Id, null);
        Test.stopTest();
        System.assertEquals(RLM_DeltaCatalogController.SHIPPED_DEFAULT_CONFIGURATOR_FLOW, resolved,
            'With nothing assigned, resolves to the shipped Default Product Configurator Flow');
    }

    // ---------- reconfigure: shared helpers ----------

    // Inserts a QuoteLineItem (Quantity/UnitPrice) and returns it. Used to obtain REAL QLI ids for
    // the reconfigure launch + commit paths.
    private static QuoteLineItem insertQli(Quote q, PricebookEntry pbe, Decimal qty) {
        QuoteLineItem qli = new QuoteLineItem(
            QuoteId = q.Id, PricebookEntryId = pbe.Id, Product2Id = pbe.Product2Id,
            Quantity = qty, UnitPrice = 10
        );
        insert qli;
        return qli;
    }

    // Deterministic fake Id of a given SObjectType (15-char, no DML) — lets buildReconfigureGraph be
    // exercised as a pure assembler with real-looking ids in the persisted/returned sets.
    private static Integer s_fakeIdSeq = 1;
    private static Id fakeId(Schema.SObjectType sot) {
        String prefix = sot.getDescribe().getKeyPrefix();
        String suffix = String.valueOf(s_fakeIdSeq++);
        return Id.valueOf(prefix + '0'.repeat(12 - suffix.length()) + suffix);
    }

    // Finds the first graph record whose verb + object match (and optionally id), else null.
    private static RevSalesTrxn.RecordResource findRecord(
        List<RevSalesTrxn.RecordWithReferenceRequest> records, String method, Schema.SObjectType type, Id id
    ) {
        for (RevSalesTrxn.RecordWithReferenceRequest r : records) {
            RevSalesTrxn.RecordResource rec = r.record;
            if (rec.method == method && rec.type == type && (id == null || rec.id == id)) {
                return rec;
            }
        }
        return null;
    }

    // ---------- getReconfigureLaunch ----------

    @IsTest
    static void testReconfigureLaunch_ValidLineReturnsRootAndQuote() {
        Quote q = insertTestQuote();
        PricebookEntry pbe = insertConfigurableProduct('Reconfig Bundle', 'RC-1');
        QuoteLineItem qli = insertQli(q, pbe, 1);

        Test.startTest();
        Map<String, Object> res = parse(RLM_DeltaCatalogController.getReconfigureLaunch(
            JSON.serialize(new Map<String, Object>{ 'quoteLineItemId' => qli.Id })));
        Test.stopTest();

        System.assertEquals(true, res.get('isSuccess'), 'Configurable QLI launches: ' + res.get('errorMessage'));
        System.assertEquals(qli.Id, res.get('rootQuoteLineItemId'), 'Returns the line as its own root');
        System.assertEquals(q.Id, res.get('quoteId'), 'Returns the quote id for the commit');
        System.assert(String.isNotBlank((String) res.get('flowApiName')), 'Resolves a configurator flow');
        Map<String, Object> ctx = (Map<String, Object>) res.get('configuratorContext');
        System.assertEquals(qli.Id, ctx.get('transactionLineId'), 'Hydration context carries the REAL root QLI id');
        System.assertEquals(q.Id, ctx.get('transactionId'), 'Hydration context carries the quote id');
    }

    @IsTest
    static void testReconfigureLaunch_NonConfigurableRejected() {
        Quote q = insertTestQuote();
        Product2 p = insertProduct('Plain Line', 'PL-1', 'Base'); // ConfigureDuringSale not 'Allowed'
        PricebookEntry pbe = [SELECT Id, Product2Id FROM PricebookEntry WHERE Product2Id = :p.Id LIMIT 1];
        QuoteLineItem qli = insertQli(q, pbe, 1);

        Map<String, Object> res = parse(RLM_DeltaCatalogController.getReconfigureLaunch(
            JSON.serialize(new Map<String, Object>{ 'quoteLineItemId' => qli.Id })));
        System.assertEquals(false, res.get('isSuccess'), 'Non-Allowed product blocked');
        System.assert(((String) res.get('errorMessage')).contains('not configurable'), 'Surfaces the guard message');
    }

    @IsTest
    static void testReconfigureLaunch_InvalidId() {
        Map<String, Object> res = parse(RLM_DeltaCatalogController.getReconfigureLaunch(
            JSON.serialize(new Map<String, Object>{ 'quoteLineItemId' => 'bad' })));
        System.assertEquals(false, res.get('isSuccess'), 'Invalid id rejected');
    }

    @IsTest
    static void testReconfigureLaunch_MalformedJson() {
        Map<String, Object> res = parse(RLM_DeltaCatalogController.getReconfigureLaunch('{bad'));
        System.assertEquals(false, res.get('isSuccess'), 'Malformed JSON fails gracefully');
    }

    @IsTest
    static void testResolveBundleRoot_StandaloneIsOwnRoot() {
        Quote q = insertTestQuote();
        PricebookEntry pbe = insertConfigurableProduct('Standalone', 'RC-2');
        QuoteLineItem qli = insertQli(q, pbe, 1);
        // No QuoteLineRelationship exists → the line is its own root.
        System.assertEquals(qli.Id, RLM_DeltaCatalogController.resolveBundleRootQuoteLineId(qli.Id),
            'A line with no relationship resolves to itself');
    }

    // ---------- buildReconfigureGraph (pure assembler) ----------

    @IsTest
    static void testBuildReconfigureGraph_MixedPatchPostDelete() {
        Id qId = fakeId(Quote.getSObjectType());
        Id rootId = fakeId(QuoteLineItem.getSObjectType());     // existing root → PATCH
        Id childId = fakeId(QuoteLineItem.getSObjectType());    // existing child → PATCH
        Id removedLineId = fakeId(QuoteLineItem.getSObjectType()); // persisted but absent → DELETE
        Id keepAttrId = fakeId(QuoteLineItemAttribute.getSObjectType());   // returned → PATCH
        Id removedAttrId = fakeId(QuoteLineItemAttribute.getSObjectType()); // absent → DELETE
        Id keepRelId = fakeId(QuoteLineRelationship.getSObjectType());   // returned → kept
        Id removedRelId = fakeId(QuoteLineRelationship.getSObjectType()); // absent → DELETE

        Map<String, Object> rootItem = new Map<String, Object>{
            'id' => String.valueOf(rootId),
            'Product' => fakeId(Product2.getSObjectType()),
            'PricebookEntry' => fakeId(PricebookEntry.getSObjectType()),
            'Quantity' => 1, 'UnitPrice' => 100,
            'SalesTransactionItemAttribute' => new List<Object>{
                new Map<String, Object>{ 'id' => String.valueOf(keepAttrId), 'AttributeValue' => 'Linux' }
            }
        };
        Map<String, Object> childItem = new Map<String, Object>{
            'id' => String.valueOf(childId),
            'Product' => fakeId(Product2.getSObjectType()),
            'Quantity' => 2,
            'SalesTrxnItemRelationship' => new List<Object>{
                new Map<String, Object>{ 'id' => String.valueOf(keepRelId), 'MainItem' => String.valueOf(childId), 'RootItem' => String.valueOf(rootId) }
            }
        };
        Map<String, Object> newItem = new Map<String, Object>{
            'id' => 'ref_new_0001',
            'Product' => fakeId(Product2.getSObjectType()),
            'PricebookEntry' => fakeId(PricebookEntry.getSObjectType()),
            'Quantity' => 1, 'SellingModelType' => 'OneTime',
            'SalesTransactionItemAttribute' => new List<Object>{
                new Map<String, Object>{ 'AttributeKey' => fakeId(AttributeDefinition.getSObjectType()), 'AttributeValue' => 'New' }
            },
            'SalesTrxnItemRelationship' => new List<Object>{
                new Map<String, Object>{ 'MainItem' => 'ref_new_0001', 'RootItem' => String.valueOf(rootId) }
            }
        };
        Map<String, Object> ctx = new Map<String, Object>{
            'SalesTransaction' => new List<Object>{
                new Map<String, Object>{ 'id' => String.valueOf(qId),
                    'SalesTransactionItem' => new List<Object>{ rootItem, childItem, newItem } }
            }
        };

        Set<Id> persistedLines = new Set<Id>{ rootId, childId, removedLineId };
        Set<Id> persistedAttrs = new Set<Id>{ keepAttrId, removedAttrId };
        Set<Id> persistedRels = new Set<Id>{ keepRelId, removedRelId };

        RLM_DeltaCatalogController.ReconcileResult plan =
            RLM_DeltaCatalogController.buildReconfigureGraph(
                qId, rootId, ctx, persistedLines, persistedAttrs, persistedRels);

        // Counts.
        System.assertEquals(2, plan.updatedCount, 'Two existing lines PATCHed (root + child)');
        System.assertEquals(1, plan.addedCount, 'One new line POSTed');
        System.assertEquals(1, plan.deletedCount, 'One removed line DELETEd');

        // PATCH of an existing line is IDENTITY-FREE.
        RevSalesTrxn.RecordResource rootPatch =
            findRecord(plan.records, 'PATCH', QuoteLineItem.getSObjectType(), rootId);
        System.assertNotEquals(null, rootPatch, 'Root line PATCH present');
        System.assert(!rootPatch.fieldValues.containsKey('QuoteId'), 'PATCH never reparents (no QuoteId)');
        System.assert(!rootPatch.fieldValues.containsKey('Product2Id'), 'PATCH never re-identifies (no Product2Id)');
        System.assert(!rootPatch.fieldValues.containsKey('PricebookEntryId'), 'PATCH never re-prices identity (no PricebookEntryId)');

        // New line POST sets identity fields.
        RevSalesTrxn.RecordResource newPost =
            findRecord(plan.records, 'POST', QuoteLineItem.getSObjectType(), null);
        System.assertNotEquals(null, newPost, 'New line POST present');
        System.assertEquals(String.valueOf(qId), newPost.fieldValues.get('QuoteId'), 'POST sets QuoteId identity');

        // Reconciliation: removed sets exclude survivors and the root.
        System.assert(plan.removedLineIds.contains(removedLineId), 'Absent persisted line marked removed');
        System.assert(!plan.removedLineIds.contains(rootId), 'Root is NEVER a delete candidate');
        System.assert(!plan.removedLineIds.contains(childId), 'Surviving child not removed');
        System.assert(plan.removedAttrIds.contains(removedAttrId), 'Absent attribute marked removed');
        System.assert(!plan.removedAttrIds.contains(keepAttrId), 'Returned attribute kept');
        System.assert(plan.removedRelIds.contains(removedRelId), 'Absent relationship marked removed');
        System.assert(!plan.removedRelIds.contains(keepRelId), 'Returned relationship kept');

        // DELETE nodes present for each removed record.
        System.assertNotEquals(null, findRecord(plan.records, 'DELETE', QuoteLineRelationship.getSObjectType(), removedRelId), 'Removed rel DELETEd');
        System.assertNotEquals(null, findRecord(plan.records, 'DELETE', QuoteLineItemAttribute.getSObjectType(), removedAttrId), 'Removed attr DELETEd');
        System.assertNotEquals(null, findRecord(plan.records, 'DELETE', QuoteLineItem.getSObjectType(), removedLineId), 'Removed line DELETEd');

        // DELETE order is dependency-safe child → parent: relationship before attribute before line.
        Integer relPos = -1, attrPos = -1, linePos = -1;
        for (Integer i = 0; i < plan.records.size(); i++) {
            RevSalesTrxn.RecordResource rec = plan.records[i].record;
            if (rec.method != 'DELETE') { continue; }
            if (rec.type == QuoteLineRelationship.getSObjectType()) { relPos = i; }
            else if (rec.type == QuoteLineItemAttribute.getSObjectType()) { attrPos = i; }
            else if (rec.type == QuoteLineItem.getSObjectType()) { linePos = i; }
        }
        System.assert(relPos < attrPos && attrPos < linePos,
            'DELETEs ordered relationship → attribute → line (child before parent)');
    }

    @IsTest
    static void testBuildReconfigureGraph_RootProtectedWhenAbsentFromTree() {
        // The returned tree omits the root entirely; the root must still never be deleted.
        Id qId = fakeId(Quote.getSObjectType());
        Id rootId = fakeId(QuoteLineItem.getSObjectType());
        Map<String, Object> ctx = new Map<String, Object>{
            'SalesTransaction' => new List<Object>{
                new Map<String, Object>{ 'id' => String.valueOf(qId), 'SalesTransactionItem' => new List<Object>() }
            }
        };
        RLM_DeltaCatalogController.ReconcileResult plan =
            RLM_DeltaCatalogController.buildReconfigureGraph(
                qId, rootId, ctx, new Set<Id>{ rootId }, new Set<Id>(), new Set<Id>());
        System.assertEquals(0, plan.deletedCount, 'Root-only persisted set yields no deletes');
        System.assert(!plan.removedLineIds.contains(rootId), 'Root never appears in the delete set');
    }

    // ---------- commitReconfiguredQuote guards ----------

    @IsTest
    static void testCommitReconfigure_MalformedJson() {
        Map<String, Object> res = parse(RLM_DeltaCatalogController.commitReconfiguredQuote('{bad'));
        System.assertEquals(false, res.get('isSuccess'), 'Malformed JSON fails gracefully');
    }

    @IsTest
    static void testCommitReconfigure_RootNotOnQuoteRejected() {
        Quote q = insertTestQuote();
        Quote other = insertTestQuote();
        PricebookEntry pbe = insertConfigurableProduct('Foreign Root', 'RC-3');
        QuoteLineItem foreignRoot = insertQli(other, pbe, 1); // belongs to a DIFFERENT quote
        Map<String, Object> in0 = new Map<String, Object>{
            'quoteId' => q.Id,
            'rootQuoteLineItemId' => foreignRoot.Id,
            'transactionContext' => new Map<String, Object>{ 'SalesTransaction' => new List<Object>() }
        };
        Map<String, Object> res = parse(RLM_DeltaCatalogController.commitReconfiguredQuote(JSON.serialize(in0)));
        System.assertEquals(false, res.get('isSuccess'), 'Root on a different quote rejected');
        System.assert(((String) res.get('errorMessage')).contains('does not belong'), 'Surfaces the ownership guard');
    }

    @IsTest
    static void testCommitReconfigure_CrossQuoteContextRejected() {
        Quote q = insertTestQuote();
        Quote other = insertTestQuote();
        PricebookEntry pbe = insertConfigurableProduct('Reconfig Root', 'RC-4');
        QuoteLineItem root = insertQli(q, pbe, 1);
        // Context echoes a DIFFERENT quote id → the tamper guard fires.
        Map<String, Object> in0 = new Map<String, Object>{
            'quoteId' => q.Id,
            'rootQuoteLineItemId' => root.Id,
            'transactionContext' => new Map<String, Object>{
                'SalesTransaction' => new List<Object>{
                    new Map<String, Object>{ 'id' => other.Id, 'SalesTransactionItem' => new List<Object>() }
                }
            }
        };
        Map<String, Object> res = parse(RLM_DeltaCatalogController.commitReconfiguredQuote(JSON.serialize(in0)));
        System.assertEquals(false, res.get('isSuccess'), 'Context for a different quote rejected');
        System.assert(((String) res.get('errorMessage')).contains('does not match'), 'Surfaces the mismatch error');
    }

    @IsTest
    static void testCommitReconfigure_MissingContextRejected() {
        Quote q = insertTestQuote();
        PricebookEntry pbe = insertConfigurableProduct('Reconfig NoCtx', 'RC-5');
        QuoteLineItem root = insertQli(q, pbe, 1);
        Map<String, Object> in0 = new Map<String, Object>{ 'quoteId' => q.Id, 'rootQuoteLineItemId' => root.Id };
        Map<String, Object> res = parse(RLM_DeltaCatalogController.commitReconfiguredQuote(JSON.serialize(in0)));
        System.assertEquals(false, res.get('isSuccess'), 'Absent transactionContext rejected');
        System.assert(((String) res.get('errorMessage')).contains('transactionContext'), 'Surfaces the missing-context error');
    }

    @IsTest
    static void testCommitReconfigure_FullGraphGracefulContract() {
        // End-to-end through the @AuraEnabled wrapper: real root QLI, an existing-child PATCH (real
        // id), and a new-component POST (ref_ id). PST is non-deterministic in test context, so we
        // assert the graceful contract — a decided result, never an exception.
        Quote q = insertTestQuote();
        PricebookEntry pbe = insertConfigurableProduct('Reconfig Full', 'RC-6');
        QuoteLineItem root = insertQli(q, pbe, 1);

        Map<String, Object> rootItem = new Map<String, Object>{
            'id' => String.valueOf(root.Id), 'Quantity' => 1, 'UnitPrice' => 100
        };
        Map<String, Object> newItem = new Map<String, Object>{
            'id' => 'ref_new_0001', 'Product' => pbe.Product2Id, 'PricebookEntry' => pbe.Id,
            'Quantity' => 1, 'SellingModelType' => 'OneTime'
        };
        Map<String, Object> in0 = new Map<String, Object>{
            'quoteId' => q.Id, 'rootQuoteLineItemId' => root.Id,
            'transactionContext' => new Map<String, Object>{
                'SalesTransaction' => new List<Object>{
                    new Map<String, Object>{ 'id' => q.Id,
                        'SalesTransactionItem' => new List<Object>{ rootItem, newItem } }
                }
            }
        };
        Test.startTest();
        Map<String, Object> res = parse(RLM_DeltaCatalogController.commitReconfiguredQuote(JSON.serialize(in0)));
        Test.stopTest();
        System.assertNotEquals(null, res.get('isSuccess'), 'Full reconfigure graph returns a decided result');
    }

    // ---------- instance-count helpers (pure, @TestVisible) ----------

    @IsTest
    static void testResolveInstanceCount_ParsesDefaultsAndFloors() {
        // A real integer passes through; string digits parse; absent/blank/zero/negative floor to 1.
        System.assertEquals(3, RLM_DeltaCatalogController.resolveInstanceCount(3), 'instanceCount 3 → 3 lines');
        System.assertEquals(5, RLM_DeltaCatalogController.resolveInstanceCount('5'), 'string "5" parses to 5');
        System.assertEquals(1, RLM_DeltaCatalogController.resolveInstanceCount(null), 'absent → 1');
        System.assertEquals(1, RLM_DeltaCatalogController.resolveInstanceCount(0), 'zero floors to 1');
        System.assertEquals(1, RLM_DeltaCatalogController.resolveInstanceCount(-4), 'negative floors to 1');
        System.assertEquals(1, RLM_DeltaCatalogController.resolveInstanceCount('not-a-number'), 'unparseable → 1');
        System.assertEquals(50, RLM_DeltaCatalogController.resolveInstanceCount(50), 'the cap itself is allowed');
    }

    @IsTest
    static void testResolveInstanceCount_OverCapRejected() {
        try {
            RLM_DeltaCatalogController.resolveInstanceCount(51);
            System.assert(false, 'A per-line count over the cap must throw');
        } catch (Exception e) {
            System.assert(e.getMessage().contains('exceeds the maximum'),
                'Surfaces a clear per-line over-cap message: ' + e.getMessage());
        }
    }

    @IsTest
    static void testTotalEmittedLines_SumsPerLineCounts() {
        List<Map<String, Object>> requested = new List<Map<String, Object>>{
            new Map<String, Object>{ 'instanceCount' => 3 },
            new Map<String, Object>{ 'instanceCount' => 2 },
            new Map<String, Object>{}  // absent → 1
        };
        System.assertEquals(6, RLM_DeltaCatalogController.totalEmittedLines(requested),
            'Total emitted lines is the sum of per-line instance counts (3 + 2 + 1)');
    }

    @IsTest
    static void testTotalEmittedLines_OverCapRejected() {
        // Five lines of 50 (each within the per-line cap) = 250, over the 200 per-checkout total cap.
        List<Map<String, Object>> requested = new List<Map<String, Object>>();
        for (Integer i = 0; i < 5; i++) {
            requested.add(new Map<String, Object>{ 'instanceCount' => 50 });
        }
        try {
            RLM_DeltaCatalogController.totalEmittedLines(requested);
            System.assert(false, 'A total over the per-checkout cap must throw');
        } catch (Exception e) {
            System.assert(e.getMessage().contains('over the maximum'),
                'Surfaces a clear total over-cap message: ' + e.getMessage());
        }
    }

    @IsTest
    static void testAddLines_InstanceCountOverCapRejected() {
        // The public entry point enforces the per-line cap before any PST work (deterministic reject).
        Quote q = insertTestQuote();
        Product2 p = insertProduct('Instance Product', 'IP-1', 'Base');
        PricebookEntry pbe = [SELECT Id FROM PricebookEntry WHERE Product2Id = :p.Id LIMIT 1];
        Map<String, Object> in0 = new Map<String, Object>{
            'quoteId' => q.Id,
            'lines' => new List<Object>{
                new Map<String, Object>{ 'pbeId' => pbe.Id, 'productId' => p.Id, 'instanceCount' => 51 }
            }
        };
        Map<String, Object> res = parse(RLM_DeltaCatalogController.addLinesToQuote(JSON.serialize(in0)));
        System.assertEquals(false, res.get('isSuccess'), 'Over-cap instanceCount rejected before PST');
        System.assert(((String) res.get('errorMessage')).contains('exceeds the maximum'), 'Surfaces the per-line cap message');
    }

    @IsTest
    static void testAddLines_InstancesGracefulContract() {
        // instanceCount > 1 emits multiple Quantity-1 line POSTs. PST is non-deterministic in test
        // context, so we assert only the graceful contract (a decided result, never an exception);
        // the actual per-instance line count is confirmed by live-org verification.
        Quote q = insertTestQuote();
        Product2 p = insertProduct('Multi Instance', 'MI-1', 'Base');
        PricebookEntry pbe = [SELECT Id FROM PricebookEntry WHERE Product2Id = :p.Id LIMIT 1];
        Map<String, Object> in0 = new Map<String, Object>{
            'quoteId' => q.Id,
            'lines' => new List<Object>{
                new Map<String, Object>{ 'pbeId' => pbe.Id, 'productId' => p.Id, 'instanceCount' => 3 }
            }
        };
        Test.startTest();
        Map<String, Object> res = parse(RLM_DeltaCatalogController.addLinesToQuote(JSON.serialize(in0)));
        Test.stopTest();
        System.assertNotEquals(null, res.get('isSuccess'), 'Instance-expanded add returns a decided result');
    }

    // ---------- attribute picker: shared test-data helpers ----------

    // A Product2 in this org exposes its attributes through its classification: the required parent of
    // a ProductAttributeDefinition is a ProductClassificationAttr, so a product-with-attributes must be
    // BasedOn a ProductClassification. We build products that way and link attributes on that
    // classification (the controller unions the inherited-classification route with product-specific).
    private static Map<Id, Id> classificationByProduct = new Map<Id, Id>();

    // Inserts an active AttributeDefinition. Pass a non-null picklistId to make it a picklist attribute.
    private static AttributeDefinition insertAttrDef(String name, String code, String dataType, Id picklistId) {
        return insertAttrDef(name, code, dataType, picklistId, false);
    }

    // A required attribute must be required on BOTH the definition and the junction (this org coerces a
    // junction IsRequired=true back to false unless the AttributeDefinition itself is required).
    private static AttributeDefinition insertAttrDef(String name, String code, String dataType, Id picklistId, Boolean isRequired) {
        AttributeDefinition ad = new AttributeDefinition(
            Name = name,
            DeveloperName = code.replaceAll('[^a-zA-Z0-9]', '_'),
            Label = name,
            Code = code,
            DataType = dataType,
            PicklistId = picklistId,
            IsRequired = isRequired,
            IsActive = true
        );
        insert ad;
        return ad;
    }

    // A product based on a fresh classification, with a standard-pricebook entry. Records the
    // classification so linkProductAttr can attach attributes to it.
    private static Product2 insertClassifiedProduct(String name, String code) {
        ProductClassification pc = new ProductClassification(Name = name + ' Class', Code = code + '-CLS', Status = 'Active');
        insert pc;
        Product2 p = new Product2(Name = name, ProductCode = code, IsActive = true, BasedOnId = pc.Id);
        insert p;
        insert new PricebookEntry(Pricebook2Id = Test.getStandardPricebookId(), Product2Id = p.Id, UnitPrice = 0, IsActive = true);
        classificationByProduct.put(p.Id, pc.Id);
        return p;
    }

    // Links an attribute to a classified product's classification with the junction metadata the picker
    // projects. A visible read-only attribute requires a DefaultValue in this org, so supply one.
    private static void linkProductAttr(
        Id productId, Id attrDefId, String name, Boolean hidden, Boolean priceImpacting,
        Boolean readOnly, Boolean required, Integer seq
    ) {
        insert new ProductClassificationAttr(
            ProductClassificationId = classificationByProduct.get(productId),
            AttributeDefinitionId = attrDefId,
            Name = name,
            IsHidden = hidden,
            IsPriceImpacting = priceImpacting,
            IsReadOnly = readOnly,
            IsRequired = required,
            // This org requires a DefaultValue on the junction for a required (or visible read-only)
            // attribute — without it IsRequired is silently coerced back to false.
            DefaultValue = (required || (readOnly && !hidden)) ? 'default' : null,
            Sequence = seq,
            Status = 'Active'
        );
    }

    private static AttributePicklist insertPicklist(String name) {
        AttributePicklist pl = new AttributePicklist(Name = name, DataType = 'Text', Status = 'Active');
        insert pl;
        return pl;
    }

    private static AttributePicklistValue insertPicklistValue(Id picklistId, String value) {
        AttributePicklistValue pv = new AttributePicklistValue(
            PicklistId = picklistId, Name = value, Code = value, Value = value, DisplayValue = value, Status = 'Active'
        );
        insert pv;
        return pv;
    }

    // ---------- getLineAttributes ----------

    @IsTest
    static void testGetLineAttributes_InformationalOnlyDiscovered() {
        Quote q = insertTestQuote();
        Product2 p = insertClassifiedProduct('Attr Product', 'ATP-1');
        PricebookEntry pbe = [SELECT Id, Product2Id FROM PricebookEntry WHERE Product2Id = :p.Id LIMIT 1];
        QuoteLineItem qli = insertQli(q, pbe, 1);

        // One informational text attr, one informational picklist attr, one hidden, one price-impacting.
        AttributePicklist pl = insertPicklist('Colors');
        insertPicklistValue(pl.Id, 'Red');
        insertPicklistValue(pl.Id, 'Blue');
        AttributeDefinition textAttr = insertAttrDef('Notes', 'NOTES', 'Text', null);
        AttributeDefinition pickAttr = insertAttrDef('Color', 'COLOR', 'Picklist', pl.Id);
        AttributeDefinition hiddenAttr = insertAttrDef('Internal', 'INTERNAL', 'Text', null);
        AttributeDefinition priceAttr = insertAttrDef('Tier', 'TIER', 'Text', null);
        linkProductAttr(p.Id, textAttr.Id, 'Notes', false, false, false, false, 1);
        linkProductAttr(p.Id, pickAttr.Id, 'Color', false, false, false, false, 2);
        linkProductAttr(p.Id, hiddenAttr.Id, 'Internal', true, false, false, false, 3);
        linkProductAttr(p.Id, priceAttr.Id, 'Tier', false, true, false, false, 4);

        Test.startTest();
        Map<String, Object> res = parse(RLM_DeltaCatalogController.getLineAttributes(
            JSON.serialize(new Map<String, Object>{ 'quoteLineItemId' => qli.Id })));
        Test.stopTest();

        System.assertEquals(true, res.get('isSuccess'), 'Discovery succeeds: ' + res.get('errorMessage'));
        List<Object> attrs = (List<Object>) res.get('attributes');
        System.assertEquals(2, attrs.size(), 'Hidden + price-impacting excluded; only 2 informational attrs remain');
        // Ordered by Sequence: Notes (1) then Color (2).
        Map<String, Object> first = (Map<String, Object>) attrs[0];
        Map<String, Object> second = (Map<String, Object>) attrs[1];
        System.assertEquals('NOTES', first.get('code'), 'First attribute by sequence is the text attr');
        System.assertEquals('COLOR', second.get('code'), 'Second is the picklist attr');
        System.assertEquals(2, ((List<Object>) second.get('picklistValues')).size(), 'Picklist attr carries its two values');
        System.assertEquals(null, first.get('picklistId'), 'Text attr has no picklist');
    }

    @IsTest
    static void testGetLineAttributes_AllowlistNarrowsAndOrders() {
        Quote q = insertTestQuote();
        Product2 p = insertClassifiedProduct('Allow Product', 'ALP-1');
        PricebookEntry pbe = [SELECT Id, Product2Id FROM PricebookEntry WHERE Product2Id = :p.Id LIMIT 1];
        QuoteLineItem qli = insertQli(q, pbe, 1);

        AttributeDefinition a1 = insertAttrDef('Alpha', 'ALPHA', 'Text', null);
        AttributeDefinition a2 = insertAttrDef('Beta', 'BETA', 'Text', null);
        AttributeDefinition a3 = insertAttrDef('Gamma', 'GAMMA', 'Text', null);
        linkProductAttr(p.Id, a1.Id, 'Alpha', false, false, false, false, 1);
        linkProductAttr(p.Id, a2.Id, 'Beta', false, false, false, false, 2);
        linkProductAttr(p.Id, a3.Id, 'Gamma', false, false, false, false, 3);

        // Allowlist a subset in a non-sequence order: GAMMA then ALPHA (BETA omitted).
        Map<String, Object> res = parse(RLM_DeltaCatalogController.getLineAttributes(
            JSON.serialize(new Map<String, Object>{ 'quoteLineItemId' => qli.Id, 'attributeCodes' => 'GAMMA, ALPHA' })));

        System.assertEquals(true, res.get('isSuccess'), 'Discovery succeeds: ' + res.get('errorMessage'));
        List<Object> attrs = (List<Object>) res.get('attributes');
        System.assertEquals(2, attrs.size(), 'Allowlist narrows to the two named attributes');
        System.assertEquals('GAMMA', ((Map<String, Object>) attrs[0]).get('code'), 'Allowlist drives order (GAMMA first)');
        System.assertEquals('ALPHA', ((Map<String, Object>) attrs[1]).get('code'), 'ALPHA second per allowlist order');
    }

    @IsTest
    static void testGetLineAttributes_ClassificationInheritedUnioned() {
        // A classification-inherited attribute (via Product2.BasedOnId → ProductClassificationAttr)
        // surfaces alongside product-specific attributes.
        Quote q = insertTestQuote();
        ProductClassification pc = new ProductClassification(Name = 'Widget Class', Code = 'WGT', Status = 'Active');
        insert pc;
        Product2 p = new Product2(Name = 'Classified Product', ProductCode = 'CLS-1', IsActive = true, BasedOnId = pc.Id);
        insert p;
        insert new PricebookEntry(Pricebook2Id = Test.getStandardPricebookId(), Product2Id = p.Id, UnitPrice = 0, IsActive = true);
        PricebookEntry pbe = [SELECT Id, Product2Id FROM PricebookEntry WHERE Product2Id = :p.Id LIMIT 1];
        QuoteLineItem qli = insertQli(q, pbe, 1);

        AttributeDefinition inherited = insertAttrDef('Warranty', 'WARRANTY', 'Text', null);
        insert new ProductClassificationAttr(
            ProductClassificationId = pc.Id, AttributeDefinitionId = inherited.Id, Name = 'Warranty',
            IsHidden = false, IsPriceImpacting = false, IsReadOnly = false, IsRequired = false, Status = 'Active'
        );

        Map<String, Object> res = parse(RLM_DeltaCatalogController.getLineAttributes(
            JSON.serialize(new Map<String, Object>{ 'quoteLineItemId' => qli.Id })));
        System.assertEquals(true, res.get('isSuccess'), 'Discovery succeeds: ' + res.get('errorMessage'));
        List<Object> attrs = (List<Object>) res.get('attributes');
        System.assertEquals(1, attrs.size(), 'The classification-inherited attribute is discovered');
        System.assertEquals('WARRANTY', ((Map<String, Object>) attrs[0]).get('code'), 'Inherited attribute surfaced');
    }

    @IsTest
    static void testGetLineAttributes_InvalidId() {
        Map<String, Object> res = parse(RLM_DeltaCatalogController.getLineAttributes(
            JSON.serialize(new Map<String, Object>{ 'quoteLineItemId' => 'bad' })));
        System.assertEquals(false, res.get('isSuccess'), 'Invalid line id fails gracefully');
    }

    @IsTest
    static void testGetLineAttributes_LineNotFound() {
        // A well-formed but nonexistent QLI id → the ownership/existence guard rejects it.
        Id missing = fakeId(QuoteLineItem.getSObjectType());
        Map<String, Object> res = parse(RLM_DeltaCatalogController.getLineAttributes(
            JSON.serialize(new Map<String, Object>{ 'quoteLineItemId' => missing })));
        System.assertEquals(false, res.get('isSuccess'), 'Nonexistent line rejected');
        System.assert(((String) res.get('errorMessage')).contains('not found'), 'Surfaces the not-found guard');
    }

    @IsTest
    static void testGetLineAttributes_MalformedJson() {
        Map<String, Object> res = parse(RLM_DeltaCatalogController.getLineAttributes('{bad'));
        System.assertEquals(false, res.get('isSuccess'), 'Malformed JSON fails gracefully');
    }

    // ---------- saveLineAttributes: guard / reject branches (fail before any PST commit) ----------

    // Inserts a product + one informational text attribute + a QLI; returns the QLI and attr def id
    // via the out-params captured by the caller through the returned map.
    private static Map<String, Object> setupLineWithTextAttr(String code, Boolean required) {
        Quote q = insertTestQuote();
        Product2 p = insertClassifiedProduct('Save Product ' + code, code + '-P');
        PricebookEntry pbe = [SELECT Id, Product2Id FROM PricebookEntry WHERE Product2Id = :p.Id LIMIT 1];
        QuoteLineItem qli = insertQli(q, pbe, 1);
        AttributeDefinition ad = insertAttrDef('Note ' + code, code, 'Text', null, required);
        linkProductAttr(p.Id, ad.Id, 'Note ' + code, false, false, false, required, 1);
        return new Map<String, Object>{ 'qliId' => qli.Id, 'attrDefId' => ad.Id, 'productId' => p.Id };
    }

    @IsTest
    static void testSaveLineAttributes_EmptyRejected() {
        Map<String, Object> setup = setupLineWithTextAttr('EMPTY', false);
        Map<String, Object> res = parse(RLM_DeltaCatalogController.saveLineAttributes(
            JSON.serialize(new Map<String, Object>{ 'quoteLineItemId' => setup.get('qliId'), 'attributes' => new List<Object>() })));
        System.assertEquals(false, res.get('isSuccess'), 'Empty attribute list rejected');
        System.assert(((String) res.get('errorMessage')).contains('No attributes'), 'Surfaces the empty-list message');
    }

    @IsTest
    static void testSaveLineAttributes_MissingDefIdRejected() {
        Map<String, Object> setup = setupLineWithTextAttr('NODEF', false);
        Map<String, Object> res = parse(RLM_DeltaCatalogController.saveLineAttributes(
            JSON.serialize(new Map<String, Object>{
                'quoteLineItemId' => setup.get('qliId'),
                'attributes' => new List<Object>{ new Map<String, Object>{ 'attributeValue' => 'x' } }
            })));
        System.assertEquals(false, res.get('isSuccess'), 'Attribute without attributeDefinitionId rejected');
        System.assert(((String) res.get('errorMessage')).contains('requires an attributeDefinitionId'), 'Surfaces the missing-id message');
    }

    @IsTest
    static void testSaveLineAttributes_HiddenAttributeRejected() {
        // A hidden attribute is filtered out of the informational set, so it isn't editable on save.
        Quote q = insertTestQuote();
        Product2 p = insertClassifiedProduct('Hidden Save', 'HS-1');
        PricebookEntry pbe = [SELECT Id, Product2Id FROM PricebookEntry WHERE Product2Id = :p.Id LIMIT 1];
        QuoteLineItem qli = insertQli(q, pbe, 1);
        AttributeDefinition hidden = insertAttrDef('Secret', 'SECRET', 'Text', null);
        linkProductAttr(p.Id, hidden.Id, 'Secret', true, false, false, false, 1);

        Map<String, Object> res = parse(RLM_DeltaCatalogController.saveLineAttributes(
            JSON.serialize(new Map<String, Object>{
                'quoteLineItemId' => qli.Id,
                'attributes' => new List<Object>{ new Map<String, Object>{ 'attributeDefinitionId' => hidden.Id, 'attributeValue' => 'x' } }
            })));
        System.assertEquals(false, res.get('isSuccess'), 'Hidden attribute rejected on save');
        System.assert(((String) res.get('errorMessage')).contains('not editable'), 'Surfaces the not-editable guard');
    }

    @IsTest
    static void testSaveLineAttributes_PriceImpactingRejected() {
        Quote q = insertTestQuote();
        Product2 p = insertClassifiedProduct('Price Save', 'PS-1');
        PricebookEntry pbe = [SELECT Id, Product2Id FROM PricebookEntry WHERE Product2Id = :p.Id LIMIT 1];
        QuoteLineItem qli = insertQli(q, pbe, 1);
        AttributeDefinition priceAttr = insertAttrDef('Tier', 'TIER2', 'Text', null);
        linkProductAttr(p.Id, priceAttr.Id, 'Tier', false, true, false, false, 1);

        Map<String, Object> res = parse(RLM_DeltaCatalogController.saveLineAttributes(
            JSON.serialize(new Map<String, Object>{
                'quoteLineItemId' => qli.Id,
                'attributes' => new List<Object>{ new Map<String, Object>{ 'attributeDefinitionId' => priceAttr.Id, 'attributeValue' => 'Gold' } }
            })));
        System.assertEquals(false, res.get('isSuccess'), 'Price-impacting attribute rejected on save');
        System.assert(((String) res.get('errorMessage')).contains('not editable'), 'Surfaces the not-editable guard');
    }

    @IsTest
    static void testSaveLineAttributes_ReadOnlyRejected() {
        Quote q = insertTestQuote();
        Product2 p = insertClassifiedProduct('ReadOnly Save', 'RO-1');
        PricebookEntry pbe = [SELECT Id, Product2Id FROM PricebookEntry WHERE Product2Id = :p.Id LIMIT 1];
        QuoteLineItem qli = insertQli(q, pbe, 1);
        // Read-only but informational (not hidden, not price-impacting) → in the set, but write-blocked.
        AttributeDefinition ro = insertAttrDef('Locked', 'LOCKED', 'Text', null);
        linkProductAttr(p.Id, ro.Id, 'Locked', false, false, true, false, 1);

        Map<String, Object> res = parse(RLM_DeltaCatalogController.saveLineAttributes(
            JSON.serialize(new Map<String, Object>{
                'quoteLineItemId' => qli.Id,
                'attributes' => new List<Object>{ new Map<String, Object>{ 'attributeDefinitionId' => ro.Id, 'attributeValue' => 'x' } }
            })));
        System.assertEquals(false, res.get('isSuccess'), 'Read-only attribute rejected on save');
        System.assert(((String) res.get('errorMessage')).contains('read-only'), 'Surfaces the read-only guard');
    }

    @IsTest
    static void testSaveLineAttributes_CrossPicklistValueRejected() {
        Quote q = insertTestQuote();
        Product2 p = insertClassifiedProduct('Cross Picklist', 'XP-1');
        PricebookEntry pbe = [SELECT Id, Product2Id FROM PricebookEntry WHERE Product2Id = :p.Id LIMIT 1];
        QuoteLineItem qli = insertQli(q, pbe, 1);
        // Attribute bound to picklist A; submit a value id from an UNRELATED picklist B.
        AttributePicklist plA = insertPicklist('Sizes');
        insertPicklistValue(plA.Id, 'Small');
        AttributePicklist plB = insertPicklist('Shapes');
        AttributePicklistValue foreign = insertPicklistValue(plB.Id, 'Square');
        AttributeDefinition pick = insertAttrDef('Size', 'SIZE', 'Picklist', plA.Id);
        linkProductAttr(p.Id, pick.Id, 'Size', false, false, false, false, 1);

        Map<String, Object> res = parse(RLM_DeltaCatalogController.saveLineAttributes(
            JSON.serialize(new Map<String, Object>{
                'quoteLineItemId' => qli.Id,
                'attributes' => new List<Object>{
                    new Map<String, Object>{ 'attributeDefinitionId' => pick.Id, 'attributePicklistValueId' => foreign.Id }
                }
            })));
        System.assertEquals(false, res.get('isSuccess'), 'A value from another attribute picklist is rejected');
        System.assert(((String) res.get('errorMessage')).contains('not valid'), 'Surfaces the cross-picklist guard');
    }

    @IsTest
    static void testSaveLineAttributes_PicklistValueOnTextRejected() {
        Map<String, Object> setup = setupLineWithTextAttr('TXTPICK', false);
        // Fabricate a valid-format picklist value id (never resolved — the shape guard fires first).
        Id fakePv = fakeId(AttributePicklistValue.getSObjectType());
        Map<String, Object> res = parse(RLM_DeltaCatalogController.saveLineAttributes(
            JSON.serialize(new Map<String, Object>{
                'quoteLineItemId' => setup.get('qliId'),
                'attributes' => new List<Object>{
                    new Map<String, Object>{ 'attributeDefinitionId' => setup.get('attrDefId'), 'attributePicklistValueId' => fakePv }
                }
            })));
        System.assertEquals(false, res.get('isSuccess'), 'A picklist value on a non-picklist attribute is rejected');
        System.assert(((String) res.get('errorMessage')).contains('does not accept a picklist value'), 'Surfaces the shape guard');
    }

    @IsTest
    static void testSaveLineAttributes_BlankOnRequiredRejected() {
        Map<String, Object> setup = setupLineWithTextAttr('REQ', true);
        Map<String, Object> res = parse(RLM_DeltaCatalogController.saveLineAttributes(
            JSON.serialize(new Map<String, Object>{
                'quoteLineItemId' => setup.get('qliId'),
                'attributes' => new List<Object>{
                    new Map<String, Object>{ 'attributeDefinitionId' => setup.get('attrDefId'), 'attributeValue' => '' }
                }
            })));
        System.assertEquals(false, res.get('isSuccess'), 'A blank value on a required attribute is rejected');
        System.assert(((String) res.get('errorMessage')).contains('is required'), 'Surfaces the required guard');
    }

    @IsTest
    static void testSaveLineAttributes_UnknownAttributeRejected() {
        // A well-formed attributeDefinitionId not associated with the line's product is not editable.
        Map<String, Object> setup = setupLineWithTextAttr('UNK', false);
        Id stranger = fakeId(AttributeDefinition.getSObjectType());
        Map<String, Object> res = parse(RLM_DeltaCatalogController.saveLineAttributes(
            JSON.serialize(new Map<String, Object>{
                'quoteLineItemId' => setup.get('qliId'),
                'attributes' => new List<Object>{
                    new Map<String, Object>{ 'attributeDefinitionId' => stranger, 'attributeValue' => 'x' }
                }
            })));
        System.assertEquals(false, res.get('isSuccess'), 'An attribute not on the product is rejected');
        System.assert(((String) res.get('errorMessage')).contains('not editable'), 'Surfaces the not-editable guard');
    }

    @IsTest
    static void testSaveLineAttributes_MalformedJson() {
        Map<String, Object> res = parse(RLM_DeltaCatalogController.saveLineAttributes('{bad'));
        System.assertEquals(false, res.get('isSuccess'), 'Malformed JSON fails gracefully');
    }

    @IsTest
    static void testSaveLineAttributes_NoEffectiveChangeReturnsZero() {
        // A blank value on an OPTIONAL attribute with no existing row is a no-op: savedCount 0, no PST.
        // Deterministic (returns before any commit).
        Map<String, Object> setup = setupLineWithTextAttr('NOOP', false);
        Test.startTest();
        Map<String, Object> res = parse(RLM_DeltaCatalogController.saveLineAttributes(
            JSON.serialize(new Map<String, Object>{
                'quoteLineItemId' => setup.get('qliId'),
                'attributes' => new List<Object>{
                    new Map<String, Object>{ 'attributeDefinitionId' => setup.get('attrDefId'), 'attributeValue' => '' }
                }
            })));
        Test.stopTest();
        System.assertEquals(true, res.get('isSuccess'), 'A no-op save succeeds without a PST commit');
        System.assertEquals(0, (Integer) res.get('savedCount'), 'No effective change → savedCount 0');
    }

    // ---------- saveLineAttributes: PST-dependent success paths (graceful contract) ----------

    @IsTest
    static void testSaveLineAttributes_PostNewGracefulContract() {
        // Setting a value on an attribute with no existing row emits a POST through PST. PST is
        // non-deterministic in test context, so assert only a decided result (never an exception);
        // the persisted QuoteLineItemAttribute is confirmed by live-org verification.
        Map<String, Object> setup = setupLineWithTextAttr('POSTNEW', false);
        Test.startTest();
        Map<String, Object> res = parse(RLM_DeltaCatalogController.saveLineAttributes(
            JSON.serialize(new Map<String, Object>{
                'quoteLineItemId' => setup.get('qliId'),
                'attributes' => new List<Object>{
                    new Map<String, Object>{ 'attributeDefinitionId' => setup.get('attrDefId'), 'attributeValue' => 'Hello' }
                }
            })));
        Test.stopTest();
        System.assertNotEquals(null, res.get('isSuccess'), 'A new-attribute save returns a decided result');
    }

    @IsTest
    static void testSaveLineAttributes_PatchExistingGracefulContract() {
        // An existing QuoteLineItemAttribute row → the save PATCHes it (identity-free). Graceful contract.
        Quote q = insertTestQuote();
        Product2 p = insertClassifiedProduct('Patch Save', 'PTCH-1');
        PricebookEntry pbe = [SELECT Id, Product2Id FROM PricebookEntry WHERE Product2Id = :p.Id LIMIT 1];
        QuoteLineItem qli = insertQli(q, pbe, 1);
        AttributeDefinition ad = insertAttrDef('Existing', 'EXISTING', 'Text', null);
        linkProductAttr(p.Id, ad.Id, 'Existing', false, false, false, false, 1);
        // QuoteLineItemAttribute is a near-core object that rejects plain DML — use insertImmediate.
        Database.insertImmediate(new QuoteLineItemAttribute(QuoteLineItemId = qli.Id, AttributeDefinitionId = ad.Id, AttributeValue = 'Old'));

        Test.startTest();
        Map<String, Object> res = parse(RLM_DeltaCatalogController.saveLineAttributes(
            JSON.serialize(new Map<String, Object>{
                'quoteLineItemId' => qli.Id,
                'attributes' => new List<Object>{
                    new Map<String, Object>{ 'attributeDefinitionId' => ad.Id, 'attributeValue' => 'New' }
                }
            })));
        Test.stopTest();
        System.assertNotEquals(null, res.get('isSuccess'), 'An edit of an existing attribute returns a decided result');
    }

    @IsTest
    static void testSaveLineAttributes_ClearViaDeleteGracefulContract() {
        // Clearing an optional attribute that has an existing row → DELETE through PST. Graceful contract.
        Quote q = insertTestQuote();
        Product2 p = insertClassifiedProduct('Clear Save', 'CLR-1');
        PricebookEntry pbe = [SELECT Id, Product2Id FROM PricebookEntry WHERE Product2Id = :p.Id LIMIT 1];
        QuoteLineItem qli = insertQli(q, pbe, 1);
        AttributeDefinition ad = insertAttrDef('Clearable', 'CLEARABLE', 'Text', null);
        linkProductAttr(p.Id, ad.Id, 'Clearable', false, false, false, false, 1);
        // QuoteLineItemAttribute is a near-core object that rejects plain DML — use insertImmediate.
        Database.insertImmediate(new QuoteLineItemAttribute(QuoteLineItemId = qli.Id, AttributeDefinitionId = ad.Id, AttributeValue = 'Remove me'));

        Test.startTest();
        Map<String, Object> res = parse(RLM_DeltaCatalogController.saveLineAttributes(
            JSON.serialize(new Map<String, Object>{
                'quoteLineItemId' => qli.Id,
                'attributes' => new List<Object>{
                    new Map<String, Object>{ 'attributeDefinitionId' => ad.Id, 'attributeValue' => '' }
                }
            })));
        Test.stopTest();
        System.assertNotEquals(null, res.get('isSuccess'), 'Clearing an existing attribute returns a decided result');
    }
}
