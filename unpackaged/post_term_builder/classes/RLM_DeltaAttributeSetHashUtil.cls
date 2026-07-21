public with sharing class RLM_DeltaAttributeSetHashUtil {

    @TestVisible
    private static final String EMPTY_SET_SENTINEL = 'RLM_ATTRIBUTE_SET_HASH_EMPTY_V1';

    public class ResolvedAttribute {
        public Id attributeDefinitionId;
        public Boolean isPicklist;
        public Id picklistValueId;
        public String freeTextValue;
    }

    public static ResolvedAttribute resolve(QuoteLineItemAttribute attr) {
        ResolvedAttribute r = new ResolvedAttribute();
        r.attributeDefinitionId = attr.AttributeDefinitionId;
        if (attr.AttributePicklistValueId != null) {
            r.isPicklist = true;
            r.picklistValueId = attr.AttributePicklistValueId;
            r.freeTextValue = null;
        } else {
            r.isPicklist = false;
            r.picklistValueId = null;
            r.freeTextValue = String.isBlank(attr.AttributeValue) ? '' : attr.AttributeValue;
        }
        return r;
    }

    public static String computeHash(List<QuoteLineItemAttribute> attrs) {
        if (attrs == null || attrs.isEmpty()) {
            return digest(EMPTY_SET_SENTINEL);
        }

        List<ResolvedAttribute> resolved = new List<ResolvedAttribute>();
        for (QuoteLineItemAttribute attr : attrs) {
            resolved.add(resolve(attr));
        }
        resolved.sort(new ByAttributeDefinitionId());

        List<String> rows = new List<String>();
        for (ResolvedAttribute r : resolved) {
            rows.add(serializeRow(r));
        }
        return digest(String.join(rows, '\n'));
    }

    private static String serializeRow(ResolvedAttribute r) {
        String kind = r.isPicklist ? 'P' : 'F';
        String value = r.isPicklist ? String.valueOf(r.picklistValueId) : r.freeTextValue;
        return r.attributeDefinitionId + kind + value.length() + ':' + value;
    }

    private static String digest(String canonical) {
        Blob hash = Crypto.generateDigest('SHA-256', Blob.valueOf(canonical));
        return EncodingUtil.base64Encode(hash);
    }

    private class ByAttributeDefinitionId implements Comparator<ResolvedAttribute> {
        public Integer compare(ResolvedAttribute a, ResolvedAttribute b) {
            return String.valueOf(a.attributeDefinitionId).compareTo(String.valueOf(b.attributeDefinitionId));
        }
    }
}
