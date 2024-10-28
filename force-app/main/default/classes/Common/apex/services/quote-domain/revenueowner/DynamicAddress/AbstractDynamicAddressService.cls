public with sharing abstract class AbstractDynamicAddressService implements IDynamicAddressService {
    public virtual DynamicAddressSchema getAddressSchemaForCountry(String isoCode) {
        throw new NotImplementedException();
    }
}
