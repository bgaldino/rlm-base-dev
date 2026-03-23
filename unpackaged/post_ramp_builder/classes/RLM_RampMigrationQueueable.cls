/**
 * @description Async Queueable that completes ramp segment setup via platform APIs.
 *
 * WHY ASYNC: Salesforce prohibits HTTP callouts after uncommitted DML in the same
 * transaction. The synchronous service creates the parent group + segment 0 via DML,
 * moves existing QLIs into segment 0, then enqueues this job. This job runs after
 * that transaction commits, allowing callouts.
 *
 * FLOW (all calls in a single execute()):
 *   1. EditGroup        — converts segment 0 to a ramped group. The platform stamps
 *                         RampIdentifier, SegmentIdentifier on every QLI in segment 0.
 *   2. CloneSalesTransaction × (N-1) — each call clones the last segment, creating a new
 *                         segment with products copied and RampIdentifiers linked.
 *                         After each clone a SOQL query identifies the new group.
 *   3. EditRampSchedule — sets correct start/end dates and names on all segments in one
 *                         call (all segments must share the same SegmentType at this point).
 *   4. EditGroup per segment — for any segment whose SegmentType differs from segment 0
 *                         (e.g., Trial=Custom, Year 1..N=Yearly), call EditGroup individually.
 *   5. DML              — updates SegmentType, Discount, RLM_UpliftPercent__c on all groups
 *                         and QLIs to match each segment's definition. Groups are bucketed by
 *                         their target SegmentType and updated in separate DML calls to satisfy
 *                         the platform constraint that all segments in one DML batch share the
 *                         same SegmentType. Also deletes OneTime QLIs from cloned segments.
 *
 * API references:
 *   POST /services/data/v66.0/connect/rev/sales-transaction/actions/place  (EditGroup, EditRampSchedule)
 *   POST /services/data/v66.0/connect/rev/sales-transaction/actions/clone  (CloneSalesTransaction)
 */
public class RLM_RampMigrationQueueable implements Queueable, Database.AllowsCallouts {

    @TestVisible
    private static final String PLACE_TX_PATH =
        '/services/data/v66.0/connect/rev/sales-transaction/actions/place';

    @TestVisible
    private static final String CLONE_TX_PATH =
        '/services/data/v66.0/connect/rev/sales-transaction/actions/clone';

    private final String quoteId;
    private final String parentGroupId;
    private final String segment0GroupId;
    private final List<RLM_RampScheduleRequest.SegmentDefinition> sortedSegments;

    public RLM_RampMigrationQueueable(
        String quoteId,
        String parentGroupId,
        String segment0GroupId,
        List<RLM_RampScheduleRequest.SegmentDefinition> sortedSegments
    ) {
        this.quoteId          = quoteId;
        this.parentGroupId    = parentGroupId;
        this.segment0GroupId  = segment0GroupId;
        this.sortedSegments   = sortedSegments;
    }

    public void execute(QueueableContext ctx) {
        try {
            // Step 1: EditGroup on segment 0 — stamps RampIdentifier/SegmentIdentifier
            // on all QLIs in the group (subscription and one-time alike).
            callEditGroup(segment0GroupId, sortedSegments[0]);

            // For single-segment schedules, EditGroup is all that's needed.
            if (sortedSegments.size() == 1) {
                return;
            }

            // Step 2: clone remaining segments via CloneSalesTransaction × (N-1).
            List<String> allGroupIds = buildRemainingSegments();

            if (allGroupIds.isEmpty()) {
                return;
            }

            // Step 3: set correct dates and names on all segments in one API call.
            // All segments still share segment 0's SegmentType here (clone inheritance),
            // satisfying EditRampSchedule's requirement that all types are equal.
            callEditRampSchedule(allGroupIds);

            // Step 4: update SegmentType, Discount, Uplift, and remove OneTime QLIs
            // from cloned segments via DML. Using DML (not EditGroup) avoids a platform
            // side-effect where calling EditGroup on an already-ramped segment creates
            // duplicate copies of OneTime product QLIs.
            updateSegmentData(allGroupIds);

        } catch (Exception e) {
            System.debug(LoggingLevel.ERROR,
                'RLM_RampMigrationQueueable failed for quote ' + quoteId
                + ': ' + e.getMessage()
                + '\n' + e.getStackTraceString());
        }
    }

