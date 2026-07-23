public with sharing class RLM_MFG_OrderToServiceContract {

    private static final String SERVICE_CONTRACT_TOKEN = 'Service Contract';
    private static final String MAINTENANCE_VISIT_TOKEN = 'Maintenance Visit';
    private static final Integer ENTITLEMENT_NAME_MAX = 80;

    @InvocableMethod(label='Create Service Contracts from Order' description='Creates one service contract with entitlements and a contract line item per covered-asset parent quote line on the related quote' category='Service Contract')
    public static List<Result> createServiceContracts(List<Request> requests) {
        if (requests == null || requests.isEmpty() || requests[0].orderId == null) {
            throw new RLM_MFG_OrderToServiceContractException('No order id was provided.');
        }

        Request req = requests[0];
        Id orderId = (Id) req.orderId;

        // ── Order + account + quote context ───────────────────────────────────────
        List<Order> orders = [
            SELECT Id, AccountId, QuoteId, Pricebook2Id, Quote.ContactId,
                   Account.BillingStreet, Account.BillingCity, Account.BillingState,
                   Account.BillingPostalCode, Account.BillingCountry,
                   Account.ShippingStreet, Account.ShippingCity, Account.ShippingState,
                   Account.ShippingPostalCode, Account.ShippingCountry
            FROM Order WHERE Id = :orderId LIMIT 1
        ];
        if (orders.isEmpty()) {
            throw new RLM_MFG_OrderToServiceContractException('Order not found: ' + orderId);
        }
        Order ord = orders[0];
        if (ord.QuoteId == null) {
            throw new RLM_MFG_OrderToServiceContractException('Order ' + orderId + ' has no related quote.');
        }

        // ── All covered-asset service-contract parent quote lines for the quote ───
        List<QuoteLineItem> parentQLs = [
            SELECT Id, QuoteId, Product2Id, ProductSellingModelId, StartDate, EndDate,
                   Quantity, ListPrice, NetUnitPrice,
                   RLM_MFG_Covered_Asset__c, RLM_MFG_Covered_Asset__r.Name,
                   RLM_MFG_Covered_Asset__r.Product2Id, RLM_MFG_Product_Name_formula__c
            FROM QuoteLineItem
            WHERE QuoteId = :ord.QuoteId
              AND RLM_MFG_Product_Name_formula__c LIKE :('%' + SERVICE_CONTRACT_TOKEN + '%')
        ];
        if (parentQLs.isEmpty()) {
            throw new RLM_MFG_OrderToServiceContractException(
                'No service contract quote lines found on quote ' + ord.QuoteId + '.');
        }

        Set<Id> parentIds = new Set<Id>();
        Set<Id> parentProductIds = new Set<Id>();
        for (QuoteLineItem p : parentQLs) {
            parentIds.add(p.Id);
            if (p.Product2Id != null) parentProductIds.add(p.Product2Id);
        }

        // ── Child entitlement quote lines, grouped by parent ──────────────────────
        Map<Id, List<QuoteLineItem>> childrenByParent = new Map<Id, List<QuoteLineItem>>();
        for (QuoteLineItem child : [
            SELECT Id, ParentQuoteLineItemId, Quantity, StartDate, EndDate,
                   RLM_MFG_Product_Name_formula__c
            FROM QuoteLineItem
            WHERE QuoteId = :ord.QuoteId AND ParentQuoteLineItemId IN :parentIds
        ]) {
            if (!childrenByParent.containsKey(child.ParentQuoteLineItemId)) {
                childrenByParent.put(child.ParentQuoteLineItemId, new List<QuoteLineItem>());
            }
            childrenByParent.get(child.ParentQuoteLineItemId).add(child);
        }

        // ── Pricebook entries for the parent products (for the contract line item) ─
        Map<Id, Id> pbeByProduct = new Map<Id, Id>();
        if (ord.Pricebook2Id != null && !parentProductIds.isEmpty()) {
            for (PricebookEntry pbe : [
                SELECT Id, Product2Id
                FROM PricebookEntry
                WHERE Pricebook2Id = :ord.Pricebook2Id AND Product2Id IN :parentProductIds
            ]) {
                pbeByProduct.put(pbe.Product2Id, pbe.Id);
            }
        }

        Boolean single = parentQLs.size() == 1;
        Id effAccountId = req.accountId != null ? (Id) req.accountId : ord.AccountId;
        Id effContactId = req.contactId != null ? (Id) req.contactId : ord.Quote.ContactId;

        // ── Build service contracts (one per parent line) ─────────────────────────
        List<ServiceContract> contracts = new List<ServiceContract>();
        for (QuoteLineItem p : parentQLs) {
            String assetName = (p.RLM_MFG_Covered_Asset__r != null && p.RLM_MFG_Covered_Asset__r.Name != null)
                ? p.RLM_MFG_Covered_Asset__r.Name : '';
            String autoName = (assetName + ' Service Contract').trim();

            ServiceContract sc = new ServiceContract();
            sc.Name = (single && String.isNotBlank(req.serviceContractName)) ? req.serviceContractName : autoName;
            sc.AccountId = effAccountId;
            sc.ContactId = effContactId;
            sc.Pricebook2Id = ord.Pricebook2Id;
            sc.RLM_MFG_Quote__c = ord.QuoteId;
            sc.Description = req.description;
            // Use today as the start date so Status auto-calculates to Active immediately.
            // The screen override is still honoured for single-asset cases.
            Date effStart = (single && req.startDateOverride != null) ? req.startDateOverride : Date.today();
            Date effEnd   = (single && req.endDateOverride != null)   ? req.endDateOverride
                          : (p.EndDate != null ? p.EndDate : Date.today().addYears(1));
            sc.StartDate = effStart;
            sc.EndDate   = effEnd;

            if (ord.Account != null) {
                sc.BillingStreet     = ord.Account.BillingStreet;
                sc.BillingCity       = ord.Account.BillingCity;
                sc.BillingState      = ord.Account.BillingState;
                sc.BillingPostalCode = ord.Account.BillingPostalCode;
                sc.BillingCountry    = ord.Account.BillingCountry;
                sc.ShippingStreet     = ord.Account.ShippingStreet;
                sc.ShippingCity       = ord.Account.ShippingCity;
                sc.ShippingState      = ord.Account.ShippingState;
                sc.ShippingPostalCode = ord.Account.ShippingPostalCode;
                sc.ShippingCountry    = ord.Account.ShippingCountry;
            }
            contracts.add(sc);
        }
        insert contracts;

        // Map parent QL -> its new service contract (positional, same order as parentQLs)
        Map<Id, Id> contractByParent = new Map<Id, Id>();
        for (Integer i = 0; i < parentQLs.size(); i++) {
            contractByParent.put(parentQLs[i].Id, contracts[i].Id);
        }

        // ── Build entitlements (per child line; maintenance lines expand by qty) ──
        List<Entitlement> entitlements = new List<Entitlement>();
        for (QuoteLineItem p : parentQLs) {
            Id contractId = contractByParent.get(p.Id);
            List<QuoteLineItem> kids = childrenByParent.get(p.Id);
            if (kids == null) continue;

            for (QuoteLineItem child : kids) {
                // Counter starts fresh for every child line (fixes never-reset bug)
                Integer copies = copiesForChild(child);
                for (Integer c = 0; c < copies; c++) {
                    entitlements.add(buildEntitlement(child, contractId, effAccountId));
                }
            }
        }
        if (!entitlements.isEmpty()) {
            insert entitlements;
        }

        // ── Build one contract line item per parent line ──────────────────────────
        List<ContractLineItem> contractLines = new List<ContractLineItem>();
        for (QuoteLineItem p : parentQLs) {
            // Product2Id and ListPrice are derived from PricebookEntryId by the platform
            ContractLineItem cli = new ContractLineItem();
            cli.ServiceContractId = contractByParent.get(p.Id);
            cli.StartDate = Date.today();
            cli.EndDate   = (p.EndDate != null ? p.EndDate : Date.today().addYears(1));
            cli.AssetId = p.RLM_MFG_Covered_Asset__c;
            cli.Quantity = p.Quantity;
            cli.UnitPrice = p.NetUnitPrice;
            cli.PricebookEntryId = pbeByProduct.get(p.Product2Id);
            contractLines.add(cli);
        }
        if (!contractLines.isEmpty()) {
            insert contractLines;
        }

        List<Result> results = new List<Result>();
        Result r = new Result();
        r.serviceContractIds = new List<String>();
        for (ServiceContract sc : contracts) {
            r.serviceContractIds.add(sc.Id);
        }
        r.primaryServiceContractId = contracts[0].Id;
        results.add(r);
        return results;
    }

    // Maintenance-visit lines expand into one entitlement per unit of quantity;
    // every other line yields exactly one. Counter is implicit (per call), so it
    // can never leak across child lines.
    @TestVisible
    private static Integer copiesForChild(QuoteLineItem child) {
        String name = child.RLM_MFG_Product_Name_formula__c;
        Boolean isMaintenance = name != null && name.contains(MAINTENANCE_VISIT_TOKEN);
        if (!isMaintenance) {
            return 1;
        }
        Integer qty = (child.Quantity != null) ? child.Quantity.intValue() : 1;
        return Math.max(qty, 1);
    }

    private static Entitlement buildEntitlement(QuoteLineItem child, Id contractId, Id accountId) {
        // Entitlement.Status is a platform-calculated field (derived from Start/End dates)
        Entitlement e = new Entitlement();
        e.AccountId = accountId;
        e.ServiceContractId = contractId;
        e.StartDate = Date.today();
        e.EndDate   = (child.EndDate != null ? child.EndDate : Date.today().addYears(1));
        String name = child.RLM_MFG_Product_Name_formula__c;
        if (name != null && name.length() > ENTITLEMENT_NAME_MAX) {
            name = name.substring(0, ENTITLEMENT_NAME_MAX);
        }
        e.Name = name;
        return e;
    }

    public class Request {
        @InvocableVariable(required=true label='Order Id')
        public String orderId;

        @InvocableVariable(label='Service Contract Name (single-asset override)')
        public String serviceContractName;

        @InvocableVariable(label='Description')
        public String description;

        @InvocableVariable(label='Start Date (single-asset override)')
        public Date startDateOverride;

        @InvocableVariable(label='End Date (single-asset override)')
        public Date endDateOverride;

        @InvocableVariable(label='Account Id')
        public String accountId;

        @InvocableVariable(label='Contact Id')
        public String contactId;
    }

    public class Result {
        @InvocableVariable(label='Created Service Contract Ids')
        public List<String> serviceContractIds;

        @InvocableVariable(label='Primary Service Contract Id')
        public String primaryServiceContractId;
    }

    public class RLM_MFG_OrderToServiceContractException extends Exception {}
}
