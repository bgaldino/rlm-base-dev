/**
 * RLM_DecisionTableManagerController
 *
 * Apex controller for the rlmDecisionTableManager Lightning Web Component.
 * Lists decision tables with both sync timestamps and a freshness verdict, queues
 * full or incremental refreshes, and polls refresh status. It deliberately does NOT
 * toggle incremental sync — see the note above setIncrementalEnabled's absence.
 *
 * ⚠ Why a flow sits in the middle of the refresh path: refreshDecisionTable is a
 * REST/Flow invocable action and is NOT callable from Apex —
 * Invocable.Action.createStandardAction('refreshDecisionTable') throws
 * "refreshDecisionTable isn't a valid action type". Apex CAN start an
 * autolaunched flow, so refreshes are delegated to
 * RLM_Refresh_Decision_Tables_Bulk, started once with the whole selection so a
 * 40-table refresh is one interview rather than 40.
 *
 * ⚠ Queued is not refreshed. The action returns Queued when it accepts the
 * request; the sync happens asynchronously afterwards. Callers must poll
 * getRefreshStatus. A rejected request that throws is counted and named by the
 * flow; one that merely fails later shows up as RefreshStatus on the table.
 *
 * ⚠ Incremental refresh advances LastIncrementalSyncDate ONLY — LastSyncDate does
 * not move. Watching LastSyncDate makes a working incremental refresh look dead.
 * Incremental also requires an initial full refresh and fails above 2000 changed
 * records (see the Refresh Decision Table action reference).
 *
 * ══ How freshness is decided, and where it deliberately refuses to decide ══
 *
 * A table is stale when its source changed after the last full sync. That
 * comparison is only meaningful if the rows counted are the rows the table
 * actually holds, so a table carrying DecisionTableSourceCriteria needs those
 * criteria reproduced in the comparison query. translateCriterion does that for
 * the cases where the translation is provably faithful, and REFUSES the rest —
 * a refused table reports "Not comparable" with the reason, never a guess.
 *
 * ⚠ The case that matters most: A CRITERION THAT READS A FIELD ON A RELATED
 * RECORD CANNOT BE REPRODUCED THIS WAY, at any depth. Editing a parent does not
 * write the child's row at all (measured: 200 of 200 sampled PricebookEntry rows
 * had a Product2 parent modified later than the child, child timestamps untouched).
 * So when a parent edit moves rows into or out of the filter, no child stamp of any
 * kind moves and the probe's MAX does not move
 * — the table would be reported FRESH at the exact moment it went stale. That is
 * the failure this repo already hit once: Contract_Pricing_* filter on
 * ContractItemPriceId.ContractId.StatusCode = Activated, and activating a
 * contract moves tier rows into the table without rewriting one of them. Depth is
 * not the test — one hop fails for the same reason two do.
 *
 * Such a criterion is DROPPED from the query and the objects it reaches across are
 * PROBED instead. That is sound, but only under two conditions, and both are
 * enforced: the criteria must be a plain conjunction (dropping an AND-ed conjunct
 * widens the row set, so a MAX over the superset that predates the sync still
 * proves nothing in the real set changed — under OR it could NARROW, which is
 * not), and the criterion's own boundary must be fixed (see ValueType below).
 * Where the objects cannot be named, there is nothing to probe and the table is
 * refused outright.
 *
 * ⚠ SourceConditionLogic (on DecisionTable) holds free-form logic over the criteria
 * by sequence number, such as "1 AND (2 OR 3)". It is POPULATED on every table that
 * has criteria — the platform writes the default conjunction ("1", "1 AND 2"), so
 * treating "not blank" as "custom logic" refuses everything and improves nothing
 * (measured: it did exactly that on the first attempt). isPlainConjunction accepts
 * only a pure AND over every criterion exactly once, and refuses anything else —
 * any OR, NOT or parenthesis — because AND-ing those would silently answer a
 * different question. The field is NOT filterable, so it cannot be checked with a
 * WHERE clause; read it and inspect the value.
 *
 * ⚠ ValueType (on DecisionTableSourceCriteria) says how Value should be read:
 * Literal, Parameter, Picklist, Formula or Lookup. Only Literal is a value that
 * can be bound directly; the others resolve WHEN THE TABLE IS REFRESHED. That
 * makes them the one class that can be neither translated NOR skipped, and the
 * distinction is easy to miss: skipping is sound only because dropping a fixed
 * conjunct widens the row set, which assumes membership changes only when a record
 * changes. A boundary that resolves at refresh time breaks that assumption — a
 * Formula meaning "StartDate <= TODAY" starts admitting a row at midnight with no
 * record edited and no timestamp anywhere to witness it, so every probe reads Fresh
 * over a table that is genuinely stale. There is nothing to watch, so a non-literal
 * criterion is REFUSED. (IsNull/IsNotNull are exempt — they compare against no
 * value at all.) Measured on a stock build: all 7 criteria are Literal, so this
 * costs no verdicts today; it is a guard against a criterion that has not been
 * authored yet.
 *
 * Three limits apply to every verdict, including the unfiltered ones, because a
 * probe only sees rows that still exist and that the caller is allowed to read:
 *
 * 1. A DELETED source row leaves no timestamp behind.
 * 2. A row edited OUT of a filter takes its timestamp with it.
 * 3. ⚠ Probes run in USER_MODE from a `with sharing` class, so both the count and
 *    the newest change are computed over the rows the RUNNING USER can see. A row
 *    hidden by sharing and modified after the sync is invisible to the probe, and
 *    the failure direction is the bad one — FRESH while stale. Unreachable for an
 *    admin with View All Data, which is the intended operator of a readiness check;
 *    reachable the moment RLM_DecisionTableManager is assigned to a restricted user
 *    in an org with private records on a source object. The verdict wording says
 *    "visible" rather than asserting org-wide emptiness so the claim matches the
 *    evidence. USER_MODE is kept deliberately: this reads no data a user could not
 *    already query, and dropping to system mode to make the wording stronger would
 *    trade a real access boundary for a cosmetic one.
 *
 * All three can leave a genuinely stale table reading FRESH. This check catches
 * inserts and edits the caller can see, which is what a post-build readiness check
 * is for; it is not a substitute for refreshing after a known data load.
 *
 * A table whose source cannot be read is UNKNOWN, never FRESH.
 */
