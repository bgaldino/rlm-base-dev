/**
 * Apex controller for the Dispute Details LWC.
 * Provides methods to resolve Invoice/InvoiceLine names and save approved amounts.
 */
public with sharing class RLM_DisputeDetailsController {

    /**
     * Resolve Invoice DocumentNumber and InvoiceLine Names + Balance from their IDs.
     */
    @AuraEnabled(cacheable=true)
    public static Map<String, Object> getRelatedNames(List<Id> invoiceIds, List<Id> invoiceLineIds) {
        Map<String, Object> result = new Map<String, Object>();

        // Invoice DocumentNumber
        Map<String, String> invoiceNames = new Map<String, String>();
        if (invoiceIds != null && !invoiceIds.isEmpty()) {
            try {
                for (Invoice inv : [SELECT Id, DocumentNumber FROM Invoice WHERE Id IN :invoiceIds]) {
                    invoiceNames.put(inv.Id, inv.DocumentNumber);
                }
            } catch (Exception e) {
                // If query fails, return empty map
            }
        }
        result.put('invoiceNames', invoiceNames);

        // InvoiceLine Name + Balance (fetch separately so a Balance failure never blocks Name)
        Map<String, String> lineNames = new Map<String, String>();
        Map<String, Decimal> lineBalances = new Map<String, Decimal>();
        if (invoiceLineIds != null && !invoiceLineIds.isEmpty()) {
            // Always fetch Name
            try {
                for (InvoiceLine il : [SELECT Id, Name FROM InvoiceLine WHERE Id IN :invoiceLineIds]) {
                    lineNames.put(il.Id, il.Name);
                }
            } catch (Exception e) {
                // Name query failed – return empty maps
            }

            // Attempt Balance separately via dynamic SOQL
            try {
                List<SObject> lines = Database.query('SELECT Id, Balance FROM InvoiceLine WHERE Id IN :invoiceLineIds');
                for (SObject il : lines) {
                    Object balVal = il.get('Balance');
                    if (balVal != null) {
                        lineBalances.put(String.valueOf(il.get('Id')), (Decimal) balVal);
                    }
                }
            } catch (Exception e) {
                // Balance field not queryable in this org – leave map empty
            }
        }
        result.put('lineNames', lineNames);
        result.put('lineBalances', lineBalances);

        return result;
    }

    /**
     * Save updated approved amounts on DisputeItem records.
     * Uses Schema describe to find the real API name for Approved Amount.
     */
    @AuraEnabled
    public static void saveApprovedAmounts(List<Map<String, Object>> items) {
        if (items == null || items.isEmpty()) return;

        Schema.SObjectType diType = Schema.getGlobalDescribe().get('DisputeItem');
        if (diType == null) {
            throw new AuraHandledException('DisputeItem object not found.');
        }

        // Find the approved amount field by scanning all fields
        Map<String, Schema.SObjectField> fieldMap = diType.getDescribe().fields.getMap();
        String approvedFieldApi = null;
        for (String key : fieldMap.keySet()) {
            Schema.DescribeFieldResult fd = fieldMap.get(key).getDescribe();
            String label = fd.getLabel().toLowerCase();
            if (label.contains('approved') && label.contains('amount')) {
                approvedFieldApi = fd.getName();
                break;
            }
        }

        if (approvedFieldApi == null) {
            // Fallback: search by API name pattern
            for (String key : fieldMap.keySet()) {
                if (key.contains('approved')) {
                    approvedFieldApi = fieldMap.get(key).getDescribe().getName();
                    break;
                }
            }
        }

        if (approvedFieldApi == null) {
            List<String> allFields = new List<String>();
            for (String key : fieldMap.keySet()) {
                allFields.add(fieldMap.get(key).getDescribe().getName());
            }
            allFields.sort();
            throw new AuraHandledException('Approved Amount field not found. All fields: ' + String.join(allFields, ', '));
        }

        // Collect IDs and amounts
        List<Id> itemIds = new List<Id>();
        Map<Id, Decimal> amountMap = new Map<Id, Decimal>();
        for (Map<String, Object> item : items) {
            Id itemId = Id.valueOf((String) item.get('id'));
            Object amtObj = item.get('approvedAmount');
            Decimal amt = amtObj != null ? Decimal.valueOf(String.valueOf(amtObj)) : 0;
            itemIds.add(itemId);
            amountMap.put(itemId, amt);
        }

        // Query and update using the discovered field name
        try {
            String query = 'SELECT Id, ' + approvedFieldApi + ' FROM DisputeItem WHERE Id IN :itemIds';
            List<SObject> records = Database.query(query);
            for (SObject rec : records) {
                rec.put(approvedFieldApi, amountMap.get(rec.Id));
            }
            update records;
        } catch (Exception e) {
            throw new AuraHandledException('Save failed (field: ' + approvedFieldApi + '): ' + e.getMessage());
        }
    }
}