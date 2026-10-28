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
 * each persona group is one of these sets plus RLM_BillingAccountFieldAccess.
 *
 * READS lists what the controllers select or filter on, per object. Keep it in step with
 * the controllers: a new USER_MODE field there belongs here, and in the permission set.
 * Left out on purpose: Task (access follows the related record; no object permission
 * exists), DatedConversionRate (advanced currency management only), InvoiceBatchRun (the
 * batch monitor's page, which the role grants), and DisputeItem (the write check covers it).
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
        'Account' => new List<String>{ 'Name', 'BillingCity', 'CurrencyIsoCode' },
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
        'BillingAccount' => new List<String>{ 'Name', 'AccountId' },
        'AccountBillingAccount' => new List<String>{ 'AccountId', 'BillingAccountId' },
        'UsageResource' => new List<String>{ 'Name' },
        'Product2' => new List<String>{ 'Name', 'IsActive', 'Family' },
        'LegalEntity' => new List<String>{ 'Name' },
        'TaxTreatment' => new List<String>{ 'Name' },
        'UnitOfMeasure' => new List<String>{ 'Name' },
        'Asset' => new List<String>{ 'Name' },
        'AssetStatePeriod' => new List<String>{ 'AssetId', 'StartDate' },
        'AssetStatePeriodAttribute' => new List<String>{ 'AssetStatePeriodId', 'AttributeName', 'AttributeValue' },
        'TransactionJournal' => new List<String>{
            'Name', 'Credit', 'Debit', 'CurrencyIsoCode', 'CreditGeneralLedgerAccountId',
            'DebitGeneralLedgerAccountId', 'ReferenceTransactionRecordId', 'CreatedDate'
        },
        'GeneralLedgerAccount' => new List<String>{ 'Name' },
        // Multi-currency orgs only; checked only there.
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
    // reads. RLM_BillingUI doesn't grant InvoiceBatchRun: its read pulls in the batch
    // scheduler and run-criteria objects.
    private static final Map<String, List<String>> BATCH_RUN_READS = new Map<String, List<String>>{
        'Invoice' => new List<String>{ 'InvoiceBatchRunId' }
    };
    // Collections Console and Dashboard: the collections objects need the Billing Advanced
    // license and its Collections and Recovery Specialist set.
    private static final Map<String, List<String>> COLLECTIONS_READS = new Map<String, List<String>>{
        'PaymentSchedule' => new List<String>{ 'CollectionPlanItemId' },
        'CollectionPlan' => new List<String>{
            'Name', 'AccountId', 'Duedate', 'TotalInvoiceBalance', 'OwnerId', 'ClosedDate',
            'CreatedDate', 'DaysPastDue'
        },
        'CollectionPlanItem' => new List<String>{ 'InvoiceId', 'CollectionPlanId' }
    };

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

    private static List<String> unreadable(Map<String, List<String>> manifest) {
        Boolean multiCurrency = UserInfo.isMultiCurrencyOrganization();
        List<String> failures = new List<String>();
        for (String obj : manifest.keySet()) {
            if (obj == 'CurrencyType' && !multiCurrency) {
                continue;
            }
            List<String> fields = new List<String>{ 'Id' };
            for (String f : manifest.get(obj)) {
                if (f != 'CurrencyIsoCode' || multiCurrency) {
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
