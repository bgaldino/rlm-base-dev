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

    @TestVisible
    private static final String CREATE_FAILED_MESSAGE =
        'The billing schedule could not be created. Check the values entered, then try again; '
        + 'if it continues, contact your administrator.';

    // A refused USER_MODE read names the object and field, so the user gets a sentence naming what
    // could not be read; the query error goes to the debug log and stays on the cause.
    @TestVisible
    private static AuraHandledException readRefused(String what, QueryException cause) {
        return RLM_AuraErrors.failed(
            'You do not have access to read ' + what + ' this screen needs. Contact your administrator.',
            'RLM_BillingScheduleGroupService read of ' + what + ' refused', cause);
    }

    @TestVisible
    private static final String NO_BILLING_LINK_ACCESS_MESSAGE =
        'You do not have access to read the links between this Account and its billing accounts '
        + '(Account Billing Account), so the billing account cannot be resolved. '
        + 'Ask an administrator to grant it, for example through the RLM Billing UI permission set.';

    // Throws for a missing id or an account the caller cannot read: there is no account name to show
    // then, and the modal surfaces the message as an error toast (its account-info wire handler), so
    // the header is not left blank without a reason. An account with no billing account still returns
    // an AccountInfo carrying the account name; the modal blocks Create until a billing account exists.
    @AuraEnabled(cacheable=true)
    public static AccountInfo getAccountBillingInfo(Id accountId) {
        if (accountId == null) {
            throw RLM_AuraErrors.handled('Account Id is required.');
        }

        List<Account> accounts;
        try {
            accounts = [SELECT Id, Name FROM Account WHERE Id = :accountId WITH USER_MODE LIMIT 1];
        } catch (QueryException qe) {
            throw readRefused('the account', qe);
        }
        if (accounts.isEmpty()) {
            throw RLM_AuraErrors.handled('Account not found.');
        }
        Account acc = accounts[0];

        // Deterministic pick: the account's default billing profile first, then oldest first. A billing
        // account linked to the account only through AccountBillingAccount is resolved too, as the
        // create path does.
        // Account.BillingCity is a component of the compound BillingAddress. Measured on a 264 org:
        // describe reports BillingCity permissionable, yet no permission set carries a FieldPermissions
        // row for Account.BillingCity, while 121 carry one for Account.BillingAddress. So the compound is
        // the grant that exists and RLM_BillingUI holds it; this repo does not grant the component, and
        // it does not insert a component row in tests. That a user holding only the compound grant reads
        // BillingCity here is inferred, not measured; RLM_BillingUIAccessTest READS asserts it where
        // the set is deployed.
        // BillingAccount.IsDefaultBillingProfile in ORDER BY adds no field-level-security dependency:
        // measured on a 264 org, describe reports it not permissionable and a FieldPermissions row for
        // it is refused, so USER_MODE does not check it and no permission set can grant it.
        List<BillingAccount> billingAccounts;
        try {
            billingAccounts = [
                SELECT Id, Name, Account.BillingCity
                FROM BillingAccount
                WHERE AccountId = :accountId
                WITH USER_MODE
                ORDER BY IsDefaultBillingProfile DESC, CreatedDate, Id
                LIMIT 1
            ];
        } catch (QueryException qe) {
            throw readRefused('the billing accounts', qe);
        }

        if (billingAccounts.isEmpty()) {
            List<AccountBillingAccount> links;
            try {
                // AccountBillingAccount.IsDefaultBillingAccount is deprecated on 264: the platform
                // refuses to set it to true ("use default field on billing account"), so a link is
                // never the default and ordering by it picks nothing. A billing account with no
                // AccountId cannot be a default billing profile either, so the oldest link wins.
                links = [
                    SELECT BillingAccountId
                    FROM AccountBillingAccount
                    WHERE AccountId = :accountId
                    WITH USER_MODE
                    ORDER BY CreatedDate, Id
                    LIMIT 1
                ];
            } catch (QueryException qe) {
                // An access failure is not "no billing account": reporting it as one would send
                // the user to create a billing account that already exists and hide the missing
                // grant. Say which access is missing.
                throw RLM_AuraErrors.failed(NO_BILLING_LINK_ACCESS_MESSAGE,
                    'RLM_BillingScheduleGroupService read of AccountBillingAccount refused', qe);
            }
            if (!links.isEmpty()) {
                // Same BillingCity read as above: covered by the compound BillingAddress grant (see there).
                try {
                    billingAccounts = [
                        SELECT Id, Name, Account.BillingCity
                        FROM BillingAccount
                        WHERE Id = :links[0].BillingAccountId
                        WITH USER_MODE
                        LIMIT 1
                    ];
                } catch (QueryException qe) {
                    throw readRefused('the billing accounts', qe);
                }
            }
        }

        if (billingAccounts.isEmpty()) {
            return new AccountInfo(acc.Name, null, null, null);
        }

        BillingAccount ba = billingAccounts[0];
        String city;
        if (ba.Account != null) {
            city = ba.Account.BillingCity;
        } else {
            // A billing account linked only through AccountBillingAccount has no owning account, so
            // its city is the requesting account's. The modal sends this city on create and has no
            // city input, so a null here would refuse every create with "Billing City is required.".
            try {
                city = [SELECT BillingCity FROM Account WHERE Id = :accountId WITH USER_MODE LIMIT 1].BillingCity;
            } catch (QueryException qe) {
                throw readRefused('the account', qe);
            }
        }
        return new AccountInfo(acc.Name, ba.Id, ba.Name, city);
    }

    @AuraEnabled(cacheable=true)
    public static List<ProductOption> getProducts() {
        List<ProductOption> results = new List<ProductOption>();
        try {
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
        } catch (QueryException qe) {
            throw readRefused('the products', qe);
        }
        return results;
    }

    @AuraEnabled(cacheable=true)
    public static List<LegalEntityOption> getLegalEntities() {
        List<LegalEntityOption> results = new List<LegalEntityOption>();
        try {
            for (LegalEntity le : [SELECT Id, Name FROM LegalEntity WHERE Status = 'Active' WITH USER_MODE ORDER BY Name]) {
                results.add(new LegalEntityOption(le.Id, le.Name));
            }
        } catch (QueryException qe) {
            throw readRefused('the legal entities', qe);
        }
        return results;
    }

    @AuraEnabled(cacheable=true)
    public static List<TaxTreatmentOption> getTaxTreatments() {
        List<TaxTreatmentOption> results = new List<TaxTreatmentOption>();
        // TaxTreatment.Status is not permissionable (measured on a 264 org), so no field grant applies;
        // object read on TaxTreatment is what gates this query.
        try {
            for (TaxTreatment tt : [SELECT Id, Name FROM TaxTreatment WHERE Status = 'Active' WITH USER_MODE ORDER BY Name]) {
                results.add(new TaxTreatmentOption(tt.Id, tt.Name));
            }
        } catch (QueryException qe) {
            throw readRefused('the tax treatments', qe);
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
            throw RLM_AuraErrors.handled('Billing account is required.');
        }

        List<BillingAccount> billingAccounts;
        try {
            billingAccounts = [
                SELECT Id, AccountId
                FROM BillingAccount
                WHERE Id = :billingAccountId
                WITH USER_MODE
                LIMIT 1
            ];
        } catch (QueryException qe) {
            throw readRefused('the billing account', qe);
        }

        if (billingAccounts.isEmpty()) {
            throw RLM_AuraErrors.handled('Billing Account not found.');
        }

        Id accountId = billingAccounts[0].AccountId;

        if (accountId == null) {
            List<AccountBillingAccount> accountBillingAccounts;
            try {
                accountBillingAccounts = [
                    SELECT AccountId, BillingAccountId
                    FROM AccountBillingAccount
                    WHERE BillingAccountId = :billingAccountId
                    WITH USER_MODE
                    LIMIT 1
                ];
            } catch (QueryException qe) {
                throw readRefused('the links between the billing account and its accounts', qe);
            }

            if (!accountBillingAccounts.isEmpty()) {
                accountId = accountBillingAccounts[0].AccountId;
            }
        }

        if (accountId == null) {
            throw RLM_AuraErrors.handled('No Account associated with this Billing Account.');
        }
        if (String.isBlank(billingTermUnitPicklist)) {
            throw RLM_AuraErrors.handled('Billing term unit is required.');
        }
        if (quantity == null || quantity < 0) {
            throw RLM_AuraErrors.handled('Quantity must be zero or greater.');
        }
        if (legalEntityId == null) {
            throw RLM_AuraErrors.handled('Legal entity is required.');
        }
        if (taxTreatmentId == null) {
            throw RLM_AuraErrors.handled('Tax Treatment is required.');
        }
        if (String.isBlank(currencyIsoCode)) {
            throw RLM_AuraErrors.handled('Currency is required.');
        }
        if (unitPrice == null || unitPrice < 0) {
            throw RLM_AuraErrors.handled('Unit Price must be zero or greater.');
        }
        if (String.isBlank(billingCity)) {
            throw RLM_AuraErrors.handled('Billing City is required.');
        }
        if (productId == null) {
            throw RLM_AuraErrors.handled('Product is required.');
        }
        if (startDate == null) {
            throw RLM_AuraErrors.handled('Start Date is required.');
        }
        if (billingDayOfMonth == null || billingDayOfMonth < 1 || billingDayOfMonth > 31) {
            throw RLM_AuraErrors.handled('Billing Day of Month must be between 1 and 31.');
        }
        if (billingStartMonth == null || billingStartMonth < 1 || billingStartMonth > 12) {
            throw RLM_AuraErrors.handled('Billing Start Month must be between 1 and 12.');
        }
        if (totalPrice == null) {
            throw RLM_AuraErrors.handled('Total Price is required.');
        }
        if (termSetting == 'Termed' && billingTermUnitPicklist != 'OneTime' && endDate == null) {
            throw RLM_AuraErrors.handled('End Date is required for a termed charge.');
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

        // A one-time charge is identified by its billing term unit: the modal marks it with
        // billingTermUnitPicklist 'OneTime' and leaves termSetting at Evergreen/Termed, and a
        // one-time sale needs SellingModelType OneTime and no end date.
        Boolean isOneTime = billingTermUnitPicklist == 'OneTime';

        String sellingModelType;
        if (isOneTime) {
            sellingModelType = 'OneTime';
        } else if (termSetting == 'Termed') {
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
        if (!isOneTime && termSetting == 'Termed' && endDate != null) {
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
            System.debug(LoggingLevel.ERROR, 'RLM_BillingScheduleGroupService: createBillingSchedulesFromTrxn returned no result.');
            throw RLM_AuraErrors.handled(CREATE_FAILED_MESSAGE);
        }

        Invocable.Action.Result res = results[0];
        if (!res.isSuccess()) {
            // The action's errors can name context mappings, fields and records, so they go to the
            // debug log and the user gets a fixed sentence.
            System.debug(LoggingLevel.ERROR, 'RLM_BillingScheduleGroupService: createBillingSchedulesFromTrxn failed: '
                + describeErrors(res.getErrors()));
            throw RLM_AuraErrors.handled(CREATE_FAILED_MESSAGE);
        }
        return res.getOutputParameters();
    }

    @TestVisible
    private static String describeErrors(List<Invocable.Action.Error> errors) {
        List<String> messages = new List<String>();
        if (errors != null) {
            for (Invocable.Action.Error err : errors) {
                messages.add(err.getCode() + ': ' + err.getMessage());
            }
        }
        return messages.isEmpty() ? '(no error detail)' : String.join(messages, '; ');
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
