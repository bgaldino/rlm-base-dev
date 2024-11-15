public abstract class AbstractConsumptionRateService implements IConsumptionRateService {

    public abstract ConsumptionRateServiceRequest prepareConsumptionRateServiceRequest(Id businessObjectId);
    public abstract ConsumptionRateServiceResponse generateConsumptionRate(ConsumptionRateServiceRequest request);
    public abstract Boolean isTrueUpScheduleForAmendContract(Id businessObjectId);
}