    // -------------------------------------------------------------------------
    // Clone loop — creates segments 1..N via CloneSalesTransaction, returns the
    // full ordered list of group IDs [seg0, seg1, ..., segN-1].
    // -------------------------------------------------------------------------
    private List<String> buildRemainingSegments() {
        List<String> allGroupIds   = new List<String>{ segment0GroupId };
        Set<String>  knownGroupIds = new Set<String>{ segment0GroupId, parentGroupId };

        for (Integer i = 1; i < sortedSegments.size(); i++) {
            String lastGroupId = allGroupIds[allGroupIds.size() - 1];

            // Clone the last segment — the platform creates a new child group with
            // all ramped QLIs copied, dates advanced to follow the source segment.
            callCloneSalesTransaction(lastGroupId);

            // The Clone API returns the quote ID, not the new group ID.
            // Identify the new group by querying for any group under the parent
            // that we haven't seen yet.
            List<QuoteLineGroup> newGroups = [
                SELECT Id FROM QuoteLineGroup
                WHERE ParentQuoteLineGroupId = :parentGroupId
                AND Id NOT IN :knownGroupIds
                LIMIT 1
            ];

            if (newGroups.isEmpty()) {
                System.debug(LoggingLevel.ERROR,
                    'RLM_RampMigrationQueueable: CloneSalesTransaction did not produce a new group '
                    + 'for segment index ' + i + ' (quote ' + quoteId + ')');
                return new List<String>();
            }

            String newGroupId = newGroups[0].Id;
            allGroupIds.add(newGroupId);
            knownGroupIds.add(newGroupId);
        }

        return allGroupIds;
    }

    // -------------------------------------------------------------------------
    // EditGroup — converts segment 0 to a ramped group and stamps identifiers.
    // Also used to update SegmentType on cloned segments.
    // -------------------------------------------------------------------------
    private void callEditGroup(String groupId, RLM_RampScheduleRequest.SegmentDefinition segDef) {
        Map<String, Object> groupFields = new Map<String, Object>{
            'IsRamped'    => true,
            'SegmentType' => mapGroupSegmentType(segDef.segmentType),
            'StartDate'   => formatDate(segDef.startDate),
            'EndDate'     => formatDate(segDef.endDate)
        };

        callPlaceSalesTransaction(new Map<String, Object>{
            'groupRampAction' => 'EditGroup',
            'pricingPref'     => 'System',
            'graph'           => new Map<String, Object>{
                'graphId' => 'editGroup_' + groupId,
                'records' => new List<Object>{
                    quotePatchRecord(quoteId),
                    groupPatchRecord(groupId, groupFields)
                }
            }
        });
    }

    // -------------------------------------------------------------------------
    // CloneSalesTransaction — clones the last ramp segment. The platform creates
    // a new child group with RampedLines copied and dates advanced automatically.
    // Response salesTransactionId is the quote ID, not the new group — use SOQL
    // after this call to locate the new group.
    // -------------------------------------------------------------------------
    private void callCloneSalesTransaction(String lastGroupId) {
        String endpoint = URL.getOrgDomainUrl().toExternalForm() + CLONE_TX_PATH;

        HttpRequest req = new HttpRequest();
        req.setEndpoint(endpoint);
        req.setMethod('POST');
        req.setHeader('Authorization', 'Bearer ' + UserInfo.getSessionId());
        req.setHeader('Content-Type', 'application/json');
        req.setBody(JSON.serialize(new Map<String, Object>{
            'recordIds'          => new List<String>{ lastGroupId },
            'salesTransactionId' => quoteId,
            'options'            => new Map<String, Object>{
                'lineScope' => 'RampedLinesOnly'
            }
        }));
        req.setTimeout(120000);

        HttpResponse res = new Http().send(req);

        if (res.getStatusCode() < 200 || res.getStatusCode() >= 300) {
            throw new CalloutException(
                'CloneSalesTransaction failed: HTTP '
                + res.getStatusCode() + ' ' + res.getStatus()
                + '\n' + res.getBody()
            );
        }

        Map<String, Object> parsed;
        try {
            parsed = (Map<String, Object>) JSON.deserializeUntyped(res.getBody());
        } catch (Exception ignored) {
            return;
        }

        if (!(Boolean) parsed.get('success')) {
            throw new CalloutException(
                'CloneSalesTransaction returned errors: '
                + JSON.serialize(parsed.get('errors'))
            );
        }
    }

