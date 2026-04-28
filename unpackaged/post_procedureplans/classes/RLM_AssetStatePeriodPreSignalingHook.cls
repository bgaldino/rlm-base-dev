/**
 * Procedure-plan Apex pre-hook (RevSignaling): for each SalesTransactionItem, loads overlapping
 * AssetStatePeriod rows for the transaction Account + line Product, pro-rates Mrr by inclusive
 * calendar-day overlap (whole-months + partial-month remainders), and writes
 * ItemInstallBaseAmount__c per line via Context.IndustriesContext so the downstream post-hook
 * can read it back when calculating NetNew / Expansion / Churned / Renewal / ARR metrics.
 *
 * This class is the install-base computation slice extracted from RLM_AssetStatePeriodSignalingHook;
 * all non-install-base logic lives in RLM_AssetStatePeriodPostSignalingHook.
 */
global with sharing class RLM_AssetStatePeriodPreSignalingHook implements RevSignaling.SignalingApexProcessor {
    @TestVisible
    static final String TAG_SALES_TRANSACTION = 'SalesTransaction';
    @TestVisible
    static final String TAG_SALES_TRANSACTION_ITEM = 'SalesTransactionItem';
    @TestVisible
    static final String ATTR_ITEM_INSTALL_BASE = 'ItemInstallBaseAmount__c';

    private static final Integer AMOUNT_SCALE = 2;
    private static final String DBG = 'RLM_AssetStatePeriodPreSignalingHook';

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
            Id accountId = resolveAccountIdFromNode(salesTransactionNode);
            if (accountId == null) {
                System.debug(LoggingLevel.WARN, DBG + '.execute: account not resolved');
                response.status = RevSignaling.TransactionStatus.FAILED;
                response.message = 'Could not resolve Account from SalesTransaction context.';
                return response;
            }
            System.debug(LoggingLevel.DEBUG, DBG + '.execute: accountId=' + accountId);

            List<LineContextRow> lines = querySalesTransactionItems(industriesContext, contextId);
            System.debug(LoggingLevel.DEBUG, DBG + '.execute: salesTransactionItem rows=' + lines.size());
            List<Map<String, Object>> nodeUpdates = new List<Map<String, Object>>();

            Integer lineIndex = 0;
            for (LineContextRow line : lines) {
                lineIndex++;
                if (line == null || line.skip) {
                    System.debug(LoggingLevel.DEBUG, DBG + '.execute: line ' + lineIndex + ' skipped (null or flagged)');
                    continue;
                }
                Date lineStart = line.lineStartDate;
                Date lineEnd = line.lineEndDate != null ? line.lineEndDate : line.lineStartDate;
                if (lineStart == null) {
                    System.debug(LoggingLevel.DEBUG, DBG + '.execute: line ' + lineIndex + ' no StartDate — skipping');
                    continue;
                }
                if (lineEnd == null || lineEnd < lineStart) {
                    lineEnd = lineStart;
                }

                Decimal total;
                if (line.sellingModelType == 'OneTime') {
                    // Per requirements, do not query AssetStatePeriod when SellingModelType is OneTime.
                    System.debug(
                        LoggingLevel.DEBUG,
                        DBG + '.execute: line ' + lineIndex + ' OneTime — skip ASP query, total=0'
                    );
                    total = 0;
                } else {
                    total = nzd(computeInstallBaseForLine(accountId, lineStart, lineEnd, line.productId));
                    System.debug(
                        LoggingLevel.DEBUG,
                        DBG + '.execute: line ' + lineIndex + ' computed total=' + total + ' productId=' + line.productId
                    );
                }

                List<Object> pathForUpdate = line.pathForFieldUpdate();
                if (pathForUpdate == null || pathForUpdate.isEmpty()) {
                    System.debug(LoggingLevel.DEBUG, DBG + '.execute: line ' + lineIndex + ' no pathForFieldUpdate');
                    continue;
                }

                nodeUpdates.add(
                    new Map<String, Object>{
                        'nodePath' => new Map<String, Object>{ 'dataPath' => pathForUpdate },
                        'attributes' => new List<Object>{
                            new Map<String, Object>{
                                'attributeName' => ATTR_ITEM_INSTALL_BASE,
                                'attributeValue' => String.valueOf(nzd(total).setScale(AMOUNT_SCALE, RoundingMode.HALF_UP))
                            }
                        }
                    }
                );
            }

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
            response.message = 'ItemInstallBaseAmount__c written for ' + nodeUpdates.size() + ' line(s).';
            System.debug(LoggingLevel.DEBUG, DBG + '.execute: SUCCESS message=' + response.message);
        } catch (Exception e) {
            System.debug(LoggingLevel.ERROR, DBG + '.execute: FAILED ' + e.getMessage() + ' ' + e.getStackTraceString());
            response.status = RevSignaling.TransactionStatus.FAILED;
            response.message = 'RLM_AssetStatePeriodPreSignalingHook: ' + e.getMessage();
        }

        System.debug(LoggingLevel.DEBUG, DBG + '.execute: exit status=' + response.status);
        return response;
    }

    /**
     * Queries SalesTransaction tag and returns the first node map (used for Account resolution).
     */
    private static Map<String, Object> queryFirstSalesTransactionNode(
        Context.IndustriesContext industriesContext,
        String contextId
    ) {
        System.debug(LoggingLevel.DEBUG, DBG + '.queryFirstSalesTransactionNode: enter contextId=' + contextId);
        Map<String, Object> outMap = industriesContext.queryTags(
            new Map<String, Object>{
                'contextId' => contextId,
                'tags' => new List<String>{ TAG_SALES_TRANSACTION }
            }
        );
        Map<String, Object> queryResult = (Map<String, Object>) outMap.get('queryResult');
        if (queryResult == null) {
            System.debug(LoggingLevel.DEBUG, DBG + '.queryFirstSalesTransactionNode: queryResult null');
            return null;
        }
        List<Object> stNodes = (List<Object>) queryResult.get(TAG_SALES_TRANSACTION);
        if (stNodes == null || stNodes.isEmpty()) {
            System.debug(LoggingLevel.DEBUG, DBG + '.queryFirstSalesTransactionNode: no SalesTransaction nodes');
            return null;
        }
        Map<String, Object> firstNode = (Map<String, Object>) stNodes[0];
        System.debug(LoggingLevel.DEBUG, DBG + '.queryFirstSalesTransactionNode: exit node found');
        return firstNode;
    }

    /** Resolves Account (or QuoteAccount) Id from an already-fetched SalesTransaction node. */
    @TestVisible
    static Id resolveAccountIdFromNode(Map<String, Object> salesTransactionNode) {
        System.debug(LoggingLevel.DEBUG, DBG + '.resolveAccountIdFromNode: enter');
        if (salesTransactionNode == null) {
            return null;
        }
        Map<String, Object> tagValue = (Map<String, Object>) salesTransactionNode.get('tagValue');
        if (tagValue == null) {
            return null;
        }
        Id accountId = parseIdTag(tagValue, 'Account');
        if (accountId == null) {
            accountId = parseIdTag(tagValue, 'QuoteAccount');
        }
        System.debug(LoggingLevel.DEBUG, DBG + '.resolveAccountIdFromNode: exit accountId=' + accountId);
        return accountId;
    }

    private static List<LineContextRow> querySalesTransactionItems(
        Context.IndustriesContext industriesContext,
        String contextId
    ) {
        System.debug(LoggingLevel.DEBUG, DBG + '.querySalesTransactionItems: enter contextId=' + contextId);
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
        System.debug(LoggingLevel.DEBUG, DBG + '.querySalesTransactionItems: exit parsedRows=' + rows.size());
        return rows;
    }

    /**
     * For an Account+Product+date window, returns the sum of pro-rated Mrr from overlapping
     * AssetStatePeriod rows. Returns 0 when productId is null (per requirements: only query ASP
     * when the line carries a Product).
     */
    private static Decimal computeInstallBaseForLine(
        Id accountId,
        Date lineStart,
        Date lineEnd,
        Id productId
    ) {
        System.debug(
            LoggingLevel.DEBUG,
            DBG + '.computeInstallBaseForLine: enter accountId=' + accountId + ' lineStart=' + lineStart + ' lineEnd=' + lineEnd + ' productId=' + productId
        );
        if (productId == null) {
            System.debug(LoggingLevel.DEBUG, DBG + '.computeInstallBaseForLine: productId null — return 0');
            return 0;
        }

        List<AssetStatePeriod> periods = [
            SELECT StartDate, EndDate, Amount, Mrr
            FROM AssetStatePeriod
            WHERE Asset.AccountId = :accountId
                AND Asset.Product2Id = :productId
                AND StartDate <= :lineEnd
                AND EndDate >= :lineStart
        ];

        System.debug(LoggingLevel.DEBUG, DBG + '.computeInstallBaseForLine: ASP rows=' + periods.size());
        Decimal sum = 0;
        for (AssetStatePeriod asp : periods) {
            Date aspS = asp.StartDate == null ? null : asp.StartDate.dateGMT();
            Date aspE = asp.EndDate == null ? null : asp.EndDate.dateGMT();
            sum += proratedAmountForOverlap(lineStart, lineEnd, aspS, aspE, asp.Mrr);
        }
        System.debug(LoggingLevel.DEBUG, DBG + '.computeInstallBaseForLine: exit sum=' + sum);
        return sum;
    }

    /** Inclusive calendar-day count between two dates (end >= start). Returns 0 if invalid. */
    @TestVisible
    static Integer inclusiveDayCount(Date startDate, Date endDate) {
        if (startDate == null || endDate == null || endDate < startDate) {
            return 0;
        }
        return startDate.daysBetween(endDate) + 1;
    }

    /** Inclusive overlap of [lineStart,lineEnd] and [aspStart,aspEnd]. Returns null if invalid or no overlap. */
    private static List<Date> overlapInclusiveSegment(
        Date lineStart,
        Date lineEnd,
        Date aspStart,
        Date aspEnd
    ) {
        if (lineStart == null || lineEnd == null || aspStart == null || aspEnd == null) {
            return null;
        }
        if (lineEnd < lineStart || aspEnd < aspStart) {
            return null;
        }
        Date ovStart = lineStart > aspStart ? lineStart : aspStart;
        Date ovEnd = lineEnd < aspEnd ? lineEnd : aspEnd;
        if (ovEnd < ovStart) {
            return null;
        }
        return new List<Date>{ ovStart, ovEnd };
    }

    private static Date firstDayOfMonth(Date d) {
        return Date.newInstance(d.year(), d.month(), 1);
    }

    private static Date lastDayOfMonth(Date d) {
        return firstDayOfMonth(d).addMonths(1).addDays(-1);
    }

    private static Integer daysInMonth(Date d) {
        Date f = firstDayOfMonth(d);
        return f.daysBetween(lastDayOfMonth(d)) + 1;
    }

    /**
     * Count of full calendar months fully contained in the overlap of line and ASP windows
     * (month runs 1st through last day, all days must lie in the inclusive overlap).
     */
    @TestVisible
    static Integer wholeMonthsInOverlap(Date lineStart, Date lineEnd, Date aspStart, Date aspEnd) {
        List<Date> seg = overlapInclusiveSegment(lineStart, lineEnd, aspStart, aspEnd);
        if (seg == null) {
            return 0;
        }
        Date ovS = seg[0];
        Date ovE = seg[1];
        Integer count = 0;
        Date m = firstDayOfMonth(ovS);
        while (m <= ovE) {
            Date mEnd = m.addMonths(1).addDays(-1);
            if (m >= ovS && mEnd <= ovE) {
                count++;
            }
            m = m.addMonths(1);
        }
        return count;
    }

    /**
     * Fractions of a calendar month for partial overlap at the start and end of the line/ASP intersection.
     * Same-calendar-month overlap uses startFraction only (endFraction 0). Full single-month overlap returns 0,0.
     */
    @TestVisible
    static MonthOverlapRemainders overlapMonthRemainderFractions(
        Date lineStart,
        Date lineEnd,
        Date aspStart,
        Date aspEnd
    ) {
        MonthOverlapRemainders out = new MonthOverlapRemainders();
        out.startFraction = 0;
        out.endFraction = 0;
        List<Date> seg = overlapInclusiveSegment(lineStart, lineEnd, aspStart, aspEnd);
        if (seg == null) {
            return out;
        }
        Date ovS = seg[0];
        Date ovE = seg[1];

        if (ovS.year() == ovE.year() && ovS.month() == ovE.month()) {
            Integer dim = daysInMonth(ovS);
            if (dim > 0) {
                Boolean fullMonth =
                    ovS == firstDayOfMonth(ovS) &&
                    ovE == lastDayOfMonth(ovE) &&
                    inclusiveDayCount(ovS, ovE) >= dim;
                if (!fullMonth) {
                    out.startFraction = Decimal.valueOf(inclusiveDayCount(ovS, ovE)) / Decimal.valueOf(dim);
                }
            }
            return out;
        }

        Date lastS = lastDayOfMonth(ovS);
        Date endLead = ovE < lastS ? ovE : lastS;
        Integer dimS = daysInMonth(ovS);
        if (dimS > 0 && endLead >= ovS) {
            Boolean startMonthWhole = (ovS.day() == 1) && (lastS <= ovE);
            if (!startMonthWhole) {
                out.startFraction = Decimal.valueOf(inclusiveDayCount(ovS, endLead)) / Decimal.valueOf(dimS);
            }
        }

        Date firstE = firstDayOfMonth(ovE);
        Date startTrail = ovS > firstE ? ovS : firstE;
        Integer dimE = daysInMonth(ovE);
        if (dimE > 0 && startTrail <= ovE) {
            Boolean endMonthWhole = (ovE == lastDayOfMonth(ovE)) && (firstE >= ovS);
            if (!endMonthWhole) {
                out.endFraction = Decimal.valueOf(inclusiveDayCount(startTrail, ovE)) / Decimal.valueOf(dimE);
            }
        }

        return out;
    }

    /** Start/end partial-month fractions for an overlap (see overlapMonthRemainderFractions). */
    public class MonthOverlapRemainders {
        public Decimal startFraction;
        public Decimal endFraction;
    }

    /**
     * Pro-rated MRR for the intersection of [lineStart,lineEnd] and [aspStart,aspEnd].
     * Uses whole-months + partial-month remainders; null Mrr treated as 0.
     */
    @TestVisible
    static Decimal proratedAmountForOverlap(
        Date lineStart,
        Date lineEnd,
        Date aspStart,
        Date aspEnd,
        Decimal mrr
    ) {
        if (mrr == null) {
            mrr = 0;
        }
        if (lineStart == null || lineEnd == null || aspStart == null || aspEnd == null) {
            return 0;
        }
        if (lineEnd < lineStart || aspEnd < aspStart) {
            return 0;
        }
        Date ovStart = lineStart > aspStart ? lineStart : aspStart;
        Date ovEnd = lineEnd < aspEnd ? lineEnd : aspEnd;
        if (ovEnd < ovStart) {
            return 0;
        }
        Integer overlapDays = inclusiveDayCount(ovStart, ovEnd);
        if (overlapDays <= 0) {
            return 0;
        }

        MonthOverlapRemainders remainders = overlapMonthRemainderFractions(lineStart, lineEnd, aspStart, aspEnd);
        Decimal fraction = wholeMonthsInOverlap(lineStart, lineEnd, aspStart, aspEnd) + remainders.startFraction + remainders.endFraction;
        Decimal result = mrr * fraction;
        System.debug(
            LoggingLevel.DEBUG,
            DBG + '.proratedAmountForOverlap: overlapDays=' + overlapDays + ' fraction=' + fraction + ' result=' + result
        );
        return result;
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
     * Per SalesTransactionItem context node (pre-hook subset): the date window, productId,
     * sellingModelType, dataPath, and a skip flag for deleted / unusable nodes.
     */
    @TestVisible
    public class LineContextRow {
        public Date lineStartDate;
        public Date lineEndDate;
        public Id productId;
        public String sellingModelType;
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
