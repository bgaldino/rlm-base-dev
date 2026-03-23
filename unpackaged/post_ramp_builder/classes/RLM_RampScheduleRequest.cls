/**
 * @description Request wrapper for Ramp Schedule API
 * Contains all input parameters for creating or validating a ramp schedule
 */
public class RLM_RampScheduleRequest {
    
    @AuraEnabled public String quoteId { get; set; }
    @AuraEnabled public String action { get; set; } // VALIDATE or CREATE
    @AuraEnabled public ScheduleHeader scheduleHeader { get; set; }
    @AuraEnabled public List<SegmentDefinition> segments { get; set; }
    @AuraEnabled public MigrationContext migrationContext { get; set; }

    /**
     * When true, uses direct DML to create the ramp group structure only (parent
     * RampScheduleGroup + N child segment groups with IsRamped=true). Synchronous,
     * single transaction, returns group IDs immediately. Does NOT distribute or stamp
     * line items — RampIdentifier/SegmentIdentifier are only assigned by the platform
     * via the EditGroup API, not via DML.
     *
     * The DML path (default, true) is the correct primary workflow:
     *   1. Creates empty parent RampScheduleGroup + N child segment groups (IsRamped=true)
     *   2. No products yet — the quote should be empty when the ramp builder runs
     *   3. User then adds products via catalog; the platform natively clones them
     *      across all ramp segments automatically
     *
     * When explicitly set to false, uses the Connect REST API (EditGroup +
     * CloneSalesTransaction + EditRampSchedule) via an async Queueable. This path
     * migrates pre-existing QLIs and distributes them across segments — intended
     * for ramping a quote that already has products on it (advanced / experimental).
     */
    @AuraEnabled public Boolean useDmlApproach { get; set; }

    // Action constants
    public static final String ACTION_VALIDATE = 'VALIDATE';
    public static final String ACTION_CREATE = 'CREATE';
    
    // Schedule Type constants
    public static final String SCHEDULE_TYPE_YEARLY = 'YEARLY';
    public static final String SCHEDULE_TYPE_CUSTOM = 'CUSTOM';
    
    // Segment Type constants
    public static final String SEGMENT_TYPE_TRIAL = 'TRIAL';
    public static final String SEGMENT_TYPE_YEARLY = 'YEARLY';
    public static final String SEGMENT_TYPE_CUSTOM = 'CUSTOM';
    public static final String SEGMENT_TYPE_PRORATA = 'PRO-RATED';
    
    /**
     * @description Schedule header containing high-level schedule details
     */
    public class ScheduleHeader {
        @AuraEnabled public String scheduleName { get; set; }
        @AuraEnabled public Date startDate { get; set; }
        @AuraEnabled public String scheduleType { get; set; } // YEARLY or CUSTOM
        @AuraEnabled public String rampMode { get; set; } // Standard Ramp or Staggered Ramp
        
        public ScheduleHeader() {}
    }
    
    /**
     * @description Individual segment definition
     */
    public class SegmentDefinition {
        @AuraEnabled public Integer sequence { get; set; }
        @AuraEnabled public String name { get; set; }
        @AuraEnabled public String segmentType { get; set; } // TRIAL, YEARLY, CUSTOM, PRO-RATED
        @AuraEnabled public Date startDate { get; set; }
        @AuraEnabled public Date endDate { get; set; }
        @AuraEnabled public Decimal discountPercent { get; set; }
        @AuraEnabled public Decimal upliftPercent { get; set; }
        
        public SegmentDefinition() {
            this.discountPercent = 0;
            this.upliftPercent = 0;
        }
    }
    
    /**
     * @description Migration context for P1 - moving existing line items
     */
    public class MigrationContext {
        @AuraEnabled public List<String> sourceLineItemIds { get; set; }
        
        public MigrationContext() {
            this.sourceLineItemIds = new List<String>();
        }
    }
    
    public RLM_RampScheduleRequest() {
        this.segments = new List<SegmentDefinition>();
        this.migrationContext = new MigrationContext();
        this.useDmlApproach = true; // DML is the correct primary path
    }
}