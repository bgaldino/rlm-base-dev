/**
 * RLM_DecisionTableManagerControllerTest
 *
 * Covers the part of the controller that can be got wrong quietly: deciding whether
 * a decision table's source criteria can be reproduced, and what the freshness query
 * becomes when they can.
 *
 * The tests assert the REFUSALS as hard as the successes. A refused table reports
 * "Not comparable", which is honest; a wrongly accepted one reports a computed
 * verdict that is wrong, which is the failure this class exists to prevent.
 *
 * ⚠ DecisionTable and DecisionTableSourceCriteria are setup objects whose fields are
 * not writeable in Apex — `new DecisionTableSourceCriteria(SourceFieldName = ...)`
 * fails to COMPILE with "Field is not writeable". JSON.deserialize builds them
 * instead. Nothing here is inserted; they are in-memory fixtures only.
 */
@isTest
private with sharing class RLM_DecisionTableManagerControllerTest {

    // A real, populated object with a plain text field to filter on, so the probe is
    // exercised against rows rather than against an empty table (where a filtered and
    // an unfiltered query both return null and prove nothing).
    private static final String TEST_CODE_MATCH = 'ZZ-DTM-MATCH';
    private static final String TEST_CODE_OTHER = 'ZZ-DTM-OTHER';

    @TestSetup
    static void makeData() {
        List<Product2> products = new List<Product2>();
        for (Integer i = 0; i < 3; i++) {
            products.add(new Product2(Name = 'DTM Match ' + i, ProductCode = TEST_CODE_MATCH, IsActive = true));
        }
        products.add(new Product2(Name = 'DTM Other', ProductCode = TEST_CODE_OTHER, IsActive = true));
        insert products;
    }

    private static DecisionTable table(String sourceObject, String conditionLogic) {
        return (DecisionTable) JSON.deserialize(
            JSON.serialize(new Map<String, Object>{
                'DeveloperName' => 'DTM_Test',
                'SetupName' => 'DTM Test',
                'SourceObject' => sourceObject,
                'DataSourceType' => 'SingleSobject',
                'SourceConditionLogic' => conditionLogic
            }),
            DecisionTable.class
        );
    }

    private static DecisionTableSourceCriteria criterion(
        String fieldName, String operator, String value, String valueType
    ) {
        return (DecisionTableSourceCriteria) JSON.deserialize(
            JSON.serialize(new Map<String, Object>{
                'SourceFieldName' => fieldName,
                'Operator' => operator,
                'Value' => value,
                'ValueType' => valueType
            }),
            DecisionTableSourceCriteria.class
        );
    }

    private static RLM_DecisionTableManagerController.SourcePlan plan(
        DecisionTable dt, List<DecisionTableSourceCriteria> criteria
    ) {
        // No joined objects: the overload under test here is the single-source path.
        return RLM_DecisionTableManagerController.planSource(
            dt, criteria, Schema.getGlobalDescribe(), null);
    }

    /** A table that also reads columns off a related object, as MultipleSobjects do. */
    private static RLM_DecisionTableManagerController.SourcePlan planWithJoins(
        DecisionTable dt, List<DecisionTableSourceCriteria> criteria, Set<String> joined
    ) {
        RLM_DecisionTableManagerController.Contributors contributors =
            new RLM_DecisionTableManagerController.Contributors();
        contributors.objects = joined == null ? new Set<String>() : joined;
        return RLM_DecisionTableManagerController.planSource(
            dt, criteria, Schema.getGlobalDescribe(), contributors);
    }

    /** A table whose contributing objects could not be worked out at all. */
    private static RLM_DecisionTableManagerController.SourcePlan planWithUnknownContributors(
        DecisionTable dt, Set<String> foundBeforeTheFailure
    ) {
        RLM_DecisionTableManagerController.Contributors contributors =
            new RLM_DecisionTableManagerController.Contributors();
        contributors.objects = foundBeforeTheFailure;
        contributors.unenumerable = true;
        return RLM_DecisionTableManagerController.planSource(
            dt, new List<DecisionTableSourceCriteria>(), Schema.getGlobalDescribe(), contributors);
    }

    // ---- criteria that CAN be reproduced ------------------------------------

    @isTest
    static void directFieldCriterionBecomesABoundWhereClause() {
        RLM_DecisionTableManagerController.SourcePlan result = plan(
            table('Product2', '1'),
            new List<DecisionTableSourceCriteria>{
                criterion('ProductCode', 'Equals', TEST_CODE_MATCH, 'Literal')
            }
        );

        Assert.isNotNull(result.probe, 'A direct-field criterion should be reproducible: ' + result.reason);
        Assert.isTrue(result.filtered, 'The plan must record that the filter was applied.');
        Assert.areEqual('ProductCode = :dtCriterion0', result.probe.whereClause,
            'The clause must use the platform field name and a generated bind.');
        Assert.areEqual(TEST_CODE_MATCH, result.probe.binds.get('dtCriterion0'),
            'The literal value must be bound, never concatenated into the query.');
    }

    @isTest
    static void aFilteredProbeMeasuresOnlyTheMatchingRows() {
        // The point of the whole feature: a filtered probe must return the newest
        // change among MATCHING rows. Proven by a filter that matches nothing
        // returning null while the same object unfiltered returns a timestamp — if
        // the WHERE clause were dropped, both would be identical.
        RLM_DecisionTableManagerController.SourcePlan matching = plan(
            table('Product2', '1'),
            new List<DecisionTableSourceCriteria>{
                criterion('ProductCode', 'Equals', TEST_CODE_MATCH, 'Literal')
            }
        );
        RLM_DecisionTableManagerController.SourcePlan noMatch = plan(
            table('Product2', '1'),
            new List<DecisionTableSourceCriteria>{
                criterion('ProductCode', 'Equals', 'ZZ-DTM-NOTHING-MATCHES-THIS', 'Literal')
            }
        );
        RLM_DecisionTableManagerController.SourcePlan unfiltered =
            plan(table('Product2', null), new List<DecisionTableSourceCriteria>());

        Map<String, RLM_DecisionTableManagerController.SourceProbe> probes =
            new Map<String, RLM_DecisionTableManagerController.SourceProbe>{
                matching.probe.key() => matching.probe,
                noMatch.probe.key() => noMatch.probe,
                unfiltered.probe.key() => unfiltered.probe
            };
        Assert.areEqual(3, probes.size(), 'Three different queries must not collapse to one key.');

        Test.startTest();
        Map<String, RLM_DecisionTableManagerController.ProbeResult> results =
            RLM_DecisionTableManagerController.runProbes(probes);
        Test.stopTest();

        RLM_DecisionTableManagerController.ProbeResult matched = results.get(matching.probe.key());
        RLM_DecisionTableManagerController.ProbeResult empty = results.get(noMatch.probe.key());
        RLM_DecisionTableManagerController.ProbeResult all = results.get(unfiltered.probe.key());

        Assert.isTrue(matched.ran, 'The filtered probe should have run: ' + matched.failureReason);
        Assert.isNotNull(matched.newest, 'Rows match the filter, so there is a newest change.');
        Assert.isTrue(empty.ran, 'The non-matching probe should still have run.');
        Assert.isNull(empty.newest, 'No rows match, so there is no newest change to report.');
        Assert.isNotNull(all.newest, 'The unfiltered probe should see the rows.');
    }

    @isTest
    static void noCriteriaProducesAnUnfilteredProbe() {
        RLM_DecisionTableManagerController.SourcePlan result =
            plan(table('Product2', null), new List<DecisionTableSourceCriteria>());

        Assert.isNotNull(result.probe, 'A table with no criteria is always comparable.');
        Assert.isFalse(result.filtered, 'Nothing was filtered, so the plan must not claim it was.');
        Assert.areEqual('', result.probe.whereClause, 'An unfiltered probe carries no WHERE clause.');
    }

    // ---- criteria that must be REFUSED --------------------------------------

    @isTest
    static void criterionOnARelatedRecordIsWatchedNotReproduced() {
        // Editing the parent moves rows into and out of the filter without touching any
        // source row, so reproducing the filter and comparing source timestamps would
        // read Fresh exactly when the table went stale. The filter is therefore NOT
        // reproduced — but the object it reaches across IS probed, so the change stays
        // visible. Dropping an AND-ed conjunct only widens the row set.
        RLM_DecisionTableManagerController.SourcePlan result = plan(
            table('PricebookEntry', '1'),
            new List<DecisionTableSourceCriteria>{
                criterion('Product2Id.ProductCode', 'Equals', TEST_CODE_MATCH, 'Literal')
            }
        );

        Assert.isNotNull(result.probe, 'The table is measurable now: ' + result.reason);
        // THE safety property, unchanged: a criterion that cannot be faithfully
        // translated never reaches SOQL.
        Assert.areEqual('', result.probe.whereClause,
            'The traversing criterion must not appear in the query.');
        Assert.isTrue(result.contributingObjects.contains('Product2'),
            'The traversed object must be watched instead: ' + result.contributingObjects);
        Assert.areEqual(1, result.unreproducedCriteria.size(),
            'And the table must record that its comparison is broader than its rows.');
    }

    @isTest
    static void aTraversalThatCannotBeResolvedIsStillRefused() {
        // Watching is only sound when the object can be NAMED. A polymorphic lookup
        // points at several objects, so there is nothing single to watch, and dropping
        // the criterion would leave the change genuinely invisible.
        RLM_DecisionTableManagerController.SourcePlan polymorphic = plan(
            table('Task', '1'),
            new List<DecisionTableSourceCriteria>{
                criterion('WhatId.Name', 'Equals', 'anything', 'Literal')
            }
        );
        Assert.isNull(polymorphic.probe, 'A polymorphic traversal has no single object to watch.');
        Assert.areEqual('Not comparable', polymorphic.verdict, 'So it must still be refused.');

        RLM_DecisionTableManagerController.SourcePlan unknownHop = plan(
            table('Product2', '1'),
            new List<DecisionTableSourceCriteria>{
                criterion('NoSuchLookup__x.Name', 'Equals', 'anything', 'Literal')
            }
        );
        Assert.isNull(unknownHop.probe, 'An unresolvable hop cannot be watched either.');

        // And the resolver itself: every hop is returned, not just the last.
        Assert.areEqual(
            new List<String>{ 'Product2' },
            RLM_DecisionTableManagerController.traversedObjects(
                'Product2Id.ProductCode', PricebookEntry.SObjectType.getDescribe().fields.getMap()),
            'A one-hop path names the object it reaches.');
        // ⚠ Two hops, asserted for real: the INTERMEDIATE object is the one a one-hop
        // test cannot distinguish from the final one, and it is exactly what gets
        // dropped when a path is resolved by naming only where the field lives.
        Assert.areEqual(
            new List<String>{ 'Account', 'User' },
            RLM_DecisionTableManagerController.traversedObjects(
                'AccountId.OwnerId.Name', Contact.SObjectType.getDescribe().fields.getMap()),
            'Both hops must come back, in order — the intermediate is a dependency too.');
        Assert.isNull(
            RLM_DecisionTableManagerController.traversedObjects(
                'WhatId.Name', Task.SObjectType.getDescribe().fields.getMap()),
            'A polymorphic hop resolves to nothing.');

        // ⚠ Degenerate paths must REFUSE, not throw. Apex drops trailing empties, so
        // "." splits to an EMPTY list — a resolver that reads the last segment without
        // checking would take the whole page down with an index-out-of-bounds instead of
        // declining one table. Regression-pinned because a refactor did exactly that.
        Map<String, Schema.SObjectField> productFields =
            Product2.SObjectType.getDescribe().fields.getMap();
        for (String degenerate : new List<String>{ '.', 'A.', '..', '.Name' }) {
            Assert.isNull(
                RLM_DecisionTableManagerController.traversedObjects(degenerate, productFields),
                'A path that names no resolvable hop must refuse, not throw: ' + degenerate);
        }
    }

    @isTest
    static void aTableReadingColumnsOffARelatedObjectProbesThatObjectToo() {
        // Measured on a stock build: all 12 MultipleSobjects tables pull columns across
        // a lookup (e.g. RateCardEntryId.RateUnitOfMeasureName) while still declaring a
        // single dataset link — so the source object alone looks sufficient and is not.
        // Editing the joined record changes what the table holds without touching a
        // primary row, so the joined object is probed alongside the primary and the
        // verdict compares against the newest change across both.
        RLM_DecisionTableManagerController.SourcePlan result = planWithJoins(
            table('Product2', null),
            new List<DecisionTableSourceCriteria>(),
            new Set<String>{ 'Contact' }
        );

        Assert.isNotNull(result.probe, 'The primary is still probed: ' + result.reason);
        Assert.areEqual(1, result.joinedProbes.size(), 'The contributing object must be probed too.');
        Assert.areEqual('Contact', result.joinedProbes[0].objectName, 'And probed by name.');
        Assert.areEqual('', result.joinedProbes[0].whereClause,
            'A contributing object is probed whole — the table may read any of its rows.');
        Assert.isTrue(result.contributingObjects.contains('Contact'),
            'The object must be reported so the pane can name what else this table depends on.');

        // A contributing object the caller cannot query is recorded, not ignored: the
        // verdict uses it to decline an all-clear it has no basis for. Asserted all the
        // way through to the verdict, because "no probe was created" is exactly what a
        // silent drop looks like too — the two are indistinguishable at the probe list.
        DecisionTable unresolvableDt = joinedTable(Datetime.newInstance(2026, 9, 1, 0, 0, 0));
        RLM_DecisionTableManagerController.SourcePlan unreadable = planWithJoins(
            unresolvableDt,
            new List<DecisionTableSourceCriteria>(),
            new Set<String>{ 'ZZ_No_Such_Object__c' }
        );
        Assert.areEqual(0, unreadable.joinedProbes.size(), 'An unresolvable object cannot be probed.');
        Assert.isTrue(unreadable.unreadableContributors.contains('ZZ_No_Such_Object__c'),
            'An object that cannot be resolved must be RECORDED, not dropped — otherwise ' +
            '"cannot check this" is quieter than "checked it": ' + unreadable.unreadableContributors);

        RLM_DecisionTableManagerController.DecisionTableInfo unreadableInfo =
            new RLM_DecisionTableManagerController.DecisionTableInfo(unresolvableDt);
        RLM_DecisionTableManagerController.applySourceVerdict(unreadableInfo, unresolvableDt, unreadable,
            new Map<String, RLM_DecisionTableManagerController.ProbeResult>{
                unreadable.probe.key() => probeResult(Datetime.newInstance(2026, 1, 1, 0, 0, 0), 5)
            });
        Assert.areEqual('Not comparable', unreadableInfo.staleness,
            'A sync later than every probe must NOT read Fresh while a named dependency ' +
            'went unchecked: ' + unreadableInfo.stalenessReason);

        // No contributing objects means the ordinary single-source path is unchanged.
        RLM_DecisionTableManagerController.SourcePlan plain = planWithJoins(
            table('Product2', null), new List<DecisionTableSourceCriteria>(), new Set<String>());
        Assert.isNotNull(plain.probe, 'A single-source table still plans normally.');
        Assert.areEqual(0, plain.joinedProbes.size(), 'And probes nothing extra.');
        Assert.isTrue(plain.contributingObjects.isEmpty(), 'And reports no extra dependency.');
    }

    /** A probe result with a chosen timestamp, so driver selection is deterministic. */
    private static RLM_DecisionTableManagerController.ProbeResult probeResult(Datetime newest, Integer rows) {
        RLM_DecisionTableManagerController.ProbeResult result =
            new RLM_DecisionTableManagerController.ProbeResult();
        result.ran = true;
        result.newest = newest;
        result.rowCount = rows;
        return result;
    }

    private static DecisionTable joinedTable(Datetime lastSync) {
        return (DecisionTable) JSON.deserialize(
            JSON.serialize(new Map<String, Object>{
                'DeveloperName' => 'DTM_Joined', 'SetupName' => 'DTM Joined',
                'SourceObject' => 'Product2', 'DataSourceType' => 'MultipleSobjects',
                'LastSyncDate' => lastSync
            }),
            DecisionTable.class
        );
    }

    @isTest
    static void aChangeInAContributingObjectMakesTheTableStale() {
        // The point of probing contributors: a joined-object edit moves no primary row,
        // so the primary timestamp cannot see it. Timestamps are supplied rather than
        // created, because rows inserted in one transaction share a LastModifiedDate
        // and could not establish which object drove the verdict.
        Datetime primaryChanged = Datetime.newInstance(2026, 1, 1, 0, 0, 0);
        Datetime joinedChanged = Datetime.newInstance(2026, 6, 1, 0, 0, 0);
        DecisionTable dt = joinedTable(Datetime.newInstance(2026, 3, 1, 0, 0, 0)); // between them

        RLM_DecisionTableManagerController.SourcePlan plan = planWithJoins(
            dt, new List<DecisionTableSourceCriteria>(), new Set<String>{ 'Contact' });

        RLM_DecisionTableManagerController.DecisionTableInfo info =
            new RLM_DecisionTableManagerController.DecisionTableInfo(dt);
        RLM_DecisionTableManagerController.applySourceVerdict(info, dt, plan,
            new Map<String, RLM_DecisionTableManagerController.ProbeResult>{
                plan.probe.key() => probeResult(primaryChanged, 5),
                plan.joinedProbes[0].key() => probeResult(joinedChanged, 3)
            });

        Assert.areEqual('Stale', info.staleness,
            'The primary alone would have read Fresh — the contributor is what makes it stale: ' +
            info.stalenessReason);
        Assert.isTrue(info.stalenessReason.startsWith('Contact'),
            'The reason must name the object that drove it, not the primary: ' + info.stalenessReason);
        Assert.areEqual(joinedChanged, info.sourceNewestChange,
            'The reported newest change must be the max across every contributing object.');
    }

    @isTest
    static void aSyncLaterThanEveryContributorIsFresh() {
        Datetime dt1 = Datetime.newInstance(2026, 1, 1, 0, 0, 0);
        Datetime dt2 = Datetime.newInstance(2026, 6, 1, 0, 0, 0);
        DecisionTable dt = joinedTable(Datetime.newInstance(2026, 9, 1, 0, 0, 0)); // after both

        RLM_DecisionTableManagerController.SourcePlan plan = planWithJoins(
            dt, new List<DecisionTableSourceCriteria>(), new Set<String>{ 'Contact' });

        RLM_DecisionTableManagerController.DecisionTableInfo info =
            new RLM_DecisionTableManagerController.DecisionTableInfo(dt);
        RLM_DecisionTableManagerController.applySourceVerdict(info, dt, plan,
            new Map<String, RLM_DecisionTableManagerController.ProbeResult>{
                plan.probe.key() => probeResult(dt1, 5),
                plan.joinedProbes[0].key() => probeResult(dt2, 3)
            });

        Assert.areEqual('Fresh', info.staleness, info.stalenessReason);
        Assert.isTrue(info.stalenessReason.contains('every object this table reads'),
            'Fresh here is the stronger claim and must say so: ' + info.stalenessReason);
        Assert.isTrue(info.contributingObjects.contains('Contact'),
            'The pane needs to know what else this table depends on.');
    }

    @isTest
    static void everyHopOfAColumnPathCountsAsADependency() {
        // ⚠ The live bug this pins: DomainObject names only the object owning the FINAL
        // field, so a two-hop column path leaves the INTERMEDIATE object unlisted.
        // Re-pointing that intermediate's lookup changes what a refresh materialises
        // while moving only the intermediate's LastModifiedDate — primary and final
        // both untouched, every probe reads Fresh. Measured on a stock build: 5 tables
        // depended on an intermediate (AssetRateCardEntry, BindingObjectRateCardEntry,
        // AssetAction) that DomainObject never mentioned.
        //
        // Contact.AccountId.OwnerId.Name stands in for that shape: Account is the
        // intermediate, User owns the field, and only User would be named.
        RLM_DecisionTableManagerController.Contributors twoHop =
            new RLM_DecisionTableManagerController.Contributors();
        RLM_DecisionTableManagerController.recordContributor(
            twoHop, 'Contact', 'User', 'AccountId.OwnerId.Name', Schema.getGlobalDescribe());
        Assert.isTrue(twoHop.objects.contains('User'), 'The named object is still a dependency.');
        Assert.isTrue(twoHop.objects.contains('Account'),
            'And so is the intermediate the path passes through: ' + twoHop.objects);
        Assert.isTrue(twoHop.unresolvedPaths.isEmpty(), 'A resolvable path is not a gap.');

        // The 'null' sentinel and a same-object column add nothing, and a path with no
        // hops has nothing to walk.
        RLM_DecisionTableManagerController.Contributors ownColumn =
            new RLM_DecisionTableManagerController.Contributors();
        RLM_DecisionTableManagerController.recordContributor(
            ownColumn, 'Contact', 'null', 'LastName', Schema.getGlobalDescribe());
        RLM_DecisionTableManagerController.recordContributor(
            ownColumn, 'Contact', 'Contact', 'FirstName', Schema.getGlobalDescribe());
        Assert.isTrue(ownColumn.objects.isEmpty(),
            'The literal string "null" and the table\'s own object are not dependencies: ' +
            ownColumn.objects);

        // An unwalkable path is recorded rather than dropped — the dependency is real
        // even though it cannot be named.
        RLM_DecisionTableManagerController.Contributors unresolvable =
            new RLM_DecisionTableManagerController.Contributors();
        RLM_DecisionTableManagerController.recordContributor(
            unresolvable, 'Contact', null, 'NoSuchLookup__x.Name', Schema.getGlobalDescribe());
        Assert.isTrue(unresolvable.objects.isEmpty(), 'Nothing resolved, so nothing is watched.');
        Assert.areEqual(new Set<String>{ 'NoSuchLookup__x.Name' }, unresolvable.unresolvedPaths,
            'But the gap is kept, so the verdict can decline an all-clear.');

        // A polymorphic hop is a gap for the same reason: several possible objects and
        // no basis for picking one.
        RLM_DecisionTableManagerController.Contributors polymorphic =
            new RLM_DecisionTableManagerController.Contributors();
        RLM_DecisionTableManagerController.recordContributor(
            polymorphic, 'Task', null, 'WhatId.Name', Schema.getGlobalDescribe());
        Assert.areEqual(new Set<String>{ 'WhatId.Name' }, polymorphic.unresolvedPaths,
            'A polymorphic lookup has no single object to watch.');
    }

    @isTest
    static void aFormulaFieldIsAGapBecauseItsInputsCannotBeSeen() {
        // ⚠ A formula is evaluated when it is READ, so a table materialising one stores
        // a value whose inputs are invisible here: a cross-object formula moves when the
        // OTHER record changes, TODAY() moves with nothing changing at all, and neither
        // touches the owning record's LastModifiedDate. Apex cannot see what a formula
        // reads — DescribeFieldResult exposes no body, and the REST describe returns
        // calculatedFormula = null for the standard formula fields this actually hits.
        // So it is recorded as a gap rather than guessed at. Measured on a stock build:
        // 4 parameters across 3 tables materialise a formula.
        // Asserted, not skipped: a test that quietly passes when it found nothing to
        // test is indistinguishable from one that verified something. (Contact was the
        // first choice and has NO isCalculated() field — Name is compound, not a
        // formula — which this assertion is what caught.)
        List<String> target = findCalculatedField();
        Assert.isNotNull(target,
            'No formula field found on any candidate object, so this test pins nothing.');
        String objectName = target[0];
        Schema.DescribeFieldResult formula = Schema.getGlobalDescribe().get(objectName)
            .getDescribe().fields.getMap().get(target[1]).getDescribe();
        RLM_DecisionTableManagerController.Contributors found =
            new RLM_DecisionTableManagerController.Contributors();
        RLM_DecisionTableManagerController.recordContributor(
            found, objectName, null, formula.getName(), Schema.getGlobalDescribe());
        Assert.areEqual(1, found.unresolvedPaths.size(),
            'A materialised formula must be recorded as an unwatchable dependency: ' +
            found.unresolvedPaths);
        // Asserts the actionable property — the gap NAMES the field, so a user can go
        // and compare it by hand — not the wording. Pinning the phrase "formula" here
        // was wrong the moment the same gap started catching platform-maintained fields
        // too, which is a message this check has no business asserting.
        Assert.isTrue(new List<String>(found.unresolvedPaths)[0].contains(formula.getName()),
            'The gap must name the field, since the fix is to compare it by hand: ' +
            found.unresolvedPaths);

        // A criterion on the same field is REFUSED, not skipped: skipping is sound only
        // while membership is a function of record state.
        RLM_DecisionTableManagerController.SourcePlan result = plan(
            table(objectName, '1'),
            new List<DecisionTableSourceCriteria>{
                criterion(formula.getName(), 'Equals', 'x', 'Literal')
            }
        );
        Assert.isNull(result.probe, 'A formula criterion cannot be widened around.');
        Assert.areEqual('Not comparable', result.verdict, result.reason);

        // Including under IsNull, which consumes no value but still reads the field.
        RLM_DecisionTableManagerController.SourcePlan isNull = plan(
            table(objectName, '1'),
            new List<DecisionTableSourceCriteria>{
                criterion(formula.getName(), 'IsNull', null, 'Literal')
            }
        );
        Assert.isNull(isNull.probe,
            'The operator consuming no value does not stop the FIELD moving underneath it.');

        // ⚠ The control must prove a stored field still TRANSLATES, which means
        // asserting the whereClause — not just that a probe exists. An earlier version
        // asked for 'LastName' on the discovered object; the discovered object is
        // AssetRateCardEntry, which has no LastName, and an unknown field is SKIPPED —
        // which still leaves a non-null probe. It would have passed with every stored
        // field wrongly refused. So the control field is discovered too.
        String storedField = findStoredFilterableField(objectName);
        Assert.isNotNull(storedField, objectName + ' must expose one ordinary stored field.');
        RLM_DecisionTableManagerController.SourcePlan stored = plan(
            table(objectName, '1'),
            new List<DecisionTableSourceCriteria>{
                criterion(storedField, 'Equals', 'x', 'Literal')
            }
        );
        Assert.isNotNull(stored.probe, 'A stored field still translates: ' + stored.reason);
        Assert.isTrue(stored.probe.whereClause.startsWith(storedField),
            'And actually reaches the query rather than being skipped: "' +
            stored.probe.whereClause + '"');
    }

    /** A plain stored field: not calculated, not platform-maintained, filterable, STRING. */
    private static String findStoredFilterableField(String objectName) {
        for (Schema.SObjectField f :
                Schema.getGlobalDescribe().get(objectName).getDescribe().fields.getMap().values()) {
            Schema.DescribeFieldResult fdr = f.getDescribe();
            if (!fdr.isCalculated() && fdr.isFilterable() && fdr.isAccessible()
                    && fdr.getType() == Schema.DisplayType.STRING
                    && !RLM_DecisionTableManagerController.PLATFORM_MAINTAINED_FIELDS
                        .contains(fdr.getName().toLowerCase())) {
                return fdr.getName();
            }
        }
        return null;
    }

    @isTest
    static void aPlatformMaintainedFieldIsAGapEvenThoughItIsNotAFormula() {
        // ⚠ isCalculated() is FALSE for these, so the formula check alone let them
        // through. Measured on Account/Opportunity/Contact/Product2. LastActivityDate is
        // the sharpest: DATE-typed and filterable, so it also clears the ordering gate
        // and a criterion on it would be FULLY TRANSLATED — the only case found where
        // translation itself is unsound, rather than a skip or a coercion. A row crosses
        // its boundary when a Task is logged, moving no LastModifiedDate anywhere.
        Map<String, Schema.SObjectField> accountFields =
            Account.SObjectType.getDescribe().fields.getMap();
        Assert.isFalse(accountFields.get('lastvieweddate').getDescribe().isCalculated(),
            'If this ever becomes true the deny-set is redundant — but it is false today, ' +
            'which is exactly why the deny-set exists.');

        // ⚠ LastActivityDate was in this set and is NOT any more. Measured live:
        // inserting a Task moved LastActivityDate AND SystemModstamp while
        // LastModifiedDate stayed put, so the witness sees it and denying it was pure
        // over-refusal. Pinned as a usable field so a well-meaning re-add fails here.
        RLM_DecisionTableManagerController.SourcePlan activity = plan(
            table('Account', '1'),
            new List<DecisionTableSourceCriteria>{
                criterion('LastActivityDate', 'Equals', '2026-01-01', 'Literal')
            }
        );
        Assert.areEqual('LastActivityDate = :dtCriterion0', activity.probe.whereClause,
            'SystemModstamp moves when LastActivityDate does, so it is measurable: ' +
            activity.reason);

        for (String fieldName : new List<String>{ 'LastViewedDate', 'LastReferencedDate' }) {
            RLM_DecisionTableManagerController.SourcePlan result = plan(
                table('Account', '1'),
                new List<DecisionTableSourceCriteria>{
                    criterion(fieldName, 'Equals', '2026-01-01', 'Literal')
                }
            );
            Assert.isNull(result.probe,
                fieldName + ' moves without a record edit, so it must not be measured against.');
            Assert.areEqual('Not comparable', result.verdict, result.reason);

            RLM_DecisionTableManagerController.Contributors found =
                new RLM_DecisionTableManagerController.Contributors();
            RLM_DecisionTableManagerController.recordContributor(
                found, 'Account', null, fieldName, Schema.getGlobalDescribe());
            Assert.areEqual(1, found.unresolvedPaths.size(),
                'And materialising it must be recorded as a gap: ' + fieldName);
        }

        // LastModifiedDate is deliberately NOT in the set: it moving IS a record edit,
        // which is the very thing every probe watches.
        //
        // ⚠ The value must be one Datetime.valueOf can actually parse ('yyyy-MM-dd
        // HH:mm:ss'). An earlier version passed ISO-8601 with a Z, which coerces to
        // null — so the criterion took the SKIP path, and asserting a non-null verdict
        // proved only "not refused" while claiming to prove "usable". The same vacuous
        // shape this very commit fixed twenty lines up.
        RLM_DecisionTableManagerController.SourcePlan lmd = plan(
            table('Account', '1'),
            new List<DecisionTableSourceCriteria>{
                criterion('LastModifiedDate', 'Equals', '2026-01-01 00:00:00', 'Literal')
            }
        );
        Assert.areEqual('LastModifiedDate = :dtCriterion0', lmd.probe.whereClause,
            'LastModifiedDate must stay usable, and actually TRANSLATE: ' + lmd.reason);
        Assert.isTrue(lmd.probe.binds.get('dtCriterion0') instanceof Datetime,
            'Bound as a Datetime, not as text.');
    }

    @isTest
    static void everyProbeWatchesSystemModstampNotLastModifiedDate() {
        // ⚠ LastModifiedDate records what a USER changed. SystemModstamp also advances
        // for internal processes that leave LastModifiedDate alone — Email Bounce
        // Management, picklist maintenance, roll-up recalculation, and an open-ended set
        // Salesforce does not enumerate. Watching the narrower stamp meant any of those
        // could change what a refresh materialises while every probe stayed older than
        // the sync: a confident false Fresh that no deny-list could have covered.
        //
        // Salesforce's own replication API (getUpdated) keys on SystemModstamp for the
        // same reason — "what changed since T" is exactly this question.
        // ⚠ Asserts the GENERATED QUERY, because nothing else can tell the two stamps
        // apart here: fixture rows have identical SystemModstamp and LastModifiedDate,
        // so a probe that silently reverted to the narrower stamp returns the same value
        // and passes every timestamp assertion. The first version of this test did
        // exactly that — it passed under the regression its own name claims to prevent.
        RLM_DecisionTableManagerController.SourcePlan plain =
            plan(table('Product2', null), new List<DecisionTableSourceCriteria>());
        Assert.areEqual(
            'SELECT COUNT(Id) srcCount, MAX(SystemModstamp) newest FROM Product2',
            RLM_DecisionTableManagerController.probeSoql(plain.probe),
            'The probe must measure SystemModstamp, not LastModifiedDate.');

        RLM_DecisionTableManagerController.SourcePlan filtered = plan(
            table('Product2', '1'),
            new List<DecisionTableSourceCriteria>{
                criterion('ProductCode', 'Equals', TEST_CODE_MATCH, 'Literal')
            }
        );
        Assert.isTrue(
            RLM_DecisionTableManagerController.probeSoql(filtered.probe)
                .startsWith('SELECT COUNT(Id) srcCount, MAX(SystemModstamp) newest FROM Product2 WHERE '),
            'And keep measuring it once a filter is attached.');

        Assert.areEqual('SystemModstamp', RLM_DecisionTableManagerController.WITNESS_FIELD,
            'The witness must be the broader stamp.');

        RLM_DecisionTableManagerController.SourcePlan result =
            plan(table('Product2', null), new List<DecisionTableSourceCriteria>());
        Map<String, RLM_DecisionTableManagerController.ProbeResult> results =
            RLM_DecisionTableManagerController.runProbes(
                new Map<String, RLM_DecisionTableManagerController.SourceProbe>{
                    result.probe.key() => result.probe
                });
        RLM_DecisionTableManagerController.ProbeResult probed = results.get(result.probe.key());
        Assert.isTrue(probed.ran, 'The probe must run against the witness: ' + probed.failureReason);

        // And it really is the newest SystemModstamp — asserted against the org rather
        // than against the string, so a query that silently changed field would fail.
        AggregateResult expected = [SELECT MAX(SystemModstamp) newest FROM Product2];
        Assert.areEqual((Datetime) expected.get('newest'), probed.newest,
            'The probe must report MAX(SystemModstamp).');

        // An object with no witness cannot be measured at all, rather than measured
        // against something else.
        Assert.isTrue(Product2.SObjectType.getDescribe().fields.getMap()
                .containsKey(RLM_DecisionTableManagerController.WITNESS_FIELD.toLowerCase()),
            'The existence guard keys on the same field the query selects.');
    }

    /**
     * The first readable formula field on a candidate object, as {object, field}.
     *
     * Discovered rather than hardcoded to one field, so the test pins the BEHAVIOUR and
     * not one org's schema. The candidates are the objects measured to carry formula
     * fields that decision tables actually materialise on a stock build —
     * AssetRateCardEntry.BindingObjectFormula and TaxRate.State/Country — with ordinary
     * standard objects behind them.
     */
    private static List<String> findCalculatedField() {
        Map<String, Schema.SObjectType> globalDescribe = Schema.getGlobalDescribe();
        for (String objectName : new List<String>{
                'AssetRateCardEntry', 'TaxRate', 'Opportunity', 'Case', 'Account', 'Product2' }) {
            Schema.SObjectType sot = globalDescribe.get(objectName);
            if (sot == null) {
                continue;
            }
            for (Schema.SObjectField f : sot.getDescribe().fields.getMap().values()) {
                Schema.DescribeFieldResult fdr = f.getDescribe();
                // ⚠ Skip formulas the platform documents as own-record: those are
                // deliberately NOT gaps, so selecting one would make this test assert
                // the opposite of the behaviour it names.
                if (fdr.isCalculated() && fdr.isAccessible()
                        && !RLM_DecisionTableManagerController.OWN_RECORD_FORMULAS.contains(
                               objectName.toLowerCase() + '.' + fdr.getName().toLowerCase())) {
                    return new List<String>{ objectName, fdr.getName().toLowerCase() };
                }
            }
        }
        return null;
    }

    @isTest
    static void aSelfReferentialColumnIsKeptWhenThePrimaryProbeIsFiltered() {
        // ⚠ A hop back to the table's OWN object is not redundant when the primary probe
        // is FILTERED: the probe then measures only the rows the table holds, while the
        // column materialises a field from a row that may sit OUTSIDE that filter. Same
        // object, different row set — and dropping it as "already probed" was a real
        // false-Fresh path.
        RLM_DecisionTableManagerController.Contributors found =
            new RLM_DecisionTableManagerController.Contributors();
        RLM_DecisionTableManagerController.recordContributor(
            found, 'Contact', null, 'ReportsToId.LastName', Schema.getGlobalDescribe());
        Assert.isTrue(found.objects.contains('Contact'),
            'The hop back to the primary object must survive: ' + found.objects);

        // Filtered: the self-reference earns its own UNFILTERED probe.
        RLM_DecisionTableManagerController.SourcePlan filtered = planWithJoins(
            table('Contact', '1'),
            new List<DecisionTableSourceCriteria>{
                criterion('LastName', 'Equals', 'DTM Match 0', 'Literal')
            },
            new Set<String>{ 'Contact' }
        );
        Assert.areEqual(1, filtered.joinedProbes.size(),
            'A filtered primary cannot see an out-of-filter row of its own object.');
        Assert.areEqual('', filtered.joinedProbes[0].whereClause,
            'And the probe that covers it must be unfiltered.');
        Assert.areNotEqual(filtered.probe.key(), filtered.joinedProbes[0].key(),
            'So it is a genuinely different query, not a duplicate.');

        // Unfiltered: it IS redundant, and is dropped rather than listed as extra.
        RLM_DecisionTableManagerController.SourcePlan unfiltered = planWithJoins(
            table('Contact', null), new List<DecisionTableSourceCriteria>(),
            new Set<String>{ 'Contact' });
        Assert.areEqual(0, unfiltered.joinedProbes.size(),
            'An unfiltered primary probe already covers every row of its own object.');
        Assert.isTrue(unfiltered.contributingObjects.isEmpty(),
            'And the pane must not claim the table "also reads" itself.');
    }

    @isTest
    static void contributorsThatCouldNotBeListedBlockAnAllClear() {
        // ⚠ The failure this pins is a fix that stops the damage without propagating
        // the signal. If the parameter scan throws — a user without read access to
        // DecisionTableParameter is enough — every table silently reverts to the
        // primary-only comparison this whole mechanism replaced, and reports a
        // confident Fresh with its contributors switched off. Not knowing what a table
        // reads has to read the same as not being able to check it.
        //
        // This asserts PROPAGATION of the flag, not the loader's scoping — the catch
        // path cannot be provoked from a test. The scoping is instead correct by
        // construction: the catch flags every table unconditionally, so there is no
        // scope left to get wrong. It once excluded SingleSobject on a measurement the
        // v67 reference disproves; a conditional there is what needed the test.
        DecisionTable dt = joinedTable(Datetime.newInstance(2026, 9, 1, 0, 0, 0));
        RLM_DecisionTableManagerController.SourcePlan plan =
            planWithUnknownContributors(dt, new Set<String>());

        Assert.isNotNull(plan.probe, 'The primary is still probed: ' + plan.reason);
        Assert.isTrue(plan.contributorsUnenumerable,
            'The plan must carry the fact that the dependency list could not be built.');

        RLM_DecisionTableManagerController.DecisionTableInfo info =
            new RLM_DecisionTableManagerController.DecisionTableInfo(dt);
        RLM_DecisionTableManagerController.applySourceVerdict(info, dt, plan,
            new Map<String, RLM_DecisionTableManagerController.ProbeResult>{
                plan.probe.key() => probeResult(Datetime.newInstance(2026, 1, 1, 0, 0, 0), 5)
            });

        Assert.areEqual('Not comparable', info.staleness,
            'A sync later than the primary must not read Fresh when the contributors are ' +
            'unknown: ' + info.stalenessReason);
        Assert.isTrue(info.stalenessReason.contains('could not be listed'),
            'And the reason must say the list could not be built, since the fix differs ' +
            'from an unreadable object: ' + info.stalenessReason);

        // Stale still stands — an unseen contributor could only add evidence.
        RLM_DecisionTableManagerController.DecisionTableInfo stale =
            new RLM_DecisionTableManagerController.DecisionTableInfo(dt);
        RLM_DecisionTableManagerController.applySourceVerdict(stale, dt, plan,
            new Map<String, RLM_DecisionTableManagerController.ProbeResult>{
                plan.probe.key() => probeResult(Datetime.newInstance(2026, 12, 1, 0, 0, 0), 5)
            });
        Assert.areEqual('Stale', stale.staleness,
            'An unknown contributor cannot rescue a table the primary already condemns: ' +
            stale.stalenessReason);
    }

    @isTest
    static void aContributorPathThatCannotBeResolvedBlocksAnAllClear() {
        // A multi-hop FieldPath whose hops do not resolve names a dependency that
        // exists and cannot be watched. Recorded rather than dropped, for the same
        // reason an unresolvable DomainObject is.
        DecisionTable dt = joinedTable(Datetime.newInstance(2026, 9, 1, 0, 0, 0));
        RLM_DecisionTableManagerController.Contributors contributors =
            new RLM_DecisionTableManagerController.Contributors();
        contributors.unresolvedPaths.add('NoSuchLookup__x.SomethingId.Name');

        RLM_DecisionTableManagerController.SourcePlan plan =
            RLM_DecisionTableManagerController.planSource(
                dt, new List<DecisionTableSourceCriteria>(), Schema.getGlobalDescribe(), contributors);

        Assert.isTrue(plan.unreadableContributors.contains('NoSuchLookup__x.SomethingId.Name'),
            'An unresolvable column path must survive into the plan: ' + plan.unreadableContributors);

        RLM_DecisionTableManagerController.DecisionTableInfo info =
            new RLM_DecisionTableManagerController.DecisionTableInfo(dt);
        RLM_DecisionTableManagerController.applySourceVerdict(info, dt, plan,
            new Map<String, RLM_DecisionTableManagerController.ProbeResult>{
                plan.probe.key() => probeResult(Datetime.newInstance(2026, 1, 1, 0, 0, 0), 5)
            });
        Assert.areEqual('Not comparable', info.staleness,
            'And must block the all-clear: ' + info.stalenessReason);
    }

    @isTest
    static void anUncheckableContributorBlocksAnAllClear() {
        // Fresh must not survive an unread contributor: something that could have
        // changed was never looked at, so there is no basis for an all-clear. Stale
        // would still stand, because an unseen change could only add to it.
        DecisionTable dt = (DecisionTable) JSON.deserialize(
            JSON.serialize(new Map<String, Object>{
                'DeveloperName' => 'DTM_Unread', 'SetupName' => 'DTM Unread',
                'SourceObject' => 'Product2', 'DataSourceType' => 'MultipleSobjects',
                'LastSyncDate' => Datetime.now().addYears(1)
            }),
            DecisionTable.class
        );
        RLM_DecisionTableManagerController.SourcePlan plan = planWithJoins(
            dt, new List<DecisionTableSourceCriteria>(), new Set<String>{ 'Contact' });

        // Only the primary result is supplied — the contributor's probe "did not run".
        Map<String, RLM_DecisionTableManagerController.SourceProbe> primaryOnly =
            new Map<String, RLM_DecisionTableManagerController.SourceProbe>{
                plan.probe.key() => plan.probe
            };
        Map<String, RLM_DecisionTableManagerController.ProbeResult> results =
            RLM_DecisionTableManagerController.runProbes(primaryOnly);

        RLM_DecisionTableManagerController.DecisionTableInfo info =
            new RLM_DecisionTableManagerController.DecisionTableInfo(dt);
        RLM_DecisionTableManagerController.applySourceVerdict(info, dt, plan, results);

        Assert.areNotEqual('Fresh', info.staleness,
            'An all-clear must not be issued while a contributing object went unchecked.');
        Assert.areEqual('Not comparable', info.staleness, info.stalenessReason);
        Assert.isTrue(info.stalenessReason.contains('Contact'),
            'The reason must name what could not be checked: ' + info.stalenessReason);
    }

    @isTest
    static void aPicklistLabelBoundInsteadOfItsApiNameIsRefused() {
        // The mechanism the empty-source guard structurally cannot catch: under Equals
        // it under-matches to zero, but under NotEquals it matches EVERYTHING and
        // produces a confident wrong verdict no later guard can see. Caught at
        // translation time instead, where the class does its refusing.
        Schema.DescribeFieldResult family = Product2.Family.getDescribe();
        String label;
        String apiValue;
        for (Schema.PicklistEntry entry : family.getPicklistValues()) {
            if (entry.isActive()) {
                apiValue = entry.getValue();
                label = entry.getLabel();
                break;
            }
        }
        Assert.isNotNull(apiValue, 'Product2.Family must expose an active picklist value to test with.');

        Assert.isNull(RLM_DecisionTableManagerController.picklistValueProblem(family, apiValue),
            'A real API value must pass: ' + apiValue);

        String bogus = 'ZZ Not A Family Value';
        String problem = RLM_DecisionTableManagerController.picklistValueProblem(family, bogus);
        if (family.isRestrictedPicklist()) {
            Assert.isNotNull(problem, 'A restricted picklist must reject a value it cannot hold.');
        } else {
            // Unrestricted: data may legitimately sit outside the defined list, so a
            // non-matching value is not by itself evidence of a mistranslation.
            Assert.isNull(problem, 'An unrestricted picklist must not refuse unlisted data.');
        }

        // Non-picklist fields are unaffected.
        Assert.isNull(
            RLM_DecisionTableManagerController.picklistValueProblem(
                Product2.ProductCode.getDescribe(), 'anything'),
            'The check must only apply to picklists.');
    }

    @isTest
    static void nonLiteralValueTypeIsRefused() {
        // ⚠ This is the one skip class where widening is NOT sound, so it is refused
        // rather than watched. Dropping an AND-ed conjunct proves nothing changed only
        // while the conjunct itself is fixed: a Parameter/Formula/Lookup value resolves
        // when the table is refreshed, so the boundary can move with no record edited
        // and no LastModifiedDate anywhere to witness it. A Formula meaning
        // "StartDate <= TODAY" starts admitting a row at midnight while every probe
        // still reads Fresh. Nothing to watch means nothing to skip toward.
        for (String valueType : new List<String>{ 'Parameter', 'Formula', 'Lookup', 'Picklist' }) {
            RLM_DecisionTableManagerController.SourcePlan result = plan(
                table('Product2', '1'),
                new List<DecisionTableSourceCriteria>{
                    criterion('ProductCode', 'Equals', TEST_CODE_MATCH, valueType)
                }
            );
            Assert.isNull(result.probe,
                valueType + ' resolves at refresh time, so the table must get no verdict.');
            Assert.areEqual('Not comparable', result.verdict,
                'And be reported as uncomparable rather than measured: ' + result.reason);
        }

        // A traversal is refused for the same reason, even though its objects COULD be
        // watched — watching them does not cover the boundary moving. The ValueType
        // gate therefore has to run before the traversal branch, not after it.
        RLM_DecisionTableManagerController.SourcePlan traversing = plan(
            table('PricebookEntry', '1'),
            new List<DecisionTableSourceCriteria>{
                criterion('Product2Id.ProductCode', 'Equals', 'x', 'Formula')
            }
        );
        Assert.isNull(traversing.probe,
            'Watching the traversed object does not make a moving boundary visible.');

        // IsNull compares against no value at all, so whatever ValueType is stamped on
        // it, its membership stays a function of record state — still skippable.
        RLM_DecisionTableManagerController.SourcePlan isNull = plan(
            table('Product2', '1'),
            new List<DecisionTableSourceCriteria>{
                criterion('ProductCode', 'IsNull', null, 'Formula')
            }
        );
        Assert.isNotNull(isNull.probe,
            'A null check has no boundary to move: ' + isNull.reason);
        Assert.areEqual('ProductCode = null', isNull.probe.whereClause,
            'And it is reproduced exactly, not skipped.');
    }

    @isTest
    static void aCriterionWithNoFieldNameIsRefusedRatherThanSkipped() {
        // Skipping needs something to watch instead, and an unnamed field resolves to
        // no object at all.
        RLM_DecisionTableManagerController.SourcePlan result = plan(
            table('Product2', '1'),
            new List<DecisionTableSourceCriteria>{
                criterion('   ', 'Equals', 'x', 'Literal')
            }
        );
        Assert.isNull(result.probe, 'An unnamed field cannot be watched, so it must not be dropped.');
        Assert.areEqual('Not comparable', result.verdict, result.reason);
    }

    @isTest
    static void operatorWithoutAnUnambiguousSoqlMeaningIsSkippedAndWidened() {
        for (String operator : new List<String>{ 'Contains', 'Matches', 'ExistsIn', 'DoesNotExistIn', 'DoesNotMatch' }) {
            RLM_DecisionTableManagerController.SourcePlan result = plan(
                table('Product2', '1'),
                new List<DecisionTableSourceCriteria>{
                    criterion('ProductCode', operator, TEST_CODE_MATCH, 'Literal')
                }
            );
            Assert.areEqual('', result.probe.whereClause,
                operator + ' has no established SOQL equivalent, so it must not reach the query.');
            Assert.areEqual(1, result.unreproducedCriteria.size(),
                'It must be recorded as unreproduced: ' + result.unreproducedCriteria);
            Assert.isTrue(result.unreproducedCriteria[0].contains(operator),
                'And name the operator: ' + result.unreproducedCriteria[0]);
        }
    }

    @isTest
    static void orderingOperatorsAreSkippedOnTypesWithNoAgreedOrdering() {
        // SOQL will compare text lexicographically, but the decision-table engine's
        // GreaterThan on a picklist plausibly means declaration order, and on an Id or
        // email it means nothing anyone intended. Two orderings that silently disagree
        // is the same hazard that keeps MULTIPICKLIST and Contains out.
        for (String operator : new List<String>{ 'GreaterThan', 'GreaterOrEqual', 'LessThan', 'LessOrEqual' }) {
            RLM_DecisionTableManagerController.SourcePlan textResult = plan(
                table('Product2', '1'),
                new List<DecisionTableSourceCriteria>{
                    criterion('ProductCode', operator, 'M', 'Literal')
                }
            );
            Assert.areEqual('', textResult.probe.whereClause,
                operator + ' on text has no agreed ordering, so it must not reach the query.');
            Assert.isTrue(textResult.unreproducedCriteria[0].contains('compares order'),
                'The skip must name the reason: ' + textResult.unreproducedCriteria[0]);
        }

        // Equality is unaffected by the gate — only ORDER comparisons are refused.
        RLM_DecisionTableManagerController.SourcePlan equality = plan(
            table('Product2', '1'),
            new List<DecisionTableSourceCriteria>{
                criterion('ProductCode', 'Equals', TEST_CODE_MATCH, 'Literal')
            }
        );
        Assert.isNotNull(equality.probe, 'Equality on text stays usable: ' + equality.reason);

        // And an ordering operator still builds a clause where the ordering IS agreed.
        // Asserted end-to-end, not just through isOrderedType, so the ACCEPT direction
        // is pinned by a real clause and not only the refuse direction.
        RLM_DecisionTableManagerController.SourcePlan ordered = plan(
            table('Contact', '1'),
            new List<DecisionTableSourceCriteria>{
                criterion('Birthdate', 'GreaterThan', '1990-01-01', 'Literal')
            }
        );
        Assert.isNotNull(ordered.probe, 'A date field has one ordering: ' + ordered.reason);
        Assert.areEqual('Birthdate > :dtCriterion0', ordered.probe.whereClause,
            'The ordering operator must reach SOQL as a bound comparison.');
        Assert.areEqual(Date.newInstance(1990, 1, 1), ordered.probe.binds.get('dtCriterion0'),
            'The boundary must be bound as a Date, not as text.');

        Assert.isTrue(RLM_DecisionTableManagerController.isOrderedType(Schema.DisplayType.DOUBLE),
            'Numbers have one ordering.');
        Assert.isTrue(RLM_DecisionTableManagerController.isOrderedType(Schema.DisplayType.DATE),
            'Dates have one ordering — Date.valueOf carries no timezone.');
        Assert.isFalse(RLM_DecisionTableManagerController.isOrderedType(Schema.DisplayType.PICKLIST),
            'A picklist has two candidate orderings, which is the problem.');
        Assert.isFalse(RLM_DecisionTableManagerController.isOrderedType(Schema.DisplayType.DATETIME),
            'A datetime ordering is obvious but its bound boundary is not — parse zone unestablished.');
        Assert.isFalse(RLM_DecisionTableManagerController.isOrderedType(Schema.DisplayType.CURRENCY),
            'Currency ordering is ambiguous in a multicurrency org.');
    }

    @isTest
    static void unknownFieldIsSkippedRatherThanQueried() {
        RLM_DecisionTableManagerController.SourcePlan result = plan(
            table('Product2', '1'),
            new List<DecisionTableSourceCriteria>{
                criterion('NoSuchField__x', 'Equals', 'x', 'Literal')
            }
        );
        Assert.areEqual('', result.probe.whereClause,
            'A field that does not exist must not be filtered on.');
        Assert.areEqual(1, result.unreproducedCriteria.size(),
            'It is skipped and the comparison widened, never guessed at.');
    }

    @isTest
    static void aPartlyReproducibleFilterIsAppliedInPartAndWidened() {
        // Applying only the reproducible half is SOUND here precisely because the
        // criteria are ANDed: the probe then covers a superset of the table's rows, so
        // a newest change predating the sync still proves the real set did not change.
        // The error can only be an over-report of Stale.
        RLM_DecisionTableManagerController.SourcePlan result = plan(
            table('PricebookEntry', '1 AND 2'),
            new List<DecisionTableSourceCriteria>{
                criterion('IsActive', 'Equals', 'true', 'Literal'),
                criterion('Product2Id.ProductCode', 'Equals', TEST_CODE_MATCH, 'Literal')
            }
        );
        Assert.isNotNull(result.probe, 'The reproducible half still buys precision: ' + result.reason);
        Assert.areEqual('IsActive = :dtCriterion0', result.probe.whereClause,
            'Only the reproducible criterion may appear, and the other must not be guessed.');
        Assert.isTrue(result.contributingObjects.contains('Product2'),
            'The unreproduced half is watched.');
        Assert.areEqual(1, result.unreproducedCriteria.size(), 'And recorded as unreproduced.');
    }

    @isTest
    static void unreadableSourceObjectIsUnknownNotFresh() {
        RLM_DecisionTableManagerController.SourcePlan result =
            plan(table('NoSuchObject__x', null), new List<DecisionTableSourceCriteria>());

        Assert.isNull(result.probe, 'A source object that does not exist cannot be probed.');
        Assert.areEqual('Unknown', result.verdict,
            'A source that cannot be read is Unknown — never Fresh, which is what swallowing the failure would produce.');
    }

    // ---- condition logic ------------------------------------------------------

    @isTest
    static void plainConjunctionsAreAcceptedAndEverythingElseIsRefused() {
        // Blank and the platform's own default ("1", "1 AND 2") mean plain AND.
        Assert.isTrue(RLM_DecisionTableManagerController.isPlainConjunction(null, 0), 'null logic is a plain AND.');
        Assert.isTrue(RLM_DecisionTableManagerController.isPlainConjunction('', 0), 'blank logic is a plain AND.');
        Assert.isTrue(RLM_DecisionTableManagerController.isPlainConjunction('1', 1), '"1" is a plain AND.');
        Assert.isTrue(RLM_DecisionTableManagerController.isPlainConjunction('1 AND 2', 2), '"1 AND 2" is a plain AND.');
        Assert.isTrue(RLM_DecisionTableManagerController.isPlainConjunction('2 AND 1', 2), 'AND commutes, so order is irrelevant.');
        Assert.isTrue(RLM_DecisionTableManagerController.isPlainConjunction(' 1 and 2 ', 2), 'Case and padding are irrelevant.');

        Assert.isFalse(RLM_DecisionTableManagerController.isPlainConjunction('1 OR 2', 2), 'OR is not a conjunction.');
        Assert.isFalse(RLM_DecisionTableManagerController.isPlainConjunction('1 AND (2 OR 3)', 3), 'Grouped logic is not reproduced.');
        Assert.isFalse(RLM_DecisionTableManagerController.isPlainConjunction('NOT 1', 1), 'Negation is not reproduced.');
        Assert.isFalse(RLM_DecisionTableManagerController.isPlainConjunction('1OR2', 2), 'A missing separator must not slip through.');
        Assert.isFalse(RLM_DecisionTableManagerController.isPlainConjunction('x AND 2', 2), 'A non-numeric token is not a criterion reference.');
        // Coverage matters as much as shape: accepting this would silently drop criterion 3.
        Assert.isFalse(RLM_DecisionTableManagerController.isPlainConjunction('1 AND 2', 3), 'Every criterion must be referenced.');
        Assert.isFalse(RLM_DecisionTableManagerController.isPlainConjunction('1 AND 1', 2), 'A repeated reference does not cover both criteria.');
    }

    @isTest
    static void customConditionLogicRefusesTheTable() {
        RLM_DecisionTableManagerController.SourcePlan result = plan(
            table('Product2', '1 OR 2'),
            new List<DecisionTableSourceCriteria>{
                criterion('ProductCode', 'Equals', TEST_CODE_MATCH, 'Literal'),
                criterion('IsActive', 'Equals', 'true', 'Literal')
            }
        );
        Assert.isNull(result.probe, 'OR logic is not reproduced, so the table cannot be measured.');
        Assert.areEqual('Not comparable', result.verdict, 'Unreproduced logic is not a verdict.');
        Assert.isTrue(result.reason.contains('1 OR 2'), 'The reason must quote the logic: ' + result.reason);
    }

    // ---- a filtered probe that finds nothing -----------------------------------

    /** Runs a table's plan and returns the verdict, the way getDecisionTables does. */
    private static RLM_DecisionTableManagerController.DecisionTableInfo verdictFor(
        DecisionTable dt, List<DecisionTableSourceCriteria> criteria
    ) {
        RLM_DecisionTableManagerController.SourcePlan plan = plan(dt, criteria);
        Map<String, RLM_DecisionTableManagerController.SourceProbe> probes =
            new Map<String, RLM_DecisionTableManagerController.SourceProbe>();
        if (plan.probe != null) {
            probes.put(plan.probe.key(), plan.probe);
        }
        if (plan.unfilteredProbe != null) {
            probes.put(plan.unfilteredProbe.key(), plan.unfilteredProbe);
        }
        Map<String, RLM_DecisionTableManagerController.ProbeResult> results =
            RLM_DecisionTableManagerController.runProbes(probes);

        RLM_DecisionTableManagerController.DecisionTableInfo info =
            new RLM_DecisionTableManagerController.DecisionTableInfo(dt);
        RLM_DecisionTableManagerController.applySourceVerdict(info, dt, plan, results);
        return info;
    }

    @isTest
    static void aFilterMatchingNothingOverAPOPULATEDObjectGetsNoVerdict() {
        // The dangerous case. "No rows matched" has two causes that look identical from
        // the result: the filter genuinely matches nothing, or the translation
        // over-restricted (a picklist label bound where SOQL wants the API name, a
        // datetime parsed in the wrong zone). Product2 HAS rows here, so the zero came
        // from the filter — and which of the two it was cannot be known.
        Test.startTest();
        RLM_DecisionTableManagerController.DecisionTableInfo info = verdictFor(
            table('Product2', '1'),
            new List<DecisionTableSourceCriteria>{
                criterion('ProductCode', 'Equals', 'ZZ-DTM-NOTHING-MATCHES-THIS', 'Literal')
            }
        );
        Test.stopTest();

        Assert.areNotEqual('Fresh', info.staleness,
            'A filter matching nothing over an object that HAS rows must not be called Fresh — ' +
            'that is exactly the false all-clear every refusal in this class exists to prevent.');
        Assert.areEqual('Not comparable', info.staleness,
            'It should be reported as not comparable: ' + info.stalenessReason);
        Assert.isTrue(info.stalenessReason.contains('does hold rows'),
            'The reason must say why the zero is untrustworthy: ' + info.stalenessReason);
    }

    @isTest
    static void aFilterOverAnEMPTYObjectIsStillFresh() {
        // The benign twin: no Contacts exist, so there is nothing for a filter to
        // over-restrict and the zero is trustworthy. Refusing here would throw away a
        // correct verdict — the disambiguation exists to keep this case usable.
        Test.startTest();
        RLM_DecisionTableManagerController.DecisionTableInfo info = verdictFor(
            table('Contact', '1'),
            new List<DecisionTableSourceCriteria>{
                criterion('LastName', 'Equals', 'ZZDtmNoSuchLastName', 'Literal')
            }
        );
        Test.stopTest();

        Assert.areEqual('Fresh', info.staleness,
            'An empty source object leaves no room for a mistranslated filter: ' + info.stalenessReason);
        // Asserted on the claim, not the sentence: what must survive rewording is that
        // the reason says the criteria excluded nothing, which is what separates this
        // from a filter that matched none of a populated object.
        Assert.isTrue(info.stalenessReason.contains('excluded nothing'),
            'The reason must distinguish this from a filter that excluded rows: ' + info.stalenessReason);
    }

    @isTest
    static void criteriaAppliedIsNotClaimedWhenNoProbeResultWasRead() {
        // An empty result map is what a probe skipped by the query cap looks like.
        // Claiming criteriaApplied there would caption an Unknown with "the verdict
        // above covers only these rows" — a verdict that does not exist.
        DecisionTable dt = table('Product2', '1');
        RLM_DecisionTableManagerController.SourcePlan plan = plan(
            dt,
            new List<DecisionTableSourceCriteria>{
                criterion('ProductCode', 'Equals', TEST_CODE_MATCH, 'Literal')
            }
        );
        RLM_DecisionTableManagerController.DecisionTableInfo info =
            new RLM_DecisionTableManagerController.DecisionTableInfo(dt);

        RLM_DecisionTableManagerController.applySourceVerdict(
            info, dt, plan, new Map<String, RLM_DecisionTableManagerController.ProbeResult>());

        Assert.areEqual('Unknown', info.staleness, 'No probe result means no verdict.');
        Assert.isFalse(info.criteriaApplied,
            'criteriaApplied must not be claimed when nothing was measured.');
    }

    // ---- the post-spin check --------------------------------------------------

    @isTest
    static void aSyncOlderThanTheOrgMeansTheTableWasBuiltSomewhereElse() {
        // The Trialforce case: a new org inherits the template's decision tables
        // INCLUDING their LastSyncDate, so every table arrives looking synced while
        // holding rows computed in a different org. The timestamp is real, it is just
        // not from here, so no source comparison can catch it.
        Datetime orgCreated = Datetime.newInstance(2026, 7, 23, 15, 9, 59);

        String inherited = RLM_DecisionTableManagerController.neverBuiltInThisOrgReason(
            orgCreated.addDays(-30), orgCreated);
        Assert.isNotNull(inherited, 'A sync predating the org must be reported.');
        Assert.isTrue(inherited.contains('predates this org'),
            'The reason must explain that the sync happened elsewhere: ' + inherited);

        Assert.isNull(
            RLM_DecisionTableManagerController.neverBuiltInThisOrgReason(orgCreated.addDays(1), orgCreated),
            'A sync after the org was created was performed in this org.');

        String never = RLM_DecisionTableManagerController.neverBuiltInThisOrgReason(null, orgCreated);
        Assert.isNotNull(never, 'A table that was never refreshed must be reported.');
        Assert.isTrue(never.contains('Never'), 'The reason must say it was never refreshed: ' + never);

        // If the org create date cannot be read the check is skipped rather than
        // measuring every table against an invented date.
        Assert.isNull(
            RLM_DecisionTableManagerController.neverBuiltInThisOrgReason(orgCreated.addDays(-30), null),
            'Without an org create date the spin check must not fire.');
        Assert.isNotNull(RLM_DecisionTableManagerController.neverBuiltInThisOrgReason(null, null),
            'A null sync is still "never refreshed" even with no org date to compare.');
    }

    @isTest
    static void aProbeReportsHowManyRowsFeedTheTable() {
        // Setup creates 3 matching + 1 other Product2.
        RLM_DecisionTableManagerController.SourcePlan matching = plan(
            table('Product2', '1'),
            new List<DecisionTableSourceCriteria>{
                criterion('ProductCode', 'Equals', TEST_CODE_MATCH, 'Literal')
            }
        );
        Map<String, RLM_DecisionTableManagerController.SourceProbe> probes =
            new Map<String, RLM_DecisionTableManagerController.SourceProbe>{
                matching.probe.key() => matching.probe
            };

        Test.startTest();
        Map<String, RLM_DecisionTableManagerController.ProbeResult> results =
            RLM_DecisionTableManagerController.runProbes(probes);
        Test.stopTest();

        RLM_DecisionTableManagerController.ProbeResult probed = results.get(matching.probe.key());
        Assert.areEqual(3, probed.rowCount,
            'The count must cover the filtered rows only — an unfiltered count would be 4.');
    }

    // ---- sources that are not sObjects at all ---------------------------------

    @isTest
    static void sourcesWithNoSobjectExplainThemselves() {
        // A stock build has no CsvUpload or ContextDefinition table, so this wording
        // and its UploadStatus fallback are never exercised by the public method.
        String uploaded = RLM_DecisionTableManagerController.nonSobjectSourceReason('CsvUpload', 'Completed');
        Assert.isTrue(uploaded.contains('Completed'), 'A known upload status must be reported: ' + uploaded);

        String noStatus = RLM_DecisionTableManagerController.nonSobjectSourceReason('CsvUpload', null);
        Assert.isTrue(noStatus.contains('none recorded'),
            'A missing upload status must say so rather than render blank: ' + noStatus);

        String context = RLM_DecisionTableManagerController.nonSobjectSourceReason('ContextDefinition', null);
        Assert.isTrue(context.contains('Context Definition'),
            'A Context Definition source must be named as such: ' + context);
        Assert.isFalse(context.contains('Upload status'),
            'A Context Definition has no upload status to report.');
    }

    @isTest
    static void lookupTypeIsReadableAndNeverInvented() {
        Assert.areEqual('Decision Table',
            RLM_DecisionTableManagerController.readableLookupType('DecisionTable'),
            'The stored value is not what a reader should see.');
        Assert.areEqual('Decision Matrix',
            RLM_DecisionTableManagerController.readableLookupType('DecisionMatrix'),
            'Matrices must be named as matrices.');
        // A value the platform adds later is shown as-is rather than dropped or
        // relabelled into one of the two known kinds.
        Assert.areEqual('SomethingNew',
            RLM_DecisionTableManagerController.readableLookupType('SomethingNew'),
            'An unrecognised type must pass through, not be forced into a known one.');
        Assert.areEqual(null, RLM_DecisionTableManagerController.readableLookupType(null),
            'Nothing known means nothing shown.');
    }

    // ---- the public surface ---------------------------------------------------

    @isTest
    static void everyReturnedTableCarriesAVerdictAndAReason() {
        Test.startTest();
        List<RLM_DecisionTableManagerController.DecisionTableInfo> infos =
            RLM_DecisionTableManagerController.getDecisionTables();
        Test.stopTest();

        // Assert there is something to check BEFORE checking it. DecisionTable is a
        // setup object read from the org rather than created here, so an empty list
        // would make every assertion below pass without examining anything.
        Assert.isTrue(!infos.isEmpty(),
            'No decision tables were returned, so this test verified nothing.');

        Set<String> allowed = new Set<String>{ 'Fresh', 'Stale', 'Not comparable', 'Unknown' };
        for (RLM_DecisionTableManagerController.DecisionTableInfo info : infos) {
            Assert.isTrue(allowed.contains(info.staleness),
                info.apiName + ' returned an unrecognised verdict: ' + info.staleness);
            Assert.isNotNull(info.stalenessReason, info.apiName + ' has a verdict with no reason.');
            Assert.isNotNull(info.label, info.apiName + ' must always have a display label.');
            // criteriaApplied means "a probe ran and the verdict below was computed
            // over the filtered rows". It does NOT imply a positive Fresh/Stale: a
            // filtered probe that legitimately cannot be interpreted reports
            // "Not comparable" and still had its criteria applied. What it must never
            // coexist with is Unknown, which means no probe result was available at all.
            if (info.criteriaApplied) {
                Assert.areNotEqual('Unknown', info.staleness,
                    info.apiName + ' claims its criteria were applied, but no probe result was read.');
            }
        }
    }

    @isTest
    static void refreshRejectsAnEmptySelectionWithoutStartingAnything() {
        RLM_DecisionTableManagerController.RefreshResult empty =
            RLM_DecisionTableManagerController.refreshTables(new List<String>(), false);
        Assert.areEqual(0, empty.queuedCount, 'Nothing was selected, so nothing may be queued.');
        Assert.isNotNull(empty.errorMessage, 'An empty selection must say why nothing happened.');

        RLM_DecisionTableManagerController.RefreshResult nullNames =
            RLM_DecisionTableManagerController.refreshTables(null, false);
        Assert.isNotNull(nullNames.errorMessage, 'A null selection must be reported, not ignored.');
    }

    @isTest
    static void unknownTableNamesAreReportedRatherThanDropped() {
        RLM_DecisionTableManagerController.RefreshResult result =
            RLM_DecisionTableManagerController.refreshTables(
                new List<String>{ 'ZZ_No_Such_Decision_Table' }, false);

        Assert.areEqual(1, result.unknownApiNames.size(),
            'A caller must be able to see which requested tables were not found.');
        Assert.areEqual('ZZ_No_Such_Decision_Table', result.unknownApiNames[0], 'The missing name must be named.');
        Assert.areEqual(0, result.queuedCount, 'Nothing real was requested, so nothing may be queued.');
    }

    @isTest
    static void flowCountsSurviveTheDecimalRoundTrip() {
        // The bulk flow returns its counts as Decimals (queuedCount comes back as
        // 2.0). Reporting that verbatim would show "2.0 queued", and a null — which
        // is what an absent output variable looks like — must read as 0, not blow up.
        Assert.areEqual(2, RLM_DecisionTableManagerController.toInteger(2.0),
            'A Decimal flow output must become a whole count.');
        Assert.areEqual(7, RLM_DecisionTableManagerController.toInteger(7),
            'An Integer output passes through unchanged.');
        Assert.areEqual(0, RLM_DecisionTableManagerController.toInteger(null),
            'A missing output counts as zero, not null.');
        Assert.areEqual(0, RLM_DecisionTableManagerController.toInteger('unexpected'),
            'An unexpected type counts as zero rather than throwing mid-refresh.');
    }

    @isTest
    static void refreshStatusOfNothingIsAnEmptyListNotAnError() {
        Assert.areEqual(0, RLM_DecisionTableManagerController.getRefreshStatus(null).size(),
            'Polling nothing returns nothing.');
        Assert.areEqual(0, RLM_DecisionTableManagerController.getRefreshStatus(new List<String>()).size(),
            'Polling an empty list returns nothing.');
    }
}
