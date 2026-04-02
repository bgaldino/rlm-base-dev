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
    static void proratedAmount_fullOverlap() {
        Date lineS = Date.newInstance(2025, 1, 1);
        Date lineE = Date.newInstance(2025, 1, 10);
        Date aspS = Date.newInstance(2025, 1, 1);
        Date aspE = Date.newInstance(2025, 1, 10);
        Decimal amt = 100;
        Decimal got = RLM_AssetStatePeriodSignalingHook.proratedAmountForOverlap(lineS, lineE, aspS, aspE, amt);
        System.assertEquals(100, got);
    }

    @IsTest
    static void proratedAmount_halfOverlap() {
        Date lineS = Date.newInstance(2025, 1, 1);
        Date lineE = Date.newInstance(2025, 1, 5);
        Date aspS = Date.newInstance(2025, 1, 1);
        Date aspE = Date.newInstance(2025, 1, 10);
        // overlap 5 days, asp 10 days -> 50%
        Decimal got = RLM_AssetStatePeriodSignalingHook.proratedAmountForOverlap(lineS, lineE, aspS, aspE, 100);
        System.assertEquals(50, got);
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
    static void proratedAmount_zeroAspDays_usesFullAmountWhenOverlap() {
        // Same start/end for ASP: inclusive count is 1, not zero — normal path
        Date d = Date.newInstance(2025, 3, 1);
        System.assertEquals(42, RLM_AssetStatePeriodSignalingHook.proratedAmountForOverlap(d, d, d, d, 42));
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
                'StartDate' => new Map<String, Object>{ 'tagValue' => '2025-01-01' },
                'EndDate' => new Map<String, Object>{ 'tagValue' => '2025-01-31' },
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
        System.assertEquals(2, row.pathForFieldUpdate().size());
    }
}
