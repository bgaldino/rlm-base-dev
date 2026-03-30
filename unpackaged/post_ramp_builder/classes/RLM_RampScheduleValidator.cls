/**
 * @description Validator for Ramp Schedule API requests
 * Implements all validation rules defined in the API specification
 */
public class RLM_RampScheduleValidator {
    
    /**
     * @description Validate the entire request
     * @param request The ramp schedule request to validate
     * @return List of validation errors (empty if valid)
     */
    public List<RLM_RampScheduleResponse.ApiError> validate(RLM_RampScheduleRequest request) {
        List<RLM_RampScheduleResponse.ApiError> errors = new List<RLM_RampScheduleResponse.ApiError>();

        if (request == null) {
            errors.add(new RLM_RampScheduleResponse.ApiError(
                RLM_RampScheduleResponse.ERROR_INVALID_ACTION,
                'Request cannot be null.',
                'A non-null RLM_RampScheduleRequest is required.'
            ));
            return errors;
        }

        // Validate action
        errors.addAll(validateAction(request.action));

        // Validate quote ID
        errors.addAll(validateQuoteId(request.quoteId));

        // Validate schedule header and required header fields
        if (request.scheduleHeader == null) {
            errors.add(new RLM_RampScheduleResponse.ApiError(
                RLM_RampScheduleResponse.ERROR_INVALID_ACTION,
                'Schedule header is required.',
                'scheduleHeader must be provided for ramp schedule requests.'
            ));
        } else {
            if (String.isBlank(request.scheduleHeader.scheduleName)) {
                errors.add(new RLM_RampScheduleResponse.ApiError(
                    RLM_RampScheduleResponse.ERROR_INVALID_ACTION,
                    'Schedule name is required.',
                    'scheduleHeader.scheduleName must be a non-blank value.'
                ));
            }
            if (String.isBlank(request.scheduleHeader.scheduleType)) {
                errors.add(new RLM_RampScheduleResponse.ApiError(
                    RLM_RampScheduleResponse.ERROR_INVALID_ACTION,
                    'Schedule type is required.',
                    'scheduleHeader.scheduleType must be specified.'
                ));
            }
        }

        // Fail fast if header/action/quote are invalid — segment validation would
        // throw NPEs when dereferencing scheduleHeader fields downstream.
        if (!errors.isEmpty()) {
            return errors;
        }

        // Validate segments exist
        if (request.segments == null || request.segments.isEmpty()) {
            errors.add(new RLM_RampScheduleResponse.ApiError(
                RLM_RampScheduleResponse.ERROR_EMPTY_SCHEDULE,
                'At least one segment is required.',
                'The segments array must contain at least 1 segment.'
            ));
            return errors; // Can't proceed with other validations
        }
        
        // Validate sequence values before sorting — null/duplicate sequences produce
        // silently incorrect sort results and must be rejected explicitly.
        errors.addAll(validateSequences(request.segments));
        if (!errors.isEmpty()) {
            return errors;
        }

        // Sort segments by sequence for validation
        List<RLM_RampScheduleRequest.SegmentDefinition> sortedSegments = sortSegmentsBySequence(request.segments);
        
        // Field-level validation
        errors.addAll(validateFieldLevel(sortedSegments));
        
        // Structural validation (only if field-level passes)
        if (errors.isEmpty()) {
            Boolean isStaggeredRamp = isStaggeredRampMode(request);
            errors.addAll(validateContinuity(sortedSegments, isStaggeredRamp));
            errors.addAll(validateTrialSegment(sortedSegments));
            errors.addAll(validateProRataSegment(sortedSegments));
            errors.addAll(validateSegmentTypeConsistency(sortedSegments));
            errors.addAll(validateYearlyDuration(sortedSegments, isStaggeredRamp));
        }
        
        return errors;
    }
    
