/**
 * @AuraEnabled facade for the rlmAssetConsole LWC.
 *
 * Read side: returns an account's lifecycle-managed assets grouped by the
 * contract that owns them (via AssetContractRelationship), plus a lightweight
 * per-asset eligibility gate. Write side: takes a flat selection of asset ids +
 * an action, groups them by contract, and delegates to RLM_AssetOrderingService
 * which drives the NATIVE lifecycle actions and consolidates the result onto a
 * single output record.
 *
 * All SOQL runs WITH USER_MODE; all id inputs are validated with Id.valueOf.
 * The eligibility gate here is intentionally self-contained (mirrors the intent
 * of post_utils' RLM_ARC_AssetValidator) so the bundle deploys standalone
 * without a hard dependency on post_utils.
 */
public with sharing class RLM_AssetConsoleController {

    private static final String NO_CONTRACT_KEY = 'none';

    // ------------------------------------------------------------------
    // View models
    // ------------------------------------------------------------------
    public class ConsoleData {
        @AuraEnabled public Id accountId;
        @AuraEnabled public String accountName;
        @AuraEnabled public Integer totalAssetCount;
        // Number of accounts the assets were read from (1 unless the hierarchy
        // is included - then the whole account tree the primary account belongs to).
        @AuraEnabled public Integer accountCount;
        @AuraEnabled public List<ContractGroupView> groups;

        public ConsoleData() {
            groups = new List<ContractGroupView>();
            totalAssetCount = 0;
            accountCount = 1;
        }
    }

    public class ContractGroupView {
        @AuraEnabled public Id contractId;          // null for the "no contract" group
        @AuraEnabled public String contractNumber;  // display label
        @AuraEnabled public String contractStatus;
        @AuraEnabled public Integer assetCount;
        @AuraEnabled public List<AssetRow> assets;

        public ContractGroupView() {
            assets = new List<AssetRow>();
            assetCount = 0;
        }
    }

    public class AssetRow {
        @AuraEnabled public Id id;
        @AuraEnabled public String name;
        @AuraEnabled public Id accountId;      // owning account (may differ from the primary in a hierarchy)
        @AuraEnabled public String accountName;
        @AuraEnabled public String serialNumber;
        @AuraEnabled public String productName;
        @AuraEnabled public String productCode;
        @AuraEnabled public Decimal quantity;
        @AuraEnabled public Decimal currentQuantity;
        @AuraEnabled public Decimal currentMrr;
        @AuraEnabled public Decimal currentAmount;
        @AuraEnabled public String status;
        @AuraEnabled public String statusReason;
        @AuraEnabled public String lifecycleEndDate; // ISO date string or null
        @AuraEnabled public Id rootAssetId;
        @AuraEnabled public Id parentId;
        @AuraEnabled public Boolean hasLifecycleManagement;
        @AuraEnabled public String assetStatus; // RLM_Asset_Status__c (Active/Suspended/BillingHeld)
        @AuraEnabled public Boolean billingHeld; // true when assetStatus == BillingHeld
        @AuraEnabled public String billingStartDate; // RLM_Billing_Start_Date__c (ISO) or null
        @AuraEnabled public Integer serialUnitCount; // native SerializedProduct records for this asset
        @AuraEnabled public String serialUnitSummary; // e.g. "SN1 (Sent), SN2 (Sent)"
        @AuraEnabled public Boolean canAmend;
        @AuraEnabled public Boolean canRenew;
        @AuraEnabled public Boolean canCancel;
        @AuraEnabled public String ineligibleReason;
    }

    // ------------------------------------------------------------------
    // Read
    // ------------------------------------------------------------------
    @AuraEnabled(cacheable=true)
    public static ConsoleData getConsole(Id recordId, String objectApiName, Boolean includeHierarchy) {
        ConsoleData data = new ConsoleData();
        if (recordId == null) return data;

        Id primaryAccountId = resolveAccountId(Id.valueOf(recordId), objectApiName);
        if (primaryAccountId == null) return data;
        data.accountId = primaryAccountId;

        // Read from just the primary account, or - when the hierarchy is
        // requested - from every account in the tree the primary belongs to.
        Set<Id> accountIds = (includeHierarchy == true)
            ? collectHierarchyAccountIds(primaryAccountId)
            : new Set<Id>{ primaryAccountId };
        data.accountCount = accountIds.size();

        Map<Id, Account> acctById = new Map<Id, Account>([
            SELECT Id, Name FROM Account WHERE Id IN :accountIds WITH USER_MODE
        ]);
        if (acctById.containsKey(primaryAccountId)) {
            data.accountName = acctById.get(primaryAccountId).Name;
        }

        List<Asset> assets = [
            SELECT Id, Name, AccountId, Account.Name, SerialNumber, Product2.Name, Product2.ProductCode,
                   Quantity, CurrentQuantity, CurrentMrr, CurrentAmount, Status, StatusReason,
                   LifecycleEndDate, RootAssetId, ParentId, HasLifecycleManagement,
                   RLM_Asset_Status__c, RLM_Billing_Start_Date__c
            FROM Asset
            WHERE AccountId IN :accountIds
            WITH USER_MODE
            ORDER BY Account.Name, Name
        ];
        data.totalAssetCount = assets.size();
        if (assets.isEmpty()) return data;

        Set<Id> assetIds = (new Map<Id, Asset>(assets)).keySet();

        // Native serialized-product units mapped to each asset. Linked via the
        // custom RLM_Asset__c lookup, not the standard AssetId (which cannot be set
        // in this edition - see RLM_ShipmentFulfillmentService).
        Map<Id, List<SerializedProduct>> serialsByAsset = new Map<Id, List<SerializedProduct>>();
        for (SerializedProduct sp : [
            SELECT Id, RLM_Asset__c, SerialNumber, Status
            FROM SerializedProduct
            WHERE RLM_Asset__c IN :assetIds
            WITH USER_MODE
            ORDER BY SerialNumber
        ]) {
            if (!serialsByAsset.containsKey(sp.RLM_Asset__c)) {
                serialsByAsset.put(sp.RLM_Asset__c, new List<SerializedProduct>());
            }
            serialsByAsset.get(sp.RLM_Asset__c).add(sp);
        }

        // asset -> owning (active) contract
        Map<Id, AssetContractRelationship> assetToRel = new Map<Id, AssetContractRelationship>();
        for (AssetContractRelationship rel : [
            SELECT AssetId, ContractId, Contract.ContractNumber, Contract.Status, StartDate, EndDate
            FROM AssetContractRelationship
            WHERE AssetId IN :assetIds
            WITH USER_MODE
            ORDER BY StartDate DESC NULLS LAST
        ]) {
            if (rel.ContractId == null) continue;
            Boolean active = (rel.EndDate == null || rel.EndDate >= System.now());
            // Keep the first active relationship seen (most recent StartDate).
            if (active && !assetToRel.containsKey(rel.AssetId)) {
                assetToRel.put(rel.AssetId, rel);
            }
        }

        // Build groups keyed by contract id (or NO_CONTRACT_KEY).
        Map<String, ContractGroupView> groupByKey = new Map<String, ContractGroupView>();
        for (Asset a : assets) {
            AssetContractRelationship rel = assetToRel.get(a.Id);
            String key = (rel == null) ? NO_CONTRACT_KEY : String.valueOf(rel.ContractId);
            ContractGroupView grp = groupByKey.get(key);
            if (grp == null) {
                grp = new ContractGroupView();
                if (rel != null) {
                    grp.contractId = rel.ContractId;
                    grp.contractNumber = (rel.Contract != null) ? rel.Contract.ContractNumber : null;
                    grp.contractStatus = (rel.Contract != null) ? rel.Contract.Status : null;
                } else {
                    grp.contractNumber = 'No contract';
                }
                groupByKey.put(key, grp);
            }
            grp.assets.add(toRow(a, serialsByAsset.get(a.Id)));
            grp.assetCount = grp.assets.size();
        }
        data.groups = groupByKey.values();
        return data;
    }

    private static AssetRow toRow(Asset a, List<SerializedProduct> serials) {
        AssetRow r = new AssetRow();
        r.id = a.Id;
        r.name = a.Name;
        r.accountId = a.AccountId;
        r.accountName = (a.Account != null) ? a.Account.Name : null;
        r.serialNumber = a.SerialNumber;
        r.productName = (a.Product2 != null) ? a.Product2.Name : null;
        r.productCode = (a.Product2 != null) ? a.Product2.ProductCode : null;
        r.quantity = a.Quantity;
        r.currentQuantity = a.CurrentQuantity;
        r.currentMrr = a.CurrentMrr;
        r.currentAmount = a.CurrentAmount;
        r.status = a.Status;
        r.statusReason = a.StatusReason;
        r.rootAssetId = a.RootAssetId;
        r.parentId = a.ParentId;
        r.hasLifecycleManagement = a.HasLifecycleManagement;
        r.assetStatus = a.RLM_Asset_Status__c;
        r.billingHeld = (a.RLM_Asset_Status__c == 'BillingHeld');
        r.billingStartDate = (a.RLM_Billing_Start_Date__c == null)
            ? null
            : a.RLM_Billing_Start_Date__c.year() + '-'
              + leftPad(a.RLM_Billing_Start_Date__c.month()) + '-'
              + leftPad(a.RLM_Billing_Start_Date__c.day());
        Integer spCount = (serials == null) ? 0 : serials.size();
        r.serialUnitCount = spCount;
        if (spCount > 0) {
            List<String> parts = new List<String>();
            for (SerializedProduct sp : serials) {
                parts.add(sp.SerialNumber + ' (' + sp.Status + ')');
            }
            r.serialUnitSummary = String.join(parts, ', ');
        }
        r.lifecycleEndDate = (a.LifecycleEndDate == null)
            ? null
            : a.LifecycleEndDate.date().year() + '-'
              + leftPad(a.LifecycleEndDate.date().month()) + '-'
              + leftPad(a.LifecycleEndDate.date().day());
        applyEligibility(a, r);
        return r;
    }

    /** Lightweight eligibility gate (self-contained; mirrors RLM_ARC_AssetValidator intent). */
    private static void applyEligibility(Asset a, AssetRow r) {
        r.canAmend = true; r.canRenew = true; r.canCancel = true;
        if (a.HasLifecycleManagement == false) {
            r.canAmend = false; r.canRenew = false; r.canCancel = false;
            r.ineligibleReason = 'Not lifecycle-managed';
            return;
        }
        Boolean expired = (a.LifecycleEndDate != null && a.LifecycleEndDate < System.now());
        if (expired) {
            // An expired asset can be renewed but not amended/cancelled.
            r.canAmend = false; r.canCancel = false;
            r.ineligibleReason = 'Expired - renew only';
        }
    }

    private static String leftPad(Integer n) {
        return (n < 10) ? '0' + String.valueOf(n) : String.valueOf(n);
    }

    private static Id resolveAccountId(Id recordId, String objectApiName) {
        String sobj = (recordId.getSObjectType() != null)
            ? String.valueOf(recordId.getSObjectType())
            : objectApiName;
        if (sobj == 'Account') {
            return recordId;
        }
        if (sobj == 'Contract') {
            List<Contract> cs = [
                SELECT AccountId FROM Contract WHERE Id = :recordId WITH USER_MODE LIMIT 1
            ];
            return cs.isEmpty() ? null : cs[0].AccountId;
        }
        if (sobj == 'Asset') {
            List<Asset> as1 = [
                SELECT AccountId FROM Asset WHERE Id = :recordId WITH USER_MODE LIMIT 1
            ];
            return as1.isEmpty() ? null : as1[0].AccountId;
        }
        return null;
    }

    // Depth caps keep the traversal governor-safe (one SOQL per level). Real
    // Salesforce account hierarchies are far shallower than this.
    private static final Integer MAX_HIERARCHY_LEVELS = 20;

    /**
     * Collect every account in the hierarchy the given account belongs to:
     * walk up ParentId to the root, then breadth-first down to gather all
     * descendants (the full tree, not just the start account's own branch).
     */
    private static Set<Id> collectHierarchyAccountIds(Id startAccountId) {
        Set<Id> all = new Set<Id>{ startAccountId };

        // Up: find the root of the tree.
        Id root = startAccountId;
        Id cursor = startAccountId;
        Integer up = 0;
        while (cursor != null && up < MAX_HIERARCHY_LEVELS) {
            up++;
            List<Account> parents = [
                SELECT ParentId FROM Account WHERE Id = :cursor WITH USER_MODE LIMIT 1
            ];
            if (parents.isEmpty() || parents[0].ParentId == null) {
                root = cursor;
                break;
            }
            cursor = parents[0].ParentId;
            root = cursor;
            all.add(cursor);
        }

        // Down: breadth-first from the root, level by level.
        all.add(root);
        Set<Id> frontier = new Set<Id>{ root };
        Integer levels = 0;
        while (!frontier.isEmpty() && levels < MAX_HIERARCHY_LEVELS) {
            levels++;
            List<Account> children = [
                SELECT Id FROM Account WHERE ParentId IN :frontier WITH USER_MODE
            ];
            Set<Id> next = new Set<Id>();
            for (Account c : children) {
                if (all.add(c.Id)) next.add(c.Id); // Set.add returns true only for new ids
            }
            frontier = next;
        }
        return all;
    }

    // ------------------------------------------------------------------
    // Write
    // ------------------------------------------------------------------
    /**
     * Launch a consolidated lifecycle action across the selected assets. The
     * selection may span multiple contracts; this method regroups by the
     * owning contract and delegates to RLM_AssetOrderingService, which chains
     * the native action so all groups land on a single output record.
     *
     * @param assetIds      selected asset ids (across any contracts)
     * @param actionType    Amend | Upgrade | Downgrade | Renew | Cancel
     * @param outputType    e.g. Quote (blank defaults to Quote)
     * @param effectiveDate ISO 'yyyy-MM-dd' (blank defaults to today)
     * @param quantityChange amend delta (nullable)
     * @param renewalEndDate ISO 'yyyy-MM-dd' for renew (nullable)
     * @param skipPricing   skip pricing on the generated output
     */
    @AuraEnabled
    public static RLM_AssetOrderingService.ConsolidationResult launchConsolidatedAction(
        List<Id> assetIds,
        String actionType,
        String outputType,
        String effectiveDate,
        Decimal quantityChange,
        String renewalEndDate,
        Boolean skipPricing
    ) {
        if (assetIds == null || assetIds.isEmpty()) {
            throw new AuraHandledException('Select at least one asset.');
        }
        // Validate every id.
        Set<Id> validated = new Set<Id>();
        for (Id raw : assetIds) {
            validated.add(Id.valueOf(raw));
        }

        // A consolidated action produces ONE output record, and a Quote/Order
        // belongs to a single account. When the hierarchy view lets a user
        // select assets from several related accounts, stop with a clear message
        // rather than letting the native action fail cryptically. (Assets from
        // different contracts on the SAME account still consolidate as before.)
        Set<Id> distinctAccounts = new Set<Id>();
        for (Asset a : [
            SELECT AccountId FROM Asset WHERE Id IN :validated WITH USER_MODE
        ]) {
            if (a.AccountId != null) distinctAccounts.add(a.AccountId);
        }
        if (distinctAccounts.size() > 1) {
            throw new AuraHandledException(
                'The selected assets belong to ' + distinctAccounts.size() +
                ' different accounts. A consolidated action produces one output for one ' +
                'account - select assets from a single account at a time.'
            );
        }

        // Regroup selected assets by owning (active) contract.
        Map<Id, Id> assetToContract = new Map<Id, Id>();
        for (AssetContractRelationship rel : [
            SELECT AssetId, ContractId, EndDate
            FROM AssetContractRelationship
            WHERE AssetId IN :validated
            WITH USER_MODE
            ORDER BY StartDate DESC NULLS LAST
        ]) {
            if (rel.ContractId == null) continue;
            Boolean active = (rel.EndDate == null || rel.EndDate >= System.now());
            if (active && !assetToContract.containsKey(rel.AssetId)) {
                assetToContract.put(rel.AssetId, rel.ContractId);
            }
        }

        Map<String, RLM_AssetOrderingService.ContractAssetGroup> groups =
            new Map<String, RLM_AssetOrderingService.ContractAssetGroup>();
        for (Id aId : validated) {
            Id cId = assetToContract.get(aId);
            String key = (cId == null) ? NO_CONTRACT_KEY : String.valueOf(cId);
            RLM_AssetOrderingService.ContractAssetGroup grp = groups.get(key);
            if (grp == null) {
                grp = new RLM_AssetOrderingService.ContractAssetGroup();
                grp.contractId = cId;
                grp.assetIds = new List<Id>();
                groups.put(key, grp);
            }
            grp.assetIds.add(aId);
        }

        RLM_AssetOrderingService.ConsolidationRequest req =
            new RLM_AssetOrderingService.ConsolidationRequest();
        req.actionType = actionType;
        req.outputType = String.isBlank(outputType) ? 'Quote' : outputType;
        req.effectiveDate = String.isBlank(effectiveDate) ? Date.today() : Date.valueOf(effectiveDate);
        req.quantityChange = quantityChange;
        req.renewalEndDate = String.isBlank(renewalEndDate) ? null : Date.valueOf(renewalEndDate);
        req.skipPricing = (skipPricing == true);
        req.groups = groups.values();

        return RLM_AssetOrderingService.runConsolidation(req);
    }

    // ------------------------------------------------------------------
    // Suspend / Resume (Phase 3)
    // ------------------------------------------------------------------
    @AuraEnabled
    public static RLM_AssetSuspensionService.SuspensionResult suspendAssets(
        List<Id> assetIds,
        String suspensionDate,
        String resumptionDate
    ) {
        if (assetIds == null || assetIds.isEmpty()) {
            throw new AuraHandledException('Select at least one asset.');
        }
        Date susp = String.isBlank(suspensionDate) ? Date.today() : Date.valueOf(suspensionDate);
        Date res = String.isBlank(resumptionDate) ? null : Date.valueOf(resumptionDate);
        return RLM_AssetSuspensionService.suspend(assetIds, susp, res);
    }

    @AuraEnabled
    public static RLM_AssetSuspensionService.SuspensionResult resumeAssets(List<Id> assetIds) {
        if (assetIds == null || assetIds.isEmpty()) {
            throw new AuraHandledException('Select at least one asset.');
        }
        return RLM_AssetSuspensionService.resume(assetIds);
    }
}
