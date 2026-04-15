List<OmniProcess> inactiveProcesses = [
    SELECT Id, UniqueName, IsActive
    FROM OmniProcess
    WHERE OmniProcessType = 'Omniscript'
    AND DesignerCustomizationType = 'Discovery Framework'
    AND VersionNumber = 1
    AND IsActive = false
];

if (!inactiveProcesses.isEmpty()) {
    for (OmniProcess op : inactiveProcesses) {
        op.IsActive = true;
    }
    update inactiveProcesses;
    System.debug('Activated ' + inactiveProcesses.size() + ' Guided Selling OmniScript(s).');
    for (OmniProcess op : inactiveProcesses) {
        System.debug('  ' + op.UniqueName + ' -> IsActive=true');
    }
} else {
    System.debug('No inactive Guided Selling OmniScripts found. Nothing to activate.');
}
