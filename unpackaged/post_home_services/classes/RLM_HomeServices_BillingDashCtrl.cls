public with sharing class RLM_HomeServices_BillingDashCtrl {

    /**
     * Returns the most recently created BillingScheduleGroup for the given Account.
     * Accounts in this demo have exactly one BSG; LIMIT 1 guards against edge cases.
     */
    @AuraEnabled(cacheable=true)
    public static BillingScheduleGroup getBillingScheduleGroup(Id accountId) {
        List<BillingScheduleGroup> bsgs = [
            SELECT Id
            FROM BillingScheduleGroup
            WHERE BillingAccountId = :accountId
            ORDER BY CreatedDate DESC
            LIMIT 1
        ];
        return bsgs.isEmpty() ? null : bsgs[0];
    }

    /**
     * Returns every BillingScheduleGroup for the given Account (with product name),
     * so the dashboard can render a timeline per plan.
     */
    @AuraEnabled(cacheable=true)
    public static List<BillingScheduleGroup> getBillingScheduleGroups(Id accountId) {
        return [
            SELECT Id, ProductName
            FROM BillingScheduleGroup
            WHERE BillingAccountId = :accountId
            ORDER BY ProductName
        ];
    }

    /**
     * Returns all BillingMilestonePlanItems across every BillingScheduleGroup
     * belonging to the given Account, including the owning plan's product name.
     * Sorting is left to the client for proper numeric ordering (1, 2 … 12).
     */
    @AuraEnabled(cacheable=true)
    public static List<BillingMilestonePlanItem> getMilestonePlanItems(Id accountId) {
        return [
            SELECT Id, Name, MilestoneType, Status, MilestoneAmount,
                   BillingScheduleGroup.ProductName
            FROM BillingMilestonePlanItem
            WHERE BillingScheduleGroup.BillingAccountId = :accountId
        ];
    }

    /**
     * Returns invoices related to the given Account, most recent first.
     */
    @AuraEnabled(cacheable=true)
    public static List<Invoice> getInvoices(Id accountId) {
        return [
            SELECT Id, InvoiceNumber, DocumentNumber, Status, InvoiceDate, DueDate,
                   TotalAmountWithTax, Balance, Description
            FROM Invoice
            WHERE BillingAccountId = :accountId
            ORDER BY InvoiceDate DESC
            LIMIT 50
        ];
    }

    /**
     * Returns saved payment methods related to the given Account.
     * SavedPaymentMethod uses ReferenceOwnerId (polymorphic) to link to Account or Contact.
     */
    @AuraEnabled(cacheable=true)
    public static List<SavedPaymentMethod> getSavedPaymentMethods(Id accountId) {
        return [
            SELECT Id, Name, Type, Status, IsDefault, ExpiryMonth, ExpiryYear
            FROM SavedPaymentMethod
            WHERE ReferenceOwnerId = :accountId
        ];
    }
}