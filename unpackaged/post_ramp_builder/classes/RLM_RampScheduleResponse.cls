/**
 * @description Response wrapper for Ramp Schedule API
 * Contains the result of create/validate operations
 */
public class RLM_RampScheduleResponse {
    
    @AuraEnabled public Boolean success { get; set; }
    @AuraEnabled public ResponseData data { get; set; }
    @AuraEnabled public List<ApiError> errors { get; set; }
    
    /**
     * @description Response data containing created record IDs
     */
    public class ResponseData {
        @AuraEnabled public String rampScheduleGroupId { get; set; }
        @AuraEnabled public List<String> segmentGroupIds { get; set; }
        @AuraEnabled public String message { get; set; }
        /** AsyncApexJob ID of the enqueued migration job (API path only). */
        @AuraEnabled public String jobId { get; set; }
        
        public ResponseData() {
            this.segmentGroupIds = new List<String>();
        }
    }
    
    /**
     * @description API error structure
     */
    public class ApiError {
        @AuraEnabled public String code { get; set; }
        @AuraEnabled public String message { get; set; }
        @AuraEnabled public String details { get; set; }
        
        public ApiError() {}
        
        public ApiError(String code, String message) {
            this.code = code;
            this.message = message;
        }
        
        public ApiError(String code, String message, String details) {
            this.code = code;
            this.message = message;
            this.details = details;
        }
    }
    
    // Error code constants
    public static final String ERROR_INVALID_QUOTE_ID = 'INVALID_QUOTE_ID';
    public static final String ERROR_EMPTY_SCHEDULE = 'EMPTY_SCHEDULE';
    public static final String ERROR_INVALID_DATE = 'INVALID_DATE';
    public static final String ERROR_INVALID_DATE_RANGE = 'INVALID_DATE_RANGE';
    public static final String ERROR_INVALID_DISCOUNT = 'INVALID_DISCOUNT';
    public static final String ERROR_INVALID_UPLIFT = 'INVALID_UPLIFT';
    public static final String ERROR_SEGMENT_DISCONTINUITY = 'SEGMENT_DISCONTINUITY';
    public static final String ERROR_TRIAL_FEATURE_DISABLED = 'TRIAL_FEATURE_DISABLED';
    public static final String ERROR_INVALID_TRIAL_CONFIG = 'INVALID_TRIAL_CONFIG';
    public static final String ERROR_INVALID_PRORATA_POSITION = 'INVALID_PRORATA_POSITION';
    public static final String ERROR_INCOMPATIBLE_SEGMENT_TYPES = 'INCOMPATIBLE_SEGMENT_TYPES';
    public static final String ERROR_INVALID_YEARLY_DURATION = 'INVALID_YEARLY_DURATION';
    public static final String ERROR_INVALID_SOURCE_LINES = 'INVALID_SOURCE_LINES';
    public static final String ERROR_INVALID_ACTION = 'INVALID_ACTION';
    public static final String ERROR_DML_EXCEPTION = 'DML_EXCEPTION';
    
    public RLM_RampScheduleResponse() {
        this.success = false;
        this.errors = new List<ApiError>();
        this.data = new ResponseData();
    }
    
    /**
     * @description Create a success response
     */
    public static RLM_RampScheduleResponse success(String rampScheduleGroupId, List<String> segmentGroupIds, String message) {
        return success(rampScheduleGroupId, segmentGroupIds, message, null);
    }

    /**
     * @description Create a success response with an async job ID (API path)
     */
    public static RLM_RampScheduleResponse success(String rampScheduleGroupId, List<String> segmentGroupIds, String message, String jobId) {
        RLM_RampScheduleResponse response = new RLM_RampScheduleResponse();
        response.success = true;
        response.data.rampScheduleGroupId = rampScheduleGroupId;
        response.data.segmentGroupIds = segmentGroupIds;
        response.data.message = message;
        response.data.jobId = jobId;
        return response;
    }
    
    /**
     * @description Create a failure response with errors
     */
    public static RLM_RampScheduleResponse failure(List<ApiError> errors) {
        RLM_RampScheduleResponse response = new RLM_RampScheduleResponse();
        response.success = false;
        response.errors = errors;
        return response;
    }
    
    /**
     * @description Create a failure response with a single error
     */
    public static RLM_RampScheduleResponse failure(String code, String message) {
        RLM_RampScheduleResponse response = new RLM_RampScheduleResponse();
        response.success = false;
        response.errors.add(new ApiError(code, message));
        return response;
    }
    
    /**
     * @description Create a failure response with a single error including details
     */
    public static RLM_RampScheduleResponse failure(String code, String message, String details) {
        RLM_RampScheduleResponse response = new RLM_RampScheduleResponse();
        response.success = false;
        response.errors.add(new ApiError(code, message, details));
        return response;
    }
}