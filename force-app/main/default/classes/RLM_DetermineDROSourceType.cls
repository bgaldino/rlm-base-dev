public class RLM_DetermineDROSourceType {
    /**
     * One output per input, in input order (the Flow bulk contract). A non-blank recordId wins when both
     * inputs are set, even a malformed one; otherwise recordIds[0] alone decides, and the object name gets
     * an "s" suffix. An input whose deciding id is missing or malformed gets a blank output instead of a
     * platform exception.
     * Callers must handle a blank output. See RLM_Assetize_Order_DRO_Fulfillment for how the shipped flow does.
     */
    @InvocableMethod(label='Determine DRO Source Type' description='Returns string value of source object that initiated DRO Fulfillment' category='RLM SE TAT')
    public static List<String> returnDROSourceObjectType(List<droSourceInfo> sourceInfoArray){
        List<String> sourceObjectTypes = new List<String>();
        if(sourceInfoArray == null){
            return sourceObjectTypes;
        }

        for(droSourceInfo sourceInfo : sourceInfoArray){
            sourceObjectTypes.add(resolveSourceType(sourceInfo));
        }
        return sourceObjectTypes;
    }

    private static String resolveSourceType(droSourceInfo sourceInfo){
        if(sourceInfo == null){
            return '';
        }

        try{
            if(String.isNotBlank(sourceInfo.recordId)){
                return objectName(sourceInfo.recordId, '');
            }
            if(sourceInfo.recordIds != null && !sourceInfo.recordIds.isEmpty() && String.isNotBlank(sourceInfo.recordIds[0])){
                return objectName(sourceInfo.recordIds[0], 's');
            }
        }catch(StringException e){
            system.debug('Not a valid record id: ' + e.getMessage());
        }
        return '';
    }

    private static String objectName(String recordId, String suffix){
        Schema.SObjectType sourceType = Id.valueOf(recordId).getSObjectType();
        return sourceType == null ? '' : String.valueOf(sourceType) + suffix;
    }

    public class droSourceInfo{
        @InvocableVariable
        public String recordId;

        @InvocableVariable
        public List<String> recordIds;
    }
}
