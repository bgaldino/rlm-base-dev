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

        // Totals for the whole billing schedule group (TotalBilledAmount / TotalPendingAmount), not one schedule.
        @AuraEnabled public Decimal groupBilledAmount;
        @AuraEnabled public Decimal groupPendingAmount;

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
        @AuraEnabled public Decimal billingPercentage;
        @AuraEnabled public Boolean shouldBillRemainder;
    }

    // ─── Main entry point ───────────────────────────────────────────────────

    @AuraEnabled(cacheable=true)
    public static BSGContext getBSGContext(String recordId) {
        BSGContext ctx = new BSGContext();

        // Validate the inbound id up front so a malformed/stale/cross-type id returns a
        // clean 'standard' context instead of surfacing a raw QueryException to the LWC.
        Id bsgRecordId;
        try {
            bsgRecordId = Id.valueOf(recordId);
        } catch (Exception e) {
            ctx.viewType = 'standard';
            return ctx;
        }

        try {
            // TotalBilledAmount and TotalPendingAmount are rollups that are not permissionable
            // (measured on a 264 org): object read is the only gate, no field grant exists.
            List<BillingScheduleGroup> bsgList = [
                SELECT Id, BillingScheduleGroupNumber, ProductName, Product2Id,
                       BillingType, BillingMethod, BillingTermUnit, BillingTerm,
                       AnchorProdtBillingSchdGrpId, BindingInstanceId,
                       BillingArrangementId, TotalBilledAmount, TotalPendingAmount, EndDate
                FROM BillingScheduleGroup
                WHERE Id = :bsgRecordId
                WITH USER_MODE
                LIMIT 1
            ];
            if (bsgList.isEmpty()) {
                ctx.viewType = 'standard';
                return ctx;
            }
            fillContext(ctx, bsgList[0]);
        } catch (Exception e) {
            // Degrade gracefully to a standard view rather than throwing to the client.
            if (ctx.viewType == null) {
                ctx.viewType = 'standard';
            }
        }

        return ctx;
    }

    // The view type and its data for a queried group: milestone, bundle, usage or standard, plus
    // its billing arrangement. Takes the group so a test can pass one, which Apex cannot insert.
    @TestVisible
    private static void fillContext(BSGContext ctx, BillingScheduleGroup bsg) {

        ctx.bsgNumber = bsg.BillingScheduleGroupNumber;
        ctx.productName = bsg.ProductName;
        ctx.billingType = bsg.BillingType;
        ctx.billingMethod = bsg.BillingMethod;
        ctx.billingTermUnit = bsg.BillingTermUnit;
        ctx.billingTerm = bsg.BillingTerm;

        // Group-level billed/pending for the panel's % calculation. The group's own rollups
        // are used (no extra query, record currency like the panel's formatting); a sum over
        // schedules would be corporate-currency converted in a multi-currency org.
        ctx.groupBilledAmount = bsg.TotalBilledAmount;
        ctx.groupPendingAmount = bsg.TotalPendingAmount;

        // 1. Check for Milestone. BillingSchedule.BillingMilestonePlanId and the
        // BillingMilestonePlan(Item) objects are license-gated billing extensions that are
        // not surfaced to the Apex compiler for static SOQL (compile visibility can also lag
        // behind entitlement propagation in a fresh org), so query them dynamically.
        Id milestonePlanId = findMilestonePlanId(bsg.Id);
        if (milestonePlanId != null) {
            ctx.viewType = 'milestone';
            ctx.milestonePlan = getMilestonePlan(milestonePlanId, bsg.TotalBilledAmount);
        }

        // 2. Check for Bundle relationships
        if (ctx.viewType == null) {
            List<BsgRelationship> asMain = [
                SELECT Id, AssociatedBsgId, AssociatedBsgRole, AssociatedBsgPricing
                FROM BsgRelationship WHERE MainBsgId = :bsg.Id WITH USER_MODE LIMIT 50
            ];
            List<BsgRelationship> asComponent = [
                SELECT Id, MainBsgId, MainBsgRole
                FROM BsgRelationship WHERE AssociatedBsgId = :bsg.Id WITH USER_MODE LIMIT 1
            ];

            if (!asMain.isEmpty() || !asComponent.isEmpty()) {
                ctx.viewType = 'bundle';
                ctx.bundle = getBundleData(bsg.Id, bsg, asMain, asComponent);
            }
        }

        // 3. Check for Usage
        if (ctx.viewType == null && bsg.BillingMethod == 'Usage') {
            ctx.viewType = 'usage';
            ctx.usage = getUsageData(bsg.Id, bsg);
        }

        // 4. Fallback
        if (ctx.viewType == null) {
            ctx.viewType = 'standard';
        }

        // 5. Check for Billing Arrangement (applies to any view type)
        if (bsg.BillingArrangementId != null) {
            ctx.arrangement = getArrangementData(bsg.BillingArrangementId);
        }
    }

    // ─── Milestone ──────────────────────────────────────────────────────────

    /**
     * Resolve the milestone plan id for a BSG. BillingSchedule.BillingMilestonePlanId is a
     * license-gated billing extension field not visible to the Apex compiler for static SOQL.
     */
    @TestVisible
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

    @TestVisible
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
            fillPlanHeader(plan, bmpList[0], bsgBilledAmount);

            List<SObject> items = Database.query(
                'SELECT Id, Name, Type, Percentage, FlatAmount, MilestoneType, ' +
                'MilestoneAmount, CommencementDate, ' +
                'IsMilestoneAccomplished, Status, MilestoneAccomplishmentDate ' +
                'FROM BillingMilestonePlanItem WHERE BillingMilestonePlanId = :planId ' +
                'ORDER BY IsMilestoneAccomplished DESC, MilestoneAccomplishmentDate ASC NULLS LAST, MilestoneAmount DESC',
                AccessLevel.USER_MODE
            );

            plan.items = new List<MilestoneItemData>();
            addMilestoneItems(plan.items, items);
        } catch (Exception e) {
            // Billing milestone extension not available — return whatever was populated
        }

        return plan;
    }

    // The plan's own fields, and the group's billed amount (zero when blank). Takes the row so a
    // test can pass a plan without the billing treatment a real one needs.
    @TestVisible
    private static void fillPlanHeader(MilestonePlanData plan, SObject bmp, Decimal bsgBilledAmount) {
        plan.planId = String.valueOf(bmp.get('Id'));
        plan.planName = (String) bmp.get('Name');
        plan.planStatus = (String) bmp.get('Status');
        plan.description = (String) bmp.get('Description');
        plan.referenceAmount = (Decimal) bmp.get('ReferenceItemAmount');
        plan.billedAmount = bsgBilledAmount != null ? bsgBilledAmount : 0;
    }

    // One item per queried milestone plan item, in query order. Takes rows so a test can pass
    // items of a plan it cannot create.
    @TestVisible
    private static void addMilestoneItems(List<MilestoneItemData> target, List<SObject> items) {
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
            target.add(mid);
        }
    }

    // ─── Bundle ─────────────────────────────────────────────────────────────

    @TestVisible
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
            mainBsgId = findRootBsgId(recordId);
        }

        BillingScheduleGroup mainBsg;
        if (mainBsgId == recordId) {
            mainBsg = currentBsg;
        } else {
            List<BillingScheduleGroup> mainBsgList = [
                SELECT Id, BillingScheduleGroupNumber, ProductName, BillingType,
                       BillingMethod, BillingTermUnit, BillingTerm, EndDate
                FROM BillingScheduleGroup WHERE Id = :mainBsgId WITH USER_MODE LIMIT 1
            ];
            if (mainBsgList.isEmpty()) {
                // Root resolved to a record the user can't see / no longer exists; fall back.
                mainBsg = currentBsg;
                mainBsgId = recordId;
            } else {
                mainBsg = mainBsgList[0];
            }
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
        // Linear walk up the parent chain. Each level depends on the prior result so it
        // can't be batched, but the visited set bounds it and guards against cycles.
        while (current != null && !visited.contains(current)) {
            visited.add(current);
            List<BsgRelationship> parentRel = [
                SELECT MainBsgId FROM BsgRelationship
                WHERE AssociatedBsgId = :current WITH USER_MODE LIMIT 1
            ];
            if (parentRel.isEmpty()) return current;
            current = parentRel[0].MainBsgId;
        }
        return current;
    }

    private static void collectChildComponents(
        Id mainBsgId, Id currentRecordId, Integer startDepth,
        List<BundleComponentData> result
    ) {
        // Breadth-first load of the descendant hierarchy: one relationship query per level
        // (≤5 levels) keyed off the whole frontier, instead of issuing 3 queries per node.
        // The flat result list is then assembled in depth-first display order in memory.
        Map<Id, List<Id>> parentToChildren = new Map<Id, List<Id>>();
        Set<Id> allChildIds = new Set<Id>();
        Set<Id> frontier = new Set<Id>{ mainBsgId };
        Set<Id> seenParents = new Set<Id>();
        Integer level = 0;
        while (!frontier.isEmpty() && level < 5) {
            frontier.removeAll(seenParents);
            if (frontier.isEmpty()) break;
            seenParents.addAll(frontier);
            Set<Id> nextFrontier = new Set<Id>();
            addRelationshipLevel([
                SELECT MainBsgId, AssociatedBsgId FROM BsgRelationship
                WHERE MainBsgId IN :frontier WITH USER_MODE
            ], parentToChildren, allChildIds, nextFrontier);
            frontier = nextFrontier;
            level++;
        }

        if (allChildIds.isEmpty()) return;

        // Any child that is itself a parent in the map is a sub-bundle.
        Set<Id> subBundleIds = new Set<Id>(parentToChildren.keySet());

        Map<Id, BillingScheduleGroup> bsgById = new Map<Id, BillingScheduleGroup>([
            SELECT Id, ProductName, BillingMethod, BillingTermUnit, BillingTerm, EndDate
            FROM BillingScheduleGroup WHERE Id IN :allChildIds WITH USER_MODE
        ]);

        appendComponentsDfs(mainBsgId, currentRecordId, startDepth, parentToChildren,
                            subBundleIds, bsgById, result, new Set<Id>{ mainBsgId });
    }

    // Records one level of the hierarchy: each child under its parent, in the next frontier and
    // among all children. Takes rows so a test can pass relationships, which Apex cannot insert.
    @TestVisible
    private static void addRelationshipLevel(
        List<BsgRelationship> rels, Map<Id, List<Id>> parentToChildren,
        Set<Id> allChildIds, Set<Id> nextFrontier
    ) {
        for (BsgRelationship rel : rels) {
            if (!parentToChildren.containsKey(rel.MainBsgId)) {
                parentToChildren.put(rel.MainBsgId, new List<Id>());
            }
            parentToChildren.get(rel.MainBsgId).add(rel.AssociatedBsgId);
            allChildIds.add(rel.AssociatedBsgId);
            nextFrontier.add(rel.AssociatedBsgId);
        }
    }

    @TestVisible
    private static void appendComponentsDfs(
        Id parentBsgId, Id currentRecordId, Integer depth,
        Map<Id, List<Id>> parentToChildren, Set<Id> subBundleIds,
        Map<Id, BillingScheduleGroup> bsgById, List<BundleComponentData> result,
        Set<Id> emitted
    ) {
        if (depth > 5) return; // safety limit
        List<Id> childIds = parentToChildren.get(parentBsgId);
        if (childIds == null || childIds.isEmpty()) return;

        // Sort siblings by ProductName to preserve the original (ORDER BY ProductName) display order.
        List<BsgNameSort> sorted = new List<BsgNameSort>();
        for (Id cid : childIds) {
            if (bsgById.containsKey(cid)) sorted.add(new BsgNameSort(bsgById.get(cid)));
        }
        sorted.sort();

        for (BsgNameSort wrapper : sorted) {
            BillingScheduleGroup comp = wrapper.bsg;
            if (emitted.contains(comp.Id)) continue; // diamond / cycle guard
            emitted.add(comp.Id);

            BundleComponentData bcd = new BundleComponentData();
            bcd.bsgId = comp.Id;
            bcd.productName = comp.ProductName;
            bcd.chargeType = deriveChargeType(comp.BillingMethod, comp.BillingTermUnit, comp.EndDate);
            bcd.billingFrequency = formatFrequency(comp.BillingTerm, comp.BillingTermUnit);
            bcd.isCurrent = (comp.Id == currentRecordId);
            bcd.depth = depth;
            bcd.isSubBundle = subBundleIds.contains(comp.Id);
            result.add(bcd);

            if (bcd.isSubBundle) {
                appendComponentsDfs(comp.Id, currentRecordId, depth + 1, parentToChildren,
                                    subBundleIds, bsgById, result, emitted);
            }
        }
    }

    private class BsgNameSort implements Comparable {
        BillingScheduleGroup bsg;
        BsgNameSort(BillingScheduleGroup b) { this.bsg = b; }
        public Integer compareTo(Object other) {
            String a = bsg.ProductName == null ? '' : bsg.ProductName;
            String b = ((BsgNameSort) other).bsg.ProductName == null ? '' : ((BsgNameSort) other).bsg.ProductName;
            return a.compareTo(b);
        }
    }

    @TestVisible
    private static String deriveChargeType(String billingMethod, String termUnit, Date endDate) {
        if (billingMethod == 'Usage') return 'Usage';
        if (termUnit != null && termUnit.equalsIgnoreCase('OneTime')) return 'One-Time';
        if (endDate == null) return 'Evergreen';
        return 'Termed Subscription';
    }

    @TestVisible
    private static String formatFrequency(Integer term, String unit) {
        if (unit != null && unit.equalsIgnoreCase('OneTime')) return 'One-Time';
        String t = (term != null ? String.valueOf(term) : '1');
        String u = (unit != null ? unit : '');
        return t + ' ' + u;
    }

    // ─── Usage ──────────────────────────────────────────────────────────────

    @TestVisible
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
            WITH USER_MODE
            ORDER BY CreatedDate, Id
            LIMIT 1
        ];
        if (!bsList.isEmpty()) {
            ud.currentResourceName = bsList[0].UsageResource.Name;
        }

        if (bsg.AnchorProdtBillingSchdGrpId != null) {
            List<BillingScheduleGroup> anchorList = [
                SELECT Id, BillingScheduleGroupNumber, ProductName
                FROM BillingScheduleGroup WHERE Id = :bsg.AnchorProdtBillingSchdGrpId WITH USER_MODE LIMIT 1
            ];
            if (!anchorList.isEmpty()) {
                ud.anchorBsgNumber = anchorList[0].BillingScheduleGroupNumber;
                ud.anchorProductName = anchorList[0].ProductName;
            }
        }

        ud.siblings = new List<UsageSiblingData>();
        if (bsg.AnchorProdtBillingSchdGrpId != null) {
            List<BillingScheduleGroup> siblingBsgs = [
                SELECT Id, BillingScheduleGroupNumber, TotalBilledAmount
                FROM BillingScheduleGroup
                WHERE AnchorProdtBillingSchdGrpId = :bsg.AnchorProdtBillingSchdGrpId
                  AND BillingMethod = 'Usage'
                WITH USER_MODE
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
                    WITH USER_MODE
                    ORDER BY CreatedDate, Id
                ]) {
                    // The earliest schedule's resource wins, deterministically.
                    if (!bsgToResourceName.containsKey(bs.BillingScheduleGroupId)) {
                        bsgToResourceName.put(bs.BillingScheduleGroupId, bs.UsageResource.Name);
                    }
                }
            }

            addUsageSiblings(ud.siblings, siblingBsgs, bsgToResourceName, recordId);
        }

        return ud;
    }

    // One row per sibling usage group, with its resource and billed amount (zero when blank),
    // marking the current group. Takes rows so a test can pass groups, which Apex cannot insert.
    @TestVisible
    private static void addUsageSiblings(
        List<UsageSiblingData> target, List<BillingScheduleGroup> siblingBsgs,
        Map<Id, String> bsgToResourceName, Id recordId
    ) {
        for (BillingScheduleGroup sib : siblingBsgs) {
            UsageSiblingData usd = new UsageSiblingData();
            usd.bsgId = sib.Id;
            usd.bsgNumber = sib.BillingScheduleGroupNumber;
            usd.resourceName = bsgToResourceName.get(sib.Id);
            usd.billedAmount = sib.TotalBilledAmount != null ? sib.TotalBilledAmount : 0;
            usd.isCurrent = (sib.Id == recordId);
            target.add(usd);
        }
    }

    // ─── Billing Arrangement ────────────────────────────────────────────────

    @TestVisible
    private static ArrangementData getArrangementData(Id arrangementId) {
        ArrangementData ad = new ArrangementData();

        List<BillingArrangement> baList = [
            SELECT Id, Name, Status
            FROM BillingArrangement WHERE Id = :arrangementId WITH USER_MODE LIMIT 1
        ];
        if (baList.isEmpty()) {
            return ad;
        }
        BillingArrangement ba = baList[0];

        ad.arrangementId = ba.Id;
        ad.arrangementName = ba.Name;
        ad.status = ba.Status;

        ad.lines = new List<ArrangementLineData>();
        // Account names are read apart from the lines: an Account.Name relationship in this query
        // would fail it, and drop every line, for a user who cannot read Account.
        List<BillingArrangementLine> arrangementLines = [
            SELECT Id, BillingArrangementLineName, AccountId,
                   BillingAccountId, BillingPercentage, ShouldBillRemainder
            FROM BillingArrangementLine
            WHERE BillingArrangementId = :arrangementId
            WITH USER_MODE
            ORDER BY BillingPercentage DESC
        ];
        Set<Id> accountIds = new Set<Id>();
        for (BillingArrangementLine bal : arrangementLines) {
            if (bal.AccountId != null) accountIds.add(bal.AccountId);
        }
        addArrangementLines(ad.lines, arrangementLines, RLM_AccountNames.forIds(accountIds));

        return ad;
    }

    // One row per queried arrangement line, in query order. Takes rows so a test can pass lines,
    // which need a fully set-up billing account to insert.
    @TestVisible
    private static void addArrangementLines(List<ArrangementLineData> target, List<BillingArrangementLine> lines, Map<Id, String> accountNames) {
        for (BillingArrangementLine bal : lines) {
            ArrangementLineData ald = new ArrangementLineData();
            ald.lineId = bal.Id;
            ald.lineName = bal.BillingArrangementLineName;
            ald.accountName = bal.AccountId != null ? accountNames.get(bal.AccountId) : null;
            ald.billingPercentage = bal.BillingPercentage;
            ald.shouldBillRemainder = bal.ShouldBillRemainder;
            target.add(ald);
        }
    }
}