    /**
     * @description Validate action parameter
     */
    private List<RLM_RampScheduleResponse.ApiError> validateAction(String action) {
        List<RLM_RampScheduleResponse.ApiError> errors = new List<RLM_RampScheduleResponse.ApiError>();
        
        if (String.isBlank(action)) {
            errors.add(new RLM_RampScheduleResponse.ApiError(
                RLM_RampScheduleResponse.ERROR_INVALID_ACTION,
                'Action is required.',
                'Valid values are: VALIDATE, CREATE'
            ));
        } else if (action != RLM_RampScheduleRequest.ACTION_VALIDATE && action != RLM_RampScheduleRequest.ACTION_CREATE) {
            errors.add(new RLM_RampScheduleResponse.ApiError(
                RLM_RampScheduleResponse.ERROR_INVALID_ACTION,
                'Invalid action: ' + action,
                'Valid values are: VALIDATE, CREATE'
            ));
        }
        
        return errors;
    }
    
    /**
     * @description Validate quote ID exists
     */
    private List<RLM_RampScheduleResponse.ApiError> validateQuoteId(String quoteId) {
        List<RLM_RampScheduleResponse.ApiError> errors = new List<RLM_RampScheduleResponse.ApiError>();
        
        if (String.isBlank(quoteId)) {
            errors.add(new RLM_RampScheduleResponse.ApiError(
                RLM_RampScheduleResponse.ERROR_INVALID_QUOTE_ID,
                'Quote ID is required.'
            ));
            return errors;
        }
        
        // Validate ID format
        try {
            Id qId = Id.valueOf(quoteId);
            if (qId.getSObjectType() != Quote.SObjectType) {
                errors.add(new RLM_RampScheduleResponse.ApiError(
                    RLM_RampScheduleResponse.ERROR_INVALID_QUOTE_ID,
                    'Invalid Quote ID format.',
                    'The provided ID is not a Quote ID.'
                ));
                return errors;
            }
        } catch (Exception e) {
            errors.add(new RLM_RampScheduleResponse.ApiError(
                RLM_RampScheduleResponse.ERROR_INVALID_QUOTE_ID,
                'Invalid Quote ID format.',
                e.getMessage()
            ));
            return errors;
        }
        
        // Check if quote exists
        List<Quote> quotes = [SELECT Id FROM Quote WHERE Id = :quoteId LIMIT 1];
        if (quotes.isEmpty()) {
            errors.add(new RLM_RampScheduleResponse.ApiError(
                RLM_RampScheduleResponse.ERROR_INVALID_QUOTE_ID,
                'Quote not found.',
                'No Quote exists with ID: ' + quoteId
            ));
        }
        
        return errors;
    }
    
    /**
     * @description Field-level validation for all segments
     */
    private List<RLM_RampScheduleResponse.ApiError> validateFieldLevel(List<RLM_RampScheduleRequest.SegmentDefinition> segments) {
        List<RLM_RampScheduleResponse.ApiError> errors = new List<RLM_RampScheduleResponse.ApiError>();
        
        for (RLM_RampScheduleRequest.SegmentDefinition segment : segments) {
            String segmentRef = 'Segment ' + segment.sequence + ' (' + segment.name + ')';
            
            // Validate dates
            if (segment.startDate == null) {
                errors.add(new RLM_RampScheduleResponse.ApiError(
                    RLM_RampScheduleResponse.ERROR_INVALID_DATE,
                    'Start date is required.',
                    segmentRef + ': startDate cannot be null.'
                ));
            }
            
            if (segment.endDate == null) {
                errors.add(new RLM_RampScheduleResponse.ApiError(
                    RLM_RampScheduleResponse.ERROR_INVALID_DATE,
                    'End date is required.',
                    segmentRef + ': endDate cannot be null.'
                ));
            }
            
            // Validate date range
            if (segment.startDate != null && segment.endDate != null && segment.endDate < segment.startDate) {
                errors.add(new RLM_RampScheduleResponse.ApiError(
                    RLM_RampScheduleResponse.ERROR_INVALID_DATE_RANGE,
                    'End date must be after start date.',
                    segmentRef + ': endDate (' + segment.endDate + ') is before startDate (' + segment.startDate + ').'
                ));
            }
            
            // Validate discount percent
            if (segment.discountPercent != null && (segment.discountPercent < 0 || segment.discountPercent > 100)) {
                errors.add(new RLM_RampScheduleResponse.ApiError(
                    RLM_RampScheduleResponse.ERROR_INVALID_DISCOUNT,
                    'Discount percent must be between 0 and 100.',
                    segmentRef + ': discountPercent is ' + segment.discountPercent
                ));
            }
            
            // Validate uplift percent
            if (segment.upliftPercent != null && (segment.upliftPercent < 0 || segment.upliftPercent > 100)) {
                errors.add(new RLM_RampScheduleResponse.ApiError(
                    RLM_RampScheduleResponse.ERROR_INVALID_UPLIFT,
                    'Uplift percent must be between 0 and 100.',
                    segmentRef + ': upliftPercent is ' + segment.upliftPercent
                ));
            }
        }
        
        return errors;
    }
    
