public with sharing class RLM_TxnJournalRelatedListController {
    @AuraEnabled(cacheable=true)
    public static List<TransactionJournal> getByInvoice(Id invoiceId) {
        if (invoiceId == null) {
            return new List<TransactionJournal>();
        }

        return [
            SELECT
                Id,
                Name,
                Credit,
                CreditGeneralLedgerAccount.Name,
                CurrencyIsoCode,
                Debit,
                DebitGeneralLedgerAccount.Name
            FROM TransactionJournal
            WHERE ReferenceTransactionRecordId = :invoiceId
            WITH SECURITY_ENFORCED
            ORDER BY CreatedDate DESC
        ];
    }
}