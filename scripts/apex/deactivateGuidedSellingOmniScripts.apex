List<OmniProcess> activeProcesses = [
    SELECT Id, UniqueName, IsActive
    FROM OmniProcess
    WHERE OmniProcessType = 'Omniscript'
    AND DesignerCustomizationType = 'Discovery Framework'
    AND IsActive = true
    ORDER BY UniqueName DESC
];

if (activeProcesses.isEmpty()) {
    System.debug('No active Guided Selling OmniScripts found. Nothing to deactivate.');
} else {
    for (OmniProcess op : activeProcesses) {
        op.IsActive = false;
    }

    Integer passCount = 0;
    Integer maxPasses = 3;
    List<OmniProcess> remaining = activeProcesses;

    while (!remaining.isEmpty() && passCount < maxPasses) {
        passCount++;
        List<Database.SaveResult> results = Database.update(remaining, false);
        List<OmniProcess> failed = new List<OmniProcess>();
        for (Integer i = 0; i < results.size(); i++) {
            if (results[i].isSuccess()) {
                System.debug('  Pass ' + passCount + ': ' + remaining[i].UniqueName + ' -> IsActive=false');
            } else {
                failed.add(remaining[i]);
            }
        }
        remaining = failed;
    }

    Integer deactivated = activeProcesses.size() - remaining.size();
    System.debug('Deactivated ' + deactivated + ' of ' + activeProcesses.size() + ' Guided Selling OmniScript(s).');

    if (!remaining.isEmpty()) {
        System.debug('WARNING: Could not deactivate ' + remaining.size() + ' record(s):');
        for (OmniProcess op : remaining) {
            System.debug('  ' + op.UniqueName + ' (Id: ' + op.Id + ')');
        }
    }
}
