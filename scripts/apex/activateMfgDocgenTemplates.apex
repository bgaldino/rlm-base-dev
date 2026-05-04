// Activate the latest version of each Manufacturing DocumentTemplate.
// Targets Badger_Proposal and Price_Contract (not prefixed with RLM_).
// Finds the highest version per name and sets IsActive = true.

Set<String> mfgTemplateNames = new Set<String>{ 'Badger_Proposal', 'Price_Contract' };

Map<String, DocumentTemplate> latestByName = new Map<String, DocumentTemplate>();

for (DocumentTemplate t : [
    SELECT Id, Name, VersionNumber, IsActive
    FROM DocumentTemplate
    WHERE Name IN :mfgTemplateNames
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
    System.debug('All MFG DocumentTemplates already active.');
}
