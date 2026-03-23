/**
 * @description Service class for Ramp Schedule API
 * Handles validation and creation of ramp schedules
 */
public with sharing class RLM_RampScheduleService {
    
    private RLM_RampScheduleValidator validator;
    private Set<String> validSegmentTypes;
    
    public RLM_RampScheduleService() {
        this.validator = new RLM_RampScheduleValidator();
        this.validSegmentTypes = getValidSegmentTypes();
    }
    
    /**
     * @description Get available SegmentType picklist values from the org
     */
    private Set<String> getValidSegmentTypes() {
        Set<String> validTypes = new Set<String>();
        Schema.DescribeFieldResult fieldResult = QuoteLineGroup.SegmentType.getDescribe();
        for (Schema.PicklistEntry entry : fieldResult.getPicklistValues()) {
            if (entry.isActive()) {
                validTypes.add(entry.getValue());
            }
        }
        return validTypes;
    }
    
    /**
     * @description Execute the ramp schedule request (VALIDATE or CREATE)
     * @param request The ramp schedule request
     * @return Response with success/failure and data or errors
     */
    public RLM_RampScheduleResponse execute(RLM_RampScheduleRequest request) {
        List<RLM_RampScheduleResponse.ApiError> validationErrors = validator.validate(request);
        if (!validationErrors.isEmpty()) {
            return RLM_RampScheduleResponse.failure(validationErrors);
        }
        if (request.action == RLM_RampScheduleRequest.ACTION_VALIDATE) {
            return RLM_RampScheduleResponse.success(null, new List<String>(), 'Validation passed. Schedule is valid.');
        }
        // DML path (default): creates empty group structure; user adds products afterward.
        // API path (useDmlApproach=false): migrates existing QLIs via Queueable — advanced use.
        return (request.useDmlApproach == false)
            ? createRampSchedule(request)
            : createRampScheduleDml(request);
    }
    
    /**
     * @description Create the ramp schedule via the Connect REST API (async, default path).
     *
     * ARCHITECTURE NOTE — two-phase creation:
     *   Phase 1 (synchronous DML, this method):
     *     - Creates the parent RampScheduleGroup and segment 0 only.
     *     - Moves pre-existing QuoteLineItems into segment 0.
     *     - Enqueues RLM_RampMigrationQueueable.
     *
     *   Phase 2 (async Queueable, RLM_RampMigrationQueueable):
     *     - EditGroup on segment 0 → stamps RampIdentifier/SegmentIdentifier on QLIs.
     *     - CloneSalesTransaction × (N-1) → creates segments 1..N with products copied.
     *     - EditRampSchedule → fixes dates/names on all segments.
     *     - DML update → sets correct SegmentType, Discount, UnitPriceUplift on cloned
     *       groups and QLIs; deletes OneTime QLIs from cloned segments.
     *
     * Use request.useDmlApproach = true for the synchronous DML alternative.
     */
    private RLM_RampScheduleResponse createRampSchedule(RLM_RampScheduleRequest request) {
        Savepoint sp = Database.setSavepoint();
        
        try {
            // Sort segments by sequence
            List<RLM_RampScheduleRequest.SegmentDefinition> sortedSegments = sortSegmentsBySequence(request.segments);
            
            // Get schedule dates from first and last segment
            Date scheduleStartDate = sortedSegments[0].startDate;
            Date scheduleEndDate = sortedSegments[sortedSegments.size() - 1].endDate;
            
            // 1. Create parent Ramp Schedule Group
            QuoteLineGroup parentGroup = new QuoteLineGroup();
            parentGroup.QuoteId = request.quoteId;
            parentGroup.Name = request.scheduleHeader.scheduleName;
            parentGroup.Type = 'RampScheduleGroup';
            parentGroup.StartDate = scheduleStartDate;
            parentGroup.EndDate = scheduleEndDate;

            if (request.scheduleHeader != null && String.isNotBlank(request.scheduleHeader.rampMode)) {
                parentGroup.put('RLM_RampMode__c', request.scheduleHeader.rampMode);
            }
            
            insert parentGroup;
            
            // 2. Create ONLY segment 0 (the first child group).
            //    Segments 1..N are created by the Queueable via CloneSalesTransaction.
            RLM_RampScheduleRequest.SegmentDefinition seg0Def = sortedSegments[0];
            QuoteLineGroup seg0Group = new QuoteLineGroup();
            seg0Group.QuoteId = request.quoteId;
            seg0Group.Name = seg0Def.name;
            seg0Group.ParentQuoteLineGroupId = parentGroup.Id;
            seg0Group.IsRamped = true;
            // Child ramp segments must leave Quote Line Group Type blank
            seg0Group.Type = null;
            seg0Group.SegmentType = mapSegmentType(seg0Def.segmentType);

            if (seg0Group.SegmentType == null) {
                seg0Group.Description = 'Original Type: ' + seg0Def.segmentType;
            }

            seg0Group.StartDate = seg0Def.startDate;
            seg0Group.EndDate   = seg0Def.endDate;

            if (request.scheduleHeader != null && String.isNotBlank(request.scheduleHeader.rampMode)) {
                seg0Group.put('RLM_RampMode__c', request.scheduleHeader.rampMode);
            }
            if (seg0Def.discountPercent != null && seg0Def.discountPercent > 0) {
                seg0Group.Discount = seg0Def.discountPercent;
            }
            if (seg0Def.upliftPercent != null && seg0Def.upliftPercent > 0) {
                seg0Group.RLM_UpliftPercent__c = seg0Def.upliftPercent;
            }

            insert seg0Group;
            
            // 3. Move any pre-existing QuoteLineItems into segment 0 and enqueue the Queueable.
            Id jobId = migrateExistingLineItems(request.quoteId, sortedSegments, seg0Group, parentGroup.Id);
            
            return RLM_RampScheduleResponse.success(
                parentGroup.Id,
                new List<String>{ seg0Group.Id },
                'Ramp Schedule created. Remaining segments are being set up.',
                String.valueOf(jobId)
            );
            
        } catch (DmlException e) {
            Database.rollback(sp);
            return RLM_RampScheduleResponse.failure(
                RLM_RampScheduleResponse.ERROR_DML_EXCEPTION,
                'Failed to create Ramp Schedule.',
                e.getMessage()
            );
        } catch (Exception e) {
            Database.rollback(sp);
            return RLM_RampScheduleResponse.failure(
                RLM_RampScheduleResponse.ERROR_DML_EXCEPTION,
                'An unexpected error occurred.',
                e.getMessage() + ' at ' + e.getStackTraceString()
            );
        }
    }
    

    /**
     * @description Pure-DML ramp creation — synchronous, single transaction.
     *
     * Creates the group structure only (parent RampScheduleGroup + N segment groups with
     * IsRamped=true). Does NOT distribute or stamp line items — that requires the platform
     * API (EditGroup + CloneSalesTransaction) which is handled by the async queueable path.
     *
     * This mirrors the original reference implementation from pm-tm-groupramp exactly.
     * Line item distribution was a planned "P1" extension that requires the API layer.
     */
    private RLM_RampScheduleResponse createRampScheduleDml(RLM_RampScheduleRequest request) {
        Savepoint sp = Database.setSavepoint();
        try {
            List<RLM_RampScheduleRequest.SegmentDefinition> segs = sortSegmentsBySequence(request.segments);
            Date scheduleStart = segs[0].startDate;
            Date scheduleEnd   = segs[segs.size() - 1].endDate;

            // 1. Parent group
            QuoteLineGroup parent = new QuoteLineGroup();
            parent.QuoteId    = request.quoteId;
            parent.Name       = request.scheduleHeader.scheduleName;
            parent.Type       = 'RampScheduleGroup';
            parent.StartDate  = scheduleStart;
            parent.EndDate    = scheduleEnd;
            if (request.scheduleHeader != null && String.isNotBlank(request.scheduleHeader.rampMode)) {
                parent.put('RLM_RampMode__c', request.scheduleHeader.rampMode);
            }
            insert parent;

            // 2. All N segment groups (IsRamped=true)
            List<QuoteLineGroup> segGroups = new List<QuoteLineGroup>();
            for (RLM_RampScheduleRequest.SegmentDefinition segDef : segs) {
                QuoteLineGroup g = new QuoteLineGroup();
                g.QuoteId                = request.quoteId;
                g.Name                   = segDef.name;
                g.ParentQuoteLineGroupId = parent.Id;
                g.IsRamped               = true;
                g.Type                   = null;
                g.SegmentType            = mapSegmentType(segDef.segmentType);
                g.StartDate              = segDef.startDate;
                g.EndDate                = segDef.endDate;
                g.Discount               = segDef.discountPercent != null ? segDef.discountPercent : 0;
                g.RLM_UpliftPercent__c   = segDef.upliftPercent   != null ? segDef.upliftPercent   : 0;
                if (request.scheduleHeader != null && String.isNotBlank(request.scheduleHeader.rampMode)) {
                    g.put('RLM_RampMode__c', request.scheduleHeader.rampMode);
                }
                if (g.SegmentType == null) {
                    g.Description = 'Original Type: ' + segDef.segmentType;
                }
                segGroups.add(g);
            }
            insert segGroups;

            List<String> segmentGroupIds = new List<String>();
            for (QuoteLineGroup g : segGroups) { segmentGroupIds.add(g.Id); }

            return RLM_RampScheduleResponse.success(
                parent.Id,
                segmentGroupIds,
                'Ramp Schedule groups created successfully. Use the API path to distribute products.'
            );

        } catch (DmlException e) {
            Database.rollback(sp);
            return RLM_RampScheduleResponse.failure(
                RLM_RampScheduleResponse.ERROR_DML_EXCEPTION,
                'Failed to create Ramp Schedule (DML).',
                e.getMessage()
            );
        } catch (Exception e) {
            Database.rollback(sp);
            return RLM_RampScheduleResponse.failure(
                RLM_RampScheduleResponse.ERROR_DML_EXCEPTION,
                'An unexpected error occurred (DML).',
                e.getMessage() + ' at ' + e.getStackTraceString()
            );
        }
    }

    /** @description Generate a platform-format RampIdentifier (RDI + 16 random hex chars). */
    private static String rampIdentifier() {
        return 'RDI' + EncodingUtil.convertToHex(Crypto.generateAesKey(128)).left(16);
    }

    /** @description Generate a platform-format SegmentIdentifier (SEG + 16 random hex chars). */
    private static String segmentIdentifier() {
        return 'SEG' + EncodingUtil.convertToHex(Crypto.generateAesKey(128)).left(16);
    }


    /**
     * @description Map API segment type to QuoteLineGroup.SegmentType picklist value.
     * Only two values are valid: 'Custom' and 'Yearly'.
     * 'Yearly' requires a duration of exactly 1 year; all non-year-duration segments
     * (Trial, Pro-Rata, Custom) must use 'Custom'. The actual duration is always
     * governed by StartDate/EndDate.
     */
    private String mapSegmentType(String apiSegmentType) {
        Map<String, String> typeMapping = new Map<String, String>{
            RLM_RampScheduleRequest.SEGMENT_TYPE_TRIAL   => 'Custom',
            RLM_RampScheduleRequest.SEGMENT_TYPE_YEARLY  => 'Yearly',
            RLM_RampScheduleRequest.SEGMENT_TYPE_CUSTOM  => 'Custom',
            RLM_RampScheduleRequest.SEGMENT_TYPE_PRORATA => 'Custom'
        };
        String mapped = typeMapping.containsKey(apiSegmentType)
            ? typeMapping.get(apiSegmentType)
            : 'Custom';
        return validSegmentTypes.contains(mapped) ? mapped : null;
    }
    
    /**
     * @description Sort segments by sequence number
     */
    private List<RLM_RampScheduleRequest.SegmentDefinition> sortSegmentsBySequence(List<RLM_RampScheduleRequest.SegmentDefinition> segments) {
        Map<Integer, RLM_RampScheduleRequest.SegmentDefinition> segmentMap = new Map<Integer, RLM_RampScheduleRequest.SegmentDefinition>();
        List<Integer> sequences = new List<Integer>();
        
        for (RLM_RampScheduleRequest.SegmentDefinition segment : segments) {
            segmentMap.put(segment.sequence, segment);
            sequences.add(segment.sequence);
        }
        
        sequences.sort();
        
        List<RLM_RampScheduleRequest.SegmentDefinition> sorted = new List<RLM_RampScheduleRequest.SegmentDefinition>();
        for (Integer seq : sequences) {
            sorted.add(segmentMap.get(seq));
        }
        
        return sorted;
    }

    /**
     * @description Move existing QuoteLineItems into segment 0 (DML only), then enqueue
     * the Queueable to call the Place Sales Transaction and Clone Sales Transaction APIs.
     *
     * Ramp identifier fields (RampIdentifier, SegmentIdentifier, IsPrimarySegment,
     * ParentQuoteLineItemId) are NOT set here — they are stamped by the platform
     * when the Queueable calls EditGroup on segment 0.
     *
     * Segments 1..N are created by the Queueable via CloneSalesTransaction.
     *
     * Strategy:
     *   - Subscription products: moved to segment 0 with aligned dates, discount, uplift.
     *   - One-time products: moved to segment 0, dates left untouched (platform constraint).
     */
    private Id migrateExistingLineItems(
        String quoteId,
        List<RLM_RampScheduleRequest.SegmentDefinition> sortedSegments,
        QuoteLineGroup seg0Group,
        Id parentGroupId
    ) {
        Set<Id> reservedIds = new Set<Id>{ parentGroupId, seg0Group.Id };

        List<QuoteLineItem> existingLines = [
            SELECT Id, SellingModelType, PeriodBoundary
            FROM QuoteLineItem
            WHERE QuoteId = :quoteId
            AND (QuoteLineGroupId = null OR QuoteLineGroupId NOT IN :reservedIds)
        ];

        if (!existingLines.isEmpty()) {
            RLM_RampScheduleRequest.SegmentDefinition seg0 = sortedSegments[0];
            List<QuoteLineItem> toUpdate = new List<QuoteLineItem>();

            for (QuoteLineItem qli : existingLines) {
                qli.QuoteLineGroupId = seg0Group.Id;
                qli.SegmentType      = seg0Group.SegmentType;
                qli.Discount         = seg0.discountPercent != null ? seg0.discountPercent : 0;
                qli.UnitPriceUplift  = seg0.upliftPercent   != null ? seg0.upliftPercent   : 0;
                if (String.isBlank(qli.PeriodBoundary)) {
                    qli.PeriodBoundary = 'Anniversary';
                }
                if (qli.SellingModelType != 'OneTime') {
                    qli.StartDate = seg0.startDate;
                    qli.EndDate   = seg0.endDate;
                }
                toUpdate.add(qli);
            }

            update toUpdate;
        }

        // Always enqueue — EditGroup on segment 0 must run to stamp ramp identifiers,
        // and CloneSalesTransaction creates the remaining segments.
        Id jobId = System.enqueueJob(new RLM_RampMigrationQueueable(
            quoteId,
            parentGroupId,
            seg0Group.Id,
            sortedSegments
        ));
        return jobId;
    }
}
