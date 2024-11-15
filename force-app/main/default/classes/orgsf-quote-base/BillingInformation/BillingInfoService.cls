public with sharing class BillingInfoService extends AbstractBillingInfoService {

    private IBillingInformationDAO billingInfoDAO;
    private IBillingInformationSelector billingInfoSelector;

    public BillingInfoService() {
        this(
            (IBillingInformationDAO)ServiceRegistry.getInstance('IBillingInformationDAO'),
            (IBillingInformationSelector)ServiceRegistry.getInstance('IBillingInformationSelector')
        );
    }

    public BillingInfoService(
        IBillingInformationDAO billingInfoDAO, 
        IBillingInformationSelector billingInfoSelector
    ) {
        this.billingInfoDAO = billingInfoDAO;
        this.billingInfoSelector = billingInfoSelector;
    }

    public override IResponse createBillingInformation(IRequest request) {
        try {
            IResponse response = BillingInfoServiceHelper.validateRequest(request);
            if(response.getErrorMessage() != null){
                return response;
            }
            return processRequest(request, DMLOperation.OP_INSERT);
        } catch(Exception ex) {
            return BillingInfoServiceHelper.getExceptionResponse(ex, request);
        }
    }

    public override IResponse updateBillingInformation(IRequest request) {
        try {
            IResponse response = BillingInfoServiceHelper.validateRequest(request);
            if(response.getErrorMessage() != null){
                return response;
            }
            return processRequest(request, DMLOperation.OP_UPDATE);
        } catch(Exception ex) {
            return BillingInfoServiceHelper.getExceptionResponse(ex, request);
        }
    }

    public override List<BillingInformation> getBillingInformation(Id accountId, String country, String billingCurrency) {
        List<BillingInformation__c> billingInfoRecordList = billingInfoSelector.getBillingInfo(accountId, country, billingCurrency);
        List<BillingInformation> billingInfoList = new List<BillingInformation>();
        for(BillingInformation__c billingInfoRecord : billingInfoRecordList) {
            billingInfoList.add(BillingInfoServiceHelper.createBillingInfoPOJOFromRecord(billingInfoRecord));
        }
        return billingInfoList;
    }

    private IResponse processRequest(IRequest request, DMLOperation op) {
        IResponse response = new BaseResponse(request);
        List<BillingInformation__c> billingInfoToProcess = new List<BillingInformation__c>();
        List<String> requestItemIdsToProcess = new List<String>();

        for(IRequestItem iRequestItem : request.getRequestItems()) {
            BillingInfoServiceRequestItem  requestItem = (BillingInfoServiceRequestItem)iRequestItem;
            BillingInfoServiceResponseItem responseItem;
            if(op.equals(DMLOperation.OP_INSERT)) {
                responseItem = BillingInfoServiceHelper.validateCreateRequestItem(requestItem);
            }
            if(op.equals(DMLOperation.OP_UPDATE)) {
                responseItem = BillingInfoServiceHelper.validateUpdateRequestItem(requestItem);
            }
            if(responseItem.isSuccess() == false) {
                response.addResponseItem(responseItem);
                continue;
            }
            billingInfoToProcess.add(BillingInfoServiceHelper.createBillingInformationFromPOJO(requestItem.billingInfo));
            requestItemIdsToProcess.add(requestItem.getRequestItemId());
        }
        List<Database.SaveResult> saveResultList = performBillingInfoDML(billingInfoToProcess, op);
        
        Integer index = 0;
        for(String requestItemId : requestItemIdsToProcess) {
            BillingInfoServiceResponseItem responseItem = new BillingInfoServiceResponseItem(requestItemId);
            Id billingInfoId = saveResultList.get(index).getId();
            if(billingInfoId == null) {
                responseItem.addResponseMessage(BillingInfoServiceErrorCodes.DML_OPERATION_FAILED.name());
                responseItem.setSuccess(false);
            } else {
                responseItem.billingInformationId = billingInfoId;
                responseItem.setSuccess(true);
            }
            response.addResponseItem(responseItem);
            index++;
        }
        return response;
    }

    private List<Database.SaveResult> performBillingInfoDML(List<BillingInformation__c> billingInfoList, DMLOperation op) {
        List<Database.SaveResult> saveResultList;
        if(op.equals(DMLOperation.OP_INSERT)) {
            SObjectAccessDecision securityDecision = Security.stripInaccessible(AccessType.CREATABLE, billingInfoList);
            if(!securityDecision.getRecords().isEmpty()) {
                saveResultList = billingInfoDAO.insertBillingInfo(securityDecision.getRecords());
            }
        }
        if(op.equals(DMLOperation.OP_UPDATE)) {
            SObjectAccessDecision securityDecision = Security.stripInaccessible(AccessType.UPDATABLE, billingInfoList);
            if(!securityDecision.getRecords().isEmpty()) {
                saveResultList = billingInfoDAO.updateBillingInfo(securityDecision.getRecords());
            }
        }
        return saveResultList;
    }
}