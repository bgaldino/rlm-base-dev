/**
 * Read-only asset timeline data for the Asset-Based Ordering console's
 * "Portfolio Timeline" tab. Returns per-asset AssetStatePeriod points (MRR +
 * quantity) for an account so the LWC can render a Chart.js timeline.
 *
 * All SOQL runs WITH USER_MODE so object/field access is enforced against the
 * running user's permissions (see .cursor/skills/apex-security-hardening).
 */
public with sharing class RLM_AccountAssetPortfolioService {

    // ----------------------------------------------------
    // WRAPPERS
    // ----------------------------------------------------
    public class PortfolioResponse {
        @AuraEnabled public List<AssetWrapper> assets;
        @AuraEnabled public List<PointWrapper> points;

        public PortfolioResponse() {
            assets = new List<AssetWrapper>();
            points = new List<PointWrapper>();
        }
    }

    public class AssetWrapper {
        @AuraEnabled public Id id;
        @AuraEnabled public String name;
        @AuraEnabled public String productName;
    }

    public class PointWrapper {
        @AuraEnabled public Id assetId;
        @AuraEnabled public String startDate; // yyyy-MM-dd (string, not date)
        @AuraEnabled public Decimal quantity;
        @AuraEnabled public Decimal mrr;
    }

    // ----------------------------------------------------
    // SAFE DATE -> STRING (NO format() USED)
    // ----------------------------------------------------
    private static String toIsoDate(Date d) {
        if (d == null) return null;

        Integer m = d.month();
        Integer day = d.day();

        String mm  = (m < 10 ? '0' + String.valueOf(m) : String.valueOf(m));
        String dd  = (day < 10 ? '0' + String.valueOf(day) : String.valueOf(day));

        return d.year() + '-' + mm + '-' + dd;
    }

    // ----------------------------------------------------
    // MAIN METHOD - MRR & QUANTITY ONLY
    // ----------------------------------------------------
    @AuraEnabled(cacheable=true)
    public static PortfolioResponse getAccountAssetTimeline(Id accountId) {
        PortfolioResponse resp = new PortfolioResponse();
        if (accountId == null) return resp;

        // Typed-Id validation at entry (rejects malformed / cross-type ids).
        Id acctId = Id.valueOf(accountId);

        // 1) Load Assets (user-mode enforced)
        List<Asset> assets = [
            SELECT Id, Name, Product2.Name
            FROM Asset
            WHERE AccountId = :acctId
            WITH USER_MODE
        ];
        if (assets.isEmpty()) return resp;

        Map<Id, AssetWrapper> assetMap = new Map<Id, AssetWrapper>();

        for (Asset a : assets) {
            AssetWrapper aw = new AssetWrapper();
            aw.id = a.Id;
            aw.name = a.Name;
            aw.productName = (a.Product2 != null ? a.Product2.Name : null);

            resp.assets.add(aw);
            assetMap.put(a.Id, aw);
        }

        // 2) Load State Periods (user-mode enforced)
        List<AssetStatePeriod> periods = [
            SELECT AssetId, StartDate, Quantity, Mrr
            FROM AssetStatePeriod
            WHERE AssetId IN :assetMap.keySet()
            WITH USER_MODE
            ORDER BY StartDate ASC
        ];

        // 3) Convert periods -> timeline points
        for (AssetStatePeriod p : periods) {
            if (p.StartDate == null) continue;

            PointWrapper pt = new PointWrapper();
            pt.assetId   = p.AssetId;
            pt.startDate = toIsoDate(p.StartDate.date()); // SAFE STRING
            pt.quantity  = p.Quantity;
            pt.mrr       = p.Mrr;

            resp.points.add(pt);
        }

        return resp;
    }
}
