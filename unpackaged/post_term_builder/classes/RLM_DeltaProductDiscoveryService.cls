/**
 * Reusable wrapper over the Revenue Cloud Product Discovery Standard Invocable Actions (v67.0):
 *   findProducts (search), getProducts (browse), getRecommendedProducts (constraint-rule
 *   recommendations), getCategories (catalog hierarchy).
 *
 * Each method builds the action through an RLM_DeltaProductDiscoveryRequest, invokes it (house pattern,
 * mirrors RLM_PreProcessOrderController), checks the action's success envelope, and normalizes the
 * output into plain DTOs. Action OUTPUTS are read via JSON round-trip
 * (JSON.deserializeUntyped(JSON.serialize(getOutputParameters()))) so the package takes no
 * compile-time dependency on the managed output/representation types. (The one managed-type
 * dependency — the additionalFields INPUT — lives in RLM_DeltaProductDiscoveryRequest.)
 *
 * Methods are virtual so a @IsTest subclass can return canned DiscoveredProduct lists, letting
 * callers be unit-tested without a live Product Discovery configuration (the actions cannot be
 * meaningfully invoked in a bare test context). Action errors surface as DiscoveryException — these
 * components run only in Revenue Cloud–configured orgs, so no graceful "unavailable" contract.
 */