    /**
     * @description Whether the request is for Staggered Ramp mode (co-term segments; continuity rules do not apply).
     */
    private Boolean isStaggeredRampMode(RLM_RampScheduleRequest request) {
        return request != null
            && request.scheduleHeader != null
            && request.scheduleHeader.rampMode == 'Staggered Ramp';
    }
    
    /**
     * @description Validate segment continuity (no gaps or overlaps). Skipped for Staggered Ramp (segments share co-term end date).
     */
    private List<RLM_RampScheduleResponse.ApiError> validateContinuity(List<RLM_RampScheduleRequest.SegmentDefinition> segments, Boolean isStaggeredRamp) {
        List<RLM_RampScheduleResponse.ApiError> errors = new List<RLM_RampScheduleResponse.ApiError>();
        if (isStaggeredRamp) {
            return errors;
        }
        
        for (Integer i = 0; i < segments.size() - 1; i++) {
            RLM_RampScheduleRequest.SegmentDefinition current = segments[i];
            RLM_RampScheduleRequest.SegmentDefinition next = segments[i + 1];
            
            if (current.endDate == null || next.startDate == null) {
                continue; // Skip if dates are null (caught by field validation)
            }
            
            // Expected next start date is current end date + 1 day
            Date expectedNextStart = current.endDate.addDays(1);
            
            if (next.startDate < expectedNextStart) {
                // Overlap detected
                errors.add(new RLM_RampScheduleResponse.ApiError(
                    RLM_RampScheduleResponse.ERROR_SEGMENT_DISCONTINUITY,
                    'Segment overlap detected.',
                    'Overlap found between Segment ' + current.sequence + ' (Ends ' + current.endDate + 
                    ') and Segment ' + next.sequence + ' (Starts ' + next.startDate + ').'
                ));
            } else if (next.startDate > expectedNextStart) {
                // Gap detected
                errors.add(new RLM_RampScheduleResponse.ApiError(
                    RLM_RampScheduleResponse.ERROR_SEGMENT_DISCONTINUITY,
                    'Segment gap detected.',
                    'Gap found between Segment ' + current.sequence + ' (Ends ' + current.endDate + 
                    ') and Segment ' + next.sequence + ' (Starts ' + next.startDate + ').'
                ));
            }
        }
        
        return errors;
    }
    
    /**
     * @description Validate trial segment rules
     * - Max 1 trial segment
     * - Must be first segment (sequence 1)
     */
    private List<RLM_RampScheduleResponse.ApiError> validateTrialSegment(List<RLM_RampScheduleRequest.SegmentDefinition> segments) {
        List<RLM_RampScheduleResponse.ApiError> errors = new List<RLM_RampScheduleResponse.ApiError>();
        
        List<RLM_RampScheduleRequest.SegmentDefinition> trialSegments = new List<RLM_RampScheduleRequest.SegmentDefinition>();
        
        for (RLM_RampScheduleRequest.SegmentDefinition segment : segments) {
            if (segment.segmentType == RLM_RampScheduleRequest.SEGMENT_TYPE_TRIAL) {
                trialSegments.add(segment);
            }
        }
        
        // Check max 1 trial
        if (trialSegments.size() > 1) {
            errors.add(new RLM_RampScheduleResponse.ApiError(
                RLM_RampScheduleResponse.ERROR_INVALID_TRIAL_CONFIG,
                'Only one trial segment is allowed.',
                'Found ' + trialSegments.size() + ' trial segments.'
            ));
        }
        
        // Check trial is first segment
        if (trialSegments.size() == 1) {
            RLM_RampScheduleRequest.SegmentDefinition trial = trialSegments[0];
            if (trial.sequence != 1) {
                errors.add(new RLM_RampScheduleResponse.ApiError(
                    RLM_RampScheduleResponse.ERROR_INVALID_TRIAL_CONFIG,
                    'Trial segment must be the first segment.',
                    'Trial segment has sequence ' + trial.sequence + ', expected 1.'
                ));
            }
        }
        
        return errors;
    }
    
