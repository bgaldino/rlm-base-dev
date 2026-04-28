/**
 * Procedure-plan Apex post-hook (RevSignaling): consumes the per-line ItemInstallBaseAmount__c
 * written by RLM_AssetStatePeriodPreSignalingHook, then computes and writes all derived line-level
 * metrics (NetNew / Expansion / Churned / Renewal amounts and ARRs, NRR, ARR, iARR) and the
 * SalesTransaction header rollup (totals + Software / Hardware / Services breakdown) via
 * Context.IndustriesContext.
 *
 * This class contains the non-install-base half of the original RLM_AssetStatePeriodSignalingHook;
 * the install-base computation lives in RLM_AssetStatePeriodPreSignalingHook.
 */
global with sharing class RLM_AssetStatePeriodPostSignalingHook implements RevSignaling.SignalingApexProcessor {
    @TestVisible
    static final String TAG_SALES_TRANSACTION = 'SalesTransaction';
    @TestVisible
    static final String TAG_SALES_TRANSACTION_ITEM = 'SalesTransactionItem';
    @TestVisible
    static final String ATTR_ITEM_INSTALL_BASE = 'ItemInstallBaseAmount__c';

    /** SalesTransaction (header) context attributes — rolled up from line-level Item* metrics. */
    @TestVisible
    static final String ATTR_ST_NET_NEW_AMOUNT = 'NetNewAmount__c';
    @TestVisible
    static final String ATTR_ST_EXPANSION_AMOUNT = 'ExpansionAmount__c';
    @TestVisible
    static final String ATTR_ST_CHURNED_AMOUNT = 'ChurnedAmount__c';
    @TestVisible
    static final String ATTR_ST_RENEWAL_AMOUNT = 'RenewalAmount__c';
    @TestVisible
    static final String ATTR_ST_NRR = 'TotalNRR__c';
    @TestVisible
    static final String ATTR_ST_ARR = 'TotalARR__c';
    @TestVisible
    static final String ATTR_ST_NET_NEW_ARR = 'NetNewARR__c';
    @TestVisible
    static final String ATTR_ST_EXPANSION_ARR = 'ExpansionARR__c';
    @TestVisible
    static final String ATTR_ST_CHURNED_ARR = 'ChurnedARR__c';
    @TestVisible
    static final String ATTR_ST_RENEWAL_ARR = 'RenewalARR__c';
    @TestVisible
    static final String ATTR_ST_I_ARR = 'iARR__c';

    private static final Integer AMOUNT_SCALE = 2;
    private static final String DBG = 'RLM_AssetStatePeriodPostSignalingHook';

    /** Null-coalesce a Decimal to 0. Keeps arithmetic and setScale calls NPE-free for missing context values. */
    private static Decimal nzd(Decimal d) {
        return d == null ? 0 : d;
    }

    global RevSignaling.TransactionResponse execute(RevSignaling.TransactionRequest request) {
        System.debug(LoggingLevel.DEBUG, DBG + '.execute: enter');
        RevSignaling.TransactionResponse response = new RevSignaling.TransactionResponse();
        if (request == null || String.isBlank(request.ctxInstanceId)) {
            System.debug(LoggingLevel.WARN, DBG + '.execute: missing request or ctxInstanceId');
            response.status = RevSignaling.TransactionStatus.FAILED;
            response.message = 'Missing TransactionRequest or ctxInstanceId.';
            return response;
        }

        String contextId = request.ctxInstanceId;
        System.debug(LoggingLevel.DEBUG, DBG + '.execute: ctxInstanceId=' + contextId);
        Context.IndustriesContext industriesContext = new Context.IndustriesContext();

        try {
            Map<String, Object> salesTransactionNode = queryFirstSalesTransactionNode(industriesContext, contextId);
            if (salesTransactionNode == null) {
                System.debug(LoggingLevel.WARN, DBG + '.execute: no SalesTransaction node');
                response.status = RevSignaling.TransactionStatus.FAILED;
                response.message = 'Could not resolve SalesTransaction context.';
                return response;
            }

            List<LineContextRow> lines = querySalesTransactionItems(industriesContext, contextId);
            System.debug(LoggingLevel.DEBUG, DBG + '.execute: salesTransactionItem rows=' + lines.size());
            List<Map<String, Object>> nodeUpdates = new List<Map<String, Object>>();
            TransactionRollupTotals rollup = new TransactionRollupTotals();

            Integer lineIndex = 0;
            for (LineContextRow line : lines) {
                lineIndex++;
                if (line == null || line.skip) {
                    System.debug(LoggingLevel.DEBUG, DBG + '.execute: line ' + lineIndex + ' skipped (null or flagged)');
                    continue;
                }
                Date lineStart = line.lineStartDate;
                if (lineStart == null) {
                    System.debug(LoggingLevel.DEBUG, DBG + '.execute: line ' + lineIndex + ' no StartDate — skipping');
                    continue;
                }

                Decimal total;
                Decimal netNewAmount = 0;
                Decimal expansionAmount = 0;
                Decimal churnedAmount = 0;
                Decimal renewalAmount = 0;
                Decimal nrr = 0;
                Decimal arr = 0;
                Decimal netNewARR = 0;
                Decimal expansionARR = 0;
                Decimal churnedARR = 0;
                Decimal renewalARR = 0;
                Decimal iARR = 0;

                if (line.sellingModelType == 'OneTime') {
                    // OneTime lines have no install base; only NRR is populated from net total price.
                    total = 0;
                    nrr = nzd(line.netTotalPrice);
                    System.debug(
                        LoggingLevel.DEBUG,
                        DBG + '.execute: line ' + lineIndex + ' OneTime — total=0 nrr=' + nrr
                    );
                } else {
                    total = nzd(line.installBaseAmount);
                    System.debug(
                        LoggingLevel.DEBUG,
                        DBG + '.execute: line ' + lineIndex + ' installBase from context=' + total
                    );

                    netNewAmount = nzd(calcNetNewAmount(line.transactionActionType, total, line.netTotalPrice));
                    expansionAmount = nzd(calcExpansionAmount(line.transactionActionType, total, line.netTotalPrice, line.startQuantity, line.endQuantity));
                    churnedAmount = nzd(calcChurnedAmount(line.transactionActionType, total, line.netTotalPrice, line.startQuantity, line.endQuantity));
                    renewalAmount = nzd(calcRenewalAmount(line.transactionActionType, total, line.netTotalPrice));
                    arr = nzd(calculateARR(line.pricingTermUnit, line.pricingTerm, line.pricingTermCount, line.netTotalPrice));
                    netNewARR = nzd(calculateARR(line.pricingTermUnit, line.pricingTerm, line.pricingTermCount, netNewAmount));
                    expansionARR = nzd(calculateARR(line.pricingTermUnit, line.pricingTerm, line.pricingTermCount, expansionAmount));
                    churnedARR = nzd(calculateARR(line.pricingTermUnit, line.pricingTerm, line.pricingTermCount, churnedAmount));
                    renewalARR = nzd(calculateARR(line.pricingTermUnit, line.pricingTerm, line.pricingTermCount, renewalAmount));
                    iARR = netNewARR + expansionARR - churnedARR;
                    System.debug(
                        LoggingLevel.DEBUG,
                        DBG +
                            '.execute: line ' + lineIndex +
                            ' metrics total=' + total +
                            ' netNew=' + netNewAmount +
                            ' expansion=' + expansionAmount +
                            ' churned=' + churnedAmount +
                            ' renewal=' + renewalAmount +
                            ' arr=' + arr +
                            ' netNewARR=' + netNewARR +
                            ' expansionARR=' + expansionARR +
                            ' churnedARR=' + churnedARR +
                            ' renewalARR=' + renewalARR
                    );
                }

                rollup.accumulateLine(
                    total, netNewAmount, expansionAmount, churnedAmount, renewalAmount,
                    nrr, arr, netNewARR, expansionARR, churnedARR, renewalARR, iARR, line.productFamily
                );

                List<Object> pathForUpdate = line.pathForFieldUpdate();
                if (pathForUpdate == null || pathForUpdate.isEmpty()) {
                    System.debug(LoggingLevel.DEBUG, DBG + '.execute: line ' + lineIndex + ' no pathForFieldUpdate');
                    continue;
                }

                List<Object> attributesForUpdate = new List<Object>();
                // Rewrite the install base too so the line attribute reflects the same scaled value
                // we used for the rollup math (also covers the rare case where the pre-hook write
                // hasn't fully reconciled to the line node yet).
                attributesForUpdate.add(scaledAttribute(ATTR_ITEM_INSTALL_BASE, total));
                attributesForUpdate.add(scaledAttribute('ItemNetNewAmount__c', netNewAmount));
                attributesForUpdate.add(scaledAttribute('ItemExpansionAmount__c', expansionAmount));
                attributesForUpdate.add(scaledAttribute('ItemChurnedAmount__c', churnedAmount));
                attributesForUpdate.add(scaledAttribute('ItemRenewalAmount__c', renewalAmount));
                attributesForUpdate.add(scaledAttribute('ItemNRR__c', nrr));
                attributesForUpdate.add(scaledAttribute('ItemARR__c', arr));
                attributesForUpdate.add(scaledAttribute('ItemNetNewARR__c', netNewARR));
                attributesForUpdate.add(scaledAttribute('ItemExpansionARR__c', expansionARR));
                attributesForUpdate.add(scaledAttribute('ItemChurnedARR__c', churnedARR));
                attributesForUpdate.add(scaledAttribute('ItemRenewalARR__c', renewalARR));
                attributesForUpdate.add(scaledAttribute('ItemiARR__c', iARR));

                nodeUpdates.add(
                    new Map<String, Object>{
                        'nodePath' => new Map<String, Object>{ 'dataPath' => pathForUpdate },
                        'attributes' => attributesForUpdate
                    }
                );
            }

            appendSalesTransactionNodeUpdate(nodeUpdates, salesTransactionNode, rollup);

            if (!nodeUpdates.isEmpty()) {
                System.debug(LoggingLevel.DEBUG, DBG + '.execute: updateContextAttributes count=' + nodeUpdates.size());
                industriesContext.updateContextAttributes(
                    new Map<String, Object>{
                        'contextId' => contextId,
                        'nodePathAndAttributes' => nodeUpdates
                    }
                );
                System.debug(LoggingLevel.DEBUG, DBG + '.execute: updateContextAttributes done');
            } else {
                System.debug(LoggingLevel.DEBUG, DBG + '.execute: no node updates to submit');
            }

            response.status = RevSignaling.TransactionStatus.SUCCESS;
            response.message = 'Data path and attributes updated for ' + nodeUpdates.size() + ' node(s).';
            System.debug(LoggingLevel.DEBUG, DBG + '.execute: SUCCESS message=' + response.message);
        } catch (Exception e) {
            System.debug(LoggingLevel.ERROR, DBG + '.execute: FAILED ' + e.getMessage() + ' ' + e.getStackTraceString());
            response.status = RevSignaling.TransactionStatus.FAILED;
            response.message = 'RLM_AssetStatePeriodPostSignalingHook: ' + e.getMessage();
        }

        System.debug(LoggingLevel.DEBUG, DBG + '.execute: exit status=' + response.status);
        return response;
    }

    private static Map<String, Object> scaledAttribute(String attrName, Decimal value) {
        return new Map<String, Object>{
            'attributeName' => attrName,
            'attributeValue' => String.valueOf(nzd(value).setScale(AMOUNT_SCALE, RoundingMode.HALF_UP))
        };
    }

    @TestVisible
    static Boolean isOneTime(String sellingModelType) {
        return sellingModelType != null && 'OneTime'.equalsIgnoreCase(sellingModelType.trim());
    }

    /**
     * Queries SalesTransaction tag and returns the first node map. Used here for the SalesTransaction
     * dataPath needed to write header-level rollup attributes.
     */
    private static Map<String, Object> queryFirstSalesTransactionNode(
        Context.IndustriesContext industriesContext,
        String contextId
    ) {
        Map<String, Object> outMap = industriesContext.queryTags(
            new Map<String, Object>{
                'contextId' => contextId,
                'tags' => new List<String>{ TAG_SALES_TRANSACTION }
            }
        );
        Map<String, Object> queryResult = (Map<String, Object>) outMap.get('queryResult');
        if (queryResult == null) {
            return null;
        }
        List<Object> stNodes = (List<Object>) queryResult.get(TAG_SALES_TRANSACTION);
        if (stNodes == null || stNodes.isEmpty()) {
            return null;
        }
        return (Map<String, Object>) stNodes[0];
    }

    /**
     * Returns the SalesTransaction node path that IndustriesContext.updateContextAttributes accepts
     * for header-level writes: [QuoteId]. The queryTags dataPath is [contextInstanceId, QuoteId]; we
     * strip the context-instance root because including it causes silent drops.
     */
    @TestVisible
    static List<Object> salesTransactionDataPath(Map<String, Object> salesTransactionNode) {
        if (salesTransactionNode == null) {
            return null;
        }
        List<Object> dataPath = (List<Object>) salesTransactionNode.get('dataPath');
        if (dataPath == null || dataPath.size() < 2) {
            return null;
        }
        return new List<Object>{ dataPath[1] };
    }

    private static List<LineContextRow> querySalesTransactionItems(
        Context.IndustriesContext industriesContext,
        String contextId
    ) {
        List<LineContextRow> rows = new List<LineContextRow>();
        Map<String, Object> outMap = industriesContext.queryTags(
            new Map<String, Object>{
                'contextId' => contextId,
                'tags' => new List<String>{ TAG_SALES_TRANSACTION_ITEM }
            }
        );
        Map<String, Object> queryResult = (Map<String, Object>) outMap.get('queryResult');
        if (queryResult == null) {
            return rows;
        }
        List<Object> itemNodes = (List<Object>) queryResult.get(TAG_SALES_TRANSACTION_ITEM);
        if (itemNodes == null) {
            return rows;
        }
        for (Object itemObj : itemNodes) {
            rows.add(buildLineContextRow((Map<String, Object>) itemObj));
        }
        return rows;
    }

    /** Annualized recurring revenue from pricing term and amount. */
    private static Decimal calculateARR(String pricingTermUnit, Decimal pricingTerm, Decimal pricingTermCount, Decimal amount) {
        Decimal amt = nzd(amount);
        Decimal term = nzd(pricingTerm);
        Decimal termCount = nzd(pricingTermCount);
        Decimal arr = 0;
        if (pricingTermUnit == 'Months' && termCount > 0 && term > 0) {
            arr = (amt / (term * termCount)) * 12;
        } else if (pricingTermUnit == 'Annual' && termCount > 0 && term > 0) {
            arr = amt / (termCount / term);
        }
        return arr;
    }

    private static Decimal calcNetNewAmount(String transactionActionType, Decimal installBaseAmount, Decimal netTotalPrice) {
        Decimal installBase = nzd(installBaseAmount);
        Decimal netTotal = nzd(netTotalPrice);
        if (String.isBlank(transactionActionType) && installBase <= 0) {
            return netTotal;
        }
        return 0;
    }

    private static Decimal calcExpansionAmount(
        String transactionActionType,
        Decimal installBaseAmount,
        Decimal netTotalPrice,
        Decimal startQuantity,
        Decimal endQuantity
    ) {
        Decimal installBase = nzd(installBaseAmount);
        Decimal netTotal = nzd(netTotalPrice);
        if (String.isBlank(transactionActionType) && installBase > 0) {
            return netTotal;
        }
        if (transactionActionType == 'Amend' && installBase > 0) {
            return netTotal;
        }
        if (transactionActionType == 'Renewal' && installBase > 0 && installBase < netTotal) {
            return netTotal - installBase;
        }
        return 0;
    }

    private static Decimal calcChurnedAmount(
        String transactionActionType,
        Decimal installBaseAmount,
        Decimal netTotalPrice,
        Decimal startQuantity,
        Decimal endQuantity
    ) {
        Decimal installBase = nzd(installBaseAmount);
        Decimal netTotal = nzd(netTotalPrice);
        Decimal startQty = nzd(startQuantity);
        Decimal endQty = nzd(endQuantity);
        if (transactionActionType == 'Cancel') {
            return netTotal.abs();
        }
        if (transactionActionType == 'Amend' && installBase > 0 && startQty > endQty) {
            return netTotal.abs();
        }
        if (transactionActionType == 'Renewal' && installBase > netTotal) {
            return (netTotal - installBase).abs();
        }
        return 0;
    }

    private static Decimal calcRenewalAmount(String transactionActionType, Decimal installBaseAmount, Decimal netTotalPrice) {
        Decimal installBase = nzd(installBaseAmount);
        if (transactionActionType == 'Renewal' && installBase > 0) {
            return installBase;
        }
        return 0;
    }

    private static Id tryParseId(String s) {
        if (String.isBlank(s)) {
            return null;
        }
        try {
            return Id.valueOf(s.trim());
        } catch (Exception e) {
            return null;
        }
    }

    @TestVisible
    static Id parseIdTag(Map<String, Object> tagValue, String tagKey) {
        if (tagValue == null || !tagValue.containsKey(tagKey)) {
            return null;
        }
        Object raw = tagValue.get(tagKey);
        if (raw instanceof Map<String, Object>) {
            Map<String, Object> tagInner = (Map<String, Object>) raw;
            Object tv = tagInner.get('tagValue');
            if (tv instanceof String) {
                return tryParseId((String) tv);
            }
            return null;
        }
        if (raw instanceof String) {
            return tryParseId((String) raw);
        }
        return null;
    }

    @TestVisible
    static Date parseContextDate(Map<String, Object> tagValue, String tagKey) {
        if (tagValue == null || !tagValue.containsKey(tagKey)) {
            return null;
        }
        Object raw = tagValue.get(tagKey);
        String s = null;
        if (raw instanceof Map<String, Object>) {
            Object tv = ((Map<String, Object>) raw).get('tagValue');
            s = String.valueOf(tv);
        } else if (raw instanceof String) {
            s = (String) raw;
        }
        if (String.isBlank(s)) {
            return null;
        }
        s = s.trim();
        try {
            if (s.length() > 10 && 'T'.equals(s.substring(10, 11))) {
                return Date.valueOf(s.substring(0, 10));
            }
            return Date.valueOf(s);
        } catch (Exception e) {
            return null;
        }
    }

    @TestVisible
    static String parseContextString(Map<String, Object> tagValue, String tagKey) {
        if (tagValue == null || !tagValue.containsKey(tagKey)) {
            return null;
        }
        Object raw = tagValue.get(tagKey);
        if (raw instanceof Map<String, Object>) {
            Object tv = ((Map<String, Object>) raw).get('tagValue');
            if (tv instanceof String) {
                String s = (String) tv;
                return String.isBlank(s) ? null : s.trim();
            }
            return null;
        }
        if (raw instanceof String) {
            String s = (String) raw;
            return String.isBlank(s) ? null : s.trim();
        }
        return null;
    }

    /**
     * Reads a Decimal from a context tagValue map. Tolerates inner Decimal, String, and the
     * stringified scaled values produced by attribute writes (e.g. "12345.67").
     */
    @TestVisible
    static Decimal parseContextDecimal(Map<String, Object> tagValue, String tagKey) {
        if (tagValue == null || !tagValue.containsKey(tagKey)) {
            return null;
        }
        Object raw = tagValue.get(tagKey);
        Object value = raw instanceof Map<String, Object>
            ? ((Map<String, Object>) raw).get('tagValue')
            : raw;
        if (value == null) {
            return null;
        }
        if (value instanceof Decimal) {
            return (Decimal) value;
        }
        if (value instanceof Integer) {
            return Decimal.valueOf((Integer) value);
        }
        if (value instanceof Long) {
            return Decimal.valueOf((Long) value);
        }
        if (value instanceof Double) {
            return Decimal.valueOf((Double) value);
        }
        if (value instanceof String) {
            String s = ((String) value).trim();
            if (String.isBlank(s)) {
                return null;
            }
            try {
                return Decimal.valueOf(s);
            } catch (Exception e) {
                return null;
            }
        }
        return null;
    }

    @TestVisible
    private static LineContextRow buildLineContextRow(Map<String, Object> itemNode) {
        LineContextRow row = new LineContextRow();
        row.dataPathFull = (List<Object>) itemNode.get('dataPath');
        row.skip = false;

        Map<String, Object> tags = (Map<String, Object>) itemNode.get('tagValue');
        if (tags == null) {
            row.skip = true;
            return row;
        }
        if (isDeletedSalesTransactionItem(tags)) {
            row.skip = true;
            return row;
        }

        row.lineStartDate = parseContextDate(tags, 'EffectiveFrom');
        row.lineEndDate = parseContextDate(tags, 'EffectiveTo');
        row.productId = parseIdTag(tags, 'Product');
        row.sellingModelType = parseContextString(tags, 'SellingModelType');
        row.transactionActionType = parseContextString(tags, 'SalesTransactionActionType');
        row.pricingTermUnit = parseContextString(tags, 'PricingTermUnit');
        row.pricingTerm = parseContextDecimal(tags, 'PricingTerm');
        row.pricingTermCount = parseContextDecimal(tags, 'PricingTermCount');
        row.netTotalPrice = parseContextDecimal(tags, 'ItemNetTotalPrice');
        row.startQuantity = parseContextDecimal(tags, 'ItemStartQuantity');
        row.endQuantity = parseContextDecimal(tags, 'ItemEndQuantity');
        row.productFamily = parseContextString(tags, 'ItemProductFamily__c');
        row.installBaseAmount = parseContextDecimal(tags, ATTR_ITEM_INSTALL_BASE);
        return row;
    }

    private static Boolean isDeletedSalesTransactionItem(Map<String, Object> tags) {
        String dml = dmlStatusFromTagMap(tags, 'LineItemPath');
        if ('DELETED'.equalsIgnoreCase(dml)) {
            return true;
        }
        dml = dmlStatusFromTagMap(tags, 'LineItem');
        return 'DELETED'.equalsIgnoreCase(dml);
    }

    private static String dmlStatusFromTagMap(Map<String, Object> tags, String key) {
        if (!tags.containsKey(key)) {
            return null;
        }
        Object raw = tags.get(key);
        if (!(raw instanceof Map<String, Object>)) {
            return null;
        }
        Object dml = ((Map<String, Object>) raw).get('dmlStatus');
        return dml instanceof String ? (String) dml : null;
    }

    /**
     * Builds the attribute list for the SalesTransaction header node from rolled-up line totals.
     */
    @TestVisible
    static List<Object> buildSalesTransactionAttributes(TransactionRollupTotals rollup) {
        List<Object> attrs = new List<Object>();
        attrs.add(scaledAttribute(ATTR_ST_NET_NEW_AMOUNT, rollup.netNewAmount));
        attrs.add(scaledAttribute(ATTR_ST_EXPANSION_AMOUNT, rollup.expansionAmount));
        attrs.add(scaledAttribute(ATTR_ST_CHURNED_AMOUNT, rollup.churnedAmount));
        attrs.add(scaledAttribute(ATTR_ST_RENEWAL_AMOUNT, rollup.renewalAmount));
        attrs.add(scaledAttribute(ATTR_ST_NRR, rollup.nrr));
        attrs.add(scaledAttribute(ATTR_ST_ARR, rollup.arr));
        attrs.add(scaledAttribute(ATTR_ST_NET_NEW_ARR, rollup.netNewARR));
        attrs.add(scaledAttribute(ATTR_ST_EXPANSION_ARR, rollup.expansionARR));
        attrs.add(scaledAttribute(ATTR_ST_CHURNED_ARR, rollup.churnedARR));
        attrs.add(scaledAttribute(ATTR_ST_RENEWAL_ARR, rollup.renewalARR));
        attrs.add(scaledAttribute(ATTR_ST_I_ARR, rollup.iARR));
        attrs.add(scaledAttribute('SoftwareTotal__c', rollup.softwareAmount));
        attrs.add(scaledAttribute('HardwareTotal__c', rollup.hardwareAmount));
        attrs.add(scaledAttribute('ServicesTotal__c', rollup.servicesAmount));
        return attrs;
    }

    /**
     * Appends a single header-level node update for the SalesTransaction to the nodeUpdates list.
     */
    private static void appendSalesTransactionNodeUpdate(
        List<Map<String, Object>> nodeUpdates,
        Map<String, Object> salesTransactionNode,
        TransactionRollupTotals rollup
    ) {
        List<Object> stPath = salesTransactionDataPath(salesTransactionNode);
        if (stPath == null) {
            System.debug(LoggingLevel.WARN, DBG + '.appendSalesTransactionNodeUpdate: no SalesTransaction dataPath — skipping header update');
            return;
        }
        nodeUpdates.add(
            new Map<String, Object>{
                'nodePath' => new Map<String, Object>{ 'dataPath' => stPath },
                'attributes' => buildSalesTransactionAttributes(rollup)
            }
        );
        System.debug(
            LoggingLevel.DEBUG,
            DBG + '.appendSalesTransactionNodeUpdate: appended header rollup (' + rollup.contributingLineCount + ' lines contributed)'
        );
    }

    /**
     * Running totals of per-line revenue metrics, accumulated during the line loop
     * and written to the SalesTransaction header node after all lines are processed.
     */
    @TestVisible
    class TransactionRollupTotals {
        public Decimal netNewAmount = 0;
        public Decimal expansionAmount = 0;
        public Decimal churnedAmount = 0;
        public Decimal renewalAmount = 0;
        public Decimal nrr = 0;
        public Decimal arr = 0;
        public Decimal netNewARR = 0;
        public Decimal expansionARR = 0;
        public Decimal churnedARR = 0;
        public Decimal renewalARR = 0;
        public Decimal iARR = 0;
        public Decimal softwareAmount = 0;
        public Decimal hardwareAmount = 0;
        public Decimal servicesAmount = 0;
        public Integer contributingLineCount = 0;

        public void accumulateLine(
            Decimal lineTotal, Decimal lineNetNew, Decimal lineExpansion,
            Decimal lineChurned, Decimal lineRenewal, Decimal lineNrr,
            Decimal lineArr, Decimal lineNetNewArr, Decimal lineExpansionArr,
            Decimal lineChurnedArr, Decimal lineRenewalArr, Decimal lineIarr, String lineProductFamily
        ) {
            netNewAmount += nz(lineNetNew);
            expansionAmount += nz(lineExpansion);
            churnedAmount += nz(lineChurned);
            renewalAmount += nz(lineRenewal);
            nrr += nz(lineNrr);
            arr += nz(lineArr);
            netNewARR += nz(lineNetNewArr);
            expansionARR += nz(lineExpansionArr);
            churnedARR += nz(lineChurnedArr);
            renewalARR += nz(lineRenewalArr);
            iARR += nz(lineIarr);
            contributingLineCount++;
            if (lineProductFamily == 'Software') {
                softwareAmount += nz(lineTotal);
            } else if (lineProductFamily == 'Hardware') {
                hardwareAmount += nz(lineTotal);
            } else if (lineProductFamily == 'Services') {
                servicesAmount += nz(lineTotal);
            }
        }

        private Decimal nz(Decimal d) {
            return d == null ? 0 : d;
        }
    }

    /**
     * Per SalesTransactionItem context node: dates, dataPath, classification fields, pricing,
     * and the install-base amount written by the pre-hook (read back from context via tagValue).
     */
    @TestVisible
    public class LineContextRow {
        public Date lineStartDate;
        public Date lineEndDate;
        public Id productId;
        public String sellingModelType;
        public String transactionActionType;
        public String pricingTermUnit;
        public Decimal pricingTerm;
        public Decimal pricingTermCount;
        public Decimal netTotalPrice;
        public Decimal startQuantity;
        public Decimal endQuantity;
        public String productFamily;
        public Decimal installBaseAmount;
        public List<Object> dataPathFull;
        public Boolean skip;

        /**
         * Trims the context-instance root from the queryTags dataPath so
         * IndustriesContext.updateContextAttributes sees [QuoteId, QLI Id]. Including the
         * context-instance id as the first segment causes silent drops.
         */
        public List<Object> pathForFieldUpdate() {
            if (dataPathFull == null || dataPathFull.size() < 3) {
                return null;
            }
            return new List<Object>{ dataPathFull[1], dataPathFull[2] };
        }
    }
}
