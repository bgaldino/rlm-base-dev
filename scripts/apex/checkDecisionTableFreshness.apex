// Report every decision table's freshness, headlessly.
//
// The same verdicts the Decision Table Manager component shows, without a browser —
// which is what makes them usable from a build, a CI gate, or an agent maintaining an
// org it cannot click around in.
//
// ⚠ This DELEGATES to RLM_DecisionTableManagerController rather than recomputing
// anything. Two implementations of "is this table stale" would drift, and the one that
// drifted would be trusted anyway. If this script will not compile, the controller is
// not deployed — run `cci task run deploy_post_utils` first.
//
// PARAM_1 = "strict" (or "true") to FAIL when any table is stale. Default reports only.
// A build that legitimately loads data after its refresh step will show stale tables,
// so failing is opt-in rather than the default.

public class DecisionTableFreshnessException extends Exception {}

String mode = '%%%PARAM_1%%%'.trim().toLowerCase();
Boolean strict = mode == 'strict' || mode == 'true';

List<RLM_DecisionTableManagerController.DecisionTableInfo> tables =
    RLM_DecisionTableManagerController.getDecisionTables();

Map<String, List<String>> byVerdict = new Map<String, List<String>>();
List<String> detail = new List<String>();
for (RLM_DecisionTableManagerController.DecisionTableInfo t : tables) {
    if (!byVerdict.containsKey(t.staleness)) {
        byVerdict.put(t.staleness, new List<String>());
    }
    byVerdict.get(t.staleness).add(t.label);
    if (t.staleness != 'Fresh') {
        String reads = t.contributingObjects.isEmpty()
            ? ''
            : '\n      also reads: ' + String.join(t.contributingObjects, ', ');
        detail.add('  [' + t.staleness + '] ' + t.label + ' (' + t.apiName + ')'
            + '\n      ' + t.stalenessReason + reads);
    }
}

List<String> summary = new List<String>();
// Fixed order so the output is diffable between runs and between orgs.
for (String verdict : new List<String>{ 'Fresh', 'Stale', 'Not comparable', 'Unknown' }) {
    if (byVerdict.containsKey(verdict)) {
        summary.add(verdict + '=' + byVerdict.get(verdict).size());
    }
}

System.debug(LoggingLevel.ERROR, '=== Decision table freshness: ' + tables.size()
    + ' table(s) — ' + String.join(summary, ', '));

if (detail.isEmpty()) {
    System.debug(LoggingLevel.ERROR, 'Every table is fresh: the last full sync is later '
        + 'than the newest change in every object each table reads.');
} else {
    System.debug(LoggingLevel.ERROR, 'Tables that are not fresh:\n' + String.join(detail, '\n'));
    System.debug(LoggingLevel.ERROR,
        'Refresh with: cci task run refresh_all_decision_tables --org <alias>\n'
        + '⚠ "Not comparable" is NOT a failure — it means this check refused to guess, '
        + 'usually because a source criterion could not be faithfully reproduced. Compare '
        + 'those by hand. Only "Stale" is a positive finding.');
}

List<String> stale = byVerdict.get('Stale');
if (strict && stale != null && !stale.isEmpty()) {
    throw new DecisionTableFreshnessException(
        stale.size() + ' decision table(s) are stale and were expected to be fresh: '
        + String.join(stale, ', ')
        + '. Run refresh_all_decision_tables, or drop strict mode if a later data load '
        + 'is expected to make them stale.');
}
