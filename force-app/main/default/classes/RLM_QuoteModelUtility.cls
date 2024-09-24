public class RLM_QuoteModelUtility {
    @InvocableMethod(label='Convert Quote to Context String' description='Converts a Single Quote to SalesTranscationModel for context' category='RLM SE TAT')
    public static List<String> CreateQuoteContextString(List<Id> quoteId){
        Quote q = getQuote(quoteId);
        List<QuoteLineItem> qls = getQuoteLines(q.Id);

        SalesContextModel SalesContext = new SalesContextModel();

        SalesContext.SalesTransaction.SalesTransactionSource = q.Id;
        SalesContext.SalesTransaction.PriceBooks = q.Pricebook2Id;
        SalesContext.SalesTransaction.EffectiveDate = String.valueOf(q.CreatedDate.format('yyyy-MM-dd\'T\'HH:mm:ss.SSS\'Z\''));
        SalesContext.SalesTransaction.CurrencyIsoCode = q.CurrencyIsoCode;
        SalesContext.SalesTransaction.SalesTransactionItem = new List<SalesTransactionItemModel>();

        for(QuoteLineItem ql: qls){
            SalesTransactionItemModel item = new SalesTransactionItemModel();

            List<QuoteLineItemAttribute> qlAtts = [SELECT QuoteLineItemId, AttributeName, AttributeValue
                                                    FROM QuoteLineItemAttribute 
                                                    WHERE QuoteLineItemId =: ql.Id];
                                                    
            List<QuoteLineRelationship> qlRs =  [SELECT  AssociatedQuoteLineId, AssociatedQuoteLine.ProductSellingModelId, AssociatedQuoteLine.Product2Id,
                                                    AssociatedQuoteLinePricing, MainQuoteLineId, MainQuoteLine.ProductSellingModelId, MainQuoteLine.Product2Id
                                                     FROM QuoteLineRelationship WHERE AssociatedQuoteLineId =: ql.Id];

            item.SalesTransactionItemParent = ql.QuoteId;
            item.price_water_fall = '';
            item.ProductSellingModel = ql.ProductSellingModelId;
            item.ItemSubscriptionTerm = String.valueOf(ql.SubscriptionTerm);
            item.Product = ql.Product2Id;
            item.InputUnitPrice = String.valueOf(ql.ListPrice);
            item.StartProrationPeriodDay = string.valueOf(ql.StartDate.day());
            item.StartProrationPeriod = ql.PeriodBoundary;
            item.AllowPartialProrationPeriods = string.valueOf(ql.ProrationPolicy.ArePartialPeriodsAllowed) ;
            item.StartProrationPeriodMonth = string.valueOf(DateTime.newInstance(ql.StartDate.year(), ql.StartDate.month(), ql.StartDate.day(), 0, 0, 0).format('MMMM'));
            item.ItemDiscountAmount = String.valueOf(ql.DiscountAmount);
            item.ItemDiscountPercentage = String.valueOf(ql.Discount);
            item.SalesTransactionItemAttribute = new List<SalesTransactionItemAttributeModel>();
            item.EffectiveFrom = convertStartDate(ql.StartDate);
            item.EffectiveTo = convertEndDate(ql.EndDate);
            item.SalesTrxnItemRelationship = new List<SalesTransactionItemRelationshipModel>();
            item.ContributorPriceDetail = new List<ContributorPriceDetailModel>();
            item.LineItem = ql.Id;
            item.LineItemQuantity = String.valueOf(ql.Quantity);
            item.ItemPricingSource = 'PriceBook';
            item.SellingModelType = ql.SellingModelType;
            item.PricingTermUnit = ql.PricingTermUnit;

            if(qlAtts.size()>0){
                for(QuoteLineItemAttribute qlAtt: qlAtts){
                    SalesTransactionItemAttributeModel att = new SalesTransactionItemAttributeModel();
                    att.SalesTransactionItemAttrParent = ql.Id;
                    att.PriceImpactingAttribute = 'TRUE';
                    att.Attribute = qlAtt.AttributeName;
                    att.AttributeValue = qlAtt.AttributeValue;

                    item.SalesTransactionItemAttribute.add(att);
                }
            }

            if(qlRs.size()>0){
                for(QuoteLineRelationship qlr: qlRs){
                    SalesTransactionItemRelationshipModel rm = new SalesTransactionItemRelationshipModel();

                    if(qlr.AssociatedQuoteLinePricing == 'NotIncludedInBundlePrice'){
                        rm.InclusivePrice = 'FALSE';
                    }else{
                        rm.InclusivePrice = 'TRUE';
                    }

                    rm.SalesTrnItemRelationshipParent = ql.Id;
                    rm.RootProductSellingModel = qlr.MainQuoteLine.ProductSellingModelId;
                    rm.MainItemProductSellingModel = qlr.MainQuoteLine.ProductSellingModelId;
                    rm.RootItemProduct = qlr.MainQuoteLine.Product2Id;
                    rm.MainItemProduct = qlr.MainQuoteLine.Product2Id;
                    
                    item.SalesTrxnItemRelationship.add(rm);
                }
            }

            SalesContext.SalesTransaction.SalesTransactionItem.add(item);
        }
        system.debug(JSON.serialize(SalesContext));
        List<String> JSONstringsToReturn = new List<String>();
		
        String JSONstringToReturn = JSON.serialize(SalesContext).replace('null', '""');
        JSONstringsToReturn.add(JSONstringToReturn);
        system.debug(JSONstringsToReturn);
        return JSONstringsToReturn;
    }

    public static Quote getQuote(List<Id> quoteId){
        Quote q = [SELECT Id, Pricebook2Id, CurrencyIsoCode, CreatedDate 
                    FROM Quote 
                    WHERE Id IN: quoteId LIMIT 1].get(0);
        return q;
    }

    public static List<QuoteLineItem> getQuoteLines(Id quoteId){
        List<QuoteLineItem> qls = [SELECT QuoteId, ProductSellingModelId, SubscriptionTerm, Product2Id,
                                ListPrice, Discount, DiscountAmount, StartDate, EndDate, LineNumber, Quantity, 
                                PeriodBoundary, PeriodBoundaryDay, PeriodBoundaryStartMonth, SellingModelType,
                                ProrationPolicy.ArePartialPeriodsAllowed, PricingTermUnit 
                                FROM QuoteLineItem WHERE QuoteId =: quoteId];

        return qls;
    }

    public static string convertStartDate(Date sd){
        DateTime startDateTime = DateTime.newInstance(sd.year(), sd.month(), sd.day(), 0, 0, 0);
        String convertedStartDateTime = startDateTime.format('yyyy-MM-dd\'T\'HH:mm:ss.SSS\'Z\'');

        return convertedStartDateTime;
    }

    public static string convertEndDate(Date ed){
        DateTime endDateTime = DateTime.newInstance(ed.year(), ed.month(), ed.day(), 23, 59, 59);
        String convertedEndDateTime = endDateTime.format('yyyy-MM-dd\'T\'HH:mm:ss.SSS\'Z\'');

        return convertedEndDateTime;
    }

    public class SalesContextModel{
        public SalesTransactionModel SalesTransaction;

        public SalesContextModel(){
            SalesTransaction = new SalesTransactionModel();
        }
    }

    public class SalesTransactionModel{
        public String SalesTransactionSource;
        public String PriceBooks;
        public List<SalesTransactionItemModel> SalesTransactionItem;
        public string CurrencyIsoCode;
        public string EffectiveDate;
        public string TotalAmount;
    }

    public class SalesTransactionItemModel{
        public string SalesTransactionItemParent;
        public string TotalLineAmount;
        public string price_water_fall;
        public string ProductSellingModel;
        public string ItemSubscriptionTerm;
        public string Product;
        public string InputUnitPrice;
        public string StartProrationPeriodDay;
        public string StartProrationPeriod;
        public string AllowPartialProrationPeriods;
        public string StartProrationPeriodMonth;
        public string ItemDiscountAmount;
        public string ItemDiscountPercentage;
        public List<SalesTransactionItemAttributeModel> SalesTransactionItemAttribute;
        public string EffectiveFrom;
        public string EffectiveTo;
        public List<SalesTransactionItemRelationshipModel> SalesTrxnItemRelationship;
        public List<ContributorPriceDetailModel> ContributorPriceDetail;
        public string LineItem;
        public string LineItemQuantity;
        public string ItemPricingSource;
        public string ItemContract;
        public string SellingModelType;
        public string PricingTermCount;
        public string PricingTermUnit;
        public string DerivedPricingAttribute;
        public string IsContracted;
        public string ItemContractDiscountValue;
        public string ItemContractPrice;
        public string ItemContractAttributePasId;
        public string ItemContractDiscountType;
        public string ItemContractVolumePasId;
    }

    public class SalesTransactionItemAttributeModel{
        public string SalesTransactionItemAttrParent;
        public string PriceImpactingAttribute;
        public string AttributeValue;
        public string Attribute;
    }

    public class ContributorPriceDetailModel{
        public string ContributorFormulaInput;
        public string ContributorScope;
        public string ContributorSource;
        public string ContributorTotalPrice;
        public string ContributorUnitPrice;
        public string Contributor;
    }

    public class SalesTransactionItemRelationshipModel{
        public string SalesTrnItemRelationshipParent;
        public string InclusivePrice;
        public string RootProductSellingModel;
        public string MainItemProductSellingModel;
        public string RootItemProduct;
        public string MainItemProduct;
    }
}