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
 * What the payload sends from the modal's choices (measured on a 264 org by calling the action
 * directly): LegalEntityId__std sets the group's legal entity; BillingTreatmentId__std sets the
 * group's billing type (Advance or Arrears) through the treatment's item, which is the only way
 * to carry timing because BillingType__std and BillingTypePicklistTiming__std are rejected
 * ("Invalid tag attribute name key"); BillingTerm__std is accepted when a term is given. A shipping
 * address tag is required: ShippingCity__std (the account's ShippingCity, else the billingCity the
 * caller submitted, which create requires).
 *
 * The account: the modal passes the id of the account page it opened on (pageAccountId). When that
 * account is the billing account's own, or is linked to it through AccountBillingAccount, it is the
 * account sent (AccountId__std) and read for the shipping city; otherwise the billing account's own
 * account is used, else its oldest link (create refuses when it has neither). When the page account differs
 * from the billing account's own it must be readable by the user (an Account read in USER_MODE) and
 * linked to the billing account; if it is not found, not readable, or not linked (the link was
 * deleted, or the cached getAccountBillingInfo is stale), or the link read is refused, create refuses
 * rather than fall back to the owner, since the city the modal submitted came from the page account.
 * getAccountBillingInfo returns the billing city of the requested account, which is the account create
 * sends, so the city the modal submits matches it. It reads BillingCity in the same query as the
 * account (covered by the compound BillingAddress grant RLM_BillingUI holds), not after a billing
 * account is resolved: one read, one refusal message. No billing treatment read can be hidden by sharing:
 * BillingTreatment's organization-wide default is public (measured on a 264 org; BillingTreatmentItem
 * is controlled by its parent), so "no treatment" means none exists, not that sharing hid one.
 *
 * Treatment selection (one wording; chooseTreatment implements it). Candidates are the oldest-first
 * active, non-milestone, billable treatments of the legal entity, in the charge's currency, counting
 * only their active items typed Advance or Arrears (a None-type item is ignored; several items of the
 * same timing are fine). The read filters on the charge's currency and is capped at 1000 items, oldest
 * treatment first; when the cap is hit the last treatment read is dropped (it may be cut short), and
 * treatments beyond the cap are not considered. Recurring charge: the first treatment whose items all bill in the chosen
 * timing; a treatment with items in both timings is ambiguous and skipped. One-time charge (the
 * billing term unit is OneTime): timing is moot, so ambiguity does not apply; the first Advance-only
 * treatment, else the first Arrears-only one, else (last, because what the platform bills for it on a
 * one-time charge is unmeasured) the first treatment with both timings (measured: the platform picks a treatment
 * of the legal entity whatever the currency, so one is sent to keep the currency right). A valid
 * Advance or Arrears sent with a one-time charge is ignored (the modal never sends one). When none
 * fits, create refuses with a message before calling the action: it names the timing only for a
 * recurring charge, and when the only candidates were skipped as ambiguous it says that treatment
 * has items in both timings and must be split, instead of saying none exists. The charge currency
 * must be an active CurrencyType, or create refuses before any treatment lookup.
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

    private static final String TIMING_ADVANCE = 'Advance';
    private static final String TIMING_ARREARS = 'Arrears';

    // One active item of a billable treatment of the legal entity: the treatment, the timing the
    // item bills in and the treatment's currency. A treatment with several items has several rows.
    @TestVisible
    private class TreatmentCandidate {
        public Id treatmentId;
        public String billingType;
        public String currencyIsoCode;

        public TreatmentCandidate(Id treatmentId, String billingType, String currencyIsoCode) {
            this.treatmentId = treatmentId;
            this.billingType = billingType;
            this.currencyIsoCode = currencyIsoCode;
        }
    }

    // The outcome of chooseTreatment: the treatment chosen, or none; when none, the first treatment that
    // would have matched but was skipped as ambiguous (items in both timings), so the refusal can say so.
    @TestVisible
    private class TreatmentChoice {
        public Id chosen;
        public Id skippedAmbiguous;
    }

    // Test seams: candidates stand in for the treatment query, and the payload handed to the action is
    // kept so a test can read what the create path really sends.
    @TestVisible
    private static List<TreatmentCandidate> mockTreatmentCandidates = null;
    @TestVisible
    private static String lastTransactionDetails = null;

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
        // True when a billing account may exist but this user cannot read it: the read of the
        // account's billing account links is refused, or a billing account of the account (its own
        // or a linked one) is hidden by sharing. Whether one exists is then unknown to the user, not
        // "there is none".
        @AuraEnabled public Boolean billingLinkUnreadable = false;

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

    // The account name, flagged as "a billing account may exist but this user cannot read it".
    private static AccountInfo billingAccountUnreadable(String accountName) {
        AccountInfo info = new AccountInfo(accountName, null, null, null);
        info.billingLinkUnreadable = true;
        return info;
    }

    // Throws for a missing id or an account the caller cannot read: there is no account name to show
    // then, and the modal surfaces the message as an error toast (its account-info wire handler), so
    // the header is not left blank without a reason. An account with no billing account still returns
    // an AccountInfo carrying the account name; the modal blocks Create until a billing account exists.
    // So does a user who cannot read the account's billing account links, with billingLinkUnreadable
    // set so the modal says the billing account could not be read rather than that there is none; the
    // same flag is set when sharing hides the account's own billing account (even if a linked one is
    // readable: the account's own comes first, as below) or the linked one the pick lands on. The
    // result is cacheable, so after access is granted the modal can show the old result until the
    // cached entry expires or the page is reloaded.
    @AuraEnabled(cacheable=true)
    public static AccountInfo getAccountBillingInfo(Id accountId) {
        if (accountId == null) {
            throw RLM_AuraErrors.handled('Account Id is required.');
        }

        List<Account> accounts;
        try {
            accounts = [SELECT Id, Name, BillingCity FROM Account WHERE Id = :accountId WITH USER_MODE LIMIT 1];
        } catch (QueryException qe) {
            throw readRefused('the account', qe);
        }
        if (accounts.isEmpty()) {
            throw RLM_AuraErrors.handled('Account not found.');
        }
        Account acc = accounts[0];

        // Deterministic pick: the account's default billing profile first, then oldest first. A billing
        // account linked to the account only through AccountBillingAccount is resolved too, as the
        // create path does. Of the account's own billing accounts, only those the user reads are
        // ranked: a readable one is returned even if a hidden one is the default, since telling them
        // apart would reveal more than that one exists. A linked one is picked by its link, oldest
        // first, whether or not the user reads it (see below).
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
                SELECT Id, Name
                FROM BillingAccount
                WHERE AccountId = :accountId
                WITH USER_MODE
                ORDER BY IsDefaultBillingProfile DESC, CreatedDate, Id
                LIMIT 1
            ];
        } catch (QueryException qe) {
            throw readRefused('the billing accounts', qe);
        }

        if (billingAccounts.isEmpty() && new HiddenBillingAccounts().existFor(accountId)) {
            // The account has a billing account of its own that sharing hides from this user (billing
            // accounts are private by default): not "no billing account" either. Checked before the
            // links, so a readable linked billing account is not picked in place of the account's own,
            // which may be its default billing profile.
            System.debug(LoggingLevel.WARN, 'RLM_BillingScheduleGroupService: the account\'s billing account is not visible to the user');
            return billingAccountUnreadable(acc.Name);
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
                // grant. The header still shows the account, flagged so the modal says the billing
                // account could not be read; Create stays blocked without a billing account.
                System.debug(LoggingLevel.ERROR, 'RLM_BillingScheduleGroupService read of the billing account links refused: '
                    + qe.getTypeName() + ': ' + qe.getMessage());
                return billingAccountUnreadable(acc.Name);
            }
            if (!links.isEmpty()) {
                // Same BillingCity read as above: covered by the compound BillingAddress grant (see there).
                try {
                    billingAccounts = [
                        SELECT Id, Name
                        FROM BillingAccount
                        WHERE Id = :links[0].BillingAccountId
                        WITH USER_MODE
                        LIMIT 1
                    ];
                } catch (QueryException qe) {
                    throw readRefused('the billing accounts', qe);
                }
                if (billingAccounts.isEmpty()) {
                    // The link names a billing account that sharing hides from this user: one exists,
                    // so this is not "no billing account" either. Only the oldest link is read, so a
                    // newer link to a billing account the user can read is not tried: the account is
                    // flagged unreadable even then. A known gap, not fixed here.
                    System.debug(LoggingLevel.WARN, 'RLM_BillingScheduleGroupService: the linked billing account is not visible to the user');
                    return billingAccountUnreadable(acc.Name);
                }
            }
        }

        if (billingAccounts.isEmpty()) {
            return new AccountInfo(acc.Name, null, null, null);
        }

        BillingAccount ba = billingAccounts[0];
        // The city is the requested account's: create sends the page account when it is linked, and a
        // billing account's own account when the page is that account, so both match this read.
        String city = acc.BillingCity;
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
        Date endDate,
        Id pageAccountId
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

        // The account page the modal opened on, when it differs from the billing account's own (when it
        // is the own account, accountId already is it). The city the modal submitted came from the page
        // account, so it must be the account sent: it has to be readable and linked to the billing
        // account through AccountBillingAccount, or create refuses (never a silent fallback to the owner).
        if (pageAccountId != null && pageAccountId != accountId) {
            List<Account> pageAccounts;
            try {
                pageAccounts = [SELECT Id FROM Account WHERE Id = :pageAccountId WITH USER_MODE LIMIT 1];
            } catch (QueryException qe) {
                throw readRefused('the account', qe);
            }
            if (pageAccounts.isEmpty()) {
                throw RLM_AuraErrors.handled('The account you opened this from was not found or is not visible to you.');
            }
            List<AccountBillingAccount> pageLinks;
            try {
                pageLinks = [SELECT Id FROM AccountBillingAccount
                    WHERE BillingAccountId = :billingAccountId AND AccountId = :pageAccountId
                    WITH USER_MODE LIMIT 1];
            } catch (QueryException qe) {
                throw readRefused('the account links', qe);
            }
            if (pageLinks.isEmpty()) {
                throw RLM_AuraErrors.handled(
                    'The account you opened this from is not linked to the billing account. Reopen it and try again.');
            }
            accountId = pageAccountId;
        }

        if (accountId == null) {
            List<AccountBillingAccount> accountBillingAccounts;
            try {
                accountBillingAccounts = [
                    SELECT AccountId, BillingAccountId
                    FROM AccountBillingAccount
                    WHERE BillingAccountId = :billingAccountId
                    WITH USER_MODE
                    ORDER BY CreatedDate, Id
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
        if (billingTerm != null && billingTerm < 1) {
            throw RLM_AuraErrors.handled('Billing Term must be 1 or greater.');
        }
        String timing = String.isBlank(billingTypePicklistTiming) ? null : billingTypePicklistTiming;
        if (timing != null && timing != TIMING_ADVANCE && timing != TIMING_ARREARS) {
            throw RLM_AuraErrors.handled('Billing Timing must be Advance or Arrears.');
        }
        if (timing == null && billingTermUnitPicklist != 'OneTime') {
            throw RLM_AuraErrors.handled('Billing Timing is required for a recurring charge.');
        }

        requireActiveCurrency(currencyIsoCode);

        // Timing travels only through a billing treatment (see the class header), chosen for the
        // legal entity and currency. A one-time charge gets the treatment the one-time rule picks (any
        // timing sent with it is ignored), so it is not left to the platform's currency-blind choice.
        Boolean isOneTime = billingTermUnitPicklist == 'OneTime';
        Id billingTreatmentId = findBillingTreatmentId(legalEntityId, isOneTime, timing, currencyIsoCode);
        String shippingCity = readShippingCity(accountId, billingCity);

        String transactionDetailsJson = buildTransactionDetailsJson(
            accountId, billingAccountId, billingTermUnitPicklist, quantity, legalEntityId,
            taxTreatmentId, currencyIsoCode, unitPrice, totalPrice, billingCity, productId,
            productName, startDate, billingDayOfMonth, billingStartMonth, termSetting, endDate,
            billingTerm, billingTreatmentId, shippingCity
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
        Date endDate,
        Integer billingTerm,
        Id billingTreatmentId,
        String shippingCity
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
            'LegalEntityId__std' => legalEntityId,
            'AccountId__std' => accountId,
            'BillingProfileId__std' => billingAccountId,
            'BillingCity__std' => billingCity,
            // Any one shipping address tag satisfies the action's shipping address requirement
            // (measured: ShippingCity__std alone clears REQUIRED_FIELD_MISSING for shippingAddress).
            'ShippingCity__std' => shippingCity,
            'BillingTermUnit__std' => billingTermUnitPicklist,
            'BillingActionType__std' => 'Add',
            'CurrencyIsoCode__std' => currencyIsoCode,
            // TotalPrice__std is Required for OneTime, Evergreen, AND TermDefined
            // new-sale transactions (Create Standalone Billing Schedules contract),
            // so it must be sent for every selling model — not just Termed.
            'TotalPrice__std' => totalPrice
        };

        // The chosen treatment is sent when there is one; an omitted term leaves the org default.
        if (billingTreatmentId != null) {
            transactionData.put('BillingTreatmentId__std', billingTreatmentId);
        }
        if (billingTerm != null) {
            transactionData.put('BillingTerm__std', billingTerm);
        }

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

    // The charge currency must be an active currency of the org, or the lookups below would only say
    // that no treatment bills in it.
    private static void requireActiveCurrency(String currencyIsoCode) {
        List<CurrencyType> active;
        try {
            active = [SELECT Id FROM CurrencyType WHERE IsoCode = :currencyIsoCode AND IsActive = true WITH USER_MODE LIMIT 1];
        } catch (QueryException qe) {
            throw readRefused('the currencies', qe);
        }
        if (active.isEmpty()) {
            throw RLM_AuraErrors.handled('Currency ' + currencyIsoCode + ' is not an active currency in this org. Choose another currency.');
        }
    }

    // The shipping city for the action: the account's, else the billing city the caller submitted
    // (create already requires it to be non-blank).
    @TestVisible
    private static String readShippingCity(Id accountId, String billingCity) {
        List<Account> accounts;
        try {
            accounts = [SELECT ShippingCity FROM Account WHERE Id = :accountId WITH USER_MODE LIMIT 1];
        } catch (QueryException qe) {
            throw readRefused('the account', qe);
        }
        // An account hidden by sharing returns no row: that is not a refused read, so fall back.
        return resolveShippingCity(accounts.isEmpty() ? null : accounts[0].ShippingCity, billingCity);
    }

    @TestVisible
    private static String resolveShippingCity(String accountShippingCity, String billingCity) {
        if (String.isNotBlank(accountShippingCity)) {
            return accountShippingCity;
        }
        return billingCity;
    }

    // Cap on treatment items read (a test lowers it).
    @TestVisible
    private static Integer ITEM_READ_CAP = 1000;

    // The billing treatment of the legal entity chosen by the rule in the class header, in the charge's
    // currency (a treatment item's BillingType is where Advance or Arrears lives). timing is not used for
    // a one-time charge. Both timings are read so a recurring charge can skip a treatment carrying both.
    @TestVisible
    private static Id findBillingTreatmentId(Id legalEntityId, Boolean isOneTime, String timing, String currencyIsoCode) {
        List<TreatmentCandidate> candidates = new List<TreatmentCandidate>();
        Boolean truncated = false;
        Integer readLimit = ITEM_READ_CAP + 1;
        if (Test.isRunningTest() && mockTreatmentCandidates != null) {
            candidates = mockTreatmentCandidates;
        } else {
            try {
                for (BillingTreatmentItem item : [
                    SELECT BillingTreatmentId, BillingType, BillingTreatment.CurrencyIsoCode
                    FROM BillingTreatmentItem
                    WHERE BillingType IN (:TIMING_ADVANCE, :TIMING_ARREARS)
                    AND Status = 'Active'
                    AND BillingTreatment.Status = 'Active'
                    AND BillingTreatment.LegalEntityId = :legalEntityId
                    AND BillingTreatment.IsMilestoneBilling = false
                    AND BillingTreatment.ExcludeFromBilling = 'No'
                    AND BillingTreatment.CurrencyIsoCode = :currencyIsoCode
                    WITH USER_MODE
                    ORDER BY BillingTreatment.CreatedDate, BillingTreatmentId
                    LIMIT :readLimit
                ]) {
                    candidates.add(new TreatmentCandidate(
                        item.BillingTreatmentId, item.BillingType, item.BillingTreatment.CurrencyIsoCode));
                }
            } catch (QueryException qe) {
                throw readRefused('the billing treatments', qe);
            }
            // One row past the cap shows the read was cut off (exactly the cap is a complete read). Drop the
            // extra row; if it belongs to the last treatment kept, that treatment may be cut short.
            truncated = candidates.size() > ITEM_READ_CAP;
            if (truncated) {
                Id extraTreatmentId = candidates.remove(candidates.size() - 1).treatmentId;
                if (candidates[candidates.size() - 1].treatmentId == extraTreatmentId) {
                    candidates = dropPartialLastTreatment(candidates, candidates.size());
                }
            }
        }
        TreatmentChoice choice = chooseTreatment(candidates, isOneTime, timing, currencyIsoCode);
        if (choice.chosen != null) {
            return choice.chosen;
        }
        if (truncated) {
            throw RLM_AuraErrors.handled(
                'The billing treatment lookup for ' + legalEntityPhrase(legalEntityId) + ' in ' + currencyIsoCode
                + ' was cut off at ' + ITEM_READ_CAP + ' items, so a matching treatment may not have been seen'
                + (choice.skippedAmbiguous == null ? '' : ' (a treatment with items in both advance and arrears was also skipped)')
                + '. Ask your administrator to consolidate or deactivate treatments, or choose another legal entity or currency.');
        }
        String lowerTiming = isOneTime ? null : timing.toLowerCase();
        if (choice.skippedAmbiguous != null) {
            throw RLM_AuraErrors.handled(
                'The billing treatment ' + treatmentPhrase(choice.skippedAmbiguous, legalEntityId)
                + ' has items in both advance and arrears, so it cannot be matched to ' + lowerTiming
                + ' in ' + currencyIsoCode + '. Split it into one treatment per timing, or choose another legal entity or currency.');
        }
        throw RLM_AuraErrors.handled(
            'No active billing treatment bills ' + (isOneTime ? '' : 'in ' + lowerTiming + ' ')
            + 'in ' + currencyIsoCode + ' for ' + legalEntityPhrase(legalEntityId) + '. '
            + (isOneTime
                ? 'Choose another legal entity or currency, or ask your administrator to set one up.'
                : 'Choose another legal entity, timing or currency, or ask your administrator to set one up.'));
    }

    // The item read is capped. Rows come treatment by treatment, so when the cap is hit the last
    // treatment may be cut short (a mixed treatment would look Advance-only or Arrears-only): drop every
    // row of the last treatment id read. Under the cap nothing is dropped.
    @TestVisible
    private static List<TreatmentCandidate> dropPartialLastTreatment(List<TreatmentCandidate> candidates, Integer cap) {
        if (candidates.size() < cap) {
            return candidates;
        }
        Id lastTreatmentId = candidates[candidates.size() - 1].treatmentId;
        List<TreatmentCandidate> kept = new List<TreatmentCandidate>();
        for (TreatmentCandidate c : candidates) {
            if (c.treatmentId != lastTreatmentId) {
                kept.add(c);
            }
        }
        return kept;
    }

    // Applies the selection rule in the class header to candidates in the order given (the query's:
    // oldest treatment first); no treatment chosen when none fits (skippedAmbiguous then says whether a
    // treatment was passed over for carrying both timings).
    @TestVisible
    private static TreatmentChoice chooseTreatment(
            List<TreatmentCandidate> candidates, Boolean isOneTime, String timing, String currencyIsoCode) {
        TreatmentChoice choice = new TreatmentChoice();
        if (isOneTime) {
            // Advance-only first, then Arrears-only, then a treatment with both timings last: what the
            // platform bills for a mixed treatment on a one-time charge is unmeasured.
            Set<Id> hasAdvance = new Set<Id>();
            Set<Id> hasArrears = new Set<Id>();
            List<Id> order = new List<Id>();
            for (TreatmentCandidate c : candidates) {
                if (c.currencyIsoCode != currencyIsoCode) {
                    continue;
                }
                if (!hasAdvance.contains(c.treatmentId) && !hasArrears.contains(c.treatmentId)) {
                    order.add(c.treatmentId);
                }
                if (c.billingType == TIMING_ADVANCE) {
                    hasAdvance.add(c.treatmentId);
                } else {
                    hasArrears.add(c.treatmentId);
                }
            }
            Id firstArrearsOnly = null;
            for (Id treatmentId : order) {
                Boolean adv = hasAdvance.contains(treatmentId);
                Boolean arr = hasArrears.contains(treatmentId);
                if (adv && !arr) {
                    choice.chosen = treatmentId;
                    return choice;
                }
                if (arr && !adv && firstArrearsOnly == null) {
                    firstArrearsOnly = treatmentId;
                }
            }
            choice.chosen = firstArrearsOnly != null ? firstArrearsOnly : (order.isEmpty() ? null : order[0]);
            return choice;
        }
        Map<Id, String> firstType = new Map<Id, String>();
        Set<Id> bothTimings = new Set<Id>();
        List<Id> inTiming = new List<Id>();
        for (TreatmentCandidate c : candidates) {
            if (c.currencyIsoCode != currencyIsoCode) {
                continue;
            }
            String seen = firstType.get(c.treatmentId);
            if (seen == null) {
                firstType.put(c.treatmentId, c.billingType);
                if (c.billingType == timing) {
                    inTiming.add(c.treatmentId);
                }
            } else if (seen != c.billingType) {
                bothTimings.add(c.treatmentId);
            }
        }
        for (Id treatmentId : inTiming) {
            if (!bothTimings.contains(treatmentId)) {
                choice.chosen = treatmentId;
                return choice;
            }
        }
        // Nothing fits. A treatment that bills in this timing but also in the other is why, when there is one.
        for (TreatmentCandidate c : candidates) {
            if (c.currencyIsoCode == currencyIsoCode && bothTimings.contains(c.treatmentId)) {
                choice.skippedAmbiguous = c.treatmentId;
                break;
            }
        }
        return choice;
    }

    // For the ambiguous-treatment refusal: "'<name>'" when the treatment is readable, else "of <legal entity>".
    private static String treatmentPhrase(Id treatmentId, Id legalEntityId) {
        try {
            List<BillingTreatment> found = [SELECT Name FROM BillingTreatment WHERE Id = :treatmentId WITH USER_MODE LIMIT 1];
            if (!found.isEmpty() && String.isNotBlank(found[0].Name)) {
                return '\'' + found[0].Name + '\'';
            }
        } catch (QueryException qe) {
            System.debug(LoggingLevel.WARN, 'RLM_BillingScheduleGroupService treatment name not readable: ' + qe.getMessage());
        }
        return 'of ' + legalEntityPhrase(legalEntityId);
    }

    // For the refusal message only: "legal entity <name>", or "the selected legal entity" when the
    // name cannot be read.
    private static String legalEntityPhrase(Id legalEntityId) {
        try {
            List<LegalEntity> les = [SELECT Name FROM LegalEntity WHERE Id = :legalEntityId WITH USER_MODE LIMIT 1];
            if (!les.isEmpty()) {
                return 'legal entity ' + les[0].Name;
            }
        } catch (QueryException qe) {
            System.debug(LoggingLevel.WARN, 'RLM_BillingScheduleGroupService legal entity name not readable: ' + qe.getMessage());
        }
        return 'the selected legal entity';
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
        if (Test.isRunningTest()) {
            lastTransactionDetails = transactionDetailsJson;
        }
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

    // Whether the account has a billing account of its own, checked past sharing. Runs only after the
    // user's own read of the account's billing accounts succeeded and found none, so only for a user
    // who can read the account and holds read access to billing accounts. It returns a yes or no and
    // nothing of the record: no Id, name or field value reaches the user, only that a billing account
    // exists, which tells the modal to say it could not be read rather than that there is none. A
    // linked billing account needs no such check: the link follows the account's sharing (the tests
    // assert the user reads it), so the hidden account is found through the link.
    // WITH SYSTEM_MODE is needed as well as without sharing: measured on a 264 org, a query with no
    // access mode in a without sharing class at API 68 still counted none of a billing account that
    // sharing hides, while the same query at API 66, or with SYSTEM_MODE at API 68, counted it.
    private without sharing class HiddenBillingAccounts {
        Boolean existFor(Id accountId) {
            return ![SELECT Id FROM BillingAccount WHERE AccountId = :accountId WITH SYSTEM_MODE LIMIT 1].isEmpty();
        }
    }
}
