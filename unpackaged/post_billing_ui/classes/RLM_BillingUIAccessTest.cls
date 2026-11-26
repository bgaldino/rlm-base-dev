/**
 * Proves that each billing role, given RLM_BillingUI, can run every USER_MODE read the
 * Billing UI controllers make, and the writes that role is meant to make.
 *
 * Admin tests prove nothing here: System Administrator bypasses object and field access.
 * So each check runs as a Minimum Access user holding the Billing permission set license,
 * one managed billing role set and RLM_BillingUI, and runs the reads as USER_MODE queries.
 * A query the user may not run throws; every failure is collected and reported together.
 *
 * The role set is required, not optional: the billing objects also need the user
 * permissions it carries (Billing Access, Milestone Billing Access and others), which
 * RLM_BillingUI deliberately does not grant. With the license and RLM_BillingUI alone,
 * BillingScheduleGroup, Dispute, CollectionPlan and most other billing objects read as
 * "not supported". The managed sets are used rather than the RLM persona groups because
 * they ship with the Billing license, so the check runs whether or not `personas` is on;
 * each persona group is one of these sets plus RLM_BillingAccountFieldAccess, and the Admin and
 * Operations groups also include RLM_BillingInvoiceDocuments (todo 292).
 *
 * READS lists what the controllers select or filter on, per object. Keep it in step with
 * the controllers: a new USER_MODE field there belongs here, and in the permission set.
 * Task has no object permission (access follows the related record), so only its permissionable
 * fields are listed. Left out on purpose: DatedConversionRate (advanced currency management only), InvoiceBatchRun (the
 * batch monitor's page: the managed Billing Operations set reads it, the managed Billing Admin
 * set does not, and the RLM_Billing_Admin and RLM_Billing_Operations groups grant it through
 * RLM_BillingInvoiceDocuments, todo 292), and DisputeItem (the write check covers it).
 */
@IsTest
private class RLM_BillingUIAccessTest {

    private static final String CREDIT_MEMO_OPERATIONS = 'RevenueLifecycleManagementBillingCreditMemoOperations';
    private static final List<String> BILLING_ONLY = new List<String>{ RLM_BillingUITestUsers.BILLING_PSL };
    private static final List<String> ROLE_SETS = new List<String>{
        'RevenueLifecycleManagementBillingAdmin',
        'RevenueLifecycleManagementBillingOperations',
        CREDIT_MEMO_OPERATIONS
    };

