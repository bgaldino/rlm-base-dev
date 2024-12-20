public with sharing class ContractRecord extends AbstractRecord {

    public Id ownerId                    {get; set;}
    public Id accountId                  {get; set;}
    public Id billingContactId           {get; set;}
    public Id billingInformationId       {get; set;}
    public Date startDate                {get; set;}
    public String status                 {get; set;}
    public String currencyIsoCode        {get; set;}
    public String referenceContractIds   {get; set;}
    public String contractCreationSource {get; set;}
    public Integer contractTerm          {get; set;}
}