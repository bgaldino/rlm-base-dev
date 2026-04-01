public with sharing class RLM_AnalyzeWhitespaceService {

    public class Request {
        @InvocableVariable(required=true label='Account ID')
        public String accountId;

        @InvocableVariable(required=true label='Similar Account IDs')
        public String similarAccountIds;
    }

    public class Response {
        @InvocableVariable
        public Boolean success;

        @InvocableVariable
        public String message;

        @InvocableVariable
        public List<RLM_WhitespaceProduct> whitespaceProductList;

        @InvocableVariable
        public String whitespaceProductIds;
    }

    @InvocableMethod(label='Analyze Whitespace' description='Compares assets between an account and similar accounts to identify product gaps (whitespace) ranked by peer adoption rate. Recommends bundle parents instead of child components.')
    public static List<Response> analyze(List<Request> requests) {
        List<Response> responses = new List<Response>();

        for (Request req : requests) {
            Response resp = new Response();
            resp.whitespaceProductList = new List<RLM_WhitespaceProduct>();

            try {
                List<String> similarIds = new List<String>();
                if (String.isNotBlank(req.similarAccountIds)) {
                    for (String sid : req.similarAccountIds.split(',')) {
                        String trimmed = sid.trim();
                        if (String.isNotBlank(trimmed)) {
                            similarIds.add(trimmed);
                        }
                    }
                }

                if (similarIds.isEmpty()) {
                    resp.success = false;
                    resp.message = 'No similar account IDs provided. Please run Find Similar Accounts first.';
                } else {
                    // ── 1. Gather current account's products ──
                    Set<Id> currentProductIds = new Set<Id>();
                    List<String> currentProductNames = new List<String>();

                    List<Asset> currentAssets = [
                        SELECT Product2Id, Product2.Name, Product2.Family, Product2.ProductCode
                        FROM Asset
                        WHERE AccountId = :req.accountId
                        AND Product2Id != null
                        AND Status != 'Retired'
                        AND Status != 'Obsolete'
                        ORDER BY Product2.Name
                    ];

                    for (Asset a : currentAssets) {
                        if (!currentProductIds.contains(a.Product2Id)) {
                            currentProductIds.add(a.Product2Id);
                            String productInfo = a.Product2.Name;
                            if (String.isNotBlank(a.Product2.Family)) {
                                productInfo += ' (' + a.Product2.Family + ')';
                            }
                            currentProductNames.add(productInfo);
                        }
                    }

                    // ── 2. Gather peer account products ──
                    List<Asset> peerAssets = [
                        SELECT Product2Id, Product2.Name, Product2.Family, Product2.ProductCode, AccountId
                        FROM Asset
                        WHERE AccountId IN :similarIds
                        AND Product2Id != null
                        AND Status != 'Retired'
                        AND Status != 'Obsolete'
                    ];

                    Map<Id, String> productIdToName = new Map<Id, String>();
                    Map<Id, String> productIdToFamily = new Map<Id, String>();
                    Map<Id, Set<Id>> productToAccounts = new Map<Id, Set<Id>>();

                    for (Asset a : peerAssets) {
                        productIdToName.put(a.Product2Id, a.Product2.Name);
                        if (String.isNotBlank(a.Product2.Family)) {
                            productIdToFamily.put(a.Product2Id, a.Product2.Family);
                        }
                        if (!productToAccounts.containsKey(a.Product2Id)) {
                            productToAccounts.put(a.Product2Id, new Set<Id>());
                        }
                        productToAccounts.get(a.Product2Id).add(a.AccountId);
                    }

                    // ── 3. Identify raw whitespace product IDs (gaps) ──
                    Set<Id> rawWhitespaceIds = new Set<Id>();
                    for (Id prodId : productToAccounts.keySet()) {
                        if (!currentProductIds.contains(prodId)) {
                            rawWhitespaceIds.add(prodId);
                        }
                    }

                    // ── 4. Dynamically resolve bundle relationships ──
                    // Find which whitespace products are children of a bundle
                    Map<Id, Id> childToParentId = new Map<Id, Id>();
                    Set<Id> parentBundleIds = new Set<Id>();

                    if (!rawWhitespaceIds.isEmpty()) {
                        List<ProductRelatedComponent> bundleRelations = [
                            SELECT ChildProductId, ParentProductId
                            FROM ProductRelatedComponent
                            WHERE ChildProductId IN :rawWhitespaceIds
                        ];

                        for (ProductRelatedComponent prc : bundleRelations) {
                            childToParentId.put(prc.ChildProductId, prc.ParentProductId);
                            parentBundleIds.add(prc.ParentProductId);
                        }
                    }

                    // Also check if any current products are children - their bundle parent is already "owned"
                    Set<Id> ownedBundleParentIds = new Set<Id>();
                    if (!currentProductIds.isEmpty()) {
                        List<ProductRelatedComponent> ownedBundleRelations = [
                            SELECT ChildProductId, ParentProductId
                            FROM ProductRelatedComponent
                            WHERE ChildProductId IN :currentProductIds
                        ];
                        for (ProductRelatedComponent prc : ownedBundleRelations) {
                            ownedBundleParentIds.add(prc.ParentProductId);
                        }
                    }
                    // Also check if any current products ARE bundle parents directly
                    ownedBundleParentIds.addAll(currentProductIds);

                    // Load bundle parent product details
                    Map<Id, Product2> bundleProducts = new Map<Id, Product2>();
                    if (!parentBundleIds.isEmpty()) {
                        bundleProducts = new Map<Id, Product2>([
                            SELECT Id, Name, Family, ProductCode
                            FROM Product2
                            WHERE Id IN :parentBundleIds
                        ]);
                    }

                    // ── 5. Build recommendations: replace children with bundle parents, keep standalone ──
                    // Track which recommendable product IDs we've already added (dedup)
                    Set<Id> addedRecommendationIds = new Set<Id>();
                    // Use a map to aggregate adoption data per recommended product
                    Map<Id, WhitespaceItem> recommendationMap = new Map<Id, WhitespaceItem>();

                    for (Id prodId : rawWhitespaceIds) {
                        Id recommendId;
                        String recommendName;
                        String recommendFamily;

                        if (childToParentId.containsKey(prodId)) {
                            // This product is a bundle child → recommend the parent bundle instead
                            Id parentId = childToParentId.get(prodId);

                            // Skip if the bundle parent is already owned
                            if (ownedBundleParentIds.contains(parentId)) {
                                continue;
                            }

                            Product2 parentProduct = bundleProducts.get(parentId);
                            if (parentProduct == null) {
                                continue;
                            }

                            recommendId = parentId;
                            recommendName = parentProduct.Name;
                            recommendFamily = parentProduct.Family;
                        } else {
                            // Standalone product (not a child of any bundle)
                            recommendId = prodId;
                            recommendName = productIdToName.get(prodId);
                            recommendFamily = productIdToFamily.get(prodId);
                        }

                        // Aggregate: merge adoption accounts from all children that map to the same recommendation
                        if (recommendationMap.containsKey(recommendId)) {
                            // Add this child's adopting accounts to the existing recommendation
                            WhitespaceItem existing = recommendationMap.get(recommendId);
                            Set<Id> childAccounts = productToAccounts.get(prodId);
                            if (childAccounts != null) {
                                existing.adoptingAccounts.addAll(childAccounts);
                                existing.adoptionCount = existing.adoptingAccounts.size();
                                existing.adoptionRate = (Decimal) existing.adoptionCount / similarIds.size() * 100;
                            }
                        } else {
                            WhitespaceItem item = new WhitespaceItem();
                            item.productId = recommendId;
                            item.productName = recommendName;
                            item.productFamily = recommendFamily;
                            item.adoptingAccounts = new Set<Id>();
                            Set<Id> childAccounts = productToAccounts.get(prodId);
                            if (childAccounts != null) {
                                item.adoptingAccounts.addAll(childAccounts);
                            }
                            item.adoptionCount = item.adoptingAccounts.size();
                            item.adoptionRate = (Decimal) item.adoptionCount / similarIds.size() * 100;
                            recommendationMap.put(recommendId, item);
                        }
                    }

                    // ── 6. Sort and format output ──
                    List<WhitespaceItem> whitespaceItems = new List<WhitespaceItem>(recommendationMap.values());
                    whitespaceItems.sort();

                    List<String> productDescriptions = new List<String>();
                    List<String> productIdsList = new List<String>();

                    for (Integer i = 0; i < whitespaceItems.size(); i++) {
                        WhitespaceItem wi = whitespaceItems[i];

                        // Add to structured list for rich UI rendering
                        resp.whitespaceProductList.add(new RLM_WhitespaceProduct(
                            wi.productId,
                            wi.productName,
                            wi.productFamily,
                            wi.adoptionCount,
                            similarIds.size()
                        ));

                        String prodDesc = wi.productName;
                        if (String.isNotBlank(wi.productFamily)) {
                            prodDesc = prodDesc + ' [' + wi.productFamily + ']';
                        }
                        Integer rate = Integer.valueOf(wi.adoptionRate.setScale(0));
                        prodDesc = prodDesc + ' - ' + wi.adoptionCount + '/' + similarIds.size() + ' peers (' + rate + '% adoption)';
                        productDescriptions.add(prodDesc);
                        productIdsList.add(String.valueOf(wi.productId));
                    }

                    resp.whitespaceProductIds = String.join(productIdsList, ',');
                    resp.success = true;

                    if (whitespaceItems.isEmpty()) {
                        resp.message = 'No product gaps found. This account has all products owned by its ' + similarIds.size() + ' peer accounts.';
                    } else {
                        String msg = 'Found ' + whitespaceItems.size() + ' product opportunit';
                        msg += (whitespaceItems.size() == 1 ? 'y' : 'ies');
                        msg += ' based on ' + similarIds.size() + ' similar account';
                        msg += (similarIds.size() == 1 ? '' : 's') + '.';

                        if (!currentProductNames.isEmpty()) {
                            msg += ' This account currently has ' + currentProductIds.size() + ' product';
                            msg += (currentProductIds.size() == 1 ? '' : 's') + '.';
                        }

                        resp.message = msg;
                    }
                }
            } catch (Exception e) {
                resp.success = false;
                resp.message = 'Error analyzing whitespace: ' + e.getMessage();
            }

            responses.add(resp);
        }

        return responses;
    }

    private class WhitespaceItem implements Comparable {
        public Id productId;
        public String productName;
        public String productFamily;
        public Integer adoptionCount;
        public Decimal adoptionRate;
        public Set<Id> adoptingAccounts;

        public Integer compareTo(Object other) {
            WhitespaceItem otherItem = (WhitespaceItem) other;
            if (this.adoptionRate > otherItem.adoptionRate) {
                return -1;
            }
            if (this.adoptionRate < otherItem.adoptionRate) {
                return 1;
            }
            return this.productName.compareTo(otherItem.productName);
        }
    }
}