    private static final Map<String, List<String>> READS = new Map<String, List<String>>{
        'Account' => new List<String>{ 'Name', 'BillingCity', 'ShippingCity', 'CurrencyIsoCode' },
        // The create path picks the treatment for a legal entity, timing and currency (Create Billing Schedule Group).
        // BillingTreatmentItem has no object grant of its own: it is a master-detail child, so its read follows
        // BillingTreatment (the grant is dropped on deploy); this reads it to prove that.
        'BillingTreatment' => new List<String>{ 'Status', 'LegalEntityId', 'IsMilestoneBilling', 'ExcludeFromBilling', 'CurrencyIsoCode' },
        'BillingTreatmentItem' => new List<String>{ 'BillingTreatmentId', 'BillingType', 'Status', 'BillingTreatment.CurrencyIsoCode', 'BillingTreatment.CreatedDate' },
        'Contact' => new List<String>{ 'Name' },
        'Invoice' => new List<String>{
            'Balance', 'BillingAccountId', 'BillToContactId', 'BillingArrangementId',
            'BillingArrangementVerNumber', 'BillingProfileId', 'CorrelationIdentifier',
            'CurrencyIsoCode', 'DaysInvoiceOpen', 'DaysInvoiceOverdue', 'DocumentNumber',
            'DueDate', 'FullSettlementDate', 'InvoiceDate', 'InvoiceNumber',
            'NetPaymentsApplied', 'SettlementStatus', 'Status', 'TotalAmount', 'TotalAmountWithTax',
            // Relationship reads. BillingProfile is a BillingAccount.
            'BillingAccount.Name', 'BillingArrangement.Name', 'BillingProfile.Name'
        },
        'InvoiceLine' => new List<String>{
            'Name', 'Description', 'Balance', 'InvoiceId', 'Product2Id', 'BillingScheduleGroupId',
            'InvoiceLineStartDate', 'InvoiceLineEndDate', 'Quantity', 'UnitPrice', 'ChargeAmount',
            'TaxAmount', 'LineAmount', 'Type', 'UsageOverageQuantity', 'UnitOfMeasureId',
            'RLM_Charge_Type__c', 'RLM_Attributes__c'
        },
        'InvoiceLineTax' => new List<String>{ 'TaxName', 'TaxAmount', 'InvoiceLineId', 'CurrencyIsoCode' },
        'InvoiceLineRelationship' => new List<String>{ 'MainInvoiceLineId', 'AssociatedInvoiceLineId' },
        'BillingPeriodItem' => new List<String>{ 'InvoiceLineId', 'BillingPeriodStartDate', 'BillingPeriodEndDate' },
        'Payment' => new List<String>{ 'Balance', 'Type', 'AccountId', 'Status', 'CurrencyIsoCode' },
        'PaymentLineInvoice' => new List<String>{ 'PaymentId', 'InvoiceId', 'Amount', 'Type', 'HasBeenUnapplied' },
        'PaymentLineInvoiceLine' => new List<String>{ 'PaymentId', 'Amount', 'Type', 'UnappliedStatus', 'InvoiceLineId' },
        'PaymentSchedule' => new List<String>{ 'ReferenceEntityId' },
        'PaymentScheduleItem' => new List<String>{
            'PaymentScheduleItemNumber', 'Status', 'RequestedAmount', 'ProcessedAmount',
            'TargetPaymentProcessingDate', 'PaymentScheduleId', 'PaymentAccountId',
            'CurrencyIsoCode', 'PaymentId'
        },
        'Case' => new List<String>{ 'IsClosed', 'Type', 'AccountId', 'Subject', 'Description', 'CaseNumber', 'Reason', 'CreatedDate' },
        'Dispute' => new List<String>{
            'Status', 'DisputedAmount', 'InvoiceId', 'CaseId', 'DisputeType', 'DisputeSubtype',
            'Description', 'CurrencyIsoCode'
        },
        'DebitMemo' => new List<String>{
            'TotalAmount', 'TotalChargeAmount', 'AccountId', 'Status', 'InvoiceGenerationStatus', 'CurrencyIsoCode'
        },
        'CreditMemo' => new List<String>{ 'Balance', 'BillingAccountId', 'Status', 'CurrencyIsoCode' },
        'Refund' => new List<String>{ 'Balance', 'AccountId', 'Status', 'CurrencyIsoCode' },
        'BillingScheduleGroup' => new List<String>{
            'ProductName', 'Product2Id', 'ReferenceEntityId', 'StartDate', 'EndDate',
            'BillingTermUnit', 'BillingTerm', 'CurrencyIsoCode', 'TotalBilledAmount',
            'TotalPendingAmount', 'BillingType', 'BillingMethod', 'BillingAccountId',
            'BillingScheduleGroupNumber', 'AnchorProdtBillingSchdGrpId', 'BindingInstanceId',
            'BillingArrangementId', 'BillDayOfMonth', 'CancellationDate', 'BillingSuspensionDate',
            'BillingResumptionDate'
        },
        'BillingSchedule' => new List<String>{
            'BillingScheduleGroupId', 'BilledAmount', 'PendingAmount',
            'UsageResourceId', 'BillingScheduleNumber', 'Category', 'Status', 'Quantity',
            'TotalAmount', 'BillingPeriodAmount', 'UnitPrice', 'BillingScheduleStartDate',
            'BillingScheduleEndDate', 'NextBillingDate', 'BillingMethod', 'BillingType',
            'BillingTerm', 'BillingTermUnit', 'CreatedDate'
        },
        'BsgRelationship' => new List<String>{ 'MainBsgId', 'AssociatedBsgId', 'AssociatedBsgRole', 'AssociatedBsgPricing', 'MainBsgRole' },
        'BillingArrangement' => new List<String>{ 'Name', 'Status' },
        'BillingArrangementLine' => new List<String>{
            'BillingArrangementLineName', 'AccountId', 'BillingAccountId', 'BillingPercentage',
            'ShouldBillRemainder', 'BillingArrangementId'
        },
        // BillToContactId: the Create Billing Schedule Group modal and service check it before the action.
        'BillingAccount' => new List<String>{ 'Name', 'AccountId', 'IsDefaultBillingProfile', 'BillToContactId' },
        'AccountBillingAccount' => new List<String>{ 'AccountId', 'BillingAccountId' },
        'UsageResource' => new List<String>{ 'Name' },
        // Collections Dashboard plan tasks (todo 435): ActivityDate and WhatId are permissionable.
        'Task' => new List<String>{ 'Subject', 'Status', 'ActivityDate', 'WhatId' },
        'Product2' => new List<String>{ 'Name', 'IsActive', 'Family' },
        'LegalEntity' => new List<String>{ 'Name', 'Status' },
        'TaxTreatment' => new List<String>{ 'Name', 'Status', 'LegalEntityId' },
        'UnitOfMeasure' => new List<String>{ 'Name' },
        'AssetStatePeriod' => new List<String>{ 'AssetId', 'StartDate' },
        'AssetStatePeriodAttribute' => new List<String>{ 'AssetStatePeriodId', 'AttributeName', 'AttributeValue' },
        'TransactionJournal' => new List<String>{
            'Name', 'Credit', 'Debit', 'CurrencyIsoCode', 'CreditGeneralLedgerAccountId',
            'DebitGeneralLedgerAccountId', 'ReferenceTransactionRecordId', 'CreatedDate'
        },
        'GeneralLedgerAccount' => new List<String>{ 'Name' },
        // The module requires a multi-currency org. The check below skips CurrencyType and the
        // CurrencyIsoCode fields only so a run on a non-multi-currency org does not fail on fields
        // that do not exist there; that is not single-currency support.
        'CurrencyType' => new List<String>{ 'IsoCode', 'IsCorporate', 'IsActive', 'ConversionRate' }
    };

