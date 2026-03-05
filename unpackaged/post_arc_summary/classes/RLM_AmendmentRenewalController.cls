public with sharing class RLM_AmendmentRenewalController {

    @AuraEnabled(cacheable=true)
    public static RLM_AmendmentRenewalDTO getAmendmentRenewalSummary(Id quoteId) {
        return RLM_AmendmentRenewalService.getAmendmentRenewalSummary(quoteId);
    }

    @AuraEnabled
    public static List<RLM_ExpansionAttritionDTO> getExpansionAttritionDetails(Id quoteId) {
        return RLM_AmendmentRenewalService.getExpansionAttritionDetails(quoteId);
    }
}