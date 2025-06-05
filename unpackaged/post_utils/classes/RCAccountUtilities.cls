public class RCAccountUtilities {

    @InvocableMethod(label='Reset Account Related Objects.')
    public static void delAccountRelatedObjects(List<InputVariables> request){

        String accountId = request.get(0).accountId;
        Boolean DeleteAssets = request.get(0).DeleteAssets; 
        Boolean DeleteFulfillment = request.get(0).DeleteFulfillment;
        Boolean DeleteBilling = request.get(0).DeleteBilling; 
        
        //deleteUsageEntitlementAccount(accountId);
       deleteOrders(accountId);
       deleteTransactionJournal(accountId);
       deleteBillingScheduleGroups(accountId);
       deleteContracts(accountId);
       deleteAssets(accountId);
       deleteQuotes(accountId);
     deleteOpportunities(accountId);
        
    }
    
    public class InputVariables {  //=====================
        @InvocableVariable
      public String accountId;
        @InvocableVariable
      public Boolean DeleteAssets;
        @InvocableVariable
      public Boolean DeleteFulfillment;
        @InvocableVariable
      public Boolean DeleteBilling;
    }
        

    private static Boolean deleteOpportunities(String accountId) {
        Id a = accountId;
        Opportunity[] opportinitiesToDelete = [SELECT Id FROM Opportunity WHERE AccountId = :a];
        if (!opportinitiesToDelete.isEmpty()) {
            Database.delete(opportinitiesToDelete);
        }
        return true;
    }
     private static Boolean deleteQuotes(String accountId) {
        Id a = AccountId;
        Quote[] quotesToDelete = [SELECT Id FROM Quote WHERE QuoteAccountId  = :a];
        if (!quotesToDelete.isEmpty()) {
            Set<Id> quoteIds = new Set<Id>();
            for (Quote q : quotesToDelete) {
                quoteIds.add(q.Id);
            }
            Database.delete(quotesToDelete);
        }
        return true;
    }
       private static Boolean deleteOrders(String accountId) {
        Id a = AccountId;
        Order[] ordersToDelete = [SELECT Id FROM Order WHERE AccountId = :a];
        if (!ordersToDelete.isEmpty()) {
            Set<Id> orderIds = new Set<Id>();
            for (Order o : ordersToDelete) {
                orderIds.add(o.Id);
                o.Status = 'Draft';
            }
            update ordersToDelete;
            OrderItem[] orderItems = getOrderItems(orderIds);
            if (!orderItems.isEmpty()) {
                deleteTransactionUsageEntitlement(a);
                deleteUsageEntitlementAccount(a);                
        deleteFulfillmentLineSourceRel(orderItems);
                
//                this.deleteRevenueSchedules(orderItems);
//                this.deleteUsages(orderItems);
//                this.deleteUsageSummaries(orderItems);
 //               Database.update(orderItems);
            }
            for (Order o : ordersToDelete) {
                orderIds.add(o.Id);
                o.Status = 'Draft';
//                o.SBQQ__Contracted__c = false;
            }
            Database.update(ordersToDelete);
            Database.delete(ordersToDelete);
        }

        System.debug('Total Number of SOQL Queries after deleteOrders(): ' + Limits.getQueries());

        return true;
    }
    private static List<OrderItem> getOrderItems(Set<Id> orderIds) {
        OrderItem[] orderItems = [SELECT Id FROM OrderItem WHERE OrderId IN :orderIds];
        return orderItems;
    }

    
    // Fulfillment Records *** START **
    private static Boolean deleteFulfillmentLineSourceRel(OrderItem[] orderItems) {
        if (!orderItems.isEmpty()) {
            Set<Id> orderItemIds = new Set<Id>();
            for (OrderItem oi : orderItems) {
                orderItemIds.add(oi.Id);
            }
            FulfillmentLineSourceRel[] fulfillmentLineSourceRelToDelete = [SELECT Id FROM FulfillmentLineSourceRel WHERE SourceLineItemId IN :orderItemIds];
            if (!fulfillmentLineSourceRelToDelete.isEmpty()) {
                Database.delete(fulfillmentLineSourceRelToDelete);
            }  
        }
        return true;
    }

    // Delete Usage Entitlement Buckets
    private static Boolean deleteUsageEntitlementBucket(Set<Id> entitlementIds) {
        System.debug('Delete Entitlement Bucket');
        UsageEntitlementBucket[] usageEntitlementBucketsToDelete = [SELECT Id FROM UsageEntitlementBucket WHERE TransactionUsageEntitlementId IN :entitlementIds];
        if (!usageEntitlementBucketsToDelete.isEmpty()) {
            Database.delete(usageEntitlementBucketsToDelete);
        }

        return true;
    }
    private static Boolean deleteUsageEntitlementBucketParent(Set<Id> entitlementIds) {
        System.debug('Delete Entitlement Bucket');
        UsageEntitlementBucket[] usageEntitlementBucketsToDelete = [SELECT Id FROM UsageEntitlementBucket WHERE ParentId IN :entitlementIds];
        if (!usageEntitlementBucketsToDelete.isEmpty()) {
            Database.delete(usageEntitlementBucketsToDelete);
        }

        return true;
    }
     // Delete TransactionUsageEntitlement
    private static Boolean deleteTransactionUsageEntitlement(String accountId) {
        Id a = AccountId;
        System.debug('JOHN');
        TransactionUsageEntitlement[] TransactionUsageEntitlementToDelete = [SELECT Id FROM TransactionUsageEntitlement WHERE AccountId = :a];
        if (!TransactionUsageEntitlementToDelete.isEmpty()) {
            Set<Id> tueIds = new Set<Id>();
            for (TransactionUsageEntitlement tue : TransactionUsageEntitlementToDelete) {
                tueIds.add(tue.Id);
            }
          deleteUsageEntitlementBucket(tueIds); 
          Database.delete(TransactionUsageEntitlementToDelete);
        }
        return true;
    }
    // Delete UsageEntitlementAccount
    private static Boolean deleteUsageEntitlementAccount(String accountId) {
        Id a = AccountId;
        System.debug('UEA ' + a);
        UsageEntitlementAccount[] UsageEntitlementAccountToDelete = [SELECT Id FROM UsageEntitlementAccount WHERE AccountId = :a];       
        if (!UsageEntitlementAccountToDelete.isEmpty()) {
            Set<Id> ueaIds = new Set<Id>();
            for (UsageEntitlementAccount uea : UsageEntitlementAccountToDelete) {
                ueaIds.add(uea.Id);
            }
            System.debug('UEA Ids ' + ueaIds);
            deleteUsageEntitlementBucketParent(ueaIds); 
            Database.delete(UsageEntitlementAccountToDelete);
        }
        return true;
    }
    // Fulfillment Records ***  END  **
    // Billing Records     *** START **
    // TransactionJournal 
    // 
     private static Boolean deleteTransactionJournal(String accountId) {
     //   Id a = AccountId;
        TransactionJournal [] TransactionJournalToDelete = [SELECT Id FROM TransactionJournal WHERE AccountId = :accountId];
        if (!TransactionJournalToDelete.isEmpty()) {
            Database.delete(TransactionJournalToDelete);
        }
        return true;
    }   
    
    
    private static Boolean deleteBillingScheduleGroups(String accountId) {
     //   Id a = AccountId;
        BillingScheduleGroup [] billingScheduleGroupsToDelete = [SELECT Id FROM BillingScheduleGroup WHERE BillingAccountId = :accountId];
        if (!billingScheduleGroupsToDelete.isEmpty()) {
            Database.delete(billingScheduleGroupsToDelete);
        }
        return true;
    }
    // Billing Records     *** END **
    // Contracts *** START ***
    private static Boolean deleteContracts(String accountId) {
     //   Id a = AccountId;
        Contract [] contractsToDelete = [SELECT Id FROM Contract WHERE AccountId = :accountId];
        if (!contractsToDelete.isEmpty()) {
            Database.delete(contractsToDelete);
        }
        return true;
    }
    // Contracts ** END ***
    // Assets  ** START **
    private static Boolean deleteAssetRelationship(Set<Id> assetIds) {
        AssetRelationship[] assetRelationshipToDelete = [SELECT Id FROM AssetRelationship WHERE AssetId IN :assetIds];
        if (!assetRelationshipToDelete.isEmpty()) {
            Database.delete(assetRelationshipToDelete);
        }

        return true;
    }
    
    private static Boolean deleteAssets(String accountId) {
        Id a = AccountId;
        System.debug('ASS ' + a);
        Asset[] assetsToDelete = [SELECT Id FROM Asset WHERE AccountId = :a];       
        if (!assetsToDelete.isEmpty()) {
            Set<Id> assIds = new Set<Id>();
            for (Asset ass : assetsToDelete) {
                assIds.add(ass.Id);
            }
            System.debug('ASS Ids ' + assIds);
            deleteAssetRelationship(assIds);
            Database.delete(assetsToDelete);
        }
        return true;
    }
    // Assets ** END **
  }