    // Reads that belong to one surface, which only some roles get. RLM_BillingUI grants the
    // objects; the user permissions or license that open them come with the role.
    // Milestone billing (BSG timeline and context panel): Milestone Billing Access.
    private static final Map<String, List<String>> MILESTONE_READS = new Map<String, List<String>>{
        'BillingSchedule' => new List<String>{ 'BillingMilestonePlanId' },
        'BillingMilestonePlan' => new List<String>{ 'Name', 'Status', 'Description', 'ReferenceItemAmount' },
        'BillingMilestonePlanItem' => new List<String>{
            'Name', 'Type', 'Percentage', 'FlatAmount', 'MilestoneType', 'MilestoneAmount',
            'CommencementDate', 'IsMilestoneAccomplished', 'Status', 'MilestoneAccomplishmentDate',
            'BillingMilestonePlanId'
        }
    };
    // Invoice Batch Run Monitor: it sits on the InvoiceBatchRun page, which Billing Operations
    // reads (Billing Admin does not; its persona group gets the read from RLM_BillingInvoiceDocuments).
    // RLM_BillingUI doesn't grant InvoiceBatchRun: its read pulls in the batch scheduler and
    // run-criteria objects.
    private static final Map<String, List<String>> BATCH_RUN_READS = new Map<String, List<String>>{
        'Invoice' => new List<String>{ 'InvoiceBatchRunId' }
    };
    // Collections Console and Dashboard: the collections objects need the Billing Advanced
    // license and its Collections and Recovery Specialist set.
    private static final Map<String, List<String>> COLLECTIONS_READS = new Map<String, List<String>>{
        'PaymentSchedule' => new List<String>{ 'CollectionPlanItemId' },
        'CollectionPlan' => new List<String>{
            'Name', 'AccountId', 'Duedate', 'TotalInvoiceBalance', 'OwnerId', 'ClosedDate',
            'CreatedDate', 'DaysPastDue', 'CurrencyIsoCode'
        },
        'CollectionPlanItem' => new List<String>{ 'InvoiceId', 'CollectionPlanId' },
        // The Collections Dashboard converts amounts at today's dated rates where there are any (todo 435).
        'DatedConversionRate' => new List<String>{ 'IsoCode', 'ConversionRate', 'StartDate', 'NextStartDate' }
    };

