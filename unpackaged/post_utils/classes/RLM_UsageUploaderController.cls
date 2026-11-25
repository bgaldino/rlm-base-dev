/**
 * RLM_UsageUploaderController
 *
 * Apex controller for the rlmUsageUploader Lightning Web Component.
 * Provides methods to:
 *  - Load Usage Resources for an Asset (dynamically from its Product)
 *  - Upload single usage records as TransactionJournal entries
 *  - Bulk upload usage from parsed CSV data
 *  - Validate usage entries before committing
 *
 * Every failure the caller sees is a fixed sentence or the caller's own input; platform text goes
 * to the debug log, with two exceptions. A validation rule's or addError message on a refused
 * save is shown as written (see rowErrorText). An argument the platform cannot convert to the
 * declared type (a malformed id or date, a wrong-shaped entry) is refused before the method runs,
 * so its platform message, which echoes only the caller's own value, reaches the caller.
 */
public with sharing class RLM_UsageUploaderController {

    // ─── Constants ──────────────────────────────────────────────────────

    private static final String USAGE_TYPE_MANAGEMENT = 'UsageManagement';
    private static final String STATUS_PENDING = 'Pending';

    // Fixed sentences for failures whose own text can name objects, fields or record ids (a
    // user-mode query the caller lacks access for, a refused save). The detail goes to the debug
    // log. The sales representative persona holds RLM_UsageUploader, so these reach end users.
    @TestVisible
    private static final String ASSETS_LOAD_FAILED_MESSAGE =
        'The assets for this account could not be loaded. Refresh the page, or contact your administrator.';
    @TestVisible
    private static final String ASSET_NOT_FOUND_MESSAGE = 'This asset was not found, or you do not have access to it.';
    @TestVisible
    private static final String RESOURCE_NOT_FOUND_MESSAGE =
        'This usage resource was not found, or you do not have access to it.';
    @TestVisible
    private static final String RESOURCES_LOAD_FAILED_MESSAGE =
        'The usage resources for this asset could not be loaded. Refresh the page, or contact your administrator.';
    @TestVisible
    private static final String VALIDATE_FAILED_MESSAGE =
        'The usage entries could not be checked. Try again, or contact your administrator.';
    @TestVisible
    private static final String UPLOAD_FAILED_MESSAGE =
        'The usage record could not be uploaded. Try again, or contact your administrator.';
    @TestVisible
    private static final String BULK_UPLOAD_FAILED_MESSAGE =
        'The usage records could not be uploaded. Try again, or contact your administrator.';
    @TestVisible
    private static final String RATES_LOAD_FAILED_MESSAGE =
        'The rates for this asset could not be loaded. Refresh the page, or contact your administrator.';
    @TestVisible
    private static final String GRANTS_LOAD_FAILED_MESSAGE =
        'The grants for this asset could not be loaded. Refresh the page, or contact your administrator.';

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
        try {
            return loadAssetsForAccount(accountId);
        } catch (AuraHandledException e) {
            throw e;
        } catch (Exception e) {
            throw RLM_UtilsAuraErrors.failed(ASSETS_LOAD_FAILED_MESSAGE, 'RLM_UsageUploaderController.getAssetsForAccount', e);
        }
    }

    private static List<AssetOption> loadAssetsForAccount(Id accountId) {
        List<AssetOption> options = new List<AssetOption>();

        List<Asset> assets = [
            SELECT Id, Name, Product2.Name, Product2.UsageModelType
            FROM Asset
            WHERE AccountId = :accountId
              AND LifecycleStartDate <= TODAY
              AND LifecycleEndDate >= TODAY
              AND Product2.UsageModelType = 'Anchor'
            WITH USER_MODE
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
        try {
            return loadUsageResourcesForAsset(assetId);
        } catch (AuraHandledException e) {
            throw e;
        } catch (Exception e) {
            throw RLM_UtilsAuraErrors.failed(RESOURCES_LOAD_FAILED_MESSAGE, 'RLM_UsageUploaderController.getUsageResourcesForAsset', e);
        }
    }

    // The asset, read in user mode. No row (a wrong id, or one the caller cannot see) is a fixed
    // sentence, not the platform's "List has no rows" text.
    private static Asset readAsset(Id assetId) {
        List<Asset> assets = [
            SELECT Id, Product2Id, AccountId
            FROM Asset
            WHERE Id = :assetId
            WITH USER_MODE
            LIMIT 1
        ];
        if (assets.isEmpty()) {
            throw RLM_UtilsAuraErrors.handled(ASSET_NOT_FOUND_MESSAGE);
        }
        return assets[0];
    }

    private static List<UsageResourceWrapper> loadUsageResourcesForAsset(Id assetId) {
        return loadUsageResourcesForAsset(readAsset(assetId));
    }

    private static List<UsageResourceWrapper> loadUsageResourcesForAsset(Asset ast) {
        if (ast.Product2Id == null) {
            throw RLM_UtilsAuraErrors.handled('This asset is not associated with a product.');
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
            WITH USER_MODE
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
                WITH USER_MODE
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
        try {
            return saveUsage(assetId, usageResourceId, quantity, transactionDate, unitOfMeasureId);
        } catch (AuraHandledException e) {
            throw e;
        } catch (DmlException e) {
            // A refused save: a validation rule's or addError message is shown, anything else
            // becomes the fixed sentence (see saveErrorText).
            List<StatusCode> codes = new List<StatusCode>();
            List<String> messages = new List<String>();
            List<String> details = new List<String>();
            for (Integer i = 0; i < e.getNumDml(); i++) {
                codes.add(e.getDmlType(i));
                messages.add(e.getDmlMessage(i));
                details.add(e.getDmlType(i) + ' ' + e.getDmlFieldNames(i) + ': ' + e.getDmlMessage(i));
            }
            throw RLM_UtilsAuraErrors.handled(saveErrorText(codes, messages, details, 'uploadUsage'));
        } catch (Exception e) {
            // Not a refused save: a user-mode read the caller lacks access for, or the access check.
            throw RLM_UtilsAuraErrors.failed(UPLOAD_FAILED_MESSAGE, 'RLM_UsageUploaderController.uploadUsage', e);
        }
    }

    private static Id saveUsage(
        Id assetId,
        Id usageResourceId,
        Decimal quantity,
        Date transactionDate,
        Id unitOfMeasureId
    ) {
        if (!Schema.sObjectType.TransactionJournal.isCreateable()) {
            throw RLM_UtilsAuraErrors.handled('You do not have permission to create usage records.');
        }

        if (quantity == null || quantity <= 0) {
            throw RLM_UtilsAuraErrors.handled('Quantity must be greater than 0');
        }
        if (transactionDate == null) {
            throw RLM_UtilsAuraErrors.handled('Transaction date is required');
        }

        // Resolve the AccountId from the Asset
        Asset ast = readAsset(assetId);

        List<ProductUsageResource> purMatches = [
            SELECT Id
            FROM ProductUsageResource
            WHERE ProductId = :ast.Product2Id
              AND UsageResourceId = :usageResourceId
              AND Status = 'Active'
            WITH USER_MODE
            LIMIT 1
        ];
        if (purMatches.isEmpty()) {
            throw RLM_UtilsAuraErrors.handled('This usage resource is not available for the asset\'s product.');
        }

        List<UsageResource> resources = [
            SELECT Id, DefaultUnitOfMeasureId, UnitOfMeasureClassId
            FROM UsageResource
            WHERE Id = :usageResourceId
            WITH USER_MODE
            LIMIT 1
        ];
        if (resources.isEmpty()) {
            throw RLM_UtilsAuraErrors.handled(RESOURCE_NOT_FOUND_MESSAGE);
        }
        UsageResource ur = resources[0];

        // Determine which UoM to use and validate any client-provided UoM.
        Id resolvedUomId;
        if (unitOfMeasureId == null) {
            resolvedUomId = ur.DefaultUnitOfMeasureId;
        } else {
            List<UnitOfMeasure> candidates = [
                SELECT Id, Status, UnitOfMeasureClassId
                FROM UnitOfMeasure
                WHERE Id = :unitOfMeasureId
                  AND UnitOfMeasureClassId = :ur.UnitOfMeasureClassId
                WITH USER_MODE
                LIMIT 1
            ];
            if (candidates.isEmpty() || candidates[0].Status != 'Active') {
                throw RLM_UtilsAuraErrors.handled('The selected unit of measure is not valid for this usage resource.');
            }
            resolvedUomId = candidates[0].Id;
        }

        TransactionJournal tj = buildTransactionJournal(
            assetId,
            ast.AccountId,
            usageResourceId,
            quantity,
            transactionDate,
            resolvedUomId
        );

        SObjectAccessDecision accessDecision = Security.stripInaccessible(
            AccessType.CREATABLE,
            new List<TransactionJournal>{ tj }
        );
        TransactionJournal sanitized = (TransactionJournal) accessDecision.getRecords()[0];
        insert as user sanitized;
        return sanitized.Id;
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
        try {
            return checkUsageEntries(assetId, entries);
        } catch (AuraHandledException e) {
            throw e;
        } catch (Exception e) {
            throw RLM_UtilsAuraErrors.failed(VALIDATE_FAILED_MESSAGE, 'RLM_UsageUploaderController.validateUsageEntries', e);
        }
    }

    private static List<ValidationResult> checkUsageEntries(Id assetId, List<UsageEntry> entries) {
        return checkUsageEntries(readAsset(assetId), entries);
    }

    private static List<ValidationResult> checkUsageEntries(Asset ast, List<UsageEntry> entries) {
        if (entries == null) {
            entries = new List<UsageEntry>();
        }
        // Build a map of resource name → resource info for this asset
        List<UsageResourceWrapper> resources = loadUsageResourcesForAsset(ast);
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
        try {
            return saveUsageEntries(assetId, entries);
        } catch (AuraHandledException e) {
            throw e;
        } catch (Exception e) {
            throw RLM_UtilsAuraErrors.failed(BULK_UPLOAD_FAILED_MESSAGE, 'RLM_UsageUploaderController.bulkUploadUsage', e);
        }
    }

    private static BulkUploadResult saveUsageEntries(Id assetId, List<UsageEntry> entries) {
        BulkUploadResult result = new BulkUploadResult();
        result.journalIds = new List<Id>();
        result.errors = new List<String>();
        result.successCount = 0;
        result.errorCount = 0;

        if (entries == null) {
            entries = new List<UsageEntry>();
        }
        // Resolve AccountId from the Asset
        Asset ast = readAsset(assetId);

        // Defensive validation (client validates before calling, but server re-validates for security)
        List<ValidationResult> validations = checkUsageEntries(ast, entries);

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
            if (!Schema.sObjectType.TransactionJournal.isCreateable()) {
                throw RLM_UtilsAuraErrors.handled('You do not have permission to create usage records.');
            }

            SObjectAccessDecision accessDecision = Security.stripInaccessible(
                AccessType.CREATABLE,
                toInsert
            );
            List<TransactionJournal> sanitized = (List<TransactionJournal>) accessDecision.getRecords();
            Database.SaveResult[] saveResults = Database.insert(sanitized, false, AccessLevel.USER_MODE);
            for (Integer i = 0; i < saveResults.size(); i++) {
                if (saveResults[i].isSuccess()) {
                    result.successCount++;
                    result.journalIds.add(saveResults[i].getId());
                } else {
                    result.errorCount++;
                    result.errors.add('Row ' + (validIndices[i] + 1) + ': '
                        + rowErrorText(saveResults[i].getErrors(), validIndices[i] + 1));
                }
            }
        }

        return result;
    }

    @TestVisible
    private static final String ROW_SAVE_FAILED_MESSAGE =
        'This usage record could not be saved. Check the values and try again, or contact your administrator.';

    // Owner decision (todo 433, 2026-11-25): row errors already follow the user-facing standard below, with
    // one deliberate pass-through: a validation rule's or trigger addError's own text is shown as written.
    // The sales representative persona holds the uploader, so this reaches end users on purpose: that text was
    // written by the org's own administrators or developers for the person saving the record. Nothing else
    // from a save reaches them raw (the header names the argument-conversion text).
    //
    // The text for a usage record that failed to save. bulkUploadUsage returns it in
    // BulkUploadResult.errors and uploadUsage throws it to the caller. For a bulk upload the shipped
    // component toasts the counts (including when no row was saved) and writes the row errors to
    // the browser console; it toasts the single-upload message. But the method returns the text to
    // any caller, including a custom component, so it is held to the user-facing standard.
    //
    // FIELD_CUSTOM_VALIDATION_EXCEPTION is the status the platform gives both a validation rule's
    // message and the text a trigger passes to addError (both measured on a 264 org), so both are
    // shown as written: an administrator or developer wrote that text for the person
    // saving the record. A trigger that passes internal detail to addError would show it too; that
    // is the trigger author's choice, and it cannot be told apart here. Every other save error
    // becomes a fixed sentence, with the detail in the debug log. Measured for TransactionJournal on
    // a 264 org, those carry field labels, a refused picklist value and a record id ("Reference
    // Record ID: id value of incorrect type: <id>"); an unhandled trigger exception arrives as
    // CANNOT_INSERT_UPDATE_ACTIVATE_ENTITY with the trigger's name and line, and is hidden too.
    @TestVisible
    private static String rowErrorText(List<Database.Error> errors, Integer rowNumber) {
        List<StatusCode> codes = new List<StatusCode>();
        List<String> messages = new List<String>();
        List<String> details = new List<String>();
        for (Database.Error err : errors) {
            codes.add(err.getStatusCode());
            messages.add(err.getMessage());
            details.add(err.getStatusCode() + ' ' + err.getFields() + ': ' + err.getMessage());
        }
        return saveErrorText(codes, messages, details, 'row ' + rowNumber);
    }

    private static String saveErrorText(
        List<StatusCode> codes, List<String> messages, List<String> details, String context
    ) {
        List<String> shown = new List<String>();
        Boolean hidden = false;
        for (Integer i = 0; i < codes.size(); i++) {
            if (codes[i] == StatusCode.FIELD_CUSTOM_VALIDATION_EXCEPTION && String.isNotBlank(messages[i])) {
                shown.add(messages[i]);
            } else {
                hidden = true;
                System.debug(LoggingLevel.ERROR, 'RLM_UsageUploaderController ' + context + ' save failed: ' + details[i]);
            }
        }
        if (hidden || shown.isEmpty()) {
            shown.add(ROW_SAVE_FAILED_MESSAGE);
        }
        return String.join(shown, ' ');
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
        try {
            return loadRatesForAsset(assetId);
        } catch (AuraHandledException e) {
            throw e;
        } catch (Exception e) {
            throw RLM_UtilsAuraErrors.failed(RATES_LOAD_FAILED_MESSAGE, 'RLM_UsageUploaderController.getRatesForAsset', e);
        }
    }

    private static List<RateInfoWrapper> loadRatesForAsset(Id assetId) {
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
            WITH USER_MODE
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
            WITH USER_MODE
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
            SELECT Id, Name FROM UsageResource WHERE Id IN :usageResourceIds WITH USER_MODE
        ]) {
            resourceNames.put(ur.Id, ur.Name);
        }

        return buildRateInfoWrappers(arces, tiersByRce, resourceNames);
    }

    // Split out from getRatesForAsset so the transform can be unit-tested against
    // in-memory (uninserted) AssetRateCardEntry rows — the object is platform-derived
    // (createable = false) and only ever populated by the real order-to-asset
    // assetization pipeline, so a unit test cannot insert one to exercise this logic.
    @TestVisible
    private static List<RateInfoWrapper> buildRateInfoWrappers(
        List<AssetRateCardEntry> arces,
        Map<Id, List<RateAdjustmentByTier>> tiersByRce,
        Map<Id, String> resourceNames
    ) {
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
        try {
            return loadGrantsForAsset(assetId);
        } catch (AuraHandledException e) {
            throw e;
        } catch (Exception e) {
            throw RLM_UtilsAuraErrors.failed(GRANTS_LOAD_FAILED_MESSAGE, 'RLM_UsageUploaderController.getGrantsForAsset', e);
        }
    }

    private static List<GrantInfoWrapper> loadGrantsForAsset(Id assetId) {
        List<TransactionUsageEntitlement> tues = [
            SELECT Id,
                   Name,
                   AssetId,
                   ProductId,
                   UsageResourceId,
                   EntitlementQuantity,
                   TransactionQuantity,
                   NetQuantity,
                   EffectiveStartDateTime,
                   EffectiveEndDateTime,
                   UsageModelType,
                   GrantType
            FROM TransactionUsageEntitlement
            WHERE AssetId = :assetId
            WITH USER_MODE
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
            SELECT Id, Name FROM UsageResource WHERE Id IN :usageResourceIds WITH USER_MODE
        ]) {
            resourceNames.put(ur.Id, ur.Name);
        }

        // Overage chargeability is no longer readable from the entitlement: 264 removed
        // TransactionUsageEntitlement.ChargeForOverage (along with DrawdownOrder,
        // RatingFrequencyPolicyId and UsageAggregationPolicyId), leaving no overage field or
        // policy lookup on the object, so it must come from the governing UsageOveragePolicy
        // by way of ProductUsageResourcePolicy. See OverageLookup for the resolution order
        // and why the resource, not just the product-resource pair, has to be consulted.
        OverageLookup overage = loadOverageLookup(usageResourceIds);

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
            WITH USER_MODE
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
            w.chargeForOverage = overage.resolve(tue.ProductId, tue.UsageResourceId);
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

    /**
     * Loads the overage policies governing a set of usage resources.
     *
     * Deliberately NOT filtered to the entitlements' own products: the policy that governs a
     * Pack or Commit entitlement belongs to the resource's Anchor product, which is usually
     * not among them. See OverageLookup for the resolution order.
     *
     * The parent association IS filtered to Active, matching the resource lookup above. A
     * reloaded dataset leaves Draft PURs carrying PURP children that overlap the Active row
     * until activateRatingRecords step 2.5a clears them, and an obsolete policy read from one
     * would not merely be stale — a disagreeing value trips the ambiguity guard and blanks the
     * Active answer. ProductUsageResourcePolicy has no status of its own, so the parent is the
     * only gate available.
     */
    @TestVisible
    private static OverageLookup loadOverageLookup(Set<Id> usageResourceIds) {
        OverageLookup lookup = new OverageLookup();
        if (usageResourceIds == null || usageResourceIds.isEmpty()) {
            return lookup;
        }
        try {
            for (ProductUsageResourcePolicy purp : [
                SELECT ProductUsageResource.ProductId,
                       ProductUsageResource.UsageResourceId,
                       UsageOveragePolicy.OverageChargeable
                FROM ProductUsageResourcePolicy
                WHERE ProductUsageResource.UsageResourceId IN :usageResourceIds
                  AND ProductUsageResource.Status = 'Active'
                  AND UsageOveragePolicyId != null
                WITH USER_MODE
            ]) {
                lookup.add(
                    purp.ProductUsageResource.ProductId,
                    purp.ProductUsageResource.UsageResourceId,
                    purp.UsageOveragePolicy.OverageChargeable
                );
            }
        } catch (QueryException e) {
            // USER_MODE throws when the caller lacks read on the policy chain, and nothing in
            // this repo grants ProductUsageResourcePolicy or UsageOveragePolicy outside RLM_UsageUploader (and RLM_USG). Rates and
            // grants are the point of this screen, so a missing grant on one optional column
            // must not fail the whole wire: degrade to blank, exactly as an absent policy does.
            return new OverageLookup();
        }
        return lookup;
    }

    /**
     * Resolves an entitlement's overage chargeability from the product usage resource policies.
     *
     * Only an Anchor product's policy row may carry a UsageOveragePolicy — the platform rejects
     * it on Pack and on Commit products — so overage is an anchor-level property of the
     * *resource*, and a Pack or Commit entitlement has no policy row under its own product.
     * Resolution order follows from that:
     *
     *   1. the entitlement's own product+resource row, when it has one (the Anchor case);
     *   2. otherwise the resource's row, when exactly one overage value governs the resource;
     *   3. otherwise null.
     *
     * Step 2 is what keeps a Pack or Commit grant showing the Yes/No the customer is actually
     * subject to; without it every non-Anchor entitlement renders blank. Step 3 covers the two
     * ways the answer is genuinely unknown — two Anchors disagreeing about one resource, or two
     * selling-model rows disagreeing about one product+resource pair. Both are schema-legal, and
     * a plausible-looking guess on a screen an end user trusts is worse than a blank.
     */
    @TestVisible
    private class OverageLookup {
        private Map<String, String> byProductResource = new Map<String, String>();
        private Set<String> conflictingPairs = new Set<String>();
        private Map<Id, String> byResource = new Map<Id, String>();
        private Set<Id> conflictingResources = new Set<Id>();

        @TestVisible
        private void add(Id productId, Id usageResourceId, String overageChargeable) {
            if (usageResourceId == null) {
                return;
            }

            String pair = productId == null ? null : productId + '|' + usageResourceId;
            if (pair != null && !conflictingPairs.contains(pair)) {
                if (!byProductResource.containsKey(pair)) {
                    byProductResource.put(pair, overageChargeable);
                } else if (byProductResource.get(pair) != overageChargeable) {
                    conflictingPairs.add(pair);
                    byProductResource.remove(pair);
                }
            }

            if (conflictingResources.contains(usageResourceId)) {
                return;
            }
            if (!byResource.containsKey(usageResourceId)) {
                byResource.put(usageResourceId, overageChargeable);
            } else if (byResource.get(usageResourceId) != overageChargeable) {
                conflictingResources.add(usageResourceId);
                byResource.remove(usageResourceId);
            }
        }

        @TestVisible
        private String resolve(Id productId, Id usageResourceId) {
            if (productId != null) {
                String pair = productId + '|' + usageResourceId;
                if (conflictingPairs.contains(pair)) {
                    return null;
                }
                if (byProductResource.containsKey(pair)) {
                    return byProductResource.get(pair);
                }
            }
            return byResource.get(usageResourceId);
        }
    }
}