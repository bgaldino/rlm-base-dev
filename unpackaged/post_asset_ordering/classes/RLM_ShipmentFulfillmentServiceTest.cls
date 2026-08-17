/**
 * Tests for RLM_ShipmentFulfillmentService (Phase 4 shipment-gated billing +
 * serialized product model). Seeds a one-time hardware bundle parent with a
 * subscription software child, then exercises hold -> confirm-shipment.
 *
 * Note: the RLM_AssetBillingHold trigger auto-holds the subscription child at
 * creation (born-held), so the seeded software is already 'BillingHeld' before any
 * explicit hold call - the assertions below reflect that.
 *
 * BillingScheduleGroup is engine-generated (no real group in a unit test), so the
 * NextBillingDateOverride lever is covered by its safe no-op branch.
 *
 * The shipment re-anchor (StartDateAdjustment amendment on a future-dated bundle)
 * invokes a native standard action, so it is covered through
 * RLM_AssetOrderingService's @TestVisible mockOutcome seam; the not-future-dated
 * path is covered by the default (skip) branch.
 */
@isTest
private class RLM_ShipmentFulfillmentServiceTest {

    private static Id hardwareAssetId;
    private static Id softwareAssetId;

    /**
     * The service DMLs run "as user"/USER_MODE, so the running user needs the
     * feature permission set for FLS on the custom Asset fields (notably the newly
     * deployed RLM_Billing_Start_Date__c). Assigning is isolated in runAs to avoid
     * MIXED_DML with the seeded (non-setup) records.
     */
    private static void grantPermset() {
        PermissionSet ps = [SELECT Id FROM PermissionSet WHERE Name = 'RLM_AssetBasedOrdering' LIMIT 1];
        System.runAs(new User(Id = UserInfo.getUserId())) {
            Integer already = [
                SELECT COUNT() FROM PermissionSetAssignment
                WHERE AssigneeId = :UserInfo.getUserId() AND PermissionSetId = :ps.Id
            ];
            if (already == 0) {
                insert new PermissionSetAssignment(
                    AssigneeId = UserInfo.getUserId(), PermissionSetId = ps.Id
                );
            }
        }
    }

    private static void seedBundle() {
        Account acct = new Account(Name = 'Ship Test Co');
        insert acct;

        Product2 hw = new Product2(Name = 'F5 Chassis (HW)', ProductCode = 'HW-CHASSIS', IsActive = true, IsSerialized = true);
        Product2 sw = new Product2(Name = 'F5 LTM Software', ProductCode = 'SW-LTM', IsActive = true);
        insert new List<Product2>{ hw, sw };

        ProductSellingModel oneTime = new ProductSellingModel(
            Name = 'One-Time', SellingModelType = 'OneTime', Status = 'Active'
        );
        ProductSellingModel term = new ProductSellingModel(
            Name = 'Term Monthly', SellingModelType = 'TermDefined', Status = 'Active',
            PricingTerm = 1, PricingTermUnit = 'Months'
        );
        insert new List<ProductSellingModel>{ oneTime, term };

        insert new List<ProductSellingModelOption>{
            new ProductSellingModelOption(Product2Id = hw.Id, ProductSellingModelId = oneTime.Id),
            new ProductSellingModelOption(Product2Id = sw.Id, ProductSellingModelId = term.Id)
        };

        Asset hwAsset = new Asset(
            Name = 'Chassis Unit', AccountId = acct.Id, Product2Id = hw.Id,
            Quantity = 1, Status = 'Purchased', HasLifecycleManagement = true,
            RLM_Asset_Status__c = 'Active'
        );
        insert hwAsset;

        Asset swAsset = new Asset(
            Name = 'LTM License', AccountId = acct.Id, Product2Id = sw.Id,
            Quantity = 1, ParentId = hwAsset.Id, HasLifecycleManagement = true,
            RLM_Asset_Status__c = 'Active'
        );
        insert swAsset;

        hardwareAssetId = hwAsset.Id;
        softwareAssetId = swAsset.Id;
    }

    @isTest
    static void getBundleFulfillment_classifiesHardwareAndSoftware() {
        grantPermset();
        seedBundle();
        Test.startTest();
        RLM_ShipmentFulfillmentService.FulfillmentView v =
            RLM_ShipmentFulfillmentService.getBundleFulfillment(hardwareAssetId);
        Test.stopTest();

        System.assertEquals(true, v.isOneTimeHardware, 'Parent should be one-time hardware');
        System.assertEquals(1, v.software.size(), 'Should find one software child');
        // The RLM_AssetBillingHold trigger auto-holds the subscription child of a
        // one-time hardware bundle the moment it is created (born-held), so it is
        // already on hold here without an explicit holdBillingForBundle call.
        System.assertEquals(1, v.softwareHeldCount, 'Software auto-held on creation');
    }

