public with sharing class QuoteBaseQuery implements IQuoteBaseQuery {
    /************************************************
     * Setup class instance
     ************************************************/
    private static IQuoteBaseQuery instance = null;
    private static AccessLevel accessLevelMode = UserInfo.getUserType() == 'automatedprocess'? AccessLevel.SYSTEM_MODE: AccessLevel.USER_MODE;
    public static IQuoteBaseQuery getInstance() {
        if (instance == null) {
            instance = new QuoteBaseQuery();
        }
        return instance;
    }
    /** @description: Make class mockable for unit tests */
    public static void setInstance(IQuoteBaseQuery existingInstance) {
        instance = existingInstance;
    }
    public QuoteBaseQuery() {
        if(Test.isRunningTest()) {
            accessLevelMode = AccessLevel.SYSTEM_MODE;
        }
    }
    public Quote getQuoteForConsumptionRate(String quoteId) {
        String quoteQuery =  'SELECT Id, Status, ApprovalStatus__c, ApprovalComments__c, BeginningQuoteAOV__c, Opportunity.AccountId, ContractId' +
            ', HasProductRuleErrors__c, Opportunity.SyncedQuoteId, TermUpdatesRequired__c, OwnerId' +
            ', ServiceStartDate__c, ServiceEndDate__c, CurrencyIsoCode, Pricebook2Id, QuoteBypass__c, Term__c, QuoteType__c, OriginalActionType'+
            ', L1Approver__c, L2Approver__c, L3Approver__c, L4Approver__c'+
            ' FROM Quote WHERE Id =: quoteId';
        List<Quote> quotes = Database.queryWithBinds(quoteQuery,
                                                    new Map<String,Object>{'quoteId' => quoteId},
                                                    accessLevelMode);
        return quotes.size() > 0 ? quotes[0] : null;
    }
    /************************************************
     * Public methods
     * reference IQuoteBaseQuery
     *  Database.queryWithBinds(qry, bindParams, AccessLevel.USER_MODE);
     ************************************************/
    public Quote getQuoteForPreviewApprovals(String quoteId) {
        List<Quote> quotes = Database.queryWithBinds(
            'SELECT Id, Status, ApprovalStatus__c, ApprovalComments__c, BeginningQuoteAOV__c, Opportunity.AccountId' +
            ', HasProductRuleErrors__c, Opportunity.SyncedQuoteId, TermUpdatesRequired__c, OwnerId, BillingCountry' +
            ', ServiceStartDate__c, ServiceEndDate__c, CurrencyIsoCode, Pricebook2Id, QuoteBypass__c, Term__c, BusinessType__c, BillingFrequency__c, BillingFrequencySpecialTerm__c'+
            ', L1Approver__c, L2Approver__c, L3Approver__c, L4Approver__c, ValidationResult'+
            ' FROM Quote WHERE Id =: quoteId',
            new Map<String,Object>{'quoteId' => quoteId},
            accessLevelMode);
        return quotes.size() > 0 ? quotes[0] : null;
    }


    public List<Account> getAccountsByIds(Set<String> accIds) {
        // Using AccessLevel System since AEs do not need additional Credit field accesses on Account
        return Database.queryWithBinds(
            'SELECT Id, Credit_Score__c, Credit_Decision__c, Org62_Account_Id__c FROM Account WHERE Id IN :accIds',
            new Map<String,Object>{'accIds' => accIds},
            AccessLevel.SYSTEM_MODE
        );
    }
    
     public OrgWideEmailAddress getOrgWideEmailAddress() {       
        return [Select Id FROM OrgWideEmailAddress WHERE DisplayName = 'NoReply'];
    }
    
    public List<EmailServicesAddress> getEmailServiceAddress(String functionName) {        
       // Query to get the associated Email Service Address record
        return [SELECT Id, LocalPart, EmailDomainName,function.functionName FROM EmailServicesAddress 
                                                    WHERE function.FunctionName = :functionName
                                                    LIMIT 1];
    }

    public List<SBAA__Approval__c> getApprovalsByQuoteIds(Set<Id> quoteIds) {
        return Database.queryWithBinds(
            'SELECT Id, Name, Quote__c, SBAA__CommentsLong__c, SBAA__Approver__c, SBAA__Approver__r.Name, SBAA__Approver__r.sbaa__User__c,SubmitterComment__c' +
            ', SBAA__DelegatedApprover__c, SBAA__DelegatedApprover__r.Name, SBAA__AssignedTo__c, SBAA__AssignedTo__r.Name' +
            ', sbaa__AssignedGroupId__c, SBAA__ApprovalChain__c, SBAA__ApprovalChain__r.Name, SBAA__Rule__c' +
            ', SBAA__Rule__r.Name, SBAA__ApprovedBy__r.Name, SBAA__ApprovedBy__r.Email, SBAA__RejectedBy__r.Name' +
            ', SBAA__RejectedBy__r.Email, SBAA__Status__c, SBAA__ApprovalStep__c, CreatedDate, LastModifiedDate' +
            ' FROM SBAA__Approval__c' +
            ' WHERE Quote__c IN :quoteIds AND SBAA__Archived__c = false AND SBAA__Status__c !=\'Recalled\'' +
            ' ORDER BY SBAA__ApprovalStep__c, Id',
            new Map<String,Object>{'quoteIds' => quoteIds},
            accessLevelMode);
    }

    public List<SBAA__ApprovalRule__c> getApprovalRules(Set<Id> ruleIds) {
        return Database.queryWithBinds(
            'SELECT Id, Name FROM SBAA__ApprovalRule__c WHERE Id IN :ruleIds',
            new Map<String,Object>{'ruleIds' => ruleIds},
            accessLevelMode
        );
    }

    public List<SBAA__Approver__c> getApprovers(Set<Id> approverIds) {
        return Database.queryWithBinds(
            'SELECT Id, Name FROM SBAA__Approver__c WHERE Id IN :approverIds',
            new Map<String,Object>{'approverIds' => approverIds},
            accessLevelMode
        );
    }

    public Quote getOmniscriptTransientData(String quoteId) {
        List<Quote> quotes = Database.queryWithBinds(
            'SELECT Id, OmniscriptTransientData__c,ServiceStartDate__c,ServiceEndDate__c,' +
            ' Term__c,BillingCountry, TotalPrice, TrueUpSchedule__c,ContractId FROM Quote WHERE Id =: quoteId',
            new Map<String,Object>{'quoteId' => quoteId},
            accessLevelMode
        );
        return quotes.size() > 0 ? quotes[0] : null;
    }
    
    public Contract getContractRecord(String contractId) {
        List<Contract> contracts = Database.queryWithBinds(
            'SELECT Id,StartDate  FROM Contract WHERE Id =: contractId',
            new Map<String,Object>{'contractId' => contractId},
            accessLevelMode
        );
        return contracts.size() > 0 ? contracts[0] : null;
    }

    public List<Rate_Card_Entry__c> getRateCardEntryByQuote(String quoteId) {
        List<Rate_Card_Entry__c> rateCardRecords = Database.queryWithBinds(
            'SELECT Id, CurrencyIsoCode, Name, Usage_Model__c, Quantity__c, Rate__c, Tenant__c, Usage_Product__c, Tenant__r.External_Id__c, Tenant__r.Fulfillment_Provider_Name__c FROM Rate_Card_Entry__c WHERE Quote__c =:quoteId',
            new Map<String,Object>{'quoteId' => quoteId},
            accessLevelMode
        );
        return rateCardRecords.size() > 0 ? rateCardRecords : null;
    }
    
    public List<ContractItemPrice> getContractItemPriceByQuote(String quoteId) {
        List<ContractItemPrice> cipList = Database.queryWithBinds(
            'SELECT ItemId, Price FROM ContractItemPrice WHERE SourceQuote__c=:quoteId AND Status__c = \'Draft\'',
            new Map<String,Object>{'quoteId' => quoteId},
            accessLevelMode
        );
        return cipList.size() > 0 ? cipList : null;
    }

    public List<TempContractItemPrice__c> getTempContractItemPriceByQuote(String quoteId) {
        List<TempContractItemPrice__c> tempCipList = Database.queryWithBinds(
            'SELECT OriginalCIP__c, Price__c FROM TempContractItemPrice__c WHERE SourceQuote__c=:quoteId AND Status__c = \'Draft\'',
            new Map<String,Object>{'quoteId' => quoteId},
            accessLevelMode
        );
        return tempCipList.size() > 0 ? tempCipList : null;
    }

    public List<ContractItemPrice> getContractItemPriceByIds(Set<Id> cipIdSet) {
        List<ContractItemPrice> cipList = Database.queryWithBinds(
            'SELECT Id, ItemId, Price FROM ContractItemPrice WHERE Id IN :cipIdSet',
            new Map<String,Object>{'cipIdSet' => cipIdSet},
            accessLevelMode
        );
        return cipList.size() > 0 ? cipList : null;
    }
    
    public List<Product2> getProduct2ByIds(Set<Id> productIdSet) {
        List<Product2> productList = Database.queryWithBinds(
            'SELECT Id, Name FROM Product2 WHERE Id IN :productIdSet',
            new Map<String,Object>{'productIdSet' => productIdSet},
            accessLevelMode
        );
        return productList.size() > 0 ? productList : null;
    }
    
    public LegalEntity getLegalEntitiesByRevenueOwner(String revenueOwner) {
        List<LegalEntity> legalEntities = Database.queryWithBinds(
            'SELECT Id, RevenueOwner__c, CounterSignatoryName__c, CounterSignatoryRole__c, CounterSignatoryDistributionListEmail__c, Name, Street1__c, Street2__c, State__c, PostalCode__c, City__c, Country__c, AddressFormat__c, CounterSignatoryImage__c FROM LegalEntity WHERE RevenueOwner__c = :revenueOwner',
            new Map<String,Object>{'revenueOwner' => revenueOwner},
            accessLevelMode
        );
        return legalEntities.size() > 0 ? legalEntities[0] : null;
    }

    public StaticResource getStaticResourceByName(String staticResourceName) {
        List<StaticResource> resources = Database.queryWithBinds(
            'SELECT Id FROM StaticResource WHERE Name = :staticResourceName LIMIT 1',
            new Map<String,Object>{'staticResourceName' => staticResourceName},
            accessLevelMode
        );
        return resources.size() > 0 ? resources[0] : null;
    }
    
    public String getRevenueOwnerByCountry(String countryName) {
        RevenueOwnerService ro = new RevenueOwnerService ();
        return ro.getRevenueOwner(countryName);
    }

    public List<Contact> getContactsByIds(List<String> contactIds) {
        return Database.queryWithBinds(
            'SELECT Id, Name, Title FROM Contact WHERE Id IN :contactIds',
            new Map<String,Object>{'contactIds' => contactIds},
            accessLevelMode
        );
    }
    
    public List<QuoteLineItem> getQuoteLinesWithTenant(String quoteId, String fp) {
        return Database.queryWithBinds(
            'select Id,Tenant__c,Product2.name,tenant__r.External_Id__c,tenant__r.Tenant_Information_Parameters__c,Quantity,Tenant__r.Fulfillment_Provider_Name__c '+
            'from QuoteLineItem where QuoteId=:quoteId and Tenant__r.Fulfillment_Provider_Name__c=: fp',
            new Map<String,Object>{'quoteId' => quoteId, 'fp' => fp},
            accessLevelMode
        );
    }
    
    public List<QuoteLineItem> getQuoteLinesWithCompleteTenant(String quoteId) {
        List<QuoteLineItem> qliList = Database.queryWithBinds(
            'SELECT Id,Tenant__c FROM QuoteLineItem WHERE QuoteId =:quoteId and Tenant__r.Quoting_Status__c =\'Complete\'',
            new Map<String,Object>{'quoteId' => quoteId},
            accessLevelMode
        );
        return qliList.size() > 0 ? qliList : null;
    }
    
    public List<Tenant__c> getTenantByIds(Set<Id> tenantIds) {
        List<Tenant__c> tenantList = Database.queryWithBinds(
            'SELECT Id,Fulfillment_Provider_Name__c,UI_Tenant_Parameters__c, External_Id__c,OptionalName__c FROM Tenant__c WHERE Id =:tenantIds',
            new Map<String,Object>{'tenantIds' => tenantIds},
            accessLevelMode
        );
        return tenantList.size() > 0 ? tenantList : null;
    }
    
    public List<DPPBreakup__c> getDPPBreakupByQuote(String quoteId) {
        List<DPPBreakup__c> dppList = Database.queryWithBinds(
            'SELECT Id,MonthlyNetUnitPrice__c,DPPQuoteLine__r.StartDate,DPPQuoteLine__r.EndDate,DerivedProduct__c,DerivedProduct__r.Name,DerivedProduct__r.Sku__c,DPPQuoteLine__r.Tenant__c,DPPQuoteLine__r.Tenant__r.OptionalName__c,DPPQuoteLine__r.Tenant__r.External_Id__c,DPPQuoteLine__r.Tenant__r.Fulfillment_Provider_Name__c,Quantity__c,ContributingQuoteLineItem__r.Quantity,ContributingQuoteLineItem__r.Product2.Name,ContributingAsset__r.Quantity,ContributingAsset__r.Product2.Name,ContributingAsset__c FROM DPPBreakup__c WHERE Quote__c =:quoteId',
            new Map<String,Object>{'quoteId' => quoteId},
            accessLevelMode
        );
        return dppList.size() > 0 ? dppList : null;
    }
    
    public List<TenantAssociationData__c> getTadRecordsByQuote(String quoteId) {
        List<TenantAssociationData__c> tadList = Database.queryWithBinds(
            'SELECT Tenant__c,TeamEncodedId__c,ActionType__c,TeamSubdomain__c,ParentTenantCSPId__c, DataResidencyRegion__c FROM TenantAssociationData__c WHERE Quote__c = :quoteId',
             new Map<String,Object>{'quoteId' => quoteId},
             accessLevelMode
        );
        return tadList.size() > 0 ? tadList : null;
    }
    
    public List<TenantAssociationData__c> getTadRecordsByQuoteAndTenant(String quoteId, Set<Id> tenantIds) {
        List<TenantAssociationData__c> tadList = Database.queryWithBinds(
            'SELECT Tenant__c,TeamEncodedId__c,ActionType__c,TeamSubdomain__c,ParentTenantCSPId__c, DataResidencyRegion__c FROM TenantAssociationData__c WHERE Quote__c = :quoteId AND Tenant__c IN :tenantIds',
             new Map<String,Object>{'quoteId' => quoteId,'tenantIds' => tenantIds},
             accessLevelMode
        );
        return tadList.size() > 0 ? tadList : null;
    }
    
    public List<QuoteLineItem> getQliByQuote(String quoteId) {
        List<QuoteLineItem> qliList = Database.queryWithBinds(
            'SELECT Product2Id,Tenant__c, QuoteId FROM QuoteLineItem WHERE QuoteId = :quoteId',
             new Map<String,Object>{'quoteId' => quoteId},
             accessLevelMode
        );
        return qliList.size() > 0 ? qliList : null;
    }

    public Application_Configuration__mdt getApplicationConfiguration(String appConfigLabel) {
        List<Application_Configuration__mdt> appConfigs = Database.queryWithBinds(
            'SELECT Label, Value__c FROM Application_Configuration__mdt WHERE Label =: appConfigLabel',
            new Map<String,Object>{'appConfigLabel' => appConfigLabel},
            accessLevelMode);
        return appConfigs.size() > 0 ? appConfigs[0] : null;
    }

    public List<Application_Configuration__mdt> getApplicationConfigurationsByCategoriesAndFunctionalAreas(List<String> appConfigCategories, List<String> appConfigFunctionalAreas){
        List<Application_Configuration__mdt> appConfigs = Database.queryWithBinds(
            'SELECT Label, Value__c FROM Application_Configuration__mdt WHERE Category__c IN: appConfigCategories AND Functional_Area__c IN: appConfigFunctionalAreas',
            new Map<String,Object>{'appConfigCategories' => appConfigCategories, 'appConfigFunctionalAreas' => appConfigFunctionalAreas},
            accessLevelMode);
        return appConfigs.size() > 0 ? appConfigs : null;
    }

    public SBAA__Approver__c getApproverById(String approverId) {
        List<SBAA__Approver__c> approvers = Database.queryWithBinds(
            'SELECT Id, Name, sbaa__User__c, sbaa__User__r.Name, sbaa__GroupId__c, OwnerId, sbaa__DelegatedUserId__c' +
            ', IsBackupGroup__c, BackupGroup__c, IsBackupGroupOwner__c,BackupGroupOwner__c, BackupGroupOwner__r.sbaa__User__c' +
            ', sbaa__User__r.ProfileId, BackupGroupOwner__r.sbaa__User__r.ProfileId' +
            ' FROM SBAA__Approver__c WHERE Id =: approverId',
            new Map<String,Object>{'approverId' => approverId},
            accessLevelMode
        );
        return approvers.size() > 0 ? approvers[0] : null;
    }

    public SBAA__Approver__c getBackupOwnerApproverByName(String approverName) {
        List<SBAA__Approver__c> approvers = Database.queryWithBinds(
            'SELECT Id, Name FROM SBAA__Approver__c WHERE Name =: approverName',
            new Map<String,Object>{'approverName' => approverName},
            accessLevelMode
        );
        return approvers.size() > 0 ? approvers[0] : null;
    }

    public List<SBAA__Approver__c> searchApproversByName(String searchText) {
        return Database.queryWithBinds(
            'SELECT Id, Name, SBAA__User__c, SBAA__User__r.Name, SBAA__User__r.Email, ' +
            'SBAA__User__r.Profile.Name, SBAA__User__r.UserRole.Name ' +
            'FROM SBAA__Approver__c WHERE SBAA__User__r.Name LIKE :searchText LIMIT 100',
            new Map<String, Object>{'searchText' => '%' + searchText + '%'},
            accessLevelMode
        );
    }

    public List<SBAA__Approver__c> searchUserApproversByName(String searchText) {
        return Database.queryWithBinds(
            'SELECT Id, Name, SBAA__User__c, SBAA__User__r.Name, SBAA__User__r.Email, ' +
            'SBAA__User__r.ProfileId, SBAA__User__r.Profile.Name, SBAA__User__r.UserRole.Name ' +
            'FROM SBAA__Approver__c WHERE SBAA__User__c != NULL AND SBAA__User__r.Name LIKE :searchText LIMIT 100',
            new Map<String, Object>{'searchText' => '%' + searchText + '%'},
            accessLevelMode
        );
    }

    public List<User> searchUsersByName(String searchText) {
        return Database.queryWithBinds(
            'SELECT Id, Name, Email, UserRole.Name, Profile.Name FROM User WHERE IsActive=TRUE AND Name LIKE :searchText LIMIT 100',
            new Map<String,Object>{'searchText' => '%' + searchText + '%'},
            accessLevelMode
        );
    }

    public Group getGroupById(String groupId) {
        List<Group> groups = Database.queryWithBinds(
            'SELECT Id, Name FROM Group WHERE id =: groupId',
            new Map<String,Object>{'groupId' => groupId},
            accessLevelMode
        );
        return groups.size() > 0 ? groups[0] : null;
    }

    public List<GroupMember> getGroupMemberByGroupId(String groupId) {
        return Database.queryWithBinds(
            'SELECT Id, GroupId, UserOrGroupId FROM GroupMember WHERE GroupId =: groupId',
            new Map<String,Object>{'groupId' => groupId},
            accessLevelMode
        );
    }

    public List<User> getUsersById(List<String> userIds) {
        return Database.queryWithBinds(
            'SELECT Id, Name, Email, Profile.Name, UserRole.Name FROM User WHERE Id IN :userIds',
            new Map<String,Object>{'userIds' => userIds},
            accessLevelMode
        );
    }

    public List<Quote> getQuote(Set<Id> quoteIdSet) {
        return Database.queryWithBinds(
            'select Id,TermUpdateForBannerNotification__c,OwnerId,TermUpdatesRequired__c,BillingLanguage__c, Opportunity.AccountId '+
            'from Quote where Id IN :quoteIdSet',
            new Map<String,Object>{'quoteIdSet' => quoteIdSet},
            accessLevelMode
        );
    }

    public SBAA__Approval__c getApprovalByIdForNotification(String approvalId) {
        List<SBAA__Approval__c> approvals = Database.queryWithBinds(
            'SELECT Id, Quote__r.OwnerId, Quote__r.SubmittedUser__c, sbaa__Approver__r.IsBackupGroupOwner__c, sbaa__Approver__r.sbaa__User__r.Id' +
            ', sbaa__Approver__r.sbaa__GroupId__c, sbaa__Approver__r.BackupGroup__c, sbaa__Approver__r.BackupGroupOwner__c, sbaa__Approver__r.IsBackupGroup__c' +
            ', sbaa__AssignedTo__r.Id, sbaa__AssignedTo__r.Name, sbaa__Rule__c, sbaa__Status__c' +
            ' FROM SBAA__Approval__c WHERE Id =: approvalId',
            new Map<String,Object>{'approvalId' => approvalId},
            accessLevelMode);
        return approvals.size() > 0 ? approvals[0] : null;
    }
    
    public List<Quote> getQuoteWithAppliedTerms(set<Id>quoteIds){
        return [
                SELECT
                        Id,Term__c,BillingFrequency__c,PaymentMethod__c,TermApprovers__c,
                        PaymentTerm__c,ApprovalLevel__c,InvoiceAmount__c,TermUpdatesRequired__c,Renewal_Cap__c,
                         (SELECT Id,Custom__c,CustomRoutingApprovals__c,SourceTermTextStatus__c,SourceContractTerm__c 
                          FROM AppliedSpecialTerms__r)
                        FROM Quote WHERE Id IN: quoteIds WITH SECURITY_ENFORCED];
    }

    public List<Quote> getQuoteAndRelatedData(Id quoteID){
        return [
                SELECT Id, OwnerId, Owner.Email, Owner.Name, Account.name,InvoiceAmount__c,ServiceEndDate__c,ServiceStartDate__c,Name,ApprovalStatus__c,opportunityId,QuoteType__c,Term__c,PaymentTerm__c,
                        AutoRenewal__c,opportunity.Amount,opportunity.CloseDate,Account.Owner.UserRole.Name,CurrencyIsoCode ,Opportunity.Name,GrandTotal,lastModifiedDate,createdDate,ApprovalComments__c,
                (SELECT Id, Name, Quote__c, SBAA__CommentsLong__c, SBAA__Approver__c, SBAA__Approver__r.Name,SubmitterComment__c,
                        SBAA__DelegatedApprover__c, SBAA__DelegatedApprover__r.Name, SBAA__AssignedTo__c, SBAA__AssignedTo__r.Name,
                        sbaa__AssignedGroupId__c, SBAA__ApprovalChain__c, SBAA__ApprovalChain__r.Name, SBAA__Rule__c,
                        SBAA__Rule__r.Name, SBAA__ApprovedBy__r.Name, SBAA__ApprovedBy__r.Email, SBAA__RejectedBy__r.Name,
                        SBAA__RejectedBy__r.Email, SBAA__Status__c, SBAA__ApprovalStep__c, CreatedDate, LastModifiedDate,SBAA__AssignedTo__r.Email,SBAA__Approver__r.sbaa__User__r.Email
                FROM Quote__r
                WHERE SBAA__Archived__c = false
                ORDER BY SBAA__ApprovalStep__c, Id),
                (SELECT Id, Quantity,Product2Id,Product2.name,UnitPrice,NetTotalPrice,Discount,EndDate,ApprovalLevel__c,CurrencyIsoCode,totalPrice,QuoteId,ContractualPricing__c,DiscountAmount FROM QuoteLineItems)
                FROM Quote WHERE Id =:quoteID WITH SECURITY_ENFORCED
        ];
    }

    public List<SBAA__Approval__c> getApprovalRequests(set<Id> approvalIds){
        return [SELECT Id, Name, Quote__c, SBAA__CommentsLong__c, SBAA__Approver__c, SBAA__Approver__r.Name,
                SBAA__DelegatedApprover__c, SBAA__DelegatedApprover__r.Name, SBAA__AssignedTo__c, SBAA__AssignedTo__r.Name,
                sbaa__AssignedGroupId__c, SBAA__ApprovalChain__c, SBAA__ApprovalChain__r.Name, SBAA__Rule__c,
                SBAA__Rule__r.Name, SBAA__ApprovedBy__r.Name, SBAA__ApprovedBy__r.Email, SBAA__RejectedBy__r.Name,
                SBAA__RejectedBy__r.Email, SBAA__Status__c, SBAA__ApprovalStep__c, CreatedDate, LastModifiedDate,SBAA__AssignedTo__r.Email,SBAA__Approver__r.sbaa__User__r.Email
        FROM SBAA__Approval__c WHERE Id IN :approvalIds WITH SECURITY_ENFORCED];
    }

    public List<sbaa__Approver__c> getBackUpApproverGroup(Set<Id> backupGroupOwnerIdSet){
        return [SELECT Id,sbaa__GroupId__c
                FROM sbaa__Approver__c WHERE 
                BackupGroupOwner__c IN :backupGroupOwnerIdSet
                WITH SECURITY_ENFORCED];
    }
    
}
