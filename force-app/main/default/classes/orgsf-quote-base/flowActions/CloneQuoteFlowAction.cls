public with sharing class CloneQuoteFlowAction {
    //@TestVisible
    //private static ProductTermsSelector termsSelector = new ProductTermsSelector();
    //private static IAppliedTermsDao termsDao = (IAppliedTermsDao) new AppliedTermsDao();
    //@TestVisible
    //private static ITenantUIDAO tadsDao = (ITenantUIDAO) new TenantUIDAO();
    @TestVisible
    private static AmendQuoteDataSelector amendQuoteDataSelector = new AmendQuoteDataSelector();

    @InvocableMethod(label='Clone Quote')
    public static List<String> flowActionCloneQuote(List<CloneQuoteFlowActionRequest> requestList) {
        List<String> result = new List<String>();
        IPlaceQuoteService placeQuoteService = (IPlaceQuoteService) ServiceRegistry.getInstance('IPlaceQuoteService');
        IQuoteLineDAO quoteLineDAO = (IQuoteLineDAO) ServiceRegistry.getInstance('IQuoteLineDAO');
        // Not bulkified
        Id originalQuoteId = requestList[0].originalQuoteId;
        Quote clonedQuote = requestList[0].quote;
        List<QuoteLineItem> originalQuoteLineItems = quoteLineDAO.getQuoteLinesByQuoteId(originalQuoteId);

        PlaceQuoteServiceRequestBuilder.QuoteRequest quoteRequest = new PlaceQuoteServiceRequestBuilder.QuoteRequest();
        quoteRequest.quote = clonedQuote;
        quoteRequest.method = 'POST';

        List<PlaceQuoteServiceRequestBuilder.QuoteLineItemRequest> quoteLineItemRequests = prepareQuoteLineItemRequests(clonedQuote, originalQuoteLineItems);
        Map<Id, QuoteAction> quoteActions = new Map<Id, QuoteAction>();

        quoteActions = amendQuoteDataSelector.selectQuoteActionsByQuoteIds(new Set<Id>{originalQuoteId});

        PlaceQuoteServiceRequest serviceRequest = new PlaceQuoteServiceRequestBuilder()
            .quote(quoteRequest)
            .quoteActions(quoteActions)
            .quoteLineItems(quoteLineItemRequests)
            .method('POST')
            .graphId('cloneQuote')
            .pricingPreference(PlaceQuote.PricingPreferenceEnum.SYSTEM)
            .configEnum(PlaceQuote.ConfigurationInputEnum.RUNANDALLOWERRORS)
            .config(new PlaceQuote.ConfigurationOptionsInput())
            .build();

        PlaceQuoteServiceResponse placeQuoteServiceResponse = placeQuoteService.placeQuote(serviceRequest);
        Id clonedQuoteId = placeQuoteServiceResponse.quoteId;
        result.add(clonedQuoteId);
        //cloneTADs(originalQuoteId, clonedQuoteId);
        //cloneTerms(originalQuoteId, clonedQuoteId);
        return result;
    }

    public class CloneQuoteFlowActionRequest {
        @InvocableVariable(required=true)
        public Id originalQuoteId;
        @InvocableVariable(required=true)
        public Quote quote;
    }

    private static List<PlaceQuoteServiceRequestBuilder.QuoteLineItemRequest> prepareQuoteLineItemRequests(Quote quote, List<QuoteLineItem> quoteLineItems) {
        List<PlaceQuoteServiceRequestBuilder.QuoteLineItemRequest> quoteLineItemRequests = new List<PlaceQuoteServiceRequestBuilder.QuoteLineItemRequest>();
        for (QuoteLineItem quoteLineItem : quoteLineItems) {
            QuoteLineItem clonedQuoteLineItem = new QuoteLineItem();
            clonedQuoteLineItem.Quantity = quoteLineItem.Quantity;
            clonedQuoteLineItem.Description = quoteLineItem.Description;
            clonedQuoteLineItem.Product2Id = quoteLineItem.Product2Id;
            clonedQuoteLineItem.ServiceDate = quoteLineItem.ServiceDate;
            clonedQuoteLineItem.BillingFrequency = quoteLineItem.BillingFrequency;
            clonedQuoteLineItem.Discount = quoteLineItem.Discount;
            clonedQuoteLineItem.DiscountAmount = quoteLineItem.DiscountAmount;
            clonedQuoteLineItem.PeriodBoundary = quoteLineItem.PeriodBoundary;
            clonedQuoteLineItem.Tenant__c = quoteLineItem.Tenant__c;
            clonedQuoteLineItem.PricebookEntryId = quoteLineItem.PricebookEntryId;
            clonedQuoteLineItem.PeriodBoundaryDay = quoteLineItem.PeriodBoundaryDay;
            clonedQuoteLineItem.UnitPrice = quoteLineItem.UnitPrice;
            clonedQuoteLineItem.StartDate = quote.ServiceStartDate__c;
            clonedQuoteLineItem.SubscriptionTerm = Integer.valueOf(quote.Term__c);
            clonedQuoteLineItem.EndDate = quote.ServiceEndDate__c;
            clonedQuoteLineItem.QuoteActionId = quoteLineItem.QuoteActionId;
            clonedQuoteLineItem.StartQuantity = quoteLineItem.StartQuantity;    
            clonedQuoteLineItem.BillingCompanyName__c = quoteLineItem.BillingCompanyName__c;

            PlaceQuoteServiceRequestBuilder.QuoteLineItemRequest quoteLineItemRequest = new PlaceQuoteServiceRequestBuilder.QuoteLineItemRequest();
            quoteLineItemRequest.quoteLineItem = clonedQuoteLineItem;
            quoteLineItemRequest.method = 'POST';

            quoteLineItemRequests.add(quoteLineItemRequest);
        }

        return quoteLineItemRequests;
    }
/* 
    private static void cloneTerms(Id originalQuoteId, Id clonedQuoteId) {
        List<AppliedSpecialTerm__c> appliedTermsList = termsSelector.getAppliedSpecialTerms(new Set<Id>{ originalQuoteId });
        List<AppliedSpecialTerm__c> optionalTermsList = new List<AppliedSpecialTerm__c>();
        for (AppliedSpecialTerm__c term : appliedTermsList) {
            if (term.Default__c == false) {
                term.Quote__c = clonedQuoteId;
                term.Id = null;
                optionalTermsList.add(term);
            }
        }
        termsDao.upsertAppliedTerms(optionalTermsList);
    }

    private static void cloneTADs(Id originalQuoteId, Id clonedQuoteId) {
        List<TenantAssociationData__c> tadsList = tadsDAO.getTADRecordsToClone(originalQuoteId);
        List<Id> oldParentTADIds = new List<Id>();
        List<Id> parentTADIds = new List<Id>();
        List<TenantAssociationData__c> cloneParentTADsList = new List<TenantAssociationData__c>();
        List<TenantAssociationData__c> cloneChildTADsList = new List<TenantAssociationData__c>();
        List<TenantAssociationData__c> cloneChildTADsList2 = new List<TenantAssociationData__c>();
        Map<Id, Id> oldToNewParentTadMap = new Map<Id, Id>();
        for (TenantAssociationData__c tad : tadsList) {
            tad.Quote__c = clonedQuoteId;
            oldToNewParentTadMap.put(tad.Id, null);  
            if(tad.AssociationRole__c == 'Primary' && tad.ParentTenantId__c == NULL){
                oldParentTADIds.add(tad.Id);
                tad.Id = null;
                cloneParentTADsList.add(tad); 
            }else{
                tad.Id = null;
                cloneChildTADsList.add(tad);
            }
               
        }
        if(cloneParentTADsList.size() > 0){
            parentTADIds = tadsDAO.insertTADRecords(cloneParentTADsList);
            if(Test.isRunningTest()){
                parentTADIds = new List<Id>();
                parentTADIds.add('a1PO900001mx6OcMAI');
            }
        }
        for (Integer i = 0; i < cloneParentTADsList.size(); i++) {
            oldToNewParentTadMap.put(oldParentTADIds[i], parentTADIds[i]);
        }
        for (TenantAssociationData__c tad2 : cloneChildTADsList) {
            tad2.ParentTenantId__c = oldToNewParentTadMap.get(tad2.ParentTenantId__c);
            cloneChildTADsList2.add(tad2);
        }
        if(cloneChildTADsList2.size() > 0){
            tadsDAO.insertTADRecords(cloneChildTADsList2);
        }
        
    }
*/
}