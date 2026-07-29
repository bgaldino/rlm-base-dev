/**
 * Provides Quote and QuoteLineItem data for the Service Proposal LWC.
 * Returns client name, billing street only, line items with pricing, and summary totals.
 */
public with sharing class RLM_HomeServices_ServiceProposalCtrl {

    public class LineItemWrapper {
        @AuraEnabled public String name;
        @AuraEnabled public String description;
        @AuraEnabled public Decimal listPrice;
        @AuraEnabled public Decimal promotion;
        @AuraEnabled public Decimal customerDiscount;
        @AuraEnabled public Decimal finalPrice;
    }

    public class ProposalWrapper {
        @AuraEnabled public String clientName;
        @AuraEnabled public String billingStreet;
        @AuraEnabled public List<LineItemWrapper> lineItems;
        @AuraEnabled public Decimal servicesTotal;
        @AuraEnabled public Decimal promotionsTotal;
        @AuraEnabled public Decimal discountsTotal;
        @AuraEnabled public Decimal tax;
        @AuraEnabled public Decimal grandTotal;
    }

    @AuraEnabled(cacheable=true)
    public static ProposalWrapper getQuoteData(String quoteId) {
        if (String.isBlank(quoteId)) {
            return null;
        }
        Id qId;
        try {
            qId = Id.valueOf(quoteId);
        } catch (Exception e) {
            return null;
        }

        List<Quote> quotes = [
            SELECT Id, QuoteToName, QuoteToStreet, QuoteAccountId,
                   Subtotal, TotalPrice, TotalPriceWithTax
            FROM Quote
            WHERE Id = :qId
            LIMIT 1
        ];
        if (quotes.isEmpty()) {
            return null;
        }
        Quote q = quotes[0];

        String clientName = String.isNotBlank(q.QuoteToName)
            ? q.QuoteToName
            : null;
        String billingStreet = String.isNotBlank(q.QuoteToStreet)
            ? q.QuoteToStreet
            : null;

        if (q.QuoteAccountId != null && (String.isBlank(clientName) || String.isBlank(billingStreet))) {
            List<Account> accts = [
                SELECT Name, BillingStreet
                FROM Account
                WHERE Id = :q.QuoteAccountId
                LIMIT 1
            ];
            if (!accts.isEmpty()) {
                if (String.isBlank(clientName)) clientName = accts[0].Name;
                if (String.isBlank(billingStreet)) billingStreet = accts[0].BillingStreet;
            }
        }

        List<QuoteLineItem> qlis = [
            SELECT Product2.Name, Product2.Description,
                   UnitPrice, Subtotal, TotalPrice, Discount
            FROM QuoteLineItem
            WHERE QuoteId = :qId
            ORDER BY CreatedDate
        ];

        List<LineItemWrapper> items = new List<LineItemWrapper>();
        Decimal servicesSum = 0;
        Decimal promotionsSum = 0;
        Decimal discountsSum = 0;

        for (QuoteLineItem qli : qlis) {
            Decimal subtotal = qli.Subtotal != null ? qli.Subtotal : 0;
            Decimal totalPrice = qli.TotalPrice != null ? qli.TotalPrice : 0;
            Decimal lineDiscount = subtotal - totalPrice;
            if (lineDiscount < 0) lineDiscount = 0;

            Decimal listPrice = qli.UnitPrice != null ? qli.UnitPrice : 0;
            Decimal promotion = 0;
            Decimal customerDiscount = lineDiscount;

            LineItemWrapper w = new LineItemWrapper();
            w.name = qli.Product2 != null ? qli.Product2.Name : '';
            w.description = qli.Product2 != null && String.isNotBlank(qli.Product2.Description)
                ? qli.Product2.Description
                : '';
            w.listPrice = listPrice;
            w.promotion = promotion;
            w.customerDiscount = customerDiscount;
            w.finalPrice = totalPrice;
            items.add(w);

            servicesSum += subtotal;
            promotionsSum += promotion;
            discountsSum += customerDiscount;
        }

        Decimal grandTotal = q.TotalPrice != null ? q.TotalPrice : 0;
        Decimal totalWithTax = q.TotalPriceWithTax != null ? q.TotalPriceWithTax : grandTotal;
        Decimal taxAmount = totalWithTax - grandTotal;
        if (taxAmount < 0) taxAmount = 0;

        ProposalWrapper result = new ProposalWrapper();
        result.clientName = clientName != null ? clientName : '';
        result.billingStreet = billingStreet != null ? billingStreet : '';
        result.lineItems = items;
        result.servicesTotal = servicesSum;
        result.promotionsTotal = promotionsSum;
        result.discountsTotal = discountsSum;
        result.tax = taxAmount;
        result.grandTotal = totalWithTax;

        return result;
    }
}