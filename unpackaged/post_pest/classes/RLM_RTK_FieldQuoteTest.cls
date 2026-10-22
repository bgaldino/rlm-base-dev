@IsTest
private class RLM_RTK_FieldQuoteTest {
    @TestSetup
    static void setup() {
        insert new RLM_RTK_Service_Zone__c(
            Name = 'Chicago Suburbs',
            Postal_Code_Prefix__c = '60108',
            Zone_Code__c = 'Suburb',
            Zone_Multiplier__c = 1.00
        );
        insert new RLM_RTK_Service_Zone__c(
            Name = 'Rural Fox Valley',
            Postal_Code_Prefix__c = '60140',
            Zone_Code__c = 'Rural',
            Zone_Multiplier__c = 1.20
        );
        insert new RLM_RTK_Service_Zone__c(
            Name = 'Dense Chicago Metro',
            Postal_Code_Prefix__c = '606',
            Zone_Code__c = 'DenseMetro',
            Zone_Multiplier__c = 0.95
        );
    }

    @IsTest
    static void zoneResolve_exactZipAndPrefix() {
        RLM_RTK_ZonePricing.ZoneResult suburb = RLM_RTK_ZonePricing.resolve('60108');
        System.assertEquals('Suburb', suburb.zoneCode);
        System.assertEquals(1.00, suburb.multiplier);

        RLM_RTK_ZonePricing.ZoneResult rural = RLM_RTK_ZonePricing.resolve('60140');
        System.assertEquals('Rural', rural.zoneCode);
        System.assertEquals(1.20, rural.multiplier);

        RLM_RTK_ZonePricing.ZoneResult metro = RLM_RTK_ZonePricing.resolve('60614');
        System.assertEquals('DenseMetro', metro.zoneCode);
        System.assertEquals(0.95, metro.multiplier);

        System.assertEquals(70.80, RLM_RTK_ZonePricing.apply(59, 1.20));
    }

    @IsTest
    static void attributeUplift_severityAndSqFt() {
        System.assertEquals(94, RLM_RTK_FieldQuote.applyAttributeUplift(59, 'Heavy', '2000to3500'));
        System.assertEquals(59, RLM_RTK_FieldQuote.applyAttributeUplift(59, 'Light', 'Under2000'));
    }

    @IsTest
    static void invocable_zoneResolve() {
        RLM_RTK_ZonePricing.ZoneRequest request = new RLM_RTK_ZonePricing.ZoneRequest();
        request.postalCode = '60108';
        List<RLM_RTK_ZonePricing.ZoneResponse> results =
            RLM_RTK_ZonePricing.resolveInvocable(new List<RLM_RTK_ZonePricing.ZoneRequest>{ request });
        System.assertEquals(1, results.size());
        System.assertEquals('Suburb', results[0].zoneCode);
    }
}
