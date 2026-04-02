public with sharing class RLM_InvoiceAgingController {
    
    @AuraEnabled(cacheable=true)
    public static InvoiceAgingData getInvoiceAgingData(Id accountId) {
        try {
            if (accountId == null) {
                return new InvoiceAgingData();
            }
            
            // Query invoices for the account with specific criteria:
            // Status = 'Posted'
            // SettlementStatus = 'PartiallySettled' OR 'NotSettled' (including label variations)
            List<Invoice> invoices = [
                SELECT Id, InvoiceNumber, DaysInvoiceOpen, DaysInvoiceOverdue, 
                       TotalAmountWithTax, Balance, DueDate, InvoiceDate, 
                       CurrencyIsoCode, Status, SettlementStatus
                FROM Invoice
                WHERE BillingAccountId = :accountId
                AND Status = 'Posted'
                AND (SettlementStatus = 'PartiallySettled' 
                     OR SettlementStatus = 'Partially Settled'
                     OR SettlementStatus = 'NotSettled'
                     OR SettlementStatus = 'Not Settled')
                ORDER BY InvoiceDate DESC
            ];
            
            return processInvoiceData(invoices);
            
        } catch (Exception e) {
            throw new AuraHandledException('Error retrieving invoice data: ' + e.getMessage());
        }
    }
    
    private static InvoiceAgingData processInvoiceData(List<Invoice> invoices) {
        InvoiceAgingData data = new InvoiceAgingData();
        
        if (invoices == null || invoices.isEmpty()) {
            return data;
        }
        
        data.totalInvoices = invoices.size();
        
        Decimal totalAmount = 0;
        Decimal totalAge = 0;
        Integer overdueCount = 0;
        Integer lessThan30 = 0;
        Integer days30To60 = 0;
        Integer moreThan60 = 0;
        
        String currencyCode = 'USD';
        
        for (Invoice inv : invoices) {
            // Get currency code from first invoice
            if (String.isNotBlank(inv.CurrencyIsoCode)) {
                currencyCode = inv.CurrencyIsoCode;
            }
            
            // Calculate totals
            if (inv.Balance != null) {
                totalAmount += inv.Balance;
            }
            
            // Calculate age using DaysInvoiceOpen
            Decimal invoiceAge = inv.DaysInvoiceOpen != null ? inv.DaysInvoiceOpen : 0;
            totalAge += invoiceAge;
            
            // Check if overdue
            if (inv.DaysInvoiceOverdue != null && inv.DaysInvoiceOverdue > 0) {
                overdueCount++;
            }
            
            // Categorize by age
            if (invoiceAge < 30) {
                lessThan30++;
            } else if (invoiceAge >= 30 && invoiceAge < 60) {
                days30To60++;
            } else {
                moreThan60++;
            }
        }
        
        // Set the data
        data.overdueInvoices = overdueCount;
        data.totalAmount = totalAmount;
        data.averageAge = data.totalInvoices > 0 ? totalAge / data.totalInvoices : 0;
        data.currencyCode = currencyCode;
        data.lessThan30 = lessThan30;
        data.days30To60 = days30To60;
        data.moreThan60 = moreThan60;
        data.invoices = invoices;
        
        return data;
    }
    
    // Wrapper class for invoice aging data
    public class InvoiceAgingData {
        @AuraEnabled public Integer totalInvoices { get; set; }
        @AuraEnabled public Integer overdueInvoices { get; set; }
        @AuraEnabled public Decimal totalAmount { get; set; }
        @AuraEnabled public Decimal averageAge { get; set; }
        @AuraEnabled public String currencyCode { get; set; }
        @AuraEnabled public Integer lessThan30 { get; set; }
        @AuraEnabled public Integer days30To60 { get; set; }
        @AuraEnabled public Integer moreThan60 { get; set; }
        @AuraEnabled public List<Invoice> invoices { get; set; }
        
        public InvoiceAgingData() {
            this.totalInvoices = 0;
            this.overdueInvoices = 0;
            this.totalAmount = 0;
            this.averageAge = 0;
            this.currencyCode = 'USD';
            this.lessThan30 = 0;
            this.days30To60 = 0;
            this.moreThan60 = 0;
            this.invoices = new List<Invoice>();
        }
    }
}