/**
 * @description Controller for the rlmUsageDataTable LWC. Dynamically queries usage-related
 *              SObjects using FieldSet metadata to determine which fields to SELECT and how
 *              to build lightning-datatable column definitions.
 *
 *              Supports TransactionJournal, UsageSummary, and UsageBillingPeriodItem.
 *              All queries are scoped to a single Account via AccountId.
 *
 *              Field handling:
 *              - Name fields (isNameField) render as clickable URLs linking to the record itself
 *              - Lookup fields (REFERENCE) render as clickable URLs linking to the related record,
 *                with the related record's name field as the display label
 *              - All other fields render as standard datatable columns with type-appropriate formatting
 *
 * @see RLM_UsageDatatable (FieldSet) on TransactionJournal, UsageSummary, UsageBillingPeriodItem
 */
public with sharing class RLM_UsageDataController {

    /** Allowlist of SObjects this controller can query. Validated server-side to prevent
     *  unauthorized object access even though the LWC picklist constrains the client-side options. */
    private static final Set<String> ALLOWED_OBJECTS = new Set<String>{
        'TransactionJournal', 'UsageSummary', 'UsageBillingPeriodItem'
    };

    /** Maps Apex Schema.DisplayType values to lightning-datatable column type strings. */
    private static final Map<Schema.DisplayType, String> TYPE_MAP = new Map<Schema.DisplayType, String>{
        Schema.DisplayType.STRING => 'text',
        Schema.DisplayType.PICKLIST => 'text',
        Schema.DisplayType.TEXTAREA => 'text',
        Schema.DisplayType.ID => 'text',
        Schema.DisplayType.PHONE => 'phone',
        Schema.DisplayType.COMBOBOX => 'text',
        Schema.DisplayType.EMAIL => 'email',
        Schema.DisplayType.DOUBLE => 'number',
        Schema.DisplayType.INTEGER => 'number',
        Schema.DisplayType.LONG => 'number',
        Schema.DisplayType.CURRENCY => 'currency',
        Schema.DisplayType.DATE => 'date',
        Schema.DisplayType.DATETIME => 'date',
        Schema.DisplayType.BOOLEAN => 'boolean',
        Schema.DisplayType.PERCENT => 'percent',
        Schema.DisplayType.URL => 'url'
    };

    /**
     * @description Queries records for the given SObject using fields defined in a FieldSet,
     *              and returns both the datatable column definitions and flattened record data.
     * @param accountId The Account record Id to filter by (WHERE AccountId = :accountId)
     * @param objectApiName API name of the SObject to query (must be in ALLOWED_OBJECTS)
     * @param fieldSetName Developer name of the FieldSet on the target SObject
     * @return Map with two keys:
     *         - 'columns': List<Map<String, Object>> - lightning-datatable column definitions
     *         - 'records': List<Map<String, Object>> - flattened record data with lookup URLs resolved
     * @throws AuraHandledException if objectApiName is not in the allowlist or fieldSetName is invalid
     */
    @AuraEnabled(cacheable=true)
    public static Map<String, Object> getFieldSetData(
        Id accountId,
        String objectApiName,
        String fieldSetName
    ) {
        if (!ALLOWED_OBJECTS.contains(objectApiName)) {
            throw new AuraHandledException('Invalid SObject: ' + objectApiName);
        }

        // Use describeSObjects() instead of getGlobalDescribe() to avoid loading all SObject metadata
        Schema.DescribeSObjectResult objDescribe = Schema.describeSObjects(
            new List<String>{ objectApiName }
        )[0];

        Schema.FieldSet fs = objDescribe.fieldSets.getMap().get(fieldSetName);
        if (fs == null) {
            throw new AuraHandledException('Invalid FieldSet: ' + fieldSetName + ' on ' + objectApiName);
        }

        // Build SOQL field list and column definitions from the FieldSet
        List<String> queryFields = new List<String>{ 'Id' };
        List<Map<String, Object>> columns = new List<Map<String, Object>>();
        Map<String, String> lookupRelNames = new Map<String, String>();   // fieldApiName -> relationship name
        Map<String, String> lookupNameFields = new Map<String, String>(); // fieldApiName -> related object's name field
        Set<String> nameFieldApis = new Set<String>();                    // tracks which fields are name fields
        Map<Schema.SObjectType, String> nameFieldCache = new Map<Schema.SObjectType, String>(); // avoids redundant describes

        Map<String, Schema.SObjectField> fieldMap = objDescribe.fields.getMap();

        for (Schema.FieldSetMember fsm : fs.getFields()) {
            String fieldApiName = fsm.getFieldPath();
            Schema.DisplayType fieldType = fsm.getType();
            String label = fsm.getLabel();
            Schema.SObjectField sObjField = fieldMap.get(fieldApiName);
            if (sObjField == null) {
                throw new AuraHandledException(
                    'FieldSet entry "' + fieldApiName + '" on ' + objectApiName +
                    ' is not a direct field on the object. Relationship paths and non-field entries are not supported.'
                );
            }
            Schema.DescribeFieldResult fieldDescribe = sObjField.getDescribe();

            if (fieldDescribe.isNameField()) {
                // Name fields (e.g. Name, UsageBillingPeriodItemNum) render as URLs to the record itself
                queryFields.add(fieldApiName);
                nameFieldApis.add(fieldApiName);
                columns.add(buildUrlColumn(label, fieldApiName + '__url', fieldApiName));

            } else if (fieldType == Schema.DisplayType.REFERENCE) {
                // Lookup fields render as URLs to the related record with the related name as label
                queryFields.add(fieldApiName);
                String relName = fieldDescribe.getRelationshipName();
                if (relName != null) {
                    String nameField = resolveNameField(fieldDescribe.getReferenceTo(), nameFieldCache);
                    queryFields.add(relName + '.' + nameField);
                    lookupRelNames.put(fieldApiName, relName);
                    lookupNameFields.put(fieldApiName, nameField);
                    columns.add(buildUrlColumn(label, fieldApiName + '__url', fieldApiName + '__name'));
                } else {
                    // Polymorphic reference: no relationship name, __name would never be populated
                    // so fall back to a plain text column showing the Id.
                    Map<String, Object> col = new Map<String, Object>();
                    col.put('label', label);
                    col.put('fieldName', fieldApiName);
                    col.put('type', 'text');
                    col.put('sortable', true);
                    columns.add(col);
                }

            } else {
                // Standard fields use type-mapped datatable column types
                queryFields.add(fieldApiName);
                String datatableType = TYPE_MAP.containsKey(fieldType) ? TYPE_MAP.get(fieldType) : 'text';

                Map<String, Object> col = new Map<String, Object>();
                col.put('label', label);
                col.put('fieldName', fieldApiName);
                col.put('type', datatableType);
                col.put('sortable', true);
                columns.add(col);
            }
        }

        // WITH SECURITY_ENFORCED enforces CRUD and FLS; `with sharing` enforces record access.
        // Users need the RLM_UsageDatatables permission set for the required object/field grants.
        String soql = 'SELECT ' + String.join(queryFields, ', ') +
            ' FROM ' + objectApiName +
            ' WHERE AccountId = :accountId WITH SECURITY_ENFORCED ORDER BY Id ASC';

        List<SObject> records = Database.query(soql);

        // Flatten SObject records into simple maps for lightning-datatable consumption.
        // Lookup relationships are resolved into separate __url and __name keys.
        List<Map<String, Object>> flatRecords = new List<Map<String, Object>>();
        for (SObject rec : records) {
            Map<String, Object> row = new Map<String, Object>();
            row.put('Id', rec.get('Id'));

            for (Schema.FieldSetMember fsm : fs.getFields()) {
                String fieldApiName = fsm.getFieldPath();

                if (nameFieldApis.contains(fieldApiName)) {
                    row.put(fieldApiName, rec.get(fieldApiName));
                    row.put(fieldApiName + '__url', '/' + String.valueOf(rec.get('Id')));

                } else if (fsm.getType() == Schema.DisplayType.REFERENCE) {
                    Object lookupId = rec.get(fieldApiName);
                    // Always populate fieldApiName with the raw Id so that text-column
                    // fallbacks (polymorphic/no-relationship-name fields) render correctly.
                    row.put(fieldApiName, lookupId);
                    if (lookupId != null) {
                        row.put(fieldApiName + '__url', '/' + String.valueOf(lookupId));
                        String relName = lookupRelNames.get(fieldApiName);
                        if (relName != null) {
                            SObject related = rec.getSObject(relName);
                            String nameField = lookupNameFields.get(fieldApiName);
                            row.put(fieldApiName + '__name', related != null ? related.get(nameField) : null);
                        }
                    } else {
                        row.put(fieldApiName + '__url', null);
                        row.put(fieldApiName + '__name', null);
                    }

                } else {
                    row.put(fieldApiName, rec.get(fieldApiName));
                }
            }

            flatRecords.add(row);
        }

        return new Map<String, Object>{
            'columns' => columns,
            'records' => flatRecords
        };
    }

    /**
     * @description Builds a lightning-datatable URL column definition. Used for both name fields
     *              (linking to the record itself) and lookup fields (linking to the related record).
     * @param label The column header label
     * @param fieldName The data key for the URL value (e.g. 'AssetId__url')
     * @param labelFieldName The data key for the display text (e.g. 'AssetId__name' or 'Name')
     * @return Column definition map compatible with lightning-datatable
     */
    private static Map<String, Object> buildUrlColumn(String label, String fieldName, String labelFieldName) {
        return new Map<String, Object>{
            'label' => label,
            'fieldName' => fieldName,
            'type' => 'url',
            'sortable' => true,
            'typeAttributes' => new Map<String, Object>{
                'label' => new Map<String, Object>{ 'fieldName' => labelFieldName },
                'target' => '_self'
            }
        };
    }

    /**
     * @description Resolves the name field for a related SObject. Most objects use 'Name', but some
     *              (e.g. UsageBillingPeriodItem) use auto-number fields like 'UsageBillingPeriodItemNum'.
     * @param refTypes List of SObjectType references from DescribeFieldResult.getReferenceTo()
     * @return The API name of the related object's name field, defaults to 'Name'
     */
    private static String resolveNameField(List<Schema.SObjectType> refTypes, Map<Schema.SObjectType, String> cache) {
        if (refTypes.isEmpty()) {
            return 'Name';
        }
        Schema.SObjectType refType = refTypes[0];
        if (cache.containsKey(refType)) {
            return cache.get(refType);
        }
        String result = 'Name';
        for (Schema.SObjectField f : refType.getDescribe().fields.getMap().values()) {
            if (f.getDescribe().isNameField()) {
                result = f.getDescribe().getName();
                break;
            }
        }
        cache.put(refType, result);
        return result;
    }
}