    // -------------------------------------------------------------------------
    // EditRampSchedule — sets correct StartDate, EndDate, and Name on all segments
    // in one call. All segments must have the same SegmentType when this is called
    // (they do, because CloneSalesTransaction inherits the type from segment 0).
    // -------------------------------------------------------------------------
    private void callEditRampSchedule(List<String> allGroupIds) {
        List<Object> records = new List<Object>{ quotePatchRecord(quoteId) };

        for (Integer i = 0; i < allGroupIds.size(); i++) {
            RLM_RampScheduleRequest.SegmentDefinition segDef = sortedSegments[i];
            records.add(groupPatchRecord(allGroupIds[i], new Map<String, Object>{
                'Name'      => segDef.name,
                'StartDate' => formatDate(segDef.startDate),
                'EndDate'   => formatDate(segDef.endDate)
            }));
        }

        callPlaceSalesTransaction(new Map<String, Object>{
            'groupRampAction' => 'EditRampSchedule',
            'pricingPref'     => 'System',
            'graph'           => new Map<String, Object>{
                'graphId' => 'editRampSchedule_' + quoteId,
                'records' => records
            }
        });
    }

    // -------------------------------------------------------------------------
    // DML — updates SegmentType, Discount, and UnitPriceUplift on cloned groups
    // and their QLIs. Also removes OneTime product QLIs from cloned segments
    // (segments 1..N) — OneTime products belong only in segment 0.
    //
    // NOTE: SegmentType is updated via DML rather than callEditGroupForType (EditGroup API)
    // because calling EditGroup on an already-ramped segment creates duplicate copies of
    // OneTime product QLIs — a platform side-effect we cannot control.
    //
    // Two separate SegmentType mappings are required:
    //   QuoteLineGroup.SegmentType  — 'Custom' | 'Yearly'
    //   QuoteLineItem.SegmentType   — 'FreeTrial' | 'Custom' | 'Yearly'
    // -------------------------------------------------------------------------
    private void updateSegmentData(List<String> allGroupIds) {
        Map<String, RLM_RampScheduleRequest.SegmentDefinition> groupToSeg =
            new Map<String, RLM_RampScheduleRequest.SegmentDefinition>();
        for (Integer i = 0; i < allGroupIds.size(); i++) {
            groupToSeg.put(allGroupIds[i], sortedSegments[i]);
        }

        // --- Group-level update: Discount, Uplift, and SegmentType ---
        // SegmentType cannot be updated in a single batch that mixes different types
        // (e.g. 'Custom' Trial + 'Yearly' Year 1-N) because the platform validates that
        // all segments in a ramp share the same SegmentType during each DML call.
        // Fix: bucket groups by their target SegmentType and issue one update per bucket.
        // Each bucket is homogeneous so the constraint is satisfied.
        Map<String, List<QuoteLineGroup>> groupsByType = new Map<String, List<QuoteLineGroup>>();
        for (String gid : allGroupIds) {
            RLM_RampScheduleRequest.SegmentDefinition segDef = groupToSeg.get(gid);
            String mappedType = mapGroupSegmentType(segDef.segmentType);
            if (!groupsByType.containsKey(mappedType)) {
                groupsByType.put(mappedType, new List<QuoteLineGroup>());
            }
            groupsByType.get(mappedType).add(new QuoteLineGroup(
                Id                   = gid,
                SegmentType          = mappedType,
                Discount             = segDef.discountPercent != null ? segDef.discountPercent : 0,
                RLM_UpliftPercent__c = segDef.upliftPercent   != null ? segDef.upliftPercent   : 0
            ));
        }
        for (List<QuoteLineGroup> sameTypeGroups : groupsByType.values()) {
            Database.update(sameTypeGroups, false);
        }

        // --- QLI-level update: SegmentType, Discount, UnitPriceUplift ---
        // OneTime products in cloned segments (1..N) are platform artefacts — delete them.
        Set<String> clonedGroupIds = new Set<String>(allGroupIds);
        clonedGroupIds.remove(segment0GroupId);

        List<QuoteLineItem> allLines = [
            SELECT Id, QuoteLineGroupId, SellingModelType
            FROM QuoteLineItem
            WHERE QuoteLineGroupId IN :allGroupIds
        ];

        List<QuoteLineItem> linesToUpdate = new List<QuoteLineItem>();
        List<QuoteLineItem> linesToDelete = new List<QuoteLineItem>();

        for (QuoteLineItem qli : allLines) {
            RLM_RampScheduleRequest.SegmentDefinition segDef = groupToSeg.get(qli.QuoteLineGroupId);
            if (segDef == null) { continue; }

            if (clonedGroupIds.contains(qli.QuoteLineGroupId)
                    && qli.SellingModelType == 'OneTime') {
                linesToDelete.add(qli);
                continue;
            }

            qli.Discount        = segDef.discountPercent != null ? segDef.discountPercent : 0;
            qli.UnitPriceUplift = segDef.upliftPercent   != null ? segDef.upliftPercent   : 0;
            qli.SegmentType     = mapLineSegmentType(segDef.segmentType);
            linesToUpdate.add(qli);
        }

        if (!linesToDelete.isEmpty()) { delete linesToDelete; }
        if (!linesToUpdate.isEmpty()) { update linesToUpdate; }
    }

