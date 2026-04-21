/**
 * Unit tests for proration/date/Id parsing helpers used by RLM_AssetStatePeriodSignalingHook.
 * Full hook execution requires a live pricing context (IndustriesContext); validate in an org via Procedure Plan.
 */
@IsTest
private class RLM_AssetStatePeriodSignalingHookTest {
    @IsTest
    static void inclusiveDayCount_singleDay() {
        Date d = Date.newInstance(2025, 6, 1);
        System.assertEquals(1, RLM_AssetStatePeriodSignalingHook.inclusiveDayCount(d, d));
    }

    @IsTest
    static void inclusiveDayCount_span() {
        Date a = Date.newInstance(2025, 6, 1);
        Date b = Date.newInstance(2025, 6, 3);
        System.assertEquals(3, RLM_AssetStatePeriodSignalingHook.inclusiveDayCount(a, b));
    }

    @IsTest
    static void inclusiveDayCount_invalid() {
        Date a = Date.newInstance(2025, 6, 5);
        Date b = Date.newInstance(2025, 6, 1);
        System.assertEquals(0, RLM_AssetStatePeriodSignalingHook.inclusiveDayCount(a, b));
        System.assertEquals(0, RLM_AssetStatePeriodSignalingHook.inclusiveDayCount(null, a));
    }

    @IsTest
    static void proratedAmount_fullMonthOverlap() {
        Date lineS = Date.newInstance(2025, 1, 1);
        Date lineE = Date.newInstance(2025, 1, 31);
        Date aspS = Date.newInstance(2025, 1, 1);
        Date aspE = Date.newInstance(2025, 1, 31);
        Decimal mrr = 100;
        Decimal got = RLM_AssetStatePeriodSignalingHook.proratedAmountForOverlap(lineS, lineE, aspS, aspE, mrr);
        System.assertEquals(100, got, 'Full calendar month overlap = 1 * MRR');
    }

    @IsTest
    static void proratedAmount_partialMonthOverlap() {
        Date lineS = Date.newInstance(2025, 1, 1);
        Date lineE = Date.newInstance(2025, 1, 15);
        Date aspS = Date.newInstance(2025, 1, 1);
        Date aspE = Date.newInstance(2025, 1, 31);
        Decimal mrr = 310;
        Decimal got = RLM_AssetStatePeriodSignalingHook.proratedAmountForOverlap(lineS, lineE, aspS, aspE, mrr);
        Decimal expected = mrr * (Decimal.valueOf(15) / Decimal.valueOf(31));
        System.assertEquals(expected, got, 'Partial month fraction = 15/31 * MRR');
    }

    @IsTest
    static void proratedAmount_nullAmount() {
        Date d1 = Date.newInstance(2025, 1, 1);
        Date d2 = Date.newInstance(2025, 1, 5);
        System.assertEquals(
            0,
            RLM_AssetStatePeriodSignalingHook.proratedAmountForOverlap(d1, d2, d1, d2, null)
        );
    }

    @IsTest
    static void proratedAmount_noOverlap() {
        Date lineS = Date.newInstance(2025, 2, 1);
        Date lineE = Date.newInstance(2025, 2, 5);
        Date aspS = Date.newInstance(2025, 1, 1);
        Date aspE = Date.newInstance(2025, 1, 10);
        System.assertEquals(
            0,
            RLM_AssetStatePeriodSignalingHook.proratedAmountForOverlap(lineS, lineE, aspS, aspE, 100)
        );
    }

    @IsTest
    static void proratedAmount_singleDayOverlap() {
        Date d = Date.newInstance(2025, 3, 1);
        Decimal mrr = 42;
        Decimal got = RLM_AssetStatePeriodSignalingHook.proratedAmountForOverlap(d, d, d, d, mrr);
        Decimal expected = mrr * (Decimal.valueOf(1) / Decimal.valueOf(31));
        System.assertEquals(expected, got, 'Single day in March = 1/31 * MRR');
    }

    @IsTest
    static void parseIdTag_nested() {
        Id userId = UserInfo.getUserId();
        Map<String, Object> tags = new Map<String, Object>{
            'Account' => new Map<String, Object>{ 'tagValue' => String.valueOf(userId) }
        };
        System.assertEquals(userId, RLM_AssetStatePeriodSignalingHook.parseIdTag(tags, 'Account'));
    }

    @IsTest
    static void parseContextDate_nestedIso() {
        Map<String, Object> tags = new Map<String, Object>{
            'StartDate' => new Map<String, Object>{ 'tagValue' => '2025-04-15T00:00:00.000Z' }
        };
        System.assertEquals(
            Date.newInstance(2025, 4, 15),
            RLM_AssetStatePeriodSignalingHook.parseContextDate(tags, 'StartDate')
        );
    }

    @IsTest
    static void isOneTime_trueFalse() {
        System.assertEquals(true, RLM_AssetStatePeriodSignalingHook.isOneTime('OneTime'));
        System.assertEquals(true, RLM_AssetStatePeriodSignalingHook.isOneTime('onetime'));
        System.assertEquals(false, RLM_AssetStatePeriodSignalingHook.isOneTime('Recurring'));
        System.assertEquals(false, RLM_AssetStatePeriodSignalingHook.isOneTime(null));
    }

    @IsTest
    static void resolveAccountIdFromNode_nullNode() {
        System.assertEquals(null, RLM_AssetStatePeriodSignalingHook.resolveAccountIdFromNode(null));
    }

    @IsTest
    static void resolveAccountIdFromNode_noTagValue() {
        Map<String, Object> node = new Map<String, Object>{ 'dataPath' => new List<Object>{ 'a' } };
        System.assertEquals(null, RLM_AssetStatePeriodSignalingHook.resolveAccountIdFromNode(node));
    }

