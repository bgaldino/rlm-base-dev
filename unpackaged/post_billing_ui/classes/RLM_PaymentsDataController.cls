public with sharing class RLM_PaymentsDataController {
    
    // Default currency from Setup → Company Information
    @AuraEnabled(cacheable=true)
    public static String getOrgDefaultCurrency() {
        String defaultCurrency = UserInfo.getDefaultCurrency();
        return String.isNotBlank(defaultCurrency) ? defaultCurrency : 'USD';
    }
    
    @AuraEnabled(cacheable=true)
    public static List<Map<String, String>> getAccountOptions() {
        List<Map<String, String>> options = new List<Map<String, String>>();
        options.add(new Map<String, String>{ 'value' => '', 'label' => 'All Accounts' });
        Set<Id> accountIds = new Set<Id>();
        for (AggregateResult ar : [
            SELECT PaymentAccountId FROM PaymentScheduleItem
            WHERE PaymentAccountId != null
            WITH USER_MODE GROUP BY PaymentAccountId
        ]) {
            accountIds.add((Id) ar.get('PaymentAccountId'));
        }
        if (accountIds.isEmpty()) {
            return options;
        }
        for (Account a : [SELECT Id, Name FROM Account WHERE Id IN :accountIds WITH USER_MODE ORDER BY Name]) {
            options.add(new Map<String, String>{ 'value' => a.Id, 'label' => a.Name });
        }
        return options;
    }
    
    // Currency list from Setup → Manage Currencies (active currencies)
    @AuraEnabled(cacheable=true)
    public static List<Map<String, String>> getCurrencyOptions() {
        List<Map<String, String>> options = new List<Map<String, String>>();
        options.add(new Map<String, String>{ 'value' => '', 'label' => 'All Currencies' });
        for (CurrencyType ct : [
            SELECT IsoCode, IsCorporate
            FROM CurrencyType
            WHERE IsActive = true
            WITH USER_MODE ORDER BY IsCorporate DESC, IsoCode ASC
        ]) {
            if (String.isNotBlank(ct.IsoCode)) {
                options.add(new Map<String, String>{ 'value' => ct.IsoCode, 'label' => ct.IsoCode });
            }
        }
        if (options.size() == 1) {
            String defaultCode = getOrgDefaultCurrency();
            options.add(new Map<String, String>{ 'value' => defaultCode, 'label' => defaultCode });
        }
        return options;
    }
    
    @AuraEnabled(cacheable=true)
    public static List<PaymentStatusSummary> getPaymentScheduleItems(Id recordId, String currencyCode) {
        // Map to store status-wise data
        Map<String, PaymentStatusSummary> statusSummaryMap = new Map<String, PaymentStatusSummary>();
        List<String> statusTypes = new List<String>{'Failed', 'Ready for Processing', 'Applied', 'Draft', 'Processing'};
        for (String status : statusTypes) {
            statusSummaryMap.put(status, new PaymentStatusSummary(status));
        }
        
        Boolean filterByAccount = recordId != null && String.isNotBlank(String.valueOf(recordId));
        Boolean filterByCurrency = String.isNotBlank(currencyCode);
        
        // Query Payment Schedule Items (all accounts when recordId blank, else by account; optional currency)
        List<PaymentScheduleItem> items;
        if (filterByAccount && filterByCurrency) {
            items = [
                SELECT Id, PaymentScheduleItemNumber, Status, RequestedAmount,
                       ProcessedAmount, TargetPaymentProcessingDate,
                       PaymentScheduleId, PaymentAccountId, CurrencyIsoCode,
                       PaymentId
                FROM PaymentScheduleItem
                WHERE PaymentAccountId = :recordId AND CurrencyIsoCode = :currencyCode
                WITH USER_MODE ORDER BY Status, TargetPaymentProcessingDate
            ];
        } else if (filterByAccount) {
            items = [
                SELECT Id, PaymentScheduleItemNumber, Status, RequestedAmount,
                       ProcessedAmount, TargetPaymentProcessingDate,
                       PaymentScheduleId, PaymentAccountId, CurrencyIsoCode,
                       PaymentId
                FROM PaymentScheduleItem
                WHERE PaymentAccountId = :recordId
                WITH USER_MODE ORDER BY Status, TargetPaymentProcessingDate
            ];
        } else if (filterByCurrency) {
            items = [
                SELECT Id, PaymentScheduleItemNumber, Status, RequestedAmount,
                       ProcessedAmount, TargetPaymentProcessingDate,
                       PaymentScheduleId, PaymentAccountId, CurrencyIsoCode,
                       PaymentId
                FROM PaymentScheduleItem
                WHERE CurrencyIsoCode = :currencyCode
                WITH USER_MODE ORDER BY Status, TargetPaymentProcessingDate
            ];
        } else {
            items = [
                SELECT Id, PaymentScheduleItemNumber, Status, RequestedAmount,
                       ProcessedAmount, TargetPaymentProcessingDate,
                       PaymentScheduleId, PaymentAccountId, CurrencyIsoCode,
                       PaymentId
                FROM PaymentScheduleItem
                WITH USER_MODE ORDER BY Status, TargetPaymentProcessingDate
            ];
        }
        
        // Collect Payment IDs and PaymentSchedule IDs
        Set<Id> paymentIds = new Set<Id>();
        Set<Id> scheduleIds = new Set<Id>();
        for (PaymentScheduleItem item : items) {
            if (item.PaymentId != null) paymentIds.add(item.PaymentId);
            if (item.PaymentScheduleId != null) scheduleIds.add(item.PaymentScheduleId);
        }
        
        // Invoices from PaymentLineInvoice (Header Level applications). An unapply adds an
        // Unapplied row and flags the original (HasBeenUnapplied; UnappliedStatus on the line
        // object), so both are left out. A user without read on these objects or fields keeps
        // the rest of the summary.
        Map<Id, List<InvoiceWrapper>> paymentInvoiceMap = new Map<Id, List<InvoiceWrapper>>();
        if (!paymentIds.isEmpty()) {
            try {
                addHeaderLevelApplications(paymentInvoiceMap, [
                    SELECT Id, PaymentId, InvoiceId, Amount,
                           Invoice.Id, Invoice.InvoiceNumber, Invoice.DocumentNumber,
                           Invoice.TotalAmount, Invoice.Balance, Invoice.Status,
                           Invoice.DueDate, Invoice.InvoiceDate, Invoice.CurrencyIsoCode
                    FROM PaymentLineInvoice
                    WHERE PaymentId IN :paymentIds AND Type != 'Unapplied' AND HasBeenUnapplied != 'Yes'
                    WITH USER_MODE ORDER BY Invoice.InvoiceNumber
                ]);
            } catch (QueryException e) {
                System.debug(LoggingLevel.WARN, 'Header-level payment applications not readable: ' + e.getMessage());
            }
        }

        // Invoices from PaymentLineInvoiceLine: with Billing Settings' Credit, Payment, and
        // Refund Application at Line Level (the Foundations default), payment lines apply to
        // invoice lines rather than the invoice.
        // A user without read on PaymentLineInvoiceLine keeps the header-level view rather than
        // losing the whole summary.
        if (!paymentIds.isEmpty()) {
            try {
                addLineLevelApplications(paymentInvoiceMap, [
                    SELECT PaymentId, Amount,
                           InvoiceLine.Invoice.Id, InvoiceLine.Invoice.InvoiceNumber, InvoiceLine.Invoice.DocumentNumber,
                           InvoiceLine.Invoice.TotalAmount, InvoiceLine.Invoice.Balance, InvoiceLine.Invoice.Status,
                           InvoiceLine.Invoice.DueDate, InvoiceLine.Invoice.InvoiceDate, InvoiceLine.Invoice.CurrencyIsoCode
                    FROM PaymentLineInvoiceLine
                    WHERE PaymentId IN :paymentIds AND Type != 'Unapplied' AND UnappliedStatus != 'Yes'
                    WITH USER_MODE ORDER BY InvoiceLine.Invoice.InvoiceNumber
                ]);
            } catch (QueryException e) {
                System.debug(LoggingLevel.WARN, 'Line-level payment applications not readable: ' + e.getMessage());
            }
        }

        // Invoice from Payment Schedule's Reference Entity (PS -> Reference Entity = Invoice)
        Map<Id, Id> scheduleToInvoiceId = new Map<Id, Id>();
        if (!scheduleIds.isEmpty()) {
            try {
                List<SObject> schedules = Database.query(
                    'SELECT Id, ReferenceEntityId FROM PaymentSchedule WHERE Id IN :scheduleIds AND ReferenceEntityId != null'
                , AccessLevel.USER_MODE);
                for (SObject ps : schedules) {
                    Id refId = (Id) ps.get('ReferenceEntityId');
                    if (refId != null) scheduleToInvoiceId.put((Id) ps.get('Id'), refId);
                }
            } catch (Exception e) {
                // ReferenceEntityId may not exist in this org
            }
        }
        
        // Fetch Invoice details for schedule reference entities
        Map<Id, InvoiceWrapper> invoiceByIdMap = new Map<Id, InvoiceWrapper>();
        if (!scheduleToInvoiceId.isEmpty()) {
            Set<Id> invoiceIds = new Set<Id>(scheduleToInvoiceId.values());
            for (Invoice inv : [
                SELECT Id, InvoiceNumber, DocumentNumber, TotalAmount, Balance, Status,
                       DueDate, InvoiceDate, CurrencyIsoCode
                FROM Invoice
                WHERE Id IN :invoiceIds WITH USER_MODE
            ]) {
                invoiceByIdMap.put(inv.Id, new InvoiceWrapper(inv));
            }
        }
        
        // Build invoice list per PSI: from PaymentLineInvoice / PaymentLineInvoiceLine + from Schedule Reference Entity (if not already included)
        for (PaymentScheduleItem item : items) {
            String status = item.Status;
            if (!statusSummaryMap.containsKey(status)) continue;
            PaymentStatusSummary summary = statusSummaryMap.get(status);
            List<InvoiceWrapper> invoices = paymentInvoiceMap.get(item.PaymentId);
            if (invoices == null) invoices = new List<InvoiceWrapper>();
            Set<Id> existingIds = new Set<Id>();
            for (InvoiceWrapper iw : invoices) existingIds.add(iw.id);
            Id scheduleInvoiceId = scheduleToInvoiceId.get(item.PaymentScheduleId);
            if (scheduleInvoiceId != null && !existingIds.contains(scheduleInvoiceId)) {
                InvoiceWrapper scheduleInv = invoiceByIdMap.get(scheduleInvoiceId);
                if (scheduleInv != null) invoices.add(scheduleInv);
            }
            summary.addItem(item, invoices);
        }
        
        // Return list of summaries
        return statusSummaryMap.values();
    }
    
    // One entry per payment and invoice: a payment applied to the same invoice more than once
    // is listed once, with the amounts summed.
    @TestVisible
    private static void addHeaderLevelApplications(Map<Id, List<InvoiceWrapper>> paymentInvoiceMap,
                                                   List<PaymentLineInvoice> rows) {
        Map<String, InvoiceWrapper> byKey = new Map<String, InvoiceWrapper>();
        for (PaymentLineInvoice pli : rows) {
            String key = pli.PaymentId + ':' + pli.InvoiceId;
            InvoiceWrapper existing = byKey.get(key);
            if (existing != null) {
                if (pli.Amount != null) existing.appliedAmount = (existing.appliedAmount == null ? 0 : existing.appliedAmount) + pli.Amount;
                continue;
            }
            InvoiceWrapper iw = new InvoiceWrapper(pli);
            byKey.put(key, iw);
            if (!paymentInvoiceMap.containsKey(pli.PaymentId)) {
                paymentInvoiceMap.put(pli.PaymentId, new List<InvoiceWrapper>());
            }
            paymentInvoiceMap.get(pli.PaymentId).add(iw);
        }
    }

    // Sum line-level applications into one entry per payment and invoice. An invoice already
    // listed from a header-level PaymentLineInvoice row (applied before a switch to Line Level)
    // gets the line amounts added to that entry, so it's listed once with the total applied.
    @TestVisible
    private static void addLineLevelApplications(Map<Id, List<InvoiceWrapper>> paymentInvoiceMap,
                                                 List<PaymentLineInvoiceLine> lines) {
        Map<String, InvoiceWrapper> byKey = new Map<String, InvoiceWrapper>();
        for (Id paymentId : paymentInvoiceMap.keySet()) {
            for (InvoiceWrapper iw : paymentInvoiceMap.get(paymentId)) byKey.put(paymentId + ':' + iw.id, iw);
        }
        for (PaymentLineInvoiceLine plil : lines) {
            Invoice inv = plil.InvoiceLine == null ? null : plil.InvoiceLine.Invoice;
            if (inv == null || inv.Id == null) continue; // invoice not readable
            String key = plil.PaymentId + ':' + inv.Id;
            InvoiceWrapper iw = byKey.get(key);
            if (iw == null) {
                iw = new InvoiceWrapper(inv);
                byKey.put(key, iw);
                if (!paymentInvoiceMap.containsKey(plil.PaymentId)) {
                    paymentInvoiceMap.put(plil.PaymentId, new List<InvoiceWrapper>());
                }
                paymentInvoiceMap.get(plil.PaymentId).add(iw);
            }
            if (plil.Amount != null) iw.appliedAmount = (iw.appliedAmount == null ? 0 : iw.appliedAmount) + plil.Amount;
        }
    }

    public class PaymentStatusSummary {
        @AuraEnabled public String status { get; set; }
        @AuraEnabled public Decimal totalRequestedAmount { get; set; }
        @AuraEnabled public Integer itemCount { get; set; }
        @AuraEnabled public List<PaymentItemWrapper> items { get; set; }
        @AuraEnabled public String statusClass { get; set; }
        @AuraEnabled public String iconName { get; set; }
        
        public PaymentStatusSummary(String status) {
            this.status = status;
            this.totalRequestedAmount = 0;
            this.itemCount = 0;
            this.items = new List<PaymentItemWrapper>();
            this.statusClass = getStatusClass(status);
            this.iconName = getIconName(status);
        }
        
        public void addItem(PaymentScheduleItem item, List<InvoiceWrapper> invoices) {
            this.items.add(new PaymentItemWrapper(item, invoices));
            this.itemCount++;
            if (item.RequestedAmount != null) {
                this.totalRequestedAmount += item.RequestedAmount;
            }
        }
        
        private String getStatusClass(String status) {
            Map<String, String> statusClasses = new Map<String, String>{
                'Failed' => 'slds-theme_error',
                'Ready for Processing' => 'slds-theme_warning',
                'Applied' => 'slds-theme_success',
                'Draft' => 'slds-theme_info',
                'Processing' => 'slds-theme_alt-inverse'
            };
            return statusClasses.containsKey(status) ? statusClasses.get(status) : 'slds-theme_default';
        }
        
        private String getIconName(String status) {
            Map<String, String> iconNames = new Map<String, String>{
                'Failed' => 'utility:error',
                'Ready for Processing' => 'utility:clock',
                'Applied' => 'utility:success',
                'Draft' => 'utility:edit',
                'Processing' => 'utility:sync'
            };
            return iconNames.containsKey(status) ? iconNames.get(status) : 'utility:moneybag';
        }
    }
    
    public class PaymentItemWrapper {
        @AuraEnabled public Id id { get; set; }
        @AuraEnabled public String itemNumber { get; set; }
        @AuraEnabled public Decimal requestedAmount { get; set; }
        @AuraEnabled public Decimal processedAmount { get; set; }
        @AuraEnabled public Date targetDate { get; set; }
        @AuraEnabled public String currencyCode { get; set; }
        @AuraEnabled public Id paymentId { get; set; }
        @AuraEnabled public List<InvoiceWrapper> invoices { get; set; }
        @AuraEnabled public Boolean hasPayment { get; set; }
        @AuraEnabled public Boolean hasInvoices { get; set; }
        
        public PaymentItemWrapper(PaymentScheduleItem item, List<InvoiceWrapper> invoices) {
            this.id = item.Id;
            this.itemNumber = item.PaymentScheduleItemNumber;
            this.requestedAmount = item.RequestedAmount;
            this.processedAmount = item.ProcessedAmount;
            this.targetDate = item.TargetPaymentProcessingDate;
            this.currencyCode = item.CurrencyIsoCode;
            this.paymentId = item.PaymentId;
            this.hasPayment = item.PaymentId != null;
            this.invoices = invoices != null ? invoices : new List<InvoiceWrapper>();
            this.hasInvoices = this.invoices.size() > 0;
        }
    }
    
    public class InvoiceWrapper {
        @AuraEnabled public Id id { get; set; }
        @AuraEnabled public String invoiceNumber { get; set; }
        @AuraEnabled public String documentNumber { get; set; }
        @AuraEnabled public Decimal totalAmount { get; set; }
        @AuraEnabled public Decimal balance { get; set; }
        @AuraEnabled public Decimal appliedAmount { get; set; }
        @AuraEnabled public String status { get; set; }
        @AuraEnabled public Date dueDate { get; set; }
        @AuraEnabled public Date invoiceDate { get; set; }
        @AuraEnabled public String currencyCode { get; set; }
        @AuraEnabled public Boolean isSettled { get; set; }
        
        public InvoiceWrapper(PaymentLineInvoice pli) {
            this.id = pli.Invoice.Id;
            this.invoiceNumber = pli.Invoice.InvoiceNumber;
            this.documentNumber = pli.Invoice.DocumentNumber;
            this.totalAmount = pli.Invoice.TotalAmount;
            this.balance = pli.Invoice.Balance;
            this.appliedAmount = pli.Amount;
            this.status = pli.Invoice.Status;
            this.dueDate = pli.Invoice.DueDate;
            this.invoiceDate = pli.Invoice.InvoiceDate;
            this.currencyCode = pli.Invoice.CurrencyIsoCode;
            this.isSettled = pli.Invoice.Balance == 0 || pli.Invoice.Balance == null;
        }
        
        public InvoiceWrapper(Invoice inv) {
            this.id = inv.Id;
            this.invoiceNumber = inv.InvoiceNumber;
            this.documentNumber = inv.DocumentNumber;
            this.totalAmount = inv.TotalAmount;
            this.balance = inv.Balance;
            this.appliedAmount = null;
            this.status = inv.Status;
            this.dueDate = inv.DueDate;
            this.invoiceDate = inv.InvoiceDate;
            this.currencyCode = inv.CurrencyIsoCode;
            this.isSettled = inv.Balance == 0 || inv.Balance == null;
        }
    }
}