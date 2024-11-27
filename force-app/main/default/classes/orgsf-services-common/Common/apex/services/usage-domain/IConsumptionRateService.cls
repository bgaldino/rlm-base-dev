public interface IConsumptionRateService {
    ConsumptionRateServiceRequest prepareConsumptionRateServiceRequest(Id businessObjectId);
    ConsumptionRateServiceResponse generateConsumptionRate(ConsumptionRateServiceRequest request);
    Boolean isTrueUpScheduleForAmendContract(Id businessObjectId);
}
