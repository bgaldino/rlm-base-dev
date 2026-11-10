/**
 * Tests for RLM_UsageDataController.getFieldSetData: the object and filter-field allowlists,
 * column definitions built from each RLM_UsageDatatable field set, how TransactionJournal
 * rows are flattened (name links, lookup links and labels), record scoping by the filter
 * field, and the row cap.
 *
 * UsageSummary and UsageBillingPeriodItem rows are produced by usage orchestration, so those
 * objects are exercised for their column definitions and an empty result only.
 *
 * Every test that reaches the controller's query needs the fields it selects to be readable by
 * the running user (for example via RLM_UsageDatatables, shipped in this bundle). The build
 * assigns that set only after this bundle deploys, so @TestSetup assigns it to the running
 * user when missing. Without read access the query fails with "No such column" even when it
 * would return no rows. The runner is the deploying user, so these tests do not show that the
 * set alone is enough. The rejection tests fail before any query and do not use the
 * assignment, though a failed @TestSetup assignment still fails them along with the rest of
 * the class.
 *
 * Not covered:
 *  - the null-lookup branch of the flattener. Describe reports every lookup in the
 *    TransactionJournal field set (ReferenceRecordId, UsageResourceId, QuantityUnitOfMeasureId)
 *    as nillable, but inserting a journal with any of them null fails with
 *    FIELD_INTEGRITY_EXCEPTION, so no journal row can carry a null lookup.
 *  - the text-column fallback for a reference field with no relationship name. Every
 *    reference field in the shipped field sets, including the polymorphic ReferenceRecordId
 *    and GrantBindingTargetId, has a relationship name, so no member reaches it.
 *  - the controller's Security.stripInaccessible path. The query needs every selected field
 *    to be readable, so stripping never removes anything in these tests.
 */
