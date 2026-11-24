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
                invoiceNames.putAll(namesById(
                    [SELECT Id, DocumentNumber FROM Invoice WHERE Id IN :invoiceIds WITH USER_MODE], 'DocumentNumber'));
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
                lineNames.putAll(namesById(
                    [SELECT Id, Name FROM InvoiceLine WHERE Id IN :invoiceLineIds WITH USER_MODE], 'Name'));
            } catch (Exception e) {
                // Name query failed – return empty maps
            }

            // Attempt Balance separately via dynamic SOQL
            try {
                List<SObject> lines = Database.query('SELECT Id, Balance FROM InvoiceLine WHERE Id IN :invoiceLineIds', AccessLevel.USER_MODE);
                lineBalances.putAll(balancesById(lines));
            } catch (Exception e) {
                // Balance field not queryable in this org – leave map empty
            }
        }
        result.put('lineNames', lineNames);
        result.put('lineBalances', lineBalances);

        return result;
    }

    // Each row's field value keyed by its id. Takes rows so a test can pass invoices and invoice
    // lines, which Apex cannot insert.
    @TestVisible
    private static Map<String, String> namesById(List<SObject> rows, String field) {
        Map<String, String> names = new Map<String, String>();
        for (SObject row : rows) {
            names.put(row.Id, (String) row.get(field));
        }
        return names;
    }

    // Each line's balance keyed by its id; a line with no balance is left out. Takes rows so a
    // test can pass invoice lines, which Apex cannot insert.
    @TestVisible
    private static Map<String, Decimal> balancesById(List<SObject> lines) {
        Map<String, Decimal> balances = new Map<String, Decimal>();
        for (SObject il : lines) {
            Object balVal = il.get('Balance');
            if (balVal != null) {
                balances.put(String.valueOf(il.get('Id')), (Decimal) balVal);
            }
        }
        return balances;
    }

    /**
     * Save updated approved amounts on DisputeItem records.
     * Uses Schema describe to find the real API name for Approved Amount.
     */
    @TestVisible
    private static final String SAVE_UNAVAILABLE_MESSAGE =
        'Approved amounts cannot be saved in this org. Contact your administrator.';
    @TestVisible
    private static final String SAVE_FAILED_MESSAGE =
        'The approved amounts could not be saved. Check the amounts and your access, then try again.';

    @AuraEnabled
    public static void saveApprovedAmounts(List<Map<String, Object>> items) {
        if (items == null || items.isEmpty()) return;

        Schema.SObjectType diType = Schema.getGlobalDescribe().get('DisputeItem');
        if (diType == null) {
            throw RLM_AuraErrors.handled('DisputeItem object not found.');
        }

        String approvedFieldApi = approvedAmountField(diType.getDescribe().fields.getMap());
        if (approvedFieldApi == null) {
            throw RLM_AuraErrors.handled(SAVE_UNAVAILABLE_MESSAGE);
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
        List<SObject> records;
        try {
            String query = 'SELECT Id, ' + approvedFieldApi + ' FROM DisputeItem WHERE Id IN :itemIds';
            records = Database.query(query, AccessLevel.USER_MODE);
        } catch (Exception e) {
            throw RLM_AuraErrors.failed(SAVE_FAILED_MESSAGE,
                'RLM_DisputeDetailsController read of DisputeItem.' + approvedFieldApi, e);
        }
        // Report ids that did not resolve (missing, deleted or not visible) instead of
        // silently saving a subset. Nothing is updated in that case.
        if (records.size() != amountMap.size()) {
            Integer missing = amountMap.size() - records.size();
            String message = missing + ' of ' + amountMap.size()
                + ' dispute items were not found or are not accessible; nothing was saved.';
            throw RLM_AuraErrors.handled(message);
        }
        try {
            for (SObject rec : records) {
                rec.put(approvedFieldApi, amountMap.get(rec.Id));
            }
            update as user records;
        } catch (Exception e) {
            throw RLM_AuraErrors.failed(SAVE_FAILED_MESSAGE,
                'RLM_DisputeDetailsController update of DisputeItem.' + approvedFieldApi, e);
        }
    }

    // The DisputeItem field that holds the approved amount: the first (by API name) whose label
    // has both "approved" and "amount", else the first whose name has "approved", else null.
    // Takes the field map so a test can pass one without such a field.
    @TestVisible
    private static String approvedAmountField(Map<String, Schema.SObjectField> fieldMap) {
        // Find the approved amount field by scanning all fields.
        // Sort keys first so selection is deterministic across orgs.
        List<String> sortedKeys = new List<String>(fieldMap.keySet());
        sortedKeys.sort();
        String approvedFieldApi = null;
        for (String key : sortedKeys) {
            Schema.DescribeFieldResult fd = fieldMap.get(key).getDescribe();
            String label = fd.getLabel().toLowerCase();
            if (label.contains('approved') && label.contains('amount')) {
                approvedFieldApi = fd.getName();
                break;
            }
        }

        if (approvedFieldApi == null) {
            // Fallback: search by API name pattern
            for (String key : sortedKeys) {
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
            System.debug(LoggingLevel.ERROR, 'RLM_DisputeDetailsController: no approved-amount field on DisputeItem. Fields: '
                + String.join(allFields, ', '));
        }
        return approvedFieldApi;
    }
}
