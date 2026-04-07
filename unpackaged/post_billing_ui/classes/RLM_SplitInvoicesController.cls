/**
 * Returns split Invoices by CorrelationIdentifier with related Account, Billing Arrangement, and Billing Profile names.
 * Invoice API names: CorrelationIdentifier, BillingArrangement (lookup), BillingProfileId (lookup).
 */
public with sharing class RLM_SplitInvoicesController {
    private static final String INVOICE_OBJECT = 'Invoice';
    private static final String CORRELATION_FIELD = 'CorrelationIdentifier';
    private static final String BILLING_ARRANGEMENT_LOOKUP = 'BillingArrangement';
    private static final String BILLING_ARRANGEMENT_REL = 'BillingArrangement';
    private static final String BILLING_PROFILE_LOOKUP = 'BillingProfileId';
    private static final String BILLING_PROFILE_REL = 'BillingProfile';
    private static final String BILLING_ARRANGEMENT_VERSION_FIELD = 'BillingArrangementVerNumber';

    /**
     * Returns Billing Arrangement name and version number for the main invoice (used above the split-invoice cards).
     * Tries BillingArrangementId + BillingArrangement.Name first (common lookup name), then fallbacks.
     */
    @AuraEnabled(cacheable=true)
    public static CurrentInvoiceBillingInfo getCurrentInvoiceBillingInfo(String invoiceId) {
        CurrentInvoiceBillingInfo info = new CurrentInvoiceBillingInfo();
        if (String.isBlank(invoiceId)) return info;
        String[] queries = new String[] {
            'SELECT Id, BillingArrangementId, BillingArrangement.Name, BillingArrangementVerNumber FROM Invoice WHERE Id = :invoiceId LIMIT 1',
            'SELECT Id, BillingArrangementId, BillingArrangement.Name FROM Invoice WHERE Id = :invoiceId LIMIT 1',
            'SELECT Id, BillingArrangement, BillingArrangement.Name, BillingArrangementVerNumber FROM Invoice WHERE Id = :invoiceId LIMIT 1',
            'SELECT Id, BillingArrangement, BillingArrangement.Name FROM Invoice WHERE Id = :invoiceId LIMIT 1'
        };
        for (Integer i = 0; i < queries.size(); i++) {
            try {
                List<SObject> listInv = Database.query(queries[i]);
                if (listInv.isEmpty()) continue;
                SObject inv = listInv[0];
                try { SObject arr = inv.getSObject('BillingArrangement'); if (arr != null) info.billingArrangementName = (String) arr.get('Name'); } catch (Exception e2) { }
                if (i == 0 || i == 2) { try { Object ver = inv.get('BillingArrangementVerNumber'); if (ver != null) info.billingArrangementVerNumber = String.valueOf(ver); } catch (Exception e3) { } }
                break;
            } catch (Exception e) { continue; }
        }
        return info;
    }

    public class CurrentInvoiceBillingInfo {
        @AuraEnabled public String billingArrangementName;
        @AuraEnabled public String billingArrangementVerNumber;
    }

    @AuraEnabled(cacheable=true)
    public static List<InvoiceRow> getInvoicesByCorrelation(String correlationId) {
        if (String.isBlank(correlationId)) {
            return new List<InvoiceRow>();
        }
        List<InvoiceRow> rows = new List<InvoiceRow>();
        String soql = 'SELECT Id, DocumentNumber, InvoiceDate, Balance, Status, '
            + CORRELATION_FIELD + ', '
            + 'BillingAccountId, BillingAccount.Name, '
            + BILLING_ARRANGEMENT_LOOKUP + ', ' + BILLING_ARRANGEMENT_REL + '.Name, '
            + BILLING_PROFILE_LOOKUP + ', ' + BILLING_PROFILE_REL + '.Name, '
            + BILLING_ARRANGEMENT_VERSION_FIELD + ' '
            + 'FROM ' + INVOICE_OBJECT + ' '
            + 'WHERE ' + CORRELATION_FIELD + ' = :correlationId '
            + 'ORDER BY DocumentNumber ASC LIMIT 500';
        try {
            List<SObject> invoices = Database.query(soql);
            for (SObject inv : invoices) {
                rows.add(new InvoiceRow(inv));
            }
        } catch (QueryException e) {
            System.debug(LoggingLevel.ERROR, 'RLM_SplitInvoicesController SOQL failed: '
                + e.getTypeName() + ': ' + e.getMessage()
                + ' | SOQL: ' + soql.replace(':correlationId', '\'' + correlationId + '\''));
            throw new AuraHandledException('Unable to load split invoices. Contact your administrator.');
        } catch (Exception e) {
            System.debug(LoggingLevel.ERROR, 'RLM_SplitInvoicesController error: ' + e.getTypeName() + ': ' + e.getMessage());
            throw new AuraHandledException('Unable to load split invoices. Contact your administrator.');
        }
        return rows;
    }

    /**
     * Resolves record names for Account, Billing Arrangement, Billing Profile, and Contact by ID.
     * Used when GraphQL provides only IDs; LWC calls this and merges names into rows.
     */
    @AuraEnabled(cacheable=false)
    public static RelatedNamesResult getRelatedNames(List<String> accountIds, List<String> arrangementIds, List<String> profileIds, List<String> contactIds) {
        RelatedNamesResult result = new RelatedNamesResult();
        result.accountNames = namesByIds(accountIds);
        result.arrangementNames = namesByIds(arrangementIds);
        result.profileNames = namesByIds(profileIds);
        result.contactNames = namesByIds(contactIds != null ? contactIds : new List<String>());
        return result;
    }

    private static Map<String, String> namesByIds(List<String> idList) {
        Map<String, String> idToName = new Map<String, String>();
        if (idList == null || idList.isEmpty()) return idToName;
        List<Id> ids = new List<Id>();
        for (String s : idList) {
            if (String.isNotBlank(s)) ids.add(Id.valueOf(s));
        }
        if (ids.isEmpty()) return idToName;
        try {
            Schema.SObjectType token = ids[0].getSObjectType();
            String objName = token.getDescribe().getName();
            String soql = 'SELECT Id, Name FROM ' + objName + ' WHERE Id IN :ids';
            for (SObject row : Database.query(soql)) {
                idToName.put(String.valueOf(row.get('Id')), (String) row.get('Name'));
            }
        } catch (Exception e) {
            // Return empty map so other object types can still resolve (e.g. Account)
            return idToName;
        }
        return idToName;
    }

    public class RelatedNamesResult {
        @AuraEnabled public Map<String, String> accountNames = new Map<String, String>();
        @AuraEnabled public Map<String, String> arrangementNames = new Map<String, String>();
        @AuraEnabled public Map<String, String> profileNames = new Map<String, String>();
        @AuraEnabled public Map<String, String> contactNames = new Map<String, String>();
    }

    public class InvoiceRow {
        @AuraEnabled public String Id;
        @AuraEnabled public String DocumentNumber;
        @AuraEnabled public Date InvoiceDate;
        @AuraEnabled public Decimal Balance;
        @AuraEnabled public String Status;
        @AuraEnabled public String billingAccountId;
        @AuraEnabled public String billingAccountName;
        @AuraEnabled public String billingArrangementId;
        @AuraEnabled public String billingArrangementName;
        @AuraEnabled public String billingProfileId;
        @AuraEnabled public String billingProfileName;
        @AuraEnabled public String billingArrangementVerNumber;

        public InvoiceRow(SObject inv) {
            this.Id = (String) inv.get('Id');
            this.DocumentNumber = (String) inv.get('DocumentNumber');
            this.InvoiceDate = (Date) inv.get('InvoiceDate');
            this.Balance = (Decimal) inv.get('Balance');
            this.Status = (String) inv.get('Status');
            Object baId = inv.get('BillingAccountId');
            this.billingAccountId = baId != null ? String.valueOf(baId) : null;
            SObject ba = inv.getSObject('BillingAccount');
            this.billingAccountName = ba != null ? (String) ba.get('Name') : null;
            Object arrId = inv.get(BILLING_ARRANGEMENT_LOOKUP);
            this.billingArrangementId = arrId != null ? String.valueOf(arrId) : null;
            SObject arr = inv.getSObject(BILLING_ARRANGEMENT_REL);
            this.billingArrangementName = arr != null ? (String) arr.get('Name') : null;
            Object profId = inv.get(BILLING_PROFILE_LOOKUP);
            this.billingProfileId = profId != null ? String.valueOf(profId) : null;
            SObject prof = inv.getSObject(BILLING_PROFILE_REL);
            this.billingProfileName = prof != null ? (String) prof.get('Name') : null;
            Object ver = inv.get(BILLING_ARRANGEMENT_VERSION_FIELD);
            this.billingArrangementVerNumber = ver != null ? String.valueOf(ver) : null;
        }
    }
}