public with sharing class QuoteTriggerHelper {
    private static IQuoteDAO quoteDAO = (IQuoteDAO) ServiceRegistry.getInstance('IQuoteDAO');
    private static IContractDAO contractDAO = (IContractDAO) ServiceRegistry.getInstance('IContractDAO');

    private static Set<String> QUOTE_STATUS_MAINTAIN_PAYMENT_DETAIL_BYPASS = new Set<String>{ 'Booked', 'Accepted' };
    private static Set<String> PAYMENT_METHODS_WITH_DETAILS = new Set<String>{ 'Credit Card', 'Direct Debit' };
    private static final String ACCEPTED_QUOTE_STATUS = 'Accepted';
    private static final String REJECTED_QUOTE_STATUS = 'Rejected';
    private static final String REJECTED_BOOKINGS_QUOTE_SUBSTATUS = 'Rejected - Bookings';
    private static final Set<String> FAILED_ACCOUNT_CREDIT_DECISION_STATUSES = new Set<String>{ 'Credit Data Not Found', 'Prepayment' };
    private static final String PUBLISH_TARGET_PDF = 'PDF';
    private static final String PO_REQUIRED_YES = 'Yes';
    private static final String PO_REQUIRED_NA = 'N/A';
    private static final Integer MIN_QUOTE_AMOUNT_CREDIT_VALIDATION = 1000000;
    private static Set<String> INVALID_QUOTE_STATUS_FOR_PROCESSING_UPDATE = new Set<String>{ 'Booked', 'Accepted', 'Offer', 'Approved' };
    private static Map<String, Integer> frequencyMap = new Map<String, Integer>{ 'Annual' => 1, 'Semi-Annual' => 2, 'Quarterly' => 4, 'Monthly' => 12 };
    private static IRevenueOwnerMdtSelector revenueOwnerMdtSelector = (IRevenueOwnerMdtSelector) ServiceRegistry.getInstance('IRevenueOwnerMdtSelector');
    private static Map<Id, Map<String, Id>> accountToContractMap = new Map<Id, Map<String, Id>>();
    
    public static Boolean shouldProcessQuoteUpdate(Quote quote) {
        if (quote == null) {
            return false;
        }

        return !INVALID_QUOTE_STATUS_FOR_PROCESSING_UPDATE.contains(quote.Status);
    }

    private static Map<String, ROCountryAugmentation__mdt> getAugmentationDataForQuotes(List<Quote> quotes) {
        Set<String> countryCodes = new Set<String>();

        for (Quote quote : quotes) {
            countryCodes.add(quote.BillingCountry);
        }

        Map<String, ROCountryAugmentation__mdt> augmentationDataForCountries = new Map<String, ROCountryAugmentation__mdt>();
        if (!countryCodes.isEmpty()) {
            List<ROCountryAugmentation__mdt> newAugmentationData = revenueOwnerMdtSelector.getSupplementalDataList(countryCodes);

            for (ROCountryAugmentation__mdt augmentationData : newAugmentationData) {
                augmentationDataForCountries.put(augmentationData.CountryISOCode__c, augmentationData);
            }
        }

        return augmentationDataForCountries;
    }

    public static void processTaxInformation(List<Quote> newQuotes) {
        if (newQuotes == null || newQuotes?.size() == 0) {
            return;
        }

        Map<String, ROCountryAugmentation__mdt> augmentationDataForCountry = getAugmentationDataForQuotes(newQuotes);
        for (Quote quote : newQuotes) {
            ROCountryAugmentation__mdt augmentationData = augmentationDataForCountry.get(quote.BillingCountry);

            if (augmentationData == null) {
                continue;
            }

            if (!augmentationData.IsBusinessTypeApplicable__c) {
                quote.BusinessType__c = 'Not Applicable';
            }

            if (!augmentationData.IsNoTaxRegistrationIdReasonApplicable__c) {
                quote.NoTaxRegistrationIdReason__c = 'Not Applicable';
            }
        }

        createTaxInformationJSON(newQuotes);
    }

    public static void createTaxInformationJSON(List<Quote> newQuotes) {
        if (newQuotes == null || newQuotes?.size() == 0) {
            return;
        }

        for (Quote quote : newQuotes) {
            Map<String, Object> taxInfomationMap = new Map<String, Object>{
                'businessType' => quote.BusinessType__c,
                'taxId' => quote.TaxRegistrationID__c,
                'SDICode' => '',
                'legalEmailAddress' => '',
                'CIGCode' => '',
                'CUPCode' => ''
            };

            quote.TaxInformationJSON__c = JSON.serialize(taxInfomationMap);
        }
    }

    public static void maintainPaymentDetails(Map<Id, Quote> oldQuotes, List<Quote> newQuotes) {
        if (oldQuotes == null || oldQuotes.size() == 0) {
            return;
        }

        if (newQuotes == null || newQuotes.size() == 0) {
            return;
        }

        for (Quote newQuote : newQuotes) {
            Quote oldQuote = oldQuotes.get(newQuote.Id);

            if (shouldClearPaymentDetail(oldQuote, newQuote)) {
                newQuote.PaymentDetailJSON__c = '';
            }
        }
    }

    @TestVisible
    private static Boolean shouldClearPaymentDetail(Quote oldQuote, Quote newQuote) {
        if (oldQuote == null || newQuote == null) {
            return false;
        }

        if (QUOTE_STATUS_MAINTAIN_PAYMENT_DETAIL_BYPASS.contains(newQuote.Status)) {
            return false;
        }

        if (!PAYMENT_METHODS_WITH_DETAILS.contains(oldQuote.PaymentMethod__c)) {
            return false;
        }

        if (oldQuote.PaymentMethod__c == newQuote.PaymentMethod__c) {
            return false;
        }

        return true;
    }

    public static void validateQuoteForConversion(Map<Id, Quote> oldQuotes, List<Quote> newQuotes) {
        if (oldQuotes == null || oldQuotes.size() == 0) {
            return;
        }
        if (newQuotes == null || newQuotes?.size() == 0) {
            return;
        }

        for (Quote newQuote : newQuotes) {
            Quote oldQuote = oldQuotes.get(newQuote.Id);
            if (oldQuote.status != newQuote.status && newQuote.status == ACCEPTED_QUOTE_STATUS) {
                updatePurchaseOrderRequired(newQuote);
                validateAcceptedQuoteExists(newQuote);
                if (newQuote.hasErrors()) {
                    return;
                }
                validateCreditScore(oldQuote, newQuote);
                validateCreditOrDebitInformation(newQuote);
            }
        }
    }

    private static void updatePurchaseOrderRequired(Quote newQuote) {
        if (
            newQuote.PurchaseOrderRequired__c == PO_REQUIRED_YES && (String.isBlank(newQuote.PurchaseOrderNumber__c) || newQuote.PurchaseOrderAmount__c == null)
        ) {
            newQuote.PurchaseOrderRequired__c = PO_REQUIRED_NA;
        }
    }

    private static void validateAcceptedQuoteExists(Quote newQuote) {
        if (quoteDAO.getAcceptedQuotesOnOppty(newQuote.OpportunityId).size() > 0) {
            newQuote.addError(Label.AcceptedQuoteAlreadyExistsError);
        }
    }

    private static void validateCreditScore(Quote oldQuote, Quote newQuote) {
        if (!needsCreditScoreValidation(newQuote)) {
            return;
        }

        if (newQuote.PublishTarget__c == PUBLISH_TARGET_PDF || oldQuote.Status == REJECTED_QUOTE_STATUS) {
            newQuote.addError(Label.CreditScorePreConversionValidationErrorMessage);
            return;
        }
        newQuote.RejectionReason__c = Label.CreditScorePreConversionValidationErrorMessage;
        newQuote.Status = REJECTED_QUOTE_STATUS;
        newQuote.SubStatus__c = REJECTED_BOOKINGS_QUOTE_SUBSTATUS;
    }
  
    private static void validateCreditOrDebitInformation( Quote newQuote) {
         if(isPaymentInfoMissing(newQuote)){
             if (newQuote.PublishTarget__c == PUBLISH_TARGET_PDF){ 
                newQuote.addError(Label.CreditOrDebitInformationValidationErrorMessage );
                return;
             }
        	 newQuote.RejectionReason__c = Label.CreditOrDebitInformationValidationErrorMessage ;
        	 newQuote.Status = REJECTED_QUOTE_STATUS;
           newQuote.SubStatus__c = REJECTED_BOOKINGS_QUOTE_SUBSTATUS;
         }
    }

    private static boolean isPaymentInfoMissing(Quote newQuote){
        return PAYMENT_METHODS_WITH_DETAILS.contains(newQuote.PaymentMethod__c) && string.IsBlank(newQuote.PaymentDetailJSON__c);
    }

    public static boolean needsCreditScoreValidation(Quote newQuote) {
        if (newQuote.TotalQuoteAmount__c < MIN_QUOTE_AMOUNT_CREDIT_VALIDATION) {
            return false;
        }
        if (String.isBlank(newQuote.AccountCreditDecision__c)) {
            return true;
        }
        return FAILED_ACCOUNT_CREDIT_DECISION_STATUSES.contains(newQuote.AccountCreditDecision__c);
    }

    public static void clearRejectionFieldsOnStatusChange(Map<Id, Quote> oldQuotes, List<Quote> newQuotes) {
        if (oldQuotes == null || oldQuotes.size() == 0) {
            return;
        }
        if (newQuotes == null || newQuotes?.size() == 0) {
            return;
        }

        for (Quote newQuote : newQuotes) {
            Quote oldQuote = oldQuotes.get(newQuote.Id);
            if (oldQuote.status == REJECTED_QUOTE_STATUS && newQuote.status != REJECTED_QUOTE_STATUS) {
                newQuote.SubStatus__c = '';
                newQuote.RejectionReason__c = '';
            }
        }
    }

    public static void processQuoteHeaderUpdate(Map<Id, Quote> oldQuotes, List<Quote> newQuotes) {
        if (oldQuotes == null || oldQuotes.size() == 0) {
            return;
        }

        if (newQuotes == null || newQuotes?.size() == 0) {
            return;
        }
        for (Quote newQuote : newQuotes) {
            Quote oldQuote = oldQuotes.get(newQuote.Id);
            if (oldquote == newQuote || !shouldProcessQuoteUpdate(newQuote)) {
                continue;
            }
            primaryBillingContactChange(oldQuote, newQuote);
            rejectedQuoteStatusChange(oldQuote, newQuote);
            startDateOrTermChange(oldQuote, newQuote);
            totalPriceChange(oldQuote, newQuote);
        }
    }

    private static void primaryBillingContactChange(Quote oldQuote, Quote newQuote) {
        if (newQuote.PrimaryBillingContact__c != null && newQuote.PrimaryBillingContact__c != oldQuote.PrimaryBillingContact__c) {
            newQuote.BillToContactId = newQuote.PrimaryBillingContact__c;
        }
    }

    private static void rejectedQuoteStatusChange(Quote oldQuote, Quote newQuote) {
        if (isRejectedQuoteEligibleForDraft(oldQuote, newQuote)) {
            newQuote.RejectionReason__c = '';
            newQuote.Status = 'Draft';
            newQuote.ApprovalStatus__c = 'Draft';
            newQuote.SubStatus__c = '';
            newQuote.ContractTermEvalComplete__c = false;
        }
    }

    private static void startDateOrTermChange(Quote oldQuote, Quote newQuote) {
        if (isStartDateOrTermChanged(oldQuote, newQuote)) {
            if (newQuote.originalActionType != 'Amend') {
                newQuote.AutoRenewal__c = getAssignAutoRenewalValue(newQuote);
                newQuote.ServiceEndDate__c = calculateEndDate(newQuote);
            }
            if (newQuote.BillingFrequencySpecialTerm__c != '') {
                newQuote.BillingFrequencySpecialTerm__c = '';
            }
        }
    }

    @TestVisible
    private static void totalPriceChange(Quote oldQuote, Quote newQuote) {
        if (isTotalPriceChanged(oldQuote, newQuote)) {
            calculateQuoteFinancialFields(newQuote);
            if (newQuote.originalActionType != 'Amend') {
                newQuote.AutoRenewal__c = getAssignAutoRenewalValue(newQuote);
            }
        }
    }

    @TestVisible
    private static void calculateQuoteFinancialFields(Quote quote) {
        IQuoteLineDAO quoteLineDAO = (IQuoteLineDAO) ServiceRegistry.getInstance('IQuoteLineDAO');
        List<QuoteLineItem> quoteLinesList = quoteLineDAO.getQuoteLinesByQuoteId(quote.Id);
        Double beginningQuoteAOV = 0;
        Double endingQuoteAOV = 0;
        for (QuoteLineItem quoteLine : quoteLinesList) {
            Double qliAOV = calculateQliAOV(quoteLine, quote);
            if (quoteLine.SellingModelType == 'OneTime' || (quoteLine.SellingModelType == 'TermDefined' && quoteLine.StartDate == quote.ServiceStartDate__c)) {
                beginningQuoteAOV += qliAOV;
            }
            if (quoteLine.SellingModelType == 'OneTime' || (quoteLine.SellingModelType == 'TermDefined' && quoteLine.EndDate == quote.ServiceEndDate__c)) {
                endingQuoteAOV += qliAOV;
            }
        }
        quote.BeginningQuoteAOV__c = beginningQuoteAOV;
        quote.EndingQuoteAOV__c = endingQuoteAOV;
        quote.InvoiceAmount__c = calculateInvoiceAmount(quote);
    }

    private static Double calculateQliAOV(QuoteLineItem quoteLine, Quote quote) {
        Double qliAOV = 0;
        if (quoteLine.SellingModelType == 'OneTime') {
            if (quote.Term__c <= 12) {
                qliAOV = quoteLine.TotalPrice;
            } else {
                qliAOV = (quoteLine.TotalPrice / quote.Term__c) * 12;
            }
        } else if (quoteLine.PricingTermCount != null) {
            qliAOV = (quoteLine.TotalPrice / quoteLine.PricingTermCount) * 12;
        }
        return qliAOV;
    }

    private static Double calculateInvoiceAmount(Quote quote) {
        Double invoiceAmt = 0;
        if (!String.isEmpty(quote.BFSTApproval__c)) {
            invoiceAmt = quote.EndingQuoteAOV__c / frequencyMap.get(quote.BFSTApproval__c);
        } else {
            invoiceAmt = quote.EndingQuoteAOV__c / frequencyMap.get(quote.BillingFrequency__c);
        }
        return invoiceAmt;
    }

    private static Boolean isRejectedQuoteEligibleForDraft(Quote oldQuote, Quote newQuote) {
        return oldQuote.status == REJECTED_QUOTE_STATUS &&
            newQuote.SubStatus__c == oldQuote.SubStatus__c &&
            newQuote.RejectionReason__c == oldQuote.RejectionReason__c &&
            newQuote.ImportStatus__c == oldQuote.ImportStatus__c &&
            newQuote.ImportCompletionDate__c == oldQuote.ImportCompletionDate__c &&
            newQuote.TermUpdatesRequired__c == oldQuote.TermUpdatesRequired__c &&
            newQuote.AutoRollDate__c == oldQuote.AutoRollDate__c &&
            newQuote.PaymentDetailJSON__c == oldQuote.PaymentDetailJSON__c;
    }

    private static Boolean isStartDateOrTermChanged(Quote oldQuote, Quote newQuote) {
        if (newQuote.ServiceStartDate__c != oldQuote.ServiceStartDate__c || newQuote.Term__c != oldQuote.Term__c) {
            return true;
        }
        return false;
    }

    private static Boolean isTotalPriceChanged(Quote oldQuote, Quote newQuote) {
        if (newQuote.TotalPrice != oldQuote.TotalPrice) {
            return true;
        }
        return false;
    }

    private static String getAssignAutoRenewalValue(Quote newQuote) {
        if (newQuote.OriginalActionType == 'Amend') {
            return newQuote.AutoRenewal__c;
        }
        if (newQuote.Term__c < 12 && (newQuote.BeginningQuoteAOV__c > 40000 || newQuote.EndingQuoteAOV__c > 40000)) {
            return 'No';
        }
        return 'Yes';
    }

    private static Date calculateEndDate(Quote newQuote) {
        Date serviceStartDate = newQuote.ServiceStartDate__c;
        Integer term = Integer.valueOf(newQuote.Term__c);
        return newQuote.originalActionType == 'Amend' ? newQuote.ServiceEndDate__c : serviceStartDate.addMonths(term).addDays(-1);
    }

    public static void processQuoteHeaderUpdateActions(Map<Id, Quote> oldQuotes, List<Quote> newQuotes) {
        if (oldQuotes == null || oldQuotes.size() == 0) {
            return;
        }
        if (newQuotes == null || newQuotes?.size() == 0) {
            return;
        }
        List<Id> refreshPriceIds = new List<Id>();
        for (Quote newQuote : newQuotes) {
            if (!shouldProcessQuoteUpdate(newQuote)) {
                continue;
            }
            Quote oldQuote = oldQuotes.get(newQuote.Id);
            if (isStartDateOrTermChanged(oldQuote, newQuote)) {
                refreshPriceIds.add(newQuote.Id);
            }
        }
        if (!refreshPriceIds.isEmpty()) {
            refreshPriceIds(refreshPriceIds);
        }
    }

    private static void refreshPriceIds(List<Id> quoteIds) {
        List<RefreshPriceAction.RefreshPriceActionRequest> requests = new List<RefreshPriceAction.RefreshPriceActionRequest>();
        for (Id qId : quoteIds) {
            RefreshPriceAction.RefreshPriceActionRequest req = new RefreshPriceAction.RefreshPriceActionRequest();
            req.quoteId = qId;
            requests.add(req);
        }
        if (!requests.isEmpty()) {
            RefreshPriceAction.refreshPrices(requests);
        }
    }

    public static void populatePricingContract(List<Quote> newQuotes) {
        Set<Id> accountIds = new Set<Id>();

        for (Quote quote : newQuotes) {
            if (quote.PricingContract__c == null) {
                accountIds.add(quote.AccountId);
            }
        }
        if (!accountIds.isEmpty()) {
            updateQuoteWithPricingContract(accountIds, newQuotes);
        }
    }

    private static void updateQuoteWithPricingContract(Set<Id> accountIds, List<Quote> newQuotes) {
        if(accountToContractMap.isEmpty()){
        	accountToContractMap = buildAccountVsContractMap(accountIds);
        }

        for (Quote quote : newQuotes) {
            if (accountToContractMap.containsKey(quote.AccountId) && accountToContractMap.get(quote.AccountId).containsKey(quote.CurrencyIsoCode)) {
                quote.PricingContract__c = accountToContractMap.get(quote.AccountId).get(quote.CurrencyIsoCode);
            }
        }
    }

    private static Map<Id, Map<String, Id>> buildAccountVsContractMap(Set<Id> accountIds) {
        
        List<Contract> pricingContracts = contractDAO.getContractByAccountId('Pricing', accountIds);

        for (Contract con : pricingContracts) {
            if (!accountToContractMap.containsKey(con.AccountId)) {
                accountToContractMap.put(con.AccountId, new Map<String, Id>());
            }
            accountToContractMap.get(con.AccountId).put(con.CurrencyIsoCode, con.Id);
        }
        return accountToContractMap;
    }
}
