public with sharing class RLM_MFG_SalesAgreementRLMOrder {

    @InvocableMethod(label='Create Order from Sales Agreement' description='Creates an RLM order from a sales agreement using Place Sales Transaction' category='Order')
    public static List<String> createOrder(List<saProductListEntries> saProducts) {
        if (saProducts == null || saProducts.isEmpty()
                || saProducts[0].salesagreementProductSchedules == null
                || saProducts[0].salesagreementProductSchedules.isEmpty()) {
            return new List<String>();
        }

        List<SalesAgreementProductSchedule> schedules =
            (List<SalesAgreementProductSchedule>) saProducts[0].salesagreementProductSchedules;

        Id accountId    = (Id) saProducts[0].customerAcctId;
        String pbId     = saProducts[0].priceBookId;
        String saId     = saProducts[0].salesAgreementId;
        String ctrId    = saProducts[0].contractId;
        String orderDateStr = String.valueOf(saProducts[0].orderDate);

        // Resolve account address for billing and shipping population
        List<Account> accounts = [
            SELECT Id, Name,
                   BillingStreet, BillingCity, BillingState, BillingPostalCode, BillingCountry,
                   ShippingStreet, ShippingCity, ShippingState, ShippingPostalCode, ShippingCountry
            FROM Account WHERE Id = :accountId LIMIT 1
        ];
        Account acct = accounts.isEmpty() ? null : accounts[0];

        // Primary contact for the account — used for BillToContactId
        List<Contact> contacts = [SELECT Id FROM Contact WHERE AccountId = :accountId LIMIT 1];
        Id contactId = contacts.isEmpty() ? null : contacts[0].Id;

        // ── Order header ──────────────────────────────────────────────────────────
        RevSalesTrxn.RecordResource orderRecord =
            new RevSalesTrxn.RecordResource(Order.getSobjectType(), 'POST');
        Map<String, Object> orderFields = new Map<String, Object>();
        orderFields.put('AccountId',       accountId);
        orderFields.put('Pricebook2Id',    pbId);
        orderFields.put('EffectiveDate',   orderDateStr);
        orderFields.put('SalesAgreementId', saId);
        orderFields.put('Status',          'Draft');

        if (ctrId != null) {
            orderFields.put('ContractId', ctrId);
        }
        if (contactId != null) {
            orderFields.put('BillToContactId', contactId);
        }
        if (acct != null) {
            if (acct.BillingStreet     != null) orderFields.put('BillingStreet',     acct.BillingStreet);
            if (acct.BillingCity       != null) orderFields.put('BillingCity',       acct.BillingCity);
            if (acct.BillingState      != null) orderFields.put('BillingState',      acct.BillingState);
            if (acct.BillingPostalCode != null) orderFields.put('BillingPostalCode', acct.BillingPostalCode);
            if (acct.BillingCountry    != null) orderFields.put('BillingCountry',    acct.BillingCountry);
            if (acct.ShippingStreet    != null) orderFields.put('ShippingStreet',    acct.ShippingStreet);
            if (acct.ShippingCity      != null) orderFields.put('ShippingCity',      acct.ShippingCity);
            if (acct.ShippingState     != null) orderFields.put('ShippingState',     acct.ShippingState);
            if (acct.ShippingPostalCode!= null) orderFields.put('ShippingPostalCode',acct.ShippingPostalCode);
            if (acct.ShippingCountry   != null) orderFields.put('ShippingCountry',   acct.ShippingCountry);
        }

        orderRecord.fieldValues = orderFields;
        List<RevSalesTrxn.RecordWithReferenceRequest> listOfRecords =
            new List<RevSalesTrxn.RecordWithReferenceRequest>{
                new RevSalesTrxn.RecordWithReferenceRequest('refOrder', orderRecord)
            };

        // ── AppUsageAssignment — marks this order as Revenue Cloud managed ────────
        RevSalesTrxn.RecordResource auaRecord =
            new RevSalesTrxn.RecordResource(AppUsageAssignment.getSobjectType(), 'POST');
        auaRecord.fieldValues = new Map<String, Object>{
            'AppUsageType' => 'RevenueLifecycleManagement',
            'RecordId'     => '@{refOrder.id}'
        };
        listOfRecords.add(new RevSalesTrxn.RecordWithReferenceRequest('refAppUsage', auaRecord));

        // ── One OrderItem per selected product schedule ───────────────────────────
        Integer counter = 0;
        for (SalesAgreementProductSchedule schedule : schedules) {
            counter++;
            RevSalesTrxn.RecordResource oiRecord =
                new RevSalesTrxn.RecordResource(OrderItem.getSobjectType(), 'POST');
            Map<String, Object> oiFields = new Map<String, Object>();
            oiFields.put('OrderId',          '@{refOrder.id}');
            oiFields.put('Product2Id',       schedule.RLM_MFG_Product2Id__c);
            oiFields.put('PricebookEntryId', schedule.RLM_MFG_PricebookEntryId__c);
            oiFields.put('Quantity',         schedule.PlannedQuantity);
            oiFields.put('UnitPrice',        schedule.SalesPrice);
            oiRecord.fieldValues = oiFields;
            listOfRecords.add(new RevSalesTrxn.RecordWithReferenceRequest(
                'refOrderItem_' + counter, oiRecord));
        }

        // ── Execute Place Sales Transaction ───────────────────────────────────────
        RevSalesTrxn.ConfigurationOptionsInput configOptions =
            new RevSalesTrxn.ConfigurationOptionsInput();
        configOptions.validateProductCatalog    = false;
        configOptions.validateAmendRenewCancel  = false;
        configOptions.executeConfigurationRules = false;
        configOptions.addDefaultConfiguration  = false;

        RevSalesTrxn.GraphRequest graph =
            new RevSalesTrxn.GraphRequest('salesAgreementOrderGraph', listOfRecords);

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
                ? String.valueOf(resp.errorResponse) : 'PST order execution failed';
            throw new RLM_MFG_SalesAgreementOrderException(errDetail);
        }

        return new List<String>{ resp.salesTransactionId };
    }

    public class saProductListEntries {
        @InvocableVariable(required=true)
        public List<sObject> salesagreementProductSchedules;

        @InvocableVariable(required=true)
        public String priceBookId;

        @InvocableVariable(required=true)
        public String salesAgreementId;

        @InvocableVariable(required=true)
        public String customerAcctId;

        @InvocableVariable(required=true)
        public Date orderDate;

        @InvocableVariable(required=false)
        public String contractId;
    }

    public class RLM_MFG_SalesAgreementOrderException extends Exception {}
}