    // What the Collections Dashboard controller reads, for a collections user who holds RLM_CollectionsDashboard
    // instead of RLM_BillingUI (todo 435). DebitMemo is left out: it reads as "not supported" without the
    // Manage Debit Memos user permission, which a read-only collections role is not given (measured on
    // 264); collectionsUserCannotReadDebitMemos pins that.
    private static final Map<String, List<String>> DASHBOARD_READS = new Map<String, List<String>>{
        'Account' => new List<String>{ 'Name' },
        // The Critical list's bill-to contact names.
        'Contact' => new List<String>{ 'Name' },
        'CurrencyType' => new List<String>{ 'IsoCode', 'IsCorporate', 'IsActive', 'ConversionRate' },
        // Today's dated rates, where advanced currency management has the object.
        'DatedConversionRate' => new List<String>{ 'IsoCode', 'ConversionRate', 'StartDate', 'NextStartDate' },
        'Invoice' => new List<String>{
            'InvoiceNumber', 'Balance', 'TotalAmount', 'DueDate', 'BillingAccountId',
            'BillToContactId', 'Status', 'CurrencyIsoCode'
        },
        'PaymentSchedule' => new List<String>{ 'ReferenceEntityId' },
        'PaymentScheduleItem' => new List<String>{
            'Status', 'RequestedAmount', 'PaymentAccountId', 'CurrencyIsoCode', 'PaymentScheduleId',
            'TargetPaymentProcessingDate'
        },
        'CollectionPlan' => new List<String>{
            'Name', 'Duedate', 'TotalInvoiceBalance', 'AccountId', 'OwnerId', 'ClosedDate', 'CreatedDate', 'DaysPastDue',
            'CurrencyIsoCode'
        },
        'CollectionPlanItem' => new List<String>{ 'InvoiceId', 'CollectionPlanId' },
        'Task' => new List<String>{ 'Subject', 'Status', 'ActivityDate', 'WhatId' },
        'Case' => new List<String>{ 'CaseNumber', 'AccountId', 'Subject', 'Description', 'Reason', 'IsClosed', 'CreatedDate' },
        'Payment' => new List<String>{ 'Balance', 'Status', 'Type', 'AccountId', 'CurrencyIsoCode' }
    };
    private static final List<String> COLLECTIONS_USER_SETS = new List<String>{
        'BillingCollectionsAndRecoverySpecialist', 'RLM_CollectionsDashboard'
    };
    private static final List<String> COLLECTIONS_LICENSES = new List<String>{
        RLM_BillingUITestUsers.BILLING_PSL, RLM_BillingUITestUsers.BILLING_ADVANCED_PSL
    };

    // The collections user the dashboard is for, without RLM_BillingUI: every read the controller makes runs.
    @IsTest
    static void collectionsUserWithoutBillingUiCanRunTheDashboardReads() {
        User u = RLM_BillingUITestUsers.create(COLLECTIONS_USER_SETS, COLLECTIONS_LICENSES);
        List<String> failures;
        System.runAs(u) {
            failures = unreadable(DASHBOARD_READS);
        }
        Assert.isTrue(failures.isEmpty(),
            'Collections Dashboard reads a collections user cannot run. Grant them in RLM_CollectionsDashboard:\n'
            + String.join(failures, '\n'));
    }

    // RLM_CollectionsDashboard adds those reads: without it the same user cannot read cases, payments, task
    // dates or plan due dates. The collections user holds no RLM_CollectionsUI: that set ships with the
    // collections flag, which can be off while billing_ui (this bundle) is on.
    @IsTest
    static void collectionsUserWithoutTheDashboardSetCannotReadCasesOrPayments() {
        User u = RLM_BillingUITestUsers.create(
            new List<String>{ 'BillingCollectionsAndRecoverySpecialist' }, COLLECTIONS_LICENSES);
        List<String> failures;
        System.runAs(u) {
            failures = unreadable(new Map<String, List<String>>{
                'Case' => new List<String>{ 'Subject' },
                'Payment' => new List<String>{ 'Balance' },
                'Task' => new List<String>{ 'ActivityDate' },
                'CollectionPlan' => new List<String>{ 'Duedate' }
            });
        }
        Assert.areEqual(4, failures.size(), 'Each read comes from RLM_CollectionsDashboard: ' + failures);
    }

