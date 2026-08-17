/**
 * Phase 4 - Shipment-gated billing + serialized product model.
 *
 * Requirement: a software subscription bundled with physical hardware must not
 * begin active billing until a shipment confirmation / serial-number mapping
 * event is received. There is no live Oracle EBS integration here - the event is
 * simulated by a record-page quick action (rlmConfirmShipment) that calls
 * confirmShipment().
 *
 * Model:
 *   - Billing hold: the software children of a one-time-hardware bundle carry
 *     Asset.RLM_Asset_Status__c = 'BillingHeld' until the hardware ships.
 *   - Serialized product: the native SerializedProduct object is the canonical
 *     per-unit serial record (SerialNumber + Product2Id + Status). The shipment
 *     event creates one SerializedProduct per shipped unit (Status 'Sent'), links
 *     it to the shipped Asset via the custom RLM_Asset__c lookup (the standard
 *     AssetId triggers a broken managed automation in this edition), and mirrors
 *     the first serial onto Asset.SerialNumber for search.
 *   - Release: on shipment the hardware Asset.Status flips to native 'Shipped',
 *     the software children go 'Active' with RLM_Billing_Start_Date__c = shipment
 *     date, and the real billing lever is set to the shipment date.
 *
 * Billing lever: the surgical, per-software-asset lever is
 * BillingScheduleGroup.NextBillingDateOverride. That group's ReferenceEntityId
 * points directly at the Asset, so we move the override on the held software's own
 * group(s) - defer the next bill as far as legally allowed while held, then pull
 * it back to the shipment date on release. Live-verified constraint: the platform
 * rejects any override on/after the group's own EndDate ("Select a next billing
 * date override that's before the end date..."), so setGroupOverride() clamps the
 * held date to EndDate - 1 (the deepest legal hold) rather than an unbounded
 * far-future sentinel. The override field is writeable and persists; the group's
 * EffectiveNextBillingDate rollup recomputes on the billing engine's own cycle
 * (at invoice time), not synchronously. It is engine-owned data, so we read/write
 * it in system mode (no BillingScheduleGroup grant needed in the feature
 * permission set) and it is non-fatal: a demo asset whose order has not yet
 * generated billing simply has no group to move - the definitive visible gate
 * remains Asset.RLM_Asset_Status__c / RLM_Billing_Start_Date__c.
 *
 * "Software bundled with hardware" = an asset whose bundle family root is a
 * ONE-TIME product and whose own product carries a TermDefined/Evergreen selling
 * model. RLM_AssetBillingHoldHandler applies the same classification to put such
 * assets on hold automatically the moment they are created.
 */
