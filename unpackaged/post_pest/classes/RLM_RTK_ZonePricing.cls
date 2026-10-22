/**
 * Location-aware pricing for Rentokil residential quotes.
 * Looks up RLM_RTK_Service_Zone__c by 5-digit ZIP, then 3-digit prefix.
 * Default multiplier is 1.0 (Chicago suburb / Bloomingdale) when no zone matches.
 */
public with sharing class RLM_RTK_ZonePricing {
    public class ZoneResult {
        @AuraEnabled public String postalCode;
        @AuraEnabled public String zoneCode;
        @AuraEnabled public String zoneName;
        @AuraEnabled public Decimal multiplier;
        @AuraEnabled public String matchedPrefix;
    }

    public static ZoneResult resolve(String postalCode) {
        ZoneResult result = new ZoneResult();
        result.postalCode = postalCode;
        result.multiplier = 1.0;
        result.zoneCode = 'Suburb';
        result.zoneName = 'Default Suburb';
        if (String.isBlank(postalCode)) {
            return result;
        }
        String digits = postalCode.replaceAll('[^0-9]', '');
        if (digits.length() < 3) {
            return result;
        }
        String five = digits.length() >= 5 ? digits.substring(0, 5) : null;
        String three = digits.substring(0, 3);
        List<String> prefixes = new List<String>();
        if (five != null) {
            prefixes.add(five);
        }
        prefixes.add(three);
        List<RLM_RTK_Service_Zone__c> zones = [
            SELECT Name, Postal_Code_Prefix__c, Zone_Code__c, Zone_Multiplier__c
            FROM RLM_RTK_Service_Zone__c
            WHERE Postal_Code_Prefix__c IN :prefixes
        ];
        Map<String, RLM_RTK_Service_Zone__c> byPrefix = new Map<String, RLM_RTK_Service_Zone__c>();
        for (RLM_RTK_Service_Zone__c zone : zones) {
            byPrefix.put(zone.Postal_Code_Prefix__c, zone);
        }
        RLM_RTK_Service_Zone__c matched = five != null ? byPrefix.get(five) : null;
        if (matched == null) {
            matched = byPrefix.get(three);
        }
        if (matched != null) {
            result.zoneCode = matched.Zone_Code__c;
            result.zoneName = matched.Name;
            result.multiplier = matched.Zone_Multiplier__c;
            result.matchedPrefix = matched.Postal_Code_Prefix__c;
        }
        return result;
    }

    public static Decimal apply(Decimal unitPrice, Decimal multiplier) {
        if (unitPrice == null) {
            return null;
        }
        Decimal factor = multiplier == null ? 1.0 : multiplier;
        return (unitPrice * factor).setScale(2, RoundingMode.HALF_UP);
    }

    public class ZoneRequest {
        @InvocableVariable(required=true) public String postalCode;
    }

    public class ZoneResponse {
        @InvocableVariable public String postalCode;
        @InvocableVariable public String zoneCode;
        @InvocableVariable public String zoneName;
        @InvocableVariable public Decimal multiplier;
        @InvocableVariable public String matchedPrefix;
    }

    @InvocableMethod(label='Resolve RTK Service Zone' category='Rentokil'
        description='Resolves the Rentokil service zone and price multiplier for a postal code.')
    public static List<ZoneResponse> resolveInvocable(List<ZoneRequest> requests) {
        List<ZoneResponse> results = new List<ZoneResponse>();
        for (ZoneRequest request : requests) {
            ZoneResult zone = resolve(request.postalCode);
            ZoneResponse response = new ZoneResponse();
            response.postalCode = zone.postalCode;
            response.zoneCode = zone.zoneCode;
            response.zoneName = zone.zoneName;
            response.multiplier = zone.multiplier;
            response.matchedPrefix = zone.matchedPrefix;
            results.add(response);
        }
        return results;
    }
}
