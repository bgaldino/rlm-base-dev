/**
 * Apex controller for the rlmContractedPricingCatalog LWC — a slim product picker that adds
 * products to a Quote as quote lines (bundle/hierarchy aware) for Contracted Pricing (rate-card)
 * negotiation.
 *
 * House conventions (mirror RLM_SetUpQuoteInvocable):
 *   - @AuraEnabled(cacheable=false) static String method(String inputJson) returning
 *     JSON.serialize(Map<String,Object>); parse the input JSON once inside a try.
 *   - Id.valueOf(...) guarded in try/catch; WITH USER_MODE reads / `as user` (PST) DML.
 *   - No SOQL/DML in loops; aggregate COUNT()/GROUP BY where counts suffice.
 *
 * Adds use Place Sales Transaction (RevSalesTrxn.PlaceSalesTransactionExecutor.execute) so bundles
 * expand and the pricing procedure runs — direct insert QuoteLineItem does neither.
 */
public with sharing class RLM_DeltaCatalogController {
    public class CatalogException extends Exception {}

    private static final Integer DEFAULT_PAGE_SIZE = 50;

    // Instance-count caps for the cart's "one QuoteLineItem per instance" checkout. Bounded to keep
    // a single addLinesToQuote call under PST/graph limits: at most 50 instances of any one product,
    // and at most 200 emitted line POSTs across the whole call.
    @TestVisible
    private static final Integer MAX_INSTANCES_PER_LINE = 50;
    @TestVisible
    private static final Integer MAX_TOTAL_EMITTED_LINES = 200;

    // Product discovery is delegated to a reusable service. @TestVisible so tests can inject a stub
    // (the standard invocable actions can't be meaningfully invoked in a bare test context).
    @TestVisible
    private static RLM_DeltaProductDiscoveryService service = new RLM_DeltaProductDiscoveryService();

    // Selling-model → BillingFrequency map (mirrors RLM_SetUpQuoteInvocable).
    private static final Map<String, String> PRICING_TERM_TO_BILLING_FREQUENCY = new Map<String, String>{
        'Months' => 'Monthly', 'Annual' => 'Annual', 'Quarterly' => 'Quarterly', 'Semi-Annual' => 'Semi-Annual'
    };

    /**
     * Resolve the Quote's pricing context: its Pricebook2Id (falling back to the standard book),
     * AccountId, currency, and the available ProductCatalog list for an optional catalog filter.
     */
    @AuraEnabled(cacheable=false)
    public static String getCatalogContext(String quoteId) {
        try {
            Id qId = parseId(quoteId, 'quoteId');
            Quote q = loadQuote(qId);
            Id pbId = (q.Pricebook2Id != null) ? q.Pricebook2Id : RLM_DeltaCatalogService.resolveStandardPricebook2Id();
            List<Map<String, Object>> catalogs = new List<Map<String, Object>>();
            for (ProductCatalog pc : [SELECT Id, Name, Code FROM ProductCatalog WITH USER_MODE ORDER BY Name LIMIT 200]) {
                catalogs.add(new Map<String, Object>{ 'id' => pc.Id, 'name' => pc.Name, 'code' => pc.Code });
            }
            return JSON.serialize(new Map<String, Object>{
                'pricebook2Id' => pbId,
                'accountId' => q.AccountId,
                'currencyCode' => readCurrency(q),
                'catalogs' => catalogs
            });
        } catch (Exception e) {
            return errorResult(e.getMessage());
        }
    }

    /**
     * Discover products via the native Product Discovery actions and return one row per PBE so
     * distinct selling models are independently selectable. A blank searchTerm browses (getProducts);
     * a non-blank term searches (findProducts). Prices (and their PBEs) come from the discovery
     * response itself — no separate PBE query. Input: { quoteId, searchTerm?, catalogId?, categoryId?,
     * contextDefinition?, displayFields?, pageSize?, cursor? }.
     */
    @AuraEnabled(cacheable=false)
    public static String searchProducts(String inputJson) {
        try {
            Map<String, Object> in0 = parseInput(inputJson);
            RLM_DeltaProductDiscoveryRequest req = buildProductRequest(in0);
            String searchTerm = asString(in0.get('searchTerm'));

            RLM_DeltaProductDiscoveryService.DiscoveryResult result = String.isBlank(searchTerm)
                ? service.browseProducts(req)
                : service.findProducts(req.withSearchTerm(searchTerm.trim()));

            return JSON.serialize(new Map<String, Object>{
                'isSuccess' => true,
                'products' => shapeRows(result.products),
                'cursor' => result.cursor,
                'fields' => requestedFieldNames(in0)
            });
        } catch (Exception e) {
            return errorResult(e.getMessage());
        }
    }

    /**
     * Constraint-rule recommendations for the quote via getRecommendedProducts. Rows are addable
     * through the same path as search. Input: { quoteId, catalogId?, contextDefinition?,
     * displayFields?, pageSize?, cursor? }.
     */
    @AuraEnabled(cacheable=false)
    public static String getRecommendations(String inputJson) {
        try {
            Map<String, Object> in0 = parseInput(inputJson);
            RLM_DeltaProductDiscoveryRequest req = buildProductRequest(in0);
            RLM_DeltaProductDiscoveryService.DiscoveryResult result = service.recommendProducts(req);
            return JSON.serialize(new Map<String, Object>{
                'isSuccess' => true,
                'products' => shapeRows(result.products),
                'cursor' => result.cursor,
                'fields' => requestedFieldNames(in0)
            });
        } catch (Exception e) {
            return errorResult(e.getMessage());
        }
    }

    /**
     * Categories under a catalog for a category picker (qualified categories surfaced).
     * Input: { catalogId, parentCategoryId?, categoryNestLevel?, contextDefinition?, enableQualification? }.
     */
    @AuraEnabled(cacheable=false)
    public static String getProductCategories(String inputJson) {
        try {
            Map<String, Object> in0 = parseInput(inputJson);
            Id catalogId = parseId(asString(in0.get('catalogId')), 'catalogId');
            RLM_DeltaProductDiscoveryRequest req = new RLM_DeltaProductDiscoveryRequest()
                .withCatalog(catalogId)
                .withParentCategory(optionalId(in0.get('parentCategoryId')))
                .withCategoryNestLevel(asInteger(in0.get('categoryNestLevel')))
                .withContextDefinition(asString(in0.get('contextDefinition')))
                .withQualification(asBoolean(in0.get('enableQualification')));
            List<RLM_DeltaProductDiscoveryService.DiscoveredCategory> cats = service.getCategories(req);
            List<Map<String, Object>> rows = new List<Map<String, Object>>();
            for (RLM_DeltaProductDiscoveryService.DiscoveredCategory c : cats) {
                rows.add(new Map<String, Object>{
                    'id' => c.id,
                    'name' => c.name,
                    'parentId' => c.parentId,
                    'isQualified' => c.isQualified,
                    'hasSubCategories' => c.hasSubCategories
                });
            }
            return JSON.serialize(new Map<String, Object>{ 'isSuccess' => true, 'categories' => rows });
        } catch (Exception e) {
            return errorResult(e.getMessage());
        }
    }

    // ---------- discovery delegation helpers ----------

    /** Build a product/recommendation discovery request from the LWC input, scoped to the quote's book. */
    private static RLM_DeltaProductDiscoveryRequest buildProductRequest(Map<String, Object> in0) {
        Id qId = parseId(asString(in0.get('quoteId')), 'quoteId');
        Quote q = loadQuote(qId);
        Id pbId = (q.Pricebook2Id != null) ? q.Pricebook2Id : RLM_DeltaCatalogService.resolveStandardPricebook2Id();
        Integer pageSize = clampPageSize(asInteger(in0.get('pageSize')));
        return new RLM_DeltaProductDiscoveryRequest()
            .forQuote(qId)
            .withPricebook(pbId)
            .withCurrency(readCurrency(q))
            .withCatalog(optionalId(in0.get('catalogId')))
            .withCategory(optionalId(in0.get('categoryId')))
            .withContextDefinition(asString(in0.get('contextDefinition')))
            .withPaging(pageSize, asString(in0.get('cursor')))
            .withDisplayFields(displayFieldsFromInput(in0));
    }

    /**
     * Flatten discovered products into the row shape the LWC consumes: ONE row per product, carrying
     * its selling models as a `sellingModels` list (each { pbeId, productSellingModelId,
     * sellingModelType }). The top-level pbeId / productSellingModelId / sellingModelType mirror the
     * DEFAULT model (the price flagged isDefault, else the first) so the LWC has an initial selection
     * and any consumer reading the flat fields keeps working; the user can switch models per row via
     * the in-row picker. Pure helper (no SObject/DML) — directly unit-testable.
     */
    @TestVisible
    private static List<Map<String, Object>> shapeRows(List<RLM_DeltaProductDiscoveryService.DiscoveredProduct> products) {
        return shapeRows(products, sellingModelLabels(products));
    }

    /**
     * Overload taking a pre-built PSM-Id → display-label map (the ProductSellingModel Name, e.g.
     * "Term Annual" vs "Term Based - Semi-Annual" — the only thing that distinguishes two TermDefined
     * models to an end user). Each sellingModels entry carries that `label`; the picker shows it and
     * keeps pbeId as the value, so the chosen label always maps to the exact PBE/PSM pair.
     */
    @TestVisible
    private static List<Map<String, Object>> shapeRows(
        List<RLM_DeltaProductDiscoveryService.DiscoveredProduct> products,
        Map<Id, String> modelLabelById
    ) {
        List<Map<String, Object>> rows = new List<Map<String, Object>>();
        if (products == null) {
            return rows;
        }
        Map<Id, String> labels = (modelLabelById != null) ? modelLabelById : new Map<Id, String>();
        for (RLM_DeltaProductDiscoveryService.DiscoveredProduct p : products) {
            if (p.prices == null || p.prices.isEmpty()) {
                // No addable PBE on the quote's book — skip rather than show an unusable row.
                continue;
            }
            List<Map<String, Object>> sellingModels = new List<Map<String, Object>>();
            RLM_DeltaProductDiscoveryService.DiscoveredPrice defaultPrice = null;
            for (RLM_DeltaProductDiscoveryService.DiscoveredPrice price : p.prices) {
                sellingModels.add(new Map<String, Object>{
                    'pbeId' => price.pbeId,
                    'productSellingModelId' => price.productSellingModelId,
                    'sellingModelType' => price.sellingModelType,
                    // Authoritative PSM Name; falls back to the type so a label is never blank.
                    'label' => labels.containsKey(price.productSellingModelId)
                        ? labels.get(price.productSellingModelId)
                        : price.sellingModelType
                });
                if (defaultPrice == null || price.isDefault == true) {
                    defaultPrice = price;
                }
            }
            rows.add(new Map<String, Object>{
                'productId' => p.productId,
                'name' => p.name,
                'code' => p.code,
                'family' => p.family,
                'isBundle' => p.isBundle,
                'isConfigurable' => p.isConfigurable,
                'pbeId' => defaultPrice.pbeId,
                'productSellingModelId' => defaultPrice.productSellingModelId,
                'sellingModelType' => defaultPrice.sellingModelType,
                'sellingModels' => sellingModels,
                'fields' => (p.fields == null) ? new Map<String, Object>() : p.fields
            });
        }
        return rows;
    }

    /**
     * ProductSellingModel Id → display Name for every PSM surfaced by discovery, in one query. The
     * Name (e.g. "Term Based - Semi-Annual") is the end-user label that disambiguates models the
     * discovery payload only types as "TermDefined". Absent/blank names fall back at render time.
     */
    private static Map<Id, String> sellingModelLabels(List<RLM_DeltaProductDiscoveryService.DiscoveredProduct> products) {
        Map<Id, String> labelById = new Map<Id, String>();
        if (products == null) {
            return labelById;
        }
        Set<Id> psmIds = new Set<Id>();
        for (RLM_DeltaProductDiscoveryService.DiscoveredProduct p : products) {
            if (p.prices == null) {
                continue;
            }
            for (RLM_DeltaProductDiscoveryService.DiscoveredPrice price : p.prices) {
                if (price.productSellingModelId != null) {
                    psmIds.add(price.productSellingModelId);
                }
            }
        }
        if (psmIds.isEmpty()) {
            return labelById;
        }
        for (ProductSellingModel psm : [
            SELECT Id, Name FROM ProductSellingModel WHERE Id IN :psmIds WITH USER_MODE
        ]) {
            if (String.isNotBlank(psm.Name)) {
                labelById.put(psm.Id, psm.Name);
            }
        }
        return labelById;
    }

    /**
     * Parse the input's displayFields into the object→fields map the request builder expects.
     * Accepts either a nested map ({ Product2: { fields: [...] } } or { Product2: [...] }) or a
     * simple list/CSV of Product2 field names.
     */
    @TestVisible
    private static Map<String, List<String>> displayFieldsFromInput(Map<String, Object> in0) {
        Object raw = in0.get('displayFields');
        Map<String, List<String>> out = new Map<String, List<String>>();
        if (raw == null) {
            return out;
        }
        if (raw instanceof Map<String, Object>) {
            Map<String, Object> byObject = (Map<String, Object>) raw;
            for (String objectName : byObject.keySet()) {
                Object val = byObject.get(objectName);
                List<String> fields = (val instanceof Map<String, Object>)
                    ? toStringList(((Map<String, Object>) val).get('fields'))
                    : toStringList(val);
                if (!fields.isEmpty()) {
                    out.put(objectName, fields);
                }
            }
        } else {
            // A bare list/CSV is treated as Product2 field names.
            List<String> fields = toStringList(raw);
            if (!fields.isEmpty()) {
                out.put('Product2', fields);
            }
        }
        return out;
    }

    /** The flat list of requested field names echoed back so the LWC can render matching columns. */
    private static List<String> requestedFieldNames(Map<String, Object> in0) {
        Map<String, List<String>> byObject = displayFieldsFromInput(in0);
        List<String> names = new List<String>();
        if (byObject.containsKey('Product2')) {
            names.addAll(byObject.get('Product2'));
        }
        return names;
    }

    private static List<String> toStringList(Object raw) {
        List<String> out = new List<String>();
        if (raw instanceof List<Object>) {
            for (Object o : (List<Object>) raw) {
                if (o != null && String.isNotBlank(String.valueOf(o))) {
                    out.add(String.valueOf(o).trim());
                }
            }
        } else if (raw != null && String.isNotBlank(String.valueOf(raw))) {
            for (String s : String.valueOf(raw).split(',')) {
                if (String.isNotBlank(s)) {
                    out.add(s.trim());
                }
            }
        }
        return out;
    }

    /** Existing QuoteLineGroups for the target-group picker. */
    @AuraEnabled(cacheable=false)
    public static String getQuoteGroups(String quoteId) {
        try {
            Id qId = parseId(quoteId, 'quoteId');
            List<Map<String, Object>> groups = new List<Map<String, Object>>();
            for (QuoteLineGroup g : [
                SELECT Id, Name, ParentQuoteLineGroupId
                FROM QuoteLineGroup
                WHERE QuoteId = :qId
                WITH USER_MODE
                ORDER BY SortOrder NULLS LAST, Name
            ]) {
                groups.add(new Map<String, Object>{ 'id' => g.Id, 'name' => g.Name, 'parentId' => g.ParentQuoteLineGroupId });
            }
            return JSON.serialize(new Map<String, Object>{ 'isSuccess' => true, 'groups' => groups });
        } catch (Exception e) {
            return errorResult(e.getMessage());
        }
    }

    /**
     * Resolve the launch payload for the native Primary Product Configurator flow for a single
     * product the user wants to configure-then-add. Input: { quoteId, pbeId, productId?,
     * productSellingModelId? }. The pbeId is an UNTRUSTED selector: it is revalidated against the
     * quote's price book and tamper-checked (claimed product/PSM must match) before use, and the
     * product's identity for the configurability guard + flow resolution is taken from the resolved
     * PBE — never from the client-supplied productId.
     *
     * Returns { isSuccess, flowApiName, configuratorContext } where configuratorContext is the
     * ProductConfig.ConfiguratorContext shape the screen flow expects (transactionId/transactionLineId/
     * parentName/origin/addedNodes). transactionLineId is null and addedNodes carries one synthetic
     * line so the configurator persists the QuoteLineItem on finish (configure-before-add).
     */
    @AuraEnabled(cacheable=false)
    public static String getConfiguratorLaunch(String inputJson) {
        try {
            Map<String, Object> in0 = parseInput(inputJson);
            Id qId = parseId(asString(in0.get('quoteId')), 'quoteId');
            Quote q = loadQuote(qId);
            Id pbId = (q.Pricebook2Id != null) ? q.Pricebook2Id : RLM_DeltaCatalogService.resolveStandardPricebook2Id();

            Id pbeId = parseId(asString(in0.get('pbeId')), 'pbeId');

            // Validate the PBE against the quote's book FIRST, then derive identity from it. Reading
            // the product's config fields here means the guard/flow resolution trust the PBE, not the
            // client-supplied productId.
            List<PricebookEntry> pbes = [
                SELECT Id, Product2Id, ProductSellingModelId, UnitPrice,
                       ProductSellingModel.SellingModelType,
                       ProductSellingModel.PricingTerm, ProductSellingModel.PricingTermUnit,
                       Product2.Name, Product2.ProductCode, Product2.ConfigureDuringSale, Product2.BasedOnId
                FROM PricebookEntry
                WHERE Id = :pbeId AND Pricebook2Id = :pbId AND IsActive = true AND Product2.IsActive = true
                WITH USER_MODE
                LIMIT 1
            ];
            if (pbes.isEmpty()) {
                return errorResult('Price book entry is not valid for this quote\'s price book.');
            }
            PricebookEntry pbe = pbes[0];

            // Tamper guard: claimed product / selling model must match the resolved PBE.
            Id claimedProduct = optionalId(in0.get('productId'));
            if (claimedProduct != null && claimedProduct != pbe.Product2Id) {
                return errorResult('Product does not match the selected price book entry.');
            }
            Id claimedPsm = optionalId(in0.get('productSellingModelId'));
            if (claimedPsm != null && claimedPsm != pbe.ProductSellingModelId) {
                return errorResult('Selling model does not match the selected price book entry.');
            }

            // Configurability guard (server-side authority; the LWC disabled icon is UX only).
            if (pbe.Product2.ConfigureDuringSale != 'Allowed') {
                return errorResult('This product is not configurable.');
            }

            String flowApiName = resolveConfiguratorFlowApiName(pbe.Product2Id, pbe.Product2.BasedOnId);
            if (String.isBlank(flowApiName)) {
                return errorResult('No product configurator flow is assigned for this product.');
            }

            // Configure-before-add: the configurator needs a synthetic line to anchor the root
            // product. The platform generates a synthetic id (ref_<uuid>) and sets BOTH the node's
            // id AND the context's transactionLineId to it — a null transactionLineId yields
            // "Transaction Line ID is missing input" and an empty configurator. The node's
            // salesTransactionItemSource carries the same id (Quote-path contract).
            String syntheticId = generateSyntheticLineId();
            Decimal unitPrice = (pbe.UnitPrice != null) ? pbe.UnitPrice : 0;
            // Flat ProductConfig__SalesTransactionItem shape (camelCase fields per the configurator
            // data-types contract). The Flow runtime coerces this by field name.
            Map<String, Object> syntheticNode = new Map<String, Object>{
                'id' => syntheticId,
                'salesTransactionItemSource' => syntheticId,
                'pricebookEntry' => pbe.Id,
                'productSellingModel' => pbe.ProductSellingModelId,
                'sellingModelType' => (pbe.ProductSellingModel != null) ? pbe.ProductSellingModel.SellingModelType : null,
                'unitPrice' => unitPrice,
                'quantity' => 1,
                'product' => pbe.Product2Id,
                'productCode' => pbe.Product2.ProductCode,
                'productName' => pbe.Product2.Name,
                'productBasedOn' => (pbe.Product2.BasedOnId != null) ? String.valueOf(pbe.Product2.BasedOnId) : null,
                'businessObjectType' => 'QuoteLineItem'
            };
            // Term fields for the in-configurator "Update Prices" pricing procedure: a TermDefined
            // root needs subscriptionTerm + pricingTermUnit, else pricing fails "Specify either the
            // end date or add the Subscription Term and subscription term unit parameters." These two
            // are the ONLY term/date fields on ProductConfig__SalesTransactionItem (it has no
            // start/end date field); seed them from the PSM. (A prior regression — empty configurator,
            // "Transaction Line ID is missing input" — came from adding fields NOT on this data type,
            // which made the Flow runtime reject the whole node; only these two are valid.)
            String launchSellingModelType = (pbe.ProductSellingModel != null) ? String.valueOf(pbe.ProductSellingModel.SellingModelType) : null;
            if ('TermDefined' == launchSellingModelType && pbe.ProductSellingModel != null) {
                if (pbe.ProductSellingModel.PricingTerm != null) {
                    syntheticNode.put('subscriptionTerm', pbe.ProductSellingModel.PricingTerm);
                }
                if (pbe.ProductSellingModel.PricingTermUnit != null) {
                    syntheticNode.put('pricingTermUnit', String.valueOf(pbe.ProductSellingModel.PricingTermUnit));
                }
            }
            Map<String, Object> configuratorContext = new Map<String, Object>{
                'transactionId' => String.valueOf(qId),
                'transactionLineId' => syntheticId,
                'parentName' => q.Name,
                'origin' => 'Quote',
                'addedNodes' => new List<Object>{ syntheticNode }
            };
            // Debug: the on-load launch payload (the context we hand <lightning-flow> to render the
            // configurator). Pairs with the inbound-save context + PST graph logs for the full trace.
            System.debug(LoggingLevel.INFO, 'getConfiguratorLaunch on-load configuratorContext = ' + JSON.serialize(configuratorContext));
            return JSON.serialize(new Map<String, Object>{
                'isSuccess' => true,
                'flowApiName' => flowApiName,
                'configuratorContext' => configuratorContext
            });
        } catch (Exception e) {
            return errorResult(e.getMessage());
        }
    }

    /**
     * Commit a configured product (the bundle/attribute tree the Product Configurator built) to the
     * quote. The configurator's `save` event hands the host a fully-expanded, fully-priced
     * `transactionContext` whose items still carry synthetic ref_ ids — it does NOT persist by
     * itself (the OOTB record-page container does that; a standalone flow host must). We translate
     * that tree into a PST graph and commit it with configuration SKIP (the tree is already
     * expanded — re-expanding would discard the user's attribute/component choices) and pricing
     * FORCE (so totals recompute server-side).
     *
     * Input: { quoteId, transactionContext: <the save event's detail.transactionContext> }.
     * The client-sent quoteId is revalidated against the context's own SalesTransaction id.
     */
    @AuraEnabled(cacheable=false)
    public static String commitConfiguredQuote(String inputJson) {
        try {
            Map<String, Object> in0 = parseInput(inputJson);
            Id qId = parseId(asString(in0.get('quoteId')), 'quoteId');
            loadQuote(qId); // access + existence check

            Object ctxObj = in0.get('transactionContext');
            if (!(ctxObj instanceof Map<String, Object>)) {
                return errorResult('transactionContext is required.');
            }
            Map<String, Object> ctx = (Map<String, Object>) ctxObj;
            // Debug: the full configurator-supplied context (the SalesTransaction tree we translate).
            // Pairs with the PST graph logged by RLM_DeltaPlaceSalesTransaction for a complete picture.
            System.debug(LoggingLevel.INFO, 'commitConfiguredQuote inbound transactionContext = ' + JSON.serialize(ctx));
            List<Object> sts = asList(ctx.get('SalesTransaction'));
            if (sts == null || sts.isEmpty()) {
                return errorResult('No sales transaction was returned by the configurator.');
            }
            Map<String, Object> st = (Map<String, Object>) sts[0];

            // Guard: the configured transaction must be THIS quote (the context echoes the real id).
            Id ctxQuoteId = optionalId(st.get('id'));
            if (ctxQuoteId != null && ctxQuoteId != qId) {
                return errorResult('The configured transaction does not match this quote.');
            }

            List<Object> items = asList(st.get('SalesTransactionItem'));
            if (items == null || items.isEmpty()) {
                return errorResult('The configured product has no lines to add.');
            }

            String quoteIdRef = String.valueOf(qId);
            List<RevSalesTrxn.RecordWithReferenceRequest> records =
                new List<RevSalesTrxn.RecordWithReferenceRequest>();
            // Quote header PATCH anchors the graph (matches the add path).
            records.add(RLM_DeltaPlaceSalesTransaction.patch('refHeader', Quote.getSObjectType(), qId, new Map<String, Object>()));

            // Map each configured item's synthetic ref_ id → a stable graph ref token so child lines,
            // attributes and relationships can point at their parent within the same graph.
            Map<String, String> refByItemId = new Map<String, String>();
            Integer idx = 0;
            for (Object o : items) {
                Map<String, Object> item = (Map<String, Object>) o;
                String itemId = asString(item.get('id'));
                if (String.isNotBlank(itemId) && !refByItemId.containsKey(itemId)) {
                    refByItemId.put(itemId, 'refLine' + idx);
                    idx++;
                }
            }

            // One QuoteLineItem POST per configured item, parent links resolved to graph refs.
            Integer attrIdx = 0;
            Integer relIdx = 0;
            for (Object o : items) {
                Map<String, Object> item = (Map<String, Object>) o;
                String itemId = asString(item.get('id'));
                String lineRef = refByItemId.get(itemId);
                if (String.isBlank(lineRef)) {
                    continue;
                }
                records.add(RLM_DeltaPlaceSalesTransaction.post(
                    lineRef, QuoteLineItem.getSObjectType(),
                    buildConfiguredLineFields(item, quoteIdRef)
                ));

                // QuoteLineItemAttribute children (configured attribute values, e.g. OS / core count).
                for (Object ao : nestedList(item, 'SalesTransactionItemAttribute')) {
                    Map<String, Object> attr = (Map<String, Object>) ao;
                    records.add(RLM_DeltaPlaceSalesTransaction.post(
                        'refAttr' + attrIdx, QuoteLineItemAttribute.getSObjectType(),
                        buildAttributeFields(attr, lineRef)
                    ));
                    attrIdx++;
                }
                // QuoteLineRelationship children (bundle component linkage to the root/main item).
                for (Object ro : nestedList(item, 'SalesTrxnItemRelationship')) {
                    Map<String, Object> rel = (Map<String, Object>) ro;
                    Map<String, Object> relFields = buildRelationshipFields(rel, refByItemId);
                    if (relFields != null) {
                        records.add(RLM_DeltaPlaceSalesTransaction.post(
                            'refRel' + relIdx, QuoteLineRelationship.getSObjectType(), relFields
                        ));
                        relIdx++;
                    }
                }
            }

            RLM_DeltaPlaceSalesTransaction.Result res =
                RLM_DeltaPlaceSalesTransaction.commitConfigured('ContractedPricingConfigurator', records);
            if (!res.isSuccess) {
                return errorResult(res.errorMessage);
            }
            return JSON.serialize(new Map<String, Object>{
                'isSuccess' => true,
                'addedCount' => refByItemId.size(),
                'errorMessage' => null
            });
        } catch (Exception e) {
            return errorResult(e.getMessage());
        }
    }

    /**
     * Resolve the launch payload to RE-configure an already-added bundle line in place. Input:
     * { quoteLineItemId }. Unlike getConfiguratorLaunch (configure-before-add, which seeds a
     * synthetic node), this HYDRATES the configurator from the persisted bundle tree: it points the
     * flow at the real root QuoteLineItem via transactionLineId and sends NO addedNodes, so the
     * configurator's Data Manager loads the existing components/attributes for editing.
     *
     * Returns { isSuccess, flowApiName, configuratorContext, rootQuoteLineItemId, quoteId } so the
     * LWC can pass rootQuoteLineItemId + quoteId straight into commitReconfiguredQuote — the commit's
     * reconciliation must know the bundle root authoritatively (it is NOT reliably derivable from the
     * returned tree, whose root id may be omitted/reshaped).
     *
     * NOTE (Phase 0 / Spike A): the exact hydrating context shape is unverified by dry-run. This is
     * the first hypothesis (real transactionLineId, no addedNodes); confirm against a live org and
     * adjust here if a seed addedNodes entry carrying the real root id is required instead.
     */
    @AuraEnabled(cacheable=false)
    public static String getReconfigureLaunch(String inputJson) {
        try {
            Map<String, Object> in0 = parseInput(inputJson);
            Id qliId = parseId(asString(in0.get('quoteLineItemId')), 'quoteLineItemId');

            // WITH USER_MODE enforces the clicked line belongs to an accessible quote.
            List<QuoteLineItem> clicked = [
                SELECT Id, QuoteId, Quote.Name, Product2Id,
                       Product2.ConfigureDuringSale, Product2.BasedOnId
                FROM QuoteLineItem
                WHERE Id = :qliId
                WITH USER_MODE
                LIMIT 1
            ];
            if (clicked.isEmpty()) {
                return errorResult('Quote line not found or not accessible.');
            }

            // Root resolution: the clicked line may be a bundle child — reconfigure from the root.
            Id rootQliId = resolveBundleRootQuoteLineId(qliId);
            QuoteLineItem rootLine = clicked[0];
            if (rootQliId != rootLine.Id) {
                List<QuoteLineItem> roots = [
                    SELECT Id, QuoteId, Quote.Name, Product2Id,
                           Product2.ConfigureDuringSale, Product2.BasedOnId
                    FROM QuoteLineItem
                    WHERE Id = :rootQliId
                    WITH USER_MODE
                    LIMIT 1
                ];
                if (roots.isEmpty()) {
                    return errorResult('Bundle root line not found or not accessible.');
                }
                rootLine = roots[0];
            }

            // ConfigureDuringSale guard on the ROOT product (server-side authority).
            if (rootLine.Product2 == null || rootLine.Product2.ConfigureDuringSale != 'Allowed') {
                return errorResult('This product is not configurable.');
            }

            String flowApiName = resolveConfiguratorFlowApiName(rootLine.Product2Id, rootLine.Product2.BasedOnId);
            if (String.isBlank(flowApiName)) {
                return errorResult('No product configurator flow is assigned for this product.');
            }

            Id qId = rootLine.QuoteId;
            // Hydration context (Spike A, first hypothesis): real transactionLineId, NO addedNodes.
            Map<String, Object> configuratorContext = new Map<String, Object>{
                'transactionId' => String.valueOf(qId),
                'transactionLineId' => String.valueOf(rootLine.Id),
                'parentName' => (rootLine.Quote != null) ? rootLine.Quote.Name : null,
                'origin' => 'Quote'
            };
            System.debug(LoggingLevel.INFO, 'getReconfigureLaunch on-load configuratorContext = ' + JSON.serialize(configuratorContext));
            return JSON.serialize(new Map<String, Object>{
                'isSuccess' => true,
                'flowApiName' => flowApiName,
                'configuratorContext' => configuratorContext,
                'rootQuoteLineItemId' => String.valueOf(rootLine.Id),
                'quoteId' => String.valueOf(qId)
            });
        } catch (Exception e) {
            return errorResult(e.getMessage());
        }
    }

    /**
     * Walk a clicked QuoteLineItem up to its bundle root. A bundle component carries a
     * QuoteLineRelationship whose AssociatedQuoteLineId is the component and RootQuoteLineId is the
     * bundle root; when the clicked line is itself the root (or a standalone line), no such row
     * exists and the line is its own root. RootQuoteLineId already points at the ultimate root, so
     * no iterative walk is needed.
     */
    @TestVisible
    private static Id resolveBundleRootQuoteLineId(Id qliId) {
        for (QuoteLineRelationship r : [
            SELECT RootQuoteLineId
            FROM QuoteLineRelationship
            WHERE AssociatedQuoteLineId = :qliId AND RootQuoteLineId != null
            WITH USER_MODE
            LIMIT 1
        ]) {
            if (r.RootQuoteLineId != null) {
                return r.RootQuoteLineId;
            }
        }
        return qliId;
    }

    /**
     * Commit a RE-configured bundle tree back to the quote. Input:
     * { quoteId, rootQuoteLineItemId, transactionContext }. Returns
     * { isSuccess, addedCount, updatedCount, deletedCount, errorMessage }.
     *
     * The configurator's Save & Exit hands back the FULL surviving tree (live-confirmed Spike B):
     * pre-existing lines/attributes/relationships carry their REAL ids; newly-added ones carry
     * synthetic ref_ ids; REMOVED ones are simply ABSENT (no delete marker). So this method:
     *   - PATCHes each returned item with a real QuoteLineItem id (mutable fields only — never
     *     identity, see buildReconfiguredLinePatchFields),
     *   - POSTs each item with a synthetic ref_ id (a genuinely new component),
     *   - reconciles the returned desired set against the persisted bundle subtree and DELETEs the
     *     lines/attributes/relationships that are gone.
     * All three verbs ride one PST graph committed with configuration SKIP (the tree is already
     * expanded; config FORCE would re-expand and duplicate components) + pricing FORCE (totals
     * recompute over the final state). The validated root is the reconciliation anchor and is never
     * emitted as a DELETE.
     */
    @AuraEnabled(cacheable=false)
    public static String commitReconfiguredQuote(String inputJson) {
        try {
            Map<String, Object> in0 = parseInput(inputJson);
            Id qId = parseId(asString(in0.get('quoteId')), 'quoteId');
            Id rootQliId = parseId(asString(in0.get('rootQuoteLineItemId')), 'rootQuoteLineItemId');
            loadQuote(qId); // access + existence

            // Contract guard: the root must be a QuoteLineItem on THIS quote. Anchors reconciliation
            // and is protected from deletion below.
            List<QuoteLineItem> roots = [
                SELECT Id FROM QuoteLineItem WHERE Id = :rootQliId AND QuoteId = :qId WITH USER_MODE LIMIT 1
            ];
            if (roots.isEmpty()) {
                return errorResult('The bundle root line does not belong to this quote.');
            }

            Object ctxObj = in0.get('transactionContext');
            if (!(ctxObj instanceof Map<String, Object>)) {
                return errorResult('transactionContext is required.');
            }
            Map<String, Object> ctx = (Map<String, Object>) ctxObj;
            System.debug(LoggingLevel.INFO, 'commitReconfiguredQuote inbound transactionContext = ' + JSON.serialize(ctx));

            // Guard: the configured transaction must be THIS quote (the context echoes the real id).
            List<Object> sts = asList(ctx.get('SalesTransaction'));
            if (sts == null || sts.isEmpty()) {
                return errorResult('No sales transaction was returned by the configurator.');
            }
            Id ctxQuoteId = optionalId(((Map<String, Object>) sts[0]).get('id'));
            if (ctxQuoteId != null && ctxQuoteId != qId) {
                return errorResult('The configured transaction does not match this quote.');
            }

            // Load the persisted bundle subtree under the validated root (root included independently,
            // not only via the relationship walk) so reconciliation can detect removed records.
            Set<Id> persistedLineIds = new Set<Id>{ rootQliId };
            Set<Id> persistedRelIds = new Set<Id>();
            for (QuoteLineRelationship r : [
                SELECT Id, AssociatedQuoteLineId
                FROM QuoteLineRelationship
                WHERE RootQuoteLineId = :rootQliId
                WITH USER_MODE
            ]) {
                persistedRelIds.add(r.Id);
                if (r.AssociatedQuoteLineId != null) {
                    persistedLineIds.add(r.AssociatedQuoteLineId);
                }
            }
            Set<Id> persistedAttrIds = new Set<Id>();
            for (QuoteLineItemAttribute a : [
                SELECT Id FROM QuoteLineItemAttribute WHERE QuoteLineItemId IN :persistedLineIds WITH USER_MODE
            ]) {
                persistedAttrIds.add(a.Id);
            }

            ReconcileResult plan = buildReconfigureGraph(
                qId, rootQliId, ctx, persistedLineIds, persistedAttrIds, persistedRelIds
            );

            RLM_DeltaPlaceSalesTransaction.Result res =
                RLM_DeltaPlaceSalesTransaction.commitConfigured('ContractedPricingReconfigure', plan.records);
            if (!res.isSuccess) {
                return errorResult(res.errorMessage);
            }
            return JSON.serialize(new Map<String, Object>{
                'isSuccess' => true,
                'addedCount' => plan.addedCount,
                'updatedCount' => plan.updatedCount,
                'deletedCount' => plan.deletedCount,
                'errorMessage' => null
            });
        } catch (Exception e) {
            return errorResult(e.getMessage());
        }
    }

    /** The assembled reconfigure graph plus reconciliation sets — returned by buildReconfigureGraph so unit tests can assert on it without invoking PST. */
    @TestVisible
    private class ReconcileResult {
        @TestVisible List<RevSalesTrxn.RecordWithReferenceRequest> records;
        @TestVisible Integer addedCount = 0;
        @TestVisible Integer updatedCount = 0;
        @TestVisible Integer deletedCount = 0;
        @TestVisible Set<Id> removedLineIds = new Set<Id>();
        @TestVisible Set<Id> removedAttrIds = new Set<Id>();
        @TestVisible Set<Id> removedRelIds = new Set<Id>();
        ReconcileResult() {
            this.records = new List<RevSalesTrxn.RecordWithReferenceRequest>();
        }
    }

    /**
     * Pure graph assembler for the reconfigure commit (no SOQL/DML — the persisted-subtree sets are
     * passed in so this is unit-testable). Classifies each returned item by id shape (real
     * QuoteLineItem id → PATCH, synthetic ref_ → POST), parents attributes/relationships to their
     * line (real id directly, new line via a graph token), and reconciles the returned desired set
     * against the persisted subtree to emit DELETE nodes — ordered dependency-safe child → parent
     * (QuoteLineRelationship → QuoteLineItemAttribute → descendant QuoteLineItem). The root is the
     * anchor and is never a DELETE candidate.
     */
    @TestVisible
    private static ReconcileResult buildReconfigureGraph(
        Id qId, Id rootQliId, Map<String, Object> ctx,
        Set<Id> persistedLineIds, Set<Id> persistedAttrIds, Set<Id> persistedRelIds
    ) {
        ReconcileResult out = new ReconcileResult();
        String qliPrefix = QuoteLineItem.getSObjectType().getDescribe().getKeyPrefix();
        String quoteIdRef = String.valueOf(qId);

        List<Object> sts = asList(ctx.get('SalesTransaction'));
        Map<String, Object> st = (sts != null && !sts.isEmpty()) ? (Map<String, Object>) sts[0] : null;
        List<Object> items = (st != null) ? nestedList(st, 'SalesTransactionItem') : new List<Object>();

        // Quote header PATCH anchors the graph (matches the add/configure paths).
        out.records.add(RLM_DeltaPlaceSalesTransaction.patch('refHeader', Quote.getSObjectType(), qId, new Map<String, Object>()));

        // Pass 1 — assign a parent reference for every item: its REAL id (PATCH lines) or a graph
        // token (POST/new lines), so children resolve their parent regardless of verb. Also collect
        // the desired real-id sets for reconciliation.
        Map<String, String> parentRefByItemId = new Map<String, String>();
        Map<String, String> postRefNameByItemId = new Map<String, String>();
        Set<Id> desiredLineIds = new Set<Id>{ rootQliId };
        Set<Id> desiredAttrIds = new Set<Id>();
        Set<Id> desiredRelIds = new Set<Id>();
        Integer postIdx = 0;
        for (Object o : items) {
            Map<String, Object> item = (Map<String, Object>) o;
            String itemId = asString(item.get('id'));
            if (String.isBlank(itemId) || parentRefByItemId.containsKey(itemId)) {
                continue;
            }
            if (isRealQuoteLineId(itemId, qliPrefix)) {
                parentRefByItemId.put(itemId, itemId); // reference an existing line by its real id
                desiredLineIds.add(Id.valueOf(itemId));
            } else {
                String name = 'refLine' + postIdx;
                postIdx++;
                postRefNameByItemId.put(itemId, name);
                parentRefByItemId.put(itemId, RLM_DeltaPlaceSalesTransaction.referenceToken(name));
            }
        }

        // Pass 2 — one PATCH or POST per item, then its attribute/relationship children.
        Integer patchIdx = 0;
        Integer attrIdx = 0;
        Integer relIdx = 0;
        for (Object o : items) {
            Map<String, Object> item = (Map<String, Object>) o;
            String itemId = asString(item.get('id'));
            if (String.isBlank(itemId)) {
                continue;
            }
            String parentRef = parentRefByItemId.get(itemId);
            Boolean isReal = isRealQuoteLineId(itemId, qliPrefix);
            if (isReal) {
                out.records.add(RLM_DeltaPlaceSalesTransaction.patch(
                    'refPatch' + patchIdx, QuoteLineItem.getSObjectType(), Id.valueOf(itemId),
                    buildReconfiguredLinePatchFields(item)
                ));
                patchIdx++;
                out.updatedCount++;
            } else {
                out.records.add(RLM_DeltaPlaceSalesTransaction.post(
                    postRefNameByItemId.get(itemId), QuoteLineItem.getSObjectType(),
                    buildConfiguredLineFields(item, quoteIdRef)
                ));
                out.addedCount++;
            }

            // Attributes: real id → PATCH (mutable value only); synthetic/blank → POST under the line.
            for (Object ao : nestedList(item, 'SalesTransactionItemAttribute')) {
                Map<String, Object> attr = (Map<String, Object>) ao;
                String attrId = asString(attr.get('id'));
                if (isRealQuoteLineId(attrId, null)) {
                    desiredAttrIds.add(Id.valueOf(attrId));
                    out.records.add(RLM_DeltaPlaceSalesTransaction.patch(
                        'refAttr' + attrIdx, QuoteLineItemAttribute.getSObjectType(), Id.valueOf(attrId),
                        buildReconfiguredAttributePatchFields(attr)
                    ));
                } else {
                    out.records.add(RLM_DeltaPlaceSalesTransaction.post(
                        'refAttr' + attrIdx, QuoteLineItemAttribute.getSObjectType(),
                        buildReconfigureAttributePostFields(attr, parentRef)
                    ));
                }
                attrIdx++;
            }

            // Relationships: real id → existing structural link, keep (track as desired). Synthetic →
            // POST the new component's linkage. Relationships have no user-mutable payload to PATCH.
            for (Object ro : nestedList(item, 'SalesTrxnItemRelationship')) {
                Map<String, Object> rel = (Map<String, Object>) ro;
                String relId = asString(rel.get('id'));
                if (isRealQuoteLineId(relId, null)) {
                    desiredRelIds.add(Id.valueOf(relId));
                    continue;
                }
                Map<String, Object> relFields = buildReconfigureRelationshipFields(rel, parentRefByItemId);
                if (relFields != null) {
                    out.records.add(RLM_DeltaPlaceSalesTransaction.post(
                        'refRel' + relIdx, QuoteLineRelationship.getSObjectType(), relFields
                    ));
                    relIdx++;
                }
            }
        }

        // Reconcile: persisted − desired = removed. Root is protected (excluded from line removals).
        out.removedRelIds = setMinus(persistedRelIds, desiredRelIds);
        out.removedAttrIds = setMinus(persistedAttrIds, desiredAttrIds);
        out.removedLineIds = setMinus(persistedLineIds, desiredLineIds);
        out.removedLineIds.remove(rootQliId);

        // Emit DELETEs child → parent: relationships, then attributes, then descendant lines.
        Integer delIdx = 0;
        for (Id relId : out.removedRelIds) {
            out.records.add(RLM_DeltaPlaceSalesTransaction.del('refDel' + delIdx, QuoteLineRelationship.getSObjectType(), relId));
            delIdx++;
        }
        for (Id attrId : out.removedAttrIds) {
            out.records.add(RLM_DeltaPlaceSalesTransaction.del('refDel' + delIdx, QuoteLineItemAttribute.getSObjectType(), attrId));
            delIdx++;
        }
        for (Id lineId : out.removedLineIds) {
            out.records.add(RLM_DeltaPlaceSalesTransaction.del('refDel' + delIdx, QuoteLineItem.getSObjectType(), lineId));
            delIdx++;
        }
        out.deletedCount = out.removedLineIds.size();
        return out;
    }

    /** True when raw is a parseable Id; when keyPrefix is non-null, also requires the prefix to match. */
    private static Boolean isRealQuoteLineId(String raw, String keyPrefix) {
        if (String.isBlank(raw)) {
            return false;
        }
        try {
            Id parsed = Id.valueOf(raw);
            return String.isBlank(keyPrefix) || String.valueOf(parsed).startsWith(keyPrefix);
        } catch (Exception e) {
            return false;
        }
    }

    private static Set<Id> setMinus(Set<Id> a, Set<Id> b) {
        Set<Id> out = new Set<Id>(a);
        out.removeAll(b);
        return out;
    }

    /**
     * Identity-free PATCH field map for an existing reconfigured line: ONLY mutable / configurator-
     * computed fields. Never QuoteId / Product2Id / PricebookEntryId — re-identifying or reparenting
     * an existing line is invalid. Subscription fields are carried through from the configurator's
     * own returned values (config SKIP derives nothing, so the skill's error ladder applies to PATCH
     * too); putIfPresent leaves OneTime lines untouched.
     */
    @TestVisible
    private static Map<String, Object> buildReconfiguredLinePatchFields(Map<String, Object> item) {
        Map<String, Object> f = new Map<String, Object>();
        Decimal qty = asDecimal(item.get('Quantity'));
        if (qty != null && qty > 0) {
            f.put('Quantity', qty);
        }
        putIfPresent(f, 'UnitPrice', item.get('UnitPrice'));
        // Carry the configurator's OWN subscription values (PSM-consistent) rather than re-deriving.
        putIfPresent(f, 'StartDate', item.get('StartDate'));
        putIfPresent(f, 'EndDate', item.get('EndDate'));
        putIfPresent(f, 'SubscriptionTerm', item.get('SubscriptionTerm'));
        putIfPresent(f, 'BillingFrequency', item.get('BillingFrequency'));
        putIfPresent(f, 'PeriodBoundary', item.get('PeriodBoundary'));
        return f;
    }

    /** Identity-free PATCH for an existing attribute: only the editable selected value (never AttributeDefinitionId / QuoteLineItemId). */
    private static Map<String, Object> buildReconfiguredAttributePatchFields(Map<String, Object> attr) {
        Map<String, Object> f = new Map<String, Object>();
        putIfPresent(f, 'AttributePicklistValueId', attr.get('AttributePicklistValue'));
        putIfPresent(f, 'AttributeValue', attr.get('AttributeValue'));
        return f;
    }

    /** POST field map for a NEW attribute parented to its line (parentRef = real id or graph token). */
    private static Map<String, Object> buildReconfigureAttributePostFields(Map<String, Object> attr, String parentRef) {
        Map<String, Object> f = new Map<String, Object>{ 'QuoteLineItemId' => parentRef };
        putIfPresent(f, 'AttributeDefinitionId', attr.get('AttributeKey'));
        putIfPresent(f, 'AttributePicklistValueId', attr.get('AttributePicklistValue'));
        putIfPresent(f, 'AttributeValue', attr.get('AttributeValue'));
        return f;
    }

    /**
     * POST field map for a NEW QuoteLineRelationship. Item links resolve through parentRefByItemId,
     * whose values are already final references (an existing line's real id, or a @{ref.id} token for
     * a line POSTed in this graph). Returns null when neither end resolves (nothing to relate).
     */
    private static Map<String, Object> buildReconfigureRelationshipFields(Map<String, Object> rel, Map<String, String> parentRefByItemId) {
        String mainRef = parentRefByItemId.get(asString(rel.get('MainItem')));
        String assocRef = parentRefByItemId.get(asString(rel.get('AssociatedItem')));
        String rootRef = parentRefByItemId.get(asString(rel.get('RootItem')));
        if (mainRef == null && assocRef == null) {
            return null;
        }
        Map<String, Object> f = new Map<String, Object>();
        if (mainRef != null) { f.put('MainQuoteLineId', mainRef); }
        if (assocRef != null) { f.put('AssociatedQuoteLineId', assocRef); }
        if (rootRef != null) { f.put('RootQuoteLineId', rootRef); }
        // Translate the configurator-returned type to the runtime bundle-component type. A dynamic
        // classification slot (fare) carries the design-time "Bundle to Product Classification
        // Component Relationship" (AssociatedProductRoleCat = ClassificationComponent), which has no
        // OrderItemRelationship role and blocks quote→order conversion. translateRuntimeRelationshipTypeId
        // maps a classification (or absent) type to bundle-component and passes any other type through.
        Id runtimePrtId = RLM_DeltaCatalogService.translateRuntimeRelationshipTypeId(
            optionalId(rel.get('ProductRelationshipType'))
        );
        if (runtimePrtId != null) {
            f.put('ProductRelationshipTypeId', runtimePrtId);
        }
        putIfPresent(f, 'ProductRelatedComponentId', rel.get('ProductRelatedComponent'));
        putIfPresent(f, 'AssociatedQuoteLinePricing', rel.get('AssociatedItemPricing'));
        return f;
    }

    /**
     * Translate one configurator SalesTransactionItem (camelCase configurator-domain fields) into a
     * QuoteLineItem field map (SObject API names). Parent links (group, item parent) resolve to
     * graph ref tokens when they point at another configured item. Excludes attribute/relationship
     * children, which are emitted as their own graph records.
     */
    private static Map<String, Object> buildConfiguredLineFields(Map<String, Object> item, String quoteIdRef) {
        Map<String, Object> f = new Map<String, Object>{ 'QuoteId' => quoteIdRef };
        putIfPresent(f, 'Product2Id', item.get('Product'));
        putIfPresent(f, 'PricebookEntryId', item.get('PricebookEntry'));
        Decimal qty = asDecimal(item.get('Quantity'));
        f.put('Quantity', (qty != null && qty > 0) ? qty : 1);
        putIfPresent(f, 'UnitPrice', item.get('UnitPrice'));

        // Subscription lines: set the date/term/billing fields EXPLICITLY from the configurator item
        // (config-step derivation via FORCE did not reliably populate them — lines still failed
        // END_DATE_MISSING). Setting EndDate clears END_DATE_MISSING; BillingFrequency from the item's
        // OWN value (already PSM-consistent) clears the "can't be null" rule without tripping the
        // "add a Billing Treatment" override guard. SubscriptionTerm is carried through as a second
        // anchor for the pricing procedure.
        // We pass through the values the configurator ALREADY computed for each subscription line
        // (it returned them fully populated — confirmed in the repricing trigger log: StartDate,
        // EndDate, BillingFrequency, PeriodBoundary=Anniversary, SubscriptionTerm). Under config SKIP
        // the platform does NOT re-derive these, so faithfully carrying the configurator's own
        // computed values — rather than re-deriving or hand-guessing — is what keeps each line valid.
        // PeriodBoundary is required for subscription lines (INVALID_PERIOD_BOUNDARY otherwise: one of
        // AlignToCalendar / Anniversary / DayOfPeriod / LastDayOfPeriod); honor the inbound value and
        // fall back to Anniversary, the value the configurator itself assigned to these lines.
        String sellingModelType = asString(item.get('SellingModelType'));
        String itemBillingFrequency = asString(item.get('BillingFrequency'));
        String itemPeriodBoundary = asString(item.get('PeriodBoundary'));
        if ('TermDefined' == sellingModelType) {
            f.put('StartDate', subscriptionStartDateIso());
            f.put('EndDate', subscriptionEndDateIso());
            putIfPresent(f, 'SubscriptionTerm', item.get('SubscriptionTerm'));
            putIfPresent(f, 'BillingFrequency', itemBillingFrequency);
            f.put('PeriodBoundary', String.isNotBlank(itemPeriodBoundary) ? itemPeriodBoundary : 'Anniversary');
        } else if ('Evergreen' == sellingModelType) {
            f.put('StartDate', subscriptionStartDateIso());
            putIfPresent(f, 'BillingFrequency', itemBillingFrequency);
            f.put('PeriodBoundary', String.isNotBlank(itemPeriodBoundary) ? itemPeriodBoundary : 'Anniversary');
        }
        return f;
    }

    /** Configurator QuoteLineItemAttribute → SObject field map, parented to its line's graph ref. */
    private static Map<String, Object> buildAttributeFields(Map<String, Object> attr, String lineRef) {
        Map<String, Object> f = new Map<String, Object>{
            'QuoteLineItemId' => RLM_DeltaPlaceSalesTransaction.referenceToken(lineRef)
        };
        putIfPresent(f, 'AttributeDefinitionId', attr.get('AttributeKey'));
        putIfPresent(f, 'AttributePicklistValueId', attr.get('AttributePicklistValue'));
        putIfPresent(f, 'AttributeValue', attr.get('AttributeValue'));
        return f;
    }

    /**
     * Configurator SalesTrxnItemRelationship → QuoteLineRelationship field map. Item links resolve
     * to graph ref tokens for items created in this graph; returns null when neither end maps to a
     * known item (nothing to relate).
     */
    private static Map<String, Object> buildRelationshipFields(Map<String, Object> rel, Map<String, String> refByItemId) {
        String mainRef = graphRefFor(rel.get('MainItem'), refByItemId);
        String assocRef = graphRefFor(rel.get('AssociatedItem'), refByItemId);
        String rootRef = graphRefFor(rel.get('RootItem'), refByItemId);
        if (mainRef == null && assocRef == null) {
            return null;
        }
        Map<String, Object> f = new Map<String, Object>();
        if (mainRef != null) { f.put('MainQuoteLineId', mainRef); }
        if (assocRef != null) { f.put('AssociatedQuoteLineId', assocRef); }
        if (rootRef != null) { f.put('RootQuoteLineId', rootRef); }
        // Translate the configurator-returned type to the runtime bundle-component type. A dynamic
        // classification slot (fare) carries the design-time "Bundle to Product Classification
        // Component Relationship" (AssociatedProductRoleCat = ClassificationComponent), which has no
        // OrderItemRelationship role and blocks quote→order conversion. translateRuntimeRelationshipTypeId
        // maps a classification (or absent) type to bundle-component and passes any other type through.
        Id runtimePrtId = RLM_DeltaCatalogService.translateRuntimeRelationshipTypeId(
            optionalId(rel.get('ProductRelationshipType'))
        );
        if (runtimePrtId != null) {
            f.put('ProductRelationshipTypeId', runtimePrtId);
        }
        putIfPresent(f, 'ProductRelatedComponentId', rel.get('ProductRelatedComponent'));
        putIfPresent(f, 'AssociatedQuoteLinePricing', rel.get('AssociatedItemPricing'));
        return f;
    }

    /** Resolve a configurator item id to its graph ref token, or null when it isn't a graph item. */
    private static String graphRefFor(Object rawItemId, Map<String, String> refByItemId) {
        String itemId = asString(rawItemId);
        if (String.isBlank(itemId)) {
            return null;
        }
        String ref = refByItemId.get(itemId);
        return (ref != null) ? RLM_DeltaPlaceSalesTransaction.referenceToken(ref) : null;
    }

    /** Put value only when non-null/non-blank (keeps PST field maps free of explicit nulls). */
    private static void putIfPresent(Map<String, Object> target, String key, Object value) {
        if (value != null && String.isNotBlank(String.valueOf(value))) {
            target.put(key, value);
        }
    }

    private static List<Object> nestedList(Map<String, Object> item, String key) {
        List<Object> l = asList(item.get(key));
        return (l != null) ? l : new List<Object>();
    }

    private static List<Object> asList(Object o) {
        return (o instanceof List<Object>) ? (List<Object>) o : null;
    }

    /**
     * Synthetic transaction-line id for configure-before-add. Mirrors the platform configurator's
     * generateSyntheticId(): a UUID with underscores instead of hyphens, prefixed with "ref_"
     * (e.g. ref_5cfcbd4a_3868_4ae1_b90d_4b08121c2620). The same id anchors the node and the
     * context's transactionLineId so the Configurator API can resolve the root product.
     */
    @TestVisible
    private static String generateSyntheticLineId() {
        return 'ref_' + UUID.randomUUID().toString().replace('-', '_');
    }

    // The managed-package "Default Product Configurator Flow" Salesforce ships with Revenue Cloud.
    // Its stored ApiName is 'ProductConfig' under the runtime_industries_cfg namespace, so the
    // fully-qualified launch reference is runtime_industries_cfg__ProductConfig. This flow is never
    // a ProductConfigurationFlow row (it's package metadata), so it's the ultimate fallback when no
    // explicit assignment and no IsDefault flow resolve. Verified live in jun25_agents.
    @TestVisible
    private static String SHIPPED_DEFAULT_CONFIGURATOR_FLOW = 'runtime_industries_cfg__ProductConfig';

    /**
     * Resolve the Primary Configurator flow API name with precedence: product-level assignment →
     * product-classification assignment → org default (IsDefault) flow → shipped default flow.
     */
    @TestVisible
    private static String resolveConfiguratorFlowApiName(Id productId, Id classificationId) {
        // Product- and classification-level Primary Configurator assignments in one query.
        String productAssigned = null;
        String classificationAssigned = null;
        for (ProductConfigFlowAssignment a : [
            SELECT ProductId, ProductClassificationId,
                   ProductConfigurationFlow.FlowIdentifier, ProductConfigurationFlow.Status
            FROM ProductConfigFlowAssignment
            WHERE AssignmentType = 'PrimaryConfiguratorFlow'
              AND ProductConfigurationFlow.Status = 'Active'
              AND (ProductId = :productId OR ProductClassificationId = :classificationId)
            WITH USER_MODE
        ]) {
            String apiName = (a.ProductConfigurationFlow != null) ? a.ProductConfigurationFlow.FlowIdentifier : null;
            if (String.isBlank(apiName)) {
                continue;
            }
            if (a.ProductId == productId) {
                productAssigned = apiName;
            } else if (classificationId != null && a.ProductClassificationId == classificationId) {
                classificationAssigned = apiName;
            }
        }
        if (String.isNotBlank(productAssigned)) {
            return productAssigned;
        }
        if (String.isNotBlank(classificationAssigned)) {
            return classificationAssigned;
        }
        // Org default flow. ProductConfigurationFlow.IsDefault is the platform's own
        // "default configurator flow" flag — the object-level form of the org-settings default.
        // Salesforce ships a "Default Product Configurator Flow" that admins clone; when that
        // shipped (or a cloned) flow is marked IsDefault, this is the catch-all for products and
        // classifications without an explicit assignment.
        for (ProductConfigurationFlow f : [
            SELECT FlowIdentifier
            FROM ProductConfigurationFlow
            WHERE IsDefault = true AND Status = 'Active'
            WITH USER_MODE
            LIMIT 1
        ]) {
            if (String.isNotBlank(f.FlowIdentifier)) {
                return f.FlowIdentifier;
            }
        }
        // No assignment and no IsDefault row: fall back to the shipped Default Product
        // Configurator Flow, which always exists as package metadata (never a
        // ProductConfigurationFlow row). This guarantees configurable products can always launch.
        return SHIPPED_DEFAULT_CONFIGURATOR_FLOW;
    }

    /**
     * Resolve a line entry's instance count for the cart's one-line-per-instance checkout: parse the
     * optional `instanceCount`, default to 1 when absent/blank/unparseable, floor at 1, and reject a
     * per-line count over MAX_INSTANCES_PER_LINE. Pure (no SOQL/DML/PST) so the count math is
     * unit-testable without a live PST commit. `instanceCount` multiplies the number of emitted
     * QuoteLineItem POSTs; the distinct `quantity` key still sets each emitted line's Quantity.
     */
    @TestVisible
    private static Integer resolveInstanceCount(Object raw) {
        Integer count = asInteger(raw);
        if (count == null || count < 1) {
            count = 1;
        }
        if (count > MAX_INSTANCES_PER_LINE) {
            throw new CatalogException(
                'Instance count ' + count + ' exceeds the maximum of ' + MAX_INSTANCES_PER_LINE + ' per product.'
            );
        }
        return count;
    }

    /**
     * Total QuoteLineItem POSTs a request would emit (sum of per-line instance counts). Rejects a
     * total over MAX_TOTAL_EMITTED_LINES so one checkout stays under PST/graph limits. Pure and
     * @TestVisible for deterministic assertions; also enforces each line's per-line cap via
     * resolveInstanceCount.
     */
    @TestVisible
    private static Integer totalEmittedLines(List<Map<String, Object>> requested) {
        Integer total = 0;
        for (Map<String, Object> line : requested) {
            total += resolveInstanceCount(line.get('instanceCount'));
        }
        if (total > MAX_TOTAL_EMITTED_LINES) {
            throw new CatalogException(
                'This checkout would create ' + total + ' lines, over the maximum of ' + MAX_TOTAL_EMITTED_LINES + ' per checkout.'
            );
        }
        return total;
    }

    /**
     * Add the selected products to the quote as quote lines via Place Sales Transaction.
     * Input: { quoteId, lines:[{ pbeId, productId, productSellingModelId, quantity?, instanceCount?,
     * targetGroupId? }], newGroupName? }. Client-sent pbeId/productId/PSM are an UNTRUSTED selector
     * revalidated server-side against the quote's price book before use. `instanceCount` (cart
     * checkout) emits that many separate Quantity-1 lines for the product; absent → 1 line, so the
     * original catalog (which never sends it) is unaffected. Returns `addedLines` (authoritative
     * pre/post-commit diff), plus the existing `addedCount`/`groupIds`.
     */
    @AuraEnabled(cacheable=false)
    public static String addLinesToQuote(String inputJson) {
        try {
            Map<String, Object> in0 = parseInput(inputJson);
            String quoteId = asString(in0.get('quoteId'));
            Id qId = parseId(quoteId, 'quoteId');
            Quote q = loadQuote(qId);
            Id pbId = (q.Pricebook2Id != null) ? q.Pricebook2Id : RLM_DeltaCatalogService.resolveStandardPricebook2Id();

            List<Object> lineObjs = (in0.get('lines') instanceof List<Object>) ? (List<Object>) in0.get('lines') : null;
            if (lineObjs == null || lineObjs.isEmpty()) {
                throw new CatalogException('Select at least one product to add.');
            }
            String newGroupName = asString(in0.get('newGroupName'));

            // Collect requested selectors.
            List<Map<String, Object>> requested = new List<Map<String, Object>>();
            Set<Id> requestedPbeIds = new Set<Id>();
            Set<Id> requestedProductIds = new Set<Id>();
            Set<Id> requestedGroupIds = new Set<Id>();
            for (Object o : lineObjs) {
                Map<String, Object> line = (Map<String, Object>) o;
                requested.add(line);
                Id pbeId = optionalId(line.get('pbeId'));
                if (pbeId != null) {
                    requestedPbeIds.add(pbeId);
                }
                Id prodId = optionalId(line.get('productId'));
                if (prodId != null) {
                    requestedProductIds.add(prodId);
                }
                Id grpId = optionalId(line.get('targetGroupId'));
                if (grpId != null) {
                    requestedGroupIds.add(grpId);
                }
            }

            // Enforce per-line and total instance caps up front (throws a clear CatalogException over
            // cap) before any expensive query, so a bad request fails fast.
            totalEmittedLines(requested);

            // Revalidate explicit PBEs against the quote's price book (tamper guard).
            Map<Id, PricebookEntry> validPbeById = new Map<Id, PricebookEntry>();
            if (!requestedPbeIds.isEmpty()) {
                for (PricebookEntry pe : [
                    SELECT Id, Product2Id, Pricebook2Id, ProductSellingModelId,
                           UnitPrice, ProductSellingModel.SellingModelType, ProductSellingModel.PricingTermUnit
                    FROM PricebookEntry
                    WHERE Id IN :requestedPbeIds AND Pricebook2Id = :pbId AND IsActive = true AND Product2.IsActive = true
                    WITH USER_MODE
                ]) {
                    validPbeById.put(pe.Id, pe);
                }
            }
            // Deterministic fallback for lines that omit pbeId: resolve by product on the quote's book.
            Map<Id, PricebookEntry> fallbackByProduct = new Map<Id, PricebookEntry>();
            Set<Id> needFallback = new Set<Id>();
            for (Map<String, Object> line : requested) {
                Id pbeId = optionalId(line.get('pbeId'));
                if (pbeId == null) {
                    Id prodId = optionalId(line.get('productId'));
                    if (prodId == null) {
                        throw new CatalogException('Each line requires a pbeId or productId.');
                    }
                    needFallback.add(prodId);
                }
            }
            if (!needFallback.isEmpty()) {
                for (PricebookEntry pe : RLM_DeltaCatalogService.queryPBEsByProductIds(needFallback, pbId)) {
                    PricebookEntry existing = fallbackByProduct.get(pe.Product2Id);
                    if (existing == null || sellingModelRank(pe) < sellingModelRank(existing)) {
                        fallbackByProduct.put(pe.Product2Id, pe);
                    }
                }
            }

            // Validate any explicit target groups belong to this quote.
            Set<Id> validGroupIds = new Set<Id>();
            if (!requestedGroupIds.isEmpty()) {
                for (QuoteLineGroup g : [SELECT Id FROM QuoteLineGroup WHERE QuoteId = :qId AND Id IN :requestedGroupIds WITH USER_MODE]) {
                    validGroupIds.add(g.Id);
                }
            }

            // Build the PST graph: Quote PATCH header, optional new group POST, one line POST per product.
            List<RevSalesTrxn.RecordWithReferenceRequest> records = new List<RevSalesTrxn.RecordWithReferenceRequest>();
            records.add(RLM_DeltaPlaceSalesTransaction.patch('refHeader', Quote.getSObjectType(), qId, new Map<String, Object>()));
            String quoteIdRef = String.valueOf(qId);

            String newGroupRef = null;
            List<String> createdGroupRefs = new List<String>();
            if (String.isNotBlank(newGroupName)) {
                newGroupRef = 'refGrp_0';
                records.add(RLM_DeltaPlaceSalesTransaction.post(
                    newGroupRef, QuoteLineGroup.getSObjectType(),
                    new Map<String, Object>{ 'Name' => newGroupName.trim(), 'QuoteId' => quoteIdRef, 'SortOrder' => 1 }
                ));
                createdGroupRefs.add(newGroupRef);
            }

            Integer lineIndex = 0;
            for (Map<String, Object> line : requested) {
                PricebookEntry pbe = resolveLinePbe(line, validPbeById, fallbackByProduct);
                Decimal qty = asDecimal(line.get('quantity'));
                Id targetGroupId = optionalId(line.get('targetGroupId'));
                String groupRef = null;
                if (String.isNotBlank(newGroupRef)) {
                    groupRef = '@{' + newGroupRef + '.id}';
                } else if (targetGroupId != null) {
                    if (!validGroupIds.contains(targetGroupId)) {
                        throw new CatalogException('Target group ' + targetGroupId + ' does not belong to this quote.');
                    }
                    groupRef = String.valueOf(targetGroupId);
                }
                // Cart checkout: emit one Quantity-1 line POST per requested instance so each instance
                // is an independently-negotiable QuoteLineItem. Absent instanceCount → 1 (the original
                // catalog is unaffected). `qty` still drives each emitted line's Quantity.
                Integer instances = resolveInstanceCount(line.get('instanceCount'));
                for (Integer i = 0; i < instances; i++) {
                    records.add(RLM_DeltaPlaceSalesTransaction.post(
                        'refLine' + lineIndex, QuoteLineItem.getSObjectType(),
                        buildQuoteLineItemFields(pbe, quoteIdRef, groupRef, qty)
                    ));
                    lineIndex++;
                }
            }

            // Snapshot the quote's existing line ids BEFORE commit so the post-commit diff below can
            // authoritatively identify the created lines without relying on the best-effort PST ref
            // map (RLM_DeltaPlaceSalesTransaction.referenceIdMap returns an empty map on any shape mismatch).
            Set<Id> preexisting = new Set<Id>();
            for (QuoteLineItem qli : [SELECT Id FROM QuoteLineItem WHERE QuoteId = :qId WITH USER_MODE]) {
                preexisting.add(qli.Id);
            }

            // Single bundle root + configuration FORCE: PST expands bundle components and prices them.
            RLM_DeltaPlaceSalesTransaction.Result res =
                RLM_DeltaPlaceSalesTransaction.commitWithExpansion('ContractedPricingCatalog', records);
            if (!res.isSuccess) {
                return errorResult(res.errorMessage);
            }

            // Authoritative created-line set: every QuoteLineItem now on the quote that wasn't there
            // before. Shape-independent — returns root + components too if a bundle product expanded
            // on commit (config FORCE), not just the flat 1:1 case. Selects Product2.Name directly
            // (the PBE revalidation query and product fallback don't project it).
            List<Map<String, Object>> addedLines = new List<Map<String, Object>>();
            for (QuoteLineItem qli : [
                SELECT Id, Product2Id, Product2.Name
                FROM QuoteLineItem
                WHERE QuoteId = :qId AND Id NOT IN :preexisting
                WITH USER_MODE
                ORDER BY CreatedDate, Id
            ]) {
                addedLines.add(new Map<String, Object>{
                    'id' => qli.Id,
                    'productId' => qli.Product2Id,
                    'productName' => (qli.Product2 != null) ? qli.Product2.Name : null
                });
            }

            // Resolve any newly-created group ids from the response references.
            List<String> groupIds = resolveCreatedGroupIds(res.referenceIds, createdGroupRefs);
            return JSON.serialize(new Map<String, Object>{
                'isSuccess' => true,
                'addedCount' => lineIndex,
                'addedLines' => addedLines,
                'groupIds' => groupIds,
                'errorMessage' => null
            });
        } catch (Exception e) {
            return errorResult(e.getMessage());
        }
    }

    // ---------- informational attribute picker (rlmLineAttributePicker) ----------

    /**
     * Discover the informational (non-price-impacting) attributes for a persisted quote line and
     * their current values, for the reusable inline attribute picker.
     *
     * Input: { quoteLineItemId, attributeCodes? }. `attributeCodes` is an optional CSV allowlist of
     * AttributeDefinition.Code that narrows AND orders the returned attributes (mirrors the catalog's
     * displayFields); absent → all informational attributes ordered by Sequence.
     *
     * Returns { isSuccess, attributes:[{ attributeDefinitionId, code, label, name, dataType,
     * displayType, picklistId, isRequired, isReadOnly, picklistValues:[{id,label,isDefault}],
     * currentPicklistValueId, currentValue, existingRecordId }], errorMessage }.
     */
    @AuraEnabled(cacheable=false)
    public static String getLineAttributes(String inputJson) {
        try {
            Map<String, Object> in0 = parseInput(inputJson);
            Id qliId = parseId(asString(in0.get('quoteLineItemId')), 'quoteLineItemId');
            String attributeCodes = asString(in0.get('attributeCodes'));

            LineAttributeContext ctx = discoverLineAttributes(qliId, attributeCodes);

            List<Map<String, Object>> attributes = new List<Map<String, Object>>();
            for (AttributeDescriptor d : ctx.descriptors) {
                QuoteLineItemAttribute existing = ctx.existingByDefId.get(d.attributeDefinitionId);
                attributes.add(new Map<String, Object>{
                    'attributeDefinitionId' => d.attributeDefinitionId,
                    'code' => d.code,
                    'label' => d.label,
                    'name' => d.name,
                    'dataType' => d.dataType,
                    'displayType' => d.displayType,
                    'picklistId' => d.picklistId,
                    'isRequired' => d.isRequired,
                    'isReadOnly' => d.isReadOnly,
                    'defaultValue' => d.defaultValue,
                    'picklistValues' => d.picklistValues,
                    'currentPicklistValueId' => (existing != null) ? existing.AttributePicklistValueId : null,
                    'currentValue' => (existing != null) ? existing.AttributeValue : null,
                    'existingRecordId' => (existing != null) ? existing.Id : null
                });
            }
            return JSON.serialize(new Map<String, Object>{
                'isSuccess' => true,
                'attributes' => attributes,
                'errorMessage' => null
            });
        } catch (Exception e) {
            return errorResult(e.getMessage());
        }
    }

    /**
     * Persist chosen informational attribute values on a persisted quote line via Place Sales
     * Transaction (the established QuoteLineItemAttribute write path — no direct DML precedent exists).
     *
     * Input: { quoteLineItemId, attributes:[{ attributeDefinitionId, attributePicklistValueId?,
     * attributeValue? }] }. Every incoming attribute is revalidated server-side against the line's
     * discovered informational attributes (§ getLineAttributes) — the client selector is untrusted:
     *   - the attributeDefinitionId must resolve to an attribute valid for the line's product and
     *     non-hidden / non-price-impacting / non-read-only (else rejected: unknown/hidden/
     *     price-impacting/read-only);
     *   - a picklist attribute accepts only an attributePicklistValueId belonging to THAT attribute's
     *     picklist (cross-picklist values rejected); a non-picklist attribute rejects any
     *     attributePicklistValueId and accepts only attributeValue;
     *   - a blank value on a required attribute is rejected.
     * A present value → PATCH the existing QuoteLineItemAttribute (identity-free) or POST a new one;
     * a blank value on an optional attribute with an existing row → DELETE it (putIfPresent makes a
     * blank PATCH a no-op, so clearing must delete). Committed pricing FORCE + config SKIP.
     *
     * Returns { isSuccess, savedCount, errorMessage }.
     */
    @AuraEnabled(cacheable=false)
    public static String saveLineAttributes(String inputJson) {
        try {
            Map<String, Object> in0 = parseInput(inputJson);
            Id qliId = parseId(asString(in0.get('quoteLineItemId')), 'quoteLineItemId');
            List<Object> attrObjs = (in0.get('attributes') instanceof List<Object>) ? (List<Object>) in0.get('attributes') : null;
            if (attrObjs == null || attrObjs.isEmpty()) {
                throw new CatalogException('No attributes to save.');
            }

            // Discovery is the source of truth for eligibility + value validation (no allowlist here —
            // validate against the full informational set). Loading the line WITH USER_MODE is the
            // implicit ownership guard.
            LineAttributeContext ctx = discoverLineAttributes(qliId, null);
            String lineIdRef = String.valueOf(qliId);

            List<RevSalesTrxn.RecordWithReferenceRequest> records = new List<RevSalesTrxn.RecordWithReferenceRequest>();
            records.add(RLM_DeltaPlaceSalesTransaction.patch('refHeader', Quote.getSObjectType(), ctx.line.QuoteId, new Map<String, Object>()));

            Integer savedCount = 0;
            Integer opIdx = 0;
            for (Object o : attrObjs) {
                Map<String, Object> attr = (Map<String, Object>) o;
                Id defId = optionalId(attr.get('attributeDefinitionId'));
                if (defId == null) {
                    throw new CatalogException('Each attribute requires an attributeDefinitionId.');
                }
                AttributeDescriptor d = ctx.byDefId.get(defId);
                if (d == null) {
                    // Unknown to the informational set: unknown / hidden / price-impacting attribute.
                    throw new CatalogException('Attribute ' + defId + ' is not editable on this line.');
                }
                if (d.isReadOnly == true) {
                    throw new CatalogException('Attribute ' + d.label + ' is read-only.');
                }

                Id picklistValueId = optionalId(attr.get('attributePicklistValueId'));
                String freeValue = asString(attr.get('attributeValue'));
                Boolean isPicklist = (d.picklistId != null);

                if (isPicklist) {
                    // A picklist attribute takes only a picklist value from its OWN picklist.
                    if (picklistValueId != null) {
                        Set<Id> valid = ctx.validValueIdsByPicklist.get(d.picklistId);
                        if (valid == null || !valid.contains(picklistValueId)) {
                            throw new CatalogException('Value is not valid for attribute ' + d.label + '.');
                        }
                    }
                    // Ignore any free-text value on a picklist attribute (the picklist value is authoritative).
                    freeValue = null;
                } else {
                    // A non-picklist attribute rejects any picklist value outright.
                    if (picklistValueId != null) {
                        throw new CatalogException('Attribute ' + d.label + ' does not accept a picklist value.');
                    }
                }

                Boolean hasValue = (picklistValueId != null) || String.isNotBlank(freeValue);
                if (!hasValue && d.isRequired == true) {
                    throw new CatalogException('Attribute ' + d.label + ' is required.');
                }

                QuoteLineItemAttribute existing = ctx.existingByDefId.get(defId);
                if (hasValue) {
                    // Normalize to the configurator-shaped keys the shared PST builders read.
                    Map<String, Object> normalized = new Map<String, Object>{
                        'AttributeKey' => defId,
                        'AttributePicklistValue' => picklistValueId,
                        'AttributeValue' => freeValue
                    };
                    if (existing != null) {
                        records.add(RLM_DeltaPlaceSalesTransaction.patch(
                            'refAttrPatch' + opIdx, QuoteLineItemAttribute.getSObjectType(), existing.Id,
                            buildReconfiguredAttributePatchFields(normalized)
                        ));
                    } else {
                        records.add(RLM_DeltaPlaceSalesTransaction.post(
                            'refAttrPost' + opIdx, QuoteLineItemAttribute.getSObjectType(),
                            buildReconfigureAttributePostFields(normalized, lineIdRef)
                        ));
                    }
                    savedCount++;
                    opIdx++;
                } else if (existing != null) {
                    // Clearing an optional attribute: a blank PATCH is a no-op (putIfPresent), so DELETE.
                    records.add(RLM_DeltaPlaceSalesTransaction.del(
                        'refAttrDel' + opIdx, QuoteLineItemAttribute.getSObjectType(), existing.Id
                    ));
                    savedCount++;
                    opIdx++;
                }
                // else: blank value on an optional attribute with no existing row → nothing to do.
            }

            if (savedCount == 0) {
                // No effective change (all-blank on attributes that were already unset).
                return JSON.serialize(new Map<String, Object>{ 'isSuccess' => true, 'savedCount' => 0, 'errorMessage' => null });
            }

            // Pricing FORCE + configuration SKIP: attributes are non-price-impacting, so this recomputes
            // pricing identically without re-expanding any configured tree (matches the reconfigure path).
            RLM_DeltaPlaceSalesTransaction.Result res =
                RLM_DeltaPlaceSalesTransaction.commitConfigured('ContractedPricingAttributes', records);
            if (!res.isSuccess) {
                return errorResult(res.errorMessage);
            }
            return JSON.serialize(new Map<String, Object>{
                'isSuccess' => true,
                'savedCount' => savedCount,
                'errorMessage' => null
            });
        } catch (Exception e) {
            return errorResult(e.getMessage());
        }
    }

    /** Junction (ProductAttributeDefinition / ProductClassificationAttr) metadata for one attribute. */
    private class JunctionMeta {
        Boolean isHidden = false;
        Boolean isPriceImpacting = false;
        Boolean isReadOnly = false;
        Boolean isRequired = false;
        Integer sequence;
        String displayType;
    }

    /** A discovered informational attribute: junction metadata + AttributeDefinition fields + picklist values. */
    @TestVisible
    private class AttributeDescriptor {
        Id attributeDefinitionId;
        String code;
        String label;
        String name;
        String dataType;
        String displayType;
        Id picklistId;
        Boolean isRequired = false;
        Boolean isReadOnly = false;
        Integer sequence;
        String defaultValue;
        List<Map<String, Object>> picklistValues = new List<Map<String, Object>>();
    }

    /** Discovery result: the line, the ordered informational attributes, and lookup maps for save-time validation. */
    @TestVisible
    private class LineAttributeContext {
        QuoteLineItem line;
        List<AttributeDescriptor> descriptors = new List<AttributeDescriptor>();
        Map<Id, AttributeDescriptor> byDefId = new Map<Id, AttributeDescriptor>();
        Map<Id, Set<Id>> validValueIdsByPicklist = new Map<Id, Set<Id>>();
        Map<Id, QuoteLineItemAttribute> existingByDefId = new Map<Id, QuoteLineItemAttribute>();
    }

    /**
     * Shared discovery for getLineAttributes/saveLineAttributes. Replicates
     * UTIL_ConfigHelper.getProductAttributesForProduct's union (classification-inherited +
     * product-specific attributes) but ALSO projects the junction metadata that class drops
     * (IsHidden/IsPriceImpacting/IsReadOnly/IsRequired/Sequence/DisplayType, which live on the
     * junctions, not AttributeDefinition), filters to informational (non-hidden, non-price-impacting)
     * attributes, applies the optional Code allowlist (narrow + order), joins the active
     * AttributeDefinition, and batch-loads picklist values + existing QuoteLineItemAttributes.
     * All reads WITH USER_MODE; loading the line is the ownership guard.
     */
    private static LineAttributeContext discoverLineAttributes(Id qliId, String attributeCodesCsv) {
        LineAttributeContext ctx = new LineAttributeContext();
        List<QuoteLineItem> lines = [
            SELECT Id, QuoteId, Product2Id, Product2.BasedOnId
            FROM QuoteLineItem WHERE Id = :qliId WITH USER_MODE LIMIT 1
        ];
        if (lines.isEmpty()) {
            throw new CatalogException('Quote line not found or not accessible.');
        }
        ctx.line = lines[0];
        Id product2Id = ctx.line.Product2Id;
        Id basedOnId = (ctx.line.Product2 != null) ? ctx.line.Product2.BasedOnId : null;

        // Union junction metadata: classification-inherited first, then product-specific (which wins).
        Map<Id, JunctionMeta> metaByDefId = new Map<Id, JunctionMeta>();
        if (basedOnId != null) {
            for (ProductClassificationAttr pca : [
                SELECT AttributeDefinitionId, IsHidden, IsPriceImpacting, IsReadOnly, IsRequired, Sequence, DisplayType
                FROM ProductClassificationAttr
                WHERE ProductClassificationId = :basedOnId AND AttributeDefinitionId != null
                WITH USER_MODE
            ]) {
                metaByDefId.put(pca.AttributeDefinitionId, buildJunctionMeta(
                    pca.IsHidden, pca.IsPriceImpacting, pca.IsReadOnly, pca.IsRequired, pca.Sequence, String.valueOf(pca.DisplayType)
                ));
            }
        }
        if (product2Id != null) {
            for (ProductAttributeDefinition pad : [
                SELECT AttributeDefinitionId, IsHidden, IsPriceImpacting, IsReadOnly, IsRequired, Sequence, DisplayType
                FROM ProductAttributeDefinition
                WHERE Product2Id = :product2Id AND AttributeDefinitionId != null
                WITH USER_MODE
            ]) {
                metaByDefId.put(pad.AttributeDefinitionId, buildJunctionMeta(
                    pad.IsHidden, pad.IsPriceImpacting, pad.IsReadOnly, pad.IsRequired, pad.Sequence, String.valueOf(pad.DisplayType)
                ));
            }
        }

        // Filter to informational attributes only (non-hidden AND non-price-impacting).
        Set<Id> informationalDefIds = new Set<Id>();
        for (Id defId : metaByDefId.keySet()) {
            JunctionMeta m = metaByDefId.get(defId);
            if (m.isHidden != true && m.isPriceImpacting != true) {
                informationalDefIds.add(defId);
            }
        }
        if (informationalDefIds.isEmpty()) {
            return ctx;
        }

        // Join the active AttributeDefinition and build descriptors.
        Map<Id, AttributeDescriptor> byDefId = new Map<Id, AttributeDescriptor>();
        Set<Id> picklistIds = new Set<Id>();
        for (AttributeDefinition ad : [
            SELECT Id, Label, Name, Code, DataType, PicklistId, DefaultValue
            FROM AttributeDefinition
            WHERE Id IN :informationalDefIds AND IsActive = true
            WITH USER_MODE
        ]) {
            JunctionMeta m = metaByDefId.get(ad.Id);
            AttributeDescriptor d = new AttributeDescriptor();
            d.attributeDefinitionId = ad.Id;
            d.code = ad.Code;
            d.label = String.isNotBlank(ad.Label) ? ad.Label : ad.Name;
            d.name = ad.Name;
            d.dataType = String.valueOf(ad.DataType);
            d.picklistId = ad.PicklistId;
            d.defaultValue = ad.DefaultValue;
            d.displayType = (m != null) ? m.displayType : null;
            d.isRequired = (m != null && m.isRequired == true);
            d.isReadOnly = (m != null && m.isReadOnly == true);
            d.sequence = (m != null) ? m.sequence : null;
            byDefId.put(ad.Id, d);
            if (ad.PicklistId != null) {
                picklistIds.add(ad.PicklistId);
            }
        }

        // Batch-load picklist values for all referenced picklists in ONE query; build both the
        // per-picklist option lists (for the picker) and the valid-value-id sets (for save-time
        // cross-picklist rejection).
        if (!picklistIds.isEmpty()) {
            Map<Id, List<Map<String, Object>>> valuesByPicklist = new Map<Id, List<Map<String, Object>>>();
            for (AttributePicklistValue pv : [
                SELECT Id, PicklistId, Value, DisplayValue, IsDefault, Sequence
                FROM AttributePicklistValue
                WHERE PicklistId IN :picklistIds AND Status = 'Active'
                WITH USER_MODE
                ORDER BY Sequence NULLS LAST, DisplayValue
            ]) {
                if (!ctx.validValueIdsByPicklist.containsKey(pv.PicklistId)) {
                    ctx.validValueIdsByPicklist.put(pv.PicklistId, new Set<Id>());
                    valuesByPicklist.put(pv.PicklistId, new List<Map<String, Object>>());
                }
                ctx.validValueIdsByPicklist.get(pv.PicklistId).add(pv.Id);
                valuesByPicklist.get(pv.PicklistId).add(new Map<String, Object>{
                    'id' => pv.Id,
                    'label' => String.isNotBlank(pv.DisplayValue) ? pv.DisplayValue : pv.Value,
                    'isDefault' => pv.IsDefault
                });
            }
            for (AttributeDescriptor d : byDefId.values()) {
                if (d.picklistId != null && valuesByPicklist.containsKey(d.picklistId)) {
                    d.picklistValues = valuesByPicklist.get(d.picklistId);
                }
            }
        }

        // Prefill + PATCH-vs-POST source: existing QuoteLineItemAttribute rows for this line, keyed by
        // AttributeDefinitionId (only those in the informational set matter).
        for (QuoteLineItemAttribute qlia : [
            SELECT Id, AttributeDefinitionId, AttributePicklistValueId, AttributeValue
            FROM QuoteLineItemAttribute
            WHERE QuoteLineItemId = :qliId AND AttributeDefinitionId IN :informationalDefIds
            WITH USER_MODE
        ]) {
            ctx.existingByDefId.put(qlia.AttributeDefinitionId, qlia);
        }

        // Order: allowlist order when provided (also narrows), else by Sequence then Label.
        List<String> allowedCodes = parseCsvTokens(attributeCodesCsv);
        if (!allowedCodes.isEmpty()) {
            Map<String, AttributeDescriptor> byCode = new Map<String, AttributeDescriptor>();
            for (AttributeDescriptor d : byDefId.values()) {
                if (String.isNotBlank(d.code)) {
                    byCode.put(d.code.toLowerCase(), d);
                }
            }
            for (String code : allowedCodes) {
                AttributeDescriptor d = byCode.get(code.toLowerCase());
                if (d != null && !ctx.byDefId.containsKey(d.attributeDefinitionId)) {
                    ctx.descriptors.add(d);
                    ctx.byDefId.put(d.attributeDefinitionId, d);
                }
            }
        } else {
            List<AttributeDescriptor> ordered = byDefId.values();
            ordered.sort(new AttributeDescriptorComparator());
            for (AttributeDescriptor d : ordered) {
                ctx.descriptors.add(d);
                ctx.byDefId.put(d.attributeDefinitionId, d);
            }
        }
        return ctx;
    }

    private static JunctionMeta buildJunctionMeta(Boolean isHidden, Boolean isPriceImpacting, Boolean isReadOnly, Boolean isRequired, Decimal sequence, String displayType) {
        JunctionMeta m = new JunctionMeta();
        m.isHidden = (isHidden == true);
        m.isPriceImpacting = (isPriceImpacting == true);
        m.isReadOnly = (isReadOnly == true);
        m.isRequired = (isRequired == true);
        m.sequence = (sequence != null) ? sequence.intValue() : null;
        m.displayType = displayType;
        return m;
    }

    /** Order informational attributes by Sequence (nulls last), then Label, for a stable default order. */
    private class AttributeDescriptorComparator implements Comparator<AttributeDescriptor> {
        public Integer compare(AttributeDescriptor a, AttributeDescriptor b) {
            if (a.sequence != b.sequence) {
                if (a.sequence == null) return 1;
                if (b.sequence == null) return -1;
                return (a.sequence < b.sequence) ? -1 : 1;
            }
            String al = (a.label != null) ? a.label : '';
            String bl = (b.label != null) ? b.label : '';
            return al.compareTo(bl);
        }
    }

    /** Split a CSV allowlist into trimmed, non-blank tokens (order preserved). */
    private static List<String> parseCsvTokens(String csv) {
        List<String> tokens = new List<String>();
        if (String.isBlank(csv)) {
            return tokens;
        }
        for (String raw : csv.split(',')) {
            String t = (raw != null) ? raw.trim() : '';
            if (String.isNotBlank(t)) {
                tokens.add(t);
            }
        }
        return tokens;
    }

    // ---------- helpers ----------

    private static PricebookEntry resolveLinePbe(Map<String, Object> line, Map<Id, PricebookEntry> validPbeById, Map<Id, PricebookEntry> fallbackByProduct) {
        Id pbeId = optionalId(line.get('pbeId'));
        if (pbeId != null) {
            PricebookEntry pbe = validPbeById.get(pbeId);
            if (pbe == null) {
                throw new CatalogException('Price book entry ' + pbeId + ' is not valid for this quote\'s price book.');
            }
            // Tamper guard: claimed product / selling model must match the resolved PBE.
            Id claimedProduct = optionalId(line.get('productId'));
            if (claimedProduct != null && claimedProduct != pbe.Product2Id) {
                throw new CatalogException('Product does not match the selected price book entry.');
            }
            Id claimedPsm = optionalId(line.get('productSellingModelId'));
            if (claimedPsm != null && claimedPsm != pbe.ProductSellingModelId) {
                throw new CatalogException('Selling model does not match the selected price book entry.');
            }
            return pbe;
        }
        Id prodId = optionalId(line.get('productId'));
        PricebookEntry fb = fallbackByProduct.get(prodId);
        if (fb == null) {
            throw new CatalogException('No active price book entry for product ' + prodId + ' on this quote\'s price book.');
        }
        return fb;
    }

    /**
     * Selling-model-aware QuoteLineItem field map (mirrors RLM_SetUpQuoteInvocable.buildQuoteLineItemFields):
     * base fields + StartDate/EndDate/PeriodBoundary/BillingFrequency for TermDefined,
     * StartDate/PeriodBoundary/BillingFrequency for Evergreen, none for OneTime.
     */
    private static Map<String, Object> buildQuoteLineItemFields(PricebookEntry pbe, String quoteIdRef, String quoteLineGroupIdRef, Decimal quantity) {
        Decimal unitPrice = (pbe.UnitPrice != null) ? pbe.UnitPrice : 0;
        String sellingModelType = (pbe.ProductSellingModel != null) ? String.valueOf(pbe.ProductSellingModel.SellingModelType) : null;
        String pricingTermUnit = (pbe.ProductSellingModel != null) ? String.valueOf(pbe.ProductSellingModel.PricingTermUnit) : null;
        String billingFrequency = (String.isNotBlank(pricingTermUnit) && PRICING_TERM_TO_BILLING_FREQUENCY.containsKey(pricingTermUnit))
            ? PRICING_TERM_TO_BILLING_FREQUENCY.get(pricingTermUnit) : null;
        Map<String, Object> fields = new Map<String, Object>{
            'QuoteId' => quoteIdRef,
            'Product2Id' => pbe.Product2Id,
            'PricebookEntryId' => pbe.Id,
            'Quantity' => (quantity != null && quantity > 0) ? quantity : 1,
            'UnitPrice' => unitPrice
        };
        if (String.isNotBlank(quoteLineGroupIdRef)) {
            fields.put('QuoteLineGroupId', quoteLineGroupIdRef);
        }
        if ('TermDefined' == sellingModelType && String.isNotBlank(billingFrequency)) {
            fields.put('StartDate', subscriptionStartDateIso());
            fields.put('EndDate', subscriptionEndDateIso());
            fields.put('PeriodBoundary', 'Anniversary');
            fields.put('BillingFrequency', billingFrequency);
        } else if ('Evergreen' == sellingModelType && String.isNotBlank(billingFrequency)) {
            fields.put('StartDate', subscriptionStartDateIso());
            fields.put('PeriodBoundary', 'Anniversary');
            fields.put('BillingFrequency', billingFrequency);
        }
        return fields;
    }

    private static String startDateIsoCache;
    private static String endDateIsoCache;

    private static String subscriptionStartDateIso() {
        if (startDateIsoCache == null) {
            startDateIsoCache = dateToIsoTimestamp(Date.today());
        }
        return startDateIsoCache;
    }

    private static String subscriptionEndDateIso() {
        if (endDateIsoCache == null) {
            endDateIsoCache = dateToIsoTimestamp(Date.today().addYears(1));
        }
        return endDateIsoCache;
    }

    private static String dateToIsoTimestamp(Date d) {
        return DateTime.newInstanceGmt(d, Time.newInstance(0, 0, 0, 0)).formatGmt('yyyy-MM-dd') + 'T00:00:00.000Z';
    }

    private static Integer sellingModelRank(PricebookEntry pbe) {
        String st = (pbe.ProductSellingModel != null) ? String.valueOf(pbe.ProductSellingModel.SellingModelType) : null;
        if (st == 'OneTime') return 1;
        if (st == 'Evergreen') return 2;
        if (st == 'TermDefined') return 3;
        return 99;
    }

    private static List<String> resolveCreatedGroupIds(Map<String, Object> refMap, List<String> createdGroupRefs) {
        List<String> groupIds = new List<String>();
        if (createdGroupRefs.isEmpty() || refMap == null) {
            return groupIds;
        }
        // The response's reference map (when populated) maps each ref name → created record id.
        for (String ref : createdGroupRefs) {
            Object id = refMap.get(ref);
            if (id != null) {
                groupIds.add(String.valueOf(id));
            }
        }
        return groupIds;
    }

    private static Quote loadQuote(Id qId) {
        List<Quote> quotes = [SELECT Id, Name, Pricebook2Id, AccountId FROM Quote WHERE Id = :qId WITH USER_MODE LIMIT 1];
        if (quotes.isEmpty()) {
            throw new CatalogException('Quote not found or not accessible.');
        }
        return quotes[0];
    }

    private static String readCurrency(Quote q) {
        if (!UserInfo.isMultiCurrencyOrganization()) {
            return UserInfo.getDefaultCurrency();
        }
        try {
            return String.valueOf(q.get('CurrencyIsoCode'));
        } catch (Exception e) {
            return UserInfo.getDefaultCurrency();
        }
    }

    private static Integer clampPageSize(Integer requested) {
        if (requested == null || requested <= 0) {
            return DEFAULT_PAGE_SIZE;
        }
        // The Product Discovery actions cap limit at 100; the builder clamps too, but keep the
        // controller's own request sane.
        return Math.min(requested, RLM_DeltaProductDiscoveryRequest.PD_MAX_LIMIT);
    }

    private static Map<String, Object> parseInput(String inputJson) {
        if (String.isBlank(inputJson)) {
            throw new CatalogException('Request body is required.');
        }
        try {
            return (Map<String, Object>) JSON.deserializeUntyped(inputJson);
        } catch (Exception e) {
            throw new CatalogException('Invalid request: malformed JSON.');
        }
    }

    private static Id parseId(String raw, String label) {
        if (String.isBlank(raw)) {
            throw new CatalogException(label + ' is required.');
        }
        try {
            return Id.valueOf(raw.trim());
        } catch (Exception e) {
            throw new CatalogException('Invalid ' + label + '.');
        }
    }

    private static Id optionalId(Object raw) {
        if (raw == null || String.isBlank(String.valueOf(raw))) {
            return null;
        }
        try {
            return Id.valueOf(String.valueOf(raw).trim());
        } catch (Exception e) {
            throw new CatalogException('Invalid id: ' + raw);
        }
    }

    private static String asString(Object o) {
        return (o == null) ? null : String.valueOf(o);
    }

    private static Integer asInteger(Object o) {
        if (o == null) return null;
        try {
            if (o instanceof Integer) return (Integer) o;
            if (o instanceof Decimal) return ((Decimal) o).intValue();
            if (o instanceof Long) return ((Long) o).intValue();
            if (o instanceof Double) return ((Double) o).intValue();
            return Integer.valueOf(String.valueOf(o));
        } catch (Exception e) {
            return null;
        }
    }

    private static Boolean asBoolean(Object o) {
        if (o instanceof Boolean) return (Boolean) o;
        if (o == null) return null;
        try {
            return Boolean.valueOf(String.valueOf(o));
        } catch (Exception e) {
            return null;
        }
    }

    private static Decimal asDecimal(Object o) {
        if (o == null) return null;
        try {
            if (o instanceof Decimal) return (Decimal) o;
            if (o instanceof Integer) return (Decimal) ((Integer) o);
            if (o instanceof Long) return (Decimal) ((Long) o);
            if (o instanceof Double) return Decimal.valueOf((Double) o);
            return Decimal.valueOf(String.valueOf(o));
        } catch (Exception e) {
            return null;
        }
    }

    private static String errorResult(String message) {
        return JSON.serialize(new Map<String, Object>{ 'isSuccess' => false, 'errorMessage' => message });
    }
}