    // Debit memos need the Manage Debit Memos user permission, which a read-only collections role is not
    // given (owner decision): the dashboard shows the Debit Memos line as not available and the total
    // balance as excluding it. Pinned so a platform change that opens the read shows here.
    @IsTest
    static void collectionsUserCannotReadDebitMemos() {
        User u = RLM_BillingUITestUsers.create(COLLECTIONS_USER_SETS, COLLECTIONS_LICENSES);
        List<String> failures;
        System.runAs(u) {
            failures = unreadable(new Map<String, List<String>>{ 'DebitMemo' => new List<String>{ 'TotalAmount' } });
        }
        Assert.areEqual(1, failures.size(), 'DebitMemo read is refused for the collections user: ' + failures);
    }

    // One method per role: each runs a query per manifest object, so together they would
    // pass the 100-query limit.
    @IsTest
    static void billingAdminCanRunItsControllerReads() {
        assertReadable(new List<String>{ 'RevenueLifecycleManagementBillingAdmin' }, BILLING_ONLY,
            new List<Map<String, List<String>>>{ READS, MILESTONE_READS });
    }

    @IsTest
    static void billingOperationsCanRunItsControllerReads() {
        assertReadable(new List<String>{ 'RevenueLifecycleManagementBillingOperations' }, BILLING_ONLY,
            new List<Map<String, List<String>>>{ READS, MILESTONE_READS, BATCH_RUN_READS });
    }

    @IsTest
    static void creditMemoOperationsCanRunItsControllerReads() {
        assertReadable(new List<String>{ CREDIT_MEMO_OPERATIONS }, BILLING_ONLY,
            new List<Map<String, List<String>>>{ READS });
    }

    // A collections user works the Collections Console and Dashboard, which also read
    // invoices, payments and the rest of READS, so the collections set is checked on top
    // of a billing role rather than alone.
    @IsTest
    static void collectionsSpecialistCanRunItsControllerReads() {
        assertReadable(
            new List<String>{ 'RevenueLifecycleManagementBillingOperations', 'BillingCollectionsAndRecoverySpecialist' },
            new List<String>{ RLM_BillingUITestUsers.BILLING_PSL, RLM_BillingUITestUsers.BILLING_ADVANCED_PSL },
            new List<Map<String, List<String>>>{ READS, COLLECTIONS_READS });
    }

    private static void assertReadable(List<String> roleSets, List<String> licenses,
            List<Map<String, List<String>>> manifests) {
        String role = String.join(roleSets, ' + ');
        User u = billingUser(roleSets, licenses);
        List<String> failures = new List<String>();
        System.runAs(u) {
            for (Map<String, List<String>> manifest : manifests) {
                failures.addAll(unreadable(manifest));
            }
        }
        Assert.isTrue(failures.isEmpty(),
            'Billing UI reads ' + role + ' cannot run with RLM_BillingUI. Grant them in '
            + 'RLM_BillingUI:\n' + String.join(failures, '\n'));
    }

    // Saving line attributes (Invoice Product Summary) is open to every role; approving a
    // dispute amount (Dispute Details) is not part of credit memo operations. These grants
    // come from the role sets, not RLM_BillingUI: they are role scope.
    @IsTest
    static void everyBillingRoleCanMakeItsBillingUiWrites() {
        List<String> failures = new List<String>();
        for (String role : ROLE_SETS) {
            System.runAs(billingUser(new List<String>{ role }, BILLING_ONLY)) {
                if (!Schema.SObjectType.Invoice.isUpdateable()) {
                    failures.add(role + ': Invoice edit (saving InvoiceLine attributes needs it)');
                }
                // Describe omits a field the user has no access to, so a missing entry is a failure too.
                Schema.SObjectField attributes = Schema.SObjectType.InvoiceLine.fields.getMap().get('RLM_Attributes__c');
                if (attributes == null || !attributes.getDescribe().isUpdateable()) {
                    failures.add(role + ': InvoiceLine.RLM_Attributes__c edit');
                }
                Schema.SObjectField approved = Schema.getGlobalDescribe().get('DisputeItem')
                    .getDescribe().fields.getMap().get('ApprovedAmount');
                if (role != CREDIT_MEMO_OPERATIONS && (approved == null || !approved.getDescribe().isUpdateable())) {
                    failures.add(role + ': DisputeItem.ApprovedAmount edit');
                }
            }
        }
        Assert.isTrue(failures.isEmpty(), 'Billing role write access missing:\n' + String.join(failures, '\n'));
    }

