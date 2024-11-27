public with sharing class GetStateCodeFlowAction {
    private static IRevenueOwnerService revenueOwnerService = (IRevenueOwnerService)ServiceRegistry.getInstance('IRevenueOwnerService');

    private static final Map<String, Map<String, String>> COUNTRY_TO_STATE_CONVERSION_MAP = new Map<String, Map<String, String>>();

    @InvocableMethod(label='Fetches the State Code from the State/Country Input')
    public static List<GetStateCodeWrapper> flowActionGetStateCode(List<GetStateCodeWrapper> wrappers) {

        for (GetStateCodeWrapper wrapper : wrappers) {
            if (String.isBlank(wrapper.countryIsoCode)) {
                wrapper.stateCode = '';
                continue;
            }

            if (!COUNTRY_TO_STATE_CONVERSION_MAP.containsKey(wrapper.countryIsoCode)) {
                populateMapForCountry(wrapper.countryIsoCode);
            }
            
            if (String.isBlank(wrapper.inputState)) {
                wrapper.stateCode = '';
                continue;
            }

            wrapper.stateCode = COUNTRY_TO_STATE_CONVERSION_MAP?.get(wrapper.countryIsoCode)?.get(wrapper.inputState.toUpperCase()) ?? '';
        }
        return wrappers;
    }

    private static void populateMapForCountry(String countryIsoCode) {
        Map<String, String> stateAbbrMappings = new Map<String, String>();

        List<StateProvinceMetadata> stateMetadataList = revenueOwnerService.getStateProvinceMetadataList(countryIsoCode);

        if (stateMetadataList == null || stateMetadataList.isEmpty()) {
            COUNTRY_TO_STATE_CONVERSION_MAP.put(countryIsoCode, stateAbbrMappings);
            return;
        }
        for (StateProvinceMetadata stateProvinceMetadata : stateMetadataList) {
            stateAbbrMappings.put((stateProvinceMetadata.name ?? '').toUpperCase(), stateProvinceMetadata.abbreviation);
            stateAbbrMappings.put((stateProvinceMetadata.abbreviation ?? '').toUpperCase(), stateProvinceMetadata.abbreviation);
        }

        COUNTRY_TO_STATE_CONVERSION_MAP.put(countryIsoCode, stateAbbrMappings);
    }

    public class GetStateCodeWrapper {
        @InvocableVariable(required=true)
        public String countryIsoCode;

        @InvocableVariable(required=false)
        public String inputState;
        
        @InvocableVariable(required=false)
        public String stateCode;
    }
}