public with sharing class EffectiveDiscountService implements IEffectiveDiscountService {

    private static final String SUPPRESS_EFFECTIVE_DISCOUNT_ATTR_NAME = 'Suppress_Effective_Discounting';
    private static final String CURRENCY_ISO_CODE_USD = 'USD';

    private static final String QLI_FIELD_DISCOUNT = 'Discount';
    private static final String QLI_FIELD_DISCOUNT_AMOUNT = 'DiscountAmount';
    private static final String QLI_FIELD_NET_UNIT_PRICE = 'NetUnitPrice';

    private IContractItemPriceDAO contractItemPriceDAO;
    private IConstantFXRateDAO constantFXRateDAO;
    private IEffectiveDiscountingFactorDAO effectiveDiscountingFactorDAO;

    public EffectiveDiscountService() {
        this.contractItemPriceDAO = (IContractItemPriceDAO) ServiceRegistry.getInstance('IContractItemPriceDAO');
        this.constantFXRateDAO = (IConstantFXRateDAO) ServiceRegistry.getInstance('IConstantFXRateDAO');
        this.effectiveDiscountingFactorDAO = (IEffectiveDiscountingFactorDAO) ServiceRegistry.getInstance('IEffectiveDiscountingFactorDAO');
    }

    public boolean shouldRun(Map<Id, QuoteLineItem> newQuoteLineItems, Map<Id, QuoteLineItem> oldQuoteLineItems) {

        List<QuoteLineItem> lines = newQuoteLineItems?.values();

        if (newQuoteLineItems?.values() == null || newQuoteLineItems?.values().isEmpty()) {
            return false;
        }
        
        for (QuoteLineItem qli : newQuoteLineItems.values()) {
            if (shouldProcess(qli, oldQuoteLineItems)) {
                return true;
            }
        }
        return false;
    }

    public List<QuoteLineItem> calculateEffectiveDiscount(QuoteLineTriggerDataBag dataBag) {
        List<QuoteLineItem> quoteLinesToUpdate = new List<QuoteLineItem>();
        Set<Id> productIds = new Set<Id>();
        List<QuoteLineItem> lines = dataBag.newQuoteLineItems?.values();
        List<QuoteLineItem> eligibleLines = new List<QuoteLineItem>();
        if (lines == null || lines.isEmpty()) {
            return quoteLinesToUpdate;
        }
        for (QuoteLineItem qli : lines) {
            if (shouldProcess(qli, dataBag.oldQuoteLineItems)) {
                eligibleLines.add(qli);
            }
            productIds.add(qli.Product2Id);
        }
        
        if (eligibleLines.isEmpty()) {
            return quoteLinesToUpdate;
        }

        Map<Id, Map<String, Object>> productAttributes = dataBag.productAttributes;
        Map<Id, QuoteLineItem> quoteLinesWithRelatedFieldsForQuote = new Map<Id, QuoteLineItem>(dataBag.quoteLineItemsWithRelatedFieldsByQuote.get(lines.get(0).QuoteId));

        // just get first element from set
        Set<Id> accountIdSet = new Set<Id> { quoteLinesWithRelatedFieldsForQuote.values().get(0).Quote.AccountId };
        String currencyCode = quoteLinesWithRelatedFieldsForQuote.values().get(0).Quote.CurrencyIsoCode;
        String billingCountry = quoteLinesWithRelatedFieldsForQuote.values().get(0).Quote.BillingCountry;
        EffectiveDiscountingFactor edf = retrieveEffectiveDiscountingFactor(billingCountry, currencyCode);
        Decimal constantFX = calculateConstantFX(currencyCode);
        Map<Id, ContractItemPrice> contractItemPrices = getFinalizedContractItemPrices(productIds, accountIdSet, currencyCode);

        for (QuoteLineItem qli : eligibleLines) {
            ContractItemPrice cip = contractItemPrices.get(qli.Product2Id);
            QuoteLineItem currentQuoteLineItem = quoteLinesWithRelatedFieldsForQuote.get(qli.Id);
            Boolean isDerived = currentQuoteLineItem.PricebookEntry.IsDerived;
            Decimal listPrice = currentQuoteLineItem.ListPrice;
            // If attribute is null, default to false
            Boolean suppressEffectiveDiscount = isEffectiveDiscountSuppressed(qli, productAttributes);
            if (shouldSetEffectiveDiscountToZero(qli, cip, listPrice)) {
                qli.EffectiveDiscount__c = 0; 
                quoteLinesToUpdate.add(currentQuoteLineItem);
            } else if (suppressEffectiveDiscount && qli.Quantity > 0) {
                qli.EffectiveDiscount__c = calculateEffectiveDiscount(qli, listPrice, cip);
                quoteLinesToUpdate.add(currentQuoteLineItem);
            } else if (edf != null && !suppressEffectiveDiscount && qli.Quantity > 0) {
                qli.EffectiveDiscount__c = calculateEffectiveDiscountWithFactor(qli, listPrice, isDerived, constantFX, cip, edf);
                quoteLinesToUpdate.add(currentQuoteLineItem);
            }
            
        }
        return quoteLinesToUpdate;
    }

    private Map<Id, ContractItemPrice> getFinalizedContractItemPrices(Set<Id> productIds, Set<Id> accountIds, String currencyIsoCode) {
        // assume quote lines belong to same quote and account
        List<ContractItemPrice> contractItemPrices = (List<ContractItemPrice>) contractItemPriceDAO.getContractQuoteFinalized('Finalized', accountIds, productIds, true, currencyIsoCode);
        Map<Id, ContractItemPrice> contractItemPriceMap = new Map<Id, ContractItemPrice>();
        for (ContractItemPrice cip : contractItemPrices) { 
            if (!contractItemPriceMap.containsKey(cip.ItemId) && cip.EndDate == null) {
                contractItemPriceMap.put(cip.ItemId, cip);
            }
        }

        return contractItemPriceMap;            
    }

    private EffectiveDiscountingFactor retrieveEffectiveDiscountingFactor(String country, String currencyIsoCode) {
        List<EffectiveDiscountingFactor__mdt> effectiveDiscountingFactors = effectiveDiscountingFactorDAO.getEffectiveDiscountingFactorForCountryAndCurrency(country, currencyIsoCode);
        if (effectiveDiscountingFactors.size() == 1) {
            EffectiveDiscountingFactor__mdt effectiveDiscountingFactor = effectiveDiscountingFactors.get(0);
            return new EffectiveDiscountingFactor(effectiveDiscountingFactor);
        }
        return null;
    }

    private Decimal calculateConstantFX(String currencyCode) {
        if (currencyCode == CURRENCY_ISO_CODE_USD) {
            return 1;
        }
        List<ConstantFXRate__mdt> constantFXRates = constantFXRateDAO.getConstantFXRates(currencyCode);
        if (constantFXRates.size() == 1) {
            return constantFXRates.get(0).ConstantFXRate__c;
        }
        return null;
    }

    private Decimal calculateEffectiveDiscount(QuoteLineItem lineItem, Decimal listPrice, ContractItemPrice cip) {
        Decimal effectiveDiscount = 0;
        Boolean hasContractItemPrice = cip != null;
        Decimal currentNetUnitPrice = calculateNetUnitPrice(lineItem);
        
        if (listPrice != null && listPrice != 0) {
            effectiveDiscount = (1 - (currentNetUnitPrice / listPrice)) * 100;
        }
            
        if (effectiveDiscount < 0 || lineItem.Quantity < 0) {
            effectiveDiscount = 0;
        }
        return effectiveDiscount;
    }
    
    private Decimal calculateNetUnitPrice(QuoteLineItem lineItem) {
       return lineItem.NetUnitPrice;
    }

    private Decimal calculateLocalCurrencyDiscount(QuoteLineItem lineItem, Decimal listPrice, Boolean isDerived, ContractItemPrice cip) {
        Decimal localCurrencyDiscount = 0;
        Decimal currentNetUnitPrice = calculateNetUnitPrice(lineItem);
        if (isDerived && currentNetUnitPrice != null && currentNetUnitPrice != 0) {
            localCurrencyDiscount = 1 - (lineItem.UnitPrice / currentNetUnitPrice);
        } else if (currentNetUnitPrice != null && listPrice != null && listPrice != 0) {
            localCurrencyDiscount = 1 - (currentNetUnitPrice / listPrice);
        }

        Decimal maxPADiscount = calculateMaxPADiscount(lineItem, listPrice, cip);
        if (maxPADiscount != null && localCurrencyDiscount < maxPADiscount) {
            localCurrencyDiscount = maxPADiscount;
        }

        return localCurrencyDiscount;
    }

    private Decimal calculateMaxPADiscount(QuoteLineItem lineItem, Decimal listPrice, ContractItemPrice cip) {
        if (cip == null || listPrice == 0) {
            return null;
        }
        return 1 - (cip.Price / listPrice);
    }

    private Decimal calculateEffectiveDiscountWithFactor(QuoteLineItem lineItem, Decimal listPrice, Boolean isDerived, Decimal constantFX, ContractItemPrice cip, EffectiveDiscountingFactor edf) {
        Decimal effectiveDiscount = 0;
        Decimal localCurrencyDiscount = calculateLocalCurrencyDiscount(lineItem, listPrice, isDerived, cip);
        Decimal expr1 = 100 * constantFX;
        Decimal expr2 = 100 * edf.currentFX;
        Decimal expr3 = 1 - localCurrencyDiscount;
        Decimal expr4;

        if (expr2 != 0) {
            expr4 = expr1 / expr2;
        }
        if (expr4 != null) {
            effectiveDiscount = (1 - (expr4 * expr3)) * 100; 
        }

        if (effectiveDiscount < 0) {
            effectiveDiscount = 0;
        } else if (effectiveDiscount > 100) {
            effectiveDiscount = 100;
        }

        return effectiveDiscount;
    }

    private class EffectiveDiscountingFactor {
        public String standardCountry;
        public String currencyIsoCode;
        public Date startDate;
        public Date endDate;
        public Decimal currentFX;

        public EffectiveDiscountingFactor(EffectiveDiscountingFactor__mdt effectiveDiscountingFactor) {
            this.standardCountry = effectiveDiscountingFactor.StandardCountry__c;
            this.currencyIsoCode = effectiveDiscountingFactor.Currency__c;
            this.startDate = effectiveDiscountingFactor.StartDate__c;
            this.endDate = effectiveDiscountingFactor.EndDate__c;
            this.currentFX = effectiveDiscountingFactor.CurrentFX__c;
        }
    }

    public static Boolean isEffectiveDiscountSuppressed(QuoteLineItem quoteLine, Map<Id, Map<String, Object>> productAttributes) {
        return Boolean.valueOf(productAttributes.get(quoteLine.Product2Id).get(SUPPRESS_EFFECTIVE_DISCOUNT_ATTR_NAME) ?? false);
    }

    private Boolean shouldSetEffectiveDiscountToZero(QuoteLineItem qli, ContractItemPrice cip, Decimal listPrice) {
        if (!hasDiscountSet(qli, listPrice)) {
            return true;
        } 
        return cip != null && cip.Price == calculateNetUnitPrice(qli) && qli.Quantity > 0;
    }

    private static Boolean shouldProcess(QuoteLineItem qli, Map<Id, QuoteLineItem> oldQuoteLineItems) {
        for (String fieldName : new List<String> {QLI_FIELD_DISCOUNT, QLI_FIELD_DISCOUNT_AMOUNT, QLI_FIELD_NET_UNIT_PRICE}) {
            if (fieldIsChanged(fieldName, qli, oldQuoteLineItems)) {
                return true;
            }
        }
        return false;
    }

    private static Boolean fieldIsChanged(String fieldName, QuoteLineItem qli, Map<Id, QuoteLineItem> oldQuoteLineItems) {
        return qli.get(fieldName) != oldQuoteLineItems?.get(qli.Id)?.get(fieldName);
    }

    private static Boolean hasDiscountSet(QuoteLineItem qli, Decimal listPrice) {
        if (listPrice != 0 && qli.UnitPrice < listPrice) {
            return true;
        }
        for (String fieldName : new List<String> {QLI_FIELD_DISCOUNT, QLI_FIELD_DISCOUNT_AMOUNT}) {
            if (qli.get(fieldName) != null && qli.get(fieldName) != 0) {
                return true;
            }
        }
        return false;
    }
}