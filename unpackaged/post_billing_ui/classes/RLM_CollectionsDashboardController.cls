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
        for (Account a : [SELECT Id, Name FROM Account ORDER BY Name LIMIT 500]) {
            options.add(new Map<String, String>{ 'value' => a.Id, 'label' => a.Name });
        }
        return options;
    }

    /** Payment Promises: total requested amount on PaymentScheduleItem by status (Ready for Processing, Draft, Failed, In Processing). */
    @AuraEnabled(cacheable=true)
    public static List<PaymentPromiseBucket> getPaymentPromiseSummary(Id accountId, String currencyCode) {
        List<PaymentPromiseBucket> buckets = new List<PaymentPromiseBucket>();
        try {
            if (!Schema.getGlobalDescribe().containsKey('PaymentScheduleItem')) return buckets;
            Map<String, Schema.SObjectField> psiFields = Schema.getGlobalDescribe().get('PaymentScheduleItem').getDescribe().fields.getMap();
            if (!psiFields.containsKey('Status') || !psiFields.containsKey('RequestedAmount')) return buckets;
            String accFld = psiFields.containsKey('PaymentAccountId') ? 'PaymentAccountId' : null;
            Boolean filterAccount = accountId != null && String.isNotBlank(String.valueOf(accountId)) && accFld != null;
            Boolean filterCurrency = String.isNotBlank(currencyCode) && paymentScheduleItemHasCurrencyField();
            String soql = 'SELECT Status, SUM(RequestedAmount) totalAmt, COUNT(Id) cnt FROM PaymentScheduleItem WHERE Status IN (\'Ready for Processing\', \'Draft\', \'Failed\', \'Processing\') ';
            if (filterAccount) soql += ' AND PaymentAccountId = :accountId ';
            if (filterCurrency) soql += ' AND CurrencyIsoCode = :currencyCode ';
            soql += ' GROUP BY Status ';
            List<AggregateResult> results = Database.query(soql);
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
        } catch (Exception e) { }
        return buckets;
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
            for (CurrencyType ct : [SELECT IsoCode, IsCorporate FROM CurrencyType WHERE IsActive = true ORDER BY IsCorporate DESC, IsoCode ASC]) {
                if (String.isNotBlank(ct.IsoCode)) {
                    options.add(new Map<String, String>{ 'value' => ct.IsoCode, 'label' => ct.IsoCode });
                }
            }
        } catch (Exception e) { }
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

        // Base invoice filter: unpaid = Balance > 0
        String invWhere = ' Balance > 0 ';
        if (filterAccount && invAccountField != null) {
            invWhere += ' AND ' + invAccountField + ' = :accountId ';
        }
        if (filterCurrency && invoiceHasCurrencyField()) {
            invWhere += ' AND CurrencyIsoCode = :currencyCode ';
        }

        List<Invoice> unpaidInvoices = new List<Invoice>();
        try {
            unpaidInvoices = Database.query('SELECT Id, Balance, TotalAmount, DueDate FROM Invoice WHERE ' + invWhere);
        } catch (Exception e) {
            return data;
        }

        Decimal sumUnpaidInvoiceBalance = 0;
        Decimal sumCurrentDue = 0;
        Decimal sumOverdue = 0;
        Decimal agingCurrent = 0, aging1_30 = 0, aging31_60 = 0, aging61_90 = 0, aging90Plus = 0;
        Integer partiallySettledCount = 0;
        Decimal partiallySettledSum = 0;
        Integer notSettledCount = 0;
        Decimal notSettledSum = 0;
        Date today = Date.today();

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

        Decimal unappliedCredits = getUnappliedCreditsSum(accountId, currencyCode);
        Decimal debitMemoNotInvoiced = getDebitMemoNotInvoicedSum(accountId, currencyCode);
        Decimal unappliedPaymentBalance = getUnappliedPaymentBalanceSum(accountId, currencyCode);
        Integer unappliedPaymentCount = getUnappliedPaymentCount(accountId, currencyCode);

        data.unappliedCredits = unappliedCredits;
        data.unappliedPaymentBalance = unappliedPaymentBalance;
        data.unappliedPaymentCount = unappliedPaymentCount;

        data.totalBalance = sumUnpaidInvoiceBalance + unappliedCredits + debitMemoNotInvoiced - unappliedPaymentBalance;
        data.totalOutstanding = sumUnpaidInvoiceBalance - unappliedPaymentBalance;

        data.totalBalanceBreakdown = new List<Map<String, Object>>();
        data.totalBalanceBreakdown.add(new Map<String, Object>{ 'label' => 'Unpaid Invoices', 'amount' => sumUnpaidInvoiceBalance, 'color' => 'blue' });
        data.totalBalanceBreakdown.add(new Map<String, Object>{ 'label' => 'Unapplied Credits', 'amount' => unappliedCredits, 'color' => 'green' });
        data.totalBalanceBreakdown.add(new Map<String, Object>{ 'label' => 'Debit Memo (not invoiced)', 'amount' => debitMemoNotInvoiced, 'color' => 'orange' });
        data.totalBalanceBreakdown.add(new Map<String, Object>{ 'label' => 'Unapplied Payments', 'amount' => -unappliedPaymentBalance, 'color' => 'red' });

        data.agingBuckets = new List<Map<String, Object>>();
        data.agingBuckets.add(new Map<String, Object>{ 'label' => 'Current', 'amount' => agingCurrent, 'key' => 'current' });
        data.agingBuckets.add(new Map<String, Object>{ 'label' => '1-30', 'amount' => aging1_30, 'key' => '1-30' });
        data.agingBuckets.add(new Map<String, Object>{ 'label' => '31-60', 'amount' => aging31_60, 'key' => '31-60' });
        data.agingBuckets.add(new Map<String, Object>{ 'label' => '61-90', 'amount' => aging61_90, 'key' => '61-90' });
        data.agingBuckets.add(new Map<String, Object>{ 'label' => '90+', 'amount' => aging90Plus, 'key' => '90+' });

        return data;
    }

    @AuraEnabled(cacheable=true)
    public static WorklistData getWorklist(Id accountId, String currencyCode) {
        WorklistData wl = new WorklistData();
        String invAccountField = getInvoiceAccountFieldName();
        Boolean filterAccount = accountId != null && String.isNotBlank(String.valueOf(accountId));
        Boolean filterCurrency = String.isNotBlank(currencyCode);
        Date today = Date.today();
        Date thirtyDaysAgo = today.addDays(-30);

        if (invAccountField != null) {
            try { buildCriticalFollowUpInvoices(wl, invAccountField, filterAccount, filterCurrency, accountId, currencyCode, thirtyDaysAgo); } catch (Exception e) { }
            try { buildHighValueDelinquents(wl, invAccountField, filterAccount, filterCurrency, accountId, currencyCode, thirtyDaysAgo); } catch (Exception e) { }
            try { buildDisputedFromCases(wl, invAccountField, filterAccount, accountId); } catch (Exception e) { }
            try { buildWorklistUnifiedFallback(wl, invAccountField, filterAccount, filterCurrency, accountId, currencyCode, today, thirtyDaysAgo); } catch (Exception e) { }
            if (wl.highValueDelinquents.isEmpty()) {
                try { buildWorklistLastResort(wl, invAccountField, today, thirtyDaysAgo); } catch (Exception e) { }
            }
        } else {
            buildDisputedFromCasesOnly(wl, filterAccount, accountId);
            invAccountField = getInvoiceAccountFieldNameFromDescribe();
            if (invAccountField != null) buildWorklistLastResort(wl, invAccountField, today, thirtyDaysAgo);
        }
        addPlaceholderRowsIfEmpty(wl);
        return wl;
    }

    private static void addPlaceholderRowsIfEmpty(WorklistData wl) {
        List<Account> accts = new List<Account>();
        try {
            accts = [SELECT Id, Name FROM Account ORDER BY Name LIMIT 1];
        } catch (Exception e) { return; }
        if (accts.isEmpty()) return;
        Id placeholderId = accts[0].Id;
        String placeholderName = accts[0].Name;
        if (wl.criticalFollowUpInvoices.isEmpty()) {
            wl.criticalFollowUpInvoices.add(new CriticalFollowUpInvoiceItem(null, 'No invoices overdue >= 30 days', 0, null, null, '—', null, null));
        }
        if (wl.highValueDelinquents.isEmpty()) {
            wl.highValueDelinquents.add(new WorklistItem(placeholderId, '(No high-value delinquents — check Invoice, DueDate & Balance)', 0, null, 'highValue', 'red', null, null));
        }
    }

    @AuraEnabled(cacheable=true)
    public static List<CpTaskItem> getCollectionPlanTasks(Id accountId) {
        List<CpTaskItem> results = new List<CpTaskItem>();
        if (!Schema.getGlobalDescribe().containsKey('CollectionPlan')) return results;
        try {
            String cpWhere = ' Id != null ';
            if (accountId != null && String.isNotBlank(String.valueOf(accountId))) {
                cpWhere += ' AND AccountId = :accountId ';
            }
            List<Id> cpIds = new List<Id>();
            for (SObject cp : Database.query('SELECT Id FROM CollectionPlan WHERE ' + cpWhere + ' LIMIT 2000')) {
                cpIds.add((Id) cp.get('Id'));
            }
            if (cpIds.isEmpty()) return results;
            for (Task t : [SELECT Id, Subject, Status, ActivityDate, WhatId FROM Task WHERE WhatId IN :cpIds ORDER BY ActivityDate DESC NULLS LAST, CreatedDate DESC LIMIT 200]) {
                results.add(new CpTaskItem(t.Id, t.Subject, t.Status, t.ActivityDate, t.WhatId));
            }
        } catch (Exception e) { }
        return results;
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

    private static String getInvoiceAccountFieldNameFromDescribe() {
        try {
            if (!Schema.getGlobalDescribe().containsKey('Invoice')) return null;
            Map<String, Schema.SObjectField> f = Schema.getGlobalDescribe().get('Invoice').getDescribe().fields.getMap();
            if (f != null && f.containsKey('BillingAccountId')) return 'BillingAccountId';
            if (f != null && f.containsKey('BillToAccountId')) return 'BillToAccountId';
            if (f != null && f.containsKey('AccountId')) return 'AccountId';
        } catch (Exception e) { }
        return null;
    }

    private static void buildWorklistLastResort(WorklistData wl, String invAccountField, Date today, Date thirtyDaysAgo) {
        try {
            String soql = 'SELECT Id, Balance, DueDate, ' + invAccountField + ' FROM Invoice WHERE Balance > 0 LIMIT 500';
            List<SObject> rows = Database.query(soql);
            Map<Id, Decimal> accountBalance = new Map<Id, Decimal>();
            Map<Id, Integer> accountMaxDays = new Map<Id, Integer>();
            for (SObject inv : rows) {
                Id accId = (Id) inv.get(invAccountField);
                if (accId == null) continue;
                Decimal bal = inv.get('Balance') != null ? (Decimal) inv.get('Balance') : 0;
                accountBalance.put(accId, accountBalance.get(accId) != null ? accountBalance.get(accId) + bal : bal);
                Object dueObj = inv.get('DueDate');
                Integer days = 0;
                if (dueObj instanceof Date) {
                    Date d = (Date) dueObj;
                    if (d < today) days = d.daysBetween(today);
                }
                Integer existing = accountMaxDays.get(accId);
                if (existing == null || days > existing) accountMaxDays.put(accId, days);
            }
            if (accountBalance.isEmpty()) return;
            List<WorklistItem> items = new List<WorklistItem>();
            Map<Id, String> accountNames = getAccountNames(accountBalance.keySet());
            for (Id accId : accountBalance.keySet()) {
                Integer days = accountMaxDays.get(accId);
                String health = (days != null && days > 30) ? 'red' : (days != null && days > 0 ? 'amber' : 'green');
                items.add(new WorklistItem(accId, accountNames.get(accId), accountBalance.get(accId), days, 'critical', health, null, null));
            }
            sortByBalance(items);
            if (wl.highValueDelinquents.isEmpty()) {
                for (Integer i = 0; i < Math.min(5, items.size()); i++) wl.highValueDelinquents.add(items[i]);
            }
        } catch (Exception e) { }
    }

    private static void buildWorklistUnifiedFallback(WorklistData wl, String invAccountField, Boolean filterAccount, Boolean filterCurrency, Id accountId, String currencyCode, Date today, Date thirtyDaysAgo) {
        if (!wl.highValueDelinquents.isEmpty()) return;
        try {
            String invWhere = ' Balance > 0 ';
            if (filterAccount) invWhere += ' AND ' + invAccountField + ' = :accountId ';
            if (filterCurrency && invoiceHasCurrencyField()) invWhere += ' AND CurrencyIsoCode = :currencyCode ';
            List<Invoice> invs = Database.query('SELECT Id, Balance, DueDate, ' + invAccountField + ' FROM Invoice WHERE ' + invWhere + ' LIMIT 1000');
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
            List<WorklistItem> items = new List<WorklistItem>();
            Map<Id, String> accountNames = getAccountNames(accountBalance.keySet());
            for (Id accId : accountBalance.keySet()) {
                Integer days = accountMaxDays.get(accId);
                String health = (days != null && days > 30) ? 'red' : (days != null && days > 0 ? 'amber' : 'green');
                items.add(new WorklistItem(accId, accountNames.get(accId), accountBalance.get(accId), days, 'critical', health, null, null));
            }
            sortByBalance(items);
            if (wl.highValueDelinquents.isEmpty()) {
                for (Integer i = 0; i < Math.min(5, items.size()); i++) wl.highValueDelinquents.add(items[i]);
            }
        } catch (Exception e) { }
    }

    private static void buildDisputedFromCasesOnly(WorklistData wl, Boolean filterAccount, Id accountId) {
        try {
            String caseWhere = ' IsClosed = false AND AccountId != null ';
            if (filterAccount) caseWhere += ' AND AccountId = :accountId ';
            List<Case> openCases = Database.query('SELECT Id, AccountId, Subject, Description FROM Case WHERE ' + caseWhere + ' ORDER BY CreatedDate DESC LIMIT 200');
            Set<Id> disputedAccountIds = new Set<Id>();
            Map<Id, String> accountDisputeReason = new Map<Id, String>();
            for (Case c : openCases) {
                if (c.AccountId == null) continue;
                disputedAccountIds.add(c.AccountId);
                if (!accountDisputeReason.containsKey(c.AccountId)) {
                    String reason = (c.Subject != null ? c.Subject : '') + (c.Description != null && c.Description.length() > 200 ? ' – ' + c.Description.substring(0, 200) + '...' : (c.Description != null ? ' – ' + c.Description : ''));
                    accountDisputeReason.put(c.AccountId, String.isNotBlank(reason) ? reason : 'Open case');
                }
            }
            if (disputedAccountIds.isEmpty()) return;
            Map<Id, String> accountNames = getAccountNames(disputedAccountIds);
            for (Id accId : disputedAccountIds) {
                wl.disputedInvoices.add(new WorklistItem(accId, accountNames.get(accId), 0, null, 'disputed', 'amber', null, accountDisputeReason.get(accId)));
            }
        } catch (Exception e) { }
    }

    private static Boolean invoiceHasBillToContactId() {
        try {
            return Schema.SObjectType.Invoice.fields.getMap().containsKey('BillToContactId');
        } catch (Exception e) { return false; }
    }

    private static Boolean invoiceHasDaysInvoiceOverdue() {
        try {
            return Schema.SObjectType.Invoice.fields.getMap().containsKey('DaysInvoiceOverdue');
        } catch (Exception e) { return false; }
    }

    private static Boolean invoiceHasBillingAccountId() {
        try {
            return Schema.SObjectType.Invoice.fields.getMap().containsKey('BillingAccountId');
        } catch (Exception e) { return false; }
    }

    private static void buildCriticalFollowUpInvoices(WorklistData wl, String invAccountField, Boolean filterAccount, Boolean filterCurrency, Id accountId, String currencyCode, Date thirtyDaysAgo) {
        try {
            Boolean hasDaysField = invoiceHasDaysInvoiceOverdue();
            Boolean hasBillingAcct = invoiceHasBillingAccountId();
            Boolean hasBillToContact = invoiceHasBillToContactId();
            Integer thirtyDays = 30;

            String invWhere;
            if (hasDaysField) {
                invWhere = ' Balance > 0 AND (DaysInvoiceOverdue >= :thirtyDays OR (DaysInvoiceOverdue = null AND DueDate != null AND DueDate < :thirtyDaysAgo)) ';
            } else {
                invWhere = ' Balance > 0 AND DueDate < :thirtyDaysAgo ';
            }
            if (filterAccount && invAccountField != null) invWhere += ' AND ' + invAccountField + ' = :accountId ';
            if (filterCurrency && invoiceHasCurrencyField()) invWhere += ' AND CurrencyIsoCode = :currencyCode ';

            String invSelect = 'SELECT Id, InvoiceNumber, Balance';
            if (hasDaysField) invSelect += ', DaysInvoiceOverdue';
            invSelect += ', DueDate';
            if (hasBillingAcct) invSelect += ', BillingAccountId';
            if (hasBillToContact) invSelect += ', BillToContactId';

            String orderField = hasDaysField ? 'DaysInvoiceOverdue DESC NULLS LAST' : 'DueDate ASC';
            List<Invoice> invs = Database.query(invSelect + ' FROM Invoice WHERE ' + invWhere + ' ORDER BY ' + orderField + ' LIMIT 200');

            Set<Id> billingAccountIds = new Set<Id>();
            for (Invoice inv : invs) {
                if (hasBillingAcct && inv.get('BillingAccountId') != null) {
                    billingAccountIds.add((Id) inv.get('BillingAccountId'));
                }
            }
            Map<Id, String> accountNames = getAccountNames(billingAccountIds);

            Set<Id> invoiceIds = new Set<Id>();
            for (Invoice inv : invs) {
                if (inv.Id != null) invoiceIds.add(inv.Id);
            }
            Map<Id, Id> invoiceToCollectionPlan = new Map<Id, Id>();
            if (!invoiceIds.isEmpty() && Schema.getGlobalDescribe().containsKey('CollectionPlanItem')) {
                try {
                    for (CollectionPlanItem cpi : [SELECT InvoiceId, CollectionPlanId FROM CollectionPlanItem WHERE InvoiceId IN :invoiceIds AND CollectionPlanId != null]) {
                        if (!invoiceToCollectionPlan.containsKey(cpi.InvoiceId)) {
                            invoiceToCollectionPlan.put(cpi.InvoiceId, cpi.CollectionPlanId);
                        }
                    }
                } catch (Exception ex) { }
            }

            Date today = Date.today();
            for (Invoice inv : invs) {
                Integer daysOverdue;
                if (hasDaysField && inv.get('DaysInvoiceOverdue') != null) {
                    daysOverdue = (Integer) inv.get('DaysInvoiceOverdue');
                } else {
                    daysOverdue = inv.DueDate != null ? inv.DueDate.daysBetween(today) : null;
                }
                String invNum = inv.InvoiceNumber != null ? inv.InvoiceNumber : '—';
                Id billingAcctId = hasBillingAcct && inv.get('BillingAccountId') != null ? (Id) inv.get('BillingAccountId') : null;
                String billingAcctName = billingAcctId != null ? accountNames.get(billingAcctId) : null;
                Id billToContactId = hasBillToContact && inv.get('BillToContactId') != null ? (Id) inv.get('BillToContactId') : null;
                Id collectionPlanId = invoiceToCollectionPlan.get(inv.Id);

                wl.criticalFollowUpInvoices.add(new CriticalFollowUpInvoiceItem(
                    inv.Id, invNum, inv.Balance != null ? inv.Balance : 0,
                    daysOverdue, billingAcctId, billingAcctName, billToContactId, collectionPlanId
                ));
            }
        } catch (Exception e) { }
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

    private static void buildCriticalFollowUpsOverdueFallback(WorklistData wl, String invAccountField, Boolean filterAccount, Boolean filterCurrency, Id accountId, String currencyCode, Date today) {
        try {
            String invWhere = ' Balance > 0 AND (DueDate < :today OR DueDate = null) ';
            if (filterAccount) invWhere += ' AND ' + invAccountField + ' = :accountId ';
            if (filterCurrency && invoiceHasCurrencyField()) invWhere += ' AND CurrencyIsoCode = :currencyCode ';
            List<Invoice> invs = new List<Invoice>();
            try {
                invs = Database.query('SELECT Id, Balance, DueDate, ' + invAccountField + ' FROM Invoice WHERE ' + invWhere);
            } catch (Exception ex) { invs = new List<Invoice>(); }
            if (invs.isEmpty()) {
                invWhere = ' Balance > 0 ';
                if (filterAccount) invWhere += ' AND ' + invAccountField + ' = :accountId ';
                if (filterCurrency && invoiceHasCurrencyField()) invWhere += ' AND CurrencyIsoCode = :currencyCode ';
                try {
                    invs = Database.query('SELECT Id, Balance, DueDate, ' + invAccountField + ' FROM Invoice WHERE ' + invWhere);
                } catch (Exception ex2) { return; }
            }
            Map<Id, Decimal> accountBalance = new Map<Id, Decimal>();
            Map<Id, Integer> accountMaxDays = new Map<Id, Integer>();
            for (Invoice inv : invs) {
                Id accId = (Id) inv.get(invAccountField);
                if (accId == null) continue;
                Decimal bal = inv.Balance != null ? inv.Balance : 0;
                accountBalance.put(accId, accountBalance.get(accId) != null ? accountBalance.get(accId) + bal : bal);
                Integer days = (inv.DueDate != null && inv.DueDate < today) ? inv.DueDate.daysBetween(today) : 0;
                Integer existing = accountMaxDays.get(accId);
                if (existing == null || days > existing) accountMaxDays.put(accId, days);
            }
            List<WorklistItem> items = new List<WorklistItem>();
            Map<Id, String> accountNames = getAccountNames(accountBalance.keySet());
            for (Id accId : accountBalance.keySet()) {
                Integer days = accountMaxDays.get(accId);
                String health = (days != null && days > 30) ? 'red' : 'amber';
                items.add(new WorklistItem(accId, accountNames.get(accId), accountBalance.get(accId), days, 'critical', health, null, null));
            }
            sortByBalance(items);
        } catch (Exception e) { }
    }

    private static Decimal getAccountUnpaidBalance(Id accId, String invAccountField, Boolean filterCurrency, String currencyCode) {
        String q = 'SELECT SUM(Balance) s FROM Invoice WHERE Balance > 0 AND ' + invAccountField + ' = :accId ';
        if (filterCurrency && invoiceHasCurrencyField()) q += ' AND CurrencyIsoCode = :currencyCode ';
        List<AggregateResult> ar = Database.query(q);
        if (ar.isEmpty() || ar[0].get('s') == null) return 0;
        return (Decimal) ar[0].get('s');
    }

    private static void buildHighValueDelinquents(WorklistData wl, String invAccountField, Boolean filterAccount, Boolean filterCurrency, Id accountId, String currencyCode, Date thirtyDaysAgo) {
        Decimal minBalanceThreshold = 1000;
        String invWhereStrict = ' Balance > :minBalanceThreshold AND DueDate < :thirtyDaysAgo ';
        if (filterAccount) invWhereStrict += ' AND ' + invAccountField + ' = :accountId ';
        if (filterCurrency && invoiceHasCurrencyField()) invWhereStrict += ' AND CurrencyIsoCode = :currencyCode ';
        invWhereStrict += getInvoiceNotFullySettledStatusFilter();
        List<Invoice> invs = new List<Invoice>();
        try {
            invs = Database.query('SELECT Id, Balance, DueDate, ' + invAccountField + ' FROM Invoice WHERE ' + invWhereStrict);
        } catch (Exception e) { invs = new List<Invoice>(); }
        if (invs.isEmpty()) {
            String invWhereFallback = ' Balance > 0 AND DueDate < :thirtyDaysAgo ';
            if (filterAccount) invWhereFallback += ' AND ' + invAccountField + ' = :accountId ';
            if (filterCurrency && invoiceHasCurrencyField()) invWhereFallback += ' AND CurrencyIsoCode = :currencyCode ';
            try {
                invs = Database.query('SELECT Id, Balance, DueDate, ' + invAccountField + ' FROM Invoice WHERE ' + invWhereFallback);
            } catch (Exception e2) { return; }
        }
        Map<Id, Decimal> accountBalance = new Map<Id, Decimal>();
        Map<Id, Integer> accountMaxDays = new Map<Id, Integer>();
        for (Invoice inv : invs) {
            Id accId = (Id) inv.get(invAccountField);
            if (accId == null) continue;
            Decimal bal = inv.Balance != null ? inv.Balance : 0;
            accountBalance.put(accId, accountBalance.get(accId) != null ? accountBalance.get(accId) + bal : bal);
            Integer days = inv.DueDate != null ? inv.DueDate.daysBetween(Date.today()) : 0;
            Integer existing = accountMaxDays.get(accId);
            if (existing == null || days > existing) accountMaxDays.put(accId, days);
        }
        List<WorklistItem> highValue = new List<WorklistItem>();
        Map<Id, String> accountNames = getAccountNames(accountBalance.keySet());
        Map<Id, Id> accountToCollectionPlan = new Map<Id, Id>();
        if (!accountBalance.keySet().isEmpty() && Schema.getGlobalDescribe().containsKey('CollectionPlan')) {
            try {
                Set<Id> accIds = accountBalance.keySet();
                for (CollectionPlan cp : [SELECT Id, AccountId FROM CollectionPlan WHERE AccountId IN :accIds AND AccountId != null]) {
                    if (!accountToCollectionPlan.containsKey(cp.AccountId)) {
                        accountToCollectionPlan.put(cp.AccountId, cp.Id);
                    }
                }
            } catch (Exception ex) { }
        }
        for (Id accId : accountBalance.keySet()) {
            WorklistItem item = new WorklistItem(accId, accountNames.get(accId), accountBalance.get(accId), accountMaxDays.get(accId), 'highValue', 'red', null, null);
            item.collectionPlanId = accountToCollectionPlan.get(accId);
            highValue.add(item);
        }
        sortByBalance(highValue);
        for (Integer i = 0; i < Math.min(5, highValue.size()); i++) wl.highValueDelinquents.add(highValue[i]);
    }

    private static String getInvoiceNotFullySettledStatusFilter() {
        try {
            if (!Schema.SObjectType.Invoice.fields.getMap().containsKey('Status')) return '';
            return ' AND (Status = null OR Status NOT IN (\'Paid\', \'Closed\', \'Canceled\')) ';
        } catch (Exception e) { return ''; }
    }

    private static String getCollectionPlanNotesAndComments(SObject cp) {
        String descr = '';
        try { descr = String.valueOf(cp.get('Description')); } catch (Exception e) { }
        try { descr += ' ' + String.valueOf(cp.get('Comments__c')); } catch (Exception e2) { }
        try { descr += ' ' + String.valueOf(cp.get('Notes__c')); } catch (Exception e3) { }
        try { descr += ' ' + String.valueOf(cp.get('Notes')); } catch (Exception e4) { }
        return descr != null ? descr : '';
    }

    private static void buildDisputedFromCases(WorklistData wl, String invAccountField, Boolean filterAccount, Id accountId) {
        try {
            String caseWhere = ' IsClosed = false AND AccountId != null ';
            if (filterAccount) caseWhere += ' AND AccountId = :accountId ';
            String caseFields = 'Id, CaseNumber, AccountId, Subject, Description';
            if (Schema.SObjectType.Case.fields.getMap().containsKey('Reason')) caseFields += ', Reason';
            List<Case> openCases = Database.query('SELECT ' + caseFields + ' FROM Case WHERE ' + caseWhere + ' ORDER BY CreatedDate DESC');
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
                    try { if (c.get('Reason') != null) reason += (String.isNotBlank(reason) ? ' [' : '') + String.valueOf(c.get('Reason')) + (String.isNotBlank(reason) ? ']' : ''); } catch (Exception e) { }
                    accountDisputeReason.put(c.AccountId, String.isNotBlank(reason) ? reason : 'Open case');
                }
            }
            if (disputedAccountIds.isEmpty()) return;
            Map<Id, String> accountNames = getAccountNames(disputedAccountIds);
            Date today = Date.today();

            String invWhere = ' Balance > 0 AND ' + invAccountField + ' IN :disputedAccountIds ';
            List<Invoice> disputedInvs = Database.query('SELECT Id, Balance, DueDate, ' + invAccountField + ' FROM Invoice WHERE ' + invWhere);
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
            if (!invoiceIds.isEmpty() && Schema.getGlobalDescribe().containsKey('PaymentSchedule') && Schema.getGlobalDescribe().containsKey('PaymentScheduleItem')) {
                try {
                    List<Id> invIdList = new List<Id>(invoiceIds);
                    Map<Id, Id> scheduleToInvoiceId = new Map<Id, Id>();
                    for (SObject ps : Database.query('SELECT Id, ReferenceEntityId FROM PaymentSchedule WHERE ReferenceEntityId IN :invIdList')) {
                        Id refId = (Id) ps.get('ReferenceEntityId');
                        if (refId != null) scheduleToInvoiceId.put((Id) ps.get('Id'), refId);
                    }
                    if (!scheduleToInvoiceId.isEmpty()) {
                        Set<Id> scheduleIds = scheduleToInvoiceId.keySet();
                        for (PaymentScheduleItem psi : Database.query('SELECT Id, PaymentScheduleId, TargetPaymentProcessingDate FROM PaymentScheduleItem WHERE PaymentScheduleId IN :scheduleIds AND TargetPaymentProcessingDate != null')) {
                            Id invId = scheduleToInvoiceId.get(psi.PaymentScheduleId);
                            Id accId = invoiceToAccountId.get(invId);
                            if (accId == null) continue;
                            Date d = psi.TargetPaymentProcessingDate;
                            Date existing = accountPtpDate.get(accId);
                            if (existing == null || (d != null && d > existing)) accountPtpDate.put(accId, d);
                        }
                    }
                } catch (Exception e) { }
            }

            for (Id accId : disputedAccountIds) {
                Decimal bal = accountBalance.get(accId) != null ? accountBalance.get(accId) : 0;
                Integer daysOverdue = accountMaxDaysOverdue.get(accId);
                Date ptpDate = accountPtpDate.get(accId);
                WorklistItem item = new WorklistItem(accId, accountNames.get(accId), bal, daysOverdue, 'disputed', 'amber', ptpDate, accountDisputeReason.get(accId));
                item.caseId = accountCaseId.get(accId);
                item.caseNumber = accountCaseNumber.get(accId);
                wl.disputedInvoices.add(item);
            }
        } catch (Exception e) { }
    }

    private static Map<Id, String> getAccountNames(Set<Id> accountIds) {
        Map<Id, String> m = new Map<Id, String>();
        if (accountIds == null || accountIds.isEmpty()) return m;
        for (Account a : [SELECT Id, Name FROM Account WHERE Id IN :accountIds]) m.put(a.Id, a.Name);
        return m;
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
        public WorklistItem(Id accId, String name, Decimal bal, Integer days, String seg) {
            accountId = accId; accountName = name; balance = bal; daysOverdue = days; segment = seg; healthScore = 'amber'; ptpDate = null; disputeReason = null; collectionPlanId = null; caseId = null; caseNumber = null;
        }
        public WorklistItem(Id accId, String name, Decimal bal, Integer days, String seg, String health) {
            accountId = accId; accountName = name; balance = bal; daysOverdue = days; segment = seg; healthScore = health; ptpDate = null; disputeReason = null; collectionPlanId = null; caseId = null; caseNumber = null;
        }
        public WorklistItem(Id accId, String name, Decimal bal, Integer days, String seg, String health, Date ptp, String disputeReasonStr) {
            accountId = accId; accountName = name; balance = bal; daysOverdue = days; segment = seg; healthScore = health; ptpDate = ptp; disputeReason = disputeReasonStr; collectionPlanId = null; caseId = null; caseNumber = null;
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
        public WorklistData() { criticalFollowUpInvoices = new List<CriticalFollowUpInvoiceItem>(); highValueDelinquents = new List<WorklistItem>(); disputedInvoices = new List<WorklistItem>(); }
    }

    private static String getInvoiceAccountFieldName() {
        try {
            Map<String, Schema.SObjectField> fMap = Schema.SObjectType.Invoice.fields.getMap();
            if (fMap.containsKey('BillingAccountId')) return 'BillingAccountId';
            if (fMap.containsKey('BillToAccountId')) return 'BillToAccountId';
            if (fMap.containsKey('AccountId')) return 'AccountId';
        } catch (Exception e) { }
        try {
            if (!Schema.getGlobalDescribe().containsKey('Invoice')) return null;
            Map<String, Schema.SObjectField> flds = Schema.getGlobalDescribe().get('Invoice').getDescribe().fields.getMap();
            if (flds != null && flds.containsKey('BillingAccountId')) return 'BillingAccountId';
            if (flds != null && flds.containsKey('BillToAccountId')) return 'BillToAccountId';
            if (flds != null && flds.containsKey('AccountId')) return 'AccountId';
        } catch (Exception e2) { }
        return null;
    }

    private static Boolean invoiceHasCurrencyField() {
        try {
            return Schema.SObjectType.Invoice.fields.getMap().containsKey('CurrencyIsoCode');
        } catch (Exception e) { return false; }
    }

    private static Boolean paymentScheduleItemHasCurrencyField() {
        try {
            if (!Schema.getGlobalDescribe().containsKey('PaymentScheduleItem')) return false;
            return Schema.getGlobalDescribe().get('PaymentScheduleItem').getDescribe().fields.getMap().containsKey('CurrencyIsoCode');
        } catch (Exception e) { return false; }
    }

    private static String getPaymentAccountFieldName() {
        try {
            if (Schema.SObjectType.Payment.fields.getMap().containsKey('PaymentAccountId')) return 'PaymentAccountId';
            if (Schema.SObjectType.Payment.fields.getMap().containsKey('AccountId')) return 'AccountId';
        } catch (Exception e) { }
        return null;
    }

    private static Decimal getUnappliedCreditsSum(Id accountId, String currencyCode) {
        Decimal sum = 0;
        try {
            String accFld = getPaymentAccountFieldName();
            String soql = 'SELECT SUM(Balance) sumBal FROM Payment WHERE Balance > 0 ';
            if (Schema.SObjectType.Payment.fields.getMap().containsKey('Type')) {
                soql += ' AND (Type = \'Credit\' OR Type = \'Credit Memo\') ';
            }
            if (accountId != null && String.isNotBlank(String.valueOf(accountId)) && accFld != null) {
                soql += ' AND ' + accFld + ' = :accountId ';
            }
            if (String.isNotBlank(currencyCode)) soql += ' AND CurrencyIsoCode = :currencyCode ';
            List<AggregateResult> ar = Database.query(soql);
            if (!ar.isEmpty() && ar[0].get('sumBal') != null) sum = (Decimal) ar[0].get('sumBal');
        } catch (Exception e) { }
        return sum;
    }

    private static Decimal getDebitMemoNotInvoicedSum(Id accountId, String currencyCode) {
        Decimal sum = 0;
        try {
            if (!Schema.getGlobalDescribe().containsKey('DebitMemo')) return 0;
            Schema.DescribeSObjectResult dmDesc = Schema.getGlobalDescribe().get('DebitMemo').getDescribe();
            Map<String, Schema.SObjectField> flds = dmDesc.fields.getMap();
            String accFld = flds.containsKey('BillToAccountId') ? 'BillToAccountId' : (flds.containsKey('AccountId') ? 'AccountId' : null);
            String soql = 'SELECT SUM(Amount) sumAmt FROM DebitMemo WHERE Amount != null ';
            if (accountId != null && accFld != null) soql += ' AND ' + accFld + ' = :accountId ';
            if (String.isNotBlank(currencyCode) && flds.containsKey('CurrencyIsoCode')) soql += ' AND CurrencyIsoCode = :currencyCode ';
            List<AggregateResult> ar = Database.query(soql);
            if (!ar.isEmpty() && ar[0].get('sumAmt') != null) sum = (Decimal) ar[0].get('sumAmt');
        } catch (Exception e) { }
        return sum;
    }

    private static Decimal getUnappliedPaymentBalanceSum(Id accountId, String currencyCode) {
        Decimal sum = 0;
        try {
            String accFld = getPaymentAccountFieldName();
            String soql = 'SELECT SUM(Balance) sumBal FROM Payment WHERE Balance > 0 ';
            if (Schema.SObjectType.Payment.fields.getMap().containsKey('Type')) {
                soql += ' AND (Type != \'Credit\' AND Type != \'Credit Memo\') ';
            }
            if (accountId != null && String.isNotBlank(String.valueOf(accountId)) && accFld != null) {
                soql += ' AND ' + accFld + ' = :accountId ';
            }
            if (String.isNotBlank(currencyCode)) soql += ' AND CurrencyIsoCode = :currencyCode ';
            List<AggregateResult> ar = Database.query(soql);
            if (!ar.isEmpty() && ar[0].get('sumBal') != null) sum = (Decimal) ar[0].get('sumBal');
        } catch (Exception e) { }
        return sum;
    }

    private static Integer getUnappliedPaymentCount(Id accountId, String currencyCode) {
        Integer cnt = 0;
        try {
            String accFld = getPaymentAccountFieldName();
            String soql = 'SELECT COUNT(Id) cnt FROM Payment WHERE Balance > 0 ';
            if (Schema.SObjectType.Payment.fields.getMap().containsKey('Type')) {
                soql += ' AND (Type != \'Credit\' AND Type != \'Credit Memo\') ';
            }
            if (accountId != null && accFld != null) soql += ' AND ' + accFld + ' = :accountId ';
            if (String.isNotBlank(currencyCode)) soql += ' AND CurrencyIsoCode = :currencyCode ';
            List<AggregateResult> ar = Database.query(soql);
            if (!ar.isEmpty() && ar[0].get('cnt') != null) cnt = (Integer) ar[0].get('cnt');
        } catch (Exception e) { }
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

        public CollectionsDashboardData() {
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
    public static List<MyCollectionPlanItem> getMyCollectionPlans() {
        List<MyCollectionPlanItem> items = new List<MyCollectionPlanItem>();
        try {
            if (!Schema.getGlobalDescribe().containsKey('CollectionPlan')) return items;
            Id currentUserId = UserInfo.getUserId();
            String acctField = 'AccountId';
            String acctNameExpr = 'Account.Name';
            Map<String, Schema.SObjectField> cpFields = Schema.SObjectType.CollectionPlan.fields.getMap();
            if (cpFields.containsKey('BillingAccountId')) {
                acctField = 'BillingAccountId';
                acctNameExpr = 'BillingAccount.Name';
            }
            if (cpFields.containsKey('AccountId')) {
                acctField = 'AccountId';
                acctNameExpr = 'Account.Name';
            }
            String selectFields = 'Id, Name, Duedate, TotalInvoiceBalance, ' + acctField + ', ' + acctNameExpr;
            String q = 'SELECT ' + selectFields + ' FROM CollectionPlan WHERE OwnerId = :currentUserId ORDER BY Duedate ASC NULLS LAST, Name ASC LIMIT 50';
            List<SObject> plans = Database.query(q);
            for (SObject cp : plans) {
                Id cpId = (Id) cp.get('Id');
                String cpName = (String) cp.get('Name');
                Date dueDate = (Date) cp.get('Duedate');
                Decimal totalInvBal = cp.get('TotalInvoiceBalance') != null ? (Decimal) cp.get('TotalInvoiceBalance') : 0;
                Id accountId = (Id) cp.get(acctField);
                String accountName = null;
                try {
                    SObject rel = cp.getSObject(acctField.replace('Id', ''));
                    if (rel != null) accountName = (String) rel.get('Name');
                } catch (Exception ex) { }
                items.add(new MyCollectionPlanItem(cpId, cpName, dueDate, accountId, accountName, totalInvBal));
            }
        } catch (Exception e) { }
        return items;
    }

    @AuraEnabled(cacheable=true)
    public static CollectionsProgressData getCollectionsProgress() {
        CollectionsProgressData result = new CollectionsProgressData();
        try {
            if (!Schema.getGlobalDescribe().containsKey('CollectionPlan')) return result;
            List<CollectionPlan> plans = [
                SELECT Id, ClosedDate, CreatedDate, TotalInvoiceBalance, DaysPastDue, Duedate
                FROM CollectionPlan
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
        } catch (Exception e) { }
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
        public CollectionsProgressData() {
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