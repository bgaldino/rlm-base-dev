/**
 * Tests for RLM_AssetBillingHoldHandler + the RLM_AssetBillingHold Asset trigger:
 * a software subscription created under a ONE-TIME hardware bundle is automatically
 * placed on billing hold (born-held); other shapes are left alone.
 *
 * The BillingScheduleGroup path (RLM_BillingScheduleGroupHold trigger /
 * applyHoldToNewGroups) touches an engine-generated object that cannot be inserted
 * in a unit test, so its decision logic is exercised with an in-memory group and
 * the real group mutation is live-verify-only.
 */
@isTest
private class RLM_AssetBillingHoldHandlerTest {

    // Build a hw/sw product pair with the given root selling-model type.
    private static Map<String, Id> makeProducts(String rootModelType) {
        Product2 hw = new Product2(Name = 'HW Root', ProductCode = 'HWR', IsActive = true);
        Product2 sw = new Product2(Name = 'SW Child', ProductCode = 'SWC', IsActive = true);
        insert new List<Product2>{ hw, sw };

        ProductSellingModel rootModel = new ProductSellingModel(
            Name = 'Root Model', SellingModelType = rootModelType, Status = 'Active'
        );
        if (rootModelType != 'OneTime') {
            // Term-Defined and Evergreen both require a pricing term + unit.
            rootModel.PricingTerm = 1;
            rootModel.PricingTermUnit = 'Months';
        }
        ProductSellingModel term = new ProductSellingModel(
            Name = 'Child Term', SellingModelType = 'TermDefined', Status = 'Active',
            PricingTerm = 1, PricingTermUnit = 'Months'
        );
        insert new List<ProductSellingModel>{ rootModel, term };

        insert new List<ProductSellingModelOption>{
            new ProductSellingModelOption(Product2Id = hw.Id, ProductSellingModelId = rootModel.Id),
            new ProductSellingModelOption(Product2Id = sw.Id, ProductSellingModelId = term.Id)
        };
        return new Map<String, Id>{ 'hw' => hw.Id, 'sw' => sw.Id };
    }

    @isTest
    static void autoHold_subscriptionChildOfOneTimeBundle() {
        Map<String, Id> p = makeProducts('OneTime');
        Account acct = new Account(Name = 'Auto Hold Co');
        insert acct;

        Asset root = new Asset(
            Name = 'HW Unit', AccountId = acct.Id, Product2Id = p.get('hw'),
            Quantity = 1, Status = 'Purchased'
        );
        insert root;

        Test.startTest();
        Asset child = new Asset(
            Name = 'SW Unit', AccountId = acct.Id, Product2Id = p.get('sw'),
            Quantity = 1, ParentId = root.Id
        );
        insert child;
        Test.stopTest();

        Asset held = [SELECT RLM_Asset_Status__c FROM Asset WHERE Id = :child.Id];
        System.assertEquals('BillingHeld', held.RLM_Asset_Status__c,
            'Subscription child of a one-time bundle should be auto-held');

        Asset hw = [SELECT RLM_Asset_Status__c FROM Asset WHERE Id = :root.Id];
        System.assertNotEquals('BillingHeld', hw.RLM_Asset_Status__c,
            'One-time hardware root is never held');
    }

    @isTest
    static void noHold_standaloneSubscription() {
        Map<String, Id> p = makeProducts('OneTime');
        Account acct = new Account(Name = 'Standalone Co');
        insert acct;

        Test.startTest();
        Asset solo = new Asset(
            Name = 'Solo SW', AccountId = acct.Id, Product2Id = p.get('sw'),
            Quantity = 1   // no ParentId / RootAssetId => not part of a bundle
        );
        insert solo;
        Test.stopTest();

        Asset after = [SELECT RLM_Asset_Status__c FROM Asset WHERE Id = :solo.Id];
        System.assertNotEquals('BillingHeld', after.RLM_Asset_Status__c,
            'A standalone subscription (no bundle) is not held');
    }

    @isTest
    static void noHold_subscriptionUnderSubscriptionRoot() {
        // Root is a subscription (Evergreen), NOT one-time. Distinct from the child's
        // TermDefined type because SellingModelType is unique per record.
        Map<String, Id> p = makeProducts('Evergreen');
        Account acct = new Account(Name = 'Sub Root Co');
        insert acct;

        Asset root = new Asset(
            Name = 'Sub Root', AccountId = acct.Id, Product2Id = p.get('hw'),
            Quantity = 1
        );
        insert root;

        Test.startTest();
        Asset child = new Asset(
            Name = 'Sub Child', AccountId = acct.Id, Product2Id = p.get('sw'),
            Quantity = 1, ParentId = root.Id
        );
        insert child;
        Test.stopTest();

        Asset after = [SELECT RLM_Asset_Status__c FROM Asset WHERE Id = :child.Id];
        System.assertNotEquals('BillingHeld', after.RLM_Asset_Status__c,
            'Only children of a ONE-TIME root are held');
    }

    @isTest
    static void applyHoldToNewGroups_guardsAndPath() {
        // Guard paths: null / empty are safe no-ops.
        RLM_AssetBillingHoldHandler.applyHoldToNewGroups(null);
        RLM_AssetBillingHoldHandler.applyHoldToNewGroups(new List<BillingScheduleGroup>());

        // Path: an in-memory group referencing a held asset exercises the "which
        // referenced assets are held" query + the holdBillingGroups call. No real
        // BillingScheduleGroup exists in a unit test, so the override is a no-op.
        Map<String, Id> p = makeProducts('OneTime');
        Account acct = new Account(Name = 'Group Path Co');
        insert acct;
        Asset root = new Asset(Name = 'HW', AccountId = acct.Id, Product2Id = p.get('hw'), Quantity = 1);
        insert root;
        Asset child = new Asset(Name = 'SW', AccountId = acct.Id, Product2Id = p.get('sw'), Quantity = 1, ParentId = root.Id);
        insert child;   // auto-held

        Test.startTest();
        RLM_AssetBillingHoldHandler.applyHoldToNewGroups(new List<BillingScheduleGroup>{
            new BillingScheduleGroup(ReferenceEntityId = child.Id)
        });
        Test.stopTest();

        // Reaching here without exception is the assertion (engine object no-op).
        System.assert(true, 'applyHoldToNewGroups handled a held-asset group reference safely');
    }
}
