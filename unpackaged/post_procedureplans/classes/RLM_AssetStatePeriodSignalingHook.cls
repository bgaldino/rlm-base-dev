/**
 * Procedure-plan Apex hook: loads overlapping AssetStatePeriod rows for the transaction Account
 * and each SalesTransactionItem date window, pro-rates Amount by inclusive calendar-day overlap,
 * aggregates per line, and writes ItemInstallBaseAmount__c via Context.IndustriesContext.
 */
global with sharing class RLM_AssetStatePeriodSignalingHook implements RevSignaling.SignalingApexProcessor {
    @TestVisible
    static final String TAG_SALES_TRANSACTION = 'SalesTransaction';
    @TestVisible
    static final String TAG_SALES_TRANSACTION_ITEM = 'SalesTransactionItem';
    @TestVisible
    static final String ATTR_ITEM_INSTALL_BASE = 'ItemInstallBaseAmount__c';

    private static final Integer AMOUNT_SCALE = 2;

    private static final String DBG = 'RLM_AssetStatePeriodSignalingHook';

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
            Id accountId = resolveAccountId(industriesContext, contextId);
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
                if (line.skip) {
                    System.debug(LoggingLevel.DEBUG, DBG + '.execute: line ' + lineIndex + ' skipped');
                    continue;
                }
                Date lineStart = line.lineStartDate;
                Date lineEnd = line.lineEndDate != null ? line.lineEndDate : line.lineStartDate;
                if (lineStart == null) {
                    System.debug(LoggingLevel.DEBUG, DBG + '.execute: line ' + lineIndex + ' no StartDate');
                    continue;
                }
                if (lineEnd < lineStart) {
                    lineEnd = lineStart;
                }

                Decimal total;
                if (isOneTime(line.sellingModelType)) {
                    // Per requirements, do not query AssetStatePeriod when SellingModelType is OneTime.
                    System.debug(
                        LoggingLevel.DEBUG,
                        DBG + '.execute: line ' + lineIndex + ' OneTime — skip ASP query, total=0'
                    );
                    total = 0;
                } else {
                    total = computeInstallBaseForLine(accountId, lineStart, lineEnd, line.productId);
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
                                'attributeValue' => String.valueOf(total.setScale(AMOUNT_SCALE, RoundingMode.HALF_UP))
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
            response.message = 'ItemInstallBaseAmount__c updated for ' + nodeUpdates.size() + ' line(s).';
            System.debug(LoggingLevel.DEBUG, DBG + '.execute: SUCCESS message=' + response.message);
        } catch (Exception e) {
            System.debug(LoggingLevel.ERROR, DBG + '.execute: FAILED ' + e.getMessage() + ' ' + e.getStackTraceString());
            response.status = RevSignaling.TransactionStatus.FAILED;
            response.message = 'RLM_AssetStatePeriodSignalingHook: ' + e.getMessage();
        }

        System.debug(LoggingLevel.DEBUG, DBG + '.execute: exit status=' + response.status);
        return response;
    }

    @TestVisible
    static Boolean isOneTime(String sellingModelType) {
        Boolean result = sellingModelType != null && 'OneTime'.equalsIgnoreCase(sellingModelType.trim());
        System.debug(LoggingLevel.DEBUG, DBG + '.isOneTime: sellingModelType=' + sellingModelType + ' result=' + result);
        return result;
    }

    private static Id resolveAccountId(Context.IndustriesContext industriesContext, String contextId) {
        System.debug(LoggingLevel.DEBUG, DBG + '.resolveAccountId: enter contextId=' + contextId);
        Map<String, Object> outMap = industriesContext.queryTags(
            new Map<String, Object>{
                'contextId' => contextId,
                'tags' => new List<String>{ TAG_SALES_TRANSACTION }
            }
        );
        Map<String, Object> queryResult = (Map<String, Object>) outMap.get('queryResult');
        if (queryResult == null) {
            System.debug(LoggingLevel.DEBUG, DBG + '.resolveAccountId: queryResult null');
            return null;
        }
        List<Object> stNodes = (List<Object>) queryResult.get(TAG_SALES_TRANSACTION);
        if (stNodes == null || stNodes.isEmpty()) {
            System.debug(LoggingLevel.DEBUG, DBG + '.resolveAccountId: no SalesTransaction nodes');
            return null;
        }
        Map<String, Object> firstNode = (Map<String, Object>) stNodes[0];
        Map<String, Object> tagValue = (Map<String, Object>) firstNode.get('tagValue');
        if (tagValue == null) {
            return null;
        }
        Id accountId = parseIdTag(tagValue, 'Account');
        if (accountId == null) {
            accountId = parseIdTag(tagValue, 'QuoteAccount');
        }
        System.debug(LoggingLevel.DEBUG, DBG + '.resolveAccountId: exit accountId=' + accountId);
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
            System.debug(LoggingLevel.DEBUG, DBG + '.querySalesTransactionItems: queryResult null');
            return rows;
        }
        List<Object> itemNodes = (List<Object>) queryResult.get(TAG_SALES_TRANSACTION_ITEM);
        if (itemNodes == null) {
            System.debug(LoggingLevel.DEBUG, DBG + '.querySalesTransactionItems: no item nodes');
            return rows;
        }

        for (Object itemObj : itemNodes) {
            Map<String, Object> itemNode = (Map<String, Object>) itemObj;
            rows.add(buildLineContextRow(itemNode));
        }
        System.debug(LoggingLevel.DEBUG, DBG + '.querySalesTransactionItems: exit parsedRows=' + rows.size());
        System.debug(LoggingLevel.DEBUG, DBG + '.querySalesTransactionItems: rows=' + rows);
        return rows;
    }

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
            // Requirement: only query AssetStatePeriod when we have the line Product to use as a parameter.
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

    /**
     * Inclusive calendar-day count between two dates (end >= start). Returns 0 if invalid.
     */
    @TestVisible
    static Integer inclusiveDayCount(Date startDate, Date endDate) {
        System.debug(LoggingLevel.DEBUG, DBG + '.inclusiveDayCount: start=' + startDate + ' end=' + endDate);
        if (startDate == null || endDate == null || endDate < startDate) {
            System.debug(LoggingLevel.DEBUG, DBG + '.inclusiveDayCount: invalid range -> 0');
            return 0;
        }
        Integer days = startDate.daysBetween(endDate) + 1;
        System.debug(LoggingLevel.DEBUG, DBG + '.inclusiveDayCount: days=' + days);
        return days;
    }

    /**
     * Inclusive overlap of [lineStart,lineEnd] and [aspStart,aspEnd]. Returns null if invalid or no overlap.
     */
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
        System.debug(
            LoggingLevel.DEBUG,
            DBG + '.wholeMonthsInOverlap: line=' + lineStart + '..' + lineEnd + ' asp=' + aspStart + '..' + aspEnd
        );
        List<Date> seg = overlapInclusiveSegment(lineStart, lineEnd, aspStart, aspEnd);
        if (seg == null) {
            System.debug(LoggingLevel.DEBUG, DBG + '.wholeMonthsInOverlap: no overlap -> 0');
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
        System.debug(LoggingLevel.DEBUG, DBG + '.wholeMonthsInOverlap: count=' + count);
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
        System.debug(
            LoggingLevel.DEBUG,
            DBG + '.overlapMonthRemainderFractions: line=' + lineStart + '..' + lineEnd + ' asp=' + aspStart + '..' + aspEnd
        );
        MonthOverlapRemainders out = new MonthOverlapRemainders();
        out.startFraction = 0;
        out.endFraction = 0;
        List<Date> seg = overlapInclusiveSegment(lineStart, lineEnd, aspStart, aspEnd);
        if (seg == null) {
            System.debug(LoggingLevel.DEBUG, DBG + '.overlapMonthRemainderFractions: no overlap -> 0,0');
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
            System.debug(
                LoggingLevel.DEBUG,
                DBG + '.overlapMonthRemainderFractions: same month start=' + out.startFraction + ' end=' + out.endFraction
            );
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

        System.debug(
            LoggingLevel.DEBUG,
            DBG + '.overlapMonthRemainderFractions: start=' + out.startFraction + ' end=' + out.endFraction
        );
        return out;
    }

    /**
     * Start/end partial-month fractions for an overlap (see overlapMonthRemainderFractions).
     */
    public class MonthOverlapRemainders {
        public Decimal startFraction;
        public Decimal endFraction;
    }

    /**
     * Pro-rated MRR for the intersection of [lineStart,lineEnd] and [aspStart,aspEnd].
     * Uses inclusive days; null Mrr treated as 0.
     */
    @TestVisible
    static Decimal proratedAmountForOverlap(
        Date lineStart,
        Date lineEnd,
        Date aspStart,
        Date aspEnd,
        Decimal mrr
    ) {
        System.debug(
            LoggingLevel.DEBUG,
            DBG + '.proratedAmountForOverlap: line=' + lineStart + '..' + lineEnd + ' asp=' + aspStart + '..' + aspEnd + ' mrr=' + mrr
        );
        if (mrr == null) {
            mrr = 0;
        }
        if (lineStart == null || lineEnd == null || aspStart == null || aspEnd == null) {
            System.debug(LoggingLevel.DEBUG, DBG + '.proratedAmountForOverlap: null date -> 0');
            return 0;
        }
        if (lineEnd < lineStart || aspEnd < aspStart) {
            System.debug(LoggingLevel.DEBUG, DBG + '.proratedAmountForOverlap: inverted range -> 0');
            return 0;
        }
        Date ovStart = lineStart > aspStart ? lineStart : aspStart;
        Date ovEnd = lineEnd < aspEnd ? lineEnd : aspEnd;
        if (ovEnd < ovStart) {
            System.debug(LoggingLevel.DEBUG, DBG + '.proratedAmountForOverlap: no overlap -> 0');
            return 0;
        }
        Integer overlapDays = inclusiveDayCount(ovStart, ovEnd);
        if (overlapDays <= 0) {
            System.debug(LoggingLevel.DEBUG, DBG + '.proratedAmountForOverlap: overlapDays<=0 -> 0');
            return 0;
        }
        Integer aspDays = inclusiveDayCount(aspStart, aspEnd);
        /*
        if (aspDays <= 0) {
            System.debug(LoggingLevel.DEBUG, DBG + '.proratedAmountForOverlap: aspDays<=0 -> full amount=' + amount);
            return amount;
        }
        */

        MonthOverlapRemainders remainders = overlapMonthRemainderFractions(lineStart, lineEnd, aspStart, aspEnd);
        Decimal fraction = wholeMonthsInOverlap(lineStart, lineEnd, aspStart, aspEnd) + remainders.startFraction + remainders.endFraction;
        Decimal result = mrr * fraction;
        System.debug(
            LoggingLevel.DEBUG,
            DBG + '.proratedAmountForOverlap: overlapDays=' + overlapDays + ' aspDays=' + aspDays + ' fraction=' + fraction + ' result=' + result
        );
        return result;
    }

    private static Id tryParseId(String s) {
        System.debug(LoggingLevel.DEBUG, DBG + '.tryParseId: enter s=' + s);
        if (String.isBlank(s)) {
            System.debug(LoggingLevel.DEBUG, DBG + '.tryParseId: blank -> null');
            return null;
        }
        try {
            Id parsed = Id.valueOf(s.trim());
            System.debug(LoggingLevel.DEBUG, DBG + '.tryParseId: exit id=' + parsed);
            return parsed;
        } catch (Exception e) {
            System.debug(LoggingLevel.DEBUG, DBG + '.tryParseId: parse failed ' + e.getMessage());
            return null;
        }
    }

    @TestVisible
    static Id parseIdTag(Map<String, Object> tagValue, String tagKey) {
        System.debug(LoggingLevel.DEBUG, DBG + '.parseIdTag: enter tagKey=' + tagKey);
        if (tagValue == null || !tagValue.containsKey(tagKey)) {
            System.debug(LoggingLevel.DEBUG, DBG + '.parseIdTag: missing key -> null');
            return null;
        }
        Object raw = tagValue.get(tagKey);
        if (raw instanceof Map<String, Object>) {
            Map<String, Object> tagInner = (Map<String, Object>) raw;
            Object tv = tagInner.get('tagValue');
            if (tv instanceof String) {
                Id id = tryParseId((String) tv);
                System.debug(LoggingLevel.DEBUG, DBG + '.parseIdTag: exit nested id=' + id);
                return id;
            }
            System.debug(LoggingLevel.DEBUG, DBG + '.parseIdTag: nested non-string tagValue -> null');
            return null;
        }
        if (raw instanceof String) {
            Id id = tryParseId((String) raw);
            System.debug(LoggingLevel.DEBUG, DBG + '.parseIdTag: exit string id=' + id);
            return id;
        }
        System.debug(LoggingLevel.DEBUG, DBG + '.parseIdTag: unsupported raw type -> null');
        return null;
    }

    @TestVisible
    static Date parseContextDate(Map<String, Object> tagValue, String tagKey) {
        System.debug(LoggingLevel.DEBUG, DBG + '.parseContextDate: enter tagKey=' + tagKey);
        if (tagValue == null || !tagValue.containsKey(tagKey)) {
            System.debug(LoggingLevel.DEBUG, DBG + '.parseContextDate: missing key -> null');
            return null;
        }
        Object raw = tagValue.get(tagKey);
        String s = null;
        if (raw instanceof Map<String, Object>) {
            Object tv = ((Map<String, Object>) raw).get('tagValue');
            system.debug('tv=' + tv);
            
            s = String.valueOf(tv);
            system.debug('Date s=' + s);
        } else if (raw instanceof String) {
            s = (String) raw;
        }
        if (String.isBlank(s)) {
            System.debug(LoggingLevel.DEBUG, DBG + '.parseContextDate: blank -> null');
            return null;
        }
        s = s.trim();
        try {
            if (s.length() > 10 && 'T'.equals(s.substring(10, 11))) {
                Date d = Date.valueOf(s.substring(0, 10));
                System.debug(LoggingLevel.DEBUG, DBG + '.parseContextDate: exit iso date=' + d);
                return d;
            }
            Date d = Date.valueOf(s);
            System.debug(LoggingLevel.DEBUG, DBG + '.parseContextDate: exit date=' + d);
            return d;
        } catch (Exception e) {
            System.debug(LoggingLevel.DEBUG, DBG + '.parseContextDate: parse error ' + e.getMessage());
            return null;
        }
    }

    @TestVisible
    static String parseContextString(Map<String, Object> tagValue, String tagKey) {
        System.debug(LoggingLevel.DEBUG, DBG + '.parseContextString: enter tagKey=' + tagKey);
        if (tagValue == null || !tagValue.containsKey(tagKey)) {
            System.debug(LoggingLevel.DEBUG, DBG + '.parseContextString: missing key -> null');
            return null;
        }
        Object raw = tagValue.get(tagKey);
        if (raw instanceof Map<String, Object>) {
            Object tv = ((Map<String, Object>) raw).get('tagValue');
            if (tv instanceof String) {
                String s = (String) tv;
                String out = String.isBlank(s) ? null : s.trim();
                System.debug(LoggingLevel.DEBUG, DBG + '.parseContextString: exit nested=' + out);
                return out;
            }
            System.debug(LoggingLevel.DEBUG, DBG + '.parseContextString: nested non-string -> null');
            return null;
        }
        if (raw instanceof String) {
            String s = (String) raw;
            String out = String.isBlank(s) ? null : s.trim();
            System.debug(LoggingLevel.DEBUG, DBG + '.parseContextString: exit string=' + out);
            return out;
        }
        System.debug(LoggingLevel.DEBUG, DBG + '.parseContextString: unsupported raw -> null');
        return null;
    }

    @TestVisible
    private static LineContextRow buildLineContextRow(Map<String, Object> itemNode) {
        System.debug(LoggingLevel.DEBUG, DBG + '.buildLineContextRow: enter');
        LineContextRow row = new LineContextRow();
        row.dataPathFull = (List<Object>) itemNode.get('dataPath');
        row.skip = false;

        Map<String, Object> tags = (Map<String, Object>) itemNode.get('tagValue');
        if (tags == null) {
            row.skip = true;
            System.debug(LoggingLevel.DEBUG, DBG + '.buildLineContextRow: no tagValue — skip');
            return row;
        }

        if (isDeletedSalesTransactionItem(tags)) {
            row.skip = true;
            System.debug(LoggingLevel.DEBUG, DBG + '.buildLineContextRow: DELETED — skip');
            return row;
        }

        row.lineStartDate = parseContextDate(tags, 'EffectiveFrom');
        row.lineEndDate = parseContextDate(tags, 'EffectiveTo');
        row.productId = parseIdTag(tags, 'Product');
        row.sellingModelType = parseContextString(tags, 'SellingModelType');
        System.debug(
            LoggingLevel.DEBUG,
            DBG + '.buildLineContextRow: exit start=' + row.lineStartDate + ' end=' + row.lineEndDate + ' productId=' + row.productId + ' sellingModelType=' + row.sellingModelType
        );
        return row;
    }

    private static Boolean isDeletedSalesTransactionItem(Map<String, Object> tags) {
        System.debug(LoggingLevel.DEBUG, DBG + '.isDeletedSalesTransactionItem: enter');
        String dml = dmlStatusFromTagMap(tags, 'LineItemPath');
        if ('DELETED'.equalsIgnoreCase(dml)) {
            System.debug(LoggingLevel.DEBUG, DBG + '.isDeletedSalesTransactionItem: LineItemPath DELETED');
            return true;
        }
        dml = dmlStatusFromTagMap(tags, 'LineItem');
        Boolean deleted = 'DELETED'.equalsIgnoreCase(dml);
        System.debug(LoggingLevel.DEBUG, DBG + '.isDeletedSalesTransactionItem: exit deleted=' + deleted);
        return deleted;
    }

    private static String dmlStatusFromTagMap(Map<String, Object> tags, String key) {
        System.debug(LoggingLevel.DEBUG, DBG + '.dmlStatusFromTagMap: key=' + key);
        if (!tags.containsKey(key)) {
            System.debug(LoggingLevel.DEBUG, DBG + '.dmlStatusFromTagMap: missing key');
            return null;
        }
        Object raw = tags.get(key);
        if (!(raw instanceof Map<String, Object>)) {
            System.debug(LoggingLevel.DEBUG, DBG + '.dmlStatusFromTagMap: not a tag map');
            return null;
        }
        Object dml = ((Map<String, Object>) raw).get('dmlStatus');
        String status = dml instanceof String ? (String) dml : null;
        System.debug(LoggingLevel.DEBUG, DBG + '.dmlStatusFromTagMap: status=' + status);
        return status;
    }

    /**
     * Per SalesTransactionItem context node: dates, dataPath, and whether to skip (deleted / unusable path).
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
         * Same trimming as common pricing hooks: use indices 1 and 2 of the full dataPath for field updates.
         */
        public List<Object> pathForFieldUpdate() {
            System.debug(LoggingLevel.DEBUG, DBG + '.LineContextRow.pathForFieldUpdate: enter dataPath size=' + (dataPathFull == null ? null : dataPathFull.size()));
            if (dataPathFull == null || dataPathFull.size() <= 2) {
                System.debug(LoggingLevel.DEBUG, DBG + '.LineContextRow.pathForFieldUpdate: insufficient path -> null');
                return null;
            }
            List<Object> path = new List<Object>{ dataPathFull[1], dataPathFull[2] };
            System.debug(LoggingLevel.DEBUG, DBG + '.LineContextRow.pathForFieldUpdate: exit path=' + path);
            return path;
        }
    }
}

