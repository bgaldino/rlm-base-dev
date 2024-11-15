public with sharing class ServiceRegistry {

    private static final Map<ServiceRegistryKey, Type> SERVICE_CONTAINER_DEFINITION = new Map<ServiceRegistryKey, Type>(); 

    private static final Map<Type, Object> SERVICE_REGISTRY_INSTANCE = new Map<Type, Object>();

    static {
        List<ServiceRegistryBinding__mdt> bindings = getServiceRegistryMetadata();
        updateServiceContainerDefinition(bindings);
    }

    public static Object getInstance(String type) {
        ServiceRegistryKey key = ServiceRegistryKey.createKey(type, true, '');
        return getInstance(key);
    }

    private static object getInstance(ServiceRegistryKey key) {
        if(!SERVICE_CONTAINER_DEFINITION.containsKey(key)) {
            throw new ServiceRegistryException(' Invalid Type ');
        }
        Type instanceType = SERVICE_CONTAINER_DEFINITION.get(key);
        
        if(SERVICE_REGISTRY_INSTANCE.containsKey(instanceType)) {
            return SERVICE_REGISTRY_INSTANCE.get(instanceType);
        }

        SERVICE_REGISTRY_INSTANCE.put(instanceType, instanceType.newInstance());
        return SERVICE_REGISTRY_INSTANCE.get(instanceType);
    }

    public static Object getInstance(String type, String identifier) {
        ServiceRegistryKey key = ServiceRegistryKey.createKey(type, false, identifier);
        return getInstance(key);
    }

    private static List<ServiceRegistryBinding__mdt> getServiceRegistryMetadata() {
        List<ServiceRegistryBinding__mdt> bindings = new List<ServiceRegistryBinding__mdt> ();
        bindings = [SELECT To__c, Type__c, Technology__c, Identifier__c, Default__c FROM ServiceRegistryBinding__mdt Where Technology__c = 'Apex' WITH SECURITY_ENFORCED];
        return bindings;
    }

    private static void updateServiceContainerDefinition(List<ServiceRegistryBinding__mdt> bindings) {
        for (ServiceRegistryBinding__mdt eachRecord : bindings) {
            Type instanceType = System.type.forName(eachRecord.To__c);
            updateDefaultDefinition(eachRecord, instanceType);
            updateNonDefaultDefinition(eachRecord, instanceType);
        }
    }

    private static void updateDefaultDefinition(ServiceRegistryBinding__mdt eachRecord, Type instanceType) {
        if(!eachRecord.Default__c) {
            return;
        }
        SERVICE_CONTAINER_DEFINITION.put(ServiceRegistryKey.createKey(eachRecord.Type__c, true, ''), instanceType);

        if(String.isNotBlank(eachRecord.Identifier__c)) {
            SERVICE_CONTAINER_DEFINITION.put(ServiceRegistryKey.createKey(eachRecord.Type__c, false, eachRecord.Identifier__c), instanceType);
        }
    }

    private static void updateNonDefaultDefinition(ServiceRegistryBinding__mdt eachRecord, Type instanceType) {
        if(eachRecord.Default__c) {
            return;
        }
        SERVICE_CONTAINER_DEFINITION.put(ServiceRegistryKey.createKey(eachRecord.Type__c, false, eachRecord.Identifier__c), instanceType);
    }

    
    public static void injectInstance(String type, String identifier, Object instance) {
        ServiceRegistryKey key = ServiceRegistryKey.createKey(type, false, identifier);
        injectInstance(key, instance);
    }

    
    public static void injectDefaultInstance(String type, Object instance) { 
        ServiceRegistryKey key = ServiceRegistryKey.createKey(type, true, '');
        injectInstance(key, instance);
    }

    @TestVisible
    private static void injectMockInstance(String type, String identifier, String instanceName, Object instance) {
        ServiceRegistryKey key = ServiceRegistryKey.createKey(type, false, identifier);
        injectInstance(key, instanceName, instance);
    }

    @TestVisible
    private static void injectMockDefaultInstance(String type, String instanceName, Object instance) { 
        ServiceRegistryKey key = ServiceRegistryKey.createKey(type, true, '');
        injectInstance(key, instanceName,instance);
    }

    private static void injectInstance(ServiceRegistryKey key, Object instance) {
        if (instance == null) {
            throw new ServiceRegistryException('The instance was null.');
        }
        String instanceName = String.valueOf(instance).substringBefore(':');
        injectInstance(key, instanceName, instance);
    }


    private static void injectInstance(ServiceRegistryKey key, String instanceName, Object instance) {
        if (instance == null) {
            throw new ServiceRegistryException('The instance was null.');
        }

        try {
            Type classType = System.Type.forName(instanceName);
            SERVICE_CONTAINER_DEFINITION.put(key, classType);
            SERVICE_REGISTRY_INSTANCE.put(classType, instance);
        } catch (Exception ex) {
            throw new ServiceRegistryException('Failed Injection Creation ' + ex.getMessage());
        }
    }
}
