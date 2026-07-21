/**
 * Fluent builder for the Revenue Cloud Product Discovery Standard Invocable Actions
 * (findProducts / getProducts / getRecommendedProducts / getCategories, API v67.0).
 *
 * Holds a neutral parameter surface and knows how to apply it to an Invocable.Action. The four
 * actions do NOT share one parameter vocabulary, so the builder exposes two apply paths:
 *   - applyProductParameters(action, forRecommendation) — findProducts/getProducts (cursor/limit/
 *     filter/contextDefinition) and, when forRecommendation=true, getRecommendedProducts
 *     (nextCursor/pageSize/filterCriteria).
 *   - applyCategoryParameters(action) — getCategories ONLY, which uses a distinct vocabulary
 *     (contextDefinitionName/qualificationProcedureName/contextMappingName, categoryNestLevel,
 *     enableQualificationProcedure) and supports no paging/additionalFields/pricing.
 *
 * additionalFields is an Apex-defined input type — the one deliberate compile-time dependency on
 * the managed runtime_industries_cpq namespace (its inputs must be strongly typed for the invocable
 * framework). Action OUTPUTS are read via JSON round-trip in RLM_DeltaProductDiscoveryService, so the
 * package takes no compile-time dependency on the output/representation types.
 *
 * Builds parameter maps separately from applying them so unit tests can assert the assembled
 * params without invoking a live action.
 */
