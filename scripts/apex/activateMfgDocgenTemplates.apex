// Activate the latest version of each Manufacturing DocumentTemplate.
// Targets RLM_MFG_Sales_Proposal_Document and Price_Contract.
// Finds the highest version per name and sets IsActive = true.

Set<String> mfgTemplateNames = new Set<String>{ 'RLM_MFG_Sales_Proposal_Document', 'Price_Contract' };

Map<String, DocumentTemplate> latestByName = new Map<String, DocumentTemplate>();

for (DocumentTemplate t : [
    SELECT Id, Name, VersionNumber, IsActive
    FROM DocumentTemplate
    WHERE Name IN :mfgTemplateNames
    ORDER BY Name ASC, VersionNumber ASC
]) {
    latestByName.put(t.Name, t); // last write wins → highest version
}

// Fail loudly if any expected template never came back — iterating only
// latestByName.values() can't detect a missing deployment on its own.
List<String> missingTemplates = new List<String>();
for (String expected : mfgTemplateNames) {
    if (!latestByName.containsKey(expected)) {
        missingTemplates.add(expected);
    }
}
if (!missingTemplates.isEmpty()) {
    throw new QueryException(
        'DocumentTemplate lookup missing expected template(s): ' +
        String.join(missingTemplates, ', ')
    );
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
