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
            TransactionRollupTotals rollup = new TransactionRollupTotals();

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
            
                if (isOneTime(line.sellingModelType)) {
                    // Per requirements, do not query AssetStatePeriod when SellingModelType is OneTime.
                    System.debug(
                        LoggingLevel.DEBUG,
                        DBG + '.execute: line ' + lineIndex + ' OneTime — skip ASP query, total=0'
                    );
                    total = 0;
                    nrr = line.netTotalPrice;
                    System.debug(
                        LoggingLevel.DEBUG,
                        DBG +
                            '.execute: line ' +
                            lineIndex +
                            ' OneTime — metrics total=0 nrr=' +
                            nrr +
                            ' (other revenue fields left 0)'
                    );
                } else {
                    total = computeInstallBaseForLine(accountId, lineStart, lineEnd, line.productId);
                    System.debug(
                        LoggingLevel.DEBUG,
                        DBG + '.execute: line ' + lineIndex + ' computed total=' + total + ' productId=' + line.productId
                    );
                    
                    netNewAmount = calcNetNewAmount(line.transactionActionType, total, line.netTotalPrice);
                    expansionAmount = calcExpansionAmount(line.transactionActionType, total, line.netTotalPrice, line.startQuantity, line.endQuantity);
                    churnedAmount = calcChurnedAmount(line.transactionActionType, total, line.netTotalPrice, line.startQuantity, line.endQuantity);
                    renewalAmount = calcRenewalAmount(line.transactionActionType, total, line.netTotalPrice);
                    arr = calculateARR(line.pricingTermUnit, line.pricingTerm, line.pricingTermCount, line.netTotalPrice);   
                    netNewARR = calculateARR(line.pricingTermUnit, line.pricingTerm, line.pricingTermCount, netNewAmount);
                    expansionARR = calculateARR(line.pricingTermUnit, line.pricingTerm, line.pricingTermCount, expansionAmount);
                    churnedARR = calculateARR(line.pricingTermUnit, line.pricingTerm, line.pricingTermCount, churnedAmount);
                    renewalARR = calculateARR(line.pricingTermUnit, line.pricingTerm, line.pricingTermCount, renewalAmount);
                    iARR = netNewARR + expansionARR - churnedARR;
                    System.debug(
                        LoggingLevel.DEBUG,
                        DBG +
                            '.execute: line ' +
                            lineIndex +
                            ' metrics total=' +
                            total +
                            ' netNew=' +
                            netNewAmount +
                            ' expansion=' +
                            expansionAmount +
                            ' churned=' +
                            churnedAmount +
                            ' renewal=' +
                            renewalAmount +
                            ' nrr=' +
                            nrr +
                            ' arr=' +
                            arr +
                            ' netNewARR=' +
                            netNewARR +
                            ' expansionARR=' +
                            expansionARR +
                            ' churnedARR=' +
                            churnedARR +
                            ' renewalARR=' +
                            renewalARR
                    );
                }

                rollup.accumulateLine(
                    total, netNewAmount, expansionAmount, churnedAmount, renewalAmount,
                    nrr, arr, netNewARR, expansionARR, churnedARR, renewalARR, iARR
                );

                List<Object> pathForUpdate = line.pathForFieldUpdate();
                if (pathForUpdate == null || pathForUpdate.isEmpty()) {
                    System.debug(LoggingLevel.DEBUG, DBG + '.execute: line ' + lineIndex + ' no pathForFieldUpdate');
                    continue;
                }

                /* old node update code
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
                */
                List<Object> attributesForUpdate = new List<Object>();
                
                attributesForUpdate.add(
                    new Map<String, Object>{
                        'attributeName' => ATTR_ITEM_INSTALL_BASE,
                        'attributeValue' => String.valueOf(total.setScale(AMOUNT_SCALE, RoundingMode.HALF_UP))
                    }
                );

                attributesForUpdate.add(
                    new Map<String, Object>{
                        'attributeName' => 'ItemNetNewAmount__c',
                        'attributeValue' => String.valueOf(netNewAmount.setScale(AMOUNT_SCALE, RoundingMode.HALF_UP))
                    }
                );

                attributesForUpdate.add(
                    new Map<String, Object>{
                        'attributeName' => 'ItemExpansionAmount__c',
                        'attributeValue' => String.valueOf(expansionAmount.setScale(AMOUNT_SCALE, RoundingMode.HALF_UP))
                    }
                );

                attributesForUpdate.add(
                    new Map<String, Object>{
                        'attributeName' => 'ItemChurnedAmount__c',
                        'attributeValue' => String.valueOf(churnedAmount.setScale(AMOUNT_SCALE, RoundingMode.HALF_UP))
                    }
                );
                
                attributesForUpdate.add(
                    new Map<String, Object>{
                        'attributeName' => 'ItemRenewalAmount__c',
                        'attributeValue' => String.valueOf(renewalAmount.setScale(AMOUNT_SCALE, RoundingMode.HALF_UP))
                    }
                );

                attributesForUpdate.add(
                    new Map<String, Object>{
                        'attributeName' => 'ItemNRR__c',
                        'attributeValue' => String.valueOf(nrr.setScale(AMOUNT_SCALE, RoundingMode.HALF_UP))
                    }
                );
                

                attributesForUpdate.add(
                    new Map<String, Object>{
                        'attributeName' => 'ItemARR__c',
                        'attributeValue' => String.valueOf(arr.setScale(AMOUNT_SCALE, RoundingMode.HALF_UP))
                    }
                );
                

                attributesForUpdate.add(
                    new Map<String, Object>{
                        'attributeName' => 'ItemNetNewARR__c',
                        'attributeValue' => String.valueOf(netNewARR.setScale(AMOUNT_SCALE, RoundingMode.HALF_UP))
                    }
                );
                

                attributesForUpdate.add(
                    new Map<String, Object>{
                        'attributeName' => 'ItemExpansionARR__c',
                        'attributeValue' => String.valueOf(expansionARR.setScale(AMOUNT_SCALE, RoundingMode.HALF_UP))
                    }
                );  
                
                attributesForUpdate.add(
                    new Map<String, Object>{
                        'attributeName' => 'ItemChurnedARR__c',
                        'attributeValue' => String.valueOf(churnedARR.setScale(AMOUNT_SCALE, RoundingMode.HALF_UP))
                    }
                );

                attributesForUpdate.add(
                    new Map<String, Object>{
                        'attributeName' => 'ItemRenewalARR__c',
                        'attributeValue' => String.valueOf(renewalARR.setScale(AMOUNT_SCALE, RoundingMode.HALF_UP))
                    }
                );

                attributesForUpdate.add(
                    new Map<String, Object>{
                        'attributeName' => 'ItemiARR__c',
                        'attributeValue' => String.valueOf(iARR.setScale(AMOUNT_SCALE, RoundingMode.HALF_UP))
                    }
                );

                /* new node update code */
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

    /**
     * Queries SalesTransaction tag and returns the first node map. Used for Account resolution
     * and for reading the SalesTransaction dataPath (needed for header-level attribute writes).
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

    /**
     * Resolves Account (or QuoteAccount) Id from an already-fetched SalesTransaction node.
     */
    @TestVisible
    static Id resolveAccountIdFromNode(Map<String, Object> salesTransactionNode) {
        System.debug(LoggingLevel.DEBUG, DBG + '.resolveAccountIdFromNode: enter');
        if (salesTransactionNode == null) {
            System.debug(LoggingLevel.DEBUG, DBG + '.resolveAccountIdFromNode: null node -> null');
            return null;
        }
        Map<String, Object> tagValue = (Map<String, Object>) salesTransactionNode.get('tagValue');
        if (tagValue == null) {
            System.debug(LoggingLevel.DEBUG, DBG + '.resolveAccountIdFromNode: tagValue null');
            return null;
        }
        Id accountId = parseIdTag(tagValue, 'Account');
        if (accountId == null) {
            accountId = parseIdTag(tagValue, 'QuoteAccount');
        }
        System.debug(LoggingLevel.DEBUG, DBG + '.resolveAccountIdFromNode: exit accountId=' + accountId);
        return accountId;
    }

    /**
     * Returns the full dataPath list from a SalesTransaction node for header-level attribute updates.
     */
    @TestVisible
    static List<Object> salesTransactionDataPath(Map<String, Object> salesTransactionNode) {
        System.debug(LoggingLevel.DEBUG, DBG + '.salesTransactionDataPath: enter');
        if (salesTransactionNode == null) {
            System.debug(LoggingLevel.DEBUG, DBG + '.salesTransactionDataPath: null node -> null');
            return null;
        }
        List<Object> dataPath = (List<Object>) salesTransactionNode.get('dataPath');
        if (dataPath == null || dataPath.isEmpty()) {
            System.debug(LoggingLevel.DEBUG, DBG + '.salesTransactionDataPath: empty dataPath -> null');
            return null;
        }
        System.debug(LoggingLevel.DEBUG, DBG + '.salesTransactionDataPath: exit segments=' + dataPath.size());
        return new List<Object>(dataPath);
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
        System.debug(
            LoggingLevel.DEBUG,
            DBG +
                '.overlapInclusiveSegment: line=' +
                lineStart +
                '..' +
                lineEnd +
                ' asp=' +
                aspStart +
                '..' +
                aspEnd
        );
        if (lineStart == null || lineEnd == null || aspStart == null || aspEnd == null) {
            System.debug(LoggingLevel.DEBUG, DBG + '.overlapInclusiveSegment: null date bound -> no segment');
            return null;
        }
        if (lineEnd < lineStart || aspEnd < aspStart) {
            System.debug(
                LoggingLevel.DEBUG,
                DBG +
                    '.overlapInclusiveSegment: inverted line or ASP range -> no segment lineEnd<lineStart=' +
                    (lineEnd < lineStart) +
                    ' aspEnd<aspStart=' +
                    (aspEnd < aspStart)
            );
            return null;
        }
        Date ovStart = lineStart > aspStart ? lineStart : aspStart;
        Date ovEnd = lineEnd < aspEnd ? lineEnd : aspEnd;
        if (ovEnd < ovStart) {
            System.debug(LoggingLevel.DEBUG, DBG + '.overlapInclusiveSegment: ranges do not intersect -> no segment');
            return null;
        }
        System.debug(LoggingLevel.DEBUG, DBG + '.overlapInclusiveSegment: overlap ovStart=' + ovStart + ' ovEnd=' + ovEnd);
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

    /** Annualized recurring revenue from pricing term and amount. */
    private static Decimal calculateARR(String pricingTermUnit, Decimal pricingTerm, Decimal pricingTermCount, Decimal amount) {
        System.debug(
            LoggingLevel.DEBUG,
            DBG +
                '.calculateARR: enter unit=' +
                pricingTermUnit +
                ' term=' +
                pricingTerm +
                ' termCount=' +
                pricingTermCount +
                ' amount=' +
                amount
        );
        Decimal arr = 0;
        if (pricingTermUnit == 'Months' && pricingTermCount > 0) {
            arr = (amount / (pricingTerm * pricingTermCount)) * 12;
            System.debug(LoggingLevel.DEBUG, DBG + '.calculateARR: branch Months — arr=' + arr);
        } else if (pricingTermUnit == 'Annual' && pricingTermCount > 0) {
            arr = amount / (pricingTermCount / pricingTerm);
            System.debug(LoggingLevel.DEBUG, DBG + '.calculateARR: branch Years — arr=' + arr);
        } else {
            System.debug(
                LoggingLevel.DEBUG,
                DBG +
                    '.calculateARR: no matching unit or non-positive termCount — arr=0 (unit=' +
                    pricingTermUnit +
                    ' count=' +
                    pricingTermCount +
                    ')'
            );
        }
        System.debug(LoggingLevel.DEBUG, DBG + '.calculateARR: exit arr=' + arr);
        return arr;
    }

    private static Decimal calcNetNewAmount(String transactionActionType, Decimal installBaseAmount, Decimal netTotalPrice) {
        System.debug(
            LoggingLevel.DEBUG,
            DBG +
                '.calcNetNewAmount: enter actionType=' +
                transactionActionType +
                ' installBase=' +
                installBaseAmount +
                ' netTotal=' +
                netTotalPrice
        );
        Decimal netNewAmount = 0;
        if (String.isBlank(transactionActionType) && (installBaseAmount == null || installBaseAmount <= 0)) {
            netNewAmount = netTotalPrice;
            System.debug(LoggingLevel.DEBUG, DBG + '.calcNetNewAmount: net-new business (blank action, no install base) — netNew=' + netNewAmount);
        } else {
            System.debug(LoggingLevel.DEBUG, DBG + '.calcNetNewAmount: not classified as net-new — netNew=0');
        }
        System.debug(LoggingLevel.DEBUG, DBG + '.calcNetNewAmount: exit netNewAmount=' + netNewAmount);
        return netNewAmount;
    }

    private static Decimal calcExpansionAmount(
        String transactionActionType,
        Decimal installBaseAmount,
        Decimal netTotalPrice,
        Decimal startQuantity,
        Decimal endQuantity
    ) {
        System.debug(
            LoggingLevel.DEBUG,
            DBG +
                '.calcExpansionAmount: enter actionType=' +
                transactionActionType +
                ' installBase=' +
                installBaseAmount +
                ' netTotal=' +
                netTotalPrice +
                ' startQty=' +
                startQuantity +
                ' endQty=' +
                endQuantity
        );
        Decimal expansionAmount = 0;
        if (String.isBlank(transactionActionType) && (installBaseAmount != null && installBaseAmount > 0)) {
            expansionAmount = netTotalPrice;
            System.debug(LoggingLevel.DEBUG, DBG + '.calcExpansionAmount: branch blank action with install base — expansion=' + expansionAmount);
        } else if (transactionActionType == 'Amend' && (installBaseAmount != null && installBaseAmount > 0)) {
            expansionAmount = netTotalPrice;
            System.debug(LoggingLevel.DEBUG, DBG + '.calcExpansionAmount: branch Amend with install base — expansion=' + expansionAmount);
        } else if (transactionActionType == 'Renewal' && (installBaseAmount != null && installBaseAmount < netTotalPrice)) {
            expansionAmount = netTotalPrice - installBaseAmount;
            System.debug(
                LoggingLevel.DEBUG,
                DBG + '.calcExpansionAmount: branch Renewal (install base < net total) — expansion=' + expansionAmount
            );
        } else {
            System.debug(LoggingLevel.DEBUG, DBG + '.calcExpansionAmount: no expansion branch matched — expansion=0');
        }
        System.debug(LoggingLevel.DEBUG, DBG + '.calcExpansionAmount: exit expansionAmount=' + expansionAmount);
        return expansionAmount;
    }

    private static Decimal calcChurnedAmount(
        String transactionActionType,
        Decimal installBaseAmount,
        Decimal netTotalPrice,
        Decimal startQuantity,
        Decimal endQuantity
    ) {
        System.debug(
            LoggingLevel.DEBUG,
            DBG +
                '.calcChurnedAmount: enter actionType=' +
                transactionActionType +
                ' installBase=' +
                installBaseAmount +
                ' netTotal=' +
                netTotalPrice +
                ' startQty=' +
                startQuantity +
                ' endQty=' +
                endQuantity
        );
        Decimal churnedAmount = 0;
        if (transactionActionType == 'Cancel') {
            churnedAmount = Math.abs(netTotalPrice);
            System.debug(LoggingLevel.DEBUG, DBG + '.calcChurnedAmount: branch Cancel — churned=' + churnedAmount);
        } else if (
            transactionActionType == 'Amend' &&
            (installBaseAmount != null && installBaseAmount > 0) &&
            (startQuantity > endQuantity)
        ) {
            churnedAmount = Math.abs(netTotalPrice);
            System.debug(LoggingLevel.DEBUG, DBG + '.calcChurnedAmount: branch Amend (qty down) — churned=' + churnedAmount);
        } else if (transactionActionType == 'Renewal' && (installBaseAmount != null && installBaseAmount > netTotalPrice)) {
            churnedAmount = Math.abs(netTotalPrice - installBaseAmount);
            System.debug(LoggingLevel.DEBUG, DBG + '.calcChurnedAmount: branch Renewal (install base > net total) — churned=' + churnedAmount);
        } else {
            System.debug(LoggingLevel.DEBUG, DBG + '.calcChurnedAmount: no churn branch matched — churned=0');
        }

        System.debug(LoggingLevel.DEBUG, DBG + '.calcChurnedAmount: exit churnedAmount=' + churnedAmount);
        return churnedAmount;
    }

    private static Decimal calcRenewalAmount(String transactionActionType, Decimal installBaseAmount, Decimal netTotalPrice) {
        System.debug(
            LoggingLevel.DEBUG,
            DBG +
                '.calcRenewalAmount: enter actionType=' +
                transactionActionType +
                ' installBase=' +
                installBaseAmount +
                ' netTotal=' +
                netTotalPrice
        );
        Decimal renewalAmount = 0;
        if (transactionActionType == 'Renewal' && (installBaseAmount != null && installBaseAmount > 0)) {
            renewalAmount = installBaseAmount;
            System.debug(LoggingLevel.DEBUG, DBG + '.calcRenewalAmount: branch Renewal with install base — renewalBase=' + renewalAmount);
        } else {
            System.debug(LoggingLevel.DEBUG, DBG + '.calcRenewalAmount: not a renewal base case — renewal=0');
        }
        System.debug(LoggingLevel.DEBUG, DBG + '.calcRenewalAmount: exit renewalAmount=' + renewalAmount);
        return renewalAmount;
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
            System.debug(LoggingLevel.DEBUG, DBG + '.parseContextDate: nested tagValue raw=' + tv);
            s = String.valueOf(tv);
            System.debug(LoggingLevel.DEBUG, DBG + '.parseContextDate: nested string for parse=' + s);
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

    private static Decimal parseContextDecimal(Map<String, Object> tagValue, String tagKey) {   
        System.debug(LoggingLevel.DEBUG, DBG + '.parseContextDecimal: enter tagKey=' + tagKey);
        if (tagValue == null || !tagValue.containsKey(tagKey)) {
            System.debug(LoggingLevel.DEBUG, DBG + '.parseContextDecimal: missing key -> null');
            return null;
        }
        Object raw = tagValue.get(tagKey);
        if (raw instanceof Map<String, Object>) {
            Object tv = ((Map<String, Object>) raw).get('tagValue');
            if (tv instanceof Decimal) {
                Decimal d = (Decimal) tv;
                System.debug(LoggingLevel.DEBUG, DBG + '.parseContextDecimal: exit nested decimal=' + d);
                return d;
            }
            System.debug(LoggingLevel.DEBUG, DBG + '.parseContextDecimal: nested non-decimal -> null');
            return null;
        }
        if (raw instanceof Decimal) {
            Decimal d = (Decimal) raw;
            System.debug(LoggingLevel.DEBUG, DBG + '.parseContextDecimal: exit decimal=' + d);
            return d;
        }
        System.debug(LoggingLevel.DEBUG, DBG + '.parseContextDecimal: unsupported raw type -> null');
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
        row.transactionActionType = parseContextString(tags, 'SalesTransactionActionType');
        row.pricingTermUnit = parseContextString(tags, 'PricingTermUnit');
        row.pricingTerm = parseContextDecimal(tags, 'ItemSubscriptionTerm');
        row.pricingTermCount = parseContextDecimal(tags, 'PricingTermCount');
        row.netTotalPrice = parseContextDecimal(tags, 'ItemNetTotalPrice');
        row.startQuantity = parseContextDecimal(tags, 'ItemStartQuantity');
        row.endQuantity = parseContextDecimal(tags, 'ItemEndQuantity');
        System.debug(
            LoggingLevel.DEBUG,
            DBG +
                '.buildLineContextRow: exit start=' +
                row.lineStartDate +
                ' end=' +
                row.lineEndDate +
                ' productId=' +
                row.productId +
                ' sellingModelType=' +
                row.sellingModelType +
                ' transactionActionType=' +
                row.transactionActionType +
                ' pricingTermUnit=' +
                row.pricingTermUnit +
                ' pricingTerm=' +
                row.pricingTerm +
                ' pricingTermCount=' +
                row.pricingTermCount +
                ' netTotalPrice=' +
                row.netTotalPrice +
                ' startQty=' +
                row.startQuantity +
                ' endQty=' +
                row.endQuantity
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
     * Builds the attribute list for the SalesTransaction header node from rolled-up line totals.
     */
    @TestVisible
    static List<Object> buildSalesTransactionAttributes(TransactionRollupTotals rollup) {
        System.debug(
            LoggingLevel.DEBUG,
            DBG +
                '.buildSalesTransactionAttributes: enter' +
                ' contributingLines=' + rollup.contributingLineCount +
                ' totalInstallBase=' + rollup.totalInstallBase +
                ' netNew=' + rollup.netNewAmount +
                ' expansion=' + rollup.expansionAmount +
                ' churned=' + rollup.churnedAmount +
                ' renewal=' + rollup.renewalAmount +
                ' nrr=' + rollup.nrr +
                ' arr=' + rollup.arr +
                ' netNewARR=' + rollup.netNewARR +
                ' expansionARR=' + rollup.expansionARR +
                ' churnedARR=' + rollup.churnedARR +
                ' renewalARR=' + rollup.renewalARR +
                ' iARR=' + rollup.iARR
        );
        List<Object> attrs = new List<Object>();
        attrs.add(new Map<String, Object>{
            'attributeName' => ATTR_ST_NET_NEW_AMOUNT,
            'attributeValue' => String.valueOf(rollup.netNewAmount.setScale(AMOUNT_SCALE, RoundingMode.HALF_UP))
        });
        attrs.add(new Map<String, Object>{
            'attributeName' => ATTR_ST_EXPANSION_AMOUNT,
            'attributeValue' => String.valueOf(rollup.expansionAmount.setScale(AMOUNT_SCALE, RoundingMode.HALF_UP))
        });
        attrs.add(new Map<String, Object>{
            'attributeName' => ATTR_ST_CHURNED_AMOUNT,
            'attributeValue' => String.valueOf(rollup.churnedAmount.setScale(AMOUNT_SCALE, RoundingMode.HALF_UP))
        });
        attrs.add(new Map<String, Object>{
            'attributeName' => ATTR_ST_RENEWAL_AMOUNT,
            'attributeValue' => String.valueOf(rollup.renewalAmount.setScale(AMOUNT_SCALE, RoundingMode.HALF_UP))
        });
        attrs.add(new Map<String, Object>{
            'attributeName' => ATTR_ST_NRR,
            'attributeValue' => String.valueOf(rollup.nrr.setScale(AMOUNT_SCALE, RoundingMode.HALF_UP))
        });
        attrs.add(new Map<String, Object>{
            'attributeName' => ATTR_ST_ARR,
            'attributeValue' => String.valueOf(rollup.arr.setScale(AMOUNT_SCALE, RoundingMode.HALF_UP))
        });
        attrs.add(new Map<String, Object>{
            'attributeName' => ATTR_ST_NET_NEW_ARR,
            'attributeValue' => String.valueOf(rollup.netNewARR.setScale(AMOUNT_SCALE, RoundingMode.HALF_UP))
        });
        attrs.add(new Map<String, Object>{
            'attributeName' => ATTR_ST_EXPANSION_ARR,
            'attributeValue' => String.valueOf(rollup.expansionARR.setScale(AMOUNT_SCALE, RoundingMode.HALF_UP))
        });
        attrs.add(new Map<String, Object>{
            'attributeName' => ATTR_ST_CHURNED_ARR,
            'attributeValue' => String.valueOf(rollup.churnedARR.setScale(AMOUNT_SCALE, RoundingMode.HALF_UP))
        });
        attrs.add(new Map<String, Object>{
            'attributeName' => ATTR_ST_RENEWAL_ARR,
            'attributeValue' => String.valueOf(rollup.renewalARR.setScale(AMOUNT_SCALE, RoundingMode.HALF_UP))
        });
        attrs.add(new Map<String, Object>{
            'attributeName' => ATTR_ST_I_ARR,
            'attributeValue' => String.valueOf(rollup.iARR.setScale(AMOUNT_SCALE, RoundingMode.HALF_UP))
        });
        System.debug(LoggingLevel.DEBUG, DBG + '.buildSalesTransactionAttributes: exit attrs=' + attrs.size());
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
        System.debug(LoggingLevel.DEBUG, DBG + '.appendSalesTransactionNodeUpdate: enter');
        List<Object> stPath = salesTransactionDataPath(salesTransactionNode);
        if (stPath == null) {
            System.debug(
                LoggingLevel.WARN,
                DBG + '.appendSalesTransactionNodeUpdate: no SalesTransaction dataPath — skipping header update'
            );
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
            DBG + '.appendSalesTransactionNodeUpdate: exit — appended header rollup (' +
                rollup.contributingLineCount + ' lines contributed)'
        );
    }

    /**
     * Running totals of per-line revenue metrics, accumulated during the line loop
     * and written to the SalesTransaction header node after all lines are processed.
     */
    private class TransactionRollupTotals {
        public Decimal totalInstallBase = 0;
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
        public Integer contributingLineCount = 0;

        public void accumulateLine(
            Decimal lineTotal, Decimal lineNetNew, Decimal lineExpansion,
            Decimal lineChurned, Decimal lineRenewal, Decimal lineNrr,
            Decimal lineArr, Decimal lineNetNewArr, Decimal lineExpansionArr,
            Decimal lineChurnedArr, Decimal lineRenewalArr, Decimal lineIarr
        ) {
            System.debug(LoggingLevel.DEBUG, DBG + '.TransactionRollupTotals.accumulateLine: enter');
            totalInstallBase += nz(lineTotal);
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
            System.debug(
                LoggingLevel.DEBUG,
                DBG + '.TransactionRollupTotals.accumulateLine: exit lineCount=' + contributingLineCount +
                    ' runningInstallBase=' + totalInstallBase
            );
        }

        private Decimal nz(Decimal d) {
            return d == null ? 0 : d;
        }
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
        public String transactionActionType;
        public String pricingTermUnit;
        public Decimal pricingTerm;
        public Decimal pricingTermCount;
        public Decimal netTotalPrice;
        public Decimal startQuantity;
        public Decimal endQuantity;
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