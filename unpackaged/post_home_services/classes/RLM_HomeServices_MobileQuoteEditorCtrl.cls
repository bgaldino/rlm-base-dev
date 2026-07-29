/**
 * Controller for the mobile-first Quote line editor LWC.
 *
 * This class is a thin UX shell over native RLM. It reads QuoteLineItem data
 * (bundle parent/child hierarchy + pricing), applies light field edits
 * (discount, quantity, dates), and removes lines. All mutations are routed
 * through the native RLM Place Sales Transaction API (RevSalesTrxn) so the
 * pricing procedure recalculates net prices and quote rollups; the class then
 * returns freshly-queried totals. A plain QuoteLineItem DML save persists the
 * fields but does NOT trigger RLM pricing, which is why the transaction API is
 * used instead. Configuration and add-product remain fully native.
 *
 * Dynamic SOQL is used so the component adapts to whichever RLM pricing/hierarchy
 * fields are present in the target org.
 */
public with sharing class RLM_HomeServices_MobileQuoteEditorCtrl {

    // Candidate API names for the bundle parent self-lookup on QuoteLineItem.
    // The first one that exists in the org is used to build the bundle tree.
    private static final List<String> PARENT_FIELD_CANDIDATES = new List<String>{
        'ParentQuoteLineItemId', 'ParentLineItemId', 'ParentQuoteLineId', 'ParentProductId'
    };

    // Quote statuses in which editing is locked down.
    private static final Set<String> LOCKED_STATUSES = new Set<String>{
        'Accepted', 'Denied', 'Rejected'
    };

    public class LineWrapper {
        @AuraEnabled public Id id;
        @AuraEnabled public String name;
        @AuraEnabled public String productCode;
        @AuraEnabled public String description;
        @AuraEnabled public Decimal quantity;
        @AuraEnabled public Decimal listPrice;
        @AuraEnabled public Decimal netUnitPrice;
        @AuraEnabled public Decimal netTotalPrice;
        // Pre-discount total for the line (Quantity x term). Used as the
        // struck-through reference price so it lines up unit-for-unit with
        // netTotalPrice (both are line totals, not per-unit prices).
        @AuraEnabled public Decimal grossTotalPrice;
        @AuraEnabled public Decimal discountPercent;
        @AuraEnabled public Decimal discountAmount;
        @AuraEnabled public Date startDate;
        @AuraEnabled public Date endDate;
        @AuraEnabled public Boolean isBundleParent;
        @AuraEnabled public Boolean isConfigurable;
        @AuraEnabled public Boolean isChild;
        @AuraEnabled public Id parentId;
        @AuraEnabled public List<LineWrapper> children;

        public LineWrapper() {
            this.children = new List<LineWrapper>();
            this.isBundleParent = false;
            this.isConfigurable = false;
            this.isChild = false;
        }
    }

    public class EditorData {
        @AuraEnabled public Id quoteId;
        @AuraEnabled public String quoteName;
        @AuraEnabled public String status;
        @AuraEnabled public Boolean editable;
        @AuraEnabled public List<LineWrapper> lines;
        @AuraEnabled public Decimal servicesTotal;
        @AuraEnabled public Decimal discountsTotal;
        @AuraEnabled public Decimal tax;
        @AuraEnabled public Decimal grandTotal;
    }

    public class AddOnWrapper {
        @AuraEnabled public Id productId;
        @AuraEnabled public String name;
        @AuraEnabled public String description;
        @AuraEnabled public Id pricebookEntryId;
        @AuraEnabled public Decimal unitPrice;
        @AuraEnabled public Boolean selected;
        @AuraEnabled public Boolean available;
        @AuraEnabled public Id existingLineId;
    }

    // Term/subscription fields copied from the bundle line onto a new add-on line
    // so the native pricing procedure has what it needs to price recurring add-ons.
    private static final List<String> SUBSCRIPTION_FIELD_CANDIDATES = new List<String>{
        'StartDate', 'EndDate', 'SubscriptionTerm', 'BillingFrequency',
        'PeriodBoundary', 'PeriodBoundaryDay', 'PeriodBoundaryStartMonth'
    };

    @AuraEnabled(cacheable=true)
    public static EditorData getQuoteLines(String quoteId) {
        return buildEditorData(safeQuoteId(quoteId));
    }

    /**
     * Applies a light edit to a single line via the native RLM Place Sales
     * Transaction API so pricing recalculates; refreshed totals are then returned.
     * Any of the value parameters may be null to leave that field unchanged.
     * discountMode: 'percent' | 'amount' | null. When set, the other discount
     * field is cleared so the two never stack.
     */
    @AuraEnabled
    public static EditorData applyLineEdit(
        String lineId,
        Decimal quantity,
        Decimal discountValue,
        String discountMode,
        String startDate,
        String endDate
    ) {
        Id lId = safeId(lineId);
        if (lId == null) {
            throw new AuraHandledException('A valid line id is required.');
        }

        Map<String, Schema.SObjectField> fm = fieldMap();
        Map<String, Object> fieldValues = new Map<String, Object>();

        if (quantity != null && fm.containsKey('quantity')) {
            fieldValues.put('Quantity', quantity);
        }
        if (String.isNotBlank(startDate) && fm.containsKey('startdate')) {
            fieldValues.put('StartDate', formatDate(Date.valueOf(startDate)));
        }
        if (String.isNotBlank(endDate) && fm.containsKey('enddate')) {
            fieldValues.put('EndDate', formatDate(Date.valueOf(endDate)));
        }
        if (discountValue != null && String.isNotBlank(discountMode)) {
            if (discountMode == 'percent' && fm.containsKey('discount')) {
                fieldValues.put('Discount', discountValue);
                if (fm.containsKey('discountamount')) {
                    fieldValues.put('DiscountAmount', null);
                }
            } else if (discountMode == 'amount' && fm.containsKey('discountamount')) {
                fieldValues.put('DiscountAmount', discountValue);
                if (fm.containsKey('discount')) {
                    fieldValues.put('Discount', null);
                }
            }
        }

        Id qId = quoteIdForLine(lId);
        if (fieldValues.isEmpty()) {
            return buildEditorData(qId);
        }

        // Route the edit through the native RLM Place Sales Transaction API so the
        // pricing procedure recalculates net prices and quote rollups. A plain
        // QuoteLineItem DML update saves the fields but does NOT trigger RLM pricing.
        RevSalesTrxn.RecordResource qliRec = new RevSalesTrxn.RecordResource(
            QuoteLineItem.getSObjectType(), 'PATCH', lId
        );
        qliRec.fieldValues = fieldValues;
        placeTransaction(qId, qliRec, 'refEdit', false);
        return buildEditorData(qId);
    }

    @AuraEnabled
    public static EditorData removeLine(String lineId) {
        Id lId = safeId(lineId);
        if (lId == null) {
            throw new AuraHandledException('A valid line id is required.');
        }
        Id qId = quoteIdForLine(lId);
        // Remove through the native RLM Place Sales Transaction API so remaining
        // line rollups and quote totals reprice. A plain DML delete would not
        // trigger RLM pricing.
        RevSalesTrxn.RecordResource delRec = new RevSalesTrxn.RecordResource(
            QuoteLineItem.getSObjectType(), 'DELETE', lId
        );
        placeTransaction(qId, delRec, 'refDel', false);
        return buildEditorData(qId);
    }

    /**
     * Returns refreshed totals for the quote. Native RLM pricing already
     * recalculated on the preceding transaction; this simply re-reads the rollups.
     */
    @AuraEnabled
    public static EditorData reprice(String quoteId) {
        return buildEditorData(safeQuoteId(quoteId));
    }

    /**
     * Returns the optional add-on components defined for the bundle line's product,
     * each flagged with whether it's already on the quote. Add-ons are the
     * ProductRelatedComponent children of the bundle product.
     */
    @AuraEnabled
    public static List<AddOnWrapper> getConfigurableAddOns(String bundleLineId) {
        Id lId = safeId(bundleLineId);
        if (lId == null) {
            return new List<AddOnWrapper>();
        }
        List<QuoteLineItem> lines = [
            SELECT Id, QuoteId, Product2Id, Quote.Pricebook2Id
            FROM QuoteLineItem
            WHERE Id = :lId
            LIMIT 1
        ];
        if (lines.isEmpty()) {
            return new List<AddOnWrapper>();
        }
        Id bundleProductId = lines[0].Product2Id;
        Id quoteId = lines[0].QuoteId;
        Id pricebookId = lines[0].Quote.Pricebook2Id;

        List<ProductRelatedComponent> comps = [
            SELECT ChildProductId, ChildProduct.Name, ChildProduct.Description, IsDefaultComponent
            FROM ProductRelatedComponent
            WHERE ParentProductId = :bundleProductId
            ORDER BY ChildProduct.Name
        ];
        if (comps.isEmpty()) {
            return new List<AddOnWrapper>();
        }

        Set<Id> childProductIds = new Set<Id>();
        for (ProductRelatedComponent c : comps) {
            childProductIds.add(c.ChildProductId);
        }

        Map<Id, PricebookEntry> pbeByProduct = new Map<Id, PricebookEntry>();
        if (pricebookId != null) {
            for (PricebookEntry pbe : [
                SELECT Id, Product2Id, UnitPrice
                FROM PricebookEntry
                WHERE Pricebook2Id = :pricebookId AND Product2Id IN :childProductIds AND IsActive = true
            ]) {
                pbeByProduct.put(pbe.Product2Id, pbe);
            }
        }

        Map<Id, Id> existingLineByProduct = new Map<Id, Id>();
        for (QuoteLineItem qli : [
            SELECT Id, Product2Id
            FROM QuoteLineItem
            WHERE QuoteId = :quoteId AND Product2Id IN :childProductIds
        ]) {
            if (!existingLineByProduct.containsKey(qli.Product2Id)) {
                existingLineByProduct.put(qli.Product2Id, qli.Id);
            }
        }

        List<AddOnWrapper> result = new List<AddOnWrapper>();
        for (ProductRelatedComponent c : comps) {
            PricebookEntry pbe = pbeByProduct.get(c.ChildProductId);
            AddOnWrapper w = new AddOnWrapper();
            w.productId = c.ChildProductId;
            w.name = c.ChildProduct.Name;
            w.description = c.ChildProduct.Description;
            w.pricebookEntryId = pbe != null ? pbe.Id : null;
            w.unitPrice = pbe != null ? pbe.UnitPrice : null;
            w.available = pbe != null;
            w.selected = existingLineByProduct.containsKey(c.ChildProductId);
            w.existingLineId = existingLineByProduct.get(c.ChildProductId);
            result.add(w);
        }
        return result;
    }

    /**
     * Adds or removes an add-on line on the quote via the native RevSalesTrxn
     * Place Sales Transaction API, so RLM configuration rules and pricing run
     * natively. Returns refreshed editor data.
     */
    @AuraEnabled
    public static EditorData setAddOn(String bundleLineId, String componentProductId, Boolean selected) {
        Id lId = safeId(bundleLineId);
        Id prodId = safeId(componentProductId);
        if (lId == null || prodId == null) {
            throw new AuraHandledException('A valid bundle line and add-on product are required.');
        }
        List<QuoteLineItem> lines = [
            SELECT Id, QuoteId, Quote.Pricebook2Id
            FROM QuoteLineItem
            WHERE Id = :lId
            LIMIT 1
        ];
        if (lines.isEmpty()) {
            throw new AuraHandledException('Bundle line not found.');
        }
        Id quoteId = lines[0].QuoteId;
        Id pricebookId = lines[0].Quote.Pricebook2Id;

        if (selected == true) {
            addComponentLine(quoteId, lId, prodId, pricebookId);
        } else {
            removeComponentLine(quoteId, prodId);
        }
        return buildEditorData(quoteId);
    }

    private static void addComponentLine(Id quoteId, Id bundleLineId, Id productId, Id pricebookId) {
        List<PricebookEntry> pbes = [
            SELECT Id FROM PricebookEntry
            WHERE Pricebook2Id = :pricebookId AND Product2Id = :productId AND IsActive = true
            LIMIT 1
        ];
        if (pbes.isEmpty()) {
            throw new AuraHandledException('No active price book entry found for this add-on.');
        }

        Map<String, Object> fieldValues = new Map<String, Object>{
            'Product2Id' => productId,
            'PricebookEntryId' => pbes[0].Id,
            'Quantity' => '1',
            'QuoteId' => '@{refQuote.id}'
        };

        // Copy term/subscription fields from the bundle line so recurring add-ons price.
        Map<String, Schema.SObjectField> fm = fieldMap();
        List<String> present = new List<String>();
        for (String sf : SUBSCRIPTION_FIELD_CANDIDATES) {
            if (fm.containsKey(sf.toLowerCase())) {
                present.add(sf);
            }
        }
        if (!present.isEmpty()) {
            String soql = 'SELECT ' + String.join(present, ', ') +
                ' FROM QuoteLineItem WHERE Id = :bundleLineId LIMIT 1';
            SObject parent = Database.query(soql)[0];
            for (String sf : present) {
                Object v = parent.get(sf);
                if (v != null && fm.get(sf.toLowerCase()).getDescribe().isCreateable()) {
                    fieldValues.put(sf, v instanceof Date ? formatDate((Date) v) : v);
                }
            }
        }

        RevSalesTrxn.RecordResource qliRec = new RevSalesTrxn.RecordResource(
            QuoteLineItem.getSObjectType(), 'POST'
        );
        qliRec.fieldValues = fieldValues;
        placeTransaction(quoteId, qliRec, 'refAddOn', true);
    }

    private static void removeComponentLine(Id quoteId, Id productId) {
        List<QuoteLineItem> existing = [
            SELECT Id FROM QuoteLineItem
            WHERE QuoteId = :quoteId AND Product2Id = :productId
            LIMIT 1
        ];
        if (existing.isEmpty()) {
            return;
        }
        RevSalesTrxn.RecordResource delRec = new RevSalesTrxn.RecordResource(
            QuoteLineItem.getSObjectType(), 'DELETE', existing[0].Id
        );
        placeTransaction(quoteId, delRec, 'refDel', true);
    }

    private static void placeTransaction(Id quoteId, RevSalesTrxn.RecordResource lineRec, String refName, Boolean runConfiguration) {
        RevSalesTrxn.RecordResource quoteRec = new RevSalesTrxn.RecordResource(
            Quote.getSObjectType(), 'PATCH', quoteId
        );
        List<RevSalesTrxn.RecordWithReferenceRequest> records =
            new List<RevSalesTrxn.RecordWithReferenceRequest>{
                new RevSalesTrxn.RecordWithReferenceRequest('refQuote', quoteRec),
                new RevSalesTrxn.RecordWithReferenceRequest(refName, lineRec)
            };
        RevSalesTrxn.GraphRequest graph = new RevSalesTrxn.GraphRequest('mobileEditorAddOn', records);

        // For simple line edits we want pricing to run without re-running default
        // configuration (which could re-add default bundle components). Pricing
        // always runs via PricingPreferenceEnum.SYSTEM regardless of this flag.
        RevSalesTrxn.ConfigurationOptionsInput opts = new RevSalesTrxn.ConfigurationOptionsInput();
        opts.addDefaultConfiguration = runConfiguration;
        opts.executeConfigurationRules = runConfiguration;

        RevSalesTrxn.PlaceSalesTransactionResponse resp;
        try {
            resp = RevSalesTrxn.PlaceSalesTransactionExecutor.execute(
                graph,
                RevSalesTrxn.PricingPreferenceEnum.SYSTEM,
                RevSalesTrxn.ConfigurationExecutionEnum.SYSTEM,
                opts,
                null
            );
        } catch (Exception e) {
            throw new AuraHandledException('Unable to update the quote: ' + e.getMessage());
        }
        if (resp == null || resp.isSuccess != true) {
            throw new AuraHandledException(firstErrorMessage(resp));
        }
    }

    private static String firstErrorMessage(RevSalesTrxn.PlaceSalesTransactionResponse resp) {
        if (resp != null && resp.errorResponse != null) {
            try {
                List<Object> errs = (List<Object>) JSON.deserializeUntyped(
                    JSON.serialize(resp.errorResponse)
                );
                if (!errs.isEmpty()) {
                    Map<String, Object> e0 = (Map<String, Object>) errs[0];
                    Object m = e0.get('message');
                    if (m != null) {
                        return (String) m;
                    }
                }
            } catch (Exception ignored) {
                // fall through to generic message
            }
        }
        return 'The add-on could not be saved. Please try again.';
    }

    private static String formatDate(Date d) {
        return DateTime.newInstance(d.year(), d.month(), d.day(), 0, 0, 0).format('yyyy-MM-dd');
    }

    // ── Internal helpers ─────────────────────────────────────────────────────

    private static EditorData buildEditorData(Id qId) {
        if (qId == null) {
            return null;
        }

        List<Quote> quotes = [
            SELECT Id, Name, Status, Subtotal, TotalPrice, TotalPriceWithTax
            FROM Quote
            WHERE Id = :qId
            LIMIT 1
        ];
        if (quotes.isEmpty()) {
            return null;
        }
        Quote q = quotes[0];

        Map<String, Schema.SObjectField> fm = fieldMap();
        String parentField = firstExistingField(fm, PARENT_FIELD_CANDIDATES);

        List<String> selectFields = new List<String>{
            'Id', 'QuoteId', 'Product2Id', 'Product2.Name', 'Product2.ProductCode',
            'Product2.Type', 'Product2.ConfigureDuringSale',
            'Quantity', 'UnitPrice', 'Subtotal', 'TotalPrice', 'Discount', 'Description'
        };
        addField(selectFields, fm, 'ListPrice');
        addField(selectFields, fm, 'NetUnitPrice');
        addField(selectFields, fm, 'NetTotalPrice');
        addField(selectFields, fm, 'DiscountAmount');
        addField(selectFields, fm, 'StartDate');
        addField(selectFields, fm, 'EndDate');
        if (parentField != null) {
            selectFields.add(parentField);
        }

        String soql = 'SELECT ' + String.join(selectFields, ', ') +
            ' FROM QuoteLineItem WHERE QuoteId = :qId ORDER BY CreatedDate';
        List<SObject> rows = Database.query(soql);

        Map<Id, LineWrapper> byId = new Map<Id, LineWrapper>();
        List<LineWrapper> ordered = new List<LineWrapper>();
        Decimal servicesSum = 0;
        Decimal discountsSum = 0;

        for (SObject row : rows) {
            LineWrapper w = toWrapper(row, parentField);
            byId.put(w.id, w);
            ordered.add(w);

            Decimal subtotal = (Decimal) numberOrZero(row.get('Subtotal'));
            Decimal total = (Decimal) numberOrZero(row.get('TotalPrice'));
            Decimal lineDiscount = subtotal - total;
            if (lineDiscount < 0) lineDiscount = 0;
            servicesSum += subtotal;
            discountsSum += lineDiscount;
        }

        // Build parent/child tree when a hierarchy field is present.
        List<LineWrapper> roots = new List<LineWrapper>();
        for (LineWrapper w : ordered) {
            if (w.parentId != null && byId.containsKey(w.parentId)) {
                LineWrapper parent = byId.get(w.parentId);
                parent.children.add(w);
                parent.isBundleParent = true;
                w.isChild = true;
            } else {
                roots.add(w);
            }
        }

        Decimal grandTotal = q.TotalPrice != null ? q.TotalPrice : 0;
        Decimal totalWithTax = q.TotalPriceWithTax != null ? q.TotalPriceWithTax : grandTotal;
        Decimal taxAmount = totalWithTax - grandTotal;
        if (taxAmount < 0) taxAmount = 0;

        EditorData data = new EditorData();
        data.quoteId = q.Id;
        data.quoteName = q.Name;
        data.status = q.Status;
        data.editable = String.isBlank(q.Status) || !LOCKED_STATUSES.contains(q.Status);
        data.lines = roots;
        data.servicesTotal = servicesSum;
        data.discountsTotal = discountsSum;
        data.tax = taxAmount;
        data.grandTotal = totalWithTax;
        return data;
    }

    private static LineWrapper toWrapper(SObject row, String parentField) {
        LineWrapper w = new LineWrapper();
        w.id = (Id) row.get('Id');
        SObject product = row.getSObject('Product2');
        w.name = product != null ? (String) product.get('Name') : '';
        w.productCode = product != null ? (String) product.get('ProductCode') : null;
        if (product != null) {
            String prodType = (String) product.get('Type');
            String configDuringSale = (String) product.get('ConfigureDuringSale');
            w.isConfigurable = prodType == 'Bundle'
                || (configDuringSale != null && configDuringSale != 'NotAllowed' && configDuringSale != 'None');
        }
        w.description = (String) row.get('Description');
        w.quantity = (Decimal) row.get('Quantity');
        w.listPrice = (Decimal) pick(row, new List<String>{ 'ListPrice', 'UnitPrice' });
        w.netUnitPrice = (Decimal) pick(row, new List<String>{ 'NetUnitPrice', 'UnitPrice' });
        w.netTotalPrice = (Decimal) pick(row, new List<String>{ 'NetTotalPrice', 'TotalPrice' });
        Decimal grossTotal = (Decimal) safeGet(row, 'Subtotal');
        if (grossTotal == null && w.listPrice != null && w.quantity != null) {
            grossTotal = w.listPrice * w.quantity;
        }
        w.grossTotalPrice = grossTotal;
        w.discountPercent = (Decimal) safeGet(row, 'Discount');
        w.discountAmount = (Decimal) safeGet(row, 'DiscountAmount');
        w.startDate = (Date) safeGet(row, 'StartDate');
        w.endDate = (Date) safeGet(row, 'EndDate');
        if (parentField != null) {
            w.parentId = (Id) row.get(parentField);
        }
        return w;
    }

    private static Id quoteIdForLine(Id lineId) {
        List<QuoteLineItem> items = [SELECT QuoteId FROM QuoteLineItem WHERE Id = :lineId LIMIT 1];
        return items.isEmpty() ? null : items[0].QuoteId;
    }

    private static Map<String, Schema.SObjectField> fieldMap() {
        return Schema.SObjectType.QuoteLineItem.fields.getMap();
    }

    private static void addField(List<String> fields, Map<String, Schema.SObjectField> fm, String apiName) {
        if (fm.containsKey(apiName.toLowerCase())) {
            fields.add(apiName);
        }
    }

    private static String firstExistingField(Map<String, Schema.SObjectField> fm, List<String> candidates) {
        for (String c : candidates) {
            if (fm.containsKey(c.toLowerCase())) {
                return c;
            }
        }
        return null;
    }

    private static Object pick(SObject row, List<String> apiNames) {
        for (String apiName : apiNames) {
            Object v = safeGet(row, apiName);
            if (v != null) {
                return v;
            }
        }
        return null;
    }

    private static Object safeGet(SObject row, String apiName) {
        try {
            return row.get(apiName);
        } catch (Exception e) {
            return null;
        }
    }

    private static Decimal numberOrZero(Object value) {
        return value == null ? 0 : (Decimal) value;
    }

    private static Id safeQuoteId(String value) {
        Id result = safeId(value);
        if (result != null && result.getSObjectType() == Quote.SObjectType) {
            return result;
        }
        return null;
    }

    private static Id safeId(String value) {
        if (String.isBlank(value)) {
            return null;
        }
        try {
            return Id.valueOf(value);
        } catch (Exception e) {
            return null;
        }
    }
}