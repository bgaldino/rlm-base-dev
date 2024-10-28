public interface IEffectiveQuantityCalculator {
    void calculateCumulativeQuantity(EffectiveQuantityDataBag effectiveQuantityDataBag);
    void calculateAssetActionSourceSum(EffectiveQuantityDataBag effectiveQuantityDataBag);
}