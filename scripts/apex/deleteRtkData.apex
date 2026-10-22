// Delete Rentokil pest demo configuration data (not transactional quotes/orders).
// Dependency order: junctions → work types/territory → related components → price book → products → zones.

List<WorkType> workTypes = [
    SELECT Id FROM WorkType
    WHERE Name IN ('Initial Pest Treatment', 'Quarterly Pest Visit', 'Pest Re-service')
];
if (!workTypes.isEmpty()) {
    delete [SELECT Id FROM SkillRequirement WHERE RelatedRecordId IN :workTypes];
}

ServiceTerritory territory;
List<ServiceTerritory> territories = [SELECT Id FROM ServiceTerritory WHERE Name = 'Bloomingdale IL' LIMIT 1];
if (!territories.isEmpty()) {
    territory = territories[0];
    delete [SELECT Id FROM ServiceTerritoryMember WHERE ServiceTerritoryId = :territory.Id];
    delete territory;
}

List<OperatingHours> hours = [SELECT Id FROM OperatingHours WHERE Name = 'Bloomingdale Pest Hours' LIMIT 1];
if (!hours.isEmpty()) {
    delete [SELECT Id FROM TimeSlot WHERE OperatingHoursId = :hours[0].Id];
    delete hours;
}

delete workTypes;

List<Product2> products = [SELECT Id FROM Product2 WHERE StockKeepingUnit LIKE 'RTK-%'];
if (!products.isEmpty()) {
    delete [
        SELECT Id FROM ProductFulfillmentScenario WHERE ProductId IN :products
    ];
    delete [
        SELECT Id FROM ProductFulfillmentDecompRule
        WHERE SourceProductId IN :products OR DestinationProductId IN :products
    ];
    delete [SELECT Id FROM ProductRelatedComponent WHERE ParentProductId IN :products OR ChildProductId IN :products];
    delete [SELECT Id FROM ProductCategoryProduct WHERE ProductId IN :products];
    delete [SELECT Id FROM ProductAttributeDefinition WHERE Product2Id IN :products];
    delete [SELECT Id FROM ProductSellingModelOption WHERE Product2Id IN :products];
    delete [SELECT Id FROM PricebookEntry WHERE Product2Id IN :products];
    delete products;
}

delete [SELECT Id FROM ProductCategory WHERE Code LIKE 'PC-RTK-%'];
delete [SELECT Id FROM ProductCatalog WHERE Code = 'CAT-RTK-RES'];
delete [SELECT Id FROM ProductClassificationAttr WHERE ProductClassification.Code = 'PC-RTK-RES'];
delete [SELECT Id FROM ProductClassification WHERE Code = 'PC-RTK-RES'];
delete [SELECT Id FROM AttributeCategoryAttribute WHERE AttributeCategory.Code = 'AC-RTK-PROPERTY'];
delete [SELECT Id FROM AttributeCategory WHERE Code = 'AC-RTK-PROPERTY'];
delete [SELECT Id FROM AttributeDefinition WHERE Code LIKE 'ATTR-RTK-%'];
delete [SELECT Id FROM AttributePicklistValue WHERE Picklist.Name LIKE 'RTK %'];
delete [SELECT Id FROM AttributePicklist WHERE Name LIKE 'RTK %'];
delete [SELECT Id FROM RLM_RTK_Service_Zone__c];
delete [SELECT Id FROM FulfillmentStepDependencyDef WHERE Name LIKE '%Treatment%' OR Name LIKE '%Pest%'];
delete [SELECT Id FROM FulfillmentStepDefinition WHERE Name LIKE '%Initial Treatment%' OR Name LIKE '%Pest Subscription%'];
delete [SELECT Id FROM FulfillmentStepDefinitionGroup WHERE Name IN ('Initial Pest Treatment', 'Pest Finance')];

System.debug('deleteRtkData complete');