    // Reading AssetStatePeriodAttribute in user mode (the product summary's attribute columns and
    // its line attribute save) needs the Core CPQ User permission. Without it the platform throws
    // ExternalObjectException from its attribute query, but only when attribute rows exist, which a
    // unit test cannot create (READS above passes either way). Measured on a 264 org as a billing
    // operations user: the query failed with the billing license alone, and with read on every
    // attribute object; it succeeded once CoreCPQUser was granted, with or without the Revenue Cloud
    // User license. So the grant is pinned here.
    // The permission is in its own set, RLM_BillingUIAssetAttributes, because it needs a license
    // that allows it: in RLM_BillingUI it would make that set unassignable to a user without one.
    @IsTest
    static void assetAttributeSetGrantsCoreCpqUserAndBillingUiDoesNot() {
        Map<String, Boolean> coreCpqBySet = new Map<String, Boolean>();
        for (PermissionSet ps : [SELECT Name, PermissionsCoreCPQUser FROM PermissionSet
                                 WHERE Name IN ('RLM_BillingUI', 'RLM_BillingUIAssetAttributes')]) {
            coreCpqBySet.put(ps.Name, ps.PermissionsCoreCPQUser);
        }
        Assert.isTrue(coreCpqBySet.get('RLM_BillingUIAssetAttributes') == true,
            'RLM_BillingUIAssetAttributes grants Core CPQ User, which the user-mode asset attribute query needs');
        Assert.isTrue(coreCpqBySet.get('RLM_BillingUI') == false,
            'RLM_BillingUI does not carry Core CPQ User, so a user whose license does not allow it can still be given the set');
    }

    // The asset attribute set is assignable with the Billing license alone: a set that carries
    // CoreCPQUser needs a license that allows it, and the Billing license is the one billing users have.
    @IsTest
    static void assetAttributeSetIsAssignableWithTheBillingLicense() {
        User u = billingUser(new List<String>{ 'RLM_BillingUIAssetAttributes' }, BILLING_ONLY);
        Assert.areEqual(1, [SELECT COUNT() FROM PermissionSetAssignment
                            WHERE AssigneeId = :u.Id AND PermissionSet.Name = 'RLM_BillingUIAssetAttributes'],
            'A Billing-licensed user can be given RLM_BillingUIAssetAttributes');
    }

    // Without a license that allows CoreCPQUser the set cannot be assigned at all, which is why the
    // permission is kept out of RLM_BillingUI. The test user holds only the Salesforce user license.
    @IsTest
    static void assetAttributeSetIsNotAssignableWithoutALicenseThatAllowsIt() {
        StatusCode refused;
        try {
            RLM_BillingUITestUsers.create(new List<String>{ 'RLM_BillingUIAssetAttributes' }, new List<String>());
        } catch (DmlException e) {
            refused = e.getDmlType(0);
        }
        Assert.areEqual(StatusCode.FIELD_INTEGRITY_EXCEPTION, refused,
            'RLM_BillingUIAssetAttributes needs a license that allows Core CPQ User');
    }

    private static List<String> unreadable(Map<String, List<String>> manifest) {
        Boolean multiCurrency = UserInfo.isMultiCurrencyOrganization();
        List<String> failures = new List<String>();
        for (String obj : manifest.keySet()) {
            if ((obj == 'CurrencyType' || obj == 'DatedConversionRate') && !multiCurrency) {
                continue;
            }
            List<String> fields = new List<String>{ 'Id' };
            for (String f : manifest.get(obj)) {
                if (!f.endsWith('CurrencyIsoCode') || multiCurrency) {
                    fields.add(f);
                }
            }
            try {
                Database.query('SELECT ' + String.join(fields, ', ') + ' FROM ' + obj + ' LIMIT 1',
                    AccessLevel.USER_MODE);
            } catch (Exception e) {
                failures.add(obj + ': ' + e.getMessage().substringBefore(' If you are attempting'));
            }
        }
        return failures;
    }

    private static User billingUser(List<String> roleSets, List<String> licenses) {
        List<String> sets = new List<String>(roleSets);
        sets.add('RLM_BillingUI');
        return RLM_BillingUITestUsers.create(sets, licenses);
    }
}
