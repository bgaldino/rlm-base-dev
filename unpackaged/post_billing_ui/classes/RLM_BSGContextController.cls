public with sharing class RLM_BSGContextController {

    public class BSGContext {
        @AuraEnabled public String viewType; // 'milestone', 'bundle', 'usage', 'standard'
        @AuraEnabled public String bsgNumber;
        @AuraEnabled public String productName;
        @AuraEnabled public String billingType;
        @AuraEnabled public String billingMethod;
        @AuraEnabled public String billingTermUnit;
        @AuraEnabled public Integer billingTerm;

        @AuraEnabled public MilestonePlanData milestonePlan;
        @AuraEnabled public BundleData bundle;
        @AuraEnabled public UsageData usage;

        @AuraEnabled public Decimal bsBilledAmount;
        @AuraEnabled public Decimal bsPendingAmount;

        // Billing Arrangement (applicable to any view type)
        @AuraEnabled public ArrangementData arrangement;
    }

    // ─── Milestone wrappers ─────────────────────────────────────────────────

    public class MilestonePlanData {
        @AuraEnabled public String planId;
        @AuraEnabled public String planName;
        @AuraEnabled public String planStatus;
        @AuraEnabled public String description;
        @AuraEnabled public Decimal referenceAmount;
        @AuraEnabled public Decimal billedAmount;
        @AuraEnabled public List<MilestoneItemData> items;
    }

    public class MilestoneItemData {
        @AuraEnabled public String id;
        @AuraEnabled public String name;
        @AuraEnabled public String itemType;
        @AuraEnabled public Decimal percentage;
        @AuraEnabled public Decimal flatAmount;
        @AuraEnabled public String milestoneType;
        @AuraEnabled public Decimal milestoneAmount;
        @AuraEnabled public String commencementDate;
        @AuraEnabled public Boolean isAccomplished;
        @AuraEnabled public String status;
        @AuraEnabled public String accomplishmentDate;
    }

    // ─── Bundle wrappers ────────────────────────────────────────────────────

    public class BundleData {
        @AuraEnabled public Boolean isMainBundle;
        @AuraEnabled public String mainBsgId;
        @AuraEnabled public String mainBsgProduct;
        @AuraEnabled public String mainChargeType;
        @AuraEnabled public String mainBillingFrequency;
        @AuraEnabled public List<BundleComponentData> components;
    }

    public class BundleComponentData {
        @AuraEnabled public String bsgId;
        @AuraEnabled public String productName;
        @AuraEnabled public String chargeType;
        @AuraEnabled public String billingFrequency;
        @AuraEnabled public Boolean isCurrent;
        @AuraEnabled public Integer depth;
        @AuraEnabled public Boolean isSubBundle;
    }

    // ─── Usage wrappers ─────────────────────────────────────────────────────

    public class UsageData {
        @AuraEnabled public String anchorBsgId;
        @AuraEnabled public String anchorBsgNumber;
        @AuraEnabled public String anchorProductName;
        @AuraEnabled public String currentResourceName;
        @AuraEnabled public String currentBsgNumber;
        @AuraEnabled public String currentProductName;
        @AuraEnabled public String billingType;
        @AuraEnabled public List<UsageSiblingData> siblings;
    }

    public class UsageSiblingData {
        @AuraEnabled public String bsgId;
        @AuraEnabled public String bsgNumber;
        @AuraEnabled public String resourceName;
        @AuraEnabled public Decimal billedAmount;
        @AuraEnabled public Boolean isCurrent;
    }

    // ─── Billing Arrangement wrappers ───────────────────────────────────────

    public class ArrangementData {
        @AuraEnabled public String arrangementId;
        @AuraEnabled public String arrangementName;
        @AuraEnabled public String status;
        @AuraEnabled public List<ArrangementLineData> lines;
    }

    public class ArrangementLineData {
        @AuraEnabled public String lineId;
        @AuraEnabled public String lineName;
        @AuraEnabled public String accountName;
        @AuraEnabled public String billingAccountName;
        @AuraEnabled public Decimal billingPercentage;
        @AuraEnabled public Boolean shouldBillRemainder;
    }

    // ─── Main entry point ───────────────────────────────────────────────────

    @AuraEnabled(cacheable=true)
    public static BSGContext getBSGContext(String recordId) {
        BSGContext ctx = new BSGContext();

        BillingScheduleGroup bsg = [
            SELECT Id, BillingScheduleGroupNumber, ProductName, Product2Id,
                   BillingType, BillingMethod, BillingTermUnit, BillingTerm,
                   AnchorProdtBillingSchdGrpId, BindingInstanceId,
                   BillingArrangementId, TotalBilledAmount, EndDate
            FROM BillingScheduleGroup
            WHERE Id = :recordId
            LIMIT 1
        ];

        ctx.bsgNumber = bsg.BillingScheduleGroupNumber;
        ctx.productName = bsg.ProductName;
        ctx.billingType = bsg.BillingType;
        ctx.billingMethod = bsg.BillingMethod;
        ctx.billingTermUnit = bsg.BillingTermUnit;
        ctx.billingTerm = bsg.BillingTerm;

        // Fetch BS-level billed/pending for % calculation
        List<BillingSchedule> bsForAmounts = [
            SELECT BilledAmount, PendingAmount
            FROM BillingSchedule
            WHERE BillingScheduleGroupId = :recordId
            LIMIT 1
        ];
        if (!bsForAmounts.isEmpty()) {
            ctx.bsBilledAmount = bsForAmounts[0].BilledAmount;
            ctx.bsPendingAmount = bsForAmounts[0].PendingAmount;
        }

        // 1. Check for Milestone. BillingSchedule.BillingMilestonePlanId and the
        // BillingMilestonePlan(Item) objects are license-gated billing extensions that are
        // not surfaced to the Apex compiler for static SOQL (compile visibility can also lag
        // behind entitlement propagation in a fresh org), so query them dynamically.
        Id milestonePlanId = findMilestonePlanId(recordId);
        if (milestonePlanId != null) {
            ctx.viewType = 'milestone';
            ctx.milestonePlan = getMilestonePlan(milestonePlanId, bsg.TotalBilledAmount);
        }

        // 2. Check for Bundle relationships
        if (ctx.viewType == null) {
            List<BsgRelationship> asMain = [
                SELECT Id, AssociatedBsgId, AssociatedBsgRole, AssociatedBsgPricing
                FROM BsgRelationship WHERE MainBsgId = :recordId LIMIT 50
            ];
            List<BsgRelationship> asComponent = [
                SELECT Id, MainBsgId, MainBsgRole
                FROM BsgRelationship WHERE AssociatedBsgId = :recordId LIMIT 1
            ];

            if (!asMain.isEmpty() || !asComponent.isEmpty()) {
                ctx.viewType = 'bundle';
                ctx.bundle = getBundleData(recordId, bsg, asMain, asComponent);
            }
        }

        // 3. Check for Usage
        if (ctx.viewType == null && bsg.BillingMethod == 'Usage') {
            ctx.viewType = 'usage';
            ctx.usage = getUsageData(recordId, bsg);
        }

        // 4. Fallback
        if (ctx.viewType == null) {
            ctx.viewType = 'standard';
        }

        // 5. Check for Billing Arrangement (applies to any view type)
        if (bsg.BillingArrangementId != null) {
            ctx.arrangement = getArrangementData(bsg.BillingArrangementId);
        }

        return ctx;
    }

    // ─── Milestone ──────────────────────────────────────────────────────────

    /**
     * Resolve the milestone plan id for a BSG. BillingSchedule.BillingMilestonePlanId is a
     * license-gated billing extension field not visible to the Apex compiler for static SOQL.
     */
    private static Id findMilestonePlanId(Id recordId) {
        try {
            List<SObject> rows = Database.query(
                'SELECT BillingMilestonePlanId FROM BillingSchedule ' +
                'WHERE BillingScheduleGroupId = :recordId AND BillingMilestonePlanId != null LIMIT 1',
                AccessLevel.USER_MODE
            );
            if (!rows.isEmpty()) {
                return (Id) rows[0].get('BillingMilestonePlanId');
            }
        } catch (Exception e) {
            // Billing milestone extension not available in this org
        }
        return null;
    }

    private static MilestonePlanData getMilestonePlan(Id planId, Decimal bsgBilledAmount) {
        MilestonePlanData plan = new MilestonePlanData();
        try {
            // BillingMilestonePlan(Item) are license-gated billing extensions accessed
            // dynamically (USER_MODE) so the class compiles regardless of compile-time visibility.
            List<SObject> bmpList = Database.query(
                'SELECT Id, Name, Status, Description, ReferenceItemAmount ' +
                'FROM BillingMilestonePlan WHERE Id = :planId LIMIT 1',
                AccessLevel.USER_MODE
            );
            if (bmpList.isEmpty()) {
                return plan;
            }
            SObject bmp = bmpList[0];

            plan.planId = String.valueOf(bmp.get('Id'));
            plan.planName = (String) bmp.get('Name');
            plan.planStatus = (String) bmp.get('Status');
            plan.description = (String) bmp.get('Description');
            plan.referenceAmount = (Decimal) bmp.get('ReferenceItemAmount');
            plan.billedAmount = bsgBilledAmount != null ? bsgBilledAmount : 0;

            List<SObject> items = Database.query(
                'SELECT Id, Name, Type, Percentage, FlatAmount, MilestoneType, ' +
                'MilestoneAmount, CommencementDate, ' +
                'IsMilestoneAccomplished, Status, MilestoneAccomplishmentDate ' +
                'FROM BillingMilestonePlanItem WHERE BillingMilestonePlanId = :planId ' +
                'ORDER BY IsMilestoneAccomplished DESC, MilestoneAccomplishmentDate ASC NULLS LAST, MilestoneAmount DESC',
                AccessLevel.USER_MODE
            );

            plan.items = new List<MilestoneItemData>();
            for (SObject item : items) {
                MilestoneItemData mid = new MilestoneItemData();
                mid.id = String.valueOf(item.get('Id'));
                mid.name = (String) item.get('Name');
                mid.itemType = (String) item.get('Type');
                mid.percentage = (Decimal) item.get('Percentage');
                mid.flatAmount = (Decimal) item.get('FlatAmount');
                mid.milestoneType = (String) item.get('MilestoneType');
                mid.milestoneAmount = (Decimal) item.get('MilestoneAmount');
                mid.commencementDate = (String) item.get('CommencementDate');
                mid.isAccomplished = (Boolean) item.get('IsMilestoneAccomplished');
                mid.status = (String) item.get('Status');
                Object accDate = item.get('MilestoneAccomplishmentDate');
                mid.accomplishmentDate = accDate != null ? String.valueOf(accDate) : null;
                plan.items.add(mid);
            }
        } catch (Exception e) {
            // Billing milestone extension not available — return whatever was populated
        }

        return plan;
    }

    // ─── Bundle ─────────────────────────────────────────────────────────────

    private static BundleData getBundleData(
        Id recordId, BillingScheduleGroup currentBsg,
        List<BsgRelationship> asMain, List<BsgRelationship> asComponent
    ) {
        BundleData bd = new BundleData();

        // Walk up to the root bundle
        Id mainBsgId;
        if (!asMain.isEmpty()) {
            bd.isMainBundle = true;
            mainBsgId = recordId;
        } else {
            bd.isMainBundle = false;
            mainBsgId = asComponent[0].MainBsgId;
            // Keep walking up if this parent is itself a component
            Set<Id> visited = new Set<Id>{ recordId };
            Id cursor = mainBsgId;
            while (cursor != null && !visited.contains(cursor)) {
                visited.add(cursor);
                List<BsgRelationship> parentRel = [
                    SELECT MainBsgId FROM BsgRelationship
                    WHERE AssociatedBsgId = :cursor LIMIT 1
                ];
                if (parentRel.isEmpty()) break;
                cursor = parentRel[0].MainBsgId;
            }
            // cursor is now the visited node; the last valid mainBsgId is one step back
            mainBsgId = (new List<Id>(visited))[visited.size() - 1];
            // Actually re-check: walk from recordId up to root
            mainBsgId = findRootBsgId(recordId);
        }

        BillingScheduleGroup mainBsg;
        if (mainBsgId == recordId) {
            mainBsg = currentBsg;
        } else {
            mainBsg = [
                SELECT Id, BillingScheduleGroupNumber, ProductName, BillingType,
                       BillingMethod, BillingTermUnit, BillingTerm, EndDate
                FROM BillingScheduleGroup WHERE Id = :mainBsgId LIMIT 1
            ];
        }

        bd.mainBsgId = mainBsg.Id;
        bd.mainBsgProduct = mainBsg.ProductName;
        bd.mainChargeType = deriveChargeType(mainBsg.BillingMethod, mainBsg.BillingTermUnit, mainBsg.EndDate);
        bd.mainBillingFrequency = formatFrequency(mainBsg.BillingTerm, mainBsg.BillingTermUnit);

        // Recursively collect all components in a flat list with depth
        bd.components = new List<BundleComponentData>();
        collectChildComponents(mainBsgId, recordId, 1, bd.components);

        return bd;
    }

    private static Id findRootBsgId(Id bsgId) {
        Set<Id> visited = new Set<Id>();
        Id current = bsgId;
        while (current != null && !visited.contains(current)) {
            visited.add(current);
            List<BsgRelationship> parentRel = [
                SELECT MainBsgId FROM BsgRelationship
                WHERE AssociatedBsgId = :current LIMIT 1
            ];
            if (parentRel.isEmpty()) return current;
            current = parentRel[0].MainBsgId;
        }
        return current;
    }

    private static void collectChildComponents(
        Id parentBsgId, Id currentRecordId, Integer depth,
        List<BundleComponentData> result
    ) {
        if (depth > 5) return; // safety limit

        List<BsgRelationship> childRels = [
            SELECT AssociatedBsgId FROM BsgRelationship WHERE MainBsgId = :parentBsgId
        ];
        if (childRels.isEmpty()) return;

        Set<Id> childIds = new Set<Id>();
        for (BsgRelationship rel : childRels) {
            childIds.add(rel.AssociatedBsgId);
        }

        // Check which children are themselves sub-bundles
        Map<Id, Boolean> isSubBundleMap = new Map<Id, Boolean>();
        for (Id cid : childIds) isSubBundleMap.put(cid, false);
        for (AggregateResult ar : [
            SELECT MainBsgId FROM BsgRelationship
            WHERE MainBsgId IN :childIds GROUP BY MainBsgId
        ]) {
            isSubBundleMap.put((Id)ar.get('MainBsgId'), true);
        }

        for (BillingScheduleGroup comp : [
            SELECT Id, ProductName, BillingMethod, BillingTermUnit, BillingTerm, EndDate
            FROM BillingScheduleGroup WHERE Id IN :childIds ORDER BY ProductName ASC
        ]) {
            BundleComponentData bcd = new BundleComponentData();
            bcd.bsgId = comp.Id;
            bcd.productName = comp.ProductName;
            bcd.chargeType = deriveChargeType(comp.BillingMethod, comp.BillingTermUnit, comp.EndDate);
            bcd.billingFrequency = formatFrequency(comp.BillingTerm, comp.BillingTermUnit);
            bcd.isCurrent = (comp.Id == currentRecordId);
            bcd.depth = depth;
            bcd.isSubBundle = isSubBundleMap.get(comp.Id) == true;
            result.add(bcd);

            // Recurse into sub-bundles
            if (bcd.isSubBundle) {
                collectChildComponents(comp.Id, currentRecordId, depth + 1, result);
            }
        }
    }

    private static String deriveChargeType(String billingMethod, String termUnit, Date endDate) {
        if (billingMethod == 'Usage') return 'Usage';
        if (termUnit != null && termUnit.equalsIgnoreCase('OneTime')) return 'One-Time';
        if (endDate == null) return 'Evergreen';
        return 'Termed Subscription';
    }

    private static String formatFrequency(Integer term, String unit) {
        if (unit != null && unit.equalsIgnoreCase('OneTime')) return 'One-Time';
        String t = (term != null ? String.valueOf(term) : '1');
        String u = (unit != null ? unit : '');
        return t + ' ' + u;
    }

    // ─── Usage ──────────────────────────────────────────────────────────────

    private static UsageData getUsageData(Id recordId, BillingScheduleGroup bsg) {
        UsageData ud = new UsageData();
        ud.anchorBsgId = bsg.AnchorProdtBillingSchdGrpId;
        ud.currentBsgNumber = bsg.BillingScheduleGroupNumber;
        ud.currentProductName = bsg.ProductName;
        ud.billingType = bsg.BillingType;

        List<BillingSchedule> bsList = [
            SELECT UsageResourceId, UsageResource.Name
            FROM BillingSchedule
            WHERE BillingScheduleGroupId = :recordId AND UsageResourceId != null
            LIMIT 1
        ];
        if (!bsList.isEmpty()) {
            ud.currentResourceName = bsList[0].UsageResource.Name;
        }

        if (bsg.AnchorProdtBillingSchdGrpId != null) {
            BillingScheduleGroup anchorBsg = [
                SELECT Id, BillingScheduleGroupNumber, ProductName
                FROM BillingScheduleGroup WHERE Id = :bsg.AnchorProdtBillingSchdGrpId LIMIT 1
            ];
            ud.anchorBsgNumber = anchorBsg.BillingScheduleGroupNumber;
            ud.anchorProductName = anchorBsg.ProductName;
        }

        ud.siblings = new List<UsageSiblingData>();
        if (bsg.AnchorProdtBillingSchdGrpId != null) {
            List<BillingScheduleGroup> siblingBsgs = [
                SELECT Id, BillingScheduleGroupNumber, TotalBilledAmount
                FROM BillingScheduleGroup
                WHERE AnchorProdtBillingSchdGrpId = :bsg.AnchorProdtBillingSchdGrpId
                  AND BillingMethod = 'Usage'
            ];

            Set<Id> siblingIds = new Set<Id>();
            for (BillingScheduleGroup sib : siblingBsgs) {
                siblingIds.add(sib.Id);
            }

            Map<Id, String> bsgToResourceName = new Map<Id, String>();
            if (!siblingIds.isEmpty()) {
                for (BillingSchedule bs : [
                    SELECT BillingScheduleGroupId, UsageResource.Name
                    FROM BillingSchedule
                    WHERE BillingScheduleGroupId IN :siblingIds AND UsageResourceId != null
                ]) {
                    bsgToResourceName.put(bs.BillingScheduleGroupId, bs.UsageResource.Name);
                }
            }

            for (BillingScheduleGroup sib : siblingBsgs) {
                UsageSiblingData usd = new UsageSiblingData();
                usd.bsgId = sib.Id;
                usd.bsgNumber = sib.BillingScheduleGroupNumber;
                usd.resourceName = bsgToResourceName.get(sib.Id);
                usd.billedAmount = sib.TotalBilledAmount != null ? sib.TotalBilledAmount : 0;
                usd.isCurrent = (sib.Id == recordId);
                ud.siblings.add(usd);
            }
        }

        return ud;
    }

    // ─── Billing Arrangement ────────────────────────────────────────────────

    private static ArrangementData getArrangementData(Id arrangementId) {
        ArrangementData ad = new ArrangementData();

        BillingArrangement ba = [
            SELECT Id, Name, Status
            FROM BillingArrangement WHERE Id = :arrangementId LIMIT 1
        ];

        ad.arrangementId = ba.Id;
        ad.arrangementName = ba.Name;
        ad.status = ba.Status;

        ad.lines = new List<ArrangementLineData>();
        for (BillingArrangementLine bal : [
            SELECT Id, BillingArrangementLineName, Account.Name,
                   BillingAccountId, BillingPercentage, ShouldBillRemainder
            FROM BillingArrangementLine
            WHERE BillingArrangementId = :arrangementId
            ORDER BY BillingPercentage DESC
        ]) {
            ArrangementLineData ald = new ArrangementLineData();
            ald.lineId = bal.Id;
            ald.lineName = bal.BillingArrangementLineName;
            ald.accountName = bal.Account.Name;
            ald.billingPercentage = bal.BillingPercentage;
            ald.shouldBillRemainder = bal.ShouldBillRemainder;
            ad.lines.add(ald);
        }

        return ad;
    }
}