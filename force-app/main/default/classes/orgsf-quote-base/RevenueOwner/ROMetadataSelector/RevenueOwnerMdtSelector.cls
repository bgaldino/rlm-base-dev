public with sharing class RevenueOwnerMdtSelector implements IRevenueOwnerMdtSelector {
    public List<ROCountryAugmentation__mdt> getEligibleCountries() {
        return [
            SELECT CountryISOCode__c, CountryName__c
            FROM ROCountryAugmentation__mdt
            WHERE IsQuotable__c = TRUE
            WITH SECURITY_ENFORCED
        ];
    }

    public ROCountryAugmentation__mdt getSupplementalData(String countryIsoCode) {
        if (countryIsoCode == null) {
            return null;
        }

        Set<String> countryIsoCodes = new Set<String>{ countryIsoCode };

        List<ROCountryAugmentation__mdt> metadataRecords = getSupplementalDataList(countryIsoCodes);

        if (metadataRecords.isEmpty()) {
            return null;
        }

        return metadataRecords.get(0);
    }

    private static Map<String, ROCountryAugmentation__mdt> supplementalDataCache = new Map<String, ROCountryAugmentation__mdt>();

    public List<ROCountryAugmentation__mdt> getSupplementalDataList(Set<String> countryIsoCodes) {
        // Calculate cache miss
        Set<String> countryCodesToQuery = new Set<String>();
        for (String countryIsoCode : countryIsoCodes) {
            if (!supplementalDataCache.containsKey(countryIsoCode)) {
                countryCodesToQuery.add(countryIsoCode);
            }
        }

        // Fetch missing data
        if (!countryCodesToQuery.isEmpty()) {
            List<ROCountryAugmentation__mdt> queriedRecords = querySupplementalDataList(countryCodesToQuery);

            for (ROCountryAugmentation__mdt record : queriedRecords) {
                supplementalDataCache.put(record.CountryISOCode__c, record);
            }
        }

        // build result
        List<ROCountryAugmentation__mdt> records = new List<ROCountryAugmentation__mdt>();
        for (String countryIsoCode : countryIsoCodes) {
            if (supplementalDataCache.containsKey(countryIsoCode)) {
                records.add(supplementalDataCache.get(countryIsoCode));
            }
            else {
                System.debug(LoggingLevel.WARN, 'No record found for Country Code ' + countryIsoCode);
            }
        }

        return records;
    }

    private List<ROCountryAugmentation__mdt> querySupplementalDataList(Set<String> countryIsoCodes) {
        return [
            SELECT
                AllowedPaymentMethods__c,
                CountryISOCode__c,
                CountryName__c,
                IsQuotable__c,
                AddressRenderTemplate__c,
                TaxIdSample__c,
                IsBusinessTypeApplicable__c,
                IsNoTaxRegistrationIdReasonApplicable__c
            FROM ROCountryAugmentation__mdt
            WHERE CountryISOCode__c IN :countryIsoCodes
            WITH SECURITY_ENFORCED
        ];
    }

    public List<ROCountryAddressField__mdt> getDefaultAddressFieldData() {
        return [
            SELECT
                Id,
                CountryISOCode__c,
                FieldId__c,
                FieldLabel__c,
                IsDefault__c,
                IsOptional__c,
                IsRequired__c,
                MapToField__c,
                MapToProperty__c,
                ValidationRegex__c,
                HelpText__c,
                ValidationErrorText__c,
                PlaceholderText__c
            FROM ROCountryAddressField__mdt
            WHERE IsDefault__c = TRUE
            WITH SECURITY_ENFORCED
        ];
    }

    public List<ROCountryAddressField__mdt> getAddressFieldDataForCountry(String countryIsoCode) {
        return [
            SELECT
                Id,
                CountryISOCode__c,
                FieldId__c,
                FieldLabel__c,
                IsDefault__c,
                IsOptional__c,
                IsRequired__c,
                MapToField__c,
                MapToProperty__c,
                ValidationRegex__c,
                HelpText__c,
                ValidationErrorText__c,
                PlaceholderText__c
            FROM ROCountryAddressField__mdt
            WHERE CountryISOCode__c = :countryIsoCode
            WITH SECURITY_ENFORCED
        ];
    }
}
