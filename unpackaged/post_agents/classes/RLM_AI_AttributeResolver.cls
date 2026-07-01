/**
 * SINGLE source of truth for product-attribute resolution on a quote line for
 * the Quinn quoting assistant.
 *
 * Before this class there were two independent attribute lookups that could
 * disagree:
 *   - RLM_AI_ProductAttributeService read the DEFINABLE set from
 *     ProductClassificationAttr (via Product2.BasedOnId) — "what CAN be set".
 *   - RLM_AI_QuoteLineAttributeService read the MATERIALIZED rows from
 *     QuoteLineItemAttribute — "what IS set" — and did so WITH USER_MODE.
 * Keyed off different objects and run under different enforcement modes, the
 * two paths resolved inconsistently: the same line could report a configurable
 * "Type" attribute one turn and "no configurable attributes" the next. That
 * inconsistency is the bug this class removes.
 *
 * resolve() returns ONE merged, de-duplicated attribute list keyed by
 * AttributeDefinitionId. An attribute is included when it is on the product's
 * classification OR already materialized on the line (the UNION) — so a line
 * with a persisted attribute is never reported as "no configurable attributes"
 * just because the classification lookup came back empty. Each entry carries
 * both the definition metadata (name, dataType, picklist values, isRequired)
 * and the line's current value (null when unset).
 *
 * Demo code: all reads run in system mode (no WITH USER_MODE). The agent's
 * permission set does not grant FLS on the attribute/classification objects,
 * and these are read-only catalog reads, so FLS enforcement only re-introduces
 * the silent-empty divergence this class exists to prevent.
 */
