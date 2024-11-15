Public with sharing class ProductTermsSelector{
    
    public static final set<String> TERM_TYPE = new set<String>{'PST'};
    public static final set<String> QUOTE_CRITICAL_STATUS = new set<String>{'Draft','Offer','In Review','Approved','Rejected'};
    public static final set<String> QUOTE_STANDARD_STATUS = new set<String>{'Draft','Offer','Rejected'};
    public static final set<String> OPPORTUNITY_STAGE = new set<String>{'Closed Won','Closed Lost'};
    public static final set<String> QUOTE_OFFER_STATUS = new set<String>{'Offer'};
    private static AccessLevel accessLevelMode = Test.isRunningTest()? AccessLevel.SYSTEM_MODE: AccessLevel.USER_MODE;

    public List<Term__c> getMandatoryTerms(set<Id> productIds, set<String> billingLanguages){
        return [
                SELECT id,SubType__c,
                (SELECT id,Term__c,Product__c,Product__r.name FROM Product_Term_Associations__r WHERE Product__c IN :productIds),
                (SELECT id, Language__c,Term__c,Text__c,Term__r.RestrictedAppliedTermApprovals__c,Term__r.CustomRoutingApprovals__c,Term__r.Persistent__c
                FROM TermTexts__r
                WHERE  Language__c IN :billingLanguages
                AND EffectiveStartDate__c <= TODAY
                AND Status__c = 'Active')
                FROM Term__c
                WHERE Recordtype.Name IN :TERM_TYPE WITH SECURITY_ENFORCED
        ];
    }

    public List<AppliedSpecialTerm__c> getAppliedSpecialTerms(set<Id> quoteIds, set<String> quoteLineIds){
        Map<Id,AppliedSpecialTerm__c> returnAppliedTermsMap = new Map<Id,AppliedSpecialTerm__c>();
        For(AppliedSpecialTerm__c appliedData :[SELECT id,RelatedLineIDs__c,ProductNames__c,ProductIDs__c,ParentTerm__c,Quote__c,SourceTermText__c FROM AppliedSpecialTerm__c WHERE Quote__c IN:quoteIds WITH SECURITY_ENFORCED]){
            For(String lineId :quoteLineIds){
                if(!returnAppliedTermsMap.containsKey(appliedData.id) && appliedData.RelatedLineIDs__c != null && appliedData.RelatedLineIDs__c.contains(lineId)){
                    returnAppliedTermsMap.put(appliedData.id, appliedData);
                }
            }
        }
        return returnAppliedTermsMap.values();
    }

    public List<AppliedSpecialTerm__c> getAppliedSpecialTerms(set<Id> quoteIds){
        return [
                SELECT id,RelatedLineIDs__c,ProductNames__c,ProductIDs__c,ParentTerm__c,SourceContractTerm__c,
                Quote__c,SourceTermText__c,Quote__r.TermUpdatesRequired__c,SourceTermTextStatus__c,
                Default__c,CustomRoutingApprovals__c,RestrictedAppliedTermApprovals__c,OmittedBy__c,
                Language__c,Persistent__c,Custom__c,Editable__c,OmitFromQuote__c,TermText__c,TokenizedText__c,
                StrippedHtmlTermText__c,HelpText__c,ParentTerm__r.ContainsToken__c
                FROM AppliedSpecialTerm__c
                WHERE Quote__c IN:quoteIds WITH SECURITY_ENFORCED
        ];
    }

    public List<AppliedSpecialTerm__c> getAppliedSpecialTermsSelector(Set<string> termTextLanguageSet,set<Id> previousTermTextIdSet,Boolean hasCriticalUpdate){
        set<String> quoteStatus = new set<String>(QUOTE_STANDARD_STATUS);
        if(hasCriticalUpdate){
            quoteStatus.addAll(QUOTE_CRITICAL_STATUS);
        }
        return [SELECT Id,Quote__c,ParentTerm__c,Language__c,SourceTermText__c
        FROM AppliedSpecialTerm__c
        WHERE Quote__r.Status IN :quoteStatus AND
        Quote__r.ServiceEndDate__c >= TODAY AND
        Quote__r.Opportunity.StageName NOT IN :OPPORTUNITY_STAGE AND
        Language__c IN :termTextLanguageSet AND
        SourceTermText__c IN :previousTermTextIdSet AND
        SourceContractTerm__c = NULL 
        WITH SECURITY_ENFORCED];
    }

    public List<CustomNotificationType> getCustomNotificationType(String customNotification){
        return [SELECT Id, DeveloperName
        FROM CustomNotificationType
        WHERE DeveloperName = :customNotification
        WITH SECURITY_ENFORCED];
    }

    public List<Report> getReport(String reportName){
        return [SELECT Id,DeveloperName
        FROM Report
        WHERE DeveloperName = :reportName
        WITH SECURITY_ENFORCED];
    }

    public List<TermText__c> getTermText(Set<Id> previousTermTextId,Set<String> languageSet){
        return [SELECT Id, Language__c, PreviousVersion__c,TermUpdatesRequired__c
                FROM TermText__c
                WHERE PreviousVersion__c IN :previousTermTextId AND
                Language__c IN :languageSet AND
                Status__c = :TermBaseConstants.STATUS_ACTIVE
                WITH SECURITY_ENFORCED];
    }

    /**
     method name : getAppliedTermsFromContract
     purpose : get AppliedContractTerm from Contract
     input parameters : Set<Id>
     return type : List<AppliedContractTerm__c>
    **/
    public List<AppliedContractTerm__c> getAppliedTermsFromContract(Set<Id> contractIdSet){
        return [SELECT Id,ParentTerm__c,SourceTermText__c,TokenizedText__c,Contract__c
                FROM AppliedContractTerm__c 
                WHERE Contract__c IN :contractIdSet
                WITH SECURITY_ENFORCED];
    }

    /**
     method name : getOfferQuotesAndAppliedTerms
     purpose : get Offered Quote and related 
     input parameters : Set<String>
     return type : List<Quote>
    **/
    public List<Quote> getOfferQuotesAndAppliedTerms(Set<String> quoteIdSet){
        return [SELECT Id,ContractId,
                    (SELECT Id,ParentTerm__c,SourceTermText__c,TokenizedText__c,
                     Quote__c,Quote__r.ContractId
                     FROM AppliedSpecialTerms__r 
                     WHERE SourceContractTerm__c = NULL AND 
                     OmitFromQuote__c = FALSE)
                FROM Quote 
                WHERE Id IN :quoteIdSet AND
                Status IN :QUOTE_OFFER_STATUS AND
                ContractTermEvalComplete__c = False
                WITH SECURITY_ENFORCED];
    }
    
    /**method name : getContractTerms
     purpose : fetch all the Contract Special Terms from Contracts
     input parameters : Set<Id>
     return type : List<AppliedContractTerm__c>
    **/
    public List<AppliedContractTerm__c> getContractTerms(Set<Id> contractIdSet){
        //fetch Contract Special Terms
        return [SELECT Id,ParentTerm__c,Persistent__c,SourceTermText__c,Contract__c,OmitFromQuote__c,
                SourceTermText__r.HelpText__c,TokenizedText__c,Language__c,Custom__c,OmittedBy__c,
                CreatedDate,CurrencyIsoCode,ParentTerm__r.CustomRoutingApprovals__c,ParentTerm__r.RestrictedAppliedTermApprovals__c
                FROM AppliedContractTerm__c
                WHERE Contract__c IN :contractIdSet
                AND Persistent__c = TRUE
                WITH SECURITY_ENFORCED];
    }
    
    public List<QuoteLineItem> getQuoteLineItems(set<String> quoteLineItemIds){
        return [
                SELECT Id,QuoteId, Quantity,Product2Id,Product2.name,UnitPrice,NetTotalPrice,Discount,EndDate,ApprovalLevel__c,CurrencyIsoCode,totalPrice
                FROM QuoteLineItem
                WHERE Id IN:quoteLineItemIds WITH SECURITY_ENFORCED
        ];
    }

    /**
     * Retrieves AppliedSpecialTerms for the specified quote and resipList
     * this data will be used on Approval email
     * @param quoteId The ID of the quote.
     * @param resipList The list of resips to filter by.
     * @return A list of AppliedSpecialTerms.
     */
    public List<AppliedSpecialTerm__c> getAppliedSpecialTerms(Id quoteId, List<String> resipList) {
        String value = '(\'' + String.join(resipList, '\',\'') + '\')';
        return Database.queryWithBinds(
            'SELECT Id, Title__c, SubType__c, TermText__c, Custom__c, Quote__r.Name, ParentTerm__c, ParentTerm__r.RecordType.Name, '+
            'StrippedHtmlTermText__c,RedlinedTermText__c FROM AppliedSpecialTerm__c WHERE Quote__c = :quoteId AND '+
            '(ParentTerm__r.RecordType.Name = \'QST\' OR ParentTerm__r.RecordType.Name = \'PST\' ) '+
            'AND OmitFromQuote__c = false AND (RestrictedAppliedTermApprovals__c  INCLUDES ' +
                value +
                ' OR (Custom__c = true AND CustomRoutingApprovals__c INCLUDES ' +
                value +
                '))',
            new Map<String, Object>{ 'quoteId' => quoteId, 'resipList' => resipList },
            SecurityCheck.getAccessLevel()
        );
    }

    /**
     * Get AppliedSpecialTerm__c records by their associated quoteId.
     * @param quoteIds List of Quote__c Ids.
     * @return List of AppliedSpecialTerm__c records.
     */
    public List<AppliedSpecialTerm__c> selectAppliedTermsByQuote(List<Id> quoteIds){
        return [SELECT Id, PreviousTermText__c,TermText__c FROM AppliedSpecialTerm__c WHERE Quote__c IN: quoteIds 
            WITH SECURITY_ENFORCED];
    }

    public List<TermText__c> getTermWithExternalIds(list<String> externalIds, set<String> billingLanguages){
        return Database.queryWithBinds(
                'select Id,Text__c,HelpText__c ,Language__c,Term__r.ExternalId__c,Term__c,Term__r.CustomRoutingApprovals__c,Term__r.Editable__c,Term__r.Persistent__c,Term__r.RestrictedAppliedTermApprovals__c '+
                        'from TermText__c where Term__r.ExternalId__c IN :externalIds AND Language__c IN :billingLanguages AND Status__c = :activeStatus',
                new Map<String,Object>{'externalIds' => externalIds, 'billingLanguages' => billingLanguages, 'activeStatus' => QuoteTermBaseConstants.STATUS_ACTIVE},
                accessLevelMode
        );
    }
}
