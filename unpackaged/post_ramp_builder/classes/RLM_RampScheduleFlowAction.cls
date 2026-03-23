/**
 * @description Invocable Action for Ramp Schedule API
 * Provides @InvocableMethod for Flow invocation
 */
public with sharing class RLM_RampScheduleFlowAction {
    
    /**
     * @description Input wrapper for the invocable method
     */
    public class FlowInput {
        @InvocableVariable(label='Quote ID' required=true description='The ID of the Quote')
        public String quoteId;
        
        @InvocableVariable(label='Schedule Name' required=true description='Name of the ramp schedule')
        public String scheduleName;
        
        @InvocableVariable(label='Schedule Type' description='YEARLY or CUSTOM')
        public String scheduleType;

        @InvocableVariable(label='Ramp Mode' description='Standard Ramp or Staggered Ramp')
        public String rampMode;
        
        @InvocableVariable(label='Segments JSON' required=true description='JSON array of segment definitions')
        public String segmentsJson;
        
        @InvocableVariable(label='Action' description='VALIDATE or CREATE (default: CREATE)')
        public String action;
    }
    
    /**
     * @description Output wrapper for the invocable method
     */
    public class FlowOutput {
        @InvocableVariable(label='Success' description='Whether the operation succeeded')
        public Boolean success;
        
        @InvocableVariable(label='Ramp Schedule Group ID' description='ID of the created parent group')
        public String rampScheduleGroupId;
        
        @InvocableVariable(label='Segment Group IDs' description='Comma-separated IDs of created segment groups')
        public String segmentGroupIds;
        
        @InvocableVariable(label='Message' description='Success or error message')
        public String message;
        
        @InvocableVariable(label='Error Code' description='Error code if failed')
        public String errorCode;
        
        @InvocableVariable(label='Error Details' description='Detailed error information')
        public String errorDetails;
        
        @InvocableVariable(label='Job ID' description='AsyncApexJob ID of the background migration job (API path)')
        public String jobId;
    }
    
    /**
     * @description Create or validate a ramp schedule
     * @param inputs List of FlowInput (bulkified)
     * @return List of FlowOutput
     */
    @InvocableMethod(
        label='Create Ramp Schedule' 
        description='Creates or validates a ramp schedule based on segment definitions'
        category='Ramp Schedule'
    )
    public static List<FlowOutput> execute(List<FlowInput> inputs) {
        List<FlowOutput> outputs = new List<FlowOutput>();
        RLM_RampScheduleService service = new RLM_RampScheduleService();
        
        for (FlowInput input : inputs) {
            FlowOutput output = new FlowOutput();
            
            try {
                // Build request
                RLM_RampScheduleRequest request = buildRequest(input);
                
                // Execute via service
                RLM_RampScheduleResponse response = service.execute(request);
                
                // Map response to output
                output.success = response.success;
                
                if (response.success) {
                    output.rampScheduleGroupId = response.data.rampScheduleGroupId;
                    output.segmentGroupIds = String.join(response.data.segmentGroupIds, ',');
                    output.message = response.data.message;
                    output.jobId = response.data.jobId;
                } else {
                    output.message = getFirstErrorMessage(response.errors);
                    output.errorCode = getFirstErrorCode(response.errors);
                    output.errorDetails = getErrorDetails(response.errors);
                    // Throw so Flow fault connector runs and user sees Error screen instead of Success
                    throw new RLM_RampScheduleFlowException(output.message, output.errorDetails);
                }
                
            } catch (RLM_RampScheduleFlowException e) {
                throw e;
            } catch (Exception e) {
                // Wrap unexpected exceptions so the Flow fault connector runs and the
                // user sees the Error screen rather than the success/confirmation screens.
                throw new RLM_RampScheduleFlowException(
                    'An unexpected error occurred.',
                    e.getMessage() + ' at ' + e.getStackTraceString()
                );
            }
            
            outputs.add(output);
        }
        
        return outputs;
    }
    
    /**
     * @description Build RLM_RampScheduleRequest from FlowInput
     */
    private static RLM_RampScheduleRequest buildRequest(FlowInput input) {
        RLM_RampScheduleRequest request = new RLM_RampScheduleRequest();
        request.quoteId = input.quoteId;
        request.action = String.isBlank(input.action) ? RLM_RampScheduleRequest.ACTION_CREATE : input.action;
        
        // Build header
        request.scheduleHeader = new RLM_RampScheduleRequest.ScheduleHeader();
        request.scheduleHeader.scheduleName = input.scheduleName;
        request.scheduleHeader.scheduleType = input.scheduleType;
        request.scheduleHeader.rampMode = input.rampMode;
        
        // Parse segments from JSON
        if (String.isNotBlank(input.segmentsJson)) {
            List<Object> segmentsList = (List<Object>) JSON.deserializeUntyped(input.segmentsJson);
            request.segments = new List<RLM_RampScheduleRequest.SegmentDefinition>();
            
            for (Object segObj : segmentsList) {
                Map<String, Object> seg = (Map<String, Object>) segObj;
                RLM_RampScheduleRequest.SegmentDefinition segment = new RLM_RampScheduleRequest.SegmentDefinition();
                
                segment.sequence = parseInteger(seg.get('sequence'));
                segment.name = (String) seg.get('name');
                segment.segmentType = (String) seg.get('segmentType');
                segment.startDate = parseDate(seg.get('startDate'));
                segment.endDate = parseDate(seg.get('endDate'));
                segment.discountPercent = parseDecimal(seg.get('discountPercent'));
                segment.upliftPercent = parseDecimal(seg.get('upliftPercent'));
                
                request.segments.add(segment);
            }
        }
        
        return request;
    }
    
    /**
     * @description Helper to parse date from various formats
     */
    private static Date parseDate(Object dateValue) {
        if (dateValue == null) {
            return null;
        }
        if (dateValue instanceof Date) {
            return (Date) dateValue;
        }
        if (dateValue instanceof String) {
            String dateStr = (String) dateValue;
            if (dateStr.contains('-')) {
                List<String> parts = dateStr.split('-');
                return Date.newInstance(
                    Integer.valueOf(parts[0]),
                    Integer.valueOf(parts[1]),
                    Integer.valueOf(parts[2].substring(0, Math.min(2, parts[2].length())))
                );
            }
        }
        return null;
    }
    
    /**
     * @description Helper to parse decimal
     */
    private static Decimal parseDecimal(Object value) {
        if (value == null) {
            return null;
        }
        if (value instanceof Decimal) {
            return (Decimal) value;
        }
        if (value instanceof Integer) {
            return Decimal.valueOf((Integer) value);
        }
        if (value instanceof Long) {
            return Decimal.valueOf((Long) value);
        }
        if (value instanceof Double) {
            return Decimal.valueOf((Double) value);
        }
        if (value instanceof String) {
            return Decimal.valueOf((String) value);
        }
        return null;
    }
    
    /**
     * @description Helper to parse integer
     */
    private static Integer parseInteger(Object value) {
        if (value == null) {
            return null;
        }
        if (value instanceof Integer) {
            return (Integer) value;
        }
        if (value instanceof Long) {
            return ((Long) value).intValue();
        }
        if (value instanceof Decimal) {
            return ((Decimal) value).intValue();
        }
        if (value instanceof Double) {
            return ((Double) value).intValue();
        }
        if (value instanceof String) {
            return Integer.valueOf((String) value);
        }
        return null;
    }
    
    /**
     * @description Get first error message
     */
    private static String getFirstErrorMessage(List<RLM_RampScheduleResponse.ApiError> errors) {
        if (errors != null && !errors.isEmpty()) {
            return errors[0].message;
        }
        return 'Unknown error';
    }
    
    /**
     * @description Get first error code
     */
    private static String getFirstErrorCode(List<RLM_RampScheduleResponse.ApiError> errors) {
        if (errors != null && !errors.isEmpty()) {
            return errors[0].code;
        }
        return 'UNKNOWN_ERROR';
    }
    
    /**
     * @description Get all error details as a single string
     */
    private static String getErrorDetails(List<RLM_RampScheduleResponse.ApiError> errors) {
        if (errors == null || errors.isEmpty()) {
            return '';
        }
        
        List<String> details = new List<String>();
        for (RLM_RampScheduleResponse.ApiError err : errors) {
            String detail = err.code + ': ' + err.message;
            if (String.isNotBlank(err.details)) {
                detail += ' (' + err.details + ')';
            }
            details.add(detail);
        }
        
        return String.join(details, '; ');
    }
}