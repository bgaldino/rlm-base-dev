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
            String fromWhere = 'FROM PaymentScheduleItem WHERE Status IN (\'Ready for Processing\', \'Draft\', \'Failed\', \'Processing\') ';
            if (filterAccount) fromWhere += ' AND PaymentAccountId = :accountId ';
            if (filterCurrency) fromWhere += ' AND CurrencyIsoCode = :currencyCode ';
            List<AggregateResult> results = boundedAggregate(fromWhere, 'Status, SUM(RequestedAmount) totalAmt, COUNT(Id) cnt',
                ' GROUP BY Status', new Map<String, Object>{ 'accountId' => accountId, 'currencyCode' => currencyCode },
                'payment schedule items');
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
            List<Invoice> unpaidInvoices = (List<Invoice>) boundedRows(
                'SELECT Id, Balance, TotalAmount, DueDate FROM Invoice WHERE ' + invWhere,
                new Map<String, Object>{ 'accountId' => accountId, 'currencyCode' => currencyCode }, 'unpaid invoices');
            tallyInvoices(data, unpaidInvoices, Date.today());
            sumUnpaidInvoiceBalance = data.receivablesOutstanding;
        } catch (Exception e) {
            // A refused or failed Invoice read is not "nothing owed": the invoice figures are
            // marked unavailable (null) and the other components still load.
            sectionSkipped('getDashboardCards', e);
            markInvoicesUnavailable(data, e);
        }

        // Each component is null when its read was refused, failed or found too many rows (the catch blocks
        // of getUnappliedCreditsSum, getDebitMemoNotInvoicedSum, getUnappliedPaymentBalanceSum and
        // getUnappliedPaymentCount, and the Invoice catch above), which list it in data.unavailable with
        // its reason. There is no total without the unpaid invoices; without another component it is a
        // partial total the page labels (totalUp). The payment count is its own key: a failed count leaves
        // the payment balance, the total and the note as they are.
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

        // Each builder catches its own reads and marks its tab. Anything that still escapes one is not an empty
        // tab either: the catch here marks that tab unavailable too (reasonFor: failed for an unexpected error),
        // and the next tab is still built.
        try {
            failIfForced(WORKLIST_CRITICAL);
            buildCriticalFollowUpInvoices(wl, invAccountField, filterAccount, filterCurrency, accountId, currencyCode, thirtyDaysAgo);
        } catch (Exception e) { sectionSkipped('getWorklist', e); markWorklistUnavailable(wl, WORKLIST_CRITICAL, e); }
        try {
            failIfForced(WORKLIST_HIGH_VALUE);
            buildHighValueDelinquents(wl, invAccountField, filterAccount, filterCurrency, accountId, currencyCode, thirtyDaysAgo);
        } catch (Exception e) { sectionSkipped('getWorklist', e); markWorklistUnavailable(wl, WORKLIST_HIGH_VALUE, e); }
        try {
            failIfForced(WORKLIST_DISPUTED);
            buildDisputedFromCases(wl, invAccountField, filterAccount, filterCurrency, accountId, currencyCode);
        } catch (Exception e) { sectionSkipped('getWorklist', e); markWorklistUnavailable(wl, WORKLIST_DISPUTED, e); }
        // Each tab shows exactly what its own reads return: rows, or none ("No items in this view"), or
        // unavailable with its reason.
        return wl;
    }

    // Keys of WorklistData.unavailable, one per worklist tab: the read the section is built from was
    // refused or failed, so its list is not "nothing to work on" (todo 435).
    @TestVisible private static final String WORKLIST_CRITICAL = 'critical';
    @TestVisible private static final String WORKLIST_HIGH_VALUE = 'highValue';
    @TestVisible private static final String WORKLIST_DISPUTED = 'disputed';

    // An unavailable tab carries no rows: any it added before the failure are dropped, not shown as the list.
    private static void markWorklistUnavailable(WorklistData wl, String key, Exception e) {
        if (!wl.unavailable.contains(key)) {
            wl.unavailable.add(key);
        }
        wl.unavailableReason.put(key, reasonFor(e));
        if (key == WORKLIST_CRITICAL) wl.criticalFollowUpInvoices.clear();
        if (key == WORKLIST_HIGH_VALUE) wl.highValueDelinquents.clear();
        if (key == WORKLIST_DISPUTED) wl.disputedInvoices.clear();
        Integer moreAt = wl.hasMore.indexOf(key);
        if (moreAt >= 0) wl.hasMore.remove(moreAt);
    }

    // Test seam: a test names the steps that throw, to prove a failure there marks its tab rather than
    // leaving it empty. Never set outside tests.
    @TestVisible private static Set<String> forcedFailures = new Set<String>();

    @TestVisible
    private class ForcedFailureException extends Exception {}

    private static void failIfForced(String step) {
        if (forcedFailures.contains(step)) {
            throw new ForcedFailureException('Forced failure at ' + step);
        }
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
            // Every plan in scope, bounded (a cut list of plans would hide their tasks without saying so).
            List<Id> cpIds = new List<Id>();
            for (SObject cp : boundedRows('SELECT Id FROM CollectionPlan WHERE ' + cpWhere,
                    new Map<String, Object>{ 'accountId' => accountId }, 'collection plans')) {
                cpIds.add((Id) cp.get('Id'));
            }
            if (cpIds.isEmpty()) return taskList;
            // One more than the list shows, so a list with more tasks says so instead of reading as all of them.
            Integer taskReadLimit = TASK_ROWS + 1;
            for (Task t : [SELECT Id, Subject, Status, ActivityDate, WhatId FROM Task WHERE WhatId IN :cpIds WITH USER_MODE ORDER BY ActivityDate DESC NULLS LAST, CreatedDate DESC LIMIT :taskReadLimit]) {
                results.add(new CpTaskItem(t.Id, t.Subject, t.Status, t.ActivityDate, t.WhatId));
            }
            taskList.hasMore = keepFirst(results, TASK_ROWS);
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
        // True when there are more tasks than the TASK_ROWS listed (latest due first).
        @AuraEnabled public Boolean hasMore { get; set; }
        public CpTaskList() {
            items = new List<CpTaskItem>();
            unavailable = false;
            hasMore = false;
        }
    }

    // How many rows each short list shows. Each is read one row longer, so a list with more says so
    // (hasMore) instead of reading as complete.
    @TestVisible private static Integer TASK_ROWS = 200;
    @TestVisible private static Integer MY_PLAN_ROWS = 50;
    @TestVisible private static Integer CRITICAL_ROWS = 200;

    // Keeps the first `count` rows of a list read one row longer; true when there was more.
    @TestVisible
    private static Boolean keepFirst(List<Object> rows, Integer count) {
        if (rows.size() <= count) return false;
        while (rows.size() > count) {
            rows.remove(rows.size() - 1);
        }
        return true;
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
            List<Invoice> invs = Database.query(invSelect + ' FROM Invoice WHERE ' + invWhere + ' ORDER BY ' + orderField
                + ' LIMIT ' + (CRITICAL_ROWS + 1), AccessLevel.USER_MODE);
            if (keepFirst(invs, CRITICAL_ROWS)) wl.hasMore.add(WORKLIST_CRITICAL);
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
                for (SObject row : boundedRows('SELECT InvoiceId, CollectionPlanId FROM CollectionPlanItem WHERE InvoiceId IN :invoiceIds AND CollectionPlanId != null',
                        new Map<String, Object>{ 'invoiceIds' => invoiceIds }, 'collection plan items')) {
                    CollectionPlanItem cpi = (CollectionPlanItem) row;
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
            // A plan lookup that was refused, failed or found too many rows is not "no plan": no Create.
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
        // The read and the rows built from it share one catch, as the Critical and Disputed tabs do: a failure
        // anywhere in the tab marks it unavailable instead of leaving it empty.
        try {
            List<Invoice> invs = (List<Invoice>) boundedRows('SELECT Id, Balance, DueDate, ' + invAccountField + ' FROM Invoice WHERE ' + invWhere,
                new Map<String, Object>{ 'accountId' => accountId, 'currencyCode' => currencyCode, 'thirtyDaysAgo' => thirtyDaysAgo },
                'high-value invoices');
            addHighValueDelinquents(wl, invs, invAccountField, Date.today());
        } catch (Exception e) {
            sectionSkipped('buildHighValueDelinquents', e);
            markWorklistUnavailable(wl, WORKLIST_HIGH_VALUE, e);
        }
    }

    // Rolls the queried invoices up by account and adds the ten largest balances of 2000 or more,
    // with each account's collection plan. Takes rows so a test can pass invoices, which Apex
    // cannot insert.
    @TestVisible
    private static void addHighValueDelinquents(WorklistData wl, List<Invoice> invs, String invAccountField, Date today) {
        failIfForced('highValueRows');
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
        // Only the ten largest balances are listed, so only their names and plans are looked up: the reads
        // stay at ten ids however many accounts qualify.
        List<WorklistItem> ranked = new List<WorklistItem>();
        for (Id accId : qualifiedAccounts) {
            ranked.add(new WorklistItem(accId, null, accountBalance.get(accId), accountMaxDays.get(accId), 'highValue', 'red', null, null));
        }
        sortByBalance(ranked);
        List<WorklistItem> listed = new List<WorklistItem>();
        Set<Id> listedIds = new Set<Id>();
        for (Integer i = 0; i < Math.min(HIGH_VALUE_ROWS, ranked.size()); i++) {
            listed.add(ranked[i]);
            listedIds.add(ranked[i].accountId);
        }
        if (ranked.size() > HIGH_VALUE_ROWS) wl.hasMore.add(WORKLIST_HIGH_VALUE);
        Map<Id, String> accountNames = getAccountNames(listedIds);
        Map<Id, Id> accountToCollectionPlan = new Map<Id, Id>();
        Boolean planLookupFailed = false;
        if (Schema.getGlobalDescribe().containsKey('CollectionPlan')) {
            try {
                for (SObject cp : boundedRows('SELECT Id, AccountId FROM CollectionPlan WHERE AccountId IN :listedIds AND AccountId != null',
                        new Map<String, Object>{ 'listedIds' => listedIds }, 'collection plans')) {
                    Id planAccountId = (Id) cp.get('AccountId');
                    if (!accountToCollectionPlan.containsKey(planAccountId)) {
                        accountToCollectionPlan.put(planAccountId, (Id) cp.get('Id'));
                    }
                }
            } catch (Exception ex) { sectionSkipped('addHighValueDelinquents', ex); planLookupFailed = true; }
        }
        for (WorklistItem item : listed) {
            String name = accountNames.get(item.accountId);
            item.accountName = name != null ? name : '—';
            item.collectionPlanId = accountToCollectionPlan.get(item.accountId);
            // A plan lookup that was refused, failed or found too many rows is not "no plan": no Create.
            item.collectionPlanUnavailable = planLookupFailed;
            wl.highValueDelinquents.add(item);
        }
    }

    // The High-Value tab lists this many accounts, largest balance first.
    @TestVisible private static Integer HIGH_VALUE_ROWS = 10;

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
            // The bulk read carries no text: each account's newest open case is picked from ids alone, and only
            // those cases' subject, description and reason are read (readDisputeReasons). A Description can be
            // 32,000 characters, so the open cases' text read in bulk could pass the heap limit on its own.
            Map<Id, Case> shownCaseByAccount = new Map<Id, Case>();
            List<Id> disputedAccountOrder = new List<Id>();
            List<Case> openCases = (List<Case>) boundedRows('SELECT Id, CaseNumber, AccountId FROM Case WHERE ' + caseWhere + ' ORDER BY CreatedDate DESC',
                new Map<String, Object>{ 'accountId' => accountId }, 'open cases');
            for (Case c : openCases) {
                if (c.AccountId != null && !shownCaseByAccount.containsKey(c.AccountId)) {
                    shownCaseByAccount.put(c.AccountId, c);
                    disputedAccountOrder.add(c.AccountId);
                }
            }
            openCases = null;
            if (disputedAccountOrder.isEmpty()) return;
            // More disputed accounts than the tab lists is too many (narrow by account), not a list cut short.
            requireWithin(disputedAccountOrder.size(), DISPUTED_ROWS, 'disputed accounts');
            Set<Id> disputedAccountIds = new Set<Id>(disputedAccountOrder);
            Map<Id, String> accountDisputeReason = readDisputeReasons(shownCaseByAccount.values());
            Map<Id, String> accountNames = getAccountNames(disputedAccountIds);
            Date today = Date.today();

            // A refused Invoice read throws here and is caught at the end of this method, which drops the
            // whole disputed section and marks it unavailable (WORKLIST_DISPUTED): a row without its invoice
            // rollup would carry a zero balance and no days overdue, which reads as a real "nothing owed".
            String invWhere = ' Balance > 0 AND ' + invAccountField + ' IN :disputedAccountIds ';
            // The page's currency filter applies to the rollup, as it does to every other invoice read.
            if (filterCurrency && invoiceHasCurrencyField()) invWhere += ' AND CurrencyIsoCode = :currencyCode ';
            Map<Id, Decimal> accountBalance = new Map<Id, Decimal>();
            Map<Id, Integer> accountMaxDaysOverdue = new Map<Id, Integer>();
            Map<Id, Id> invoiceToAccountId = new Map<Id, Id>();
            Set<Id> invoiceIds = new Set<Id>();
            // The rows are held only for this loop (the rollup keeps sums and ids), not into the lookups below.
            for (Invoice inv : (List<Invoice>) boundedRows('SELECT Id, Balance, DueDate, ' + invAccountField + ' FROM Invoice WHERE ' + invWhere,
                    new Map<String, Object>{ 'disputedAccountIds' => disputedAccountIds, 'currencyCode' => currencyCode }, 'disputed invoices')) {
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
                    accountPtpDate = latestPromiseDates(schedulesForInvoices(invoiceIds), invoiceToAccountId);
                } catch (Exception e) { sectionSkipped('buildDisputedFromCases', e); ptpLookupFailed = true; }
            }

            for (Id accId : disputedAccountOrder) {
                Decimal bal = accountBalance.get(accId) != null ? accountBalance.get(accId) : 0;
                Integer daysOverdue = accountMaxDaysOverdue.get(accId);
                Date ptpDate = accountPtpDate.get(accId);
                WorklistItem item = new WorklistItem(accId, accountNames.get(accId), bal, daysOverdue, 'disputed', 'amber', ptpDate, accountDisputeReason.get(accId));
                item.caseId = shownCaseByAccount.get(accId).Id;
                item.caseNumber = shownCaseByAccount.get(accId).CaseNumber;
                // A promise lookup that was refused, failed or found too many rows is not "no promise".
                item.ptpUnavailable = ptpLookupFailed;
                wl.disputedInvoices.add(item);
            }
        } catch (Exception e) {
            sectionSkipped('buildDisputedFromCases', e);
            markWorklistUnavailable(wl, WORKLIST_DISPUTED, e);
        }
    }

    // The payment schedules of the disputed accounts' invoices, by schedule id: the invoice each one is for.
    // Bounded; separate from latestPromiseDates so a test can run each read without invoices, which Apex
    // cannot insert.
    @TestVisible
    private static Map<Id, Id> schedulesForInvoices(Set<Id> invoiceIds) {
        List<Id> invIdList = new List<Id>(invoiceIds);
        Map<Id, Id> scheduleToInvoiceId = new Map<Id, Id>();
        for (SObject ps : boundedRows('SELECT Id, ReferenceEntityId FROM PaymentSchedule WHERE ReferenceEntityId IN :invIdList',
                new Map<String, Object>{ 'invIdList' => invIdList }, 'payment schedules')) {
            Id refId = (Id) ps.get('ReferenceEntityId');
            if (refId != null) scheduleToInvoiceId.put((Id) ps.get('Id'), refId);
        }
        return scheduleToInvoiceId;
    }

    // Each account's latest promise-to-pay date: the latest target processing date among its invoices'
    // payment schedule items. Bounded.
    @TestVisible
    private static Map<Id, Date> latestPromiseDates(Map<Id, Id> scheduleToInvoiceId, Map<Id, Id> invoiceToAccountId) {
        Map<Id, Date> accountPtpDate = new Map<Id, Date>();
        if (scheduleToInvoiceId.isEmpty()) return accountPtpDate;
        Set<Id> scheduleIds = scheduleToInvoiceId.keySet();
        for (SObject row : boundedRows('SELECT Id, PaymentScheduleId, TargetPaymentProcessingDate FROM PaymentScheduleItem WHERE PaymentScheduleId IN :scheduleIds AND TargetPaymentProcessingDate != null',
                new Map<String, Object>{ 'scheduleIds' => scheduleIds }, 'payment schedule items')) {
            PaymentScheduleItem psi = (PaymentScheduleItem) row;
            Id accId = invoiceToAccountId.get(scheduleToInvoiceId.get(psi.PaymentScheduleId));
            if (accId == null) continue;
            Date d = psi.TargetPaymentProcessingDate;
            Date existing = accountPtpDate.get(accId);
            if (existing == null || (d != null && d > existing)) accountPtpDate.put(accId, d);
        }
        return accountPtpDate;
    }

    // The Disputed tab lists at most this many accounts (newest open case first). More is too many: the tab
    // reads each listed account's case text, which only a bounded number of accounts keeps within the heap.
    @TestVisible private static Integer DISPUTED_ROWS = 200;
    // Case text is read this many cases at a time, and only a 200-character excerpt is kept. Measured on a 264
    // org (2026-11-26): 200 cases with 32,000-character descriptions (the field's maximum) take 6.4 MB of heap
    // as one list, over the 6 MB synchronous limit, and a one-row SOQL for loop peaks at the same 6.46 MB
    // (it fetches 200 rows at a time). Read 50 per query as here, the same 200 cases peaked at 1.65 MB and the
    // excerpts kept took 48 KB.
    @TestVisible private static Integer DESCRIPTION_BATCH = 50;

    // Each shown case's dispute reason by account: its subject, a 200-character excerpt of its description,
    // and its reason, or 'Open case'. Reads DESCRIPTION_BATCH cases per query, so a query's rows stay small
    // whatever the descriptions hold.
    @TestVisible
    private static Map<Id, String> readDisputeReasons(List<Case> shownCases) {
        Map<Id, Id> accountByCase = new Map<Id, Id>();
        for (Case c : shownCases) {
            accountByCase.put(c.Id, c.AccountId);
        }
        requireWithin(accountByCase.size(), rowAllowance(), 'cases');
        String fields = 'Id, Subject, Description';
        if (Schema.SObjectType.Case.fields.getMap().containsKey('Reason')) fields += ', Reason';
        List<Id> caseIds = new List<Id>(accountByCase.keySet());
        Map<Id, String> reasons = new Map<Id, String>();
        for (Integer start = 0; start < caseIds.size(); start += DESCRIPTION_BATCH) {
            List<Id> batch = new List<Id>();
            for (Integer i = start; i < Math.min(start + DESCRIPTION_BATCH, caseIds.size()); i++) {
                batch.add(caseIds[i]);
            }
            for (Case c : (List<Case>) Database.queryWithBinds('SELECT ' + fields + ' FROM Case WHERE Id IN :batch',
                    new Map<String, Object>{ 'batch' => batch }, AccessLevel.USER_MODE)) {
                reasons.put(accountByCase.get(c.Id), disputeReason(c));
            }
        }
        return reasons;
    }

    private static String disputeReason(Case c) {
        String reason = '';
        if (String.isNotBlank(c.Subject)) reason = c.Subject;
        if (String.isNotBlank(c.Description)) reason += (String.isNotBlank(reason) ? ' – ' : '') + (c.Description.length() > 200 ? c.Description.substring(0, 200) + '...' : c.Description);
        try { if (c.get('Reason') != null) reason += (String.isNotBlank(reason) ? ' [' : '') + String.valueOf(c.get('Reason')) + (String.isNotBlank(reason) ? ']' : ''); } catch (Exception e) { probeSkipped('disputeReason', e); }
        return String.isNotBlank(reason) ? reason : 'Open case';
    }

    // Every catch (Exception) in this class is one of two kinds, named by the helper it calls:
    //  - probeSkipped: guards a describe or field-presence probe (does Invoice have this field, is
    //    Case.Reason in the query). The field being absent is the normal case in some orgs; nothing
    //    is read from the database, so a permission refusal cannot land here.
    //  - sectionSkipped: everything that reads records, including the reads of objects whose
    //    existence was checked first (CollectionPlan, CollectionPlanItem, PaymentSchedule,
    //    CurrencyType). A refused, failed or too-many read marks that section unavailable while the
    //    others still load, and is logged at WARN; it is a permission or data problem, not an absent schema.
    //    Where the section is a figure (the cards and total balance, payment promises, progress), it is
    //    returned as unavailable (null, or the wrapper's unavailable flag or list), never as a zero the
    //    page would show as a real amount (todo 435). The lists follow the same rule: the task, plan and
    //    promise wrappers carry an unavailable flag, and a worklist tab whose read was refused or failed is
    //    listed in WorklistData.unavailable. Each carries its reason (reasonFor: refused, failed or tooMany).
    // Neither throws and neither puts platform exception text in a response.
    private static void probeSkipped(String context, Exception e) {
        System.debug(LoggingLevel.FINE, 'RLM_CollectionsDashboardController.' + context + ' (field or object not present): ' + e.getMessage());
    }

    // Why a section is unavailable, so the page can tell the user what to do: 'refused' when the user may
    // not read it (ask an administrator), 'tooMany' when a bounded read found more rows than it may take
    // (narrow the filters), 'failed' for anything else (try again). Measured on a 264 org
    // (2026-11-26, todo 435): a USER_MODE read of an object the user cannot read throws a QueryException
    // "sObject type 'X' is not supported", and of a field the user cannot read "No such column 'F' on
    // entity 'X'". Any other exception (a timeout, a limit, a platform error) is a failure, not a refusal.
    @TestVisible private static final String REASON_REFUSED = 'refused';
    @TestVisible private static final String REASON_FAILED = 'failed';
    // More rows than a bounded read may take: narrow the filters (todo 435).
    @TestVisible private static final String REASON_TOO_MANY = 'tooMany';

    // Bounded reads (todo 435). Every record read and every summing aggregate in this class goes through
    // boundedRows or boundedAggregate, except the reads that carry their own small LIMIT (the critical
    // follow-up invoices, the tasks and getMyCollectionPlans' plans, each read one row past what it lists so
    // the page can say there are more (CRITICAL_ROWS, TASK_ROWS, MY_PLAN_ROWS); the 500 account options), the
    // active currencies, the payment count (COUNT(Id): one query row) and the account names, which
    // getAccountNames checks against the same allowance. A read that finds more rows
    // than it may take makes its section unavailable as REASON_TOO_MANY, instead of a figure or list built
    // from a cut-off read, and instead of the 50,000-row query limit of a transaction, whose LimitException
    // no catch block can handle and which would fail the whole call. Each read may take the lesser of:
    //  - ROW_CAP rows. Heap measured on a 264 org (2026-11-26), against the 6 MB synchronous limit: 10,001
    //    invoice rows with the five fields the invoice reads select take about 1.34 MB; 10,001 case rows with
    //    the three fields the open-case read selects (no text) about 1.0 MB. Case text: DESCRIPTION_BATCH.
    //  - the rows the transaction has left, less ROW_HEADROOM. A read with an allowance of zero runs no query.
    //    So whatever the data, the bounded reads of one call stop at 50,000 - ROW_HEADROOM + 1 query rows
    //    (a read takes at most its allowance plus one row, after which every later bounded read has none and
    //    is too many without querying), and the only fixed reads after them, the payment count (one row) and
    //    the plan tasks (TASK_ROWS + 1 = 201 rows), keep the call under 49,250.
    // Query-row costs measured on the same org: a row read costs one per row returned; SUM costs one per row
    // it adds up, with or without GROUP BY; COUNT() and COUNT(Id) cost one; GROUP BY COUNT(Id) one per group.
    // So boundedAggregate counts the rows first (one query row) and adds them up only within the bound.
    @TestVisible private static Integer ROW_CAP = 10000;
    @TestVisible private static final Integer ROW_HEADROOM = 1000;

    // The bounded reads a call made, by label: read by the tests, so each caller is proven to be bounded.
    @TestVisible private static Set<String> boundedReads = new Set<String>();

    @TestVisible
    private class TooManyRowsException extends Exception {}

    // How many rows the next read may return: ROW_CAP, or what the transaction has left less ROW_HEADROOM,
    // whichever is less (never below zero).
    @TestVisible
    private static Integer rowAllowance(Integer cap, Integer limitRows, Integer usedRows) {
        return Math.max(0, Math.min(cap, limitRows - usedRows - ROW_HEADROOM));
    }

    private static Integer rowAllowance() {
        return rowAllowance(ROW_CAP, Limits.getLimitQueryRows(), Limits.getQueryRows());
    }

    // A read that found more rows than it was allowed cannot be summed or listed: anything built from the
    // rows that were read would be wrong.
    @TestVisible
    private static void requireWithin(Integer rowCount, Integer allowed, String what) {
        if (rowCount > allowed) {
            throw new TooManyRowsException('More than ' + allowed + ' ' + what + ' to read.');
        }
    }

    // The next read's allowance; with none left the read is too many without querying, so a call whose rows
    // are spent runs no further query (a LIMIT 1 read would still cost a row).
    private static Integer requireAllowance(String what) {
        Integer allowed = rowAllowance();
        if (allowed == 0) {
            throw new TooManyRowsException('No query rows left to read ' + what + '.');
        }
        return allowed;
    }

    // A record read, bounded: LIMIT one more than allowed, so a read with too many rows is seen as one.
    private static List<SObject> boundedRows(String soql, Map<String, Object> binds, String what) {
        boundedReads.add(what);
        Integer allowed = requireAllowance(what);
        List<SObject> rows = Database.queryWithBinds(soql + ' LIMIT ' + (allowed + 1), binds, AccessLevel.USER_MODE);
        requireWithin(rows.size(), allowed, what);
        return rows;
    }

    // An aggregate that adds rows up, bounded: COUNT() the rows first (one query row), then aggregate them.
    private static List<AggregateResult> boundedAggregate(String fromWhere, String selectList, String groupBy,
            Map<String, Object> binds, String what) {
        boundedReads.add(what);
        Integer allowed = requireAllowance(what);
        Integer rowCount = Database.countQueryWithBinds('SELECT COUNT() ' + fromWhere + ' LIMIT ' + (allowed + 1), binds,
            AccessLevel.USER_MODE);
        requireWithin(rowCount, allowed, what);
        return (List<AggregateResult>) Database.queryWithBinds('SELECT ' + selectList + ' ' + fromWhere + groupBy, binds,
            AccessLevel.USER_MODE);
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
    // dropped by the caller's catch. The read returns at most one row per id, so the ids are checked against
    // the same allowance as a bounded read.
    private static Map<Id, String> getAccountNames(Set<Id> accountIds) {
        requireWithin(accountIds.size(), rowAllowance(), 'accounts');
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

    // Largest balance first. A sort, not pairwise swaps: the roll-up can rank thousands of accounts.
    private static void sortByBalance(List<WorklistItem> items) {
        items.sort(new LargestBalanceFirst());
    }

    private class LargestBalanceFirst implements System.Comparator<WorklistItem> {
        public Integer compare(WorklistItem a, WorklistItem b) {
            Decimal balanceA = a.balance != null ? a.balance : 0;
            Decimal balanceB = b.balance != null ? b.balance : 0;
            return balanceA == balanceB ? 0 : (balanceB > balanceA ? 1 : -1);
        }
    }

    public class WorklistData {
        @AuraEnabled public List<CriticalFollowUpInvoiceItem> criticalFollowUpInvoices { get; set; }
        @AuraEnabled public List<WorklistItem> highValueDelinquents { get; set; }
        @AuraEnabled public List<WorklistItem> disputedInvoices { get; set; }
        // Tabs whose read was refused, failed or found too many rows (WORKLIST_*): their lists are not "none".
        @AuraEnabled public List<String> unavailable { get; set; }
        // Each unavailable tab's reason: REASON_REFUSED, REASON_FAILED or REASON_TOO_MANY.
        @AuraEnabled public Map<String, String> unavailableReason { get; set; }
        // Tabs with more rows than they list (WORKLIST_*): Critical's CRITICAL_ROWS most overdue invoices,
        // High-Value's HIGH_VALUE_ROWS largest balances. The page says the list is the first of more.
        @AuraEnabled public List<String> hasMore { get; set; }
        public WorklistData() { criticalFollowUpInvoices = new List<CriticalFollowUpInvoiceItem>(); highValueDelinquents = new List<WorklistItem>(); disputedInvoices = new List<WorklistItem>(); unavailable = new List<String>(); unavailableReason = new Map<String, String>(); hasMore = new List<String>(); }
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
            String fromWhere = 'FROM Payment WHERE Balance > 0 AND Status = \'' + PROCESSED_PAYMENT + '\' ';
            if (Schema.SObjectType.Payment.fields.getMap().containsKey('Type')) {
                fromWhere += ' AND (Type = \'Credit\' OR Type = \'Credit Memo\') ';
            }
            if (accountId != null && String.isNotBlank(String.valueOf(accountId)) && accFld != null) {
                fromWhere += ' AND ' + accFld + ' = :accountId ';
            }
            if (String.isNotBlank(currencyCode) && paymentHasCurrencyField()) fromWhere += ' AND CurrencyIsoCode = :currencyCode ';
            List<AggregateResult> ar = boundedAggregate(fromWhere, 'SUM(Balance) sumBal', '',
                new Map<String, Object>{ 'accountId' => accountId, 'currencyCode' => currencyCode }, 'unapplied credits');
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
            String fromWhere = 'FROM DebitMemo WHERE TotalAmount != null'
                + ' AND Status = \'Posted\' ';
            if (flds.containsKey('InvoiceGenerationStatus')) {
                fromWhere += ' AND InvoiceGenerationStatus != \'Posted Invoice Generated\' ';
            }
            if (accountId != null && accFld != null) fromWhere += ' AND ' + accFld + ' = :accountId ';
            if (String.isNotBlank(currencyCode) && flds.containsKey('CurrencyIsoCode')) fromWhere += ' AND CurrencyIsoCode = :currencyCode ';
            List<AggregateResult> ar = boundedAggregate(fromWhere, 'SUM(TotalAmount) sumAmt', '',
                new Map<String, Object>{ 'accountId' => accountId, 'currencyCode' => currencyCode }, 'debit memos');
            if (!ar.isEmpty() && ar[0].get('sumAmt') != null) sum = (Decimal) ar[0].get('sumAmt');
        } catch (Exception e) { sectionSkipped('getDebitMemoNotInvoicedSum', e); markUnavailable(data, UNAVAILABLE_DEBIT_MEMOS, e); return null; }
        return sum;
    }

    private static Decimal getUnappliedPaymentBalanceSum(CollectionsDashboardData data, Id accountId, String currencyCode) {
        Decimal sum = 0;
        try {
            String accFld = getPaymentAccountFieldName();
            String fromWhere = 'FROM Payment WHERE Balance > 0 AND Status = \'' + PROCESSED_PAYMENT + '\' ';
            if (Schema.SObjectType.Payment.fields.getMap().containsKey('Type')) {
                fromWhere += ' AND (Type != \'Credit\' AND Type != \'Credit Memo\') ';
            }
            if (accountId != null && String.isNotBlank(String.valueOf(accountId)) && accFld != null) {
                fromWhere += ' AND ' + accFld + ' = :accountId ';
            }
            if (String.isNotBlank(currencyCode) && paymentHasCurrencyField()) fromWhere += ' AND CurrencyIsoCode = :currencyCode ';
            List<AggregateResult> ar = boundedAggregate(fromWhere, 'SUM(Balance) sumBal', '',
                new Map<String, Object>{ 'accountId' => accountId, 'currencyCode' => currencyCode }, 'unapplied payments');
            if (!ar.isEmpty() && ar[0].get('sumBal') != null) sum = (Decimal) ar[0].get('sumBal');
        } catch (Exception e) { sectionSkipped('getUnappliedPaymentBalanceSum', e); markUnavailable(data, UNAVAILABLE_PAYMENTS, e); return null; }
        return sum;
    }

    private static Integer getUnappliedPaymentCount(CollectionsDashboardData data, Id accountId, String currencyCode) {
        Integer cnt = 0;
        try {
            String accFld = getPaymentAccountFieldName();
            // COUNT(Id) costs one query row however many it counts (measured): no bound needed.
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
        // Components whose read was refused, failed or found too many rows (UNAVAILABLE_*); their figures are null.
        @AuraEnabled public List<String> unavailable { get; set; }
        // Each unavailable key's reason: REASON_REFUSED, REASON_FAILED or REASON_TOO_MANY.
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
            String q = 'SELECT ' + selectFields + ' FROM CollectionPlan WHERE OwnerId = :currentUserId ORDER BY Duedate ASC NULLS LAST, Name ASC'
                + ' LIMIT ' + (MY_PLAN_ROWS + 1);
            List<SObject> plans = Database.query(q, AccessLevel.USER_MODE);
            planList.hasMore = keepFirst(plans, MY_PLAN_ROWS);
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
        // True when the user owns more plans than the MY_PLAN_ROWS listed (soonest due first).
        @AuraEnabled public Boolean hasMore { get; set; }
        public MyCollectionPlanList() {
            items = new List<MyCollectionPlanItem>();
            unavailable = false;
            hasMore = false;
        }
    }

    @AuraEnabled(cacheable=true)
    public static CollectionsProgressData getCollectionsProgress() {
        CollectionsProgressData result = new CollectionsProgressData();
        try {
            if (!Schema.getGlobalDescribe().containsKey('CollectionPlan')) return result;
            List<CollectionPlan> plans = (List<CollectionPlan>) boundedRows(
                'SELECT Id, ClosedDate, CreatedDate, TotalInvoiceBalance, DaysPastDue, Duedate FROM CollectionPlan',
                new Map<String, Object>(), 'collection plans');
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
        // Why it is unavailable: REASON_REFUSED, REASON_FAILED or REASON_TOO_MANY (null when it is not).
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