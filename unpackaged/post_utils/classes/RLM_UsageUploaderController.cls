/**
 * RLM_UsageUploaderController
 *
 * Apex controller for the rlmUsageUploader Lightning Web Component.
 * Provides methods to:
 *  - Load Usage Resources for an Asset (dynamically from its Product)
 *  - Upload single usage records as TransactionJournal entries
 *  - Bulk upload usage from parsed CSV data
 *  - Validate usage entries before committing
 */
public with sharing class RLM_UsageUploaderController {

    // ─── Constants ──────────────────────────────────────────────────────

    private static final String USAGE_TYPE_MANAGEMENT = 'UsageManagement';
    private static final String STATUS_PENDING = 'Pending';

    // ─── Inner Classes (Wrappers) ───────────────────────────────────────

    public class UsageResourceWrapper {
        @AuraEnabled public Id resourceId;
        @AuraEnabled public String resourceName;
        @AuraEnabled public String unitOfMeasureName;
        @AuraEnabled public String unitOfMeasureCode;
        @AuraEnabled public Id unitOfMeasureId;
        @AuraEnabled public Id unitOfMeasureClassId;
        @AuraEnabled public List<UomOption> availableUoms;
    }

    public class UomOption {
        @AuraEnabled public Id uomId;
        @AuraEnabled public String uomName;
        @AuraEnabled public String uomCode;
    }

    public class UsageEntry {
        @AuraEnabled public Id usageResourceId { get; set; }
        @AuraEnabled public String usageResourceName { get; set; }
        @AuraEnabled public Decimal quantity { get; set; }
        @AuraEnabled public Date transactionDate { get; set; }
    }

    public class BulkUploadResult {
        @AuraEnabled public Integer successCount;
        @AuraEnabled public Integer errorCount;
        @AuraEnabled public List<Id> journalIds;
        @AuraEnabled public List<String> errors;
    }

    public class ValidationResult {
        @AuraEnabled public Integer rowIndex;
        @AuraEnabled public Boolean isValid;
        @AuraEnabled public String errorMessage;
        @AuraEnabled public Id resolvedResourceId;
        @AuraEnabled public Id resolvedUnitOfMeasureId;
    }

    public class RateInfoWrapper {
        @AuraEnabled public Id rateCardEntryId;
        @AuraEnabled public String rateCardName;
        @AuraEnabled public String rateCardType;     // 'Base' or 'Tier'
        @AuraEnabled public Id usageResourceId;
        @AuraEnabled public String usageResourceName;
        @AuraEnabled public Decimal baseRate;
        @AuraEnabled public Decimal negotiatedRate;
        @AuraEnabled public String rateUomName;
        @AuraEnabled public Datetime startDate;
        @AuraEnabled public Datetime endDate;
        @AuraEnabled public List<TierInfo> tiers;
    }

    public class TierInfo {
        @AuraEnabled public Decimal lowerBound;
        @AuraEnabled public Decimal upperBound;
        @AuraEnabled public String adjustmentType;
        @AuraEnabled public Decimal adjustmentValue;
        @AuraEnabled public String rateUomName;
    }

    public class GrantInfoWrapper {
        @AuraEnabled public Id entitlementId;
        @AuraEnabled public String entitlementName;
        @AuraEnabled public Id usageResourceId;
        @AuraEnabled public String usageResourceName;
        @AuraEnabled public Decimal entitlementQuantity;
        @AuraEnabled public String usageModelType;
        @AuraEnabled public String grantType;
        @AuraEnabled public String chargeForOverage;
        @AuraEnabled public Datetime startDate;
        @AuraEnabled public Datetime endDate;
        @AuraEnabled public Decimal bucketBalance;
        @AuraEnabled public Decimal consumedEntitlement;
        @AuraEnabled public Decimal totalConsumedEntitlement;
    }

    public class AssetOption {
        @AuraEnabled public Id assetId;
        @AuraEnabled public String assetName;
        @AuraEnabled public String productName;
    }

    // ─── Methods ────────────────────────────────────────────────────────

    /**
     * Retrieves active Assets for an Account, filtered by lifecycle dates and Anchor products.
     * Used by the rlmUsageUploader component when placed on Account record pages.
     */
    @AuraEnabled(cacheable=true)
    public static List<AssetOption> getAssetsForAccount(Id accountId) {
        List<AssetOption> options = new List<AssetOption>();

        List<Asset> assets = [
            SELECT Id, Name, Product2.Name, Product2.UsageModelType
            FROM Asset
            WHERE AccountId = :accountId
              AND LifecycleStartDate <= TODAY
              AND LifecycleEndDate >= TODAY
              AND Product2.UsageModelType = 'Anchor'
            ORDER BY Name ASC
        ];

        for (Asset ast : assets) {
            AssetOption opt = new AssetOption();
            opt.assetId = ast.Id;
            opt.assetName = ast.Name;
            opt.productName = ast.Product2?.Name;
            options.add(opt);
        }

        return options;
    }

    /**
     * Retrieves all active Usage Resources associated with an Asset's Product.
     * Returns resource details including UoM name and code for display.
     */
    @AuraEnabled(cacheable=true)
    public static List<UsageResourceWrapper> getUsageResourcesForAsset(Id assetId) {
        Asset ast = [
            SELECT Id, Product2Id
            FROM Asset
            WHERE Id = :assetId
            LIMIT 1
        ];

        if (ast.Product2Id == null) {
            throw new AuraHandledException('This asset is not associated with a product.');
        }

        List<ProductUsageResource> purList = [
            SELECT Id,
                   UsageResourceId,
                   UsageResource.Name,
                   UsageResource.DefaultUnitOfMeasureId,
                   UsageResource.DefaultUnitOfMeasure.Name,
                   UsageResource.DefaultUnitOfMeasure.UnitCode,
                   UsageResource.UnitOfMeasureClassId
            FROM ProductUsageResource
            WHERE ProductId = :ast.Product2Id
              AND Status = 'Active'
            ORDER BY UsageResource.Name ASC
        ];

        Set<Id> uomClassIds = new Set<Id>();
        for (ProductUsageResource pur : purList) {
            if (pur.UsageResource.UnitOfMeasureClassId != null) {
                uomClassIds.add(pur.UsageResource.UnitOfMeasureClassId);
            }
        }

        Map<Id, List<UomOption>> uomsByClass = new Map<Id, List<UomOption>>();
        if (!uomClassIds.isEmpty()) {
            for (UnitOfMeasure uom : [
                SELECT Id, Name, UnitCode, UnitOfMeasureClassId
                FROM UnitOfMeasure
                WHERE UnitOfMeasureClassId IN :uomClassIds
                  AND Status = 'Active'
                ORDER BY Name ASC
            ]) {
                if (!uomsByClass.containsKey(uom.UnitOfMeasureClassId)) {
                    uomsByClass.put(uom.UnitOfMeasureClassId, new List<UomOption>());
                }
                UomOption opt = new UomOption();
                opt.uomId = uom.Id;
                opt.uomName = uom.Name;
                opt.uomCode = uom.UnitCode;
                uomsByClass.get(uom.UnitOfMeasureClassId).add(opt);
            }
        }

        List<UsageResourceWrapper> wrappers = new List<UsageResourceWrapper>();
        for (ProductUsageResource pur : purList) {
            UsageResourceWrapper w = new UsageResourceWrapper();
            w.resourceId = pur.UsageResourceId;
            w.resourceName = pur.UsageResource.Name;
            w.unitOfMeasureId = pur.UsageResource.DefaultUnitOfMeasureId;
            w.unitOfMeasureName = pur.UsageResource.DefaultUnitOfMeasure?.Name;
            w.unitOfMeasureCode = pur.UsageResource.DefaultUnitOfMeasure?.UnitCode;
            w.unitOfMeasureClassId = pur.UsageResource.UnitOfMeasureClassId;
            w.availableUoms = uomsByClass.containsKey(pur.UsageResource.UnitOfMeasureClassId)
                ? uomsByClass.get(pur.UsageResource.UnitOfMeasureClassId)
                : new List<UomOption>();
            wrappers.add(w);
        }

        return wrappers;
    }

    /**
     * Creates a single TransactionJournal record for usage tracking.
     * If unitOfMeasureId is provided, uses it; otherwise falls back to the resource's default UoM.
     */
    @AuraEnabled
    public static Id uploadUsage(
        Id assetId,
        Id usageResourceId,
        Decimal quantity,
        Date transactionDate,
        Id unitOfMeasureId
    ) {
        // Resolve the AccountId from the Asset
        Asset ast = [
            SELECT Id, AccountId
            FROM Asset
            WHERE Id = :assetId
            LIMIT 1
        ];

        // Determine which UoM to use
        Id resolvedUomId = unitOfMeasureId;
        if (resolvedUomId == null) {
            UsageResource ur = [
                SELECT Id, DefaultUnitOfMeasureId
                FROM UsageResource
                WHERE Id = :usageResourceId
                LIMIT 1
            ];
            resolvedUomId = ur.DefaultUnitOfMeasureId;
        }

        TransactionJournal tj = buildTransactionJournal(
            assetId,
            ast.AccountId,
            usageResourceId,
            quantity,
            transactionDate,
            resolvedUomId
        );

        insert tj;
        return tj.Id;
    }

    /**
     * Helper method to build a TransactionJournal record with standard fields.
     */
    private static TransactionJournal buildTransactionJournal(
        Id assetId,
        Id accountId,
        Id usageResourceId,
        Decimal quantity,
        Date transactionDate,
        Id unitOfMeasureId
    ) {
        TransactionJournal tj = new TransactionJournal();
        tj.ReferenceRecordId = assetId;
        tj.AccountId = accountId;
        tj.UsageResourceId = usageResourceId;
        tj.Quantity = quantity;
        tj.ActivityDate = transactionDate;
        tj.StartDate = transactionDate;
        tj.EndDate = transactionDate;
        tj.QuantityUnitOfMeasureId = unitOfMeasureId;
        tj.UsageType = USAGE_TYPE_MANAGEMENT;
        tj.Status = STATUS_PENDING;
        return tj;
    }

    /**
     * Validates a list of UsageEntry records against the asset's available resources.
     * Returns per-row validation results with resolved IDs.
     */
    @AuraEnabled
    public static List<ValidationResult> validateUsageEntries(Id assetId, List<UsageEntry> entries) {
        // Build a map of resource name → resource info for this asset
        List<UsageResourceWrapper> resources = getUsageResourcesForAsset(assetId);
        Map<String, UsageResourceWrapper> resourceByName = new Map<String, UsageResourceWrapper>();
        Map<Id, UsageResourceWrapper> resourceById = new Map<Id, UsageResourceWrapper>();

        for (UsageResourceWrapper r : resources) {
            resourceByName.put(r.resourceName.toLowerCase(), r);
            resourceById.put(r.resourceId, r);
        }

        List<ValidationResult> results = new List<ValidationResult>();

        for (Integer i = 0; i < entries.size(); i++) {
            UsageEntry entry = entries[i];
            ValidationResult vr = new ValidationResult();
            vr.rowIndex = i;
            vr.isValid = true;
            vr.errorMessage = '';

            // Validate Usage Resource - try by ID first, then by name
            UsageResourceWrapper matchedResource = null;
            if (entry.usageResourceId != null && resourceById.containsKey(entry.usageResourceId)) {
                matchedResource = resourceById.get(entry.usageResourceId);
            } else if (String.isNotBlank(entry.usageResourceName)) {
                matchedResource = resourceByName.get(entry.usageResourceName.toLowerCase().trim());
            }

            if (matchedResource == null) {
                vr.isValid = false;
                String resourceRef = String.isNotBlank(entry.usageResourceName)
                    ? entry.usageResourceName
                    : String.valueOf(entry.usageResourceId);
                vr.errorMessage = 'Unknown usage resource: ' + resourceRef;
            } else {
                vr.resolvedResourceId = matchedResource.resourceId;
                vr.resolvedUnitOfMeasureId = matchedResource.unitOfMeasureId;
            }

            // Validate Quantity
            if (entry.quantity == null || entry.quantity <= 0) {
                vr.isValid = false;
                vr.errorMessage += String.isNotBlank(vr.errorMessage) ? '; ' : '';
                vr.errorMessage += 'Quantity must be greater than 0';
            }

            // Validate Date
            if (entry.transactionDate == null) {
                vr.isValid = false;
                vr.errorMessage += String.isNotBlank(vr.errorMessage) ? '; ' : '';
                vr.errorMessage += 'Transaction date is required';
            }

            results.add(vr);
        }

        return results;
    }

    /**
     * Bulk-creates TransactionJournal records from validated CSV entries.
     * Entries should be validated first via validateUsageEntries.
     */
    @AuraEnabled
    public static BulkUploadResult bulkUploadUsage(Id assetId, List<UsageEntry> entries) {
        BulkUploadResult result = new BulkUploadResult();
        result.journalIds = new List<Id>();
        result.errors = new List<String>();
        result.successCount = 0;
        result.errorCount = 0;

        // Resolve AccountId from the Asset
        Asset ast = [
            SELECT Id, AccountId
            FROM Asset
            WHERE Id = :assetId
            LIMIT 1
        ];

        // Defensive validation (client validates before calling, but server re-validates for security)
        List<ValidationResult> validations = validateUsageEntries(assetId, entries);

        List<TransactionJournal> toInsert = new List<TransactionJournal>();
        List<Integer> validIndices = new List<Integer>();

        for (Integer i = 0; i < validations.size(); i++) {
            ValidationResult vr = validations[i];
            if (!vr.isValid) {
                result.errorCount++;
                result.errors.add('Row ' + (i + 1) + ': ' + vr.errorMessage);
                continue;
            }

            UsageEntry entry = entries[i];
            TransactionJournal tj = buildTransactionJournal(
                assetId,
                ast.AccountId,
                vr.resolvedResourceId,
                entry.quantity,
                entry.transactionDate,
                vr.resolvedUnitOfMeasureId
            );

            toInsert.add(tj);
            validIndices.add(i);
        }

        if (!toInsert.isEmpty()) {
            Database.SaveResult[] saveResults = Database.insert(toInsert, false);
            for (Integer i = 0; i < saveResults.size(); i++) {
                if (saveResults[i].isSuccess()) {
                    result.successCount++;
                    result.journalIds.add(saveResults[i].getId());
                } else {
                    result.errorCount++;
                    String errorMsg = '';
                    for (Database.Error err : saveResults[i].getErrors()) {
                        errorMsg += err.getMessage() + ' ';
                    }
                    result.errors.add('Row ' + (validIndices[i] + 1) + ': ' + errorMsg.trim());
                }
            }
        }

        return result;
    }

    // ─── Rate & Grant Methods ─────────────────────────────────────────

    /**
     * Retrieves rate card entries for an Asset, including tier-based pricing.
     * Returns both base rates and tiered rate adjustments grouped by usage resource.
     *
     * Note: Queries are intentionally unbounded. An Asset typically has <50 rate entries
     * and <500 total tier adjustments. If cardinality grows significantly, implement pagination.
     */
    @AuraEnabled(cacheable=true)
    public static List<RateInfoWrapper> getRatesForAsset(Id assetId) {
        List<AssetRateCardEntry> arces = [
            SELECT Id,
                   AssetId,
                   UsageResourceId,
                   NegotiatedRate,
                   RateCardEntryId,
                   RateCardEntry.Rate,
                   RateCardEntry.RateUnitOfMeasureName,
                   RateCardEntry.RateCardType,
                   RateCardId,
                   RateCard.Name,
                   StartDate,
                   EndDate,
                   RateUnitOfMeasureId
            FROM AssetRateCardEntry
            WHERE AssetId = :assetId
            ORDER BY UsageResourceId, RateCard.Name ASC
        ];

        if (arces.isEmpty()) {
            return new List<RateInfoWrapper>();
        }

        // Collect RateCardEntry IDs and Usage Resource IDs
        Set<Id> rceIds = new Set<Id>();
        Set<Id> usageResourceIds = new Set<Id>();
        for (AssetRateCardEntry arce : arces) {
            rceIds.add(arce.RateCardEntryId);
            usageResourceIds.add(arce.UsageResourceId);
        }

        // Query tier adjustments for these rate card entries
        Map<Id, List<RateAdjustmentByTier>> tiersByRce = new Map<Id, List<RateAdjustmentByTier>>();
        for (RateAdjustmentByTier rat : [
            SELECT Id, RateCardEntryId, AdjustmentType, AdjustmentValue,
                   LowerBound, UpperBound, RateUnitOfMeasureName
            FROM RateAdjustmentByTier
            WHERE RateCardEntryId IN :rceIds
            ORDER BY LowerBound ASC
        ]) {
            if (!tiersByRce.containsKey(rat.RateCardEntryId)) {
                tiersByRce.put(rat.RateCardEntryId, new List<RateAdjustmentByTier>());
            }
            tiersByRce.get(rat.RateCardEntryId).add(rat);
        }

        // Query Usage Resource names
        Map<Id, String> resourceNames = new Map<Id, String>();
        for (UsageResource ur : [
            SELECT Id, Name FROM UsageResource WHERE Id IN :usageResourceIds
        ]) {
            resourceNames.put(ur.Id, ur.Name);
        }

        // Build wrapper list
        List<RateInfoWrapper> wrappers = new List<RateInfoWrapper>();
        for (AssetRateCardEntry arce : arces) {
            RateInfoWrapper w = new RateInfoWrapper();
            w.rateCardEntryId = arce.RateCardEntryId;
            w.rateCardName = arce.RateCard?.Name;
            w.rateCardType = arce.RateCardEntry?.RateCardType;
            w.usageResourceId = arce.UsageResourceId;
            w.usageResourceName = resourceNames.get(arce.UsageResourceId);
            w.baseRate = arce.RateCardEntry?.Rate;
            w.negotiatedRate = arce.NegotiatedRate;
            w.rateUomName = arce.RateCardEntry?.RateUnitOfMeasureName;
            w.startDate = arce.StartDate;
            w.endDate = arce.EndDate;

            // Add tier info if available
            List<RateAdjustmentByTier> tiers = tiersByRce.get(arce.RateCardEntryId);
            if (tiers != null && !tiers.isEmpty()) {
                w.tiers = new List<TierInfo>();
                for (RateAdjustmentByTier rat : tiers) {
                    TierInfo ti = new TierInfo();
                    ti.lowerBound = rat.LowerBound;
                    ti.upperBound = rat.UpperBound;
                    ti.adjustmentType = rat.AdjustmentType;
                    ti.adjustmentValue = rat.AdjustmentValue;
                    ti.rateUomName = rat.RateUnitOfMeasureName;
                    w.tiers.add(ti);
                }
            }

            wrappers.add(w);
        }

        return wrappers;
    }

    /**
     * Retrieves usage entitlement grants for an Asset, including bucket balances.
     * Shows the entitlement quantity, consumed amount, and remaining balance per resource.
     *
     * Note: Queries are intentionally unbounded. An Asset typically has <20 entitlements
     * and <100 total bucket splits. If cardinality grows significantly, implement pagination.
     */
    @AuraEnabled(cacheable=true)
    public static List<GrantInfoWrapper> getGrantsForAsset(Id assetId) {
        List<TransactionUsageEntitlement> tues = [
            SELECT Id,
                   Name,
                   AssetId,
                   UsageResourceId,
                   EntitlementQuantity,
                   TransactionQuantity,
                   NetQuantity,
                   ChargeForOverage,
                   EffectiveStartDateTime,
                   EffectiveEndDateTime,
                   UsageModelType,
                   GrantType
            FROM TransactionUsageEntitlement
            WHERE AssetId = :assetId
            ORDER BY UsageResourceId ASC
        ];

        if (tues.isEmpty()) {
            return new List<GrantInfoWrapper>();
        }

        // Collect IDs
        Set<Id> tueIds = new Set<Id>();
        Set<Id> usageResourceIds = new Set<Id>();
        for (TransactionUsageEntitlement tue : tues) {
            tueIds.add(tue.Id);
            usageResourceIds.add(tue.UsageResourceId);
        }

        // Query Usage Resource names
        Map<Id, String> resourceNames = new Map<Id, String>();
        for (UsageResource ur : [
            SELECT Id, Name FROM UsageResource WHERE Id IN :usageResourceIds
        ]) {
            resourceNames.put(ur.Id, ur.Name);
        }

        // Query the current-period entitlement buckets (child buckets with a parent)
        // These contain the actual balance and consumption for the current period
        Map<Id, UsageEntitlementBucket> currentBucketByTue = new Map<Id, UsageEntitlementBucket>();
        for (UsageEntitlementBucket ueb : [
            SELECT Id, TransactionUsageEntitlementId, BucketBalance,
                   ConsumedEntitlement, TotalConsumedEntitlement,
                   EffectiveStartDateTime, EffectiveEndDateTime
            FROM UsageEntitlementBucket
            WHERE TransactionUsageEntitlementId IN :tueIds
              AND ParentId != null
            ORDER BY EffectiveStartDateTime DESC
        ]) {
            // Keep only the most recent period bucket per TUE
            if (!currentBucketByTue.containsKey(ueb.TransactionUsageEntitlementId)) {
                currentBucketByTue.put(ueb.TransactionUsageEntitlementId, ueb);
            }
        }

        // Build wrapper list
        List<GrantInfoWrapper> wrappers = new List<GrantInfoWrapper>();
        for (TransactionUsageEntitlement tue : tues) {
            GrantInfoWrapper w = new GrantInfoWrapper();
            w.entitlementId = tue.Id;
            w.entitlementName = tue.Name;
            w.usageResourceId = tue.UsageResourceId;
            w.usageResourceName = resourceNames.get(tue.UsageResourceId);
            w.entitlementQuantity = tue.EntitlementQuantity;
            w.usageModelType = tue.UsageModelType;
            w.grantType = tue.GrantType;
            w.chargeForOverage = tue.ChargeForOverage;
            w.startDate = tue.EffectiveStartDateTime;
            w.endDate = tue.EffectiveEndDateTime;

            // Add bucket info if available
            UsageEntitlementBucket bucket = currentBucketByTue.get(tue.Id);
            if (bucket != null) {
                w.bucketBalance = bucket.BucketBalance;
                w.consumedEntitlement = bucket.ConsumedEntitlement != null ? bucket.ConsumedEntitlement : 0;
                w.totalConsumedEntitlement = bucket.TotalConsumedEntitlement != null ? bucket.TotalConsumedEntitlement : 0;
            }

            wrappers.add(w);
        }

        return wrappers;
    }
}