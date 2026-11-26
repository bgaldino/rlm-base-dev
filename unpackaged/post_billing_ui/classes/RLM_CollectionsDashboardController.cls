/**
 * Controller for Collections Dashboard.
 * All dashboard data methods accept accountId (Id, optional) and currencyCode (String, optional)
 * so that Account and Currency filters apply consistently to every card/section on the page.
 * Uses Invoice, Payment, and optional DebitMemo/Credit objects per Salesforce Billing/Revenue Cloud.
 */
public with sharing class RLM_CollectionsDashboardController {

    @AuraEnabled(cacheable=true)
    public static String getOrgDefaultCurrency() {
        String defaultCurrency = UserInfo.getDefaultCurrency();
        return String.isNotBlank(defaultCurrency) ? defaultCurrency : 'USD';
    }

    @AuraEnabled(cacheable=true)
    public static List<Map<String, String>> getAccountOptions() {
        List<Map<String, String>> options = new List<Map<String, String>>();
        options.add(new Map<String, String>{ 'value' => '', 'label' => 'All Accounts' });
        try {
            for (Account a : [SELECT Id, Name FROM Account WITH USER_MODE ORDER BY Name LIMIT 500]) {
                options.add(new Map<String, String>{ 'value' => a.Id, 'label' => a.Name });
            }
        } catch (QueryException e) {
            // The user cannot read Account: offer only "All Accounts" so the rest of the
            // dashboard (currency options, worklist) still loads, as the other sections do.
            return new List<Map<String, String>>{ options[0] };
        }
        return options;
    }

    /** Payment Promises: total requested amount on PaymentScheduleItem by status (Ready for Processing, Draft, Failed, In Processing). */
    @AuraEnabled(cacheable=true)
    public static PaymentPromiseSummary getPaymentPromiseSummary(Id accountId, String currencyCode) {
        PaymentPromiseSummary summary = new PaymentPromiseSummary();
        List<PaymentPromiseBucket> buckets = summary.buckets;
        try {
            if (!Schema.getGlobalDescribe().containsKey('PaymentScheduleItem')) return summary;
            Map<String, Schema.SObjectField> psiFields = Schema.getGlobalDescribe().get('PaymentScheduleItem').getDescribe().fields.getMap();
            if (!psiFields.containsKey('Status') || !psiFields.containsKey('RequestedAmount')) return summary;
            String accFld = psiFields.containsKey('PaymentAccountId') ? 'PaymentAccountId' : null;
            Boolean filterAccount = accountId != null && String.isNotBlank(String.valueOf(accountId)) && accFld != null;
            Boolean filterCurrency = String.isNotBlank(currencyCode) && paymentScheduleItemHasCurrencyField();
            String soql = 'SELECT Status, SUM(RequestedAmount) totalAmt, COUNT(Id) cnt FROM PaymentScheduleItem WHERE Status IN (\'Ready for Processing\', \'Draft\', \'Failed\', \'Processing\') ';
            if (filterAccount) soql += ' AND PaymentAccountId = :accountId ';
            if (filterCurrency) soql += ' AND CurrencyIsoCode = :currencyCode ';
            soql += ' GROUP BY Status ';
            List<AggregateResult> results = Database.query(soql, AccessLevel.USER_MODE);
            Map<String, Decimal> amountByStatus = new Map<String, Decimal>();
            Map<String, Integer> countByStatus = new Map<String, Integer>();
            for (AggregateResult ar : results) {
                String st = (String) ar.get('Status');
                if (st != null) {
                    amountByStatus.put(st, (Decimal) ar.get('totalAmt'));
                    countByStatus.put(st, (Integer) ar.get('cnt'));
                }
            }
            List<String> order = new List<String>{ 'Failed', 'Ready for Processing', 'Draft', 'Processing' };
            for (String status : order) {
                Decimal amt = amountByStatus.get(status) != null ? amountByStatus.get(status) : 0;
                Integer cnt = countByStatus.get(status) != null ? countByStatus.get(status) : 0;
                buckets.add(new PaymentPromiseBucket(status, amt, cnt));
            }
        } catch (Exception e) {
            // Not "no promises": the page says the schedule items could not be read.
            sectionSkipped('getPaymentPromiseSummary', e);
            PaymentPromiseSummary unreadable = new PaymentPromiseSummary();
            unreadable.unavailable = true;
            unreadable.unavailableReason = reasonFor(e);
            return unreadable;
        }
        return summary;
    }

    // The promise buckets, or unavailable (with its reason) when the schedule items could not be read.
    public class PaymentPromiseSummary {
        @AuraEnabled public List<PaymentPromiseBucket> buckets { get; set; }
        @AuraEnabled public Boolean unavailable { get; set; }
        @AuraEnabled public String unavailableReason { get; set; }
        public PaymentPromiseSummary() {
            buckets = new List<PaymentPromiseBucket>();
            unavailable = false;
        }
    }

    public class PaymentPromiseBucket {
        @AuraEnabled public String status { get; set; }
        @AuraEnabled public Decimal totalRequestedAmount { get; set; }
        @AuraEnabled public Integer itemCount { get; set; }
        public PaymentPromiseBucket(String status, Decimal totalRequestedAmount, Integer itemCount) {
            this.status = status;
            this.totalRequestedAmount = totalRequestedAmount != null ? totalRequestedAmount : 0;
            this.itemCount = itemCount != null ? itemCount : 0;
        }
    }

    @AuraEnabled(cacheable=true)
    public static List<Map<String, String>> getCurrencyOptions() {
        List<Map<String, String>> options = new List<Map<String, String>>();
        options.add(new Map<String, String>{ 'value' => '', 'label' => 'All Currencies' });
        try {
            for (CurrencyType ct : [SELECT IsoCode, IsCorporate FROM CurrencyType WHERE IsActive = true WITH USER_MODE ORDER BY IsCorporate DESC, IsoCode ASC]) {
                if (String.isNotBlank(ct.IsoCode)) {
                    options.add(new Map<String, String>{ 'value' => ct.IsoCode, 'label' => ct.IsoCode });
                }
            }
        } catch (Exception e) { sectionSkipped('getCurrencyOptions', e); }
        if (options.size() == 1) {
            String defaultCode = getOrgDefaultCurrency();
            options.add(new Map<String, String>{ 'value' => defaultCode, 'label' => defaultCode });
        }
        return options;
    }

    @AuraEnabled(cacheable=true)
    public static CollectionsDashboardData getDashboardCards(Id accountId, String currencyCode) {
        CollectionsDashboardData data = new CollectionsDashboardData();
        Boolean filterAccount = accountId != null && String.isNotBlank(String.valueOf(accountId));
        Boolean filterCurrency = String.isNotBlank(currencyCode);
        String invAccountField = getInvoiceAccountFieldName();

        // Base invoice filter: unpaid posted invoices only
        String invWhere = ' Balance > 0 AND Status = \'Posted\' ';
        if (filterAccount) {
            invWhere += ' AND ' + invAccountField + ' = :accountId ';
        }
        if (filterCurrency && invoiceHasCurrencyField()) {
            invWhere += ' AND CurrencyIsoCode = :currencyCode ';
        }

        Decimal sumUnpaidInvoiceBalance = null;
        try {
            List<Invoice> unpaidInvoices = (List<Invoice>) cappedInvoiceRows(
                'SELECT Id, Balance, TotalAmount, DueDate FROM Invoice WHERE ' + invWhere,
                new Map<String, Object>{ 'accountId' => accountId, 'currencyCode' => currencyCode });
            tallyInvoices(data, unpaidInvoices, Date.today());
            sumUnpaidInvoiceBalance = data.receivablesOutstanding;
        } catch (Exception e) {
            // A refused or failed Invoice read is not "nothing owed": the invoice figures are
            // marked unavailable (null) and the other components still load.
            sectionSkipped('getDashboardCards', e);
            markInvoicesUnavailable(data, e);
        }

        // Each component is null when its read was refused or failed (the catch blocks of
        // getUnappliedCreditsSum, getDebitMemoNotInvoicedSum, getUnappliedPaymentBalanceSum and
        // getUnappliedPaymentCount, and the Invoice catch above), which list it in data.unavailable with
        // its reason. The total balance adds only the amounts that were read and the page names what it
        // leaves out; with nothing read it is null, not zero. The payment count is its own key: a failed
        // count leaves the payment balance, the total and the note as they are.
        Decimal unappliedCredits = getUnappliedCreditsSum(data, accountId, currencyCode);
        Decimal debitMemoNotInvoiced = getDebitMemoNotInvoicedSum(data, accountId, currencyCode);
        Decimal unappliedPaymentBalance = getUnappliedPaymentBalanceSum(data, accountId, currencyCode);
        Integer unappliedPaymentCount = getUnappliedPaymentCount(data, accountId, currencyCode);

        totalUp(data, sumUnpaidInvoiceBalance, unappliedCredits, debitMemoNotInvoiced, unappliedPaymentBalance,
            unappliedPaymentCount);
        return data;
    }

    // The card figures and the total balance from the components that were read (null = not read). The
    // total, its breakdown and the payment card follow the amounts alone: a payment count that could not be
    // read shows only the count as not available. Takes values so a test can build any mix.
    @TestVisible
    private static void totalUp(CollectionsDashboardData data, Decimal sumUnpaidInvoiceBalance, Decimal unappliedCredits,
            Decimal debitMemoNotInvoiced, Decimal unappliedPaymentBalance, Integer unappliedPaymentCount) {
        data.unappliedCredits = unappliedCredits;
        data.unappliedPaymentBalance = unappliedPaymentBalance;
        data.unappliedPaymentCount = unappliedPaymentCount;

        // No total without the unpaid invoices, its main component (as total outstanding). Without debit
        // memos, credits or payments it is a partial total the page labels as excluding them.
        data.totalBalance = sumUnpaidInvoiceBalance == null ? null : sumUnpaidInvoiceBalance + orZero(debitMemoNotInvoiced)
            - orZero(unappliedCredits) - orZero(unappliedPaymentBalance);
        data.totalOutstanding = sumUnpaidInvoiceBalance == null || unappliedPaymentBalance == null
            ? null : sumUnpaidInvoiceBalance - unappliedPaymentBalance;

        data.totalBalanceBreakdown = new List<Map<String, Object>>();
        data.totalBalanceBreakdown.add(breakdownRow('Unpaid Invoices', sumUnpaidInvoiceBalance, 'blue', UNAVAILABLE_INVOICES));
        data.totalBalanceBreakdown.add(breakdownRow('Debit Memos', debitMemoNotInvoiced, 'orange', UNAVAILABLE_DEBIT_MEMOS));
        data.totalBalanceBreakdown.add(breakdownRow('Unapplied Credits', negate(unappliedCredits), 'green', UNAVAILABLE_CREDITS));
        data.totalBalanceBreakdown.add(breakdownRow('Unapplied Payments', negate(unappliedPaymentBalance), 'red', UNAVAILABLE_PAYMENTS));

    }

    // Keys of CollectionsDashboardData.unavailable: the card components whose read was refused or
    // failed. The page shows those as not available instead of a zero, and the total balance as
    // excluding them.
    @TestVisible private static final String UNAVAILABLE_INVOICES = 'invoices';
    @TestVisible private static final String UNAVAILABLE_DEBIT_MEMOS = 'debitMemos';
    @TestVisible private static final String UNAVAILABLE_CREDITS = 'unappliedCredits';
    @TestVisible private static final String UNAVAILABLE_PAYMENTS = 'unappliedPayments';
    // The unapplied payment count alone: not a component of the total balance.
    @TestVisible private static final String UNAVAILABLE_PAYMENT_COUNT = 'unappliedPaymentCount';

    private static void markUnavailable(CollectionsDashboardData data, String key, Exception e) {
        if (!data.unavailable.contains(key)) {
            data.unavailable.add(key);
        }
        data.unavailableReason.put(key, reasonFor(e));
    }

    private static void markInvoicesUnavailable(CollectionsDashboardData data, Exception e) {
        markUnavailable(data, UNAVAILABLE_INVOICES, e);
        data.receivablesOutstanding = null;
        data.invoiceCount = null;
        data.partiallySettledCount = null;
        data.partiallySettledSum = null;
        data.notSettledCount = null;
        data.notSettledSum = null;
        data.currentDue = null;
        data.overdue = null;
        data.agingBuckets = new List<Map<String, Object>>();
    }

    // One row of the total balance breakdown; a component that could not be read has a null amount and
    // carries the key the page uses to say so.
    private static Map<String, Object> breakdownRow(String label, Decimal amount, String color, String unavailableKey) {
        Map<String, Object> row = new Map<String, Object>{ 'label' => label, 'amount' => amount, 'color' => color };
        if (amount == null) {
            row.put('unavailable', unavailableKey);
        }
        return row;
    }

    private static Decimal orZero(Decimal value) {
        return value == null ? 0 : value;
    }

    private static Decimal negate(Decimal value) {
        return value == null ? null : -value;
    }

    // The invoice totals, settlement counts and aging buckets on the dashboard cards, from the
    // queried unpaid invoices. Takes rows so a test can pass invoices, which Apex cannot insert.
    @TestVisible
    private static void tallyInvoices(CollectionsDashboardData data, List<Invoice> unpaidInvoices, Date today) {
        Decimal sumUnpaidInvoiceBalance = 0;
        Decimal sumCurrentDue = 0;
        Decimal sumOverdue = 0;
        Decimal agingCurrent = 0, aging1_30 = 0, aging31_60 = 0, aging61_90 = 0, aging90Plus = 0;
        Integer partiallySettledCount = 0;
        Decimal partiallySettledSum = 0;
        Integer notSettledCount = 0;
        Decimal notSettledSum = 0;

        for (Invoice inv : unpaidInvoices) {
            Decimal bal = inv.Balance != null ? inv.Balance : 0;
            Decimal total = inv.TotalAmount != null ? inv.TotalAmount : 0;
            sumUnpaidInvoiceBalance += bal;
            if (inv.DueDate != null) {
                if (inv.DueDate >= today) {
                    sumCurrentDue += bal;
                    agingCurrent += bal;
                } else {
                    sumOverdue += bal;
                    Integer daysOverdue = inv.DueDate.daysBetween(today);
                    if (daysOverdue <= 30) aging1_30 += bal;
                    else if (daysOverdue <= 60) aging31_60 += bal;
                    else if (daysOverdue <= 90) aging61_90 += bal;
                    else aging90Plus += bal;
                }
            } else {
                sumCurrentDue += bal;
                agingCurrent += bal;
            }
            if (total > 0 && bal > 0 && bal < total) {
                partiallySettledCount++;
                partiallySettledSum += bal;
            } else {
                notSettledCount++;
                notSettledSum += bal;
            }
        }

        data.receivablesOutstanding = sumUnpaidInvoiceBalance;
        data.invoiceCount = unpaidInvoices.size();
        data.partiallySettledCount = partiallySettledCount;
        data.partiallySettledSum = partiallySettledSum;
        data.notSettledCount = notSettledCount;
        data.notSettledSum = notSettledSum;
        data.currentDue = sumCurrentDue;
        data.overdue = sumOverdue;

        data.agingBuckets = new List<Map<String, Object>>();
        data.agingBuckets.add(new Map<String, Object>{ 'label' => 'Current', 'amount' => agingCurrent, 'key' => 'current' });
        data.agingBuckets.add(new Map<String, Object>{ 'label' => '1-30', 'amount' => aging1_30, 'key' => '1-30' });
        data.agingBuckets.add(new Map<String, Object>{ 'label' => '31-60', 'amount' => aging31_60, 'key' => '31-60' });
        data.agingBuckets.add(new Map<String, Object>{ 'label' => '61-90', 'amount' => aging61_90, 'key' => '61-90' });
        data.agingBuckets.add(new Map<String, Object>{ 'label' => '90+', 'amount' => aging90Plus, 'key' => '90+' });
    }

    @AuraEnabled(cacheable=true)
    public static WorklistData getWorklist(Id accountId, String currencyCode) {
        WorklistData wl = new WorklistData();
        String invAccountField = getInvoiceAccountFieldName();
        Boolean filterAccount = accountId != null && String.isNotBlank(String.valueOf(accountId));
        Boolean filterCurrency = String.isNotBlank(currencyCode);
        Date thirtyDaysAgo = Date.today().addDays(-30);

        try { buildCriticalFollowUpInvoices(wl, invAccountField, filterAccount, filterCurrency, accountId, currencyCode, thirtyDaysAgo); } catch (Exception e) { sectionSkipped('getWorklist', e); }
        try { buildHighValueDelinquents(wl, invAccountField, filterAccount, filterCurrency, accountId, currencyCode, thirtyDaysAgo); } catch (Exception e) { sectionSkipped('getWorklist', e); }
        try { buildDisputedFromCases(wl, invAccountField, filterAccount, filterCurrency, accountId, currencyCode); } catch (Exception e) { sectionSkipped('getWorklist', e); }
        // Each tab shows exactly what its own read returns: rows, or nothing ("No items in this view"), or
        // unavailable with its reason. No fallback widens an empty tab and no placeholder row fills one.
        return wl;
    }

    // Keys of WorklistData.unavailable, one per worklist tab: the read the section is built from was
    // refused or failed, so its list is not "nothing to work on" (todo 435).
    @TestVisible private static final String WORKLIST_CRITICAL = 'critical';
    @TestVisible private static final String WORKLIST_HIGH_VALUE = 'highValue';
    @TestVisible private static final String WORKLIST_DISPUTED = 'disputed';

    private static void markWorklistUnavailable(WorklistData wl, String key, Exception e) {
        if (!wl.unavailable.contains(key)) {
            wl.unavailable.add(key);
        }
        wl.unavailableReason.put(key, reasonFor(e));
    }

    @AuraEnabled(cacheable=true)
    public static CpTaskList getCollectionPlanTasks(Id accountId) {
        CpTaskList taskList = new CpTaskList();
        List<CpTaskItem> results = taskList.items;
        if (!Schema.getGlobalDescribe().containsKey('CollectionPlan')) return taskList;
        try {
            String cpWhere = ' Id != null ';
            if (accountId != null && String.isNotBlank(String.valueOf(accountId))) {
                cpWhere += ' AND AccountId = :accountId ';
            }
            List<Id> cpIds = new List<Id>();
            for (SObject cp : Database.query('SELECT Id FROM CollectionPlan WHERE ' + cpWhere + ' LIMIT 2000', AccessLevel.USER_MODE)) {
                cpIds.add((Id) cp.get('Id'));
            }
            if (cpIds.isEmpty()) return taskList;
            for (Task t : [SELECT Id, Subject, Status, ActivityDate, WhatId FROM Task WHERE WhatId IN :cpIds WITH USER_MODE ORDER BY ActivityDate DESC NULLS LAST, CreatedDate DESC LIMIT 200]) {
                results.add(new CpTaskItem(t.Id, t.Subject, t.Status, t.ActivityDate, t.WhatId));
            }
        } catch (Exception e) {
            // Not "no tasks": the page says the plans or their tasks could not be read.
            sectionSkipped('getCollectionPlanTasks', e);
            CpTaskList unreadable = new CpTaskList();
            unreadable.unavailable = true;
            unreadable.unavailableReason = reasonFor(e);
            return unreadable;
        }
        return taskList;
    }

    // The plan tasks, or unavailable (with its reason) when the plans or their tasks could not be read.
    public class CpTaskList {
        @AuraEnabled public List<CpTaskItem> items { get; set; }
        @AuraEnabled public Boolean unavailable { get; set; }
        @AuraEnabled public String unavailableReason { get; set; }
        public CpTaskList() {
            items = new List<CpTaskItem>();
            unavailable = false;
        }
    }

    public class CpTaskItem {
        @AuraEnabled public Id taskId { get; set; }
        @AuraEnabled public String subject { get; set; }
        @AuraEnabled public String status { get; set; }
        @AuraEnabled public Date activityDate { get; set; }
        @AuraEnabled public Id collectionPlanId { get; set; }
        public CpTaskItem(Id taskId, String subject, String status, Date activityDate, Id collectionPlanId) {
            this.taskId = taskId;
            this.subject = subject;
            this.status = status;
            this.activityDate = activityDate;
            this.collectionPlanId = collectionPlanId;
        }
    }

    // Any unpaid invoice, when nothing older than 30 days was found, under the same account and currency
    // filters as the primary high-value query: with an account selected it never lists other accounts.
    private static Boolean invoiceHasBillToContactId() {
        try {
            return Schema.SObjectType.Invoice.fields.getMap().containsKey('BillToContactId');
        } catch (Exception e) { probeSkipped('invoiceHasBillToContactId', e); return false; }
    }

    private static Boolean invoiceHasDaysInvoiceOverdue() {
        try {
            return Schema.SObjectType.Invoice.fields.getMap().containsKey('DaysInvoiceOverdue');
        } catch (Exception e) { probeSkipped('invoiceHasDaysInvoiceOverdue', e); return false; }
    }

    private static void buildCriticalFollowUpInvoices(WorklistData wl, String invAccountField, Boolean filterAccount, Boolean filterCurrency, Id accountId, String currencyCode, Date thirtyDaysAgo) {
        try {
            Boolean hasDaysField = invoiceHasDaysInvoiceOverdue();
            Boolean hasBillToContact = invoiceHasBillToContactId();
            Integer thirtyDays = 30;

            Decimal criticalMinBalance = 2000;
            String invWhere;
            if (hasDaysField) {
                invWhere = ' Balance >= :criticalMinBalance AND (DaysInvoiceOverdue >= :thirtyDays OR (DaysInvoiceOverdue = null AND DueDate != null AND DueDate < :thirtyDaysAgo)) ';
            } else {
                invWhere = ' Balance >= :criticalMinBalance AND DueDate < :thirtyDaysAgo ';
            }
            if (filterAccount) invWhere += ' AND ' + invAccountField + ' = :accountId ';
            if (filterCurrency && invoiceHasCurrencyField()) invWhere += ' AND CurrencyIsoCode = :currencyCode ';

            String invSelect = 'SELECT Id, InvoiceNumber, Balance';
            if (hasDaysField) invSelect += ', DaysInvoiceOverdue';
            invSelect += ', DueDate';
            invSelect += ', BillingAccountId';
            if (hasBillToContact) invSelect += ', BillToContactId';

            String orderField = hasDaysField ? 'DaysInvoiceOverdue DESC NULLS LAST' : 'DueDate ASC';
            List<Invoice> invs = Database.query(invSelect + ' FROM Invoice WHERE ' + invWhere + ' ORDER BY ' + orderField + ' LIMIT 200', AccessLevel.USER_MODE);
            addCriticalFollowUps(wl, invs, hasDaysField, hasBillToContact, Date.today());
        } catch (Exception e) {
            sectionSkipped('buildCriticalFollowUpInvoices', e);
            markWorklistUnavailable(wl, WORKLIST_CRITICAL, e);
        }
    }

    // One row per queried invoice, with its account name and collection plan. Takes rows so a
    // test can pass invoices, which Apex cannot insert.
    @TestVisible
    private static void addCriticalFollowUps(WorklistData wl, List<Invoice> invs, Boolean hasDaysField, Boolean hasBillToContact, Date today) {
        Set<Id> billingAccountIds = new Set<Id>();
        for (Invoice inv : invs) {
            if (inv.get('BillingAccountId') != null) {
                billingAccountIds.add((Id) inv.get('BillingAccountId'));
            }
        }
        Map<Id, String> accountNames = getAccountNames(billingAccountIds);

        Set<Id> invoiceIds = new Set<Id>();
        for (Invoice inv : invs) {
            if (inv.Id != null) invoiceIds.add(inv.Id);
        }
        Map<Id, Id> invoiceToCollectionPlan = new Map<Id, Id>();
        Boolean planLookupFailed = false;
        if (!invoiceIds.isEmpty() && Schema.getGlobalDescribe().containsKey('CollectionPlanItem')) {
            try {
                for (CollectionPlanItem cpi : [SELECT InvoiceId, CollectionPlanId FROM CollectionPlanItem WHERE InvoiceId IN :invoiceIds AND CollectionPlanId != null WITH USER_MODE]) {
                    if (!invoiceToCollectionPlan.containsKey(cpi.InvoiceId)) {
                        invoiceToCollectionPlan.put(cpi.InvoiceId, cpi.CollectionPlanId);
                    }
                }
            } catch (Exception ex) { sectionSkipped('addCriticalFollowUps', ex); planLookupFailed = true; }
        }

        for (Invoice inv : invs) {
            Integer daysOverdue;
            if (hasDaysField && inv.get('DaysInvoiceOverdue') != null) {
                daysOverdue = (Integer) inv.get('DaysInvoiceOverdue');
            } else {
                daysOverdue = inv.DueDate != null ? inv.DueDate.daysBetween(today) : null;
            }
            String invNum = inv.InvoiceNumber != null ? inv.InvoiceNumber : '—';
            Id billingAcctId = inv.get('BillingAccountId') != null ? (Id) inv.get('BillingAccountId') : null;
            String billingAcctName = billingAcctId != null ? accountNames.get(billingAcctId) : null;
            Id billToContactId = hasBillToContact && inv.get('BillToContactId') != null ? (Id) inv.get('BillToContactId') : null;
            Id collectionPlanId = invoiceToCollectionPlan.get(inv.Id);

            CriticalFollowUpInvoiceItem row = new CriticalFollowUpInvoiceItem(
                inv.Id, invNum, inv.Balance != null ? inv.Balance : 0,
                daysOverdue, billingAcctId, billingAcctName, billToContactId, collectionPlanId
            );
            // A plan lookup that was refused or failed is not "no plan": the page offers no Create.
            row.collectionPlanUnavailable = planLookupFailed;
            wl.criticalFollowUpInvoices.add(row);
        }
    }

    public class CriticalFollowUpInvoiceItem {
        @AuraEnabled public Id invoiceId { get; set; }
        @AuraEnabled public String invoiceNumber { get; set; }
        @AuraEnabled public Decimal balance { get; set; }
        @AuraEnabled public Integer daysInvoiceOverdue { get; set; }
        @AuraEnabled public Id billingAccountId { get; set; }
        @AuraEnabled public String billingAccountName { get; set; }
        @AuraEnabled public Id billToContactId { get; set; }
        @AuraEnabled public Id collectionPlanId { get; set; }
        // True when the plan lookup was refused or failed: collectionPlanId null then is not "no plan".
        @AuraEnabled public Boolean collectionPlanUnavailable { get; set; }
        public CriticalFollowUpInvoiceItem(Id invoiceId, String invoiceNumber, Decimal balance, Integer daysInvoiceOverdue, Id billingAccountId, String billingAccountName, Id billToContactId, Id collectionPlanId) {
            this.invoiceId = invoiceId;
            this.invoiceNumber = invoiceNumber != null ? invoiceNumber : '—';
            this.balance = balance;
            this.daysInvoiceOverdue = daysInvoiceOverdue;
            this.billingAccountId = billingAccountId;
            this.billingAccountName = billingAccountName != null ? billingAccountName : '—';
            this.billToContactId = billToContactId;
            this.collectionPlanId = collectionPlanId;
        }
    }

    private static void buildHighValueDelinquents(WorklistData wl, String invAccountField, Boolean filterAccount, Boolean filterCurrency, Id accountId, String currencyCode, Date thirtyDaysAgo) {
        String invWhere = ' Balance > 0 AND DueDate < :thirtyDaysAgo ';
        if (filterAccount) invWhere += ' AND ' + invAccountField + ' = :accountId ';
        if (filterCurrency && invoiceHasCurrencyField()) invWhere += ' AND CurrencyIsoCode = :currencyCode ';
        invWhere += getInvoiceNotFullySettledStatusFilter();
        List<Invoice> invs = new List<Invoice>();
        try {
            invs = (List<Invoice>) cappedInvoiceRows('SELECT Id, Balance, DueDate, ' + invAccountField + ' FROM Invoice WHERE ' + invWhere,
                new Map<String, Object>{ 'accountId' => accountId, 'currencyCode' => currencyCode, 'thirtyDaysAgo' => thirtyDaysAgo });
        } catch (Exception e) {
            sectionSkipped('buildHighValueDelinquents', e);
            markWorklistUnavailable(wl, WORKLIST_HIGH_VALUE, e);
            return;
        }
        addHighValueDelinquents(wl, invs, invAccountField, Date.today());
    }

    // Rolls the queried invoices up by account and adds the ten largest balances of 2000 or more,
    // with each account's collection plan. Takes rows so a test can pass invoices, which Apex
    // cannot insert.
    @TestVisible
    private static void addHighValueDelinquents(WorklistData wl, List<Invoice> invs, String invAccountField, Date today) {
        Decimal minBalanceThreshold = 2000;
        Map<Id, Decimal> accountBalance = new Map<Id, Decimal>();
        Map<Id, Integer> accountMaxDays = new Map<Id, Integer>();
        for (Invoice inv : invs) {
            Id accId = (Id) inv.get(invAccountField);
            if (accId == null) continue;
            Decimal bal = inv.Balance != null ? inv.Balance : 0;
            accountBalance.put(accId, accountBalance.get(accId) != null ? accountBalance.get(accId) + bal : bal);
            Integer days = inv.DueDate != null ? inv.DueDate.daysBetween(today) : 0;
            Integer existing = accountMaxDays.get(accId);
            if (existing == null || days > existing) accountMaxDays.put(accId, days);
        }
        // Filter accounts below the $2000 threshold
        Set<Id> qualifiedAccounts = new Set<Id>();
        for (Id accId : accountBalance.keySet()) {
            if (accountBalance.get(accId) >= minBalanceThreshold) {
                qualifiedAccounts.add(accId);
            }
        }
        if (qualifiedAccounts.isEmpty()) return;
        List<WorklistItem> highValue = new List<WorklistItem>();
        Map<Id, String> accountNames = getAccountNames(qualifiedAccounts);
        Map<Id, Id> accountToCollectionPlan = new Map<Id, Id>();
        Boolean planLookupFailed = false;
        if (Schema.getGlobalDescribe().containsKey('CollectionPlan')) {
            try {
                Set<Id> accIds = qualifiedAccounts;
                for (CollectionPlan cp : [SELECT Id, AccountId FROM CollectionPlan WHERE AccountId IN :accIds AND AccountId != null WITH USER_MODE]) {
                    if (!accountToCollectionPlan.containsKey(cp.AccountId)) {
                        accountToCollectionPlan.put(cp.AccountId, cp.Id);
                    }
                }
            } catch (Exception ex) { sectionSkipped('addHighValueDelinquents', ex); planLookupFailed = true; }
        }
        for (Id accId : qualifiedAccounts) {
            WorklistItem item = new WorklistItem(accId, accountNames.get(accId), accountBalance.get(accId), accountMaxDays.get(accId), 'highValue', 'red', null, null);
            item.collectionPlanId = accountToCollectionPlan.get(accId);
            // A plan lookup that was refused or failed is not "no plan": the page offers no Create.
            item.collectionPlanUnavailable = planLookupFailed;
            highValue.add(item);
        }
        sortByBalance(highValue);
        for (Integer i = 0; i < Math.min(10, highValue.size()); i++) wl.highValueDelinquents.add(highValue[i]);
    }

    private static String getInvoiceNotFullySettledStatusFilter() {
        try {
            if (!Schema.SObjectType.Invoice.fields.getMap().containsKey('Status')) return '';
            return ' AND (Status = null OR Status NOT IN (\'Paid\', \'Closed\', \'Canceled\')) ';
        } catch (Exception e) { probeSkipped('getInvoiceNotFullySettledStatusFilter', e); return ''; }
    }

    private static void buildDisputedFromCases(WorklistData wl, String invAccountField, Boolean filterAccount,
            Boolean filterCurrency, Id accountId, String currencyCode) {
        try {
            String caseWhere = ' IsClosed = false AND AccountId != null ';
            if (filterAccount) caseWhere += ' AND AccountId = :accountId ';
            String caseFields = 'Id, CaseNumber, AccountId, Subject, Description';
            if (Schema.SObjectType.Case.fields.getMap().containsKey('Reason')) caseFields += ', Reason';
            List<Case> openCases = Database.query('SELECT ' + caseFields + ' FROM Case WHERE ' + caseWhere + ' ORDER BY CreatedDate DESC', AccessLevel.USER_MODE);
            Map<Id, String> accountDisputeReason = new Map<Id, String>();
            Map<Id, Id> accountCaseId = new Map<Id, Id>();
            Map<Id, String> accountCaseNumber = new Map<Id, String>();
            Set<Id> disputedAccountIds = new Set<Id>();
            for (Case c : openCases) {
                if (c.AccountId == null) continue;
                disputedAccountIds.add(c.AccountId);
                if (!accountCaseId.containsKey(c.AccountId)) {
                    accountCaseId.put(c.AccountId, c.Id);
                    accountCaseNumber.put(c.AccountId, c.CaseNumber);
                }
                if (!accountDisputeReason.containsKey(c.AccountId)) {
                    String reason = '';
                    if (String.isNotBlank(c.Subject)) reason = c.Subject;
                    if (String.isNotBlank(c.Description)) reason += (String.isNotBlank(reason) ? ' – ' : '') + (c.Description.length() > 200 ? c.Description.substring(0, 200) + '...' : c.Description);
                    try { if (c.get('Reason') != null) reason += (String.isNotBlank(reason) ? ' [' : '') + String.valueOf(c.get('Reason')) + (String.isNotBlank(reason) ? ']' : ''); } catch (Exception e) { probeSkipped('buildDisputedFromCases', e); }
                    accountDisputeReason.put(c.AccountId, String.isNotBlank(reason) ? reason : 'Open case');
                }
            }
            if (disputedAccountIds.isEmpty()) return;
            Map<Id, String> accountNames = getAccountNames(disputedAccountIds);
            Date today = Date.today();

            // A refused Invoice read throws here and is caught at the end of this method, which drops the
            // whole disputed section and marks it unavailable (WORKLIST_DISPUTED): a row without its invoice
            // rollup would carry a zero balance and no days overdue, which reads as a real "nothing owed".
            String invWhere = ' Balance > 0 AND ' + invAccountField + ' IN :disputedAccountIds ';
            // The page's currency filter applies to the rollup, as it does to every other invoice read.
            if (filterCurrency && invoiceHasCurrencyField()) invWhere += ' AND CurrencyIsoCode = :currencyCode ';
            List<Invoice> disputedInvs = (List<Invoice>) cappedInvoiceRows('SELECT Id, Balance, DueDate, ' + invAccountField + ' FROM Invoice WHERE ' + invWhere,
                new Map<String, Object>{ 'disputedAccountIds' => disputedAccountIds, 'currencyCode' => currencyCode });
            Map<Id, Decimal> accountBalance = new Map<Id, Decimal>();
            Map<Id, Integer> accountMaxDaysOverdue = new Map<Id, Integer>();
            Map<Id, Id> invoiceToAccountId = new Map<Id, Id>();
            Set<Id> invoiceIds = new Set<Id>();
            for (Invoice inv : disputedInvs) {
                Id accId = (Id) inv.get(invAccountField);
                if (accId == null) continue;
                invoiceToAccountId.put(inv.Id, accId);
                invoiceIds.add(inv.Id);
                Decimal bal = inv.Balance != null ? inv.Balance : 0;
                accountBalance.put(accId, accountBalance.get(accId) != null ? accountBalance.get(accId) + bal : bal);
                if (inv.DueDate != null && inv.DueDate < today) {
                    Integer days = inv.DueDate.daysBetween(today);
                    Integer existing = accountMaxDaysOverdue.get(accId);
                    if (existing == null || days > existing) accountMaxDaysOverdue.put(accId, days);
                }
            }

            Map<Id, Date> accountPtpDate = new Map<Id, Date>();
            Boolean ptpLookupFailed = false;
            if (!invoiceIds.isEmpty() && Schema.getGlobalDescribe().containsKey('PaymentSchedule') && Schema.getGlobalDescribe().containsKey('PaymentScheduleItem')) {
                try {
                    List<Id> invIdList = new List<Id>(invoiceIds);
                    Map<Id, Id> scheduleToInvoiceId = new Map<Id, Id>();
                    for (SObject ps : Database.query('SELECT Id, ReferenceEntityId FROM PaymentSchedule WHERE ReferenceEntityId IN :invIdList', AccessLevel.USER_MODE)) {
                        Id refId = (Id) ps.get('ReferenceEntityId');
                        if (refId != null) scheduleToInvoiceId.put((Id) ps.get('Id'), refId);
                    }
                    if (!scheduleToInvoiceId.isEmpty()) {
                        Set<Id> scheduleIds = scheduleToInvoiceId.keySet();
                        for (PaymentScheduleItem psi : Database.query('SELECT Id, PaymentScheduleId, TargetPaymentProcessingDate FROM PaymentScheduleItem WHERE PaymentScheduleId IN :scheduleIds AND TargetPaymentProcessingDate != null', AccessLevel.USER_MODE)) {
                            Id invId = scheduleToInvoiceId.get(psi.PaymentScheduleId);
                            Id accId = invoiceToAccountId.get(invId);
                            if (accId == null) continue;
                            Date d = psi.TargetPaymentProcessingDate;
                            Date existing = accountPtpDate.get(accId);
                            if (existing == null || (d != null && d > existing)) accountPtpDate.put(accId, d);
                        }
                    }
                } catch (Exception e) { sectionSkipped('buildDisputedFromCases', e); ptpLookupFailed = true; }
            }

            for (Id accId : disputedAccountIds) {
                Decimal bal = accountBalance.get(accId) != null ? accountBalance.get(accId) : 0;
                Integer daysOverdue = accountMaxDaysOverdue.get(accId);
                Date ptpDate = accountPtpDate.get(accId);
                WorklistItem item = new WorklistItem(accId, accountNames.get(accId), bal, daysOverdue, 'disputed', 'amber', ptpDate, accountDisputeReason.get(accId));
                item.caseId = accountCaseId.get(accId);
                item.caseNumber = accountCaseNumber.get(accId);
                // A promise lookup that was refused or failed is not "no promise".
                item.ptpUnavailable = ptpLookupFailed;
                wl.disputedInvoices.add(item);
            }
        } catch (Exception e) {
            sectionSkipped('buildDisputedFromCases', e);
            markWorklistUnavailable(wl, WORKLIST_DISPUTED, e);
        }
    }

    // Every catch (Exception) in this class is one of two kinds, named by the helper it calls:
    //  - probeSkipped: guards a describe or field-presence probe (does Invoice have this field, is
    //    Case.Reason in the query). The field being absent is the normal case in some orgs; nothing
    //    is read from the database, so a permission refusal cannot land here.
    //  - sectionSkipped: everything that reads records, including the reads of objects whose
    //    existence was checked first (CollectionPlan, CollectionPlanItem, PaymentSchedule,
    //    CurrencyType). A refused or failed read leaves that section empty while the others still
    //    load, and is logged at WARN; it is a permission or data problem, not an absent schema.
    //    Where the section is a figure (the cards and total balance, payment promises, progress), it is
    //    returned as unavailable (null, or the wrapper's unavailable flag or list), never as a zero the
    //    page would show as a real amount (todo 435). The lists follow the same rule: the task, plan and
    //    promise wrappers carry an unavailable flag, and a worklist tab whose read was refused or failed is
    //    listed in WorklistData.unavailable. Each carries its reason (reasonFor: refused or failed).
    // Neither throws and neither puts platform exception text in a response.
    private static void probeSkipped(String context, Exception e) {
        System.debug(LoggingLevel.FINE, 'RLM_CollectionsDashboardController.' + context + ' (field or object not present): ' + e.getMessage());
    }

    // Why a section is unavailable, so the page can tell the user what to do: 'refused' when the user may
    // not read it (ask an administrator), 'failed' for anything else (try again). Measured on a 264 org
    // (2026-11-26, todo 435): a USER_MODE read of an object the user cannot read throws a QueryException
    // "sObject type 'X' is not supported", and of a field the user cannot read "No such column 'F' on
    // entity 'X'". Any other exception (a timeout, a limit, a platform error) is a failure, not a refusal.
    @TestVisible private static final String REASON_REFUSED = 'refused';
    @TestVisible private static final String REASON_FAILED = 'failed';
    // More rows than a section can total in one transaction: narrow the filters (todo 435).
    @TestVisible private static final String REASON_TOO_MANY = 'tooMany';

    // The most invoice rows a section reads to total or roll up. One more than this means the read was
    // cut off, so the figure would be wrong: the section is unavailable (REASON_TOO_MANY) instead, well
    // before the 50,000-row query limit, which no catch block can handle.
    @TestVisible private static Integer INVOICE_ROW_CAP = 10000;

    @TestVisible
    private class TooManyRowsException extends Exception {}

    private static List<SObject> cappedInvoiceRows(String soql, Map<String, Object> binds) {
        List<SObject> rows = Database.queryWithBinds(soql + ' LIMIT ' + (INVOICE_ROW_CAP + 1), binds, AccessLevel.USER_MODE);
        if (rows.size() > INVOICE_ROW_CAP) {
            throw new TooManyRowsException('More than ' + INVOICE_ROW_CAP + ' invoices to total.');
        }
        return rows;
    }

    @TestVisible
    private static String reasonFor(Exception e) {
        if (e instanceof NoAccessException) {
            return REASON_REFUSED;
        }
        if (e instanceof TooManyRowsException) {
            return REASON_TOO_MANY;
        }
        String message = e == null || e.getMessage() == null ? '' : e.getMessage();
        if (!(e instanceof QueryException)) {
            return REASON_FAILED;
        }
        if (message.contains('is not supported')) {
            return REASON_REFUSED;
        }
        // "No such column 'F' on entity 'X'" is a refusal only when X has a field F the user cannot see;
        // a field the org does not have at all (a single-currency org's CurrencyIsoCode) is a failure.
        Matcher column = Pattern.compile('No such column \'(\\w+)\' on entity \'(\\w+)\'').matcher(message);
        if (column.find() && fieldExists(column.group(2), column.group(1))) {
            return REASON_REFUSED;
        }
        return REASON_FAILED;
    }

    @TestVisible
    private static Boolean fieldExists(String objectName, String fieldName) {
        Schema.SObjectType objectType = Schema.getGlobalDescribe().get(objectName);
        return objectType != null && objectType.getDescribe().fields.getMap().containsKey(fieldName);
    }

    private static void sectionSkipped(String context, Exception e) {
        System.debug(LoggingLevel.WARN, 'RLM_CollectionsDashboardController.' + context + ' skipped: ' + e.getTypeName() + ': ' + e.getMessage());
    }

    // A refused Account read leaves the rows listed with a dash for the name (see RLM_AccountNames), not
    // dropped by the caller's catch.
    private static Map<Id, String> getAccountNames(Set<Id> accountIds) {
        return RLM_AccountNames.forIds(accountIds);
    }

    public class WorklistItem implements Comparable {
        @AuraEnabled public Id accountId { get; set; }
        @AuraEnabled public String accountName { get; set; }
        @AuraEnabled public Decimal balance { get; set; }
        @AuraEnabled public Integer daysOverdue { get; set; }
        @AuraEnabled public String segment { get; set; }
        @AuraEnabled public String healthScore { get; set; }
        @AuraEnabled public Date ptpDate { get; set; }
        @AuraEnabled public String disputeReason { get; set; }
        @AuraEnabled public Id collectionPlanId { get; set; }
        @AuraEnabled public Id caseId { get; set; }
        @AuraEnabled public String caseNumber { get; set; }
        // True when the plan or promise lookup was refused or failed: a null then is not "none".
        @AuraEnabled public Boolean collectionPlanUnavailable { get; set; }
        @AuraEnabled public Boolean ptpUnavailable { get; set; }
        public WorklistItem(Id accId, String name, Decimal bal, Integer days, String seg) {
            accountId = accId; accountName = name != null ? name : '—'; balance = bal; daysOverdue = days; segment = seg; healthScore = 'amber'; ptpDate = null; disputeReason = null; collectionPlanId = null; caseId = null; caseNumber = null;
        }
        public WorklistItem(Id accId, String name, Decimal bal, Integer days, String seg, String health) {
            accountId = accId; accountName = name != null ? name : '—'; balance = bal; daysOverdue = days; segment = seg; healthScore = health; ptpDate = null; disputeReason = null; collectionPlanId = null; caseId = null; caseNumber = null;
        }
        public WorklistItem(Id accId, String name, Decimal bal, Integer days, String seg, String health, Date ptp, String disputeReasonStr) {
            accountId = accId; accountName = name != null ? name : '—'; balance = bal; daysOverdue = days; segment = seg; healthScore = health; ptpDate = ptp; disputeReason = disputeReasonStr; collectionPlanId = null; caseId = null; caseNumber = null;
        }
        public Integer compareTo(Object o) {
            WorklistItem other = (WorklistItem) o;
            if (daysOverdue == null && other.daysOverdue == null) return 0;
            if (daysOverdue == null) return 1;
            if (other.daysOverdue == null) return -1;
            return other.daysOverdue - daysOverdue;
        }
    }

    private static void sortByBalance(List<WorklistItem> items) {
        for (Integer i = 0; i < items.size(); i++) {
            for (Integer j = i + 1; j < items.size(); j++) {
                Decimal bi = items[i].balance != null ? items[i].balance : 0;
                Decimal bj = items[j].balance != null ? items[j].balance : 0;
                if (bj > bi) {
                    WorklistItem t = items[i];
                    items[i] = items[j];
                    items[j] = t;
                }
            }
        }
    }

    public class WorklistData {
        @AuraEnabled public List<CriticalFollowUpInvoiceItem> criticalFollowUpInvoices { get; set; }
        @AuraEnabled public List<WorklistItem> highValueDelinquents { get; set; }
        @AuraEnabled public List<WorklistItem> disputedInvoices { get; set; }
        // Tabs whose read was refused or failed (WORKLIST_*): their lists are not "none".
        @AuraEnabled public List<String> unavailable { get; set; }
        // Each unavailable tab's reason: REASON_REFUSED or REASON_FAILED.
        @AuraEnabled public Map<String, String> unavailableReason { get; set; }
        public WorklistData() { criticalFollowUpInvoices = new List<CriticalFollowUpInvoiceItem>(); highValueDelinquents = new List<WorklistItem>(); disputedInvoices = new List<WorklistItem>(); unavailable = new List<String>(); unavailableReason = new Map<String, String>(); }
    }

    // Invoice.BillingAccountId always exists where this module deploys: other classes in it
    // (RLM_InvoiceAgingController, for one) name the field in static SOQL, so the bundle does not
    // compile without it. The describe probing this replaced always returned it, and the branches
    // for an org without it could not run.
    private static String getInvoiceAccountFieldName() {
        return 'BillingAccountId';
    }

    private static Boolean invoiceHasCurrencyField() {
        try {
            return Schema.SObjectType.Invoice.fields.getMap().containsKey('CurrencyIsoCode');
        } catch (Exception e) { probeSkipped('invoiceHasCurrencyField', e); return false; }
    }

    private static Boolean paymentScheduleItemHasCurrencyField() {
        try {
            if (!Schema.getGlobalDescribe().containsKey('PaymentScheduleItem')) return false;
            return Schema.getGlobalDescribe().get('PaymentScheduleItem').getDescribe().fields.getMap().containsKey('CurrencyIsoCode');
        } catch (Exception e) { probeSkipped('paymentScheduleItemHasCurrencyField', e); return false; }
    }

    // Payment.CurrencyIsoCode exists only on a multi-currency org: the payment reads filter on it only then,
    // as the invoice reads do (an absent field is not a refusal, and must not be shown as one).
    private static Boolean paymentHasCurrencyField() {
        try {
            return Schema.SObjectType.Payment.fields.getMap().containsKey('CurrencyIsoCode');
        } catch (Exception e) { probeSkipped('paymentHasCurrencyField', e); return false; }
    }

    private static String getPaymentAccountFieldName() {
        try {
            if (Schema.SObjectType.Payment.fields.getMap().containsKey('PaymentAccountId')) return 'PaymentAccountId';
            if (Schema.SObjectType.Payment.fields.getMap().containsKey('AccountId')) return 'AccountId';
        } catch (Exception e) { probeSkipped('getPaymentAccountFieldName', e); }
        return null;
    }

    // Only a Processed payment can be applied, so only its remaining balance is unapplied: a Draft,
    // Pending, Failed or Canceled payment keeps its Balance but is not money to apply.
    private static final String PROCESSED_PAYMENT = 'Processed';

    private static Decimal getUnappliedCreditsSum(CollectionsDashboardData data, Id accountId, String currencyCode) {
        Decimal sum = 0;
        try {
            String accFld = getPaymentAccountFieldName();
            String soql = 'SELECT SUM(Balance) sumBal FROM Payment WHERE Balance > 0 AND Status = \'' + PROCESSED_PAYMENT + '\' ';
            if (Schema.SObjectType.Payment.fields.getMap().containsKey('Type')) {
                soql += ' AND (Type = \'Credit\' OR Type = \'Credit Memo\') ';
            }
            if (accountId != null && String.isNotBlank(String.valueOf(accountId)) && accFld != null) {
                soql += ' AND ' + accFld + ' = :accountId ';
            }
            if (String.isNotBlank(currencyCode) && paymentHasCurrencyField()) soql += ' AND CurrencyIsoCode = :currencyCode ';
            List<AggregateResult> ar = Database.query(soql, AccessLevel.USER_MODE);
            if (!ar.isEmpty() && ar[0].get('sumBal') != null) sum = (Decimal) ar[0].get('sumBal');
        } catch (Exception e) { sectionSkipped('getUnappliedCreditsSum', e); markUnavailable(data, UNAVAILABLE_CREDITS, e); return null; }
        return sum;
    }

    private static Decimal getDebitMemoNotInvoicedSum(CollectionsDashboardData data, Id accountId, String currencyCode) {
        Decimal sum = 0;
        try {
            // No DebitMemo object in this org: nothing can be owed on one, so zero is the real figure.
            if (!Schema.getGlobalDescribe().containsKey('DebitMemo')) return 0;
            Schema.DescribeSObjectResult dmDesc = Schema.getGlobalDescribe().get('DebitMemo').getDescribe();
            Map<String, Schema.SObjectField> flds = dmDesc.fields.getMap();
            String accFld = flds.containsKey('BillToAccountId') ? 'BillToAccountId' : (flds.containsKey('AccountId') ? 'AccountId' : null);
            // Posted and not yet on a posted invoice: a Draft or Canceled memo is not owed, and
            // a posted invoice's balance already counts its lines. A draft invoice is in no
            // invoice sum, so a memo on one still counts here.
            String soql = 'SELECT SUM(TotalAmount) sumAmt FROM DebitMemo WHERE TotalAmount != null'
                + ' AND Status = \'Posted\' ';
            if (flds.containsKey('InvoiceGenerationStatus')) {
                soql += ' AND InvoiceGenerationStatus != \'Posted Invoice Generated\' ';
            }
            if (accountId != null && accFld != null) soql += ' AND ' + accFld + ' = :accountId ';
            if (String.isNotBlank(currencyCode) && flds.containsKey('CurrencyIsoCode')) soql += ' AND CurrencyIsoCode = :currencyCode ';
            List<AggregateResult> ar = Database.query(soql, AccessLevel.USER_MODE);
            if (!ar.isEmpty() && ar[0].get('sumAmt') != null) sum = (Decimal) ar[0].get('sumAmt');
        } catch (Exception e) { sectionSkipped('getDebitMemoNotInvoicedSum', e); markUnavailable(data, UNAVAILABLE_DEBIT_MEMOS, e); return null; }
        return sum;
    }

    private static Decimal getUnappliedPaymentBalanceSum(CollectionsDashboardData data, Id accountId, String currencyCode) {
        Decimal sum = 0;
        try {
            String accFld = getPaymentAccountFieldName();
            String soql = 'SELECT SUM(Balance) sumBal FROM Payment WHERE Balance > 0 AND Status = \'' + PROCESSED_PAYMENT + '\' ';
            if (Schema.SObjectType.Payment.fields.getMap().containsKey('Type')) {
                soql += ' AND (Type != \'Credit\' AND Type != \'Credit Memo\') ';
            }
            if (accountId != null && String.isNotBlank(String.valueOf(accountId)) && accFld != null) {
                soql += ' AND ' + accFld + ' = :accountId ';
            }
            if (String.isNotBlank(currencyCode) && paymentHasCurrencyField()) soql += ' AND CurrencyIsoCode = :currencyCode ';
            List<AggregateResult> ar = Database.query(soql, AccessLevel.USER_MODE);
            if (!ar.isEmpty() && ar[0].get('sumBal') != null) sum = (Decimal) ar[0].get('sumBal');
        } catch (Exception e) { sectionSkipped('getUnappliedPaymentBalanceSum', e); markUnavailable(data, UNAVAILABLE_PAYMENTS, e); return null; }
        return sum;
    }

    private static Integer getUnappliedPaymentCount(CollectionsDashboardData data, Id accountId, String currencyCode) {
        Integer cnt = 0;
        try {
            String accFld = getPaymentAccountFieldName();
            String soql = 'SELECT COUNT(Id) cnt FROM Payment WHERE Balance > 0 AND Status = \'' + PROCESSED_PAYMENT + '\' ';
            if (Schema.SObjectType.Payment.fields.getMap().containsKey('Type')) {
                soql += ' AND (Type != \'Credit\' AND Type != \'Credit Memo\') ';
            }
            if (accountId != null && accFld != null) soql += ' AND ' + accFld + ' = :accountId ';
            if (String.isNotBlank(currencyCode) && paymentHasCurrencyField()) soql += ' AND CurrencyIsoCode = :currencyCode ';
            List<AggregateResult> ar = Database.query(soql, AccessLevel.USER_MODE);
            if (!ar.isEmpty() && ar[0].get('cnt') != null) cnt = (Integer) ar[0].get('cnt');
        } catch (Exception e) { sectionSkipped('getUnappliedPaymentCount', e); markUnavailable(data, UNAVAILABLE_PAYMENT_COUNT, e); return null; }
        return cnt;
    }

    public class CollectionsDashboardData {
        @AuraEnabled public Decimal totalBalance { get; set; }
        @AuraEnabled public List<Map<String, Object>> totalBalanceBreakdown { get; set; }
        @AuraEnabled public Decimal receivablesOutstanding { get; set; }
        @AuraEnabled public Integer invoiceCount { get; set; }
        @AuraEnabled public Integer partiallySettledCount { get; set; }
        @AuraEnabled public Decimal partiallySettledSum { get; set; }
        @AuraEnabled public Integer notSettledCount { get; set; }
        @AuraEnabled public Decimal notSettledSum { get; set; }
        @AuraEnabled public Decimal currentDue { get; set; }
        @AuraEnabled public Decimal overdue { get; set; }
        @AuraEnabled public Decimal unappliedPaymentBalance { get; set; }
        @AuraEnabled public Integer unappliedPaymentCount { get; set; }
        @AuraEnabled public Decimal unappliedCredits { get; set; }
        @AuraEnabled public Decimal totalOutstanding { get; set; }
        @AuraEnabled public List<Map<String, Object>> agingBuckets { get; set; }
        // Components whose read was refused or failed (UNAVAILABLE_*); their figures are null.
        @AuraEnabled public List<String> unavailable { get; set; }
        // Each unavailable key's reason: REASON_REFUSED or REASON_FAILED.
        @AuraEnabled public Map<String, String> unavailableReason { get; set; }

        public CollectionsDashboardData() {
            unavailable = new List<String>();
            unavailableReason = new Map<String, String>();
            totalBalance = 0;
            totalBalanceBreakdown = new List<Map<String, Object>>();
            receivablesOutstanding = 0;
            invoiceCount = 0;
            partiallySettledCount = 0;
            partiallySettledSum = 0;
            notSettledCount = 0;
            notSettledSum = 0;
            currentDue = 0;
            overdue = 0;
            unappliedPaymentBalance = 0;
            unappliedPaymentCount = 0;
            unappliedCredits = 0;
            totalOutstanding = 0;
            agingBuckets = new List<Map<String, Object>>();
        }
    }

    @AuraEnabled(cacheable=true)
    public static MyCollectionPlanList getMyCollectionPlans() {
        MyCollectionPlanList planList = new MyCollectionPlanList();
        List<MyCollectionPlanItem> items = planList.items;
        try {
            if (!Schema.getGlobalDescribe().containsKey('CollectionPlan')) return planList;
            Id currentUserId = UserInfo.getUserId();
            String acctField = 'AccountId';
            Map<String, Schema.SObjectField> cpFields = Schema.SObjectType.CollectionPlan.fields.getMap();
            if (cpFields.containsKey('BillingAccountId')) {
                acctField = 'BillingAccountId';
            }
            if (cpFields.containsKey('AccountId')) {
                acctField = 'AccountId';
            }
            String selectFields = 'Id, Name, Duedate, TotalInvoiceBalance, ' + acctField;
            String q = 'SELECT ' + selectFields + ' FROM CollectionPlan WHERE OwnerId = :currentUserId ORDER BY Duedate ASC NULLS LAST, Name ASC LIMIT 50';
            List<SObject> plans = Database.query(q, AccessLevel.USER_MODE);
            // Names come from getAccountNames, not an Account.Name relationship in the plan query: a
            // refused Account read then leaves the plans listed with a dash for the name instead of dropping them.
            Set<Id> planAccountIds = new Set<Id>();
            for (SObject cp : plans) {
                if (cp.get(acctField) != null) planAccountIds.add((Id) cp.get(acctField));
            }
            Map<Id, String> planAccountNames = getAccountNames(planAccountIds);
            for (SObject cp : plans) {
                Id cpId = (Id) cp.get('Id');
                String cpName = (String) cp.get('Name');
                Date dueDate = (Date) cp.get('Duedate');
                Decimal totalInvBal = cp.get('TotalInvoiceBalance') != null ? (Decimal) cp.get('TotalInvoiceBalance') : 0;
                Id accountId = (Id) cp.get(acctField);
                String accountName = accountId != null ? planAccountNames.get(accountId) : null;
                items.add(new MyCollectionPlanItem(cpId, cpName, dueDate, accountId, accountName, totalInvBal));
            }
        } catch (Exception e) {
            // Not "no plans": the page says the collection plans could not be read.
            sectionSkipped('getMyCollectionPlans', e);
            MyCollectionPlanList unreadable = new MyCollectionPlanList();
            unreadable.unavailable = true;
            unreadable.unavailableReason = reasonFor(e);
            return unreadable;
        }
        return planList;
    }

    // The user's plans, or unavailable (with its reason) when the plans could not be read.
    public class MyCollectionPlanList {
        @AuraEnabled public List<MyCollectionPlanItem> items { get; set; }
        @AuraEnabled public Boolean unavailable { get; set; }
        @AuraEnabled public String unavailableReason { get; set; }
        public MyCollectionPlanList() {
            items = new List<MyCollectionPlanItem>();
            unavailable = false;
        }
    }

    @AuraEnabled(cacheable=true)
    public static CollectionsProgressData getCollectionsProgress() {
        CollectionsProgressData result = new CollectionsProgressData();
        try {
            if (!Schema.getGlobalDescribe().containsKey('CollectionPlan')) return result;
            List<CollectionPlan> plans = [
                SELECT Id, ClosedDate, CreatedDate, TotalInvoiceBalance, DaysPastDue, Duedate
                FROM CollectionPlan
                WITH USER_MODE
            ];
            if (plans.isEmpty()) return result;
            Integer totalCount = plans.size();
            Integer recoveredCount = 0;
            Decimal recoveredAmount = 0;
            Decimal notRecoveredAmount = 0;
            Decimal totalDaysToClose = 0;
            Integer closedWithDatesCount = 0;
            Decimal totalDaysPastDue = 0;
            Integer daysPastDueCount = 0;
            for (CollectionPlan cp : plans) {
                if (cp.ClosedDate != null) {
                    recoveredCount++;
                    recoveredAmount += cp.TotalInvoiceBalance != null ? cp.TotalInvoiceBalance : 0;
                    if (cp.CreatedDate != null) {
                        totalDaysToClose += cp.CreatedDate.date().daysBetween(cp.ClosedDate);
                        closedWithDatesCount++;
                    }
                } else {
                    notRecoveredAmount += cp.TotalInvoiceBalance != null ? cp.TotalInvoiceBalance : 0;
                }
                if (cp.DaysPastDue != null) {
                    totalDaysPastDue += cp.DaysPastDue;
                    daysPastDueCount++;
                }
            }
            result.totalPlans = totalCount;
            result.recoveredCount = recoveredCount;
            result.notRecoveredCount = totalCount - recoveredCount;
            result.recoveredAmount = recoveredAmount;
            result.notRecoveredAmount = notRecoveredAmount;
            result.recoveredPercent = totalCount > 0 ? (Decimal) recoveredCount * 100 / totalCount : 0;
            result.notRecoveredPercent = totalCount > 0 ? (Decimal) (totalCount - recoveredCount) * 100 / totalCount : 0;
            result.avgDaysToClose = closedWithDatesCount > 0 ? (totalDaysToClose / closedWithDatesCount).setScale(1) : 0;
            result.avgDaysPastDue = daysPastDueCount > 0 ? (totalDaysPastDue / daysPastDueCount).setScale(1) : 0;
        } catch (Exception e) {
            // Not "no plans": the page says the collection plans could not be read.
            sectionSkipped('getCollectionsProgress', e);
            CollectionsProgressData unreadable = new CollectionsProgressData();
            unreadable.unavailable = true;
            unreadable.unavailableReason = reasonFor(e);
            return unreadable;
        }
        return result;
    }

    public class CollectionsProgressData {
        @AuraEnabled public Integer totalPlans { get; set; }
        @AuraEnabled public Integer recoveredCount { get; set; }
        @AuraEnabled public Integer notRecoveredCount { get; set; }
        @AuraEnabled public Decimal recoveredAmount { get; set; }
        @AuraEnabled public Decimal notRecoveredAmount { get; set; }
        @AuraEnabled public Decimal recoveredPercent { get; set; }
        @AuraEnabled public Decimal notRecoveredPercent { get; set; }
        @AuraEnabled public Decimal avgDaysToClose { get; set; }
        @AuraEnabled public Decimal avgDaysPastDue { get; set; }
        // True when the collection plans could not be read: the figures above are not measurements.
        @AuraEnabled public Boolean unavailable { get; set; }
        // Why it is unavailable: REASON_REFUSED or REASON_FAILED (null when it is not).
        @AuraEnabled public String unavailableReason { get; set; }
        public CollectionsProgressData() {
            unavailable = false;
            totalPlans = 0; recoveredCount = 0; notRecoveredCount = 0;
            recoveredAmount = 0; notRecoveredAmount = 0;
            recoveredPercent = 0; notRecoveredPercent = 0;
            avgDaysToClose = 0; avgDaysPastDue = 0;
        }
    }

    public class MyCollectionPlanItem {
        @AuraEnabled public Id collectionPlanId { get; set; }
        @AuraEnabled public String name { get; set; }
        @AuraEnabled public Date dueDate { get; set; }
        @AuraEnabled public Id accountId { get; set; }
        @AuraEnabled public String accountName { get; set; }
        @AuraEnabled public Decimal totalInvoiceBalance { get; set; }
        public MyCollectionPlanItem(Id cpId, String cpName, Date dueDate, Id accountId, String accountName, Decimal totalInvBal) {
            this.collectionPlanId = cpId;
            this.name = cpName != null ? cpName : '—';
            this.dueDate = dueDate;
            this.accountId = accountId;
            this.accountName = accountName != null ? accountName : '—';
            this.totalInvoiceBalance = totalInvBal != null ? totalInvBal : 0;
        }
    }
}