public class RLM_DetermineDROSourceType {
    @InvocableMethod(label='Determine DRO Source Type' description='Returns string value of source object that initiated DRO Fulfillment' category='RLM SE TAT')
    public static List<String> returnDROSourceObjectType(List<droSourceInfo> sourceInfoArray){

        droSourceInfo sourceInfo = sourceInfoArray.get(0);

        List<String> sourceObjectType = new List<String>();

        if(sourceInfo.recordId != null){
            Id sourceId = sourceInfo.recordId;
            sourceObjectType.add(String.valueOf(sourceId.getSObjectType()));

            system.debug('Source Object Type is ' + sourceObjectType);
        }else if(sourceInfo.recordIds != null){
            Id sourceId = sourceInfo.recordIds.get(0);
            sourceObjectType.add(String.valueOf(sourceId.getSObjectType())+'s');

            system.debug('Source Object Type is ' + sourceObjectType);
        }

        return sourceObjectType;
    }

    public class droSourceInfo{
        @InvocableVariable
        public String recordId;

        @InvocableVariable
        public List<String> recordIds;
    }
}