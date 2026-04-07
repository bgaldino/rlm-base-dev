// Resolve portable names to target-org IDs in SeqPolicySelectionCondition.FilterValue.
// The qb-billing data plan stores a human-readable record Name in FilterValue for
// Reference-type conditions. This script replaces each name with the correct
// target-org ID by deriving the SObject type from FilterField (strip trailing "Id")
// and querying that object by Name.
// Runs after insert_billing_data.
// Uses fully dynamic SOQL/DML to avoid compile-time SObject type resolution errors.

// Collect all Reference-type conditions dynamically
List<SObject> conditions = Database.query(
    'SELECT Id, FilterField, FilterValue ' +
    'FROM SeqPolicySelectionCondition ' +
    'WHERE FilterFieldType = \'Reference\' ' +
    'AND FilterValue != null'
);

if (conditions.isEmpty()) {
    System.debug(LoggingLevel.INFO, 'resolveSeqPolicyConditionRefs: no Reference conditions found.');
    return;
}

// Group conditions by SObject type (derived from FilterField by stripping trailing "Id")
// e.g. "LegalEntityId" -> "LegalEntity", "AccountId" -> "Account"
Map<String, List<SObject>> byObjectType = new Map<String, List<SObject>>();
Map<String, Set<String>> namesByObjectType = new Map<String, Set<String>>();

for (SObject c : conditions) {
    String field = (String) c.get('FilterField');
    String objectType = field.endsWith('Id') ? field.left(field.length() - 2) : field;
    if (!byObjectType.containsKey(objectType)) {
        byObjectType.put(objectType, new List<SObject>());
        namesByObjectType.put(objectType, new Set<String>());
    }
    byObjectType.get(objectType).add(c);
    namesByObjectType.get(objectType).add((String) c.get('FilterValue'));
}

// For each SObject type, query Name -> Id and patch FilterValue
List<SObject> toUpdate = new List<SObject>();

for (String objectType : byObjectType.keySet()) {
    Set<String> names = namesByObjectType.get(objectType);
    Map<String, Id> idByName = new Map<String, Id>();
    try {
        String soql = 'SELECT Id, Name FROM ' + objectType + ' WHERE Name IN :names';
        for (SObject obj : Database.query(soql)) {
            idByName.put((String) obj.get('Name'), (Id) obj.get('Id'));
        }
    } catch (Exception e) {
        System.debug(LoggingLevel.ERROR, 'resolveSeqPolicyConditionRefs: failed to query ' + objectType + ': ' + e.getMessage());
        continue;
    }

    for (SObject c : byObjectType.get(objectType)) {
        String currentValue = (String) c.get('FilterValue');
        Id resolvedId = idByName.get(currentValue);
        if (resolvedId != null) {
            c.put('FilterValue', resolvedId);
            toUpdate.add(c);
        } else {
            System.debug(LoggingLevel.WARN, 'resolveSeqPolicyConditionRefs: no ' + objectType + ' found with Name = "' + currentValue + '"');
        }
    }
}

if (!toUpdate.isEmpty()) {
    Database.update(toUpdate, false);
    System.debug(LoggingLevel.INFO, 'resolveSeqPolicyConditionRefs: updated ' + toUpdate.size() + ' condition(s).');
}
