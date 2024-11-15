public with sharing class RevenueOwnerServiceHelper {
    private static final String CHAPI_ERROR = 'error';
    private static final String CHAPI_ERROR_INVALID_CLIENT = 'Invalid Client';
    private static final String CHAPI_CODE = 'code';
    private static final String CHAPI_COUNTRY = 'chapiCountry';
    private static final String CHAPI_SUPPORTED_CURRENCIES = 'supportedCurrencies';
    private static final String CHAPI_CURRENCY_CODE = 'currencyCode';
    private static final String CHAPI_DEFAULT_CURRENCY = 'defaultCurrency';
    private static final String CHAPI_TAX_VALIDATION_SCHEMA = 'taxValidationSchema';
    private static final String CHAPI_PROPERTIES = 'properties';
    private static final String CHAPI_BUSINESS_TYPE = 'businessType';
    private static final String CHAPI_ENUM = 'enum';
    private static final String CHAPI_REVENUE_OWNER = 'revenueOwner';
    private static final String CHAPI_ISO_CODE = 'ISOCode';
    private static final String CHAPI_COUNTRY_NAME = 'countryName';
    private static final String CHAPI_STATE_PROVINCES = 'stateProvinces';
    private static final String CHAPI_ZIP_CODE_REQUIRED = 'zipCodeRequired';
    private static final String CHAPI_TAX_ID_INFORMATION = 'taxIdInformation';
    private static final String CHAPI_TAX_ID_REQUIRED = 'taxIdRequired';
    private static final String CHAPI_TAX_ID_LABEL = 'taxIdLabel';
    private static final String CHAPI_TAX_ID_FORMAT = 'taxIdFormat';
    private static final String CHAPI_TAX_ID_EXEMPTION_LABEL = 'taxIdExemptionLabel';
    private static final String BUSINESS_TYPE_B2B = 'BUSINESS_TO_BUSINESS';
    private static final String CHAPI_CC_MERCHANT_INFO = 'chapiCCMerchantInfo';
    private static final String CYBERSOURCE_ENDPOINT_IFRAME = 'cyberSourceEndPointIframe';
    private static final String IS_3DS2 = 'is3DS2';
    private static final String SECRET_KEY = 'secretKey';
    private static final String MERCHANT_ID = 'merchantId';
    private static final String ACCESS_KEY = 'accessKey';
    private static final String PROFILE_ID = 'profileId';
    private static final String VALID_CREDIT_CARD_TYPES = 'validCreditCardTypes';
    private static final String COMPLIANCE_LANGUAGE_FOR_CC = 'complianceLanguageForCC';
    private static final String CHAPI_DATA_MAP = 'dataMap';
    private static final String CHAPI_TAX_ERRORS = 'errors';

    public static Map<String, Object> parseResponse(String jsonResponse) {
        Map<String, Object> chapiResponse = (Map<String, Object>) JSON.deserializeUntyped(jsonResponse);
        if (chapiResponse == null || (String) chapiResponse.get(CHAPI_ERROR) == CHAPI_ERROR_INVALID_CLIENT) {
            return null;
        }

        Integer responseCode = Integer.valueOf((String) chapiResponse.get(CHAPI_CODE));
        List<Object> chapiCountries = (List<Object>) chapiResponse.get(CHAPI_COUNTRY);

        if (responseCode >= 2000 && responseCode <= 2999 && chapiCountries.size() == 1) {
            return (Map<String, Object>) chapiCountries[0];
        }

        return null;
    }

    public static Map<String, Object> parseTaxValidationResponse(String jsonResponse) {
        Map<String, Object> chapiResponse = (Map<String, Object>) JSON.deserializeUntyped(jsonResponse);
        if (chapiResponse == null || (String) chapiResponse.get(CHAPI_ERROR) == CHAPI_ERROR_INVALID_CLIENT) {
            return null;
        }
        Integer responseCode = Integer.valueOf((String) chapiResponse.get(CHAPI_CODE));
        if (responseCode == 2000) {
            return (Map<String, Object>) chapiResponse.get(CHAPI_DATA_MAP);
        }
        if (responseCode == 4308) {
            return new Map<String, Object>{ 'error' => chapiResponse.get(CHAPI_TAX_ERRORS) };
        }
        return null;
    }

    public static List<SupportedCurrency> unwrapSupportedCurrencies(Map<String, Object> chapiCountry) {
        List<SupportedCurrency> supportedCurrencies = new List<SupportedCurrency>();
        List<Object> chapiSupportedCurrencies = (List<Object>) chapiCountry.get(CHAPI_SUPPORTED_CURRENCIES);

        if (chapiSupportedCurrencies == null || chapiSupportedCurrencies.size() == 0) {
            return supportedCurrencies;
        }

        for (Object chapiSupportedCurrencyObj : chapiSupportedCurrencies) {
            Map<String, Object> chapiSupportedCurrency = (Map<String, Object>) chapiSupportedCurrencyObj;

            SupportedCurrency supportedCurrency = new SupportedCurrency(
                (String) chapiSupportedCurrency.get(CHAPI_CURRENCY_CODE),
                (Boolean) chapiSupportedCurrency.get(CHAPI_DEFAULT_CURRENCY)
            );
            supportedCurrencies.add(supportedCurrency);
        }

        return supportedCurrencies;
    }

    public static List<String> unwrapBusinessTypes(Map<String, Object> chapiCountry) {
        List<String> businessTypes = new List<String>();

        Map<String, Object> taxValidationSchema = (Map<String, Object>) chapiCountry?.get(CHAPI_TAX_VALIDATION_SCHEMA);
        Map<String, Object> properties = (Map<String, Object>) taxValidationSchema?.get(CHAPI_PROPERTIES);
        Map<String, Object> businessType = (Map<String, Object>) properties?.get(CHAPI_BUSINESS_TYPE);
        List<Object> businessTypesObjs = (List<Object>) businessType?.get(CHAPI_ENUM);

        if (businessTypesObjs == null || businessTypesObjs.size() == 0) {
            return businessTypes;
        }

        for (Object businessTypeObj : businessTypesObjs) {
            businessTypes.add((String) businessTypeObj);
        }
        return businessTypes;
    }

    public static String unwrapRevenueOwner(Map<String, Object> chapiCountry) {
        return (String) chapiCountry.get(CHAPI_REVENUE_OWNER);
    }

    public static String unwrapISOCode(Map<String, Object> chapiCountry) {
        return (String) chapiCountry.get(CHAPI_ISO_CODE);
    }

    public static String unwrapCountryName(Map<String, Object> chapiCountry) {
        return (String) chapiCountry.get(CHAPI_COUNTRY_NAME);
    }

    public static Boolean unwrapZipCodeRequired(Map<String, Object> chapiCountry) {
        return (Boolean) chapiCountry.get(CHAPI_ZIP_CODE_REQUIRED);
    }

    public static Map<String, String> unwrapLabelTranslations(Map<String, Object> chapiCountry) {
        return (Map<String, String>) chapiCountry.get('countryLabelTranslations');
    }

    public static TaxInformation unwrapTaxInformation(Map<String, Object> chapiCountry, ROCountryAugmentation__mdt augmentationData) {
        TaxInformation taxInformation = new TaxInformation();

        Map<String, Object> taxIdInformationMap = (Map<String, Object>) chapiCountry.get(CHAPI_TAX_ID_INFORMATION);
        if (taxIdInformationMap == null || taxIdInformationMap.size() == 0) {
            return taxInformation;
        }
        taxInformation.isTaxIdRequired = (Boolean) taxIdInformationMap.get(CHAPI_TAX_ID_REQUIRED);
        taxInformation.taxIdLabel = (String) taxIdInformationMap.get(CHAPI_TAX_ID_LABEL);
        taxInformation.taxIdFormatRegex = (String) taxIdInformationMap.get(CHAPI_TAX_ID_FORMAT);
        taxInformation.taxIdExemptionLabel = (String) taxIdInformationMap.get(CHAPI_TAX_ID_EXEMPTION_LABEL);
        taxInformation.taxIdSample = augmentationData?.TaxIdSample__c;
        taxInformation.isBusinessTypeApplicable = augmentationData?.IsBusinessTypeApplicable__c;
        taxInformation.isNoTaxRegistrationIdReasonApplicable = augmentationData?.IsNoTaxRegistrationIdReasonApplicable__c;
        taxInformation.taxValidationSchema = TaxSchemaParser.makeTaxValidationSchema((Map<String, Object>) chapiCountry?.get(CHAPI_TAX_VALIDATION_SCHEMA));
        return taxInformation;
    }

    public static List<StateProvinceMetadata> unwrapStateProvinceData(Map<String, Object> chapiCountry) {
        List<StateProvinceMetadata> stateProvinceMetadataList = new List<StateProvinceMetadata>();

        Map<String, Object> stateProvinceMap = (Map<String, Object>) chapiCountry.get(CHAPI_STATE_PROVINCES);
        if (stateProvinceMap == null || stateProvinceMap.size() == 0) {
            return stateProvinceMetadataList;
        }

        for (String abbreviation : stateProvinceMap.keySet()) {
            StateProvinceMetadata stateProvinceMetadata = new StateProvinceMetadata();
            stateProvinceMetadata.name = (String) stateProvinceMap.get(abbreviation);
            stateProvinceMetadata.abbreviation = abbreviation;
            stateProvinceMetadataList.add(stateProvinceMetadata);
        }

        return stateProvinceMetadataList;
    }

    public static MerchantInfo unwrapMerchantInfo(Map<String, Object> chapiCountry) {
        MerchantInfo merchantInfo = new MerchantInfo();

        Map<String, Object> merchantInfoMap = (Map<String, Object>) chapiCountry.get(CHAPI_CC_MERCHANT_INFO);
        if (merchantInfoMap == null || merchantInfoMap.size() == 0) {
            return merchantInfo;
        }

        merchantInfo.cyberSourceEndPointIframe = (String) merchantInfoMap.get(CYBERSOURCE_ENDPOINT_IFRAME);
        merchantInfo.is3DS2 = (Boolean) merchantInfoMap.get(IS_3DS2);
        merchantInfo.secretKey = (String) merchantInfoMap.get(SECRET_KEY);
        merchantInfo.merchantId = (String) merchantInfoMap.get(MERCHANT_ID);
        merchantInfo.accessKey = (String) merchantInfoMap.get(ACCESS_KEY);
        merchantInfo.profileId = (String) merchantInfoMap.get(PROFILE_ID);
        merchantInfo.complianceLanguageForCC = (String) merchantInfoMap.get(COMPLIANCE_LANGUAGE_FOR_CC);
        merchantInfo.returnURL = 'https://' + DomainCreator.getVisualforceHostname('c') + '/apex/PaymentDetailReceipt';

        merchantInfo.validCreditCardTypes = new List<String>();
        for (Object validCreditCardType : (List<Object>) merchantInfoMap.get(VALID_CREDIT_CARD_TYPES)) {
            merchantInfo.validCreditCardTypes.add((String) validCreditCardType);
        }

        return merchantInfo;
    }

    public static RevenueOwnerCountryDetail makeRevenueOwnerCountryDetail(Map<String, Object> chapiCountry, ROCountryAugmentation__mdt augmentationData) {
        RevenueOwnerCountryDetail revenueOwnerCountryDetail = new RevenueOwnerCountryDetail();
        revenueOwnerCountryDetail.isoCode = unwrapISOCode(chapiCountry);
        revenueOwnerCountryDetail.name = unwrapCountryName(chapiCountry);
        revenueOwnerCountryDetail.revenueOwner = unwrapRevenueOwner(chapiCountry);
        revenueOwnerCountryDetail.supportedCurrencies = unwrapSupportedCurrencies(chapiCountry);
        revenueOwnerCountryDetail.paymentMethods = fromCommaSeparatedString(augmentationData?.AllowedPaymentMethods__c);
        revenueOwnerCountryDetail.businessTypes = unwrapBusinessTypes(chapiCountry);
        revenueOwnerCountryDetail.zipCodeMetadata = makeZipCodeMetadata(chapiCountry, augmentationData);
        revenueOwnerCountryDetail.taxInformation = unwrapTaxInformation(chapiCountry, augmentationData);
        revenueOwnerCountryDetail.stateProvinceMetadataList = unwrapStateProvinceData(chapiCountry);

        return revenueOwnerCountryDetail;
    }

    public static ZipCodeMetadata makeZipCodeMetadata(Map<String, Object> chapiCountry, ROCountryAugmentation__mdt augmentationData) {
        ZipCodeMetadata zipCodeMetadata = new ZipCodeMetadata();
        zipCodeMetadata.isRequired = unwrapZipCodeRequired(chapiCountry);
        return zipCodeMetadata;
    }

    public static List<String> fromCommaSeparatedString(String commaString) {
        if (commaString == null) {
            return null;
        }

        List<String> values = commaString.split(',');
        for (Integer i = 0; i < values.size(); i++) {
            values[i] = values[i].trim();
        }
        return values;
    }
}
