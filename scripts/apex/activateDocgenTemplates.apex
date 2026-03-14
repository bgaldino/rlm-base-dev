// Activate the latest version of each RLM_ DocumentTemplate
// Queries all RLM_ templates, finds the highest version per name, activates it.

Map<String, DocumentTemplate> latestByName = new Map<String, DocumentTemplate>();

for (DocumentTemplate t : [
    SELECT Id, Name, VersionNumber, IsActive
    FROM DocumentTemplate
    WHERE Name LIKE 'RLM_%'
    ORDER BY Name ASC, VersionNumber ASC
]) {
    latestByName.put(t.Name, t); // last write wins → highest version
}

List<DocumentTemplate> toActivate = new List<DocumentTemplate>();
for (DocumentTemplate t : latestByName.values()) {
    if (!t.IsActive) {
        t.IsActive = true;
        toActivate.add(t);
    }
}

if (!toActivate.isEmpty()) {
    update toActivate;
    for (DocumentTemplate t : toActivate) {
        System.debug('Activated: ' + t.Name + ' v' + t.VersionNumber);
    }
} else {
    System.debug('All RLM_ DocumentTemplates already active.');
}