    /**
     * @description Validate pro-rata segment rules
     * - Max 1 pro-rata segment
     * - Must be first non-trial segment OR last segment
     */
    private List<RLM_RampScheduleResponse.ApiError> validateProRataSegment(List<RLM_RampScheduleRequest.SegmentDefinition> segments) {
        List<RLM_RampScheduleResponse.ApiError> errors = new List<RLM_RampScheduleResponse.ApiError>();
        
        List<RLM_RampScheduleRequest.SegmentDefinition> proRataSegments = new List<RLM_RampScheduleRequest.SegmentDefinition>();
        Integer firstNonTrialSequence = null;
        Integer lastSequence = 0;
        
        for (RLM_RampScheduleRequest.SegmentDefinition segment : segments) {
            if (segment.segmentType == RLM_RampScheduleRequest.SEGMENT_TYPE_PRORATA) {
                proRataSegments.add(segment);
            }
            if (segment.segmentType != RLM_RampScheduleRequest.SEGMENT_TYPE_TRIAL && firstNonTrialSequence == null) {
                firstNonTrialSequence = segment.sequence;
            }
            if (segment.sequence > lastSequence) {
                lastSequence = segment.sequence;
            }
        }
        
        // Check max 1 pro-rata
        if (proRataSegments.size() > 1) {
            errors.add(new RLM_RampScheduleResponse.ApiError(
                RLM_RampScheduleResponse.ERROR_INVALID_PRORATA_POSITION,
                'Only one pro-rata segment is allowed.',
                'Found ' + proRataSegments.size() + ' pro-rata segments.'
            ));
        }
        
        // Check pro-rata position
        if (proRataSegments.size() == 1) {
            RLM_RampScheduleRequest.SegmentDefinition proRata = proRataSegments[0];
            Boolean isFirstNonTrial = (proRata.sequence == firstNonTrialSequence);
            Boolean isLast = (proRata.sequence == lastSequence);
            
            if (!isFirstNonTrial && !isLast) {
                errors.add(new RLM_RampScheduleResponse.ApiError(
                    RLM_RampScheduleResponse.ERROR_INVALID_PRORATA_POSITION,
                    'Pro-rata segment must be first (after trial) or last.',
                    'Pro-rata segment has sequence ' + proRata.sequence + 
                    '. Expected sequence ' + firstNonTrialSequence + ' or ' + lastSequence + '.'
                ));
            }
        }
        
        return errors;
    }
    
    /**
     * @description Validate segment type consistency
     * - Cannot mix YEARLY and CUSTOM types (excluding Trial/Pro-rata)
     */
    private List<RLM_RampScheduleResponse.ApiError> validateSegmentTypeConsistency(
        List<RLM_RampScheduleRequest.SegmentDefinition> segments
    ) {
        List<RLM_RampScheduleResponse.ApiError> errors = new List<RLM_RampScheduleResponse.ApiError>();
        
        Boolean hasYearly = false;
        Boolean hasCustom = false;
        
        for (RLM_RampScheduleRequest.SegmentDefinition segment : segments) {
            if (segment.segmentType == RLM_RampScheduleRequest.SEGMENT_TYPE_YEARLY) {
                hasYearly = true;
            } else if (segment.segmentType == RLM_RampScheduleRequest.SEGMENT_TYPE_CUSTOM) {
                hasCustom = true;
            }
        }
        
        if (hasYearly && hasCustom) {
            errors.add(new RLM_RampScheduleResponse.ApiError(
                RLM_RampScheduleResponse.ERROR_INCOMPATIBLE_SEGMENT_TYPES,
                'Cannot mix YEARLY and CUSTOM segment types.',
                'Schedule contains both YEARLY and CUSTOM segments. Use one type consistently.'
            ));
        }
        
        return errors;
    }
    
