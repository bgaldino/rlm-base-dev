// Customer demo hard reset — pre-catalog cleanup so reload flows do not fail on FKs.
// Runs as step 1 of prepare_customer_demo_catalog (customer_demo_purge_records).
//
// 0) Quote line / order item usage resource *policies* (QuotLineItmUsageRsrcPlcy, OrderItemUsageRsrcPlcy)
//    tied to demo ProductUsageResourcePolicy rows — otherwise delete_customer_demo_rating_data cannot
//    delete PURP (QLIURP / order policy block).
// 1) Quote line usage resource grants (QuotLineItmUseRsrcGrant) on demo meters (SF-UR-*)
//    — otherwise delete_customer_demo_rating_data cannot delete UsageResource (QLIURG block).
// 2) Order item usage resource grants on the same meters (if any).
//
// Does not delete Product2, PCM rows, or quotes themselves; those are refreshed by SFDMU/API
// in later flow steps. For a full SKU removal from the org, use a dedicated data-delete plan.

final Set<String> demoUsageProductSkus = new Set<String>{
    'SF-USG-STORAGE',
    'SF-USG-EGRESS',
    'SF-USG-COMPUTE'
};

List<ProductUsageResource> demoPurs = [
    SELECT Id FROM ProductUsageResource WHERE Product.StockKeepingUnit IN :demoUsageProductSkus
];
Set<Id> demoPurIds = new Map<Id, ProductUsageResource>(demoPurs).keySet();
if (!demoPurIds.isEmpty()) {
    List<ProductUsageResourcePolicy> demoPurps = [
        SELECT Id FROM ProductUsageResourcePolicy WHERE ProductUsageResourceId IN :demoPurIds
    ];
    Set<Id> demoPurpIds = new Map<Id, ProductUsageResourcePolicy>(demoPurps).keySet();
    if (!demoPurpIds.isEmpty()) {
        List<QuotLineItmUsageRsrcPlcy> qlPolicies = [
            SELECT Id FROM QuotLineItmUsageRsrcPlcy WHERE ProductUsageResourcePolicyId IN :demoPurpIds
        ];
        if (!qlPolicies.isEmpty()) {
            delete qlPolicies;
            System.debug(
                'customer-purge: deleted ' +
                qlPolicies.size() +
                ' QuotLineItmUsageRsrcPlcy row(s) for demo PURP.'
            );
        }
        List<OrderItemUsageRsrcPlcy> oiPolicies = [
            SELECT Id FROM OrderItemUsageRsrcPlcy WHERE ProductUsageResourcePolicyId IN :demoPurpIds
        ];
        if (!oiPolicies.isEmpty()) {
            delete oiPolicies;
            System.debug(
                'customer-purge: deleted ' +
                oiPolicies.size() +
                ' OrderItemUsageRsrcPlcy row(s) for demo PURP.'
            );
        }
    }
}

final Set<String> demoUsageResourceCodes = new Set<String>{
    'SF-UR-STORAGE',
    'SF-UR-EGRESS',
    'SF-UR-COMPUTE'
};

List<UsageResource> demoUrs = [
    SELECT Id FROM UsageResource WHERE Code IN :demoUsageResourceCodes
];
Set<Id> demoUrIds = new Map<Id, UsageResource>(demoUrs).keySet();

if (demoUrIds.isEmpty()) {
    System.debug('customer-purge: no SF-UR-* UsageResource rows — skip usage-grant cleanup.');
} else {
    List<QuotLineItmUseRsrcGrant> qlGrants = [
        SELECT Id FROM QuotLineItmUseRsrcGrant WHERE UsageResourceId IN :demoUrIds
    ];
    if (!qlGrants.isEmpty()) {
        delete qlGrants;
        System.debug(
            'customer-purge: deleted ' + qlGrants.size() + ' QuotLineItmUseRsrcGrant row(s) for demo meters.'
        );
    } else {
        System.debug('customer-purge: no QuotLineItmUseRsrcGrant rows on demo meters.');
    }

    List<OrderItemUsageRsrcGrant> oiGrants = [
        SELECT Id FROM OrderItemUsageRsrcGrant WHERE UsageResourceId IN :demoUrIds
    ];
    if (!oiGrants.isEmpty()) {
        delete oiGrants;
        System.debug(
            'customer-purge: deleted ' + oiGrants.size() + ' OrderItemUsageRsrcGrant row(s) for demo meters.'
        );
    }
}
