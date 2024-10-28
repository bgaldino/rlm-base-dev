public with sharing class BillingInfoServiceHelper {

    private static IBillingInformationSelector billingInfoSelector = (IBillingInformationSelector)ServiceRegistry.getInstance('IBillingInformationSelector');

    public static IResponse validateRequest(IRequest request) {
        IResponse response = new BaseResponse();
        if(request == null) {
            response.setErrorMessage(BillingInfoServiceErrorCodes.NULL_REQUEST.name());
        } else if(request.getRequestItems().size() == 0) {
            response.setErrorMessage(BillingInfoServiceErrorCodes.EMPTY_REQUEST_ITEMS_LIST.name());
        }
        return response;
    }

    public static BillingInfoServiceResponseItem validateCreateRequestItem(BillingInfoServiceRequestItem requestItem) {
        
        BillingInfoServiceResponseItem responseItem = new BillingInfoServiceResponseItem(requestItem.getRequestItemId());
        validateNotNull(
            requestItem.billingInfo,
            BillingInfoServiceErrorCodes.NULL_BILLING_INFO.name(), 
            responseItem
        );
        if(responseItem.isSuccess() != null && responseItem.isSuccess() == false) {
            return responseItem;
        }
        validateNull(
            requestItem.billingInfo.billingInformationId, 
            BillingInfoServiceErrorCodes.BILLING_INFO_ID_NOT_REQUIRED.name(), 
            responseItem
        );
        validateNotNull(
            requestItem.billingInfo.name, 
            BillingInfoServiceErrorCodes.NULL_BILLING_INFO_NAME.name(), 
            responseItem
        );
        validateNotNull(
            requestItem.billingInfo.accountId, 
            BillingInfoServiceErrorCodes.NULL_ACCOUNT_ID.name(), 
            responseItem
        );
        if(requestItem.billingInfo.name != null && requestItem.billingInfo.accountId != null) {
            validateDuplicateName(
                requestItem.billingInfo.name,
                requestItem.billingInfo.accountId,
                BillingInfoServiceErrorCodes.DUPLICATE_BILLING_INFO_NAME.name(),
                responseItem
            );
        }
        validateNotNull(
            requestItem.billingInfo.primaryContact, 
            BillingInfoServiceErrorCodes.NULL_PRIMARY_CONTACT.name(), 
            responseItem
        );
        validateNotNull(
            requestItem.billingInfo.autoRenewPreference, 
            BillingInfoServiceErrorCodes.NULL_AUTO_RENEW_PREFERENCE.name(), 
            responseItem
        );
        validateNotNull(
            requestItem.billingInfo.autoRenewPreference, 
            BillingInfoServiceErrorCodes.NULL_AUTO_RENEW_PREFERENCE.name(), 
            responseItem
        );
        if(requestItem.billingInfo.autoRenewPreference.equals('Yes')) {
            validateNotNull(
                requestItem.billingInfo.renewalTerm, 
                BillingInfoServiceErrorCodes.NULL_RENEWAL_TERM.name(), 
                responseItem
            );
        }
        validateNotNull(
            requestItem.billingInfo.frequency, 
            BillingInfoServiceErrorCodes.NULL_BILLING_FREQUENCY.name(), 
            responseItem
        );
        validateNotNull(
            requestItem.billingInfo.language, 
            BillingInfoServiceErrorCodes.NULL_BILLING_LANGUAGE.name(), 
            responseItem
        );
        validateNotNull(
            requestItem.billingInfo.country, 
            BillingInfoServiceErrorCodes.NULL_BILLING_COUNTRY.name(), 
            responseItem
        );
        validateNotNull(
            requestItem.billingInfo.billingCurrency, 
            BillingInfoServiceErrorCodes.NULL_BILLING_CURRENCY.name(), 
            responseItem
        );
        validateNotNull(
            requestItem.billingInfo.billingCompanyName, 
            BillingInfoServiceErrorCodes.NULL_BILLING_COMPANY_NAME.name(), 
            responseItem
        );
        
        validateNotNull(
            requestItem.billingInfo.invoiceDispatchMethod, 
            BillingInfoServiceErrorCodes.NULL_INVOICE_DISPATCH_METHOD.name(), 
            responseItem
        );
        validateNotNull(
            requestItem.billingInfo.paymentMethod, 
            BillingInfoServiceErrorCodes.NULL_PAYMENT_METHOD.name(), 
            responseItem
        );
        validateNotNull(
            requestItem.billingInfo.paymentTerm, 
            BillingInfoServiceErrorCodes.NULL_PAYMENT_TERM.name(), 
            responseItem
        );
        validateNotNull(
            requestItem.billingInfo.preBillDays, 
            BillingInfoServiceErrorCodes.NULL_PRE_BILL_DAYS.name(), 
            responseItem
        );
        validateNotNull(
            requestItem.billingInfo.businessType, 
            BillingInfoServiceErrorCodes.NULL_BUSINESS_TYPE.name(), 
            responseItem
        );
        if(requestItem.billingInfo.taxRegistrationId == null) {
            validateNotNull(
                requestItem.billingInfo.noTaxRegistrationIdReason, 
                BillingInfoServiceErrorCodes.NULL_NO_TAX_REGISTRATION_ID_REASON.name(), 
                responseItem
            );
        }
        validateNotNull(
            requestItem.billingInfo.taxExemptStatus, 
            BillingInfoServiceErrorCodes.NULL_TAX_EXEMPT_STATUS.name(), 
            responseItem
        );
        if(requestItem.billingInfo.taxExemptStatus == 'Exempt') {
            validateNotNull(
                requestItem.billingInfo.taxExemptionId, 
                BillingInfoServiceErrorCodes.NULL_TAX_EXEMPTION_ID.name(), 
                responseItem
            );
        }
        if(responseItem.isSuccess() == null || responseItem.isSuccess() != false) {
            validateDuplicateBillingInfo(
                requestItem.billingInfo,
                BillingInfoServiceErrorCodes.DUPLICATE_BILLING_INFO.name(),
                responseItem
            );
        }
        return responseItem;
    }

    public static BillingInfoServiceResponseItem validateUpdateRequestItem(BillingInfoServiceRequestItem requestItem) {
        BillingInfoServiceResponseItem responseItem = new BillingInfoServiceResponseItem(requestItem.getRequestItemId());
        validateNotNull(
            requestItem.billingInfo,
            BillingInfoServiceErrorCodes.NULL_BILLING_INFO.name(), 
            responseItem
        );
        if(responseItem.isSuccess() != null && responseItem.isSuccess() == false) {
            return responseItem;
        }
        validateNotNull(
            requestItem.billingInfo.billingInformationId, 
            BillingInfoServiceErrorCodes.BILLING_INFO_ID_REQUIRED.name(), 
            responseItem
        );
        validateNull(
            requestItem.billingInfo.accountId, 
            BillingInfoServiceErrorCodes.CANNOT_UPDATE_ACCOUNT.name(), 
            responseItem
        );
        validateNull(
            requestItem.billingInfo.country, 
            BillingInfoServiceErrorCodes.CANNOT_UPDATE_COUNTRY.name(), 
            responseItem
        );
        validateNull(
            requestItem.billingInfo.billingCurrency, 
            BillingInfoServiceErrorCodes.CANNOT_UPDATE_CURRENCY.name(), 
            responseItem
        );
        return responseItem;
    }

    public static BillingInformation__c createBillingInformationFromPOJO(BillingInformation billingInfo) {
        BillingInformation__c billingInfoRecord = new BillingInformation__c();
        copyBillingInfo(billingInfoRecord, billingInfo);
        copyTaxInfo(billingInfoRecord, billingInfo);
        return billingInfoRecord;
    }

    public static BillingInformation createBillingInfoPOJOFromRecord(BillingInformation__c billingInfoRecord) {
        BillingInformation billingInfo = new BillingInformation();
        billingInfo.billingInformationId = billingInfoRecord.Id;
        billingInfo.name = billingInfoRecord.Name;
        billingInfo.accountId = billingInfoRecord.Account__c;
        billingInfo.primaryContact = billingInfoRecord.PrimaryBillingContact__c;
        billingInfo.secondaryContact = billingInfoRecord.SecondaryBillingContact__c;
        billingInfo.autoRenewPreference = billingInfoRecord.AutoRenewal__c;
        billingInfo.frequency = billingInfoRecord.BillingFrequency__c;
        billingInfo.language = billingInfoRecord.BillingLanguage__c;
        billingInfo.country = billingInfoRecord.BillingCountry__c;
        billingInfo.billingCurrency = billingInfoRecord.CurrencyIsoCode;
        billingInfo.invoiceDispatchMethod = billingInfoRecord.InvoiceDispatchMethod__c;
        billingInfo.paymentMethod = billingInfoRecord.PaymentMethod__c;
        billingInfo.paymentTerm = billingInfoRecord.PaymentTerm__c;
        billingInfo.preBillDays = Integer.valueOf(billingInfoRecord.PreBillDays__c);
        billingInfo.renewalTerm = Integer.valueOf(billingInfoRecord.RenewalTerm__c);
        billingInfo.businessType = billingInfoRecord.BusinessType__c;
        billingInfo.taxExemptStatus = billingInfoRecord.TaxExemptStatus__c;
        billingInfo.taxExemptionId = billingInfoRecord.TaxExemptionId__c;
        billingInfo.taxRegistrationId = billingInfoRecord.TaxRegistrationId__c;
        billingInfo.noTaxRegistrationIdReason = billingInfoRecord.NoTaxRegistrationIdReason__c;
        billingInfo.billingCompanyName = billingInfoRecord.BillingCompanyName__c;
        return billingInfo;
    }

    public static IResponse getExceptionResponse(Exception ex, IRequest request) {
        String errorMessage = 'Exception during Billing Info Service call :: ' + ex.getMessage();
        IResponse response = new BaseResponse();
        response.setErrorMessage(errorMessage);
        return response;
    }

    private static void validateNotNull(Object fieldToValidate, String error, BillingInfoServiceResponseItem responseItem) {
        if(fieldToValidate == null) {
           responseItem.addResponseMessage(error);
           responseItem.setSuccess(false);
        }
    }

    private static void validateNull(Object fieldToValidate, String error, BillingInfoServiceResponseItem responseItem) {
        if(fieldToValidate != null) {
           responseItem.addResponseMessage(error);
           responseItem.setSuccess(false);
        }
    }

    private static void validateDuplicateName(
        String name,
        Id accountId,
        String error, 
        BillingInfoServiceResponseItem responseItem
    ) {
        if(billingInfoSelector.getBillingInfoByName(accountId, name).size() > 0) {
            responseItem.addResponseMessage(error);
            responseItem.setSuccess(false);
        }
    }

    private static void validateDuplicateBillingInfo(
        BillingInformation billingInfo, 
        String error, 
        BillingInfoServiceResponseItem responseItem
    ) {
        List<BillingInformation__c> resp = billingInfoSelector.getBillingInfoDuplicate(billingInfo);
        if(resp.size() > 0) {
            responseItem.billingInformationId = resp.get(0).Id;
            responseItem.addResponseMessage(error + ' Name:' + resp.get(0).Name);
            responseItem.setSuccess(false);
        }
    }

    private static void copyTaxInfo(BillingInformation__c billingInfoRecord, BillingInformation billingInfo) {
        if(billingInfo.businessType != null) {
            billingInfoRecord.BusinessType__c = billingInfo.businessType;
        }
        if(billingInfo.taxExemptStatus != null) {
            billingInfoRecord.TaxExemptStatus__c = billingInfo.taxExemptStatus;
        }
        if(billingInfo.taxExemptionId != null) {
            billingInfoRecord.TaxExemptionId__c = billingInfo.taxExemptionId;
        }
        if(billingInfo.taxRegistrationId != null) {
            billingInfoRecord.TaxRegistrationId__c = billingInfo.taxRegistrationId;
        }
        if(billingInfo.noTaxRegistrationIdReason != null) {
            billingInfoRecord.NoTaxRegistrationIdReason__c = billingInfo.noTaxRegistrationIdReason;
        }
    }

    private static void copyBillingInfo(BillingInformation__c billingInfoRecord, BillingInformation billingInfo) {
        if(billingInfo.billingInformationId != null) {
            billingInfoRecord.Id = billingInfo.billingInformationId;
        }
        if(billingInfo.name != null) {
            billingInfoRecord.Name = billingInfo.name;
        }
        if(billingInfo.accountId != null) {
            billingInfoRecord.Account__c = billingInfo.accountId;
        }
        if(billingInfo.primaryContact != null) {
            billingInfoRecord.PrimaryBillingContact__c = billingInfo.primaryContact;
        }
        if(billingInfo.secondaryContact != null) {
            billingInfoRecord.SecondaryBillingContact__c = billingInfo.secondaryContact;
        }
        if(billingInfo.autoRenewPreference != null) {
            billingInfoRecord.AutoRenewal__c = billingInfo.autoRenewPreference;
        }
        if(billingInfo.frequency != null) {
            billingInfoRecord.BillingFrequency__c = billingInfo.frequency;
        }
        if(billingInfo.language != null) {
            billingInfoRecord.BillingLanguage__c = billingInfo.language;
        }
        if(billingInfo.country != null) {
            billingInfoRecord.BillingCountry__c = billingInfo.country;
        }
        if(billingInfo.billingCurrency != null) {
            billingInfoRecord.CurrencyIsoCode = billingInfo.billingCurrency;
        }
        if(billingInfo.invoiceDispatchMethod != null) {
            billingInfoRecord.InvoiceDispatchMethod__c = billingInfo.invoiceDispatchMethod;
        }
        copyBillingInfoDetails(billingInfoRecord, billingInfo);
       
    }
    
    private static void copyBillingInfoDetails(BillingInformation__c billingInfoRecord, BillingInformation billingInfo) {
       
        if(billingInfo.paymentMethod != null) {
            billingInfoRecord.PaymentMethod__c = billingInfo.paymentMethod;
        }
        if(billingInfo.paymentTerm != null) {
            billingInfoRecord.PaymentTerm__c = billingInfo.paymentTerm;
        }
        if(billingInfo.preBillDays != null) {
            billingInfoRecord.PreBillDays__c = billingInfo.preBillDays;
        }
        if(billingInfo.renewalTerm != null) {
            billingInfoRecord.RenewalTerm__c = billingInfo.renewalTerm;
        }
        if(billingInfo.billingCompanyName != null) {
            billingInfoRecord.BillingCompanyName__c = billingInfo.billingCompanyName;
        }
    }
}