    /**
     * @description Validate yearly segment duration is exactly 12 months. Skipped for Staggered Ramp (yearly segments use co-term end date).
     */
    private List<RLM_RampScheduleResponse.ApiError> validateYearlyDuration(List<RLM_RampScheduleRequest.SegmentDefinition> segments, Boolean isStaggeredRamp) {
        List<RLM_RampScheduleResponse.ApiError> errors = new List<RLM_RampScheduleResponse.ApiError>();
        if (isStaggeredRamp) {
            return errors;
        }
        
        for (RLM_RampScheduleRequest.SegmentDefinition segment : segments) {
            if (segment.segmentType == RLM_RampScheduleRequest.SEGMENT_TYPE_YEARLY) {
                if (segment.startDate == null || segment.endDate == null) {
                    continue; // Skip if dates are null
                }
                
                // Calculate expected end date (start date + 12 months - 1 day)
                // e.g., Jan 1 + 12 months = Jan 1 next year, -1 day = Dec 31
                Date expectedEndDate = segment.startDate.addMonths(12).addDays(-1);
                
                if (segment.endDate != expectedEndDate) {
                    errors.add(new RLM_RampScheduleResponse.ApiError(
                        RLM_RampScheduleResponse.ERROR_INVALID_YEARLY_DURATION,
                        'Yearly segment must be exactly 12 months.',
                        'Segment ' + segment.sequence + ' (' + segment.name + '): Expected end date ' + 
                        expectedEndDate + ' but found ' + segment.endDate + '.'
                    ));
                }
            }
        }
        
        return errors;
    }
    
    /**
     * @description Validate that every segment has a non-null, positive, unique sequence.
     * A null or duplicate sequence would cause sortSegmentsBySequence to silently drop or
     * overwrite entries, leading to incorrect structural validation.
     */
    private List<RLM_RampScheduleResponse.ApiError> validateSequences(
            List<RLM_RampScheduleRequest.SegmentDefinition> segments) {
        List<RLM_RampScheduleResponse.ApiError> errors = new List<RLM_RampScheduleResponse.ApiError>();
        Set<Integer> seen = new Set<Integer>();
        for (Integer i = 0; i < segments.size(); i++) {
            RLM_RampScheduleRequest.SegmentDefinition seg = segments[i];
            if (seg.sequence == null) {
                errors.add(new RLM_RampScheduleResponse.ApiError(
                    RLM_RampScheduleResponse.ERROR_INVALID_SEQUENCE,
                    'Segment at index ' + i + ' is missing a sequence number.',
                    'Every segment must have a non-null, positive sequence value.'
                ));
            } else if (seg.sequence < 1) {
                errors.add(new RLM_RampScheduleResponse.ApiError(
                    RLM_RampScheduleResponse.ERROR_INVALID_SEQUENCE,
                    'Segment sequence must be a positive integer (got ' + seg.sequence + ').',
                    'Segment at index ' + i + ' has sequence ' + seg.sequence + '.'
                ));
            } else if (seen.contains(seg.sequence)) {
                errors.add(new RLM_RampScheduleResponse.ApiError(
                    RLM_RampScheduleResponse.ERROR_INVALID_SEQUENCE,
                    'Duplicate segment sequence: ' + seg.sequence + '.',
                    'Each segment must have a unique sequence number.'
                ));
            } else {
                seen.add(seg.sequence);
            }
        }
        return errors;
    }

    /**
     * @description Sort segments by sequence number
     */
    private List<RLM_RampScheduleRequest.SegmentDefinition> sortSegmentsBySequence(List<RLM_RampScheduleRequest.SegmentDefinition> segments) {
        // Create a map for sorting
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
}