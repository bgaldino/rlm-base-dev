public class RLM_DetermineDROSourceType {
    /**
     * One output per input, in input order (the Flow bulk contract). An input that names no usable
     * record id (none, an empty list, or a malformed id) gets a blank output instead of a platform
     * exception, so the calling flow's decision falls to its default branch.
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