    // -------------------------------------------------------------------------
    // Place Sales Transaction HTTP helper
    // -------------------------------------------------------------------------
    @TestVisible
    private void callPlaceSalesTransaction(Map<String, Object> requestBody) {
        String endpoint = URL.getOrgDomainUrl().toExternalForm() + PLACE_TX_PATH;

        HttpRequest req = new HttpRequest();
        req.setEndpoint(endpoint);
        req.setMethod('POST');
        req.setHeader('Authorization', 'Bearer ' + UserInfo.getSessionId());
        req.setHeader('Content-Type', 'application/json');
        req.setBody(JSON.serialize(requestBody));
        req.setTimeout(120000);

        HttpResponse res = new Http().send(req);

        if (res.getStatusCode() < 200 || res.getStatusCode() >= 300) {
            throw new CalloutException(
                'Place Sales Transaction failed: HTTP '
                + res.getStatusCode() + ' ' + res.getStatus()
                + '\n' + res.getBody()
            );
        }

        Map<String, Object> parsed;
        try {
            parsed = (Map<String, Object>) JSON.deserializeUntyped(res.getBody());
        } catch (Exception ignored) {
            return;
        }

        Object errorsObj = parsed.get('errors');
        if (errorsObj instanceof List<Object> && !((List<Object>) errorsObj).isEmpty()) {
            throw new CalloutException(
                'Place Sales Transaction returned errors: '
                + JSON.serialize(errorsObj)
            );
        }
    }

    // -------------------------------------------------------------------------
    // Graph record builders
    // -------------------------------------------------------------------------
    private static Map<String, Object> quotePatchRecord(String qId) {
        return new Map<String, Object>{
            'referenceId' => qId,
            'record'      => new Map<String, Object>{
                'attributes' => new Map<String, Object>{
                    'type'   => 'Quote',
                    'method' => 'PATCH',
                    'id'     => qId
                }
            }
        };
    }

    private static Map<String, Object> groupPatchRecord(
        String groupId,
        Map<String, Object> fields
    ) {
        Map<String, Object> record = new Map<String, Object>{
            'attributes' => new Map<String, Object>{
                'type'   => 'QuoteLineGroup',
                'method' => 'PATCH',
                'id'     => groupId
            }
        };
        record.putAll(fields);
        return new Map<String, Object>{
            'referenceId' => groupId,
            'record'      => record
        };
    }

    // -------------------------------------------------------------------------
    // Helpers
    // -------------------------------------------------------------------------

    private static String formatDate(Date d) {
        return d == null ? null : String.valueOf(d);
    }

    /**
     * @description Map API segment type to QuoteLineGroup.SegmentType picklist value.
     * Only two values are valid in this org: 'Custom' and 'Yearly'.
     * Trial and Pro-Rata segments both map to 'Custom'.
     */
    private static String mapGroupSegmentType(String apiType) {
        Map<String, String> mapping = new Map<String, String>{
            RLM_RampScheduleRequest.SEGMENT_TYPE_TRIAL   => 'Custom',
            RLM_RampScheduleRequest.SEGMENT_TYPE_YEARLY  => 'Yearly',
            RLM_RampScheduleRequest.SEGMENT_TYPE_CUSTOM  => 'Custom',
            RLM_RampScheduleRequest.SEGMENT_TYPE_PRORATA => 'Custom'
        };
        return mapping.containsKey(apiType) ? mapping.get(apiType) : 'Custom';
    }

    /**
     * @description Map API segment type to QuoteLineItem.SegmentType picklist value.
     * QLI-level segment type uses different values from the group-level field:
     *   TRIAL     → 'FreeTrial'  (matches what EditGroup API stamps natively)
     *   YEARLY    → 'Yearly'
     *   CUSTOM    → 'Custom'
     *   PRO-RATED → 'Custom'
     */
    private static String mapLineSegmentType(String apiType) {
        Map<String, String> mapping = new Map<String, String>{
            RLM_RampScheduleRequest.SEGMENT_TYPE_TRIAL   => 'FreeTrial',
            RLM_RampScheduleRequest.SEGMENT_TYPE_YEARLY  => 'Yearly',
            RLM_RampScheduleRequest.SEGMENT_TYPE_CUSTOM  => 'Custom',
            RLM_RampScheduleRequest.SEGMENT_TYPE_PRORATA => 'Custom'
        };
        return mapping.containsKey(apiType) ? mapping.get(apiType) : 'Custom';
    }
}
