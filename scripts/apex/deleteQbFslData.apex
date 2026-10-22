// Delete QuantumBit Field Service demo data in child -> parent order.
// Scoped to the qb-fsl records (by name) so unrelated Field Service data is left alone.

final String HOURS_NAME = 'QuantumBit Standard Hours';
final String TERRITORY_NAME = 'QuantumBit San Francisco';
final Set<String> WORK_TYPE_NAMES = new Set<String>{ 'Server Rack Installation', 'Preventive Maintenance', 'Hardware Break/Fix' };

List<WorkType> workTypes = [SELECT Id FROM WorkType WHERE Name IN :WORK_TYPE_NAMES];
List<ServiceTerritory> territories = [SELECT Id FROM ServiceTerritory WHERE Name = :TERRITORY_NAME];
List<OperatingHours> hours = [SELECT Id FROM OperatingHours WHERE Name = :HOURS_NAME];

List<MaintenancePlan> plans = [SELECT Id FROM MaintenancePlan WHERE WorkTypeId IN :workTypes];
List<WorkOrder> workOrders = [SELECT Id, AssetId FROM WorkOrder
    WHERE WorkTypeId IN :workTypes OR ServiceTerritoryId IN :territories OR MaintenancePlanId IN :plans];
Set<Id> assetIds = new Set<Id>();
for (WorkOrder wo : workOrders) {
    if (wo.AssetId != null) {
        assetIds.add(wo.AssetId);
    }
}
delete [SELECT Id FROM AssignedResource WHERE ServiceAppointment.ParentRecordId IN :workOrders];
delete [SELECT Id FROM ServiceAppointment WHERE ParentRecordId IN :workOrders];
delete workOrders;

delete [SELECT Id FROM MaintenanceAsset WHERE MaintenancePlanId IN :plans];
delete [SELECT Id FROM MaintenanceWorkRule WHERE ParentMaintenancePlanId IN :plans];
delete plans;
delete [SELECT Id FROM Entitlement WHERE AssetId IN :assetIds AND Name LIKE 'Gold Hardware Maintenance - %'];

delete [SELECT Id FROM SkillRequirement WHERE RelatedRecordId IN :workTypes];
delete [SELECT Id FROM ProductRequired WHERE ParentRecordId IN :workTypes];

List<ServiceTerritoryMember> members = [SELECT Id, ServiceResourceId FROM ServiceTerritoryMember WHERE ServiceTerritoryId IN :territories];
Set<Id> resourceIds = new Set<Id>();
for (ServiceTerritoryMember m : members) {
    resourceIds.add(m.ServiceResourceId);
}
delete members;
delete [SELECT Id FROM ServiceResourceSkill WHERE ServiceResourceId IN :resourceIds];
// ServiceResource cannot be deleted once used; deactivate instead.
List<ServiceResource> resources = [SELECT Id, IsActive FROM ServiceResource WHERE Id IN :resourceIds];
for (ServiceResource r : resources) {
    r.IsActive = false;
}
update resources;

delete workTypes;
delete territories;
delete [SELECT Id FROM TimeSlot WHERE OperatingHoursId IN :hours];
delete hours;
