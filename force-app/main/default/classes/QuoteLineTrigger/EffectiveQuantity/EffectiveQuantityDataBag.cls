public with sharing class EffectiveQuantityDataBag {
    public QuoteLineTriggerDataBag quoteLineTriggerDataBag { get; set; }

    //Key for the 2 below is a hash of QuoteId/ProductId/ProductSellingModelId
    public Map<Integer, Double> cumulativeQuantityMap = new Map<Integer,Double>();
    public Map<Integer, Integer> longestQLITermInMonths = new Map<Integer, Integer>();
    
    //Key for the 2 below is a hash of AccountId/ProductId/ProductSellingModelId
    public Map<Integer, List<AssetActionSource>> assetActionSourceMap = new Map<Integer, List<AssetActionSource>>();
    public Map<Integer, Integer> longestAssetTermInMonths = new Map<Integer, Integer>();

}