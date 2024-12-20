public with sharing class TaxSchemaParser {
    private static final String MIN_LENGTH = 'minLength';
    private static final String MAX_LENGTH = 'maxLength';
    private static final String PATTERN = 'pattern';
    private static final String KEY_IF = 'if';
    private static final String KEY_THEN = 'then';
    private static final String PROPERTIES = 'properties';
    private static final String KEY_ENUM = 'enum';
    private static final String REQUIRED = 'required';
    private static final String ALLOF = 'allOf';

    public static TaxValidationSchema makeTaxValidationSchema(Map<String, Object> taxValidationSchemaMap) {
        TaxValidationSchema taxValidationSchema = new TaxValidationSchema();
        if (taxValidationSchemaMap == null || taxValidationSchemaMap.isEmpty()) {
            return taxValidationSchema;
        }
        parseRequiredFields(taxValidationSchema.requiredFields, taxValidationSchemaMap);
        parseValidationSchemaOptions(taxValidationSchema, taxValidationSchemaMap);
        return taxValidationSchema;
    }

    private static void parseRequiredFields(List<String> targetList, Map<String, Object> node) {
        List<Object> requiredFieldsList = (List<Object>) node.get(REQUIRED);
        system.debug(requiredFieldsList);
        if (requiredFieldsList == null || requiredFieldsList.size() == 0) {
            return;
        }
        
        for (Object requiredField : requiredFieldsList) {
            targetList.add(String.valueOf(requiredField));
        }
    }

    /*
        Parse ALLOF Schema Options
    */
    private static void parseValidationSchemaOptions(TaxValidationSchema taxValidationSchema, Map<String, Object> taxValidationSchemaMap) {
        List<Object> allOfList = (List<Object>) taxValidationSchemaMap?.get(ALLOF);
        if (allOfList == null || allOfList.size() == 0) {
            return;
        }

        for (Object validationOptionNode : allOfList) {
            taxValidationSchema.taxValidationSchemaOptions.add(makeValidationSchemaOption((Map<String, Object>) validationOptionNode));
        }
    }

    private static TaxValidationSchemaOption makeValidationSchemaOption(Map<String, Object> validationOptionNode) {
        if (validationOptionNode == null || validationOptionNode.size() == 0) {
            return null;
        }

        TaxValidationSchemaOption option = new TaxValidationSchemaOption();
        parseIf(option, validationOptionNode);
        parseThen(option, validationOptionNode);

        return option;
    }

    /*
        Parse IF half of the JSON
    */
    private static void parseIf(TaxValidationSchemaOption option, Map<String, Object> validationOptionNode) {
        Map<String, Object> ifNode = (Map<String, Object>) validationOptionNode.get(KEY_IF);
        if (ifNode == null || ifNode.size() == 0) {
            return;
        }

        Map<String, Object> propertiesNode = (Map<String, Object>) ifNode.get(PROPERTIES);
        if (propertiesNode == null || propertiesNode.size() == 0) {
            return;
        }

        for (String propertyKey : propertiesNode.keySet()) {
            parseIfProperty(option, propertyKey, (Map<String, Object>) propertiesNode.get(propertyKey));
        }
    }

    private static void parseIfProperty(TaxValidationSchemaOption option, String key, Map<String, Object> ifPropertyNode) {
        if (ifPropertyNode == null || ifPropertyNode.size() == 0) {
            return;
        }

        List<Object> enumValues = (List<Object>) ifPropertyNode.get(KEY_ENUM);
        if (enumValues == null || enumValues.size() == 0) {
            return;
        }

        List<String> values = new List<String>();
        for (Object enumValue : enumValues) {
            values.add(String.valueOf(enumValue));
        }

        option.matchIf.put(key, values);
    }

    /*
        Parse THEN half of the JSON
    */
    private static void parseThen(TaxValidationSchemaOption option, Map<String, Object> validationOptionNode) {
        Map<String, Object> thenNode = (Map<String, Object>) validationOptionNode.get(KEY_THEN);
        if (thenNode == null || thenNode.size() == 0) {
            return;
        }

        parseRequiredFields(option.requiredFields, thenNode);
        parseThenProperties(option, thenNode);
    }

    private static void parseThenProperties(TaxValidationSchemaOption option, Map<String, Object> thenNode) {
        Map<String, Object> propertiesNode = (Map<String, Object>) thenNode.get(PROPERTIES);
        if (propertiesNode == null || propertiesNode.size() == 0) {
            return;
        }
        
        for (String keyName : propertiesNode.keySet()) {
            Map<String, Object> validationData = (Map<String, Object>) propertiesNode.get(keyName);
            option.validationProperties.put(keyName, makeValidationProperty(validationData));
        }
    }


    private static TaxValidationSchemaProperty makeValidationProperty(Map<String, Object> validationData ) {
        TaxValidationSchemaProperty validationProperty = new TaxValidationSchemaProperty();
        if (validationData.containsKey(MIN_LENGTH)) {
            validationProperty.minimumLength = Integer.valueOf(validationData.get(MIN_LENGTH));
        }
        if (validationData.containsKey(MAX_LENGTH)) {
            validationProperty.maximumLength = Integer.valueOf(validationData.get(MAX_LENGTH));
        }
        if (validationData.containsKey(PATTERN)) {
            validationProperty.regexPattern = String.valueOf(validationData.get(PATTERN));
        }
        return validationProperty;
    }
}