public with sharing class RLM_ShipmentFulfillmentService {

    private static final String STATUS_HELD    = 'BillingHeld';
    private static final String STATUS_ACTIVE  = 'Active';
    private static final String ASSET_SHIPPED  = 'Shipped';
    private static final String SP_STATUS_SENT = 'Sent';
    private static final Set<String> SUBSCRIPTION_MODELS = new Set<String>{ 'TermDefined', 'Evergreen' };
    private static final Set<String> ONE_TIME_MODELS     = new Set<String>{ 'OneTime' };

    // Sentinel expressing "hold as long as the platform allows" for
    // BillingScheduleGroup.NextBillingDateOverride while a software line is held
    // ("do not bill until shipment"). The platform rejects any override on/after
    // the group's own EndDate, so setGroupOverride() clamps this to EndDate - 1
    // per group (defer the next bill to the last legal day of the term). Replaced
    // with the real shipment date on release.
    private static final Date HELD_UNTIL = Date.newInstance(2999, 12, 31);

    // ------------------------------------------------------------------
    // View models
    // ------------------------------------------------------------------
    public class FulfillmentView {
        @AuraEnabled public Id hardwareAssetId;
        @AuraEnabled public String hardwareName;
        @AuraEnabled public String hardwareProductName;
        @AuraEnabled public Boolean isOneTimeHardware = false;
        @AuraEnabled public Boolean isSerialized = false;  // Product2.IsSerialized
        @AuraEnabled public String hardwareStatus;         // native Asset.Status
        @AuraEnabled public Decimal expectedUnits;         // hardware Quantity
        @AuraEnabled public Integer existingSerialCount = 0;
        @AuraEnabled public Integer softwareHeldCount = 0;
        @AuraEnabled public List<SoftwareLine> software = new List<SoftwareLine>();
    }

    public class SoftwareLine {
        @AuraEnabled public Id assetId;
        @AuraEnabled public String assetName;
        @AuraEnabled public String productName;
        @AuraEnabled public String status;               // RLM_Asset_Status__c
        @AuraEnabled public String billingStartDate;     // ISO or null
        @AuraEnabled public String billingHeldUntil;     // BillingScheduleGroup.NextBillingDateOverride (ISO) or null
    }

    public class FulfillmentResult {
        @AuraEnabled public Boolean isSuccess = true;
        @AuraEnabled public Integer serializedCreated = 0;
        @AuraEnabled public Integer softwareHeld = 0;
        @AuraEnabled public Integer softwareReleased = 0;
        @AuraEnabled public Integer billingSchedulesUpdated = 0;
        // Draft StartDateAdjustment amendment quote created on shipment to
        // re-anchor the subscription term to the ship date (null when the bundle
        // was not future-dated, so no re-anchor was needed). The rep reviews and
        // activates it; activation regenerates the billing schedule.
        @AuraEnabled public Id amendmentQuoteId;
        @AuraEnabled public List<String> messages = new List<String>();
    }

    // ------------------------------------------------------------------
    // Read (quick-action state)
    // ------------------------------------------------------------------
    @AuraEnabled(cacheable=true)
    public static FulfillmentView getBundleFulfillment(Id hardwareAssetId) {
        FulfillmentView v = new FulfillmentView();
        if (hardwareAssetId == null) return v;
        Id hwId = Id.valueOf(hardwareAssetId);

        List<Asset> hw = [
            SELECT Id, Name, Quantity, Status, Product2Id, Product2.Name, Product2.IsSerialized,
                   RootAssetId, ParentId
            FROM Asset WHERE Id = :hwId WITH USER_MODE LIMIT 1
        ];
        if (hw.isEmpty()) return v;
        Asset hardware = hw[0];
        v.hardwareAssetId = hardware.Id;
        v.hardwareName = hardware.Name;
        v.hardwareProductName = (hardware.Product2 != null) ? hardware.Product2.Name : null;
        v.isSerialized = (hardware.Product2 != null && hardware.Product2.IsSerialized == true);
        v.hardwareStatus = hardware.Status;
        v.expectedUnits = hardware.Quantity;

        List<Asset> family = familyOf(hardware);
        Set<Id> prodIds = new Set<Id>();
        for (Asset a : family) if (a.Product2Id != null) prodIds.add(a.Product2Id);
        Map<Id, Set<String>> modelsByProduct = sellingModelTypesByProduct(prodIds);

        v.isOneTimeHardware = hasAny(modelsByProduct.get(hardware.Product2Id), ONE_TIME_MODELS);

        for (Asset a : family) {
            if (a.Id == hardware.Id) continue;
            if (!hasAny(modelsByProduct.get(a.Product2Id), SUBSCRIPTION_MODELS)) continue;
            SoftwareLine s = new SoftwareLine();
            s.assetId = a.Id;
            s.assetName = a.Name;
            s.productName = (a.Product2 != null) ? a.Product2.Name : null;
            s.status = a.RLM_Asset_Status__c;
            s.billingStartDate = isoDate(a.RLM_Billing_Start_Date__c);
            if (a.RLM_Asset_Status__c == STATUS_HELD) v.softwareHeldCount++;
            v.software.add(s);
        }

        // Reflect the real billing lever (the software's own BillingScheduleGroup
        // override) so the UI shows whether billing is actually deferred, not just
        // the status flag. Engine-owned data - read in system mode.
        Set<Id> swIds = new Set<Id>();
        for (SoftwareLine s : v.software) swIds.add(s.assetId);
        if (!swIds.isEmpty()) {
            Map<Id, Date> overrideByAsset = new Map<Id, Date>();
            for (BillingScheduleGroup g : [
                SELECT ReferenceEntityId, NextBillingDateOverride
                FROM BillingScheduleGroup
                WHERE ReferenceEntityId IN :swIds AND NextBillingDateOverride != null
            ]) {
                overrideByAsset.put(g.ReferenceEntityId, g.NextBillingDateOverride);
            }
            for (SoftwareLine s : v.software) {
                s.billingHeldUntil = isoDate(overrideByAsset.get(s.assetId));
            }
        }

        v.existingSerialCount = [
            SELECT COUNT() FROM SerializedProduct WHERE RLM_Asset__c = :hardware.Id WITH USER_MODE
        ];
        return v;
    }

    // ------------------------------------------------------------------
    // Hold (demo setup) - put the bundle's software on billing hold
    // ------------------------------------------------------------------
    @AuraEnabled
    public static FulfillmentResult holdBillingForBundle(List<Id> assetIds) {
        FulfillmentResult res = new FulfillmentResult();
        if (assetIds == null || assetIds.isEmpty()) {
            res.isSuccess = false;
            res.messages.add('Select at least one asset.');
            return res;
        }
        Set<Id> ids = new Set<Id>();
        for (Id raw : assetIds) ids.add(Id.valueOf(raw));

        List<Asset> anchors = [
            SELECT Id, Product2Id, RootAssetId, ParentId FROM Asset WHERE Id IN :ids WITH USER_MODE
        ];
        // Slim update records (Id + changed fields only) so user-mode DML does not
        // enforce FLS on the read-only fields the SELECT also loaded (AccountId,
        // Product2Id, etc.).
        Map<Id, Asset> softwareToHold = new Map<Id, Asset>();
        for (Asset anchor : anchors) {
            for (Asset sw : subscriptionChildren(anchor)) {
                if (sw.RLM_Asset_Status__c != STATUS_HELD && !softwareToHold.containsKey(sw.Id)) {
                    softwareToHold.put(sw.Id, new Asset(
                        Id = sw.Id,
                        RLM_Asset_Status__c = STATUS_HELD,
                        RLM_Billing_Start_Date__c = null
                    ));
                }
            }
        }
        if (!softwareToHold.isEmpty()) {
            update as user softwareToHold.values();
            // Engage the real billing lever on the held software's own group(s).
            res.billingSchedulesUpdated = setGroupOverride(softwareToHold.keySet(), HELD_UNTIL, res);
        }
        res.softwareHeld = softwareToHold.size();
        res.messages.add(res.softwareHeld + ' software line(s) placed on billing hold pending shipment.');
        return res;
    }

    // ------------------------------------------------------------------
    // Confirm shipment (simulated EBS event)
    //   serialize + ship + release billing + re-anchor subscription start
    // ------------------------------------------------------------------
    @AuraEnabled
    public static FulfillmentResult confirmShipment(
        Id hardwareAssetId,
        List<String> serialNumbers,
        Date shipmentDate
    ) {
        FulfillmentResult res = new FulfillmentResult();
        if (hardwareAssetId == null) {
            res.isSuccess = false;
            res.messages.add('No hardware asset specified.');
            return res;
        }
        Date shipDate = (shipmentDate == null) ? Date.today() : shipmentDate;
        Id hwId = Id.valueOf(hardwareAssetId);

        List<Asset> hw = [
            SELECT Id, AccountId, Product2Id, Product2.IsSerialized, Status, SerialNumber,
                   RootAssetId, ParentId, Quantity
            FROM Asset WHERE Id = :hwId WITH USER_MODE LIMIT 1
        ];
        if (hw.isEmpty()) {
            res.isSuccess = false;
            res.messages.add('Asset not found or not accessible.');
            return res;
        }
        Asset hardware = hw[0];
        Boolean isSerialized = (hardware.Product2 != null && hardware.Product2.IsSerialized == true);

        // 1. Serialize: one native SerializedProduct per shipped unit.
        List<String> serials = new List<String>();
        if (serialNumbers != null) {
            for (String s : serialNumbers) {
                if (String.isNotBlank(s)) serials.add(s.trim());
            }
        }
        if (!serials.isEmpty() && !isSerialized) {
            res.messages.add(
                'Serial numbers were provided but the hardware product is not marked serialized ' +
                '(Product2.IsSerialized). Skipping serial records; hardware still marked shipped and ' +
                'software still released.'
            );
        }
        if (!serials.isEmpty() && isSerialized && hardware.Product2Id != null) {
            // Link each serial to the shipped asset via the custom RLM_Asset__c
            // lookup. The standard SerializedProduct.AssetId cannot be used: a
            // managed platform automation fires on AssetId and references
            // Asset.ProductItemId (absent in this edition), which fails the write.
            // Setting a custom lookup on insert does not trigger that automation,
            // so the serial-to-asset link is reliable and visible on the asset.
            List<SerializedProduct> sps = new List<SerializedProduct>();
            for (String s : serials) {
                sps.add(new SerializedProduct(
                    Product2Id   = hardware.Product2Id,
                    SerialNumber = s,
                    Status       = SP_STATUS_SENT,
                    RLM_Asset__c = hardware.Id
                ));
            }
            insert as user sps;
            res.serializedCreated = sps.size();
        }

        // 2. Ship the hardware (native lifecycle status) + mirror first serial.
        //    Slim update so user-mode DML only checks FLS on the changed fields.
        Asset hwUpdate = new Asset(Id = hardware.Id, Status = ASSET_SHIPPED);
        if (!serials.isEmpty() && String.isBlank(hardware.SerialNumber)) {
            hwUpdate.SerialNumber = serials[0];
        }
        update as user new List<Asset>{ hwUpdate };

        // 3. Release the bundle's software from billing hold as of the ship date.
        List<Asset> toRelease = new List<Asset>();      // slim (Id + changed)
        List<Asset> releasedFull = new List<Asset>();   // full records (Ids feed the group override)
        for (Asset sw : subscriptionChildren(hardware)) {
            if (sw.RLM_Asset_Status__c == STATUS_HELD) {
                toRelease.add(new Asset(
                    Id = sw.Id,
                    RLM_Asset_Status__c = STATUS_ACTIVE,
                    RLM_Billing_Start_Date__c = shipDate
                ));
                releasedFull.add(sw);
            }
        }
        if (!toRelease.isEmpty()) {
            update as user toRelease;
            res.softwareReleased = toRelease.size();
            Set<Id> releasedIds = new Set<Id>();
            for (Asset a : releasedFull) releasedIds.add(a.Id);
            res.billingSchedulesUpdated = setGroupOverride(releasedIds, shipDate, res);
        }

        // 4. Re-anchor the subscription term to the ship date (revenue-correct).
        //    Only when the bundle is still future-dated (not yet started): the
        //    native StartDateAdjustment amendment requires a lifecycle start after
        //    today, must target the TOP-LEVEL asset (components can't be amended
        //    alone), and cascades the new start to every line. It produces a DRAFT
        //    amendment quote for the rep to review + activate; that activation is
        //    what regenerates the billing schedule from the ship date. The interim
        //    override above keeps billing deferred until then. Best-effort: a
        //    re-anchor miss is surfaced as a message, not a hard failure - the
        //    shipment itself (serials, status, release) already succeeded.
        Id rootId = (hardware.RootAssetId != null) ? hardware.RootAssetId : hardware.Id;
        List<Asset> roots = [
            SELECT Id, LifecycleStartDate FROM Asset WHERE Id = :rootId WITH USER_MODE LIMIT 1
        ];
        if (!roots.isEmpty() && roots[0].LifecycleStartDate != null
                && roots[0].LifecycleStartDate > System.now()) {
            RLM_AssetOrderingService.ConsolidationResult amend =
                RLM_AssetOrderingService.reanchorStartDate(rootId, shipDate);
            if (amend != null && amend.isSuccess && amend.outputRecordId != null) {
                res.amendmentQuoteId = amend.outputRecordId;
                res.messages.add(
                    'Start-date amendment quote created to re-anchor the subscription term to ' +
                    isoDate(shipDate) + '. Review and activate it to regenerate billing from the ship date.'
                );
            } else {
                res.messages.add(
                    'Start-date re-anchor amendment was not created' +
                    (amend == null || amend.messages.isEmpty() ? '.' : ': ' + String.join(amend.messages, '; '))
                );
            }
        } else {
            res.messages.add(
                'Bundle already started (not future-dated), so no start-date re-anchor was needed; ' +
                'billing was released to the ship date via the billing override.'
            );
        }

        res.messages.add(
            'Shipment confirmed: ' + res.serializedCreated + ' serialized unit(s) mapped, hardware marked Shipped, ' +
            res.softwareReleased + ' software line(s) released to bill from ' + isoDate(shipDate) + '.'
        );
        return res;
    }

    // ------------------------------------------------------------------
    // Helpers
    // ------------------------------------------------------------------

    /** All assets in the bundle family of the given anchor (root + descendants). */
    private static List<Asset> familyOf(Asset anchor) {
        Set<Id> keys = new Set<Id>{ anchor.Id };
        if (anchor.RootAssetId != null) keys.add(anchor.RootAssetId);
        if (anchor.ParentId != null) keys.add(anchor.ParentId);
        return [
            SELECT Id, Name, AccountId, Product2Id, Product2.Name, RLM_Asset_Status__c,
                   RLM_Billing_Start_Date__c, ParentId, RootAssetId
            FROM Asset
            WHERE Id IN :keys OR ParentId IN :keys OR RootAssetId IN :keys
            WITH USER_MODE
        ];
    }

    /** Subscription (software) members of the anchor's bundle family. */
    private static List<Asset> subscriptionChildren(Asset anchor) {
        List<Asset> family = familyOf(anchor);
        Set<Id> prodIds = new Set<Id>();
        for (Asset a : family) if (a.Product2Id != null) prodIds.add(a.Product2Id);
        Map<Id, Set<String>> modelsByProduct = sellingModelTypesByProduct(prodIds);
        List<Asset> out = new List<Asset>();
        for (Asset a : family) {
            if (a.Id == anchor.Id) continue;
            if (hasAny(modelsByProduct.get(a.Product2Id), SUBSCRIPTION_MODELS)) out.add(a);
        }
        return out;
    }

    private static Map<Id, Set<String>> sellingModelTypesByProduct(Set<Id> prodIds) {
        Map<Id, Set<String>> m = new Map<Id, Set<String>>();
        if (prodIds == null || prodIds.isEmpty()) return m;
        for (ProductSellingModelOption o : [
            SELECT Product2Id, ProductSellingModel.SellingModelType
            FROM ProductSellingModelOption
            WHERE Product2Id IN :prodIds AND ProductSellingModel.SellingModelType != null
            WITH USER_MODE
        ]) {
            if (!m.containsKey(o.Product2Id)) m.put(o.Product2Id, new Set<String>());
            m.get(o.Product2Id).add(o.ProductSellingModel.SellingModelType);
        }
        return m;
    }

    private static Boolean hasAny(Set<String> have, Set<String> wanted) {
        if (have == null) return false;
        for (String w : wanted) if (have.contains(w)) return true;
        return false;
    }

    /** Put the given software assets' billing group(s) on hold (far-future). */
    public static Integer holdBillingGroups(Set<Id> softwareAssetIds) {
        return setGroupOverride(softwareAssetIds, HELD_UNTIL, null);
    }

    /**
     * Surgical, per-software-asset billing hold/release using the real billing
     * object. BillingScheduleGroup.ReferenceEntityId points at the Asset, so we
     * set NextBillingDateOverride precisely on the held software's own group(s):
     *   - hold:    overrideDate = HELD_UNTIL (far-future = "not until shipment")
     *   - release: overrideDate = the shipment date
     * Engine-owned object, so we read/write in system mode (no BillingScheduleGroup
     * grant needed in the feature permission set). Non-fatal: an asset whose order
     * has not yet generated billing has no group to move - the visible gate remains
     * the asset fields.
     */
    private static Integer setGroupOverride(Set<Id> softwareAssetIds, Date overrideDate, FulfillmentResult res) {
        if (softwareAssetIds == null || softwareAssetIds.isEmpty()) return 0;
        try {
            List<BillingScheduleGroup> groups = [
                SELECT Id, EndDate, NextBillingDateOverride
                FROM BillingScheduleGroup
                WHERE ReferenceEntityId IN :softwareAssetIds
            ];
            List<BillingScheduleGroup> toUpdate = new List<BillingScheduleGroup>();
            for (BillingScheduleGroup g : groups) {
                // NextBillingDateOverride must fall strictly before the group's
                // EndDate. Clamp the requested date (the HELD_UNTIL far-future
                // sentinel on hold, or the shipment date on release) so the write
                // is always accepted: the deepest legal hold is EndDate - 1.
                Date target = overrideDate;
                if (g.EndDate != null && target != null && target >= g.EndDate) {
                    target = g.EndDate.addDays(-1);
                }
                if (target != null && g.NextBillingDateOverride != target) {
                    toUpdate.add(new BillingScheduleGroup(
                        Id = g.Id,
                        NextBillingDateOverride = target
                    ));
                }
            }
            if (toUpdate.isEmpty()) return 0;
            update as system toUpdate;
            return toUpdate.size();
        } catch (Exception ex) {
            if (res != null) {
                res.messages.add('Billing group override skipped: ' + ex.getTypeName() + ': ' + ex.getMessage());
            }
            return 0;
        }
    }

    private static String isoDate(Date d) {
        return (d == null) ? null
            : d.year() + '-' + lp(d.month()) + '-' + lp(d.day());
    }
    private static String lp(Integer n) {
        return (n < 10) ? '0' + n : String.valueOf(n);
    }
}
