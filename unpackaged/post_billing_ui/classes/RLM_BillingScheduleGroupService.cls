/**
 * Service for the "Create Billing Schedule Group" screen-action modal
 * (rlmBillingScheduleGroupModal) on Account.
 *
 * Provides the picklist/lookup option queries the modal hydrates with, plus the
 * context-aware create path that generates a BillingScheduleGroup (+ BillingSchedule).
 *
 * The create path (createBillingScheduleGroupAndScheduleViaAPI) invokes the
 * standard "Create Standalone Billing Schedules" action
 * (createBillingSchedulesFromTrxn) NATIVELY via Invocable.Action — no HTTP
 * self-callout, no Visualforce session scraping, no Remote Site Setting. This
 * mirrors the native-ConnectApi decision made for the refund button. The action
 * is asynchronous: it returns requestId + statusUrl (AsyncOperationTracker),
 * which are surfaced back to the LWC.
 *
 * The standard context definition (StandaloneBillingContext__stdctx) and its
 * read/save context mappings (TransactionMapping / BSGEntitiesMapping) are
 * platform-provided with the Revenue Cloud Billing license — they are not custom
 * artifacts and require no deployment.
 */
public with sharing class RLM_BillingScheduleGroupService {
    @TestVisible
    private static final String CONTEXT_DEFINITION_NAME = 'StandaloneBillingContext__stdctx';
    @TestVisible
    private static final String READ_CONTEXT_MAPPING_NAME = 'TransactionMapping';
    @TestVisible
    private static final String SAVE_CONTEXT_MAPPING_NAME = 'BSGEntitiesMapping';

    // Test seam: when set in a test context, the native action invoke is
    // short-circuited with these outputs so the build/parse paths are covered
    // without enqueuing a real async billing-schedule job.
    @TestVisible
    private static Map<String, Object> mockActionOutputs = null;

    public class LegalEntityOption {
        @AuraEnabled public Id id;
        @AuraEnabled public String name;

        public LegalEntityOption(Id id, String name) {
            this.id = id;
            this.name = name;
        }
    }

    public class TaxTreatmentOption {
        @AuraEnabled public Id id;
        @AuraEnabled public String name;

        public TaxTreatmentOption(Id id, String name) {
            this.id = id;
            this.name = name;
        }
    }

    public class PicklistOption {
        @AuraEnabled public String label;
        @AuraEnabled public String value;

        public PicklistOption(String label, String value) {
            this.label = label;
            this.value = value;
        }
    }

    public class CreateResult {
        @AuraEnabled public Id billingScheduleGroupId;
        @AuraEnabled public Id billingScheduleId;
        @AuraEnabled public Id captureId;
        @AuraEnabled public String requestId;
        @AuraEnabled public String statusUrl;
        @AuraEnabled public String apiResponse;
    }

    public class AccountInfo {
        @AuraEnabled public String accountName;
        @AuraEnabled public Id billingAccountId;
        @AuraEnabled public String billingAccountName;
        @AuraEnabled public String billingCity;

        public AccountInfo(String accountName, Id billingAccountId, String billingAccountName, String billingCity) {
            this.accountName = accountName;
            this.billingAccountId = billingAccountId;
            this.billingAccountName = billingAccountName;
            this.billingCity = billingCity;
        }
    }

    public class ProductOption {
        @AuraEnabled public Id id;
        @AuraEnabled public String name;

        public ProductOption(Id id, String name) {
            this.id = id;
            this.name = name;
        }
    }

    @AuraEnabled(cacheable=true)
    public static AccountInfo getAccountBillingInfo(Id accountId) {
        if (accountId == null) {
            throw new AuraHandledException('Account Id is required.');
        }

        List<Account> accounts = [SELECT Id, Name FROM Account WHERE Id = :accountId WITH USER_MODE LIMIT 1];
        if (accounts.isEmpty()) {
            throw new AuraHandledException('Account not found.');
        }
        Account acc = accounts[0];

        List<BillingAccount> billingAccounts = [
            SELECT Id, Name, Account.BillingCity
            FROM BillingAccount
            WHERE AccountId = :accountId
            WITH USER_MODE
            LIMIT 1
        ];

        if (billingAccounts.isEmpty()) {
            return new AccountInfo(acc.Name, null, null, null);
        }

        BillingAccount ba = billingAccounts[0];
        String city = ba.Account != null ? ba.Account.BillingCity : null;
        return new AccountInfo(acc.Name, ba.Id, ba.Name, city);
    }

    @AuraEnabled(cacheable=true)
    public static List<ProductOption> getProducts() {
        List<ProductOption> results = new List<ProductOption>();
        for (Product2 prod : [
            SELECT Id, Name
            FROM Product2
            WHERE IsActive = true
            AND Family = 'Software'
            WITH USER_MODE
            ORDER BY Name
            LIMIT 200
        ]) {
            results.add(new ProductOption(prod.Id, prod.Name));
        }
        return results;
    }

    @AuraEnabled(cacheable=true)
    public static List<LegalEntityOption> getLegalEntities() {
        List<LegalEntityOption> results = new List<LegalEntityOption>();
        for (LegalEntity le : [SELECT Id, Name FROM LegalEntity WITH USER_MODE ORDER BY Name]) {
            results.add(new LegalEntityOption(le.Id, le.Name));
        }
        return results;
    }

    @AuraEnabled(cacheable=true)
    public static List<TaxTreatmentOption> getTaxTreatments() {
        List<TaxTreatmentOption> results = new List<TaxTreatmentOption>();
        for (TaxTreatment tt : [SELECT Id, Name FROM TaxTreatment WITH USER_MODE ORDER BY Name]) {
            results.add(new TaxTreatmentOption(tt.Id, tt.Name));
        }
        return results;
    }

    private static List<PicklistOption> getPicklistOptions(String sobjectApi, String fieldApi) {
        Schema.SObjectType objType = Schema.getGlobalDescribe().get(sobjectApi);
        if (objType == null) {
            return new List<PicklistOption>();
        }

        Map<String, Schema.SObjectField> fields = objType.getDescribe().fields.getMap();
        if (!fields.containsKey(fieldApi)) {
            return new List<PicklistOption>();
        }

        Schema.DescribeFieldResult dfr = fields.get(fieldApi).getDescribe();
        List<Schema.PicklistEntry> entries = dfr.getPicklistValues();

        List<PicklistOption> options = new List<PicklistOption>();
        for (Schema.PicklistEntry pe : entries) {
            options.add(new PicklistOption(pe.getLabel(), pe.getValue()));
        }
        return options;
    }

    @AuraEnabled(cacheable=true)
    public static List<PicklistOption> getBillingScheduleBillingTermUnitOptions() {
        List<PicklistOption> options = getPicklistOptions('BillingSchedule', 'BillingTermUnit');
        if (!options.isEmpty()) return options;

        return new List<PicklistOption>{
            new PicklistOption('Month', 'Month'),
            new PicklistOption('Day', 'Day'),
            new PicklistOption('OneTime', 'OneTime')
        };
    }

    @AuraEnabled(cacheable=true)
    public static List<PicklistOption> getPricingTermUnitOptions() {
        List<PicklistOption> options = getPicklistOptions('BillingSchedule', 'PricingTermUnit');
        if (!options.isEmpty()) return options;

        return new List<PicklistOption>{
            new PicklistOption('Annual', 'Annual'),
            new PicklistOption('Months', 'Months')
        };
    }

    /**
     * Creates BillingScheduleGroup and BillingSchedule via the standard Create
     * Standalone Billing Schedules action (createBillingSchedulesFromTrxn),
     * invoked natively. Asynchronous: returns requestId + statusUrl.
     */
    @AuraEnabled
    public static CreateResult createBillingScheduleGroupAndScheduleViaAPI(
        Id billingAccountId,
        String billingTermUnitPicklist,
        Integer billingTerm,
        String billingTypePicklistTiming,
        Decimal quantity,
        Id legalEntityId,
        Id taxTreatmentId,
        String currencyIsoCode,
        Decimal unitPrice,
        Decimal totalPrice,
        String billingCity,
        Id productId,
        String productName,
        Date startDate,
        Integer billingDayOfMonth,
        Integer billingStartMonth,
        String termSetting,
        Date endDate
    ) {
        if (billingAccountId == null) {
            throw new AuraHandledException('Billing account is required.');
        }

        List<BillingAccount> billingAccounts = [
            SELECT Id, AccountId
            FROM BillingAccount
            WHERE Id = :billingAccountId
            WITH USER_MODE
            LIMIT 1
        ];

        if (billingAccounts.isEmpty()) {
            throw new AuraHandledException('Billing Account not found.');
        }

        Id accountId = billingAccounts[0].AccountId;

        if (accountId == null) {
            List<AccountBillingAccount> accountBillingAccounts = [
                SELECT AccountId, BillingAccountId
                FROM AccountBillingAccount
                WHERE BillingAccountId = :billingAccountId
                WITH USER_MODE
                LIMIT 1
            ];

            if (!accountBillingAccounts.isEmpty()) {
                accountId = accountBillingAccounts[0].AccountId;
            }
        }

        if (accountId == null) {
            throw new AuraHandledException('No Account associated with this Billing Account.');
        }
        if (String.isBlank(billingTermUnitPicklist)) {
            throw new AuraHandledException('Billing term unit is required.');
        }
        if (quantity == null || quantity < 0) {
            throw new AuraHandledException('Quantity must be zero or greater.');
        }
        if (legalEntityId == null) {
            throw new AuraHandledException('Legal entity is required.');
        }
        if (taxTreatmentId == null) {
            throw new AuraHandledException('Tax Treatment is required.');
        }
        if (String.isBlank(currencyIsoCode)) {
            throw new AuraHandledException('Currency is required.');
        }
        if (unitPrice == null || unitPrice < 0) {
            throw new AuraHandledException('Unit Price must be zero or greater.');
        }
        if (String.isBlank(billingCity)) {
            throw new AuraHandledException('Billing City is required.');
        }
        if (productId == null) {
            throw new AuraHandledException('Product is required.');
        }
        if (startDate == null) {
            throw new AuraHandledException('Start Date is required.');
        }
        if (billingDayOfMonth == null || billingDayOfMonth < 1 || billingDayOfMonth > 31) {
            throw new AuraHandledException('Billing Day of Month must be between 1 and 31.');
        }
        if (billingStartMonth == null || billingStartMonth < 1 || billingStartMonth > 12) {
            throw new AuraHandledException('Billing Start Month must be between 1 and 12.');
        }

        String transactionDetailsJson = buildTransactionDetailsJson(
            accountId, billingAccountId, billingTermUnitPicklist, quantity, legalEntityId,
            taxTreatmentId, currencyIsoCode, unitPrice, totalPrice, billingCity, productId,
            productName, startDate, billingDayOfMonth, billingStartMonth, termSetting, endDate
        );

        Map<String, Object> outputs = invokeStandaloneBillingScheduleCreate(transactionDetailsJson);
        return parseCreateResult(outputs);
    }

    /**
     * Builds the transactionDetails JSON string consumed by the standard action.
     */
    @TestVisible
    private static String buildTransactionDetailsJson(
        Id accountId,
        Id billingAccountId,
        String billingTermUnitPicklist,
        Decimal quantity,
        Id legalEntityId,
        Id taxTreatmentId,
        String currencyIsoCode,
        Decimal unitPrice,
        Decimal totalPrice,
        String billingCity,
        Id productId,
        String productName,
        Date startDate,
        Integer billingDayOfMonth,
        Integer billingStartMonth,
        String termSetting,
        Date endDate
    ) {
        String transactionId = 'txn_' + String.valueOf(System.currentTimeMillis());

        String sellingModelType;
        if (termSetting == 'Termed') {
            sellingModelType = 'TermDefined';
        } else if (String.isNotBlank(termSetting)) {
            sellingModelType = termSetting;
        } else {
            sellingModelType = 'Evergreen';
        }

        String formattedStartDate = formatIsoDate(startDate);

        Map<String, Object> transactionData = new Map<String, Object>{
            'TransactionId__std' => transactionId,
            'SellingModelType__std' => sellingModelType,
            'ProductId__std' => productId,
            'ProductName__std' => productName,
            'StartDate__std' => formattedStartDate,
            'PeriodBoundary__std' => 'Anniversary',
            'BillingDayOfMonth__std' => billingDayOfMonth,
            'BillingStartMonth__std' => billingStartMonth,
            'UnitPrice__std' => unitPrice,
            'Quantity__std' => quantity,
            'TaxTreatmentId__std' => taxTreatmentId,
            'AccountId__std' => accountId,
            'BillingProfileId__std' => billingAccountId,
            'BillingCity__std' => billingCity,
            'BillingTermUnit__std' => billingTermUnitPicklist,
            'BillingActionType__std' => 'Add',
            'CurrencyIsoCode__std' => currencyIsoCode,
            // TotalPrice__std is Required for OneTime, Evergreen, AND TermDefined
            // new-sale transactions (Create Standalone Billing Schedules contract),
            // so it must be sent for every selling model — not just Termed.
            'TotalPrice__std' => totalPrice
        };

        // EndDate applies only to a fixed-term (TermDefined) schedule; OneTime and
        // Evergreen have no end date.
        if (termSetting == 'Termed' && endDate != null) {
            transactionData.put('EndDate__std', formatIsoDate(endDate));
        }

        Map<String, Object> transactionWrapper = new Map<String, Object>{
            'Transaction' => new List<Object>{ transactionData }
        };
        return JSON.serialize(transactionWrapper);
    }

    @TestVisible
    private static String formatIsoDate(Date d) {
        return String.valueOf(d.year()) + '-' +
            String.valueOf(d.month()).leftPad(2, '0') + '-' +
            String.valueOf(d.day()).leftPad(2, '0');
    }

    /**
     * Invokes the standard Create Standalone Billing Schedules action natively.
     * Returns the action's output parameters (requestId, statusUrl).
     */
    @TestVisible
    private static Map<String, Object> invokeStandaloneBillingScheduleCreate(String transactionDetailsJson) {
        if (Test.isRunningTest() && mockActionOutputs != null) {
            return mockActionOutputs;
        }

        Invocable.Action action = Invocable.Action.createStandardAction('createBillingSchedulesFromTrxn');
        action.setInvocationParameter('transactionDetails', transactionDetailsJson);
        action.setInvocationParameter('contextDefinitionName', CONTEXT_DEFINITION_NAME);
        action.setInvocationParameter('readContextMappingName', READ_CONTEXT_MAPPING_NAME);
        action.setInvocationParameter('saveContextMappingName', SAVE_CONTEXT_MAPPING_NAME);

        List<Invocable.Action.Result> results = action.invoke();
        if (results.isEmpty()) {
            throw new AuraHandledException('Create Standalone Billing Schedules action returned no result.');
        }

        Invocable.Action.Result res = results[0];
        if (!res.isSuccess()) {
            List<String> messages = new List<String>();
            for (Invocable.Action.Error err : res.getErrors()) {
                messages.add(err.getCode() + ': ' + err.getMessage());
            }
            throw new AuraHandledException(
                'Create Standalone Billing Schedules action failed: ' + String.join(messages, '; ')
            );
        }
        return res.getOutputParameters();
    }

    /**
     * Maps the standard action's output parameters into a CreateResult. The action
     * is asynchronous, so requestId/statusUrl are the primary outputs; the BSG and
     * schedule ids are read defensively if a synchronous variant ever returns them.
     */
    @TestVisible
    private static CreateResult parseCreateResult(Map<String, Object> outputs) {
        CreateResult result = new CreateResult();
        if (outputs == null) {
            return result;
        }
        result.apiResponse = JSON.serialize(outputs);
        if (outputs.get('requestId') != null) {
            result.requestId = String.valueOf(outputs.get('requestId'));
        }
        if (outputs.get('statusUrl') != null) {
            result.statusUrl = String.valueOf(outputs.get('statusUrl'));
        }
        if (outputs.containsKey('billingScheduleGroupId') && outputs.get('billingScheduleGroupId') != null) {
            result.billingScheduleGroupId = (Id) outputs.get('billingScheduleGroupId');
        }
        if (outputs.containsKey('billingScheduleId') && outputs.get('billingScheduleId') != null) {
            result.billingScheduleId = (Id) outputs.get('billingScheduleId');
        } else if (outputs.containsKey('billingScheduleIds')) {
            Object idsObj = outputs.get('billingScheduleIds');
            if (idsObj instanceof List<Object> && !((List<Object>) idsObj).isEmpty()) {
                result.billingScheduleId = (Id) ((List<Object>) idsObj)[0];
            }
        }
        return result;
    }
}
