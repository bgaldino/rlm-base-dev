// Idempotent Rentokil Field Service junctions for Bloomingdale territory.

OperatingHours hours = [
    SELECT Id FROM OperatingHours WHERE Name = 'Bloomingdale Pest Hours' LIMIT 1
];
ServiceTerritory territory = [
    SELECT Id FROM ServiceTerritory WHERE Name = 'Bloomingdale IL' LIMIT 1
];

// Time slots Mon-Sat 07:00-18:00 if missing
Set<String> existingDays = new Set<String>();
for (TimeSlot ts : [SELECT DayOfWeek FROM TimeSlot WHERE OperatingHoursId = :hours.Id]) {
    existingDays.add(ts.DayOfWeek);
}
List<TimeSlot> slots = new List<TimeSlot>();
for (String day : new List<String>{
    'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'
}) {
    if (!existingDays.contains(day)) {
        slots.add(new TimeSlot(
            OperatingHoursId = hours.Id,
            DayOfWeek = day,
            StartTime = Time.newInstance(7, 0, 0, 0),
            EndTime = Time.newInstance(18, 0, 0, 0)
        ));
    }
}
insert slots;

// Service Resource for running user
Id userId = UserInfo.getUserId();
List<ServiceResource> resources = [
    SELECT Id FROM ServiceResource WHERE RelatedRecordId = :userId LIMIT 1
];
ServiceResource resource;
if (resources.isEmpty()) {
    resource = new ServiceResource(
        Name = UserInfo.getName() + ' (Pest Tech)',
        RelatedRecordId = userId,
        IsActive = true,
        ResourceType = 'T'
    );
    insert resource;
} else {
    resource = resources[0];
}

List<ServiceTerritoryMember> members = [
    SELECT Id FROM ServiceTerritoryMember
    WHERE ServiceResourceId = :resource.Id AND ServiceTerritoryId = :territory.Id LIMIT 1
];
if (members.isEmpty()) {
    // Secondary if the user already has a primary territory (e.g. QuantumBit demo)
    String territoryType = 'P';
    List<ServiceTerritoryMember> primary = [
        SELECT Id FROM ServiceTerritoryMember
        WHERE ServiceResourceId = :resource.Id AND TerritoryType = 'P' LIMIT 1
    ];
    if (!primary.isEmpty()) {
        territoryType = 'S';
    }
    insert new ServiceTerritoryMember(
        ServiceResourceId = resource.Id,
        ServiceTerritoryId = territory.Id,
        TerritoryType = territoryType,
        EffectiveStartDate = Date.today().addYears(-1)
    );
}

Map<String, Id> skillByLabel = new Map<String, Id>();
for (Skill s : [SELECT Id, MasterLabel FROM Skill WHERE MasterLabel IN ('General Pest', 'Termite', 'Mosquito')]) {
    skillByLabel.put(s.MasterLabel, s.Id);
}
Set<Id> existingSkills = new Set<Id>();
for (ServiceResourceSkill srs : [
    SELECT SkillId FROM ServiceResourceSkill WHERE ServiceResourceId = :resource.Id
]) {
    existingSkills.add(srs.SkillId);
}
List<ServiceResourceSkill> newSkills = new List<ServiceResourceSkill>();
for (Id skillId : skillByLabel.values()) {
    if (!existingSkills.contains(skillId)) {
        newSkills.add(new ServiceResourceSkill(
            ServiceResourceId = resource.Id,
            SkillId = skillId,
            EffectiveStartDate = Date.today().addYears(-1)
        ));
    }
}
insert newSkills;

Map<String, Id> workTypeByName = new Map<String, Id>();
for (WorkType wt : [
    SELECT Id, Name FROM WorkType
    WHERE Name IN ('Initial Pest Treatment', 'Quarterly Pest Visit', 'Pest Re-service')
]) {
    workTypeByName.put(wt.Name, wt.Id);
}
Map<String, String> workTypeSkill = new Map<String, String>{
    'Initial Pest Treatment' => 'General Pest',
    'Quarterly Pest Visit' => 'General Pest',
    'Pest Re-service' => 'General Pest'
};
Set<String> existingReq = new Set<String>();
for (SkillRequirement sr : [
    SELECT RelatedRecordId, SkillId FROM SkillRequirement
    WHERE RelatedRecordId IN :workTypeByName.values()
]) {
    existingReq.add(String.valueOf(sr.RelatedRecordId) + ':' + String.valueOf(sr.SkillId));
}
List<SkillRequirement> reqs = new List<SkillRequirement>();
for (String wtName : workTypeSkill.keySet()) {
    Id wtId = workTypeByName.get(wtName);
    Id skillId = skillByLabel.get(workTypeSkill.get(wtName));
    if (wtId == null || skillId == null) {
        continue;
    }
    String key = String.valueOf(wtId) + ':' + String.valueOf(skillId);
    if (!existingReq.contains(key)) {
        reqs.add(new SkillRequirement(RelatedRecordId = wtId, SkillId = skillId, SkillLevel = 1));
    }
}
insert reqs;

System.debug('setupRtkFoundation complete');