public with sharing class RLM_AI_AttributeResolver {

    /** One attribute on a line, merged from classification + materialized value. */
    public class ResolvedAttribute {
        public Id attributeDefinitionId;
        public String name;
        public String developerName;
        public String dataType;
        public Boolean isRequired;
        public Boolean isPriceImpacting;
        public List<String> picklistValues;   // empty for non-picklist types
        public String currentValue;            // null when not set on the line
        public Boolean isOnClassification;     // part of the definable set
        public Boolean isOnLine;               // materialized on the line
    }

    /** Result of resolving a single quote line. */
    public class Resolution {
        public Boolean lineFound = false;
        public Id productId;
        public String productName;
        public List<ResolvedAttribute> attributes = new List<ResolvedAttribute>();

        /**
         * True when the line has at least one known attribute (definable OR
         * materialized). This is THE configurability signal every consumer
         * shares — there is no second, divergent definition.
         */
        public Boolean hasAttributes() {
            return attributes != null && !attributes.isEmpty();
        }
    }

    /**
     * Resolves the merged attribute picture for a quote line. Never throws for
     * a missing line — returns a Resolution with lineFound=false instead — so
     * callers map it to their own friendly message. Throws only on genuine
     * system/query errors, which callers catch and report.
     */
    public static Resolution resolve(Id quoteLineItemId) {
        Resolution res = new Resolution();
        if (quoteLineItemId == null) {
            return res;
        }

        // Line + product + classification id in one query.
        List<QuoteLineItem> qlis = [
            SELECT Product2Id, Product2.Name, Product2.BasedOnId
            FROM QuoteLineItem
            WHERE Id = :quoteLineItemId
            LIMIT 1
        ];
        if (qlis.isEmpty()) {
            return res;
        }
        res.lineFound = true;
        res.productId = qlis[0].Product2Id;
        res.productName = qlis[0].Product2 != null ? qlis[0].Product2.Name : null;
        Id classificationId = qlis[0].Product2 != null ? qlis[0].Product2.BasedOnId : null;

        // Definable set: the active, editable, visible attributes for the
        // product's classification. Empty when the product has no classification.
        Map<Id, ProductClassificationAttr> classByAttrDefId =
            new Map<Id, ProductClassificationAttr>();
        if (classificationId != null) {
            for (ProductClassificationAttr pca : [
                SELECT AttributeDefinitionId, IsRequired, IsPriceImpacting
                FROM ProductClassificationAttr
                WHERE ProductClassificationId = :classificationId
                  AND Status = 'Active'
                  AND IsReadOnly = false
                  AND IsHidden = false
            ]) {
                classByAttrDefId.put(pca.AttributeDefinitionId, pca);
            }
        }

        // Materialized values: what is currently set on the line.
        Map<Id, QuoteLineItemAttribute> lineByAttrDefId =
            new Map<Id, QuoteLineItemAttribute>();
        for (QuoteLineItemAttribute qlia : [
            SELECT AttributeName, AttributeValue, IsPriceImpacting, AttributeDefinitionId
            FROM QuoteLineItemAttribute
            WHERE QuoteLineItemId = :quoteLineItemId
        ]) {
            if (qlia.AttributeDefinitionId != null) {
                lineByAttrDefId.put(qlia.AttributeDefinitionId, qlia);
            }
        }

        // Union of both sources. This is the merge that makes the two old paths
        // converge: an attribute counts as known when it is definable OR set.
        Set<Id> attrDefIds = new Set<Id>();
        attrDefIds.addAll(classByAttrDefId.keySet());
        attrDefIds.addAll(lineByAttrDefId.keySet());
        if (attrDefIds.isEmpty()) {
            return res;
        }

        Map<Id, AttributeDefinition> defs = new Map<Id, AttributeDefinition>([
            SELECT Id, Name, DeveloperName, DataType, PicklistId
            FROM AttributeDefinition
            WHERE Id IN :attrDefIds
        ]);

        // Picklist values for any picklist-typed attribute, one query for all.
        Set<Id> picklistIds = new Set<Id>();
        for (AttributeDefinition ad : defs.values()) {
            if (ad.DataType == 'Picklist' && ad.PicklistId != null) {
                picklistIds.add(ad.PicklistId);
            }
        }
        Map<Id, List<String>> valuesByPicklist = new Map<Id, List<String>>();
        if (!picklistIds.isEmpty()) {
            for (AttributePicklistValue pv : [
                SELECT Name, Code, PicklistId
                FROM AttributePicklistValue
                WHERE PicklistId IN :picklistIds
                ORDER BY Name ASC
            ]) {
                if (!valuesByPicklist.containsKey(pv.PicklistId)) {
                    valuesByPicklist.put(pv.PicklistId, new List<String>());
                }
                valuesByPicklist.get(pv.PicklistId).add(
                    String.isNotBlank(pv.Name) ? pv.Name : pv.Code
                );
            }
        }

        // Build the merged list. Definition order is by attribute name for a
        // stable, user-friendly presentation across calls.
        List<AttributeDefinition> ordered = new List<AttributeDefinition>(defs.values());
        ordered.sort(new AttributeDefinitionNameComparator());

        for (AttributeDefinition ad : ordered) {
            ProductClassificationAttr pca = classByAttrDefId.get(ad.Id);
            QuoteLineItemAttribute qlia = lineByAttrDefId.get(ad.Id);

            ResolvedAttribute ra = new ResolvedAttribute();
            ra.attributeDefinitionId = ad.Id;
            ra.name = String.isNotBlank(ad.Name)
                ? ad.Name
                : (qlia != null ? qlia.AttributeName : null);
            ra.developerName = ad.DeveloperName;
            ra.dataType = ad.DataType;
            ra.isOnClassification = (pca != null);
            ra.isOnLine = (qlia != null);
            ra.isRequired = (pca != null && pca.IsRequired == true);
            // Price impact: prefer the classification flag; fall back to the line's.
            ra.isPriceImpacting = pca != null
                ? (pca.IsPriceImpacting == true)
                : (qlia != null && qlia.IsPriceImpacting == true);
            ra.currentValue = (qlia != null) ? qlia.AttributeValue : null;
            ra.picklistValues = (ad.DataType == 'Picklist' && ad.PicklistId != null
                    && valuesByPicklist.containsKey(ad.PicklistId))
                ? valuesByPicklist.get(ad.PicklistId)
                : new List<String>();

            res.attributes.add(ra);
        }
        return res;
    }

    /**
     * Serializes a resolution's attributes to the JSON array the planner and the
     * invocable actions consume. Each entry carries the full picture so a single
     * call answers both "what can I set" and "what is set now".
     */
    public static String toJson(List<ResolvedAttribute> attributes) {
        List<Map<String, Object>> rows = new List<Map<String, Object>>();
        if (attributes != null) {
            for (ResolvedAttribute ra : attributes) {
                Map<String, Object> entry = new Map<String, Object>{
                    'name'             => ra.name,
                    'developerName'    => ra.developerName,
                    'dataType'         => ra.dataType,
                    'isRequired'       => ra.isRequired,
                    'isPriceImpacting' => ra.isPriceImpacting,
                    'attributeId'      => ra.attributeDefinitionId,
                    'currentValue'     => ra.currentValue
                };
                if (ra.dataType == 'Picklist') {
                    entry.put('picklistValues',
                        ra.picklistValues != null ? ra.picklistValues : new List<String>());
                }
                rows.add(entry);
            }
        }
        return JSON.serialize(rows);
    }

    private class AttributeDefinitionNameComparator implements Comparator<AttributeDefinition> {
        public Integer compare(AttributeDefinition a, AttributeDefinition b) {
            String na = a != null && a.Name != null ? a.Name.toLowerCase() : '';
            String nb = b != null && b.Name != null ? b.Name.toLowerCase() : '';
            if (na == nb) return 0;
            return na < nb ? -1 : 1;
        }
    }
}
