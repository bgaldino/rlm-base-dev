public with sharing class RLM_InvoiceProductSummaryController {

    // ─── Wrapper classes ──────────────────────────────────────────────────────

    public class AssetAttributeDetail {
        @AuraEnabled public String label { get; set; }
        @AuraEnabled public String value { get; set; }
    }

    public class AssetBlock {
        @AuraEnabled public String assetId   { get; set; }
        @AuraEnabled public String assetName { get; set; }
        @AuraEnabled public List<AssetAttributeDetail> attributes { get; set; }
        public AssetBlock() { this.attributes = new List<AssetAttributeDetail>(); }
    }

    public class InvoiceLineDetail {
        @AuraEnabled public String  lineId          { get; set; }
        @AuraEnabled public String  name            { get; set; }
        @AuraEnabled public String  description     { get; set; }
        @AuraEnabled public Date    periodStartDate { get; set; }
        @AuraEnabled public Date    periodEndDate   { get; set; }
        @AuraEnabled public Decimal quantity        { get; set; }
        @AuraEnabled public Decimal unitPrice       { get; set; }
        @AuraEnabled public Decimal chargeAmount    { get; set; }
        @AuraEnabled public Decimal taxAmount       { get; set; }
        @AuraEnabled public Decimal totalWithTax    { get; set; }
        @AuraEnabled public String  type            { get; set; }
        @AuraEnabled public String  chargeType      { get; set; }
        @AuraEnabled public String  assetId         { get; set; }
        // Usage Resource fields
        @AuraEnabled public Boolean isUsage         { get; set; }
        @AuraEnabled public Decimal overageQty      { get; set; }
        @AuraEnabled public String  unitOfMeasure   { get; set; }
        @AuraEnabled public Decimal rate            { get; set; }
        @AuraEnabled public String  currencyCode    { get; set; }
        // Bundle fields
        @AuraEnabled public Boolean isParent           { get; set; }
        @AuraEnabled public Boolean isComponent        { get; set; }
        @AuraEnabled public Boolean isSuppressedParent { get; set; }
        @AuraEnabled public String  bundleRole         { get; set; }
        @AuraEnabled public List<InvoiceLineDetail> components { get; set; }

        public InvoiceLineDetail() {
            this.isUsage            = false;
            this.isParent           = false;
            this.isComponent        = false;
            this.isSuppressedParent = false;
            this.components         = new List<InvoiceLineDetail>();
        }
    }

    public class ProductSummary {
        @AuraEnabled public String productId         { get; set; }
        @AuraEnabled public String productName       { get; set; }
        @AuraEnabled public String chargeType        { get; set; }
        @AuraEnabled public Integer lineCount        { get; set; }
        @AuraEnabled public Decimal subtotal         { get; set; }
        @AuraEnabled public Decimal taxAmount        { get; set; }
        @AuraEnabled public Decimal totalWithTax     { get; set; }
        @AuraEnabled public List<InvoiceLineDetail> lines       { get; set; }
        @AuraEnabled public List<AssetBlock>        assetBlocks { get; set; }
        public ProductSummary() {
            this.lineCount    = 0;
            this.subtotal     = 0;
            this.taxAmount    = 0;
            this.totalWithTax = 0;
            this.lines        = new List<InvoiceLineDetail>();
            this.assetBlocks  = new List<AssetBlock>();
        }
    }

    public class InvoiceSummaryResult {
        @AuraEnabled public List<ProductSummary> products      { get; set; }
        @AuraEnabled public Decimal              grandSubtotal  { get; set; }
        @AuraEnabled public Decimal              grandTax       { get; set; }
        @AuraEnabled public Decimal              grandTotal     { get; set; }
        @AuraEnabled public Integer              totalLines     { get; set; }
        @AuraEnabled public String               currencyCode   { get; set; }
        public InvoiceSummaryResult() {
            this.products      = new List<ProductSummary>();
            this.grandSubtotal = 0;
            this.grandTax      = 0;
            this.grandTotal    = 0;
            this.totalLines    = 0;
        }
    }

    // ─── Comparators ─────────────────────────────────────────────────────────

    private class AttributeLabelComparator implements Comparator<AssetAttributeDetail> {
        public Integer compare(AssetAttributeDetail a, AssetAttributeDetail b) {
            if (a.label == null && b.label == null) return 0;
            if (a.label == null) return 1;
            if (b.label == null) return -1;
            return a.label.compareTo(b.label);
        }
    }

    private class ProductSummaryComparator implements Comparator<ProductSummary> {
        public Integer compare(ProductSummary a, ProductSummary b) {
            if (a.productName == null && b.productName == null) return 0;
            if (a.productName == null) return 1;
            if (b.productName == null) return -1;
            return a.productName.compareTo(b.productName);
        }
    }

    // ─── Helper: BSG → Asset Id ───────────────────────────────────────────────

    private static Map<Id, Id> resolveBsgToAsset(Set<Id> bsgIds) {
        Map<Id, Id> result = new Map<Id, Id>();
        if (bsgIds == null || bsgIds.isEmpty()) return result;
        try {
            for (BillingScheduleGroup bsg : [
                SELECT Id, ReferenceEntityId
                FROM BillingScheduleGroup
                WHERE Id IN :bsgIds AND ReferenceEntityId != null
            ]) {
                if (String.valueOf(bsg.ReferenceEntityId).startsWith('02i')) {
                    result.put(bsg.Id, bsg.ReferenceEntityId);
                }
            }
        } catch (Exception e) { System.debug('BSG query failed: ' + e.getMessage()); }
        return result;
    }

    // ─── Helper: Asset → AssetStatePeriodAttribute ────────────────────────────

    private static Map<Id, List<AssetAttributeDetail>> resolveAssetAttributes(Set<Id> assetIds) {
        Map<Id, List<AssetAttributeDetail>> result = new Map<Id, List<AssetAttributeDetail>>();
        if (assetIds == null || assetIds.isEmpty()) return result;
        try {
            Map<Id, Id> assetToStatePeriod = new Map<Id, Id>();
            for (AssetStatePeriod asp : [
                SELECT Id, AssetId FROM AssetStatePeriod
                WHERE AssetId IN :assetIds
                ORDER BY AssetId, StartDate DESC NULLS LAST
            ]) {
                if (!assetToStatePeriod.containsKey(asp.AssetId)) {
                    assetToStatePeriod.put(asp.AssetId, asp.Id);
                }
            }
            if (assetToStatePeriod.isEmpty()) return result;

            Set<Id> statePeriodIds = new Set<Id>(assetToStatePeriod.values());
            Map<Id, Id> statePeriodToAsset = new Map<Id, Id>();
            for (Id aid : assetToStatePeriod.keySet()) {
                statePeriodToAsset.put(assetToStatePeriod.get(aid), aid);
            }

            for (AssetStatePeriodAttribute attr : [
                SELECT AssetStatePeriodId, AttributeName, AttributeValue
                FROM AssetStatePeriodAttribute
                WHERE AssetStatePeriodId IN :statePeriodIds
                ORDER BY AttributeName ASC NULLS LAST
            ]) {
                Id assetId = statePeriodToAsset.get(attr.AssetStatePeriodId);
                if (assetId == null) continue;
                if (!result.containsKey(assetId)) {
                    result.put(assetId, new List<AssetAttributeDetail>());
                }
                AssetAttributeDetail aad = new AssetAttributeDetail();
                aad.label = attr.AttributeName;
                aad.value = attr.AttributeValue;
                result.get(assetId).add(aad);
            }
        } catch (Exception e) { System.debug('AssetStatePeriodAttribute failed: ' + e.getMessage()); }
        return result;
    }

    // ─── Helper: Asset names ──────────────────────────────────────────────────

    private static Map<Id, String> resolveAssetNames(Set<Id> assetIds) {
        Map<Id, String> names = new Map<Id, String>();
        if (assetIds == null || assetIds.isEmpty()) return names;
        try {
            for (Asset a : [SELECT Id, Name FROM Asset WHERE Id IN :assetIds]) {
                names.put(a.Id, a.Name);
            }
        } catch (Exception e) { System.debug('Asset name query failed: ' + e.getMessage()); }
        return names;
    }

    // ─── Helper: Rich text table for RLM_Attributes__c ────────────────────────────

    private static String buildRichTextTable(List<AssetAttributeDetail> attrs) {
        if (attrs == null || attrs.isEmpty()) return null;
        String html = '<table border="1" cellpadding="4" cellspacing="0" style="border-collapse:collapse;width:100%;font-size:12px;">';
        html += '<thead><tr>'
            + '<th style="background:#f3f2f2;text-align:left;padding:4px 8px;font-weight:bold;">Attribute</th>'
            + '<th style="background:#f3f2f2;text-align:left;padding:4px 8px;font-weight:bold;">Value</th>'
            + '</tr></thead><tbody>';
        for (AssetAttributeDetail aad : attrs) {
            String lbl = aad.label != null ? aad.label.escapeHtml4() : '';
            String val = aad.value != null ? aad.value.escapeHtml4() : '—';
            html += '<tr><td style="padding:4px 8px;">' + lbl + '</td>'
                  + '<td style="padding:4px 8px;">' + val + '</td></tr>';
        }
        html += '</tbody></table>';
        return html;
    }

    // ─── Helper: Build InvoiceLineDetail from an InvoiceLine ─────────────────

    private static InvoiceLineDetail buildDetail(
        InvoiceLine line,
        Map<Id, Date> linePeriodStart,
        Map<Id, Date> linePeriodEnd,
        Map<Id, Id>   bsgToAssetId,
        Map<Id, String> uomNames,
        String currencyCode
    ) {
        Decimal chargeAmt = line.ChargeAmount != null ? line.ChargeAmount : 0;
        Decimal taxAmt    = line.TaxAmount    != null ? line.TaxAmount    : 0;
        Decimal lineAmt   = line.LineAmount   != null ? line.LineAmount   : (chargeAmt + taxAmt);

        Boolean isUsage = (line.RLM_Charge_Type__c != null &&
                           line.RLM_Charge_Type__c.equalsIgnoreCase('Usage Resource'));
        Decimal overageQty = null;
        String  uomName    = null;
        Decimal rate       = null;
        if (isUsage) {
            overageQty = line.UsageOverageQuantity;
            if (line.UnitOfMeasureId != null) uomName = uomNames.get(line.UnitOfMeasureId);
            if (line.Quantity != null && line.Quantity != 0) {
                rate = (chargeAmt / line.Quantity).setScale(4, System.RoundingMode.HALF_UP);
            }
        }

        String resolvedAssetId = null;
        if (line.BillingScheduleGroupId != null) {
            Id aid = bsgToAssetId.get(line.BillingScheduleGroupId);
            if (aid != null) resolvedAssetId = String.valueOf(aid);
        }

        InvoiceLineDetail d = new InvoiceLineDetail();
        d.lineId          = line.Id;
        d.name            = line.Name;
        d.description     = line.Description;
        d.periodStartDate = linePeriodStart.containsKey(line.Id)
            ? linePeriodStart.get(line.Id) : line.InvoiceLineStartDate;
        d.periodEndDate   = linePeriodEnd.containsKey(line.Id)
            ? linePeriodEnd.get(line.Id)   : line.InvoiceLineEndDate;
        d.quantity        = line.Quantity;
        d.unitPrice       = line.UnitPrice;
        d.chargeAmount    = chargeAmt;
        d.taxAmount       = taxAmt;
        d.totalWithTax    = lineAmt;
        d.type            = line.Type;
        d.chargeType      = line.RLM_Charge_Type__c;
        d.assetId         = resolvedAssetId;
        d.isUsage         = isUsage;
        d.overageQty      = overageQty;
        d.unitOfMeasure   = uomName;
        d.rate            = rate;
        d.currencyCode    = currencyCode;
        return d;
    }

    // ─── METHOD 1: Save attributes to Invoice Line (DML) ─────────────────────

    @AuraEnabled
    public static void saveLineAttributes(Id invoiceId) {
        try {
            List<InvoiceLine> lines = [
                SELECT Id, BillingScheduleGroupId, RLM_Attributes__c
                FROM InvoiceLine
                WHERE InvoiceId = :invoiceId
                AND   BillingScheduleGroupId != null
            ];

            List<InvoiceLine> blankLines = new List<InvoiceLine>();
            for (InvoiceLine l : lines) {
                if (String.isBlank(l.RLM_Attributes__c)) blankLines.add(l);
            }
            if (blankLines.isEmpty()) return;

            Set<Id> bsgIds = new Set<Id>();
            for (InvoiceLine l : blankLines) bsgIds.add(l.BillingScheduleGroupId);

            Map<Id, Id> bsgToAssetId                          = resolveBsgToAsset(bsgIds);
            Map<Id, List<AssetAttributeDetail>> assetToAttrs  = resolveAssetAttributes(new Set<Id>(bsgToAssetId.values()));

            List<InvoiceLine> toUpdate = new List<InvoiceLine>();
            for (InvoiceLine line : blankLines) {
                Id assetId = bsgToAssetId.get(line.BillingScheduleGroupId);
                if (assetId == null) continue;
                List<AssetAttributeDetail> attrs = assetToAttrs.get(assetId);
                if (attrs == null || attrs.isEmpty()) continue;
                String richText = buildRichTextTable(attrs);
                if (richText == null) continue;
                InvoiceLine upd   = new InvoiceLine(Id = line.Id);
                upd.RLM_Attributes__c = richText;
                toUpdate.add(upd);
            }
            if (!toUpdate.isEmpty()) update toUpdate;

        } catch (Exception e) {
            System.debug('saveLineAttributes failed: ' + e.getMessage());
            throw new AuraHandledException('Failed to save attributes: ' + e.getMessage());
        }
    }

    // ─── METHOD 2: Read summary ───────────────────────────────────────────────

    @AuraEnabled(cacheable=true)
    public static InvoiceSummaryResult getInvoiceProductSummary(Id invoiceId) {
        try {

            Invoice inv = [
                SELECT Id, CurrencyIsoCode FROM Invoice WHERE Id = :invoiceId LIMIT 1
            ];

            List<InvoiceLine> lines = [
                SELECT Id, Name, Description, Product2Id, Product2.Name,
                       RLM_Charge_Type__c, BillingScheduleGroupId,
                       InvoiceLineStartDate, InvoiceLineEndDate,
                       Quantity, UnitPrice, ChargeAmount, TaxAmount, LineAmount,
                       Type, UsageOverageQuantity, UnitOfMeasureId
                FROM InvoiceLine
                WHERE InvoiceId = :invoiceId
                ORDER BY Product2.Name ASC NULLS LAST,
                         InvoiceLineStartDate ASC NULLS LAST
            ];

            if (lines.isEmpty()) {
                InvoiceSummaryResult empty = new InvoiceSummaryResult();
                empty.currencyCode = inv.CurrencyIsoCode;
                return empty;
            }

            Set<Id> lineIds = new Set<Id>();
            Set<Id> bsgIds  = new Set<Id>();
            Set<Id> uomIds  = new Set<Id>();
            for (InvoiceLine l : lines) {
                lineIds.add(l.Id);
                if (l.BillingScheduleGroupId != null) bsgIds.add(l.BillingScheduleGroupId);
                if (l.UnitOfMeasureId        != null) uomIds.add(l.UnitOfMeasureId);
            }

            // Billing periods
            Map<Id, Date> linePeriodStart = new Map<Id, Date>();
            Map<Id, Date> linePeriodEnd   = new Map<Id, Date>();
            try {
                for (BillingPeriodItem bpi : [
                    SELECT InvoiceLineId, BillingPeriodStartDate, BillingPeriodEndDate
                    FROM BillingPeriodItem WHERE InvoiceLineId IN :lineIds
                    ORDER BY BillingPeriodStartDate ASC NULLS LAST
                ]) {
                    Id lid = bpi.InvoiceLineId;
                    if (!linePeriodStart.containsKey(lid) ||
                        (bpi.BillingPeriodStartDate != null &&
                         bpi.BillingPeriodStartDate < linePeriodStart.get(lid)))
                        linePeriodStart.put(lid, bpi.BillingPeriodStartDate);
                    if (!linePeriodEnd.containsKey(lid) ||
                        (bpi.BillingPeriodEndDate != null &&
                         bpi.BillingPeriodEndDate > linePeriodEnd.get(lid)))
                        linePeriodEnd.put(lid, bpi.BillingPeriodEndDate);
                }
            } catch (Exception e) { System.debug('BillingPeriodItem failed: ' + e.getMessage()); }

            // UoM names
            Map<Id, String> uomNames = new Map<Id, String>();
            if (!uomIds.isEmpty()) {
                try {
                    for (UnitOfMeasure uom : [SELECT Id, Name FROM UnitOfMeasure WHERE Id IN :uomIds])
                        uomNames.put(uom.Id, uom.Name);
                } catch (Exception e) { System.debug('UoM query failed: ' + e.getMessage()); }
            }

            // Asset attributes
            Map<Id, Id>     bsgToAssetId = resolveBsgToAsset(bsgIds);
            Set<Id>         assetIds     = new Set<Id>(bsgToAssetId.values());
            Map<Id, List<AssetAttributeDetail>> assetToAttrs = resolveAssetAttributes(assetIds);
            Map<Id, String> assetNames   = resolveAssetNames(assetIds);

            // ── Bundle relationships ─────────────────────────────────────────────────
            // componentToParent: child lineId → its direct parent lineId
            // A line can be BOTH a component (has a parent) AND a parent (has children)
            // — this is a nested bundle. We handle this recursively.
            Map<Id, Id>        componentToParent = new Map<Id, Id>();
            Map<Id, List<Id>>  parentToChildren  = new Map<Id, List<Id>>();
            try {
                for (InvoiceLineRelationship ilr : [
                    SELECT MainInvoiceLineId, AssociatedInvoiceLineId
                    FROM InvoiceLineRelationship
                    WHERE MainInvoiceLineId IN :lineIds
                       OR AssociatedInvoiceLineId IN :lineIds
                ]) {
                    if (ilr.MainInvoiceLineId == null || ilr.AssociatedInvoiceLineId == null) continue;
                    componentToParent.put(ilr.AssociatedInvoiceLineId, ilr.MainInvoiceLineId);
                    if (!parentToChildren.containsKey(ilr.MainInvoiceLineId)) {
                        parentToChildren.put(ilr.MainInvoiceLineId, new List<Id>());
                    }
                    parentToChildren.get(ilr.MainInvoiceLineId).add(ilr.AssociatedInvoiceLineId);
                }
            } catch (Exception e) { System.debug('InvoiceLineRelationship failed: ' + e.getMessage()); }

            // Build flat detail map for all lines first
            Map<Id, InvoiceLineDetail> detailMap = new Map<Id, InvoiceLineDetail>();
            for (InvoiceLine line : lines) {
                InvoiceLineDetail d = buildDetail(
                    line, linePeriodStart, linePeriodEnd,
                    bsgToAssetId, uomNames, inv.CurrencyIsoCode
                );
                d.isParent    = parentToChildren.containsKey(line.Id);
                d.isComponent = componentToParent.containsKey(line.Id);
                if (d.isParent)    d.bundleRole = 'Bundle Parent';
                if (d.isComponent) d.bundleRole = 'Bundle Component';
                detailMap.put(line.Id, d);
            }

            // Recursively attach children to parents (supports unlimited nesting depth)
            for (Id parentId : parentToChildren.keySet()) {
                InvoiceLineDetail parent = detailMap.get(parentId);
                if (parent == null) continue;
                for (Id childId : parentToChildren.get(parentId)) {
                    InvoiceLineDetail child = detailMap.get(childId);
                    if (child != null) parent.components.add(child);
                }
            }

            // ── Product grouping ──────────────────────────────────────────────────────
            // Only top-level lines (those with no parent) are added to products.
            // A top-level line may itself be a bundle parent — it shows once in the
            // product header section and is NOT repeated as a line row beneath it.
            Map<String, ProductSummary> productMap = new Map<String, ProductSummary>();
            List<String> productOrder              = new List<String>();

            for (InvoiceLine line : lines) {
                // Skip children — they appear nested under their parent
                if (componentToParent.containsKey(line.Id)) continue;

                String key         = line.Product2Id != null ? (String) line.Product2Id : 'NO_PRODUCT';
                String productName = line.Product2Id != null
                    ? (line.Product2 != null ? line.Product2.Name : 'Unknown Product')
                    : 'No Product';

                if (!productMap.containsKey(key)) {
                    ProductSummary ps = new ProductSummary();
                    ps.productId      = key;
                    ps.productName    = productName;
                    ps.chargeType     = line.RLM_Charge_Type__c;
                    productMap.put(key, ps);
                    productOrder.add(key);
                }

                ProductSummary ps = productMap.get(key);
                ps.lineCount++;
                if (ps.chargeType == null && line.RLM_Charge_Type__c != null)
                    ps.chargeType = line.RLM_Charge_Type__c;

                Decimal chargeAmt = line.ChargeAmount != null ? line.ChargeAmount : 0;
                Decimal taxAmt    = line.TaxAmount    != null ? line.TaxAmount    : 0;
                Decimal lineAmt   = line.LineAmount   != null ? line.LineAmount   : (chargeAmt + taxAmt);
                ps.subtotal     += chargeAmt;
                ps.taxAmount    += taxAmt;
                ps.totalWithTax += lineAmt;

                InvoiceLineDetail detail = detailMap.get(line.Id);
                // If this top-level line IS a bundle parent and shares the product name,
                // suppress it as a row — its children show directly and the product
                // header already carries the name. Just add its children as flat lines.
                if (detail.isParent && detail.components != null && !detail.components.isEmpty()
                    && detail.name != null && detail.name.equalsIgnoreCase(productName)
                    && ps.lines.isEmpty()) {
                    // Don't add the parent row; add children directly so they render
                    // at top level (the product IS the bundle parent)
                    detail.isSuppressedParent = true;
                }
                ps.lines.add(detail);
            }

            // Build merged attribute block per product
            for (String key : productOrder) {
                ProductSummary ps = productMap.get(key);
                Set<String> seenAssetIds = new Set<String>();
                Set<String> seenLabels   = new Set<String>();
                List<AssetAttributeDetail> mergedAttrs = new List<AssetAttributeDetail>();

                for (InvoiceLineDetail ld : ps.lines) {
                    if (ld.assetId == null || seenAssetIds.contains(ld.assetId)) continue;
                    seenAssetIds.add(ld.assetId);
                    Id aid = (Id) ld.assetId;
                    List<AssetAttributeDetail> attrs = assetToAttrs.get(aid);
                    if (attrs == null || attrs.isEmpty()) continue;
                    for (AssetAttributeDetail aad : attrs) {
                        String lk = aad.label != null ? aad.label.toLowerCase() : 'null';
                        if (seenLabels.contains(lk)) continue;
                        seenLabels.add(lk);
                        mergedAttrs.add(aad);
                    }
                }

                if (!mergedAttrs.isEmpty()) {
                    AssetBlock block = new AssetBlock();
                    block.assetId   = 'merged';
                    block.assetName = null;
                    block.attributes = mergedAttrs;
                    ps.assetBlocks = new List<AssetBlock>{ block };
                }
            }

            // Sort and assemble
            List<ProductSummary> sorted = new List<ProductSummary>();
            for (String key : productOrder) sorted.add(productMap.get(key));
            sorted.sort(new ProductSummaryComparator());

            InvoiceSummaryResult result = new InvoiceSummaryResult();
            result.currencyCode         = inv.CurrencyIsoCode;
            result.totalLines           = lines.size();

            for (ProductSummary ps : sorted) {
                result.products.add(ps);
                result.grandSubtotal += ps.subtotal;
                result.grandTax      += ps.taxAmount;
                result.grandTotal    += ps.totalWithTax;
            }

            return result;

        } catch (Exception e) {
            throw new AuraHandledException('Error fetching invoice product summary: ' + e.getMessage());
        }
    }
}