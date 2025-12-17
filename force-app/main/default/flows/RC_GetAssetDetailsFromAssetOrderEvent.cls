// ...existing code...
public class RC_GetAssetDetailsFromAssetOrderEvent {
    @InvocableMethod(label='Get Asset Details From Asset Order Event' description='Get Asset Details From Asset Order Event' category='RevCloud SE TAT')
    public static List<AssetDetailInfo> getAssetDetailsFromAssetOrderEvent(List<CreateAssetOrderEvent> assetOrderEventList){
        System.debug(LoggingLevel.DEBUG, 'Entering getAssetDetailsFromAssetOrderEvent. Input list: ' + assetOrderEventList);

        List<AssetDetailInfo> assetDetailInfoList = new List<AssetDetailInfo>();

        if (assetOrderEventList == null || assetOrderEventList.isEmpty()) {
            System.debug(LoggingLevel.WARN, 'assetOrderEventList is null or empty. Returning empty AssetDetailInfo list.');
            return assetDetailInfoList;
        }

        CreateAssetOrderEvent assetOrderEvent = assetOrderEventList[0];
        System.debug(LoggingLevel.DEBUG, 'Processing first CreateAssetOrderEvent: ' + assetOrderEvent);

        if (assetOrderEvent.AssetDetails == null || assetOrderEvent.AssetDetails.isEmpty()) {
            System.debug(LoggingLevel.WARN, 'AssetDetails on the CreateAssetOrderEvent is null or empty. Returning empty AssetDetailInfo list.');
            return assetDetailInfoList;
        }

        // Log AssetDetails size and first entry
        System.debug(LoggingLevel.DEBUG, 'AssetDetails size: ' + assetOrderEvent.AssetDetails.size());
        System.debug(LoggingLevel.DEBUG, 'First AssetDetail: ' + assetOrderEvent.AssetDetails.get(0));

        AssetDetailInfo assetDetailInfo = new AssetDetailInfo();
        assetDetailInfo.assetId = assetOrderEvent.AssetDetails.get(0).AssetId;
        assetDetailInfo.orderItemId = assetOrderEvent.AssetDetails.get(0).OrderItemId;

        assetDetailInfoList.add(assetDetailInfo);

        System.debug(LoggingLevel.INFO, 'Prepared AssetDetailInfo: ' + assetDetailInfo + ' — Returning list of size: ' + assetDetailInfoList.size());
        return assetDetailInfoList;
    }

    public class AssetDetailInfo{
        @InvocableVariable(label='Asset Id' description='Asset Id')
        public Id assetId;

        @InvocableVariable(label='Order Item Id' description='Order Item Id')
        public Id orderItemId;
    }
}