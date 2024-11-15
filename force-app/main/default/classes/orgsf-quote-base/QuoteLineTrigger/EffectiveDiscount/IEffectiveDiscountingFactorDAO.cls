public interface IEffectiveDiscountingFactorDAO {

    List<EffectiveDiscountingFactor__mdt> getEffectiveDiscountingFactorForCountryAndCurrency(String countryCode, String currencyCode);

}