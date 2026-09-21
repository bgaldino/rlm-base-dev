/**
 * activateCustomerDemoRatingRecords.apex
 *
 * Customer-demo-scoped counterpart to activateRatingRecords.apex.
 *
 * activateRatingRecords.apex activates EVERY non-Active UnitOfMeasureClass, UsageResource,
 * ProductUsageResource and ProductUsageGrant in the org. That is correct for a QB build, but
 * wrong in a shared demo org for two reasons:
 *
 *   1. It flips other customers' Draft records to Active as a side effect.
 *   2. Its org-wide UnitOfMeasureClass update hard-fails on any pre-existing class whose
 *      DefaultUnitOfMeasure is not associated with that class. In the customer-template org
 *      that is CAS01 (Case), whose default unit is EACH — and EACH has no class at all:
 *        INVALID_INPUT, Enter a unit of measure as the default unit of measure
 *        that's associated with the unit of measure class.: [DefaultUnitOfMeasureId]
 *      One bad pre-existing row aborts activation for everything else.
 *
 * This version touches only the meters listed below and the records hanging off them.
 * Steps 3 and 4 of the QB script (TokenResourceId pre-population and Token PUR ordering)
 * are omitted because customer demo meters are Category='Usage' with no TokenResource.
 *
 * Idempotent: already-Active records are skipped.
 */

final Set<String> CUSTOMER_METER_CODES = new Set<String>{
    'SFDC-UR-FLEX',
    'SFDC-UR-CONV'
};

List<UsageResource> meters = [
    SELECT Id, Code, Status, UnitOfMeasureClassId, UsageDefinitionProductId
    FROM UsageResource
    WHERE Code IN :CUSTOMER_METER_CODES
];

if (meters.isEmpty()) {
    System.debug('activateCustomerDemoRating: no customer meters found — nothing to do.');
    return;
}

Set<Id> meterIds = new Set<Id>();
Set<Id> classIds = new Set<Id>();
Set<Id> definitionProductIds = new Set<Id>();
for (UsageResource ur : meters) {
    meterIds.add(ur.Id);
    if (ur.UnitOfMeasureClassId != null) classIds.add(ur.UnitOfMeasureClassId);
    if (ur.UsageDefinitionProductId != null) definitionProductIds.add(ur.UsageDefinitionProductId);
}

// Step 1: activate only the UOM classes these meters actually use.
List<UnitOfMeasureClass> classes = [
    SELECT Id, Code, Status FROM UnitOfMeasureClass
    WHERE Id IN :classIds AND Status != 'Active'
];
if (!classes.isEmpty()) {
    for (UnitOfMeasureClass c : classes) c.Status = 'Active';
    update classes;
    System.debug('activateCustomerDemoRating: activated ' + classes.size() + ' UnitOfMeasureClass record(s).');
}

// Step 2: activate the meters themselves.
List<UsageResource> draftMeters = new List<UsageResource>();
for (UsageResource ur : meters) {
    if (ur.Status != 'Active') {
        ur.Status = 'Active';
        draftMeters.add(ur);
    }
}
if (!draftMeters.isEmpty()) {
    update draftMeters;
    System.debug('activateCustomerDemoRating: activated ' + draftMeters.size() + ' UsageResource record(s).');
}

// Step 3: clear+activate the ProductUsageResource rows.
// Assigning TokenResourceId = null in the same DML stops the platform re-populating it
// during the update, which is what blocks activation. Mirrors Step 5 of the QB script.
List<ProductUsageResource> purs = [
    SELECT Id, Status, TokenResourceId
    FROM ProductUsageResource
    WHERE UsageResourceId IN :meterIds AND Status != 'Active'
];
if (!purs.isEmpty()) {
    for (ProductUsageResource pur : purs) {
        pur.TokenResourceId = null;
        pur.Status = 'Active';
    }
    List<Database.SaveResult> purResults = Database.update(purs, false);
    Integer purOk = 0;
    for (Integer i = 0; i < purResults.size(); i++) {
        if (purResults[i].isSuccess()) {
            purOk++;
        } else {
            for (Database.Error err : purResults[i].getErrors()) {
                System.debug(LoggingLevel.ERROR,
                    'activateCustomerDemoRating: failed to activate PUR ' + purs[i].Id + ': ' + err.getMessage());
            }
        }
    }
    System.debug('activateCustomerDemoRating: clear+activated ' + purOk + '/' + purs.size() + ' PUR(s).');
}

// Step 4: activate the grants. They attach either to a PUR or to the usage definition product.
Set<Id> purIds = new Set<Id>();
for (ProductUsageResource pur : [SELECT Id FROM ProductUsageResource WHERE UsageResourceId IN :meterIds]) {
    purIds.add(pur.Id);
}
List<ProductUsageGrant> pugs = [
    SELECT Id, Status
    FROM ProductUsageGrant
    WHERE Status != 'Active'
    AND (ProductUsageResourceId IN :purIds OR UsageDefinitionProductId IN :definitionProductIds)
];
if (!pugs.isEmpty()) {
    for (ProductUsageGrant pug : pugs) pug.Status = 'Active';
    List<Database.SaveResult> pugResults = Database.update(pugs, false);
    Integer pugOk = 0;
    for (Integer i = 0; i < pugResults.size(); i++) {
        if (pugResults[i].isSuccess()) {
            pugOk++;
        } else {
            for (Database.Error err : pugResults[i].getErrors()) {
                System.debug(LoggingLevel.ERROR,
                    'activateCustomerDemoRating: failed to activate PUG ' + pugs[i].Id + ': ' + err.getMessage());
            }
        }
    }
    System.debug('activateCustomerDemoRating: activated ' + pugOk + '/' + pugs.size() + ' ProductUsageGrant record(s).');
}