    @IsTest
    static void resolveAccountIdFromNode_resolves_Account() {
        Id userId = UserInfo.getUserId();
        Map<String, Object> node = new Map<String, Object>{
            'tagValue' => new Map<String, Object>{
                'Account' => new Map<String, Object>{ 'tagValue' => String.valueOf(userId) }
            }
        };
        System.assertEquals(userId, RLM_AssetStatePeriodSignalingHook.resolveAccountIdFromNode(node));
    }

    @IsTest
    static void resolveAccountIdFromNode_fallsBackToQuoteAccount() {
        Id userId = UserInfo.getUserId();
        Map<String, Object> node = new Map<String, Object>{
            'tagValue' => new Map<String, Object>{
                'QuoteAccount' => new Map<String, Object>{ 'tagValue' => String.valueOf(userId) }
            }
        };
        System.assertEquals(userId, RLM_AssetStatePeriodSignalingHook.resolveAccountIdFromNode(node));
    }

    @IsTest
    static void salesTransactionDataPath_nullNode() {
        System.assertEquals(null, RLM_AssetStatePeriodSignalingHook.salesTransactionDataPath(null));
    }

    @IsTest
    static void salesTransactionDataPath_noDataPath() {
        Map<String, Object> node = new Map<String, Object>{
            'tagValue' => new Map<String, Object>{ 'Account' => 'x' }
        };
        System.assertEquals(null, RLM_AssetStatePeriodSignalingHook.salesTransactionDataPath(node));
    }

    @IsTest
    static void salesTransactionDataPath_stripsContextRoot() {
        List<Object> original = new List<Object>{ 'ctx-instance-id', 'quote-id' };
        Map<String, Object> node = new Map<String, Object>{
            'dataPath' => original
        };
        List<Object> result = RLM_AssetStatePeriodSignalingHook.salesTransactionDataPath(node);
        System.assertEquals(1, result.size(), 'Expected single-segment path (context root stripped)');
        System.assertEquals('quote-id', result[0]);
        result.add('extra');
        System.assertEquals(2, original.size(), 'Original dataPath should not be mutated');
    }

    @IsTest
    static void salesTransactionDataPath_rootOnly_returnsNull() {
        Map<String, Object> node = new Map<String, Object>{
            'dataPath' => new List<Object>{ 'ctx-instance-id' }
        };
        System.assertEquals(null, RLM_AssetStatePeriodSignalingHook.salesTransactionDataPath(node));
    }

    @IsTest
    static void execute_nullRequest_fails() {
        RLM_AssetStatePeriodSignalingHook hook = new RLM_AssetStatePeriodSignalingHook();
        RevSignaling.TransactionResponse resp = hook.execute(null);
        System.assertEquals(RevSignaling.TransactionStatus.FAILED, resp.status);
    }

    @IsTest
    static void execute_blankCtxInstanceId_fails() {
        RLM_AssetStatePeriodSignalingHook hook = new RLM_AssetStatePeriodSignalingHook();
        RevSignaling.TransactionRequest req =
            (RevSignaling.TransactionRequest) JSON.deserialize(
                '{"ctxInstanceId":""}', RevSignaling.TransactionRequest.class
            );
        RevSignaling.TransactionResponse resp = hook.execute(req);
        System.assertEquals(RevSignaling.TransactionStatus.FAILED, resp.status);
    }

    @IsTest
    static void buildLineContextRow_deleted_skips() {
        Map<String, Object> itemNode = new Map<String, Object>{
            'dataPath' => new List<Object>{ 'a', 'b', 'c' },
            'tagValue' => new Map<String, Object>{
                'LineItem' => new Map<String, Object>{ 'tagValue' => 'x', 'dmlStatus' => 'DELETED' }
            }
        };
        RLM_AssetStatePeriodSignalingHook.LineContextRow row = RLM_AssetStatePeriodSignalingHook.buildLineContextRow(
            itemNode
        );
        System.assertEquals(true, row.skip);
    }

    @IsTest
    static void buildLineContextRow_parsesDates() {
        Id productId = UserInfo.getUserId();
        Map<String, Object> itemNode = new Map<String, Object>{
            'dataPath' => new List<Object>{ 'root', 'mid', 'leaf' },
            'tagValue' => new Map<String, Object>{
                'LineItem' => new Map<String, Object>{ 'tagValue' => 'QLI001' },
                'EffectiveFrom' => new Map<String, Object>{ 'tagValue' => '2025-01-01' },
                'EffectiveTo' => new Map<String, Object>{ 'tagValue' => '2025-01-31' },
                'Product' => new Map<String, Object>{ 'tagValue' => String.valueOf(productId) },
                'SellingModelType' => new Map<String, Object>{ 'tagValue' => 'Recurring' }
            }
        };
        RLM_AssetStatePeriodSignalingHook.LineContextRow row = RLM_AssetStatePeriodSignalingHook.buildLineContextRow(
            itemNode
        );
        System.assertEquals(false, row.skip);
        System.assertEquals(Date.newInstance(2025, 1, 1), row.lineStartDate);
        System.assertEquals(Date.newInstance(2025, 1, 31), row.lineEndDate);
        System.assertEquals(productId, row.productId);
        System.assertEquals('Recurring', row.sellingModelType);
        List<Object> updatePath = row.pathForFieldUpdate();
        System.assertEquals(2, updatePath.size(), 'Expected [quote, line] — context-instance root stripped');
        System.assertEquals('mid', updatePath[0]);
        System.assertEquals('leaf', updatePath[1]);
    }
}