public with sharing class RLM_DeltaProductDiscoveryRequest {
    /** Hard cap enforced by findProducts/getProducts: limit must be 1–100. */
    public static final Integer PD_MAX_LIMIT = 100;

    private Id quoteId;
    private String searchTerm;
    private Id catalogId;
    private Id categoryId;
    private Id parentCategoryId;
    private Integer categoryNestLevel;
    private Id pricebookId;
    private String currencyCode;
    private String contextDefinition;
    private String contextMapping;
    private Integer pageLimit;
    private String cursor;
    private Boolean enablePricing;
    private Boolean enableQualification;
    private Map<String, List<String>> displayFields;

    // ---------- fluent setters ----------

    public RLM_DeltaProductDiscoveryRequest forQuote(Id value) {
        this.quoteId = value;
        return this;
    }

    public RLM_DeltaProductDiscoveryRequest withSearchTerm(String value) {
        this.searchTerm = value;
        return this;
    }

    public RLM_DeltaProductDiscoveryRequest withCatalog(Id value) {
        this.catalogId = value;
        return this;
    }

    public RLM_DeltaProductDiscoveryRequest withCategory(Id value) {
        this.categoryId = value;
        return this;
    }

    public RLM_DeltaProductDiscoveryRequest withParentCategory(Id value) {
        this.parentCategoryId = value;
        return this;
    }

    public RLM_DeltaProductDiscoveryRequest withCategoryNestLevel(Integer value) {
        this.categoryNestLevel = value;
        return this;
    }

    public RLM_DeltaProductDiscoveryRequest withPricebook(Id value) {
        this.pricebookId = value;
        return this;
    }

    public RLM_DeltaProductDiscoveryRequest withCurrency(String value) {
        this.currencyCode = value;
        return this;
    }

    /** Omit (or pass blank) to fall back to the Product Discovery Settings default context definition. */
    public RLM_DeltaProductDiscoveryRequest withContextDefinition(String value) {
        this.contextDefinition = String.isBlank(value) ? null : value;
        return this;
    }

    public RLM_DeltaProductDiscoveryRequest withContextMapping(String value) {
        this.contextMapping = String.isBlank(value) ? null : value;
        return this;
    }

    /** Limit is clamped to 1–100; cursor is the opaque paging token returned by the prior call. */
    public RLM_DeltaProductDiscoveryRequest withPaging(Integer limitValue, String cursorValue) {
        if (limitValue != null) {
            this.pageLimit = Math.max(1, Math.min(limitValue, PD_MAX_LIMIT));
        }
        this.cursor = String.isBlank(cursorValue) ? null : cursorValue;
        return this;
    }

    public RLM_DeltaProductDiscoveryRequest withPricing(Boolean value) {
        this.enablePricing = value;
        return this;
    }

    public RLM_DeltaProductDiscoveryRequest withQualification(Boolean value) {
        this.enableQualification = value;
        return this;
    }

    /** Object API name → list of field API names to surface in the response (e.g. Product2 → [Family]). */
    public RLM_DeltaProductDiscoveryRequest withDisplayFields(Map<String, List<String>> value) {
        this.displayFields = value;
        return this;
    }

    /** The display fields requested for an object (e.g. Product2), or null if none — used by the service to project results. */
    public List<String> getRequestedFields(String objectName) {
        return (displayFields == null) ? null : displayFields.get(objectName);
    }

    // ---------- apply paths ----------

    /**
     * Apply the product/recommendation parameters to the action, mapping the neutral builder state
     * to each action's actual parameter names. findProducts/getProducts use limit/cursor/filter;
     * getRecommendedProducts (forRecommendation=true) uses pageSize/nextCursor/filterCriteria.
     */
    public void applyProductParameters(Invocable.Action action, Boolean forRecommendation) {
        Map<String, Object> params = buildProductParameterMap(forRecommendation);
        for (String name : params.keySet()) {
            action.setInvocationParameter(name, params.get(name));
        }
    }

    /** Apply the getCategories parameters (distinct vocabulary; no paging/additionalFields/pricing). */
    public void applyCategoryParameters(Invocable.Action action) {
        Map<String, Object> params = buildCategoryParameterMap();
        for (String name : params.keySet()) {
            action.setInvocationParameter(name, params.get(name));
        }
    }

    // ---------- parameter assembly (test-visible) ----------

    @TestVisible
    private Map<String, Object> buildProductParameterMap(Boolean forRecommendation) {
        Boolean isRec = (forRecommendation == true);
        Map<String, Object> params = new Map<String, Object>();
        putIfNotNull(params, 'searchTerm', searchTerm);
        putIfNotNull(params, 'catalogId', toStringOrNull(catalogId));
        putIfNotNull(params, 'categoryId', toStringOrNull(categoryId));
        putIfNotNull(params, 'currencyCode', currencyCode);
        putIfNotNull(params, 'priceBookId', toStringOrNull(pricebookId));
        putIfNotNull(params, 'transactionId', toStringOrNull(quoteId));
        putIfNotNull(params, 'contextDefinition', contextDefinition);
        putIfNotNull(params, 'contextMapping', contextMapping);
        putIfNotNull(params, 'enablePricing', enablePricing);
        putIfNotNull(params, 'enableQualification', enableQualification);
        // Paging param names differ between the search/browse actions and recommendations.
        if (isRec) {
            putIfNotNull(params, 'pageSize', pageLimit);
            putIfNotNull(params, 'nextCursor', cursor);
        } else {
            putIfNotNull(params, 'limit', pageLimit);
            putIfNotNull(params, 'cursor', cursor);
        }
        runtime_industries_cpq.AdditionalFields af = buildAdditionalFields();
        if (af != null) {
            params.put('additionalFields', af);
        }
        return params;
    }

    @TestVisible
    private Map<String, Object> buildCategoryParameterMap() {
        Map<String, Object> params = new Map<String, Object>();
        // catalogId is required by getCategories; the service guards for it before invoking.
        putIfNotNull(params, 'catalogId', toStringOrNull(catalogId));
        putIfNotNull(params, 'parentCategoryId', toStringOrNull(parentCategoryId));
        putIfNotNull(params, 'categoryNestLevel', categoryNestLevel);
        putIfNotNull(params, 'enableQualificationProcedure', enableQualification);
        // getCategories uses the *Name forms, not the bare context params.
        putIfNotNull(params, 'contextDefinitionName', contextDefinition);
        putIfNotNull(params, 'contextMappingName', contextMapping);
        return params;
    }

    /** Build the Apex-defined additionalFields input, or null when no display fields are requested. */
    @TestVisible
    private runtime_industries_cpq.AdditionalFields buildAdditionalFields() {
        if (displayFields == null || displayFields.isEmpty()) {
            return null;
        }
        Map<String, runtime_industries_cpq.AdditionalFieldsInput> byObject =
            new Map<String, runtime_industries_cpq.AdditionalFieldsInput>();
        for (String objectName : displayFields.keySet()) {
            List<String> fields = displayFields.get(objectName);
            if (fields == null || fields.isEmpty()) {
                continue;
            }
            runtime_industries_cpq.AdditionalFieldsInput input = new runtime_industries_cpq.AdditionalFieldsInput();
            input.fields = fields;
            byObject.put(objectName, input);
        }
        if (byObject.isEmpty()) {
            return null;
        }
        runtime_industries_cpq.AdditionalFields af = new runtime_industries_cpq.AdditionalFields();
        af.additionalFields = byObject;
        return af;
    }

    // ---------- helpers ----------

    private static void putIfNotNull(Map<String, Object> params, String name, Object value) {
        if (value != null) {
            params.put(name, value);
        }
    }

    private static String toStringOrNull(Id value) {
        return (value == null) ? null : String.valueOf(value);
    }
}
