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
// PARAM_1 modes, comma- or space-separated:
//   strict (or true) — FAIL when any table is stale. Default reports only: a build that
//                      legitimately loads data after its refresh step will show stale
//                      tables, so failing is opt-in.
//   json             — also print the dependency map as one `DECISION_TABLE_MAP_JSON <json>`
//                      line: per table, what it reads and its verdict.
//   false            — report only, the same as passing nothing.
// Any other token FAILS the run rather than being ignored: a typo like `stirct` would
// otherwise turn a strict gate into a report that always passes.

public class DecisionTableFreshnessException extends Exception {}

Set<String> modes = new Set<String>('%%%PARAM_1%%%'.trim().toLowerCase().split('[,\\s]+'));
// Not passing param1 leaves the token unsubstituted rather than empty.
modes.removeAll(new Set<String>{ '', '%%%' + 'param_1' + '%%%' });
Set<String> unknownModes = modes.clone();
unknownModes.removeAll(new Set<String>{ 'strict', 'true', 'json', 'false' });
if (!unknownModes.isEmpty()) {
    throw new DecisionTableFreshnessException('Unknown param1 mode(s): '
        + String.join(new List<String>(unknownModes), ', ')
        + '. Use strict (or true), json, both as "strict,json", or false to report only.');
}
Boolean strict = modes.contains('strict') || modes.contains('true');
Boolean asJson = modes.contains('json');

List<RLM_DecisionTableManagerController.DecisionTableInfo> tables =
    RLM_DecisionTableManagerController.getDecisionTables();

// ⚠ No tables is NOT a pass. An org that never deployed them, or a user whose
// permissions hide them, would otherwise fall through to "Every table is fresh" and
// exit 0 in strict mode — a readiness gate reporting ready because it looked at
// nothing. This is the same absence-of-evidence-as-verdict failure the controller
// refuses everywhere else; the gate has to refuse it too.
if (tables.isEmpty()) {
    throw new DecisionTableFreshnessException(
        'No decision tables were readable, so freshness could not be checked at all. '
        + 'Either none are deployed (run prepare_rlm_org, or deploy_decision_tables), '
        + 'or the running user cannot see them. This is NOT a clean result.');
}

// The dependency map as data (todo 076 / issue #325): one line, prefixed so it can be cut out of the
// log, with what each table reads and its verdict. Same values the Manager shows; nothing recomputed.
// ⚠ Printed before the summary and per-table detail: FileBasedAnonymousApexTask shows only the
// first 500 output lines, and the detail block below grows with every non-fresh table. Last, it
// could be cut off, and a consumer piping it into jq would read "no table reads X" from the
// missing line.
if (asJson) {
    List<Map<String, Object>> dependencyMap = new List<Map<String, Object>>();
    for (RLM_DecisionTableManagerController.DecisionTableInfo t : tables) {
        dependencyMap.add(new Map<String, Object>{
            'apiName' => t.apiName,
            'label' => t.label,
            'usageType' => t.usageType,
            'sourceObject' => t.sourceObject,
            'readsObjects' => t.readsObjects,
            'contributingObjects' => t.contributingObjects,
            'latestSyncDate' => t.latestSyncDate,
            'latestSyncKind' => t.latestSyncKind,
            'staleness' => t.staleness,
            'stalenessReason' => t.stalenessReason,
            // A Stale verdict may be over-reported when a source criterion was not reproduced.
            'criteriaApplied' => t.criteriaApplied,
            'unreproducedCriteria' => t.unreproducedCriteria
        });
    }
    System.debug(LoggingLevel.ERROR, 'DECISION_TABLE_MAP_JSON ' + JSON.serialize(dependencyMap));
}

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
    // ⚠ "visible to the running user" carries the same weight here as "visible" does in
    // the controller's Fresh reason: probes run USER_MODE, so this ran against the rows
    // THIS user can see. It matters more headlessly than in the UI — a build gate reads
    // as an org-wide all-clear unless it says whose view produced it.
    System.debug(LoggingLevel.ERROR, 'Every table is fresh: the last sync (full or incremental, whichever is later) is later '
        + 'than the newest change VISIBLE TO THE RUNNING USER in every object each '
        + 'table reads. Run this as an operator with org-wide read to make that the '
        + 'whole org.');
} else {
    System.debug(LoggingLevel.ERROR, 'Tables that are not fresh:\n' + String.join(detail, '\n'));
    System.debug(LoggingLevel.ERROR,
        'Refresh with: cci flow run refresh_all_decision_tables --org <alias>\n'
        + '⚠ "Not comparable" is NOT a failure — it means this check refused to guess, '
        + 'usually because a source criterion could not be faithfully reproduced, or because '
        + 'sharing can hide rows from the running user. Compare those by hand. Only "Stale" '
        + 'is a positive finding.');
}

List<String> stale = byVerdict.get('Stale');
if (strict && stale != null && !stale.isEmpty()) {
    throw new DecisionTableFreshnessException(
        stale.size() + ' decision table(s) are stale and were expected to be fresh: '
        + String.join(stale, ', ')
        + '. Run cci flow run refresh_all_decision_tables --org <alias>, or drop strict mode if a later data load '
        + 'is expected to make them stale.');
}
