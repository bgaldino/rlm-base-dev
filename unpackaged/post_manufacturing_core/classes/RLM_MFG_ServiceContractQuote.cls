public with sharing class RLM_MFG_ServiceContractQuote {

    @InvocableMethod(label='Create Service Contract Quote' description='Creates a service contract quote for one or more assets and returns the quote id' category='Quote')
    public static List<String> createUpdateQuote(List<svcContractRequest> svcContractRequests) {
        if (svcContractRequests == null || svcContractRequests.isEmpty()
                || svcContractRequests[0].assets == null || svcContractRequests[0].assets.isEmpty()) {
            return new List<String>();
        }

        List<Id> myAssetIds = new List<Id>();
        for (sObject myObject : svcContractRequests[0].assets) {
            myAssetIds.add(myObject.Id);
        }

        // Restrict to root (parent) assets only — child asset IDs are discarded
        List<Asset> myAssets = [SELECT Id, AccountId FROM Asset WHERE Id IN :myAssetIds AND ParentId = null WITH USER_MODE];
        if (myAssets.isEmpty()) {
            return new List<String>();
        }

        Id accountId = myAssets[0].AccountId;

        // Resolve account name and address to populate quote fields
        List<Account> accounts = [
            SELECT Id, Name, BillingStreet, BillingCity, BillingPostalCode, BillingCountry,
                   ShippingStreet, ShippingCity, ShippingPostalCode, ShippingCountry
            FROM Account WHERE Id = :accountId WITH USER_MODE LIMIT 1
        ];
        Account acct = accounts.isEmpty() ? null : accounts[0];

        // Primary contact for the account — used for BillToContactId / ContactId
        List<Contact> contacts = [SELECT Id FROM Contact WHERE AccountId = :accountId WITH USER_MODE LIMIT 1];
        Id contactId = contacts.isEmpty() ? null : contacts[0].Id;

        // Validate the two inputs bound directly into SOQL Id filters below, so a
        // malformed value is a friendly, catchable error rather than a raw QueryException.
        Id productId                   = toId(svcContractRequests[0].productId, 'product id');
        Id priceBookId                 = toId(svcContractRequests[0].priceBookId, 'price book id');
        String priceBookEntryId        = svcContractRequests[0].priceBookEntryId;
        String productRelationshipTypeId = svcContractRequests[0].productRelationshipTypeId;

        // Required bundle components for the selected service contract product
        List<ProductRelatedComponent> options = [
            SELECT Id, Quantity, ChildProductId, ChildSellingModelId
            FROM ProductRelatedComponent
            WHERE ParentProductId = :productId AND IsComponentRequired = TRUE
            WITH USER_MODE
        ];
        List<Id> optionIds = new List<Id>();
        for (ProductRelatedComponent prc : options) {
            optionIds.add(prc.ChildProductId);
        }

        // Map child product + selling model -> PricebookEntry Id. A product can have one
        // entry per selling model in the same pricebook, so key by both to avoid an
        // arbitrary row winning.
        List<PriceBookEntry> pbes = [
            SELECT Id, Product2Id, ProductSellingModelId
            FROM PriceBookEntry
            WHERE Product2Id IN :optionIds AND Pricebook2Id = :priceBookId
            WITH USER_MODE
        ];
        Map<String, String> optionPBEs = new Map<String, String>();
        for (PriceBookEntry pbe : pbes) {
            optionPBEs.put(pbeKey(pbe.Product2Id, pbe.ProductSellingModelId), pbe.Id);
        }

        // ── Quote header ──────────────────────────────────────────────────────────
        RevSalesTrxn.RecordResource quoteRecord = new RevSalesTrxn.RecordResource(Quote.getSobjectType(), 'POST');
        Map<String, Object> quoteFieldValues = new Map<String, Object>();
        String acctName = (acct != null && acct.Name != null) ? acct.Name : '';
        quoteFieldValues.put('Name', 'Service Contract Quote - ' + acctName);
        quoteFieldValues.put('QuoteAccountId', accountId);
        quoteFieldValues.put('Pricebook2Id', priceBookId);

        if (contactId != null) {
            quoteFieldValues.put('BillToContactId', contactId);
            quoteFieldValues.put('ContactId', contactId);
        }

        if (acct != null) {
            if (acct.BillingStreet    != null) quoteFieldValues.put('BillingStreet',     acct.BillingStreet);
            if (acct.BillingCity      != null) quoteFieldValues.put('BillingCity',       acct.BillingCity);
            if (acct.BillingPostalCode!= null) quoteFieldValues.put('BillingPostalCode', acct.BillingPostalCode);
            if (acct.BillingCountry   != null) quoteFieldValues.put('BillingCountry',    acct.BillingCountry);
            if (acct.ShippingStreet   != null) quoteFieldValues.put('ShippingStreet',    acct.ShippingStreet);
            if (acct.ShippingCity     != null) quoteFieldValues.put('ShippingCity',      acct.ShippingCity);
            if (acct.ShippingPostalCode!= null) quoteFieldValues.put('ShippingPostalCode',acct.ShippingPostalCode);
            if (acct.ShippingCountry  != null) quoteFieldValues.put('ShippingCountry',   acct.ShippingCountry);
        }

        quoteRecord.fieldValues = quoteFieldValues;
        RevSalesTrxn.RecordWithReferenceRequest quoteRef =
            new RevSalesTrxn.RecordWithReferenceRequest('refQuote', quoteRecord);

        List<RevSalesTrxn.RecordWithReferenceRequest> listOfRecords =
            new List<RevSalesTrxn.RecordWithReferenceRequest>{ quoteRef };

        Date startDate    = Date.today().addDays(10);
        Date endDate      = Date.today().addDays(374);
        String startDateStr = String.valueOf(startDate);
        String endDateStr   = String.valueOf(endDate);

        // ── One QLI (+ required component QLIs + QLRs) per selected asset ────────
        // RLM_MFG_Covered_Asset__c is included in the graph and preserved by PST
        // via the CoveredAsset__c attribute registered in RLM_SalesTransactionContext.
        Integer assetCounter = 0;
        for (Asset myAsset : myAssets) {
            assetCounter++;
            String parentRef = 'refQuoteItem1_' + assetCounter;

            // Service contract product line
            RevSalesTrxn.RecordResource qliRecord = new RevSalesTrxn.RecordResource(QuoteLineItem.getSobjectType(), 'POST');
            Map<String, Object> qliFields = new Map<String, Object>();
            qliFields.put('Product2Id',             productId);
            qliFields.put('PricebookEntryId',        priceBookEntryId);
            qliFields.put('Quantity',                '1.0');
            qliFields.put('StartDate',               startDateStr);
            qliFields.put('EndDate',                 endDateStr);
            qliFields.put('PeriodBoundary',          'Anniversary');
            qliFields.put('BillingFrequency',        'Annual');
            qliFields.put('QuoteId',                 '@{refQuote.id}');
            qliFields.put('RLM_MFG_Covered_Asset__c', (String) myAsset.Id);
            qliRecord.fieldValues = qliFields;
            listOfRecords.add(new RevSalesTrxn.RecordWithReferenceRequest(parentRef, qliRecord));

            // Required bundle component lines + QuoteLineRelationships
            Integer optionCounter = 0;
            for (ProductRelatedComponent prc : options) {
                optionCounter++;
                String childRef = 'refQuoteItem_' + assetCounter + '_' + optionCounter;

                // Every required component must resolve to a PricebookEntry, or the PST
                // graph would carry a null PricebookEntryId and fail opaquely. Fail early
                // with a friendly, catchable error instead.
                String componentPbeId = optionPBEs.get(pbeKey(prc.ChildProductId, prc.ChildSellingModelId));
                if (componentPbeId == null) {
                    throw new RLM_MFG_ServiceContractQuoteException(
                        'No PricebookEntry found for required component product ' + prc.ChildProductId
                        + ' (selling model ' + prc.ChildSellingModelId + ') in price book ' + priceBookId
                        + '. Cannot build the service contract quote.');
                }

                RevSalesTrxn.RecordResource optionRecord = new RevSalesTrxn.RecordResource(QuoteLineItem.getSobjectType(), 'POST');
                Map<String, Object> optionFields = new Map<String, Object>();
                optionFields.put('Product2Id',             prc.ChildProductId);
                optionFields.put('PricebookEntryId',        componentPbeId);
                // Preserve the required component's configured quantity; default to 1 when null.
                // prc.Quantity is a Double, so build the string directly to avoid a
                // Double-to-Decimal assignment and keep the existing "N.0" payload convention.
                String componentQty = (prc.Quantity != null) ? String.valueOf(prc.Quantity) : '1.0';
                optionFields.put('Quantity',                componentQty);
                optionFields.put('StartDate',               startDateStr);
                optionFields.put('EndDate',                 endDateStr);
                optionFields.put('PeriodBoundary',          'Anniversary');
                optionFields.put('BillingFrequency',        'Annual');
                optionFields.put('QuoteId',                 '@{refQuote.id}');
                optionFields.put('RLM_MFG_Covered_Asset__c', (String) myAsset.Id);
                optionRecord.fieldValues = optionFields;
                listOfRecords.add(new RevSalesTrxn.RecordWithReferenceRequest(childRef, optionRecord));

                // Quote Line Relationship linking component to parent line
                RevSalesTrxn.RecordResource qlrRecord = new RevSalesTrxn.RecordResource(QuoteLineRelationship.getSobjectType(), 'POST');
                Map<String, Object> qlrFields = new Map<String, Object>();
                qlrFields.put('ProductRelationshipTypeId',  productRelationshipTypeId);
                qlrFields.put('ProductRelatedComponentId',  prc.Id);
                qlrFields.put('MainQuoteLineId',            '@{' + parentRef + '.id}');
                qlrFields.put('AssociatedQuoteLineId',      '@{' + childRef + '.id}');
                qlrFields.put('AssociatedQuoteLinePricing', 'IncludedInBundlePrice');
                qlrRecord.fieldValues = qlrFields;
                listOfRecords.add(new RevSalesTrxn.RecordWithReferenceRequest(
                    'QuoteLineRelationship_' + assetCounter + '_' + optionCounter, qlrRecord));
            }
        }

        // ── Execute Place Sales Transaction ───────────────────────────────────────
        // RLM_SalesTransactionContext (QuoteEntitiesMapping, isDefault=true) is applied
        // automatically by PST for Quote transactions. CoveredAsset__c registered as
        // INPUTOUTPUT on SalesTransactionItem allows PST to preserve RLM_MFG_Covered_Asset__c.
        RevSalesTrxn.ConfigurationOptionsInput configOptions = new RevSalesTrxn.ConfigurationOptionsInput();
        configOptions.validateProductCatalog    = false;
        configOptions.validateAmendRenewCancel  = false;
        configOptions.executeConfigurationRules = false;
        configOptions.addDefaultConfiguration  = false;

        RevSalesTrxn.GraphRequest graph = new RevSalesTrxn.GraphRequest('svcContractGraph', listOfRecords);

        RevSalesTrxn.PlaceSalesTransactionResponse resp =
            RevSalesTrxn.PlaceSalesTransactionExecutor.execute(
                graph,
                RevSalesTrxn.PricingPreferenceEnum.SYSTEM,
                RevSalesTrxn.ConfigurationExecutionEnum.SKIP,
                configOptions,
                null
            );

        if (resp == null || !resp.isSuccess) {
            String errDetail = (resp != null && resp.errorResponse != null)
                ? String.valueOf(resp.errorResponse) : 'PST execution failed';
            throw new RLM_MFG_ServiceContractQuoteException(errDetail);
        }

        return new List<String>{ resp.salesTransactionId };
    }

    public class svcContractRequest {
        @InvocableVariable(required=true)
        public List<sObject> assets;

        @InvocableVariable(required=true)
        public String productId;

        @InvocableVariable(required=true)
        public String priceBookId;

        @InvocableVariable(required=true)
        public String priceBookEntryId;

        @InvocableVariable(required=true)
        public String productRelationshipTypeId;
    }

    // Composite key for the component PricebookEntry lookup: a product may have one entry
    // per selling model in the same pricebook, so both parts identify the correct entry.
    private static String pbeKey(Id productId, Id sellingModelId) {
        return String.valueOf(productId) + ';' + String.valueOf(sellingModelId);
    }

    // Validates a String invocable input as an Id, converting a malformed value into a
    // friendly, catchable error instead of a raw QueryException / StringException.
    private static Id toId(String value, String label) {
        try {
            return Id.valueOf(value);
        } catch (Exception e) {
            throw new RLM_MFG_ServiceContractQuoteException('Invalid ' + label + ': ' + value);
        }
    }

    public class RLM_MFG_ServiceContractQuoteException extends Exception {}
}
