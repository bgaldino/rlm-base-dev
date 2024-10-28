public class UsageTypeValidationError {
    public UsageTypeValidationError(Id tenantInformationId, UsageTypeValidationErrorCode errorCode, String usageTypeName) {
        this.tenantInformationId = tenantInformationId;
        this.errorCode = errorCode;
        this.usageTypeName = usageTypeName;
    }

    public Id tenantInformationId;
    public UsageTypeValidationErrorCode errorCode;
    public String usageTypeName;
}