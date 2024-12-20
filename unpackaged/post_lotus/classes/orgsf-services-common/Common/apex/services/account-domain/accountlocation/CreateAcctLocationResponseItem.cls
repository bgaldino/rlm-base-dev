public with sharing class CreateAcctLocationResponseItem extends BaseResponseItem {

    public Id addressId { get; set; }
    public Id locationId { get; set; }
    public Id associatedLocationId { get; set; }

    public CreateAcctLocationResponseItem(String requestId) {
        super(requestId);
    }
}