/**
 * Creates a priced Rentokil residential Quote in the field via Place Sales Transaction.
 * Always includes Initial Service (RTK-INITIAL) with the selected plan. Applies location
 * zone multiplier from RLM_RTK_Service_Zone__c to list prices before pricing.
 */
public with sharing class RLM_RTK_FieldQuote {
    public static final String INITIAL_SKU = 'RTK-INITIAL';
    public static final String LOB = 'Residential Pest';

    public class Request {
        @InvocableVariable(required=true) public Id accountId;
        @InvocableVariable(required=true) public String planSku;
        @InvocableVariable public String opportunityName;
        @InvocableVariable public String propertyType;
        @InvocableVariable public String squareFootage;
        @InvocableVariable public String severity;
        @InvocableVariable public Boolean includeMosquito;
        @InvocableVariable public Boolean includeTermite;
        @InvocableVariable public Id inspectionId;
        @InvocableVariable public String overrideReason;
    }

    public class Response {
        @InvocableVariable public Id quoteId;
        @InvocableVariable public Id opportunityId;
        @InvocableVariable public String zoneCode;
        @InvocableVariable public Decimal zoneMultiplier;
        @InvocableVariable public String message;
        @InvocableVariable public Boolean success;
    }

    @InvocableMethod(label='Create Rentokil Field Quote' category='Rentokil'
        description='Places a priced residential pest Quote for the account, including Initial Service and location pricing.')
    public static List<Response> createQuotes(List<Request> requests) {
        List<Response> responses = new List<Response>();
        for (Request request : requests) {
            responses.add(createQuote(request));
        }
        return responses;
    }

    public static Response createQuote(Request request) {
        Response response = new Response();
        response.success = false;
        try {
            Account account = [
                SELECT Id, Name, ShippingStreet, ShippingCity, ShippingState, ShippingPostalCode, ShippingCountry,
                    BillingStreet, BillingCity, BillingState, BillingPostalCode, BillingCountry
                FROM Account WHERE Id = :request.accountId
            ];
            RLM_RTK_ZonePricing.ZoneResult zone = RLM_RTK_ZonePricing.resolve(account.ShippingPostalCode);
            response.zoneCode = zone.zoneCode;
            response.zoneMultiplier = zone.multiplier;

            List<String> skus = new List<String>{ request.planSku, INITIAL_SKU };
            if (request.includeMosquito == true) {
                skus.add('RTK-MOSQUITO');
            }
            if (request.includeTermite == true) {
                skus.add('RTK-TERMITE');
            }

            Map<String, PricebookEntry> entries = new Map<String, PricebookEntry>();
            for (PricebookEntry entry : [
                SELECT Id, UnitPrice, Product2Id, Pricebook2Id, Product2.StockKeepingUnit,
                    ProductSellingModel.SellingModelType
                FROM PricebookEntry
                WHERE Product2.StockKeepingUnit IN :skus AND Pricebook2.IsStandard = true
                    AND CurrencyIsoCode = 'USD' AND IsActive = true
            ]) {
                entries.put(entry.Product2.StockKeepingUnit, entry);
            }
            if (!entries.containsKey(request.planSku) || !entries.containsKey(INITIAL_SKU)) {
                response.message = 'Missing price book entries for plan or Initial Service';
                return response;
            }

            String oppName = String.isBlank(request.opportunityName)
                ? account.Name + ' - Residential Pest'
                : request.opportunityName;
            Opportunity opportunity = new Opportunity(
                Name = oppName,
                AccountId = account.Id,
                StageName = 'Qualification',
                CloseDate = Date.today().addDays(14)
            );
            insert opportunity;
            response.opportunityId = opportunity.Id;

            String today = String.valueOf(Date.today());
            PricebookEntry planEntry = entries.get(request.planSku);
            RevSalesTrxn.RecordResource quoteRecord = new RevSalesTrxn.RecordResource(Quote.SObjectType, 'POST');
            quoteRecord.fieldValues = new Map<String, Object>{
                'Name' => oppName,
                'OpportunityId' => opportunity.Id,
                'Pricebook2Id' => planEntry.Pricebook2Id,
                'RLM_Line_of_Business__c' => LOB,
                'ShippingStreet' => account.ShippingStreet,
                'ShippingCity' => account.ShippingCity,
                'ShippingState' => account.ShippingState,
                'ShippingPostalCode' => account.ShippingPostalCode,
                'ShippingCountry' => account.ShippingCountry,
                'BillingStreet' => account.BillingStreet,
                'BillingCity' => account.BillingCity,
                'BillingState' => account.BillingState,
                'BillingPostalCode' => account.BillingPostalCode,
                'BillingCountry' => account.BillingCountry
            };

            List<RevSalesTrxn.RecordWithReferenceRequest> graphRecords =
                new List<RevSalesTrxn.RecordWithReferenceRequest>{
                    new RevSalesTrxn.RecordWithReferenceRequest('refQuote', quoteRecord)
                };
            Integer i = 1;
            for (String sku : skus) {
                PricebookEntry entry = entries.get(sku);
                if (entry == null) {
                    continue;
                }
                Decimal unitPrice = RLM_RTK_ZonePricing.apply(entry.UnitPrice, zone.multiplier);
                if (sku == request.planSku) {
                    unitPrice = applyAttributeUplift(unitPrice, request.severity, request.squareFootage);
                }
                RevSalesTrxn.RecordResource line = new RevSalesTrxn.RecordResource(QuoteLineItem.SObjectType, 'POST');
                Map<String, Object> fields = new Map<String, Object>{
                    'QuoteId' => '@{refQuote.id}',
                    'Product2Id' => entry.Product2Id,
                    'PricebookEntryId' => entry.Id,
                    'Quantity' => '1',
                    'UnitPrice' => String.valueOf(unitPrice),
                    'StartDate' => today
                };
                if (entry.ProductSellingModel != null && entry.ProductSellingModel.SellingModelType == 'Evergreen') {
                    fields.put('PeriodBoundary', 'Anniversary');
                    fields.put('BillingFrequency', 'Monthly');
                }
                line.fieldValues = fields;
                graphRecords.add(new RevSalesTrxn.RecordWithReferenceRequest('refLine' + i, line));
                i++;
            }

            RevSalesTrxn.GraphRequest graph = new RevSalesTrxn.GraphRequest('rtkFieldQuote', graphRecords);
            RevSalesTrxn.PlaceSalesTransactionResponse pstResponse =
                RevSalesTrxn.PlaceSalesTransactionExecutor.execute(
                    graph,
                    RevSalesTrxn.PricingPreferenceEnum.SYSTEM,
                    RevSalesTrxn.ConfigurationExecutionEnum.SKIP,
                    new RevSalesTrxn.ConfigurationOptionsInput(),
                    null,
                    null,
                    RevSalesTrxn.TaxPreferenceEnum.SKIP,
                    null
                );
            if (pstResponse == null || pstResponse.isSuccess != true || String.isBlank(pstResponse.salesTransactionId)) {
                response.message = 'Place Sales Transaction failed: ' +
                    (pstResponse == null ? 'null' : JSON.serialize(pstResponse.errorResponse));
                return response;
            }
            response.quoteId = pstResponse.salesTransactionId;
            if (request.inspectionId != null) {
                RLM_RTK_Inspection.markQuoted(request.inspectionId, response.quoteId, request.overrideReason);
            }
            response.success = true;
            response.message = 'Quote created with zone ' + zone.zoneCode + ' x' + String.valueOf(zone.multiplier);
        } catch (Exception e) {
            response.message = e.getMessage();
        }
        return response;
    }

    @TestVisible
    private static Decimal applyAttributeUplift(Decimal base, String severity, String squareFootage) {
        Decimal price = base == null ? 0 : base;
        if (severity == 'Moderate') {
            price += 10;
        } else if (severity == 'Heavy') {
            price += 25;
        }
        if (squareFootage == '2000to3500') {
            price += 10;
        } else if (squareFootage == 'Over3500') {
            price += 20;
        }
        return price.setScale(2, RoundingMode.HALF_UP);
    }
}
