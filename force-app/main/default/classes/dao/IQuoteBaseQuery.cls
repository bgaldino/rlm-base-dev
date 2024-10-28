public interface IQuoteBaseQuery {
    List<Account> getAccountsByIds(Set<String> accIds);
    List<Contact> getContactsByIds(List<String> contactIds);
    List<QuoteLineItem> getQuoteLinesWithTenant(String quoteId, String fp);
    List<User> searchUsersByName(String searchText);
    Group getGroupById(String groupId);
    List<GroupMember> getGroupMemberByGroupId(String groupId);
    List<User> getUsersById(List<String> userIds);
    List<Quote> getQuote(Set<Id> quoteIdSet);
    Application_Configuration__mdt getApplicationConfiguration(String appConfigLabel);
    List<Application_Configuration__mdt> getApplicationConfigurationsByCategoriesAndFunctionalAreas(List<String> appConfigCategories, List<String> appConfigFunctionalAreas);
    StaticResource getStaticResourceByName(String staticResourceName);
    String getRevenueOwnerByCountry(String countryName);
    List<ContractItemPrice> getContractItemPriceByQuote(String quoteId);
    List<ContractItemPrice> getContractItemPriceByIds(Set<Id> cipIdSet);
    List<Product2> getProduct2ByIds(Set<Id> productIdSet);
    OrgWideEmailAddress getOrgWideEmailAddress();
    Contract getContractRecord(String contractId);
    List<QuoteLineItem> getQuoteLinesWithCompleteTenant(String quoteId);
    List<Tenant__c> getTenantByIds(Set<Id> tenantIds);
    List<EmailServicesAddress> getEmailServiceAddress(String functionName );
    List<QuoteLineItem> getQliByQuote(String quoteId);
}