@IsTest
private with sharing class RLM_UsageDataControllerTest {

    private static final String FIELD_SET = 'RLM_UsageDatatable';
    private static final String ACCOUNT_NAME = 'RLM UDC Account';
    private static final String EMPTY_ACCOUNT_NAME = 'RLM UDC Empty Account';
    private static final String ASSET_ONE = 'RLM UDC Asset One';
    private static final String ASSET_TWO = 'RLM UDC Asset Two';
    private static final String RESOURCE_NAME = 'RLM UDC Resource';
    private static final String UOM_NAME = 'RLM UDC Unit';
    private static final String PRODUCT_NAME = 'RLM UDC Usage Product';

    @TestSetup
    static void setupData() {
        Account acc = new Account(Name = ACCOUNT_NAME);
        Account emptyAcc = new Account(Name = EMPTY_ACCOUNT_NAME);
        insert new List<Account>{ acc, emptyAcc };

        Product2 prod = new Product2(Name = PRODUCT_NAME, IsActive = true, UsageModelType = 'Anchor');
        insert prod;

        UnitOfMeasureClass uomClass = new UnitOfMeasureClass(
            Name = 'RLM UDC Volume',
            Code = 'RLM_UDC_TEST_UOMC',
            Type = 'Usage',
            Status = 'Draft'
        );
        insert uomClass;
        uomClass.Status = 'Active';
        update uomClass;

        UnitOfMeasure uom = new UnitOfMeasure(
            Name = UOM_NAME,
            UnitCode = 'RLMUDCU',
            Type = 'Usage',
            UnitOfMeasureClassId = uomClass.Id,
            Status = 'Draft'
        );
        insert uom;
        uom.Status = 'Active';
        update uom;

        UsageResource ur = new UsageResource(
            Name = RESOURCE_NAME,
            Code = 'RLM_UDC_TEST_UR',
            Category = 'Usage',
            Status = 'Draft',
            DefaultUnitOfMeasureId = uom.Id,
            UnitOfMeasureClassId = uomClass.Id
        );
        insert ur;
        ur.Status = 'Active';
        update ur;

        ProductUsageResource pur = new ProductUsageResource(
            ProductId = prod.Id,
            UsageResourceId = ur.Id,
            Status = 'Draft',
            EffectiveStartDate = Datetime.now().addDays(-30),
            IsOptional = false
        );
        insert pur;
        pur.Status = 'Active';
        update pur;

        Asset one = new Asset(Name = ASSET_ONE, AccountId = acc.Id, Product2Id = prod.Id);
        Asset two = new Asset(Name = ASSET_TWO, AccountId = acc.Id, Product2Id = prod.Id);
        insert new List<Asset>{ one, two };

        insert new List<TransactionJournal>{
            buildJournal(acc.Id, one.Id, ur.Id, uom.Id, 150),
            buildJournal(acc.Id, one.Id, ur.Id, uom.Id, 25),
            buildJournal(acc.Id, two.Id, ur.Id, uom.Id, 7)
        };

        // After the non-setup DML, in its own runAs context to avoid mixed DML: one assignment
        // per test class run, rather than one per test method.
        Id me = UserInfo.getUserId();
        Id setId = usageDatatablesSetId();
        if ([SELECT COUNT() FROM PermissionSetAssignment WHERE AssigneeId = :me AND PermissionSetId = :setId] == 0) {
            System.runAs(new User(Id = me)) {
                insert new PermissionSetAssignment(AssigneeId = me, PermissionSetId = setId);
            }
        }
    }

    // ─── Fixtures ───────────────────────────────────────────────────────

    private static TransactionJournal buildJournal(Id accountId, Id assetId, Id resourceId, Id uomId, Decimal qty) {
        Datetime activity = Datetime.now().addDays(-1);
        return new TransactionJournal(
            AccountId = accountId,
            ReferenceRecordId = assetId,
            UsageResourceId = resourceId,
            QuantityUnitOfMeasureId = uomId,
            Quantity = qty,
            ActivityDate = activity,
            StartDate = activity,
            EndDate = activity,
            UsageType = 'UsageManagement',
            Status = 'Pending'
        );
    }

    private static Id accountId(String name) {
        return [SELECT Id FROM Account WHERE Name = :name LIMIT 1].Id;
    }

    private static Asset assetNamed(String name) {
        return [SELECT Id, Name FROM Asset WHERE Name = :name LIMIT 1];
    }

    private static List<Map<String, Object>> columnsOf(Map<String, Object> result) {
        return (List<Map<String, Object>>) result.get('columns');
    }

    private static List<Map<String, Object>> recordsOf(Map<String, Object> result) {
        return (List<Map<String, Object>>) result.get('records');
    }

    private static Map<String, Object> column(List<Map<String, Object>> columns, String fieldName) {
        for (Map<String, Object> col : columns) {
            if (fieldName.equals(col.get('fieldName'))) {
                return col;
            }
        }
        Assert.fail('No column with fieldName ' + fieldName + ' in ' + JSON.serialize(columns));
        return null;
    }

    private static Map<String, Object> rowFor(List<Map<String, Object>> rows, Id recordId) {
        for (Map<String, Object> row : rows) {
            if (recordId == (Id) row.get('Id')) {
                return row;
            }
        }
        Assert.fail('No row for ' + recordId);
        return null;
    }

    /** Asserts a url column whose link text comes from labelField. */
    private static void assertUrlColumn(Map<String, Object> col, String labelField) {
        Assert.areEqual('url', col.get('type'), col.get('fieldName') + ' renders as a link');
        Assert.areEqual(true, col.get('sortable'), col.get('fieldName') + ' is sortable');
        Map<String, Object> typeAttributes = (Map<String, Object>) col.get('typeAttributes');
        Assert.isNotNull(typeAttributes, col.get('fieldName') + ' carries typeAttributes');
        Map<String, Object> label = (Map<String, Object>) typeAttributes.get('label');
        Assert.areEqual(labelField, label.get('fieldName'), col.get('fieldName') + ' link text field');
        Assert.areEqual('_self', typeAttributes.get('target'), col.get('fieldName') + ' opens in the same tab');
    }

    /** The object's RLM_UsageDatatable field set, failing as a PRECONDITION when it is missing. */
    private static Schema.FieldSet usageFieldSet(Schema.SObjectType type) {
        Schema.DescribeSObjectResult objDescribe = type.getDescribe();
        Schema.FieldSet fs = objDescribe.fieldSets.getMap().get(FIELD_SET);
        Assert.isNotNull(fs, 'PRECONDITION: ' + objDescribe.getName() + ' has the ' + FIELD_SET + ' field set');
        return fs;
    }

    /**
     * Asserts that every field the controller's query touches for this object is readable by
     * the running user (for example via RLM_UsageDatatables, or because the field is required,
     * as Name and Status are): the filter fields, every RLM_UsageDatatable field set member, and
     * for each reference member with a relationship name, the related object's name field used
     * as the link label. The related name field is found the way the controller finds it: the
     * isNameField() field of getReferenceTo()[0], falling back to Name. Derived from the field
     * set and describe, so it follows the field set; mirrors the controller's name-field
     * resolution (polymorphic lookups excepted).
     */
    private static void assertFieldSetReadable(Schema.SObjectType type, List<String> filterFields) {
        Schema.DescribeSObjectResult objDescribe = type.getDescribe();
        String objName = objDescribe.getName();
        Map<String, Schema.SObjectField> fields = objDescribe.fields.getMap();
        Map<String, Schema.SObjectField> touched = new Map<String, Schema.SObjectField>();
        for (String filterField : filterFields) {
            touched.put(objName + '.' + filterField, fields.get(filterField));
        }
        for (Schema.FieldSetMember member : usageFieldSet(type).getFields()) {
            String path = member.getFieldPath();
            Schema.SObjectField f = fields.get(path);
            Assert.isNotNull(f, 'PRECONDITION: ' + objName + '.' + path + ' exists on the object');
            Schema.DescribeFieldResult fieldDescribe = f.getDescribe();
            touched.put(objName + '.' + path, f);
            if (fieldDescribe.isNameField()
                || member.getType() != Schema.DisplayType.REFERENCE
                || fieldDescribe.getRelationshipName() == null
                || fieldDescribe.getReferenceTo().isEmpty()
                || fieldDescribe.getReferenceTo().size() > 1) {
                // A polymorphic lookup's .Name resolves against the Name entity, not
                // getReferenceTo()[0], so its label field is not checked here.
                continue;
            }
            Schema.DescribeSObjectResult refDescribe = fieldDescribe.getReferenceTo()[0].getDescribe();
            Map<String, Schema.SObjectField> refFields = refDescribe.fields.getMap();
            Schema.SObjectField nameField = refFields.get('Name');
            for (Schema.SObjectField candidate : refFields.values()) {
                if (candidate.getDescribe().isNameField()) {
                    nameField = candidate;
                    break;
                }
            }
            Assert.isNotNull(nameField, 'PRECONDITION: ' + refDescribe.getName() + ' has a name field for the link label');
            touched.put(refDescribe.getName() + '.' + nameField.getDescribe().getName(), nameField);
        }
        for (String label : touched.keySet()) {
            Assert.isNotNull(touched.get(label), 'PRECONDITION: ' + label + ' exists');
            Assert.isTrue(
                touched.get(label).getDescribe().isAccessible(),
                'PRECONDITION: ' + label + ' must be readable by the running user (for example via RLM_UsageDatatables)'
            );
        }
    }

    private static Id usageDatatablesSetId() {
        List<PermissionSet> sets = [SELECT Id FROM PermissionSet WHERE Name = 'RLM_UsageDatatables' AND NamespacePrefix = null LIMIT 1];
        Assert.isFalse(sets.isEmpty(), 'PRECONDITION: RLM_UsageDatatables ships in this bundle');
        return sets[0].Id;
    }

    /**
     * The running user, for System.runAs: a fresh context so the RLM_UsageDatatables assignment
     * made in @TestSetup is in effect. Every test that reaches the controller's query runs as
     * this user. Read-only: it only checks that the assignment is there.
     */
    private static User runningUserHoldingUsageDatatables() {
        Id me = UserInfo.getUserId();
        Id setId = usageDatatablesSetId();
        Assert.areEqual(
            1,
            [SELECT COUNT() FROM PermissionSetAssignment WHERE AssigneeId = :me AND PermissionSetId = :setId],
            'PRECONDITION: the running user holds RLM_UsageDatatables (assigned in @TestSetup when missing)'
        );
        return new User(Id = me);
    }

    private static void assertRejected(Id recordId, String filterField, String objectApiName, String fieldSetName) {
        Boolean threw = false;
        Integer queriesBefore = Limits.getQueries();
        try {
            RLM_UsageDataController.getFieldSetData(recordId, filterField, objectApiName, fieldSetName);
        } catch (AuraHandledException e) {
            threw = true;
        }
        Assert.isTrue(
            threw,
            'Expected rejection for object=' + objectApiName + ' filter=' + filterField + ' fieldSet=' + fieldSetName
        );
        Assert.areEqual(
            queriesBefore,
            Limits.getQueries(),
            'A rejected request must fail before any SOQL runs (object=' + objectApiName + ', filter=' + filterField + ')'
        );
    }

    // ─── TransactionJournal ─────────────────────────────────────────────

    @IsTest
    static void transactionJournalColumnsFollowTheFieldSet() {
        Id accId = accountId(ACCOUNT_NAME);

        System.runAs(runningUserHoldingUsageDatatables()) {
            assertFieldSetReadable(TransactionJournal.SObjectType, new List<String>{ 'AccountId' });

            Test.startTest();
            Map<String, Object> result = RLM_UsageDataController.getFieldSetData(
                accId, 'AccountId', 'TransactionJournal', FIELD_SET
            );
            Test.stopTest();

            List<Map<String, Object>> columns = columnsOf(result);
            Assert.areEqual(
                usageFieldSet(TransactionJournal.SObjectType).getFields().size(),
                columns.size(),
                'One column per field set member'
            );

            // Name is the autonumber name field: a link to the record itself, labelled by the name.
            assertUrlColumn(column(columns, 'Name__url'), 'Name');

            // Lookups with a relationship name link to the related record, labelled by its name.
            assertUrlColumn(column(columns, 'UsageResourceId__url'), 'UsageResourceId__name');
            assertUrlColumn(column(columns, 'QuantityUnitOfMeasureId__url'), 'QuantityUnitOfMeasureId__name');
            assertUrlColumn(column(columns, 'ReferenceRecordId__url'), 'ReferenceRecordId__name');

            // Plain fields render with these column types.
            Assert.areEqual('date', column(columns, 'ActivityDate').get('type'), 'ActivityDate renders as a date column');
            Assert.areEqual('date', column(columns, 'StartDate').get('type'), 'StartDate renders as a date column');
            Assert.areEqual('number', column(columns, 'Quantity').get('type'), 'Quantity renders as a number column');
            Assert.areEqual('text', column(columns, 'Status').get('type'), 'Status renders as a text column');
            Assert.areEqual(true, column(columns, 'Quantity').get('sortable'), 'Plain columns are sortable');
            String quantityLabel;
            for (Schema.FieldSetMember member : usageFieldSet(TransactionJournal.SObjectType).getFields()) {
                if (member.getFieldPath() == 'Quantity') {
                    quantityLabel = member.getLabel();
                }
            }
            Assert.isNotNull(quantityLabel, 'PRECONDITION: Quantity is in the TransactionJournal field set');
            Assert.areEqual(quantityLabel, column(columns, 'Quantity').get('label'), 'Plain columns carry the field set label');
        }
    }

    @IsTest
    static void transactionJournalRowsAreFlattenedWithLinksAndLabels() {
        Id accId = accountId(ACCOUNT_NAME);
        Asset one = assetNamed(ASSET_ONE);
        UsageResource ur = [SELECT Id FROM UsageResource WHERE Name = :RESOURCE_NAME LIMIT 1];
        UnitOfMeasure uom = [SELECT Id FROM UnitOfMeasure WHERE Name = :UOM_NAME LIMIT 1];
        TransactionJournal journal150 = [
            SELECT Id, Name FROM TransactionJournal WHERE ReferenceRecordId = :one.Id AND Quantity = 150 LIMIT 1
        ];

        System.runAs(runningUserHoldingUsageDatatables()) {
            assertFieldSetReadable(TransactionJournal.SObjectType, new List<String>{ 'AccountId' });

            Test.startTest();
            Map<String, Object> result = RLM_UsageDataController.getFieldSetData(
                accId, 'AccountId', 'TransactionJournal', FIELD_SET
            );
            Test.stopTest();

            Assert.areEqual(false, result.get('truncated'), 'Three rows are well under the cap');
            List<Map<String, Object>> rows = recordsOf(result);
            Assert.areEqual(3, rows.size(), 'Every journal on the account is returned');

            Map<String, Object> row = rowFor(rows, journal150.Id);
            Assert.areEqual(journal150.Name, row.get('Name'), 'The name field carries the record name');
            Assert.areEqual('/' + journal150.Id, row.get('Name__url'), 'The name links to the journal itself');
            Assert.areEqual(150, ((Decimal) row.get('Quantity')).intValue(), 'Plain fields are copied as-is');
            Assert.areEqual('Pending', row.get('Status'), 'Picklist values are copied as-is');
            Assert.areEqual(ur.Id, row.get('UsageResourceId'), 'The raw lookup id is kept');
            Assert.areEqual('/' + ur.Id, row.get('UsageResourceId__url'), 'The lookup links to the related record');
            Assert.areEqual(RESOURCE_NAME, row.get('UsageResourceId__name'), 'The lookup label is the related name');
            Assert.areEqual(uom.Id, row.get('QuantityUnitOfMeasureId'), 'The raw unit of measure id is kept');
            Assert.areEqual(UOM_NAME, row.get('QuantityUnitOfMeasureId__name'), 'The unit of measure label is its name');
            Assert.areEqual(one.Id, row.get('ReferenceRecordId'), 'The polymorphic asset id is kept');
            Assert.areEqual('/' + one.Id, row.get('ReferenceRecordId__url'), 'The asset reference links to the asset');
            Assert.areEqual(ASSET_ONE, row.get('ReferenceRecordId__name'), 'The asset reference is labelled by name');
        }
    }

    @IsTest
    static void transactionJournalsAreScopedToTheFilterRecord() {
        Asset two = assetNamed(ASSET_TWO);

        System.runAs(runningUserHoldingUsageDatatables()) {
            assertFieldSetReadable(TransactionJournal.SObjectType, new List<String>{ 'ReferenceRecordId' });

            Test.startTest();
            Map<String, Object> result = RLM_UsageDataController.getFieldSetData(
                two.Id, 'ReferenceRecordId', 'TransactionJournal', FIELD_SET
            );
            Test.stopTest();

            List<Map<String, Object>> rows = recordsOf(result);
            Assert.areEqual(1, rows.size(), 'Only the journal referencing the second asset is returned');
            Assert.areEqual(two.Id, rows[0].get('ReferenceRecordId'), 'The row belongs to the filter record');
            Assert.areEqual(7, ((Decimal) rows[0].get('Quantity')).intValue(), 'It is the second asset\'s journal');
        }
    }

    @IsTest
    static void accountWithoutJournalsReturnsColumnsAndNoRows() {
        Id emptyAccId = accountId(EMPTY_ACCOUNT_NAME);

        System.runAs(runningUserHoldingUsageDatatables()) {
            assertFieldSetReadable(TransactionJournal.SObjectType, new List<String>{ 'AccountId' });

            Test.startTest();
            Map<String, Object> result = RLM_UsageDataController.getFieldSetData(
                emptyAccId, 'AccountId', 'TransactionJournal', FIELD_SET
            );
            Test.stopTest();

            Assert.isTrue(recordsOf(result).isEmpty(), 'No journals, no rows');
            Assert.areEqual(
                usageFieldSet(TransactionJournal.SObjectType).getFields().size(),
                columnsOf(result).size(),
                'Every field set column is still returned for the empty table'
            );
            Assert.areEqual(false, result.get('truncated'), 'An empty result is not truncated');
        }
    }

    /**
     * Pins current behaviour: a null recordId is not rejected. The query then filters on
     * AccountId = null, but no journal can carry a null AccountId (insert rejects it), so the
     * rows such a filter would match cannot be seeded and are not observed here.
     */
    @IsTest
    static void nullRecordIdIsNotRejected() {
        System.runAs(runningUserHoldingUsageDatatables()) {
            assertFieldSetReadable(TransactionJournal.SObjectType, new List<String>{ 'AccountId' });

            Test.startTest();
            Map<String, Object> result = RLM_UsageDataController.getFieldSetData(
                null, 'AccountId', 'TransactionJournal', FIELD_SET
            );
            Test.stopTest();

            Assert.isNotNull(
                result,
                'Known gap: a null recordId is not rejected; update this test when it is rejected'
            );
            Assert.isTrue(recordsOf(result).isEmpty(), 'No journal has a null AccountId, so nothing matches');
        }
    }

    @IsTest
    static void resultIsCappedAtTwoThousandRowsAndFlaggedTruncated() {
        Id accId = accountId(ACCOUNT_NAME);
        UsageResource ur = [SELECT Id FROM UsageResource WHERE Name = :RESOURCE_NAME LIMIT 1];
        UnitOfMeasure uom = [SELECT Id FROM UnitOfMeasure WHERE Name = :UOM_NAME LIMIT 1];
        Product2 prod = [SELECT Id FROM Product2 WHERE Name = :PRODUCT_NAME LIMIT 1];
        Asset busy = new Asset(Name = 'RLM UDC Busy Asset', AccountId = accId, Product2Id = prod.Id);
        insert busy;

        List<TransactionJournal> journals = new List<TransactionJournal>();
        for (Integer i = 0; i < 2001; i++) {
            journals.add(buildJournal(accId, busy.Id, ur.Id, uom.Id, 1));
        }
        insert journals;
        journals = null; // release the inserted list so the measured call has the heap to itself
        // Measured on a live org: the 2001-row call leaves about 1.27 MB on the heap (synchronous limit 6 MB).

        System.runAs(runningUserHoldingUsageDatatables()) {
            assertFieldSetReadable(TransactionJournal.SObjectType, new List<String>{ 'ReferenceRecordId' });

            Test.startTest();
            Map<String, Object> result = RLM_UsageDataController.getFieldSetData(
                busy.Id, 'ReferenceRecordId', 'TransactionJournal', FIELD_SET
            );
            Test.stopTest();

            Assert.areEqual(true, result.get('truncated'), 'More than 2000 matches is flagged truncated');
            Assert.areEqual(2000, recordsOf(result).size(), 'Rows are capped at 2000');
        }
    }

    // ─── UsageSummary / UsageBillingPeriodItem ──────────────────────────

    @IsTest
    static void usageSummaryColumnsResolveNonStandardNameFields() {
        Asset one = assetNamed(ASSET_ONE);
        // LiableSummaryId points at UsageBillingPeriodItem, whose name field is an autonumber
        // other than Name; the query below must resolve it or it throws.
        Assert.areEqual(
            new List<Schema.SObjectType>{ UsageBillingPeriodItem.SObjectType },
            UsageSummary.LiableSummaryId.getDescribe().getReferenceTo(),
            'PRECONDITION: UsageSummary.LiableSummaryId references only UsageBillingPeriodItem'
        );
        Assert.isFalse(
            Schema.SObjectType.UsageBillingPeriodItem.fields.getMap().containsKey('Name'),
            'PRECONDITION: UsageBillingPeriodItem has no Name field, so a Name fallback would fail the query'
        );

        System.runAs(runningUserHoldingUsageDatatables()) {
            assertFieldSetReadable(UsageSummary.SObjectType, new List<String>{ 'AssetId', 'AccountId' });

            Test.startTest();
            Map<String, Object> byAsset = RLM_UsageDataController.getFieldSetData(
                one.Id, 'AssetId', 'UsageSummary', FIELD_SET
            );
            Map<String, Object> byAccount = RLM_UsageDataController.getFieldSetData(
                accountId(ACCOUNT_NAME), 'AccountId', 'UsageSummary', FIELD_SET
            );
            Test.stopTest();

            List<Map<String, Object>> columns = columnsOf(byAsset);
            Assert.areEqual(
                usageFieldSet(UsageSummary.SObjectType).getFields().size(),
                columns.size(),
                'One column per field set member'
            );
            assertUrlColumn(column(columns, 'Name__url'), 'Name');
            assertUrlColumn(column(columns, 'AssetId__url'), 'AssetId__name');
            assertUrlColumn(column(columns, 'LiableSummaryId__url'), 'LiableSummaryId__name');
            assertUrlColumn(column(columns, 'UsageEntitlementAccountId__url'), 'UsageEntitlementAccountId__name');
            Assert.areEqual('number', column(columns, 'ConsumptionUnits').get('type'), 'ConsumptionUnits renders as a number column');

            Assert.isTrue(recordsOf(byAsset).isEmpty(), 'Tests create no usage summaries');
            Assert.isTrue(recordsOf(byAccount).isEmpty(), 'AccountId is accepted as a UsageSummary filter');
        }
    }

    @IsTest
    static void usageBillingPeriodItemColumnsUseItsAutonumberNameField() {
        Asset one = assetNamed(ASSET_ONE);

        System.runAs(runningUserHoldingUsageDatatables()) {
            assertFieldSetReadable(UsageBillingPeriodItem.SObjectType, new List<String>{ 'AssetId' });

            Test.startTest();
            Map<String, Object> result = RLM_UsageDataController.getFieldSetData(
                one.Id, 'AssetId', 'UsageBillingPeriodItem', FIELD_SET
            );
            Test.stopTest();

            List<Map<String, Object>> columns = columnsOf(result);
            Assert.areEqual(
                usageFieldSet(UsageBillingPeriodItem.SObjectType).getFields().size(),
                columns.size(),
                'One column per field set member'
            );
            assertUrlColumn(column(columns, 'UsageBillingPeriodItemNum__url'), 'UsageBillingPeriodItemNum');
            assertUrlColumn(column(columns, 'AssetId__url'), 'AssetId__name');
            assertUrlColumn(column(columns, 'UsageEntitlementBucketId__url'), 'UsageEntitlementBucketId__name');
            assertUrlColumn(column(columns, 'GrantBindingTargetId__url'), 'GrantBindingTargetId__name');
            Assert.areEqual('currency', column(columns, 'OverageAmount').get('type'), 'OverageAmount renders as a currency column');
            Assert.isTrue(recordsOf(result).isEmpty(), 'Tests create no billing period items');
            Assert.areEqual(false, result.get('truncated'), 'An empty result is not truncated');
        }
    }

    // ─── Allowlists and validation ──────────────────────────────────────

    @IsTest
    static void rejectsObjectsOutsideTheAllowlist() {
        Id accId = accountId(ACCOUNT_NAME);

        // Both cases guard the object allowlist specifically: neither name can be described, so
        // without the allowlist the describe call would throw a non-Aura exception and fail
        // this test. (A real object such as Account would be rejected later by the field-set
        // check, so it would not show the allowlist working.)
        Test.startTest();
        assertRejected(accId, 'AccountId', 'Not_A_Real_Object__c', FIELD_SET);
        assertRejected(accId, 'AccountId', null, FIELD_SET);
        Test.stopTest();
    }

    @IsTest
    static void rejectsUnknownFieldSet() {
        Test.startTest();
        assertRejected(accountId(ACCOUNT_NAME), 'AccountId', 'TransactionJournal', 'No_Such_Field_Set');
        Test.stopTest();
    }

    /**
     * ReferenceRecordId is on the controller's UsageSummary filter allowlist but is not a field
     * of UsageSummary, so only the field-exists check can reject it. Without that check the
     * dynamic query would fail with a QueryException instead of an AuraHandledException.
     * This relies on that dead allowlist entry, which is documented here, not pinned: removing
     * it from the controller would not fail this test's PRECONDITION. If it is removed, repoint
     * this test at another allowlisted-but-missing field or remove it.
     */
    @IsTest
    static void rejectsAllowlistedFilterFieldThatIsNotOnTheObject() {
        Id accId = accountId(ACCOUNT_NAME);
        Assert.isFalse(
            Schema.SObjectType.UsageSummary.fields.getMap().containsKey('ReferenceRecordId'),
            'PRECONDITION: UsageSummary has no ReferenceRecordId field, so only the field-exists check can reject it'
        );
        // The controller checks the field set first; it must exist so the field-exists check is the one that rejects.
        usageFieldSet(UsageSummary.SObjectType);

        Test.startTest();
        assertRejected(accId, 'ReferenceRecordId', 'UsageSummary', FIELD_SET);
        Test.stopTest();
    }

    @IsTest
    static void rejectsRealFieldsThatAreNotAllowlistedFilters() {
        Id accId = accountId(ACCOUNT_NAME);

        // Real fields that are not allowed filters for their object. CreatedById would widen the
        // scope beyond one Account or Asset; the others are simply not offered as filters. Each
        // exists on its object, so the allowlist (not the field-exists check) is what rejects it.
        Assert.isTrue(Schema.SObjectType.TransactionJournal.fields.getMap().containsKey('CreatedById'),
            'PRECONDITION: TransactionJournal.CreatedById exists');
        Assert.isTrue(Schema.SObjectType.TransactionJournal.fields.getMap().containsKey('UsageResourceId'),
            'PRECONDITION: TransactionJournal.UsageResourceId exists');
        Assert.isTrue(Schema.SObjectType.UsageSummary.fields.getMap().containsKey('Status'),
            'PRECONDITION: UsageSummary.Status exists');
        Assert.isTrue(
            Schema.SObjectType.UsageBillingPeriodItem.fields.getMap().containsKey('UsageEntitlementBucketId'),
            'PRECONDITION: UsageBillingPeriodItem.UsageEntitlementBucketId exists'
        );
        // The controller checks the field set first; each must exist so the allowlist is the check that rejects.
        usageFieldSet(TransactionJournal.SObjectType);
        usageFieldSet(UsageSummary.SObjectType);
        usageFieldSet(UsageBillingPeriodItem.SObjectType);

        Test.startTest();
        assertRejected(UserInfo.getUserId(), 'CreatedById', 'TransactionJournal', FIELD_SET);
        assertRejected(accId, 'UsageResourceId', 'TransactionJournal', FIELD_SET);
        assertRejected(accId, 'Status', 'UsageSummary', FIELD_SET);
        assertRejected(accId, 'UsageEntitlementBucketId', 'UsageBillingPeriodItem', FIELD_SET);
        Test.stopTest();
    }
}
