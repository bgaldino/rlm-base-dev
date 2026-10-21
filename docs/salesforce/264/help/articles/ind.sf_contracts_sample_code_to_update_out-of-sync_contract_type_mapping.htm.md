---
article_id: ind.sf_contracts_sample_code_to_update_out-of-sync_contract_type_mapping.htm
title: Sample Code To Update Out-of-Sync Contract Type Mapping
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_sample_code_to_update_out-of-sync_contract_type_mapping.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_contract_type_config_settings.htm
fetched_at: 2026-10-13
---

# Sample Code To Update Out-of-Sync Contract Type Mapping

If you delete, add or modify a record type mapping with a contact type, the changes will only apply to the new contracts. To update the out-of-sync contracts, the system admin can run a custom code.

System admin can use this sample code to modify the contract mapping for existing contracts. Open Developer Console, go to DebugOpen Execute Anonymous Window, paste the sample code and click Execute. For more information on using Apex Class, see the Apex Developer Guide.

Use case: Contract type Health corresponds to record types Inpatient Care and Outpatient Care. There are 1000 contract records that have this mapping. You change the mapping for record type Inpatient Care to contract type Revenue and out of the existing 1000 records, there are 500 Inpatient Care record types pointing to Contract Type Health. The contract rows will continue to show the contract type as Health and the record type as Inpatient Care because the Salesforce Contracts application doesn't automatically update the contract records that have record type Inpatient Care with contract type Revenue. Only the system administrator can apply the changes using a sample code. However, when a new contract is created with a record type Inpatient Care, then the contract type will be Revenue.

NOTE The Contract Type field on the contract object by default is read-only for all the non-admin profiles. At a profile level, based on field-level security, users can update the out-of-sync contract type on the contract object manually or using an apex code.

The sample code pulls a list of Contract Types. You can pass any number of Contract Types and adjust the mapping. You can edit the query to make changes and pull contracts with specific statuses such as Draft, Contract Expired, Canceled, etc.

public class SyncContractTypes {
   
	// use-case1 : sync contracts when existing RecordType that's associated with contracts is newly mapped to a existing ContractType
	// use-case2 : sync contracts when existing RecordType that's associated with contracts is removed from ContractType object - ContractType, SubType mapping
	// use-case3 : sync contracts when existing RecordType that's associated with contracts is removed from ContractType object - ContractType, SubType mapping  and mapped to existing ContractType, SubType
   
	public static void syncOutOfSyncContractTypes(List<String> contractTypes) {
       
    	Map<String,String> contractTypeSubtypeMap = new Map<String,String>();
    	Map<String,String> subtypeContractTypeMap = new Map<String,String>();
       
    	if(contractTypes != null && !contractTypes.isEmpty()) {
       	// Here we are querying all the contractTypes to support a use-case2
       	// where a SubType is removed from a contractType and mapped to another existing contractType
       	// If customers don't want to update when existing subType is mapped to another existing contractType they can
       	// restrict this by adding a where condition, WHERE MasterLabel IN :contractTypes
        	List<ContractType> contractTypeList = [SELECT MasterLabel,SubTypes FROM ContractType];
           
        	if(contractTypeList!= null && !contractTypeList.isEmpty()) {
            	for( ContractType c : contractTypeList) {
                	contractTypeSubtypeMap.put(c.MasterLabel, c.SubTypes);
                	if(c.subTypes != null) {
                    	for(String s : c.subTypes.split(',')) {
                        	subtypeContractTypeMap.put(s, c.MasterLabel);
                    	}
                	}
            	}
        	}
           
        	for(String ct : contractTypes) {
           
            	String contractType = (contractTypeSubtypeMap.containsKey(ct)) ? ct : '';
               
            	List<String> subTypesList = (contractTypeSubtypeMap.get(ct) != null) ? contractTypeSubtypeMap.get(ct).split(',') : new List<String>();
               
            	// we are applying basic filters here, please modify them accordingly to your use case
            	List<Contract> contracts = [
                	SELECT Id, ContractType, Name, RecordType.Name
                	FROM Contract
                	WHERE (ContractType =: contractType OR RecordType.Name IN :subTypesList)
                        	AND IsAssociatedWithCLM = true
                        	AND (NOT (ContractType =: contractType AND RecordType.Name IN : subTypesList))];
               
            	List<Contract> contractsToUpdate = new List<Contract>();
            	// check if any of the contracts are out of sync and update them
            	for(Contract c : contracts) {
                	String RecordTypeName = c.RecordType.Name;
                	if(subTypesList.contains(RecordTypeName) && c.ContractType != contractType) {
                    	c.ContractType = contractType;
                    	contractsToUpdate.add(c);
                	} else if(!subTypesList.contains(RecordTypeName) ){
                    	// check to see if any other ContractTypes has this RecordType as SubType
                    	c.ContractType = (subtypeContractTypeMap.get(RecordTypeName) != null) ? subtypeContractTypeMap.get(RecordTypeName) : '';
                    	contractsToUpdate.add(c);
                	}
                   
            	}           
            	if(contractsToUpdate != null && !contractsToUpdate.isEmpty()) {
                   
                	Database.SaveResult[] saveResult = Database.Update(contractsToUpdate, false);
                	for (Database.SaveResult sr : saveResult) {
                    	if (sr.isSuccess()) {
                        	// Operation was successful, so get the ID of the record that was processed
                        	System.debug('Successfully updated contract. Contract ID: ' + sr.getId());
                    	}
               	     else {
                        	// Operation failed, so get all errors               
                        	for(Database.Error err : sr.getErrors()) {
                            	System.debug('The following error has occurred.');    	            
                            	System.debug(err.getStatusCode() + ': ' + err.getMessage());
                            	System.debug('Contract fields that affected this error: ' + err.getFields());
                        	}
                   	}
                	}
            	}
        	}
  	}
	}
}