public with sharing class RLM_DecisionTableManagerController {

    @TestVisible private static final String BULK_REFRESH_FLOW = 'RLM_Refresh_Decision_Tables_Bulk';

    // Staleness verdicts. Anything that is not a positive, computed comparison is
    // one of the two non-committal values — never FRESH by default.
    @TestVisible private static final String STALENESS_FRESH = 'Fresh';
    @TestVisible private static final String STALENESS_STALE = 'Stale';
    @TestVisible private static final String STALENESS_UNCOMPUTED = 'Not comparable';
    @TestVisible private static final String STALENESS_UNKNOWN = 'Unknown';

    // Freshness costs one aggregate query per DISTINCT probe, and probes are registered
    // in more than one place — every `probesByKey.put` site in getDecisionTables is a
    // source, and planSource decides how many each table contributes. Deliberately NOT
    // enumerated here: this comment has already gone stale twice by listing them by
    // hand next to a constant that never moved, and a count measured on one build dates
    // the moment another probe kind is added.
    //
    // An org with many more probes than the cap would exhaust the governor limit
    // mid-loop and throw, so bound it explicitly and report the tables that were
    // skipped rather than truncating silently or dying.
    //
    // ⚠ A filtered probe and its disambiguator are NOT kept together by this cap —
    // either can be the one that gets dropped. applyEmptySourceVerdict handles the
    // split honestly rather than assuming the partner ran.
    @TestVisible private static final Integer MAX_SOURCE_QUERIES = 70;

    // DataSourceType values whose rows do NOT come from an sObject, so comparing
    // LastSyncDate against a source object's newest change is meaningless for them.
    // A CsvUpload table is refreshed by uploading a file — UploadStatus is its real
    // signal — and a ContextDefinition table is fed by Context Service.
    @TestVisible private static final Set<String> NON_SOBJECT_SOURCE_TYPES =
        new Set<String>{ 'CsvUpload', 'ContextDefinition' };

    // The only ValueType whose Value is a literal that can be bound as-is. Parameter,
    // Formula and Lookup resolve at runtime, and Picklist is not the same thing as a
    // literal picklist value — the platform stamps Literal for those (measured on
    // IndexRate.UsageType, a picklist field, whose criterion is ValueType=Literal).
    @TestVisible private static final String VALUE_TYPE_LITERAL = 'Literal';

    /**
     * The timestamp every probe measures. A platform constant, never stored text — it
     * is concatenated into the aggregate query.
     *
     * ⚠ SystemModstamp, NOT LastModifiedDate. LastModifiedDate records changes made by
     * a USER; SystemModstamp also advances for internal processes that leave it alone —
     * Email Bounce Management, picklist maintenance, roll-up recalculation, and an
     * open-ended set of others Salesforce does not enumerate. Watching LastModifiedDate
     * meant any of those could change what a refresh materialises while every probe
     * stayed older than the sync, which is a confident false Fresh.
     *
     * This is the same reason Salesforce's own replication API (getUpdated) keys on
     * SystemModstamp: "what changed since T" is exactly the question here.
     *
     * Strictly safer, never weaker: SystemModstamp >= LastModifiedDate always, so the
     * switch can only report MORE Stale, which is the sanctioned direction. Measured on
     * a stock build: identical on all 22 source objects, so it cost nothing — and it
     * closes a class no deny-list could have enumerated.
     *
     * It does NOT subsume PLATFORM_MAINTAINED_FIELDS below: LastActivityDate and the
     * view stamps live outside the record's own modification tracking, so those guards
     * stay.
     */
    @TestVisible private static final String WITNESS_FIELD = 'SystemModstamp';

    // ⚠ Says what is actually true of BOTH kinds movesWithoutARecordEdit catches. It
    // once said "a formula", which was a guess about which kind had been found — and
    // wrong for every platform-maintained field, where there is no formula at all.
    @TestVisible private static final String UNWATCHABLE_FIELD =
        'can change without its record being edited, so no timestamp here moves with it';

    /**
     * Fields the PLATFORM maintains whose value moves without the record being edited,
     * without isCalculated() being true, AND without WITNESS_FIELD moving — the last
     * clause is what makes the entry load-bearing rather than merely cautious.
     *
     * Measured on a live org rather than reasoned about, because the two candidates
     * that looked alike behave oppositely:
     *
     *   - VIEW STAMPS: reading a record `FOR VIEW` moved LastViewedDate and
     *     LastReferencedDate forward a day while SystemModstamp did NOT move at all.
     *     They live in RecentlyViewed storage, not the record row. **Load-bearing:
     *     nothing else here would ever see them change.**
     *   - LastActivityDate: inserting a Task against an Account moved LastActivityDate
     *     AND SystemModstamp, while LastModifiedDate stayed put. The witness sees it,
     *     so denying it was pure over-refusal — REMOVED. (That measurement is also the
     *     clearest demonstration of why the witness swap was necessary at all: a real
     *     change that LastModifiedDate could not see.)
     *   - SystemModstamp itself: witnessed by construction — REMOVED.
     */
    @TestVisible private static final Set<String> PLATFORM_MAINTAINED_FIELDS = new Set<String>{
        'lastvieweddate', 'lastreferenceddate'
    };

    /**
     * Formula fields Salesforce DOCUMENTS as computing only from fields on their own
     * record, keyed `object.field` in lower case.
     *
     * ⚠ Read the rule this is an exception to first: a formula is refused because Apex
     * cannot see what it reads, and a cross-object formula moves when the OTHER record
     * changes. That is a statement about what this code can PROVE, not about formulas
     * being unwatchable in principle. Where the platform documents the inputs and they
     * are all on the same row, an edit to any of them writes that row — so the row's
     * own WITNESS_FIELD sees every change, and refusing is pure over-refusal.
     *
     * The bar for an entry is the dev guide saying what the formula computes, not
     * someone reasoning about what it probably does. Each entry carries its citation.
     *
     * ⚠ Version-pinned by nature: a release can redefine a standard formula. Re-verify
     * these against the dev guide at each release cut, alongside the other version
     * sweeps. If a definition becomes cross-object and this is not updated, the entry
     * turns into a false Fresh — which is why the list is short and cited rather than
     * convenient.
     *
     * - assetratecardentry.bindingobjectformula (262 / API v67.0):
     *   "The formula that returns the ID of the associated binding object, if
     *   specified. If binding object isn't added, the formula returns the asset ID of
     *   the asset related to this asset rate card entry."
     *   — sforce_api_objects_assetratecardentry. Both inputs (BindingObjectId, the
     *   related asset) are fields on the AssetRateCardEntry row itself.
     */
    @TestVisible private static final Set<String> OWN_RECORD_FORMULAS = new Set<String>{
        'assetratecardentry.bindingobjectformula'
    };

    // Operator values with an unambiguous SOQL equivalent. The picklist also offers
    // Matches, DoesNotMatch, Contains, ExistsIn and DoesNotExistIn; those are left
    // out because their exact semantics in the decision-table engine (wildcards,
    // escaping, list delimiter, case sensitivity) are not established here, and a
    // guessed translation produces a confident wrong verdict. A table using one is
    // refused by name so it is obvious what to add.
    @TestVisible private static final Map<String, String> SOQL_OPERATORS = new Map<String, String>{
        'Equals' => '=',
        'NotEquals' => '!=',
        'GreaterThan' => '>',
        'GreaterOrEqual' => '>=',
        'LessThan' => '<',
        'LessOrEqual' => '<='
    };

    // The four above that compare ORDER rather than equality. SOQL will happily apply
    // them to text — it compares lexicographically — but the decision-table engine's
    // GreaterThan on a picklist plausibly means picklist DECLARATION order, and on an
    // Id or email it means nothing anyone intended. Two different orderings that
    // silently disagree is the same hazard that keeps MULTIPICKLIST out of the type
    // list and Contains/Matches out of the operator map, so these are allowed only on
    // types with one unambiguous ordering.
    @TestVisible private static final Set<String> ORDERING_OPERATORS = new Set<String>{
        'GreaterThan', 'GreaterOrEqual', 'LessThan', 'LessOrEqual'
    };

    // Operators that compare against null and therefore take no bind variable.
    @TestVisible private static final Map<String, String> NULL_OPERATORS = new Map<String, String>{
        'IsNull' => '=',
        'IsNotNull' => '!='
    };

    // Field types whose Value text converts to a bind with no ambiguity.
    // MULTIPICKLIST is excluded on purpose: SOQL '=' on a multi-select means an exact
    // match of the whole set, which is probably not what "Equals" means in the
    // decision-table engine. TEXTAREA, ENCRYPTEDSTRING and the rest are excluded
    // because they are not reliably filterable.
    private static final Set<Schema.DisplayType> TEXT_FIELD_TYPES = new Set<Schema.DisplayType>{
        Schema.DisplayType.STRING, Schema.DisplayType.PICKLIST, Schema.DisplayType.EMAIL,
        Schema.DisplayType.PHONE, Schema.DisplayType.URL, Schema.DisplayType.COMBOBOX
    };
    // ⚠ NOT text, though they look it. Binding a raw String to an Id field is a repo
    // DO NOT (.cursor/rules/apex-classes.mdc) and turns a malformed criterion into a
    // query-time exception — which this class would report as Unknown, when it should
    // have been a controlled refusal at translation. Coerced through Id.valueOf below.
    private static final Set<Schema.DisplayType> ID_FIELD_TYPES = new Set<Schema.DisplayType>{
        Schema.DisplayType.ID, Schema.DisplayType.REFERENCE
    };
    private static final Set<Schema.DisplayType> NUMBER_FIELD_TYPES = new Set<Schema.DisplayType>{
        Schema.DisplayType.INTEGER, Schema.DisplayType.LONG, Schema.DisplayType.DOUBLE,
        Schema.DisplayType.PERCENT
    };

    // Types whose COMPARISON VALUE this check cannot pin down, so no operator on them
    // is translated — not equality, not ordering. See translateCriterion for each one's
    // reason. Skipping widens the probe, which stays sound: both types move only when
    // their record is written.
    private static final Set<Schema.DisplayType> UNESTABLISHED_COMPARISON_TYPES =
        new Set<Schema.DisplayType>{ Schema.DisplayType.DATETIME, Schema.DisplayType.CURRENCY };

    /**
     * Every decision table with its sync state and, where it can be computed
     * correctly, whether it is stale relative to its own source rows.
     *
     * NOT cacheable, deliberately. With cacheable=true the client cache satisfied the
     * reload issued after a refresh completed, so the table snapped back to the
     * timestamps it held BEFORE the refresh — the rows visibly reverted from the new
     * sync time to the old one once polling ended. A component whose entire purpose
     * is reporting how current something is cannot serve a cached answer.
     */
    @AuraEnabled(cacheable=false)
    public static List<DecisionTableInfo> getDecisionTables() {
        List<DecisionTable> tables = [
            SELECT Id, DeveloperName, SetupName, Description, SourceObject, UsageType,
                   Status, Type, DataSourceType, ExecutionType, ConditionType,
                   FilterResultBy, UploadStatus, IsVersioned, DataSpaceName,
                   SourceConditionLogic, LastSyncDate, LastIncrementalSyncDate,
                   RefreshStatus, RefreshFailureReason, IsIncrementalSyncEnabled
            FROM DecisionTable
            WITH USER_MODE
            ORDER BY UsageType, SetupName
        ];

        Map<Id, List<DecisionTableSourceCriteria>> criteriaByTable = loadSourceCriteria(tables);
        // Resolved once: getGlobalDescribe is expensive and does not vary per table.
        Map<String, SObjectType> globalDescribe = Schema.getGlobalDescribe();

        // Plan every table's source query first, then run the distinct ones. Two
        // tables over the same object with the same filter share a single query.
        Map<Id, SourcePlan> planByTable = new Map<Id, SourcePlan>();
        Map<String, SourceProbe> probesByKey = new Map<String, SourceProbe>();
        Map<Id, Contributors> joinedObjectsByTable = loadJoinedObjects(tables, globalDescribe);
        for (DecisionTable dt : tables) {
            if (NON_SOBJECT_SOURCE_TYPES.contains(dt.DataSourceType) || String.isBlank(dt.SourceObject)) {
                continue; // no sObject behind it; handled by its own branch below
            }
            SourcePlan plan = planSource(dt, criteriaByTable.get(dt.Id), globalDescribe,
                joinedObjectsByTable.get(dt.Id));
            planByTable.put(dt.Id, plan);
            if (plan.probe != null) {
                probesByKey.put(plan.probe.key(), plan.probe);
            }
            if (plan.unfilteredProbe != null) {
                probesByKey.put(plan.unfilteredProbe.key(), plan.unfilteredProbe);
            }
            for (SourceProbe joined : plan.joinedProbes) {
                probesByKey.put(joined.key(), joined);
            }
        }
        Map<String, ProbeResult> probeResults = runProbes(probesByKey);

        // Iterate the EXPECTED tables, not the maps built above. A map cannot
        // contain what its query never returned, so walking the map would silently
        // validate only the tables that already succeeded.
        Datetime orgCreated = orgCreatedDate();
        Map<String, String> lookupTypes = loadLookupTypes(tables);

        List<DecisionTableInfo> results = new List<DecisionTableInfo>();
        for (DecisionTable dt : tables) {
            DecisionTableInfo info = new DecisionTableInfo(dt);
            info.sourceCriteria = describeCriteria(criteriaByTable.get(dt.Id));
            info.lookupType = lookupTypes.get(dt.SetupName);

            // Checked FIRST, and for every table whatever its source. A sync that
            // never happened, or that happened before this org existed, settles the
            // question on its own — comparing against a source cannot make a table
            // that was never built in this org fresh.
            String spinReason = neverBuiltInThisOrgReason(dt.LastSyncDate, orgCreated);
            if (spinReason != null) {
                info.staleness = STALENESS_STALE;
                info.stalenessReason = spinReason;
            } else if (NON_SOBJECT_SOURCE_TYPES.contains(dt.DataSourceType)) {
                info.staleness = STALENESS_UNCOMPUTED;
                info.stalenessReason = nonSobjectSourceReason(dt.DataSourceType, dt.UploadStatus);
            } else if (String.isBlank(dt.SourceObject)) {
                info.staleness = STALENESS_UNKNOWN;
                info.stalenessReason = 'Decision table has no source object.';
            } else {
                applySourceVerdict(info, dt, planByTable.get(dt.Id), probeResults);
            }
            results.add(info);
        }
        return results;
    }

    /**
     * Whether each table is a decision table or a decision matrix, by SetupName.
     *
     * CalculationMatrix is the storage behind both, and carries the one field that
     * tells them apart. The join is on Name, which holds the LABEL — matching on
     * DeveloperName finds almost nothing (2 of 40 on a stock build, where SetupName
     * matches 40 of 40).
     *
     * ⚠ Every row this component lists will say "Decision Table", because the
     * DecisionTable object only ever contains decision tables — the org's decision
     * matrices are not in it. It is shown in the details pane as context for what the
     * record is, and it is NOT a column: a column whose every cell reads the same is
     * the MasterLabel mistake. It starts telling you something only if this component
     * grows to list matrices too.
     *
     * Absent rather than guessed when it cannot be read, so the pane omits the field.
     */
    private static Map<String, String> loadLookupTypes(List<DecisionTable> tables) {
        Map<String, String> typeByLabel = new Map<String, String>();
        Set<String> labels = new Set<String>();
        for (DecisionTable dt : tables) {
            if (String.isNotBlank(dt.SetupName)) {
                labels.add(dt.SetupName);
            }
        }
        if (labels.isEmpty()) {
            return typeByLabel;
        }
        try {
            for (CalculationMatrix matrix : [
                SELECT Name, DecisionMatrixType
                FROM CalculationMatrix
                WHERE Name IN :labels
                WITH USER_MODE
            ]) {
                String readable = readableLookupType(matrix.DecisionMatrixType);
                // Name is unique on a stock build, but two rows sharing a label and
                // disagreeing would make the answer arbitrary — drop it instead.
                if (typeByLabel.containsKey(matrix.Name) && typeByLabel.get(matrix.Name) != readable) {
                    typeByLabel.put(matrix.Name, null);
                } else {
                    typeByLabel.put(matrix.Name, readable);
                }
            }
        } catch (Exception e) {
            // No read access to CalculationMatrix: the field is simply not shown.
            return new Map<String, String>();
        }
        return typeByLabel;
    }

    @TestVisible
    private static String readableLookupType(String decisionMatrixType) {
        if (decisionMatrixType == 'DecisionTable') {
            return 'Decision Table';
        }
        if (decisionMatrixType == 'DecisionMatrix') {
            return 'Decision Matrix';
        }
        // An unrecognised value is shown as-is rather than dropped or relabelled.
        return decisionMatrixType;
    }

    /**
     * When this org was created, used to catch tables carrying a sync that happened
     * somewhere else. Null if it cannot be read, which disables the check rather
     * than inventing a date every table would be measured against.
     */
    private static Datetime orgCreatedDate() {
        try {
            for (Organization org : [SELECT CreatedDate FROM Organization WITH USER_MODE LIMIT 1]) {
                return org.CreatedDate;
            }
        } catch (Exception e) {
            // Fall through: the spin check is skipped, the source comparison still runs.
        }
        return null;
    }

    /**
     * Why a table cannot have been built in THIS org, or null if it could have been.
     *
     * ⚠ This is the check that matters after a Trialforce spin. A new org from a
     * template inherits the template's decision tables INCLUDING their LastSyncDate,
     * so every table arrives looking synced while holding rows computed in a
     * different org against different data. The source comparison cannot see it —
     * the timestamp is real, it is just not from here — so a table can read Fresh in
     * an org where it has never once been refreshed. Comparing the sync against the
     * org's own creation date is what exposes that.
     *
     * Deliberately returns STALE rather than a softer verdict: the whole point of a
     * post-spin readiness check is to say out loud that these tables need refreshing.
     */
    @TestVisible
    private static String neverBuiltInThisOrgReason(Datetime lastSyncDate, Datetime orgCreated) {
        if (lastSyncDate == null) {
            return 'Never fully refreshed in this org.';
        }
        if (orgCreated != null && lastSyncDate < orgCreated) {
            return 'Last full sync (' + lastSyncDate.format() + ') predates this org, created ' +
                orgCreated.format() + '. An org spun from a template inherits the template\'s ' +
                'sync timestamp, so this table still holds rows built somewhere else — refresh it.';
        }
        return null;
    }

    /**
     * Why a table with no sObject behind it can never carry a computed verdict.
     *
     * Extracted so it can be tested: a stock build has no CsvUpload or
     * ContextDefinition table, so this branch is unreachable through the public
     * method and would otherwise ship with its wording and its UploadStatus
     * fallback never once executed.
     */
    @TestVisible
    private static String nonSobjectSourceReason(String dataSourceType, String uploadStatus) {
        if (dataSourceType == 'CsvUpload') {
            return 'Rows come from an uploaded CSV, not an sObject, so there is no source to ' +
                'compare against. Upload status: ' +
                (String.isBlank(uploadStatus) ? 'none recorded' : uploadStatus) + '.';
        }
        return 'Rows come from a Context Definition, not an sObject, so there is no source to compare against.';
    }

    /**
     * Turns one table's planned probe and its result into a verdict.
     *
     * Every path here ends in an explicit verdict with a reason. There is no
     * fall-through that leaves a table looking fresh because nothing set it.
     */
    @TestVisible
    private static void applySourceVerdict(
        DecisionTableInfo info,
        DecisionTable dt,
        SourcePlan plan,
        Map<String, ProbeResult> probeResults
    ) {
        if (plan == null) {
            info.staleness = STALENESS_UNKNOWN;
            info.stalenessReason = 'The source of this table was never checked.';
            return;
        }
        if (plan.probe == null) {
            info.staleness = plan.verdict;
            info.stalenessReason = plan.reason;
            return;
        }

        ProbeResult probed = probeResults.get(plan.probe.key());
        if (probed == null || !probed.ran) {
            // criteriaApplied is deliberately NOT set on this path. It means "the
            // verdict below was computed over the filtered rows", and there is no
            // verdict — setting it would caption an Unknown with "covers only these
            // rows" and would trip the invariant that criteriaApplied implies a
            // computed comparison.
            info.staleness = STALENESS_UNKNOWN;
            info.stalenessReason = 'Source object ' + dt.SourceObject + ' was not read: ' +
                (probed == null ? 'its source query was never run' : probed.failureReason) + '.';
            return;
        }
        info.criteriaApplied = plan.filtered;

        // A filtered probe compares only the rows the table actually holds, so say so
        // — a verdict computed over a subset must not read as if it covered the object.
        String scope = plan.filtered ? ' Compared against rows matching the source criteria.' : '';
        if (!plan.unreproducedCriteria.isEmpty()) {
            // Say it plainly: the comparison covered more rows than the table holds, so
            // a Stale here may belong to a row the table excludes. Fresh is unaffected.
            scope += ' ' + plan.unreproducedCriteria.size() + ' criterion(s) could not be ' +
                'reproduced, so this covers more rows than the table holds and their objects ' +
                'are watched instead.';
        }
        info.sourceRowCount = probed.rowCount;
        info.contributingObjects = plan.contributingObjects;
        info.unreproducedCriteria = plan.unreproducedCriteria;

        // No branch for LastSyncDate == null: getDecisionTables settles that before
        // reaching here, because a table that was never refreshed is stale whether or
        // not its source has rows. An empty PRIMARY means an empty table, which no
        // amount of change in a joined object can make stale, so that path is settled
        // on the primary alone.
        if (probed.newest == null) {
            info.sourceNewestChange = null;
            applyEmptySourceVerdict(info, plan, probeResults);
            return;
        }

        // The newest change across EVERY object this table reads, not just its own.
        Datetime newest = probed.newest;
        String driver = dt.SourceObject;
        List<String> unread = new List<String>(plan.unreadableContributors);
        for (SourceProbe joined : plan.joinedProbes) {
            ProbeResult joinedResult = probeResults.get(joined.key());
            if (joinedResult == null || !joinedResult.ran) {
                unread.add(joined.objectName);
                continue;
            }
            if (joinedResult.newest != null && joinedResult.newest > newest) {
                newest = joinedResult.newest;
                driver = joined.objectName;
            }
        }
        info.sourceNewestChange = newest;

        String alsoReads = plan.contributingObjects.isEmpty()
            ? ''
            : ' This table also reads ' + String.join(plan.contributingObjects, ', ') + '.';

        if (dt.LastSyncDate < newest) {
            // Stale stands even with an unread contributor: another unseen change could
            // only add to it.
            info.staleness = STALENESS_STALE;
            // ⚠ "or an automated process" is load-bearing, not padding. The witness is
            // SystemModstamp, which a background process moves without any user edit —
            // so someone who reads "changed" and goes looking in field history can find
            // nothing and conclude the tool is wrong. Say what the timestamp means.
            info.stalenessReason = driver + ' was changed by a user or an automated ' +
                'process at ' + newest.format() + ', after the last full sync.' + scope;
        } else if (!unread.isEmpty() || plan.contributorsUnenumerable) {
            // Fresh does NOT stand: something that could have changed was not read, so
            // there is no basis for an all-clear. Two different gaps reach here — a
            // named dependency that could not be checked, and a dependency list that
            // could not be built at all — and the reason says which, because the fix
            // differs (grant access to that object vs. to DecisionTableParameter).
            List<String> gaps = new List<String>();
            if (!unread.isEmpty()) {
                gaps.add(String.join(unread, ', ') + ' could not be checked, and this table reads from it');
            }
            if (plan.contributorsUnenumerable) {
                gaps.add('the objects this table assembles its columns from could not be listed');
            }
            info.staleness = STALENESS_UNCOMPUTED;
            info.stalenessReason = 'Nothing readable has changed since the last sync, but ' +
                String.join(gaps, ', and ') + ' — so freshness cannot be confirmed.';
        } else {
            info.staleness = STALENESS_FRESH;
            info.stalenessReason = 'The last full sync is later than the newest change in ' +
                'every object this table reads.' + alsoReads + scope;
        }
    }

    /**
     * The verdict when the probe found no newest change — the one place an ABSENCE
     * of evidence becomes a verdict, so it is the place to be careful.
     *
     * ⚠ On a FILTERED probe, "no rows matched" has two causes that look identical
     * from here: the filter genuinely matches nothing, or the translation
     * over-restricted and excluded rows it should have kept (a picklist label bound
     * where SOQL wants the API name, a datetime parsed in the wrong zone, any future
     * coercion that parses cleanly and binds the wrong thing). Calling that Fresh
     * would hard-code the exact outcome every refusal in this class exists to avoid.
     *
     * The unfiltered probe of the same object settles it: if the object holds no rows
     * at all, there is nothing for a filter to over-restrict and the zero is
     * trustworthy. If the object HAS rows and the filter matched none of them, the two
     * causes stay indistinguishable and the table gets no verdict.
     *
     * Note what is NOT claimed even in the trustworthy case: an empty source proves
     * nothing has changed since the last sync, not that the table is itself empty. A
     * table synced while rows existed still holds them, and no timestamp can reveal
     * that — the deletion blindness the class header documents for every verdict.
     */
    private static void applyEmptySourceVerdict(
        DecisionTableInfo info,
        SourcePlan plan,
        Map<String, ProbeResult> probeResults
    ) {
        if (!plan.filtered) {
            info.staleness = STALENESS_FRESH;
            info.stalenessReason = 'No visible row in the source object has changed since the last sync.';
            return;
        }

        ProbeResult wholeObject = plan.unfilteredProbe == null
            ? null
            : probeResults.get(plan.unfilteredProbe.key());

        // The disambiguating probe may not have run — the query cap does not keep a
        // filtered probe and its partner together, and either can throw on its own.
        // Say that, rather than asserting the object holds rows when nothing counted
        // them: claiming more than the evidence supports is the defect this whole
        // method exists to fix.
        if (wholeObject == null || !wholeObject.ran) {
            info.staleness = STALENESS_UNCOMPUTED;
            info.stalenessReason = 'No source rows match the reproduced criteria, and the ' +
                'whole-object check that would tell a genuinely empty source from a filter ' +
                'translated too narrowly did not run (' +
                (wholeObject == null ? 'it was never planned' : wholeObject.failureReason) +
                ') — so no verdict.';
            return;
        }

        if (wholeObject.rowCount == 0) {
            info.staleness = STALENESS_FRESH;
            info.stalenessReason = 'The source object holds no visible rows at all, so the criteria ' +
                'excluded nothing and no visible row has changed since the last sync.';
            return;
        }

        info.staleness = STALENESS_UNCOMPUTED;
        info.stalenessReason = 'No source rows match the reproduced criteria, but the object does ' +
            'hold rows. That is either a filter that genuinely matches nothing or a criterion ' +
            'translated too narrowly, and the two cannot be told apart here — so no verdict.';
    }

    /**
     * Raw source criteria per decision table, in sequence order. Absence of a key
     * means the table has no criteria, which is what makes an unfiltered comparison
     * valid for it.
     */
    private static Map<Id, List<DecisionTableSourceCriteria>> loadSourceCriteria(List<DecisionTable> tables) {
        Map<Id, List<DecisionTableSourceCriteria>> byTable = new Map<Id, List<DecisionTableSourceCriteria>>();
        if (tables.isEmpty()) {
            return byTable;
        }
        for (DecisionTableSourceCriteria c : [
            SELECT DecisionTableId, SourceFieldName, Operator, Value, ValueType
            FROM DecisionTableSourceCriteria
            WHERE DecisionTableId IN :tables
            WITH USER_MODE
            ORDER BY DecisionTableId, SequenceNumber
        ]) {
            if (!byTable.containsKey(c.DecisionTableId)) {
                byTable.put(c.DecisionTableId, new List<DecisionTableSourceCriteria>());
            }
            byTable.get(c.DecisionTableId).add(c);
        }
        return byTable;
    }

    /**
     * Objects OTHER than its own source that each table reads columns from, whose
     * changes therefore count against the table's freshness.
     *
     * DecisionTableParameter is the table's column definition, and DomainObject names
     * the object each column comes from. A parameter whose DomainObject is not the
     * table's SourceObject is a join: the column's value is pulled across a lookup
     * (FieldPath like RateCardEntryId.RateUnitOfMeasureName) and materialised into the
     * synced table, so editing the joined record changes what the table should hold.
     *
     * Measured on a stock build: all 12 MultipleSobjects tables do this — 33 of their
     * 89 parameters point off-primary — while every table still declares exactly one
     * DecisionTableDatasetLink, which is why the source object alone looks sufficient
     * and is not.
     *
     * ⚠ DomainObject alone is NOT the whole dependency. It names the object that owns
     * the FINAL field in the path, so every INTERMEDIATE object a multi-hop FieldPath
     * passes through goes unnamed — and re-pointing an intermediate's lookup changes
     * what a refresh materialises while moving only that intermediate's timestamp.
     * Measured on a stock build: 13 parameters traverse two hops, and 5 tables (both
     * Asset rate-adjustment pairs, both Binding Object ones, and Asset Action Source
     * Entries V2) depend on an intermediate — AssetRateCardEntry,
     * BindingObjectRateCardEntry, AssetAction — that DomainObject never mentions. So
     * every hop is resolved from FieldPath as well, through the same walk the criteria
     * use.
     *
     * Marked rather than assumed when the query fails: the scan flags the tables whose
     * dependencies it could not enumerate instead of returning an empty map, which
     * would silently restore the primary-only comparison this exists to replace.
     */
    private static Map<Id, Contributors> loadJoinedObjects(
        List<DecisionTable> tables, Map<String, SObjectType> globalDescribe
    ) {
        Map<Id, Contributors> byTable = new Map<Id, Contributors>();
        if (tables.isEmpty()) {
            return byTable;
        }
        Map<Id, DecisionTable> tableById = new Map<Id, DecisionTable>(tables);
        for (DecisionTable dt : tables) {
            byTable.put(dt.Id, new Contributors());
        }
        try {
            for (DecisionTableParameter param : [
                SELECT DecisionTableId, FieldPath, DomainObject
                FROM DecisionTableParameter
                WHERE DecisionTableId IN :tables
                WITH USER_MODE
            ]) {
                DecisionTable dt = tableById.get(param.DecisionTableId);
                if (dt == null) {
                    continue;
                }
                recordContributor(byTable.get(param.DecisionTableId), dt.SourceObject,
                    param.DomainObject, param.FieldPath, globalDescribe);
            }
        } catch (Exception e) {
            // Whatever was collected before the failure stays — it is still a real
            // dependency — but EVERY table is flagged, so Fresh is withheld until the
            // scan can run.
            //
            // ⚠ This was once scoped to MultipleSobjects, on the reasoning that
            // DataSourceType is the platform's statement about how many objects feed a
            // table, and that all 28 SingleSobject tables measured had zero off-primary
            // parameters. That measurement describes one org's inventory, not the
            // schema: the v67 Metadata API reference ships a SingleSobject decision
            // table whose sourceObject is WorkBadgeDefinition and whose parameter has
            // domainObject=AccountFeed. So a SingleSobject table CAN read off-primary,
            // and exempting it would have reinstated the primary-only comparison for
            // exactly the tables nobody was watching.
            for (DecisionTable dt : tables) {
                byTable.get(dt.Id).unenumerable = true;
            }
        }
        return byTable;
    }

    /**
     * What ONE column definition says this table depends on.
     *
     * Split out of the query loop so it can be tested with supplied values:
     * DecisionTableParameter is a setup object whose rows cannot be inserted in a test,
     * so this is the only way the multi-hop resolution gets covered by anything other
     * than whatever the running org happens to contain.
     */
    @TestVisible
    private static void recordContributor(
        Contributors found,
        String primary,
        String domainObject,
        String fieldPath,
        Map<String, SObjectType> globalDescribe
    ) {
        // ⚠ DomainObject holds the literal four-character STRING 'null' for a column
        // that comes from the table's own object — 206 of 309 parameters on a stock
        // build, against 14 that are a genuine SQL null. String.isBlank does not catch
        // 'null', so without this every such table is refused for reading an object
        // called "null" (StandardTax was, before a live run caught it).
        Boolean offPrimary = String.isNotBlank(domainObject)
            && domainObject != 'null' && domainObject != primary;
        if (offPrimary) {
            found.objects.add(domainObject);
        }

        String path = fieldPath == null ? '' : fieldPath.trim();
        SObjectType sot = globalDescribe.get(primary);
        if (sot == null) {
            found.unresolvedPaths.add(String.isBlank(path) ? domainObject : path);
            return;
        }
        Map<String, SObjectField> sourceFields = sot.getDescribe().fields.getMap();

        if (!path.contains('.')) {
            // ⚠ An off-primary column whose path names no hop leaves the ROUTE to that
            // object unexplained — the final object is watched, anything on the way to
            // it is not. Measured zero on a stock build, so failing closed costs nothing
            // today; if the shape ever appears, a refusal is the honest answer until
            // someone works out what the join actually is.
            if (offPrimary) {
                found.unresolvedPaths.add(path + ' (reads ' + domainObject +
                    ', but the path names no route to it)');
                return;
            }
            // A same-object column: the primary probe already covers it, unless the
            // field's own value can move without the record being edited.
            if (movesWithoutARecordEdit(primary, sourceFields.get(path.toLowerCase()))) {
                found.unresolvedPaths.add(path + ' (' + UNWATCHABLE_FIELD + ')');
            }
            return;
        }

        ResolvedPath resolved = resolvePath(path, sourceFields);
        if (resolved.objects == null || resolved.objects.isEmpty()) {
            // A dependency that is real but cannot be named: recorded so the verdict
            // declines an all-clear rather than ignoring it.
            found.unresolvedPaths.add(path);
            return;
        }
        if (movesWithoutARecordEdit(resolved.objects[resolved.objects.size() - 1], resolved.terminal)) {
            found.unresolvedPaths.add(path + ' (' + UNWATCHABLE_FIELD + ')');
            // The gap already blocks Fresh, but the objects this path crosses are still
            // real dependencies — watch them anyway so an edit to one can still prove
            // the table STALE. Returning here instead would trade a recoverable verdict
            // for nothing.
            found.objects.addAll(resolved.objects);
            return;
        }
        // ⚠ A hop back to the table's OWN object is kept, not dropped as redundant. The
        // primary probe may be FILTERED by source criteria, in which case it measures
        // only the rows the table holds — and a self-referential column materialises a
        // field from a row that may sit OUTSIDE that filter. Same object, different row
        // set. Where the primary probe is unfiltered the two dedupe by probe key, so
        // keeping it costs nothing there.
        found.objects.addAll(resolved.objects);
    }

    /** Human-readable "field Operator value" strings for the row-details panel. */
    private static List<String> describeCriteria(List<DecisionTableSourceCriteria> criteria) {
        List<String> described = new List<String>();
        if (criteria == null) {
            return described;
        }
        for (DecisionTableSourceCriteria c : criteria) {
            String text = c.SourceFieldName + ' ' + c.Operator;
            if (String.isNotBlank(c.Value)) {
                text += ' ' + c.Value;
            }
            described.add(text);
        }
        return described;
    }

    /**
     * Decides how (or whether) one table's source can be measured.
     *
     * Returns a plan carrying either a runnable probe or the verdict and reason for
     * refusing.
     *
     * Translation is PARTIAL BY DESIGN: a criterion that cannot be reproduced is
     * dropped and the objects it reads are probed instead, so the query covers a
     * SUPERSET of the table's rows. That is sound only because isPlainConjunction has
     * already proved the criteria are ANDed — dropping a conjunct can then only widen —
     * and only for criteria whose membership is pinned to record state. The ones that
     * are not are refused outright (see TranslatedCriterion.mustRefuse), which is why
     * this is partial rather than approximate: nothing is ever guessed at.
     */
    @TestVisible
    private static SourcePlan planSource(
        DecisionTable dt,
        List<DecisionTableSourceCriteria> criteria,
        Map<String, SObjectType> globalDescribe,
        Contributors contributors
    ) {
        SourcePlan plan = new SourcePlan();
        // Copied, never mutated in place: the caller's map is shared across tables, and
        // criteria watch objects below are this table's alone.
        Set<String> joinedObjects = contributors == null
            ? new Set<String>()
            : new Set<String>(contributors.objects);
        if (contributors != null) {
            plan.contributorsUnenumerable = contributors.unenumerable;
            plan.unreadableContributors.addAll(contributors.unresolvedPaths);
        }

        // Resolve through the global describe so only a real, accessible sObject
        // name can ever reach the dynamic query.
        SObjectType sot = globalDescribe.get(dt.SourceObject);
        if (sot == null) {
            plan.verdict = STALENESS_UNKNOWN;
            plan.reason = 'Source object ' + dt.SourceObject + ' does not exist in this org.';
            return plan;
        }
        DescribeSObjectResult dsr = sot.getDescribe();
        if (!dsr.isQueryable() || !dsr.isAccessible()) {
            plan.verdict = STALENESS_UNKNOWN;
            plan.reason = 'You do not have read access to ' + dsr.getName() + '.';
            return plan;
        }
        Map<String, SObjectField> fields = dsr.fields.getMap();
        if (!fields.containsKey(WITNESS_FIELD.toLowerCase())) {
            plan.verdict = STALENESS_UNKNOWN;
            plan.reason = dsr.getName() + ' has no ' + WITNESS_FIELD + ' to compare against.';
            return plan;
        }

        SourceProbe probe = new SourceProbe();
        // dsr.getName() is the platform's own name for the type, never the stored
        // string, so the query text cannot be injected.
        probe.objectName = dsr.getName();

        if (criteria != null && !criteria.isEmpty()) {
            // Anything other than a plain AND over every criterion is not reproduced
            // here, and AND-ing it anyway would answer a different question.
            if (!isPlainConjunction(dt.SourceConditionLogic, criteria.size())) {
                plan.verdict = STALENESS_UNCOMPUTED;
                plan.reason = 'Source criteria combine with logic this check does not reproduce (' +
                    dt.SourceConditionLogic.trim() + ').';
                return plan;
            }

            // ⚠ Criteria that cannot be reproduced are SKIPPED, not fatal — but only
            // because isPlainConjunction above proved they are ANDed. Dropping a
            // conjunct can only widen the row set, so the probe measures a SUPERSET of
            // the table's rows: a newest change that predates the sync still proves
            // nothing in the real set changed, and the only possible error is reporting
            // Stale for a change to a row the table excludes. Under OR logic dropping a
            // term could NARROW instead, which is unsound — hence the earlier gate.
            List<String> clauses = new List<String>();
            List<String> skipped = new List<String>();
            List<String> blockers = new List<String>();
            Set<String> watch = new Set<String>();
            Integer bindIndex = 0;
            for (DecisionTableSourceCriteria c : criteria) {
                TranslatedCriterion translated = translateCriterion(
                    c, dsr.getName(), fields, probe.binds, bindIndex);
                bindIndex++;
                if (translated.clause != null) {
                    clauses.add(translated.clause);
                    continue;
                }
                if (translated.mustRefuse) {
                    blockers.add(translated.reason);
                } else {
                    skipped.add(translated.reason);
                    watch.addAll(translated.watchObjects);
                }
            }
            if (!blockers.isEmpty()) {
                plan.verdict = STALENESS_UNCOMPUTED;
                plan.reason = 'Source is filtered by criteria this check can neither reproduce nor ' +
                    'watch — ' + String.join(blockers, '; ') + '. Compare manually.';
                return plan;
            }
            probe.whereClause = String.join(clauses, ' AND ');
            plan.filtered = !clauses.isEmpty();
            plan.unreproducedCriteria = skipped;
            // Watched objects join the contributing set, so a change that moves rows
            // through the unreproduced filter still shows up in the verdict.
            joinedObjects.addAll(watch);

            // A second, UNFILTERED probe of the same object, used only to disambiguate
            // a filtered probe that finds nothing. "No rows match the filter" has two
            // causes that look identical — the filter genuinely matches nothing, or the
            // translation over-restricted and excluded rows it should have kept. If the
            // object itself is empty, there is nothing for a filter to over-restrict and
            // the zero is trustworthy; if the object HAS rows, it is not. Costs one
            // query per distinct object, and dedupes against any unfiltered probe
            // another table already registered for it.
            SourceProbe unfiltered = new SourceProbe();
            unfiltered.objectName = probe.objectName;
            plan.unfilteredProbe = unfiltered;
        }

        plan.probe = probe;

        // ⚠ A table's freshness depends on EVERY object it reads, not just the one its
        // rows come from. A MultipleSobjects table pulls columns across a lookup
        // (RateCardEntryId.RateUnitOfMeasureName) and materialises them, so editing the
        // joined record changes what the table should hold while no primary row is
        // touched and the primary timestamp does not move — the same blindness that
        // makes a traversing criterion unreproducible.
        //
        // So probe each contributing object too and compare the sync against the NEWEST
        // change across all of them. This is a stronger claim than the primary alone:
        // Fresh comes to mean "nothing in anything this table reads has changed". It
        // also catches contract activation, which writes the Contract row while
        // leaving every tier row untouched.
        //
        // The probes are unfiltered and therefore over-broad — any edit to a shared
        // object marks every table reading it stale. That is the safe direction (an
        // unnecessary refresh, not a false all-clear) and measured at zero occurrences
        // on a stock build, because builds load data and THEN refresh. If it ever gets
        // noisy, scope each one to referenced rows with a semi-join.
        List<String> named = new List<String>(joinedObjects);
        named.sort();
        for (String joined : named) {
            // A self-referential dependency on an UNFILTERED primary is genuinely
            // redundant — the primary probe already covers every row of that object —
            // so it is dropped here rather than listed as something extra the table
            // reads. When the primary probe is filtered it is NOT redundant, and the
            // unfiltered probe below is exactly what catches an out-of-filter row.
            if (!plan.filtered && joined == dsr.getName()) {
                continue;
            }
            SObjectType joinedType = globalDescribe.get(joined);
            if (joinedType == null) {
                // Named as a dependency but not resolvable — a DomainObject value that
                // is not an object in this org, or one this user cannot see at all.
                // Recorded like any other unreadable contributor rather than dropped:
                // "cannot check this" must not be quieter than "checked it".
                plan.unreadableContributors.add(joined);
                continue;
            }
            DescribeSObjectResult joinedDsr = joinedType.getDescribe();
            if (!joinedDsr.isQueryable() || !joinedDsr.isAccessible()
                    || !joinedDsr.fields.getMap().containsKey(WITNESS_FIELD.toLowerCase())) {
                // Recorded as contributing but unprobeable: the verdict below
                // refuses to claim Fresh rather than ignoring it.
                plan.unreadableContributors.add(joined);
                continue;
            }
            SourceProbe joinedProbe = new SourceProbe();
            joinedProbe.objectName = joinedDsr.getName();
            plan.joinedProbes.add(joinedProbe);
            plan.contributingObjects.add(joinedDsr.getName());
        }
        return plan;
    }

    /**
     * Whether SourceConditionLogic means "every criterion, ANDed together".
     *
     * Accepts a bare conjunction over each criterion's sequence number exactly once
     * ("1", "1 AND 2", "2 AND 1"). Order does not matter because AND commutes, but
     * COVERAGE does: requiring the full set is what stops "1 AND 2" being accepted
     * for a table that actually has three criteria, which would drop one silently.
     *
     * Default-deny: anything this does not positively recognise — an OR, a NOT, a
     * parenthesis, a token that is not a number — returns false and the table is
     * reported "Not comparable" rather than measured against the wrong row set.
     */
    @TestVisible
    private static Boolean isPlainConjunction(String logic, Integer criteriaCount) {
        // Blank means the platform recorded no logic, which is a plain conjunction.
        if (String.isBlank(logic)) {
            return true;
        }
        String normalized = logic.trim().toUpperCase();
        if (normalized.contains('(') || normalized.contains(')')
                || normalized.contains(' OR ') || normalized.contains('NOT ')) {
            return false;
        }
        Set<Integer> referenced = new Set<Integer>();
        for (String part : normalized.split('AND')) {
            String token = part.trim();
            if (!token.isNumeric()) {
                return false;
            }
            referenced.add(Integer.valueOf(token));
        }
        // Every criterion must be referenced, and nothing beyond them.
        if (referenced.size() != criteriaCount) {
            return false;
        }
        for (Integer sequence = 1; sequence <= criteriaCount; sequence++) {
            if (!referenced.contains(sequence)) {
                return false;
            }
        }
        return true;
    }

    /**
     * One source criterion as a bound SOQL clause, or a reason it was refused.
     *
     * Refusing is the safe outcome — it downgrades the table to "Not comparable".
     * Guessing is not: it produces a verdict that looks computed and is wrong.
     */
    private static TranslatedCriterion translateCriterion(
        DecisionTableSourceCriteria c,
        String sourceObject,
        Map<String, SObjectField> fields,
        Map<String, Object> binds,
        Integer bindIndex
    ) {
        TranslatedCriterion out = new TranslatedCriterion();

        String path = c.SourceFieldName == null ? '' : c.SourceFieldName.trim();
        if (String.isBlank(path)) {
            // Nothing to watch: an unnamed field cannot be resolved to an object, so
            // skipping it would drop a filter whose movement nothing observes.
            out.mustRefuse = true;
            out.reason = 'a criterion has no field name';
            return out;
        }
        // ⚠ SKIPPING IS ONLY SOUND WHEN THE FILTER ITSELF CANNOT MOVE.
        //
        // Dropping an AND-ed conjunct widens the row set, and a MAX over a superset
        // that predates the sync proves nothing in the real set changed — but ONLY
        // because membership in the real set is a function of RECORD STATE, which some
        // probed timestamp witnesses. A non-literal Value breaks that premise:
        // Parameter, Formula and Lookup values resolve when the table is refreshed, so
        // the boundary can move with no record edited anywhere. A Formula criterion
        // meaning "StartDate <= TODAY" admits a new row the moment the date passes;
        // every probe still reads Fresh over a table that is genuinely stale.
        //
        // There is no timestamp to watch for that, so it is refused rather than
        // skipped. Checked BEFORE the traversal branch below, because watching the
        // objects a path reaches across does not cover the boundary moving either.
        // IsNull/IsNotNull are exempt: they compare against no value at all, so their
        // membership stays a function of record state whatever ValueType is stamped.
        if (c.ValueType != VALUE_TYPE_LITERAL && !NULL_OPERATORS.containsKey(c.Operator)) {
            out.mustRefuse = true;
            out.reason = '"' + path + '" compares against a ' +
                (String.isBlank(c.ValueType) ? 'value of unknown type' : c.ValueType + ' value') +
                ' rather than a literal, and a value that resolves at refresh time can ' +
                'change the rows without changing any record';
            return out;
        }
        // ⚠ A parent edit moves rows into and out of this filter without writing any
        // child row, so reproducing the filter and comparing child
        // timestamps would read FRESH exactly when the table went stale.
        //
        // The filter is therefore not reproduced — but the objects it reaches across
        // ARE probed, so the change itself stays visible. Dropping an AND-ed conjunct
        // only widens the row set, and a MAX over a superset that predates the sync
        // still proves nothing in the real set changed; the error can only be an
        // over-report of Stale. That is sound where reproducing the filter was not.
        if (path.contains('.')) {
            ResolvedPath resolved = resolvePath(path, fields);
            if (resolved.objects == null || resolved.objects.isEmpty()) {
                // The objects cannot be named, so they cannot be watched, and dropping
                // the criterion would leave the change genuinely invisible.
                out.mustRefuse = true;
                out.reason = '"' + path + '" reads a field on a related record that cannot be resolved';
                return out;
            }
            // Watching the objects the path crosses does not cover a field whose value
            // moves without any of them being edited.
            if (movesWithoutARecordEdit(resolved.objects[resolved.objects.size() - 1], resolved.terminal)) {
                out.mustRefuse = true;
                out.reason = '"' + path + '" ends on a field whose value ' + UNWATCHABLE_FIELD +
                    ', so nothing here can observe it changing';
                return out;
            }
            out.watchObjects = resolved.objects;
            out.reason = '"' + path + '" reads a field on ' + String.join(resolved.objects, ', ') +
                ', so it is watched instead of reproduced';
            return out;
        }
        SObjectField field = fields.get(path.toLowerCase());
        if (field == null) {
            out.reason = 'field "' + path + '" does not exist on the source object';
            return out;
        }
        DescribeFieldResult fdr = field.getDescribe();
        // ⚠ Refused, not skipped, for the same reason a non-literal Value is: skipping
        // is sound only while membership is a function of record state, and a formula's
        // value moves when something this check cannot see moves. Applies to IsNull too
        // — the operator consumes no value, but the FIELD still shifts underneath it.
        //
        // ⚠ ORDER MATTERS, and it was wrong: this ran AFTER the isAccessible check
        // below, so a formula the running user cannot read took the accessible-field
        // exit and was SKIPPED — widening the probe around a field whose movement
        // nothing observes. Unwatchability is a property of the field itself, not of
        // who can see it, so it has to be decided first.
        if (movesWithoutARecordEdit(sourceObject, field)) {
            out.mustRefuse = true;
            out.reason = 'field "' + path + '" has a value that ' + UNWATCHABLE_FIELD +
                ', so nothing here can observe it changing';
            return out;
        }
        if (!fdr.isAccessible()) {
            out.reason = 'you cannot read field "' + path + '"';
            return out;
        }
        if (!fdr.isFilterable()) {
            out.reason = 'field "' + path + '" cannot be filtered in a query';
            return out;
        }

        if (NULL_OPERATORS.containsKey(c.Operator)) {
            out.clause = fdr.getName() + ' ' + NULL_OPERATORS.get(c.Operator) + ' null';
            return out;
        }
        if (!SOQL_OPERATORS.containsKey(c.Operator)) {
            out.reason = 'operator "' + c.Operator + '" has no unambiguous SOQL equivalent';
            return out;
        }
        if (ORDERING_OPERATORS.contains(c.Operator) && !isOrderedType(fdr.getType())) {
            out.reason = 'operator "' + c.Operator + '" compares order, and ' + fdr.getType() +
                ' has no ordering that SOQL and the decision table are guaranteed to agree on';
            return out;
        }
        // ⚠ EVERY comparison on these types, not just the ordering ones. isOrderedType
        // excludes both for a reason that condemns equality just as hard, and refusing
        // only ordering was an inconsistency the review caught twice — once per type:
        //   DATETIME — Datetime.valueOf parses in the RUNNING USER'S timezone, and the
        //     zone the engine reads its boundary in is unestablished.
        //   CURRENCY — in a multicurrency org the stored amount, the corporate-currency
        //     amount and the converted amount are three different numbers, and which one
        //     the engine compares is unestablished.
        // Either way a boundary bound to the wrong value selects a different NONEMPTY
        // row set, which the zero-result safeguard cannot catch, and the probe then
        // measures rows the table does not hold.
        if (UNESTABLISHED_COMPARISON_TYPES.contains(fdr.getType())) {
            out.reason = 'field "' + path + '" is a ' + fdr.getType() +
                ', and how the decision-table engine reads its comparison value is not ' +
                'established here';
            return out;
        }

        Object bound = coerceValue(fdr, c.Value);
        if (bound == null) {
            out.reason = 'value "' + c.Value + '" cannot be read as ' + fdr.getType();
            return out;
        }
        // Checked after coercion so the value is already trimmed, and before the clause
        // is built so a label-for-API-name mistake never reaches SOQL.
        String picklistProblem = picklistValueProblem(fdr, String.valueOf(bound));
        if (picklistProblem != null) {
            out.reason = picklistProblem;
            return out;
        }
        // A generated bind name, never anything derived from stored text.
        String bindName = 'dtCriterion' + bindIndex;
        binds.put(bindName, bound);
        out.clause = fdr.getName() + ' ' + SOQL_OPERATORS.get(c.Operator) + ' :' + bindName;
        return out;
    }

    /**
     * Every object a criterion's field path reaches across, or null if the path cannot
     * be walked.
     *
     * ContractItemPriceId.ContractId.StatusCode yields [ContractItemPrice, Contract] —
     * BOTH, because a change to either can move a row into or out of the filter. The
     * stored segments are FIELD names (ContractItemPriceId), not relationship names, so
     * each hop is resolved through the describe rather than by trimming "Id".
     *
     * Null on anything it cannot resolve — an unknown field, a non-reference segment,
     * or a POLYMORPHIC lookup, which points at several objects and so has no single
     * thing to watch. Null makes the caller refuse rather than watch the wrong object.
     */
    @TestVisible
    private static List<String> traversedObjects(String path, Map<String, SObjectField> sourceFields) {
        List<String> objects = resolvePath(path, sourceFields).objects;
        return (objects == null || objects.isEmpty()) ? null : objects;
    }

    /**
     * One walk of a field path, answering BOTH questions any caller has: which objects
     * it crosses, and which field it lands on.
     *
     * Deliberately one walker rather than two. The hops and the terminal are read by
     * different callers for different reasons, and two loops that must agree about what
     * a path means is exactly the divergence this class keeps finding in other people's
     * code.
     */
    private static ResolvedPath resolvePath(String path, Map<String, SObjectField> sourceFields) {
        ResolvedPath resolved = new ResolvedPath();
        List<String> segments = path.split('\\.');
        // ⚠ Apex drops trailing empties, so "." splits to an EMPTY list and the terminal
        // lookup below would be segments[-1]. Left unguarded this refactor would have
        // turned a refusal into an uncaught exception for the whole page.
        if (segments.isEmpty()) {
            return resolved;
        }
        Map<String, SObjectField> currentFields = sourceFields;
        List<String> objects = new List<String>();
        // The last segment is the field itself, not a hop.
        for (Integer i = 0; i < segments.size() - 1; i++) {
            SObjectField hop = currentFields.get(segments[i].trim().toLowerCase());
            if (hop == null) {
                return resolved;
            }
            DescribeFieldResult hopDescribe = hop.getDescribe();
            List<SObjectType> targets = hopDescribe.getReferenceTo();
            if (hopDescribe.getType() != Schema.DisplayType.REFERENCE || targets.size() != 1) {
                return resolved;
            }
            DescribeSObjectResult target = targets[0].getDescribe();
            objects.add(target.getName());
            currentFields = target.fields.getMap();
        }
        resolved.objects = objects;
        // Null when the path names a field that does not exist on whatever it landed on.
        resolved.terminal = currentFields.get(segments[segments.size() - 1].trim().toLowerCase());
        return resolved;
    }

    /**
     * Whether a field's value can move WITHOUT its own record being edited.
     *
     * This is the soundness condition the whole class rests on: every verdict compares
     * MAX(WITNESS_FIELD), so a field that moves while that stamp does not is
     * invisible to every probe. Two kinds qualify, and the second was missed for a
     * round because the check was written for the first.
     *
     * ⚠ FORMULAS are evaluated when read, so a materialised formula's value moves when
     * a cross-object input changes, or when TODAY()/NOW() rolls over — with nothing
     * edited. Apex cannot see what a formula reads: DescribeFieldResult exposes no body,
     * and the REST describe returns calculatedFormula = null for the standard formula
     * fields this actually hits (AssetRateCardEntry.BindingObjectFormula, measured). So
     * the dependency cannot be enumerated, only recorded as a gap.
     *
     * ⚠ PLATFORM-MAINTAINED fields move by other means entirely, and isCalculated() is
     * FALSE for all of them (measured on Account/Opportunity/Contact/Product2):
     *   - LastViewedDate / LastReferencedDate — advance when a user merely looks,
     *     and measured NOT to move SystemModstamp, so nothing else here sees them.
     *
     * LastActivityDate was here until the witness swap and is not any more: it moves
     * the record's SystemModstamp, so denying it was over-refusal. See
     * PLATFORM_MAINTAINED_FIELDS for that measurement and the reasoning.
     *
     * ⚠ UNVERIFIED: roll-up summary fields are the other canonical member of this class
     * — a child edit moves the parent's rollup while touching only the child's
     * timestamp. Whether they are already covered turns on isCalculated() returning true
     * for them, which could not be checked: this org has no roll-up summary field on any
     * object queried. Settle with, on an org that has one:
     *   Schema.SObjectType.<Obj>.fields.<Rollup>.getDescribe().isCalculated()
     * True means covered; false means it belongs beside the names below.
     */
    private static Boolean movesWithoutARecordEdit(String owningObject, SObjectField field) {
        if (field == null) {
            return false;
        }
        DescribeFieldResult described = field.getDescribe();
        String fieldName = described.getName().toLowerCase();
        if (PLATFORM_MAINTAINED_FIELDS.contains(fieldName)) {
            return true;
        }
        if (!described.isCalculated()) {
            return false;
        }
        // A formula whose inputs the platform documents as own-record: an edit to any of
        // them writes this row, so WITNESS_FIELD sees it after all.
        String key = (owningObject == null ? '' : owningObject.toLowerCase()) + '.' + fieldName;
        return !OWN_RECORD_FORMULAS.contains(key);
    }

    /**
     * Types where BOTH the ordering and the bound boundary value are unambiguous.
     *
     * ⚠ DATETIME is excluded even though its ordering is obvious, because the boundary
     * is not: Datetime.valueOf parses in the RUNNING USER'S timezone, and the zone the
     * decision-table engine reads its own literal in is not established. An offset
     * between them shifts the boundary by hours, silently including or excluding rows
     * around it — and excluding the newest changed row reports Fresh while stale. The
     * class's bar is a translation that is provably faithful; an unestablished parse
     * zone does not clear it, so this refuses until it is settled live.
     *
     * CURRENCY is excluded for the sibling reason: in a multicurrency org SOQL compares
     * a bare bound number against amounts in each record's own currency, and whether
     * the engine converts first is likewise unestablished. This repo ships multicurrency
     * tooling, so that shape is not hypothetical.
     *
     * DATE is fine — Date.valueOf carries no zone. Equality on these types is
     * unaffected; only ORDER comparisons are refused.
     */
    @TestVisible
    private static Boolean isOrderedType(Schema.DisplayType fieldType) {
        return fieldType == Schema.DisplayType.INTEGER
            || fieldType == Schema.DisplayType.LONG
            || fieldType == Schema.DisplayType.DOUBLE
            || fieldType == Schema.DisplayType.PERCENT
            || fieldType == Schema.DisplayType.DATE;
    }

    /**
     * Whether a picklist criterion's literal is an API value the field can actually
     * hold, rather than a display label.
     *
     * ⚠ SOQL filters picklists on the API name; the criterion stores whatever was
     * configured. When a LABEL is stored and the API name differs, the translation is
     * silently wrong in both directions — Equals matches nothing (which the empty-source
     * guard can only catch when the object is otherwise non-empty), and NotEquals
     * matches EVERYTHING, over-including rows the table excludes and producing a
     * confident false Stale that no later guard can see. Refusing at translation time
     * kills both, and turns an invisible wrong verdict into a reason someone can act on.
     *
     * Only refuses when the value is demonstrably not a valid API value: on an
     * unrestricted picklist the data may legitimately hold values outside the defined
     * list, so a non-matching value is refused only when it matches a LABEL — which is
     * positive evidence of the label-for-API-name mistake rather than a guess.
     */
    @TestVisible
    private static String picklistValueProblem(DescribeFieldResult fdr, String value) {
        Schema.DisplayType fieldType = fdr.getType();
        if (fieldType != Schema.DisplayType.PICKLIST && fieldType != Schema.DisplayType.COMBOBOX) {
            return null;
        }
        Set<String> apiValues = new Set<String>();
        Set<String> labels = new Set<String>();
        for (Schema.PicklistEntry entry : fdr.getPicklistValues()) {
            if (!entry.isActive()) {
                continue;
            }
            apiValues.add(entry.getValue());
            labels.add(entry.getLabel());
        }
        if (apiValues.isEmpty() || apiValues.contains(value)) {
            return null;
        }
        if (labels.contains(value)) {
            return 'value "' + value + '" is the LABEL of a picklist entry, not its API name, ' +
                'and SOQL filters on the API name';
        }
        if (fdr.isRestrictedPicklist()) {
            return 'value "' + value + '" is not an active value of this restricted picklist';
        }
        // Unrestricted picklist, value not in the defined list: legitimate data may sit
        // outside that list, so this is not evidence of a mistranslation.
        return null;
    }

    /**
     * The criterion's text Value as the type its field expects, or null when it
     * cannot be converted — which the caller turns into a refusal, not a default.
     */
    private static Object coerceValue(DescribeFieldResult fdr, String rawValue) {
        if (String.isBlank(rawValue)) {
            return null;
        }
        String value = rawValue.trim();
        Schema.DisplayType fieldType = fdr.getType();
        try {
            if (TEXT_FIELD_TYPES.contains(fieldType)) {
                return value;
            }
            if (NUMBER_FIELD_TYPES.contains(fieldType)) {
                return Decimal.valueOf(value);
            }
            if (fieldType == Schema.DisplayType.BOOLEAN) {
                // Strict on purpose: Boolean.valueOf turns anything unrecognised into
                // false, which would silently invert the filter.
                if (value.equalsIgnoreCase('true')) {
                    return true;
                }
                if (value.equalsIgnoreCase('false')) {
                    return false;
                }
                return null;
            }
            if (ID_FIELD_TYPES.contains(fieldType)) {
                // Throws on anything that is not a well-formed Id, which the catch turns
                // into a skip — a refusal decided here rather than a query that fails.
                return Id.valueOf(value);
            }
            if (UNESTABLISHED_COMPARISON_TYPES.contains(fieldType)) {
                // Refused at translateCriterion with a precise reason; belt-and-braces
                // here so no future caller can coerce one by accident.
                return null;
            }
            if (fieldType == Schema.DisplayType.DATE) {
                return Date.valueOf(value);
            }
            // ⚠ DATETIME is NOT coerced, deliberately, and this is the same reason
            // isOrderedType excludes it: Datetime.valueOf parses in the RUNNING USER'S
            // timezone, and the zone the decision-table engine parses in is
            // unestablished. Refusing only ORDERING comparisons was inconsistent — an
            // equality bound to the wrong instant selects a different row set just as
            // silently, and a filtered probe measuring the wrong rows can report Fresh.
            // Falls through to null, so the criterion is skipped and the comparison
            // widened, which is sound: a datetime field moves only when its record is
            // written. Establish the engine's zone and this can be translated.
        } catch (Exception e) {
            // An unparseable value refuses the whole table rather than filtering on
            // something the criterion did not ask for.
            return null;
        }
        return null;
    }

    /**
     * Newest WITNESS_FIELD per distinct probe, one aggregate query each — see that
     * constant for why it is SystemModstamp and not LastModifiedDate. Either way it is
     * a modification stamp rather than CreatedDate, because an EDITED source row
     * invalidates a decision table exactly as a new one does.
     *
     * A probe that cannot run carries its failure reason instead of a timestamp. The
     * caller reports those as UNKNOWN — deliberately not as fresh, which is what a
     * silently swallowed failure would produce.
     */
    /**
     * The aggregate query one probe will run.
     *
     * Split out so a test can assert WHICH FIELD is measured. Asserting the returned
     * timestamp cannot do that: fixture rows have identical SystemModstamp and
     * LastModifiedDate, so a probe that silently reverted to the narrower stamp would
     * return the same value and pass — which is exactly what the first version of that
     * test did.
     *
     * COUNT rides along in the SAME query as MAX, so the row count costs no extra SOQL.
     * It answers a question the timestamp cannot: a table that synced cleanly against a
     * source holding nothing is reported Fresh, and only the count reveals it produced
     * no rows.
     */
    @TestVisible
    private static String probeSoql(SourceProbe probe) {
        String soql = 'SELECT COUNT(Id) srcCount, MAX(' + WITNESS_FIELD + ') newest FROM ' +
            probe.objectName;
        if (String.isNotBlank(probe.whereClause)) {
            soql += ' WHERE ' + probe.whereClause;
        }
        return soql;
    }

    @TestVisible
    private static Map<String, ProbeResult> runProbes(Map<String, SourceProbe> probesByKey) {
        Map<String, ProbeResult> resultsByKey = new Map<String, ProbeResult>();
        Integer queriesIssued = 0;
        for (String key : probesByKey.keySet()) {
            SourceProbe probe = probesByKey.get(key);
            ProbeResult result = new ProbeResult();

            if (queriesIssued >= MAX_SOURCE_QUERIES) {
                // Stop rather than throw, and say so per table rather than truncating
                // silently. Every remaining probe reports UNKNOWN — never FRESH.
                result.failureReason = 'this org needs more source queries than one transaction allows (limit ' +
                    MAX_SOURCE_QUERIES + ')';
                resultsByKey.put(key, result);
                continue;
            }

            String soql = probeSoql(probe);
            // Counted before the attempt: a query that throws has still been issued.
            queriesIssued++;
            try {
                List<AggregateResult> rows = Database.queryWithBinds(
                    soql, probe.binds, AccessLevel.USER_MODE
                );
                result.ran = true;
                if (!rows.isEmpty()) {
                    result.newest = (Datetime) rows[0].get('newest');
                    result.rowCount = (Integer) rows[0].get('srcCount');
                }
            } catch (Exception e) {
                result.failureReason = 'the source query failed (' + e.getMessage() + ')';
            }
            resultsByKey.put(key, result);
        }
        return resultsByKey;
    }

    /**
     * Queues a refresh for the named decision tables.
     *
     * Requested names are validated against the tables that actually exist, and
     * unknown names are returned rather than dropped — a caller that asked for six
     * tables and got four refreshed must be able to see which two were not.
     */
    @AuraEnabled
    public static RefreshResult refreshTables(List<String> apiNames, Boolean incremental) {
        RefreshResult result = new RefreshResult();
        if (apiNames == null || apiNames.isEmpty()) {
            result.errorMessage = 'No decision tables were selected.';
            return result;
        }

        Set<String> requested = new Set<String>(apiNames);
        Set<String> known = new Set<String>();
        List<String> incrementalDisabled = new List<String>();
        for (DecisionTable dt : [
            SELECT DeveloperName, IsIncrementalSyncEnabled FROM DecisionTable
            WHERE DeveloperName IN :requested
            WITH USER_MODE
        ]) {
            known.add(dt.DeveloperName);
            if (dt.IsIncrementalSyncEnabled != true) {
                incrementalDisabled.add(dt.DeveloperName);
            }
        }
        // ⚠ An incremental request against a table with IsIncrementalSyncEnabled =
        // false is accepted by the platform action and then does not sync the changed
        // rows — so the caller sees "queued" and the table stays stale. Measured: false
        // on every table this repo ships and on all 40 in a built org, which makes this
        // the DEFAULT outcome of choosing Incremental rather than an edge case.
        //
        // Refused rather than silently downgraded to a full refresh: a full sync is a
        // heavier operation than the caller asked for, and doing it unasked would be a
        // different surprise. Naming the tables lets them re-run with Full.
        if (incremental == true && !incrementalDisabled.isEmpty()) {
            result.errorMessage = 'Incremental sync is not enabled on ' +
                incrementalDisabled.size() + ' of the selected table(s): ' +
                String.join(incrementalDisabled, ', ') +
                '. An incremental refresh there is accepted and then changes nothing. ' +
                'Run a full refresh, or enable incremental sync on the table first.';
            result.incremental = true;
            result.failedApiNames.addAll(incrementalDisabled);
            result.failedCount = incrementalDisabled.size();
            return result;
        }
        // Diff the EXPECTED set against what was found, rather than reporting on
        // the found set alone.
        for (String name : requested) {
            if (!known.contains(name)) {
                result.unknownApiNames.add(name);
            }
        }
        if (known.isEmpty()) {
            result.errorMessage = 'None of the requested decision tables exist.';
            return result;
        }

        try {
            Flow.Interview flow = Flow.Interview.createInterview(
                BULK_REFRESH_FLOW,
                new Map<String, Object>{
                    'decisionTableApiNames' => new List<String>(known),
                    'isIncremental' => incremental == true
                }
            );
            flow.start();
            result.queuedCount = toInteger(flow.getVariableValue('queuedCount'));
            result.failedCount = toInteger(flow.getVariableValue('failedCount'));
            Object failed = flow.getVariableValue('failedApiNames');
            if (failed instanceof List<String>) {
                result.failedApiNames = (List<String>) failed;
            }
            result.incremental = (incremental == true);
        } catch (Exception e) {
            result.errorMessage = 'Refresh could not be started: ' + e.getMessage();
        }
        return result;
    }

    /**
     * Current refresh state for the named tables, for the component's poll loop.
     * Not cacheable — a cached poll would report the state it started from.
     */
    @AuraEnabled(cacheable=false)
    public static List<DecisionTableInfo> getRefreshStatus(List<String> apiNames) {
        List<DecisionTableInfo> results = new List<DecisionTableInfo>();
        if (apiNames == null || apiNames.isEmpty()) {
            return results;
        }
        Set<String> requested = new Set<String>(apiNames);
        for (DecisionTable dt : [
            SELECT Id, DeveloperName, SetupName, Description, SourceObject, UsageType,
                   Status, Type, DataSourceType, ExecutionType, ConditionType,
                   FilterResultBy, UploadStatus, IsVersioned, DataSpaceName,
                   LastSyncDate, LastIncrementalSyncDate, RefreshStatus,
                   RefreshFailureReason, IsIncrementalSyncEnabled
            FROM DecisionTable
            WHERE DeveloperName IN :requested
            WITH USER_MODE
        ]) {
            results.add(new DecisionTableInfo(dt));
        }
        return results;
    }

    // NOTE: there is deliberately no setIncrementalEnabled here.
    // IsIncrementalSyncEnabled describes as updateable=true and IS writable over the
    // REST API, but DecisionTable is a setup object and Apex DML on it is rejected
    // outright at compile time: "DML operation Update not allowed on
    // List<DecisionTable>". Enabling incremental sync therefore has to happen through
    // Setup or the REST API, so the component reports the flag read-only rather than
    // offering a control that cannot work. Adding it would mean the session-id
    // Visualforce callout pattern RLM_ExpressionSetManagerController uses.

    /**
     * A flow output variable as a count. The bulk refresh flow hands back Decimals
     * (queuedCount arrives as 2.0), so this conversion is what makes the number the
     * component shows correct — and it is only reached on the live refresh path,
     * which tests do not take.
     */
    @TestVisible
    private static Integer toInteger(Object value) {
        if (value == null) {
            return 0;
        }
        if (value instanceof Decimal) {
            return ((Decimal) value).intValue();
        }
        if (value instanceof Integer) {
            return (Integer) value;
        }
        return 0;
    }

    /**
     * What one table reads BESIDES its primary object — and, just as importantly, what
     * could not be worked out. An unknown dependency has to survive as a fact, because
     * a verdict that silently forgets one is exactly the false all-clear this class
     * exists to prevent.
     */
    /** One field path, walked once: the objects it crosses and the field it lands on. */
    private class ResolvedPath {
        public List<String> objects;   // null until the walk succeeds
        public SObjectField terminal;  // null when the final segment does not resolve
    }

    @TestVisible
    private class Contributors {
        public Set<String> objects = new Set<String>();
        // FieldPaths whose hops could not be resolved: a real dependency with no name.
        public Set<String> unresolvedPaths = new Set<String>();
        // True when the parameter scan failed, so this table may read objects nothing
        // in this plan lists.
        public Boolean unenumerable = false;
    }

    /** How one table's source will be measured, or why it will not be. */
    @TestVisible
    private class SourcePlan {
        public SourceProbe probe;          // null when the source cannot be measured
        public SourceProbe unfilteredProbe; // set only when filtered; disambiguates a zero result
        public String verdict;             // set only when probe is null
        public String reason;              // set only when probe is null
        public Boolean filtered = false;   // true when criteria were reproduced in the probe
        // Other objects this table reads columns from. Probed alongside the primary so
        // the verdict covers every object that can change what the table holds.
        public List<SourceProbe> joinedProbes = new List<SourceProbe>();
        public List<String> contributingObjects = new List<String>();
        // Contributing objects that exist but cannot be queried by this user. Kept so
        // the verdict can decline to claim Fresh rather than silently ignoring them.
        public List<String> unreadableContributors = new List<String>();
        // True when the contributing objects could not be ENUMERATED at all (the
        // parameter scan failed), as opposed to being known and unreadable. Withholds
        // Fresh for the same reason: something that could have changed was never seen.
        public Boolean contributorsUnenumerable = false;
        // Criteria that were dropped from the probe rather than reproduced. Their
        // objects are watched instead, and the probe therefore covers a SUPERSET of the
        // table's rows — sound for proving Fresh, and over-reports Stale.
        public List<String> unreproducedCriteria = new List<String>();
    }

    /** One aggregate query against a source object, optionally filtered. */
    @TestVisible
    private class SourceProbe {
        public String objectName;
        public String whereClause = '';
        public Map<String, Object> binds = new Map<String, Object>();

        /**
         * Identity of the query this probe will run, so two tables sharing an object
         * AND a filter share one query. Serialized rather than concatenated so no
         * separator can collide and merge two genuinely different probes.
         */
        public String key() {
            return JSON.serialize(new List<String>{
                objectName, whereClause, JSON.serialize(binds)
            });
        }
    }

    /** What a probe found, or why it found nothing. */
    @TestVisible
    private class ProbeResult {
        public Boolean ran = false;
        public Datetime newest;
        public Integer rowCount;
        public String failureReason;
    }

    /** One criterion as SOQL, or the reason it was refused. */
    private class TranslatedCriterion {
        String clause;
        String reason;
        // Objects the criterion reaches across. Probed so a change that moves rows in
        // or out of this filter is still visible even though the filter itself was not
        // reproduced.
        List<String> watchObjects = new List<String>();
        // True when dropping the criterion would NOT be sound, because nothing this
        // check probes would witness the criterion's membership changing. Four causes,
        // and they are all "there is nothing to watch", never "this is hard":
        //   1. a traversal whose objects cannot be resolved
        //   2. a non-literal Value, which resolves at refresh time
        //   3. a formula field, whose inputs are invisible here
        //   4. a criterion with no field name at all
        // Everything else is SKIPPED and the comparison widened. Keep this list in step
        // with translateCriterion: a new refusal that is not listed here reads as a bug
        // to the next person, and a stale list invites "re-)classifying" a real one.
        Boolean mustRefuse = false;
    }

    public class DecisionTableInfo {
        @AuraEnabled public Id id;
        @AuraEnabled public String apiName;
        @AuraEnabled public String label;
        @AuraEnabled public String sourceObject;
        @AuraEnabled public String usageType;
        @AuraEnabled public String status;
        @AuraEnabled public Datetime lastSyncDate;
        @AuraEnabled public Datetime lastIncrementalSyncDate;
        @AuraEnabled public String refreshStatus;
        @AuraEnabled public String refreshFailureReason;
        @AuraEnabled public Boolean incrementalEnabled;
        @AuraEnabled public String description;
        @AuraEnabled public String tableType;
        @AuraEnabled public String dataSourceType;
        @AuraEnabled public String executionType;
        @AuraEnabled public String conditionType;
        @AuraEnabled public String filterResultBy;
        @AuraEnabled public String uploadStatus;
        @AuraEnabled public Boolean isVersioned;
        @AuraEnabled public String dataSpaceName;
        // "Decision Table" or "Decision Matrix", from CalculationMatrix. Details-pane
        // context only — see loadLookupTypes for why it must not become a column.
        @AuraEnabled public String lookupType;
        @AuraEnabled public String staleness;
        @AuraEnabled public String stalenessReason;
        @AuraEnabled public Datetime sourceNewestChange;
        // Rows in the SOURCE, not rows in the decision table — the table's own row
        // count is not reachable from Apex: DecisionTableDataset and
        // DecisionTableRecordset reject aggregates outright ("Aggregate functions not
        // supported") and reject any partial filter ("Filters may not have any gaps
        // within the composite key"). Read together with criteriaApplied, which says
        // whether this counts the filtered set or the whole object. Null when the
        // source was never read.
        @AuraEnabled public Integer sourceRowCount;
        @AuraEnabled public List<String> sourceCriteria = new List<String>();
        // Objects OTHER than the source that this table reads columns from or filters
        // across, and whose changes therefore count against its freshness. Empty for a
        // single-object table; populated for the MultipleSobjects ones.
        @AuraEnabled public List<String> contributingObjects = new List<String>();
        // Criteria the check watched rather than reproduced, so the comparison covers
        // more rows than the table holds. Non-empty means Stale may be over-reported —
        // Fresh is unaffected, since a superset that predates the sync proves the real
        // set does too.
        @AuraEnabled public List<String> unreproducedCriteria = new List<String>();
        // Whether the criteria above were reproduced in the freshness comparison.
        // The component says which, so a filtered verdict is never read as covering
        // the whole object and an unapplied filter is never read as applied.
        @AuraEnabled public Boolean criteriaApplied = false;

        public DecisionTableInfo(DecisionTable dt) {
            this.id = dt.Id;
            this.apiName = dt.DeveloperName;
            // MasterLabel is the constant string "Decision Tables" on every row, so it
            // cannot identify a table. SetupName carries the human name.
            this.label = String.isNotBlank(dt.SetupName) ? dt.SetupName : dt.DeveloperName;
            this.sourceObject = dt.SourceObject;
            this.usageType = dt.UsageType;
            this.status = dt.Status;
            this.lastSyncDate = dt.LastSyncDate;
            this.lastIncrementalSyncDate = dt.LastIncrementalSyncDate;
            this.refreshStatus = dt.RefreshStatus;
            this.refreshFailureReason = dt.RefreshFailureReason;
            this.incrementalEnabled = dt.IsIncrementalSyncEnabled;
            this.description = dt.Description;
            this.tableType = dt.Type;
            this.dataSourceType = dt.DataSourceType;
            this.executionType = dt.ExecutionType;
            this.conditionType = dt.ConditionType;
            this.filterResultBy = dt.FilterResultBy;
            this.uploadStatus = dt.UploadStatus;
            this.isVersioned = dt.IsVersioned;
            this.dataSpaceName = dt.DataSpaceName;
        }
    }

    public class RefreshResult {
        @AuraEnabled public Integer queuedCount = 0;
        @AuraEnabled public Integer failedCount = 0;
        @AuraEnabled public Boolean incremental = false;
        @AuraEnabled public List<String> failedApiNames = new List<String>();
        @AuraEnabled public List<String> unknownApiNames = new List<String>();
        @AuraEnabled public String errorMessage;
    }
}
