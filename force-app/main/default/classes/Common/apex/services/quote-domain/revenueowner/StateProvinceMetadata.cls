public with sharing class StateProvinceMetadata implements Comparable {
    @AuraEnabled
    public String name { get; set; }
    @AuraEnabled
    public String abbreviation { get; set; }
    
    public Integer compareTo(Object compareTo) {
        StateProvinceMetadata stateWrapper = (StateProvinceMetadata) compareTo;
        return abbreviation.compareTo(stateWrapper.abbreviation);      
    }
}