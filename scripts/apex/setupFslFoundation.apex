// Idempotent Field Service foundation junctions for the QuantumBit demo.
// Runs after qb-fsl (OperatingHours, ServiceTerritory, WorkType) and post_fsl (Skills).
// Each record is inserted only when its logical key does not already exist, so the
// script can run repeatedly without duplicates and without deleting existing data.

final String HOURS_NAME = 'QuantumBit Standard Hours';
final String TERRITORY_NAME = 'QuantumBit San Francisco';
final List<String> WEEKDAYS = new List<String>{ 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday' };
final Time DAY_START = Time.newInstance(8, 0, 0, 0);
final Time DAY_END = Time.newInstance(17, 0, 0, 0);

// WorkType name => Skill DeveloperNames
Map<String, List<String>> skillsByWorkType = new Map<String, List<String>>{
    'Server Rack Installation' => new List<String>{ 'Server_Rack_Install' },
    'Preventive Maintenance' => new List<String>{ 'Preventive_Maintenance' },
    'Hardware Break/Fix' => new List<String>{ 'Hardware_Break_Fix' }
};
// WorkType name => Product2 SKUs required on site
Map<String, List<String>> productsByWorkType = new Map<String, List<String>>{
    'Server Rack Installation' => new List<String>{ 'QB-BDL-R750', 'QB-BDL-RAXS', 'QB-CMPC-5882' }
};

OperatingHours hours = [SELECT Id FROM OperatingHours WHERE Name = :HOURS_NAME LIMIT 1];
ServiceTerritory territory = [SELECT Id FROM ServiceTerritory WHERE Name = :TERRITORY_NAME LIMIT 1];

Map<String, WorkType> workTypes = new Map<String, WorkType>();
for (WorkType wt : [SELECT Id, Name FROM WorkType WHERE Name IN :skillsByWorkType.keySet()]) {
    workTypes.put(wt.Name, wt);
}
Map<String, Skill> skills = new Map<String, Skill>();
for (Skill s : [SELECT Id, DeveloperName FROM Skill]) {
    skills.put(s.DeveloperName, s);
}
Set<String> allSkus = new Set<String>();
for (List<String> skus : productsByWorkType.values()) {
    allSkus.addAll(skus);
}
Map<String, Id> productIdBySku = new Map<String, Id>();
for (Product2 p : [SELECT Id, StockKeepingUnit FROM Product2 WHERE StockKeepingUnit IN :allSkus]) {
    productIdBySku.put(p.StockKeepingUnit, p.Id);
}

// --- TimeSlots (Mon-Fri 8-17) ---
Set<String> existingSlots = new Set<String>();
for (TimeSlot ts : [SELECT DayOfWeek, StartTime FROM TimeSlot WHERE OperatingHoursId = :hours.Id]) {
    existingSlots.add(ts.DayOfWeek + '|' + String.valueOf(ts.StartTime));
}
List<TimeSlot> newSlots = new List<TimeSlot>();
for (String day : WEEKDAYS) {
    if (!existingSlots.contains(day + '|' + String.valueOf(DAY_START))) {
        newSlots.add(new TimeSlot(OperatingHoursId = hours.Id, DayOfWeek = day, StartTime = DAY_START, EndTime = DAY_END, Type = 'Normal'));
    }
}
insert newSlots;

// --- SkillRequirements (WorkType -> Skill) ---
Set<String> existingReqs = new Set<String>();
for (SkillRequirement sr : [SELECT RelatedRecordId, SkillId FROM SkillRequirement WHERE RelatedRecordId IN :new Map<Id, WorkType>(workTypes.values()).keySet()]) {
    existingReqs.add(sr.RelatedRecordId + '|' + sr.SkillId);
}
List<SkillRequirement> newReqs = new List<SkillRequirement>();
for (String wtName : skillsByWorkType.keySet()) {
    WorkType wt = workTypes.get(wtName);
    if (wt == null) continue;
    for (String devName : skillsByWorkType.get(wtName)) {
        Skill s = skills.get(devName);
        if (s != null && !existingReqs.contains(wt.Id + '|' + s.Id)) {
            newReqs.add(new SkillRequirement(RelatedRecordId = wt.Id, SkillId = s.Id, SkillLevel = 1));
        }
    }
}
insert newReqs;

// --- ProductRequired (WorkType -> Product2) ---
Set<String> existingProdReqs = new Set<String>();
for (ProductRequired pr : [SELECT ParentRecordId, Product2Id FROM ProductRequired WHERE ParentRecordId IN :new Map<Id, WorkType>(workTypes.values()).keySet()]) {
    existingProdReqs.add(pr.ParentRecordId + '|' + pr.Product2Id);
}
List<ProductRequired> newProdReqs = new List<ProductRequired>();
for (String wtName : productsByWorkType.keySet()) {
    WorkType wt = workTypes.get(wtName);
    if (wt == null) continue;
    for (String sku : productsByWorkType.get(wtName)) {
        Id productId = productIdBySku.get(sku);
        if (productId != null && !existingProdReqs.contains(wt.Id + '|' + productId)) {
            newProdReqs.add(new ProductRequired(ParentRecordId = wt.Id, Product2Id = productId, QuantityRequired = 1));
        }
    }
}
insert newProdReqs;

// --- ServiceResource for the running user (demo technician) ---
Id userId = UserInfo.getUserId();
List<ServiceResource> resources = [SELECT Id FROM ServiceResource WHERE RelatedRecordId = :userId LIMIT 1];
ServiceResource resource;
if (resources.isEmpty()) {
    resource = new ServiceResource(Name = UserInfo.getName(), RelatedRecordId = userId, ResourceType = 'T', IsActive = true);
    insert resource;
} else {
    resource = resources[0];
}

// --- ServiceResourceSkills (technician has every demo skill) ---
Set<Id> existingResourceSkills = new Set<Id>();
for (ServiceResourceSkill srs : [SELECT SkillId FROM ServiceResourceSkill WHERE ServiceResourceId = :resource.Id]) {
    existingResourceSkills.add(srs.SkillId);
}
List<ServiceResourceSkill> newResourceSkills = new List<ServiceResourceSkill>();
for (List<String> devNames : skillsByWorkType.values()) {
    for (String devName : devNames) {
        Skill s = skills.get(devName);
        if (s != null && !existingResourceSkills.contains(s.Id)) {
            newResourceSkills.add(new ServiceResourceSkill(ServiceResourceId = resource.Id, SkillId = s.Id, SkillLevel = 1, EffectiveStartDate = System.now().addDays(-1)));
            existingResourceSkills.add(s.Id);
        }
    }
}
insert newResourceSkills;

// --- ServiceTerritoryMember (primary territory) ---
// A resource can hold only one open primary membership, so end any primary elsewhere first.
if ([SELECT COUNT() FROM ServiceTerritoryMember WHERE ServiceResourceId = :resource.Id AND ServiceTerritoryId = :territory.Id] == 0) {
    Datetime cutover = System.now();
    List<ServiceTerritoryMember> otherPrimaries = [SELECT Id FROM ServiceTerritoryMember
        WHERE ServiceResourceId = :resource.Id AND TerritoryType = 'P' AND ServiceTerritoryId != :territory.Id
        AND (EffectiveEndDate = null OR EffectiveEndDate > :cutover)];
    for (ServiceTerritoryMember m : otherPrimaries) {
        m.EffectiveEndDate = cutover.addMinutes(-1);
    }
    update otherPrimaries;
    insert new ServiceTerritoryMember(ServiceResourceId = resource.Id, ServiceTerritoryId = territory.Id, TerritoryType = 'P', EffectiveStartDate = cutover, OperatingHoursId = hours.Id);
}

System.debug('FSL foundation: +' + newSlots.size() + ' time slots, +' + newReqs.size() + ' skill reqs, +'
    + newProdReqs.size() + ' product reqs, +' + newResourceSkills.size() + ' resource skills');