public with sharing virtual class RLM_DeltaProductDiscoveryService {
    public class DiscoveryException extends Exception {}

    /** One discovered product, plus its addable per-PBE prices and any configured display fields. */
    public class DiscoveredProduct {
        public Id productId;
        public String name;
        public String code;
        public String family;
        public String productType;
        public Boolean isBundle;
        public Boolean isConfigurable;
        public Boolean isQualified;
        public Map<String, Object> fields = new Map<String, Object>();
        public List<DiscoveredPrice> prices = new List<DiscoveredPrice>();
    }

    /** One price-book entry for a product — the unit the catalog renders and adds as a quote line. */
    public class DiscoveredPrice {
        public Id pbeId;
        public Id priceBookId;
        public Decimal price;
        public Id productSellingModelId;
        public String sellingModelType;
        public Boolean isDefault;
    }

    /** Search result: products + opaque paging cursor + facets passthrough. */
    public class DiscoveryResult {
        public List<DiscoveredProduct> products = new List<DiscoveredProduct>();
        public String cursor;
        public Object facets;
    }

    /** One category in the catalog hierarchy. */
    public class DiscoveredCategory {
        public Id id;
        public String name;
        public Id parentId;
        public Boolean isQualified;
        public Boolean hasSubCategories;
    }

    // ---------- actions ----------

    /** findProducts — ranked search; requires a search term on the request. */
    public virtual DiscoveryResult findProducts(RLM_DeltaProductDiscoveryRequest req) {
        Map<String, Object> out = invokeProductAction('findProducts', req, false);
        DiscoveryResult result = new DiscoveryResult();
        result.products = normalizeProducts(asList(out.get('results')), req);
        result.cursor = asString(out.get('cursor'));
        result.facets = out.get('facets');
        return result;
    }

    /** getProducts — catalog/category browse; no search term. */
    public virtual DiscoveryResult browseProducts(RLM_DeltaProductDiscoveryRequest req) {
        Map<String, Object> out = invokeProductAction('getProducts', req, false);
        DiscoveryResult result = new DiscoveryResult();
        result.products = normalizeProducts(asList(out.get('results')), req);
        result.cursor = asString(out.get('cursor'));
        return result;
    }

    /**
     * getRecommendedProducts — Constraint Rule Engine recommendations for the request's quote.
     * The action's output keys are doc-ambiguous (table vs sample), so both shapes are read. (Live
     * v67.0 in this org returns an empty success envelope when no constraint rules are modeled.)
     */
    public virtual DiscoveryResult recommendProducts(RLM_DeltaProductDiscoveryRequest req) {
        Map<String, Object> out = invokeProductAction('getRecommendedProducts', req, true);
        DiscoveryResult result = new DiscoveryResult();
        Object products = (out.get('recommendedProducts') != null)
            ? out.get('recommendedProducts')
            : out.get('recomProdOutputRepresentations');
        result.products = normalizeProducts(asList(products), req);
        result.cursor = (out.get('nextCursor') != null)
            ? asString(out.get('nextCursor'))
            : asString(out.get('productCursor'));
        return result;
    }

    /** getCategories — categories under a catalog (and optional parent category). */
    public virtual List<DiscoveredCategory> getCategories(RLM_DeltaProductDiscoveryRequest req) {
        Invocable.Action action = Invocable.Action.createStandardAction('getCategories');
        req.applyCategoryParameters(action);
        Map<String, Object> out = invokeAndRead(action, 'getCategories');
        List<DiscoveredCategory> categories = new List<DiscoveredCategory>();
        for (Object o : asList(out.get('resultCategoryList'))) {
            Map<String, Object> c = (Map<String, Object>) o;
            DiscoveredCategory dc = new DiscoveredCategory();
            dc.id = optionalId(c.get('id'));
            dc.name = asString(c.get('name'));
            dc.parentId = optionalId(c.get('parentCategoryId'));
            dc.isQualified = readIsQualified(c);
            dc.hasSubCategories = asBoolean(c.get('hasSubCategories'));
            categories.add(dc);
        }
        return categories;
    }

    // ---------- invocation ----------

    private Map<String, Object> invokeProductAction(String actionName, RLM_DeltaProductDiscoveryRequest req, Boolean forRecommendation) {
        Invocable.Action action = Invocable.Action.createStandardAction(actionName);
        req.applyProductParameters(action, forRecommendation);
        return invokeAndRead(action, actionName);
    }

    /** Invoke an action, assert success, and return its output parameters as an untyped map. */
    private Map<String, Object> invokeAndRead(Invocable.Action action, String actionName) {
        List<Invocable.Action.Result> results = action.invoke();
        if (results == null || results.isEmpty()) {
            throw new DiscoveryException(actionName + ' returned no result.');
        }
        Invocable.Action.Result r = results[0];
        if (!r.isSuccess()) {
            throw new DiscoveryException(actionName + ' failed: ' + String.valueOf(r.getErrors()));
        }
        Map<String, Object> out = toUntypedMap(r.getOutputParameters());
        // getRecommendedProducts carries its own success flag in the output payload.
        if (out.containsKey('isSuccessful') && out.get('isSuccessful') == false) {
            Object errs = (out.get('errorMessages') != null) ? out.get('errorMessages') : out.get('prodRecomErrorOutRepresentation');
            throw new DiscoveryException(actionName + ' was unsuccessful: ' + String.valueOf(errs));
        }
        return out;
    }

    // ---------- normalization ----------

    /**
     * Map representation entries → DiscoveredProduct, flattening prices[] into per-PBE DiscoveredPrice
     * and projecting the requested display fields. Shared by find/browse/recommend (their product
     * representations carry the same id/name/prices/pricingModel shape).
     */
    @TestVisible
    private List<DiscoveredProduct> normalizeProducts(List<Object> rawProducts, RLM_DeltaProductDiscoveryRequest req) {
        List<String> requestedProductFields = (req == null) ? null : req.getRequestedFields('Product2');
        List<DiscoveredProduct> out = new List<DiscoveredProduct>();
        if (rawProducts == null) {
            return out;
        }
        for (Object o : rawProducts) {
            Map<String, Object> p = (Map<String, Object>) o;
            DiscoveredProduct dp = new DiscoveredProduct();
            dp.productId = optionalId(p.get('id'));
            dp.name = asString(p.get('name'));
            dp.code = asString(p.get('productCode'));
            dp.family = asString(p.get('family'));
            dp.productType = asString(p.get('productType'));
            dp.isBundle = deriveIsBundle(p);
            // ConfigureDuringSale ('Allowed'/'NotAllowed') is the authoritative configurability
            // signal — and is NOT bundle-only (attribute-configurable simple products carry it too).
            dp.isConfigurable = 'Allowed'.equals(asString(p.get('configureDuringSale')));
            dp.isQualified = readIsQualified(p);
            dp.fields = projectFields(p, requestedProductFields);
            dp.prices = normalizePrices(asList(p.get('prices')));
            out.add(dp);
        }
        return out;
    }

    private static List<DiscoveredPrice> normalizePrices(List<Object> rawPrices) {
        List<DiscoveredPrice> prices = new List<DiscoveredPrice>();
        if (rawPrices == null) {
            return prices;
        }
        for (Object o : rawPrices) {
            Map<String, Object> pr = (Map<String, Object>) o;
            DiscoveredPrice dpr = new DiscoveredPrice();
            dpr.pbeId = optionalId(pr.get('priceBookEntryId'));
            dpr.priceBookId = optionalId(pr.get('priceBookId'));
            dpr.price = asDecimal(pr.get('price'));
            dpr.isDefault = asBoolean(pr.get('isDefault'));
            Object pm = pr.get('pricingModel');
            if (pm instanceof Map<String, Object>) {
                Map<String, Object> model = (Map<String, Object>) pm;
                dpr.productSellingModelId = optionalId(model.get('id'));
                dpr.sellingModelType = asString(model.get('pricingModelType'));
            }
            // Only PBE-bearing prices are addable; skip any malformed price entry without one.
            if (dpr.pbeId != null) {
                prices.add(dpr);
            }
        }
        return prices;
    }

    private static Boolean deriveIsBundle(Map<String, Object> p) {
        if ('Bundle'.equals(asString(p.get('productType')))) {
            return true;
        }
        if (p.get('productRelatedComponent') != null) {
            return true;
        }
        List<Object> groups = asList(p.get('productComponentGroups'));
        return groups != null && !groups.isEmpty();
    }

    private static Boolean readIsQualified(Map<String, Object> m) {
        Object qc = m.get('qualificationContext');
        if (qc instanceof Map<String, Object>) {
            return asBoolean(((Map<String, Object>) qc).get('isQualified'));
        }
        return null;
    }

    /**
     * Project the requested display fields off a product representation. Live-confirmed (v67.0): the
     * additionalFields output is a list of { "key": <fieldName>, "value": <fieldValue> } pairs. A
     * requested field may also already be present as a top-level representation key (e.g. Description),
     * so this prefers the top-level value and falls back to the additionalFields pair.
     */
    private static Map<String, Object> projectFields(Map<String, Object> p, List<String> requestedFields) {
        Map<String, Object> fields = new Map<String, Object>();
        if (requestedFields == null || requestedFields.isEmpty()) {
            return fields;
        }
        // Index the additionalFields key/value pairs for lookup.
        Map<String, Object> additional = new Map<String, Object>();
        for (Object o : asList(p.get('additionalFields'))) {
            if (!(o instanceof Map<String, Object>)) {
                continue;
            }
            Map<String, Object> w = (Map<String, Object>) o;
            String key = asString(w.get('key'));
            if (key != null) {
                additional.put(key, w.get('value'));
            }
        }
        for (String fieldName : requestedFields) {
            // Prefer a default top-level value; otherwise take the layered additionalFields value.
            if (p.get(fieldName) != null) {
                fields.put(fieldName, p.get(fieldName));
            } else if (additional.containsKey(fieldName)) {
                fields.put(fieldName, additional.get(fieldName));
            } else {
                fields.put(fieldName, null);
            }
        }
        return fields;
    }

    // ---------- coercion helpers ----------

    private static Map<String, Object> toUntypedMap(Map<String, Object> raw) {
        // Round-trip so nested managed types deserialize to plain maps/lists.
        return (Map<String, Object>) JSON.deserializeUntyped(JSON.serialize(raw));
    }

    private static List<Object> asList(Object o) {
        return (o instanceof List<Object>) ? (List<Object>) o : null;
    }

    private static String asString(Object o) {
        return (o == null) ? null : String.valueOf(o);
    }

    private static Boolean asBoolean(Object o) {
        if (o instanceof Boolean) {
            return (Boolean) o;
        }
        if (o == null) {
            return null;
        }
        return Boolean.valueOf(String.valueOf(o));
    }

    private static Decimal asDecimal(Object o) {
        if (o == null) {
            return null;
        }
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

    private static Id optionalId(Object raw) {
        if (raw == null || String.isBlank(String.valueOf(raw))) {
            return null;
        }
        try {
            return Id.valueOf(String.valueOf(raw).trim());
        } catch (Exception e) {
            return null;
        }
    }
}
