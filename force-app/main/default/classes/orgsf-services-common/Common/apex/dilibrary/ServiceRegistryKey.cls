public with sharing class ServiceRegistryKey {
    
    public String interfaceName;
    public Boolean isDefault;
    public String identifier;
    
    private ServiceRegistryKey(String interfaceName, Boolean isDefault, String identifier) {
        this.interfaceName = interfaceName;
        this.isDefault = isDefault;
        this.identifier = identifier;
    }
    
    public Boolean equals(Object objectToCompare) {
        if (objectToCompare instanceof ServiceRegistryKey) {
            ServiceRegistryKey keyToCompare = (ServiceRegistryKey) objectToCompare;
            Boolean interfaceNameEqual = this.interfaceName == keyToCompare.interfaceName;
            Boolean isDefaultEqual = this.isDefault == keyToCompare.isDefault;
            Boolean identifierEqual = this.identifier == keyToCompare.identifier;
            return interfaceNameEqual && isDefaultEqual && identifierEqual;
        }
        return false;
    }
    
    public Integer hashCode() {
        return (this.interfaceName != null ? this.interfaceName.hashCode() : 0) ^
               (this.isDefault != null ? this.isDefault.hashCode() : 0) ^
               (this.identifier != null ? this.identifier.hashCode() : 0);
    }
    
    public static ServiceRegistryKey createKey(String interfaceName, Boolean isDefault, String identifier) {
        return new ServiceRegistryKey(interfaceName, isDefault, identifier);
    }
    
}