    @isTest
    static void holdThenConfirm_releasesBillingAndSerializes() {
        grantPermset();
        seedBundle();
        // Born-held: the trigger already placed the subscription child on hold at
        // creation, so the explicit hold is idempotent (nothing new to hold).
        Asset swAfterSeed = [SELECT RLM_Asset_Status__c FROM Asset WHERE Id = :softwareAssetId];
        System.assertEquals('BillingHeld', swAfterSeed.RLM_Asset_Status__c, 'Software auto-held on creation');

        Test.startTest();
        RLM_ShipmentFulfillmentService.FulfillmentResult held =
            RLM_ShipmentFulfillmentService.holdBillingForBundle(new List<Id>{ hardwareAssetId });
        System.assertEquals(0, held.softwareHeld, 'Already auto-held; explicit hold is idempotent');
        System.assertEquals(true, held.isSuccess, 'Idempotent hold still succeeds');

        Date shipDate = Date.today();
        RLM_ShipmentFulfillmentService.FulfillmentResult res =
            RLM_ShipmentFulfillmentService.confirmShipment(
                hardwareAssetId, new List<String>{ 'SN-001' }, shipDate
            );
        Test.stopTest();

        System.assertEquals(true, res.isSuccess, 'confirmShipment should succeed');
        System.assertEquals(1, res.serializedCreated, 'One serialized product created');
        System.assertEquals(1, res.softwareReleased, 'One software line released');

        Asset hw = [SELECT Status, SerialNumber FROM Asset WHERE Id = :hardwareAssetId];
        System.assertEquals('Shipped', hw.Status, 'Hardware should be Shipped');
        System.assertEquals('SN-001', hw.SerialNumber, 'First serial mirrored to Asset');

        Asset sw = [SELECT RLM_Asset_Status__c, RLM_Billing_Start_Date__c FROM Asset WHERE Id = :softwareAssetId];
        System.assertEquals('Active', sw.RLM_Asset_Status__c, 'Software released to Active');
        System.assertEquals(shipDate, sw.RLM_Billing_Start_Date__c, 'Billing start stamped to ship date');

        // Serial is linked to the shipped asset via the custom RLM_Asset__c lookup
        // (the standard AssetId triggers a broken managed automation in this edition).
        List<SerializedProduct> sps = [
            SELECT SerialNumber, Status, RLM_Asset__c
            FROM SerializedProduct WHERE RLM_Asset__c = :hardwareAssetId
        ];
        System.assertEquals(1, sps.size(), 'SerializedProduct linked to the shipped asset');
        System.assertEquals('SN-001', sps[0].SerialNumber, 'Serial number persisted');
        System.assertEquals('Sent', sps[0].Status, 'Serial status Sent');
    }

    @isTest
    static void confirmShipment_futureDatedBundle_createsReanchorAmendment() {
        grantPermset();
        seedBundle();
        // Future-date the bundle root so the re-anchor path engages (the native
        // StartDateAdjustment requires a lifecycle start after today).
        update new Asset(
            Id = hardwareAssetId,
            LifecycleStartDate = System.now().addDays(30),
            LifecycleEndDate = System.now().addDays(395)
        );
        // Mock the native amendment outcome (no live standard action in tests).
        // The stand-in output id is an Asset id, not a real Quote - that is fine:
        // neutralizeOneTimeDates no-ops on any non-Quote/Order type, and the test
        // only asserts the id is threaded back onto the result.
        RLM_AssetOrderingService.ActionOutcome mock = new RLM_AssetOrderingService.ActionOutcome();
        mock.isSuccess = true;
        mock.outputRecordId = hardwareAssetId;
        RLM_AssetOrderingService.mockOutcome = mock;

        Test.startTest();
        RLM_ShipmentFulfillmentService.FulfillmentResult res =
            RLM_ShipmentFulfillmentService.confirmShipment(
                hardwareAssetId, new List<String>{ 'SN-RE1' }, Date.today()
            );
        Test.stopTest();

        System.assertEquals(true, res.isSuccess, 'confirmShipment should succeed');
        System.assertEquals(1, res.softwareReleased, 'Born-held software released on shipment');
        System.assertEquals(hardwareAssetId, res.amendmentQuoteId,
            'Re-anchor amendment id should be threaded back for the rep to activate');
    }

    @isTest
    static void guards_nullInputs() {
        Test.startTest();
        RLM_ShipmentFulfillmentService.FulfillmentView v =
            RLM_ShipmentFulfillmentService.getBundleFulfillment(null);
        System.assertEquals(null, v.hardwareAssetId, 'Null asset -> empty view');

        RLM_ShipmentFulfillmentService.FulfillmentResult r1 =
            RLM_ShipmentFulfillmentService.holdBillingForBundle(new List<Id>());
        System.assertEquals(false, r1.isSuccess, 'Empty hold list is a no-op failure');

        RLM_ShipmentFulfillmentService.FulfillmentResult r2 =
            RLM_ShipmentFulfillmentService.confirmShipment(null, new List<String>{ 'X' }, Date.today());
        System.assertEquals(false, r2.isSuccess, 'Null hardware asset -> failure');
        Test.stopTest();
    }
}
