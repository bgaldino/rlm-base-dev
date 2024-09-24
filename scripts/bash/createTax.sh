#!/bin/bash
# shellcheck shell=bash
function create_tax_engine() {
  local provider_name="$1"
  #local taxProviderClassName
  #local namedCredentialDeveloperName
  #local namedCredentialMasterLabel
  case $provider_name in
  "avalara")
    taxProviderClassName="$TAX_PROVIDER_AVALARA_CLASS_NAME"
    namedCredentialDeveloperName="$TAX_AVALARA_NAMED_CREDENTIAL_DEVELOPER_NAME"
    namedCredentialMasterLabel="$TAX_AVALARA_NAMED_CREDENTIAL_MASTER_LABEL"
    echo_color green "Using Avalara Tax Engine"
    ;;
  "mock")
    taxProviderClassName="$TAX_PROVIDER_MOCK_CLASS_NAME"
    namedCredentialDeveloperName="$TAX_MOCK_NAMED_CREDENTIAL_DEVELOPER_NAME"
    namedCredentialMasterLabel="$TAX_MOCK_NAMED_CREDENTIAL_MASTER_LABEL"
    echo_color green "Using Mock Tax Engine"
    echo_keypair taxProviderClassName "$taxProviderClassName"
    echo_keypair namedCredentialDeveloperName "$namedCredentialDeveloperName"
    echo_keypair namedCredentialMasterLabel "$namedCredentialMasterLabel"
    ;;
  *)
    taxProviderClassName="$TAX_PROVIDER_MOCK_CLASS_NAME"
    namedCredentialDeveloperName="$TAX_MOCK_NAMED_CREDENTIAL_DEVELOPER_NAME"
    namedCredentialMasterLabel="$TAX_MOCK_NAMED_CREDENTIAL_MASTER_LABEL"
    echo_color red "Tax Engine Provider $provider_name not found or none passed to create_tax_engine(). Using Mock Tax Engine"
    ;;
  esac
  echo_color green "Getting Id for ApexClass $taxProviderClassName"
  taxProviderClassId=$(get_record_id ApexClass Name "$taxProviderClassName")
  echo_keypair taxProviderClassId "$taxProviderClassId"
  echo_color green "Checking for existing TaxEngineProvider $taxProviderClassName"
  taxEngineProviderId=$(get_record_id TaxEngineProvider DeveloperName "$taxProviderClassName")
  if [ -z "$taxEngineProviderId" ]; then
    echo_color green "Creating TaxEngineProvider $taxProviderClassName"
    $sfdx data create record -s TaxEngineProvider -v "DeveloperName='$taxProviderClassName' MasterLabel='$taxProviderClassName' ApexAdapterId=$taxProviderClassId"
    echo_color green "Getting Id for TaxEngineProvider $taxProviderClassName"
    taxEngineProviderId=$(get_record_id TaxEngineProvider DeveloperName "$taxProviderClassName")
  fi
  echo_keypair taxEngineProviderId "$taxEngineProviderId"

  echo_color green "Getting Id for NamedCredential $namedCredentialMasterLabel"
  taxMerchantCredentialId=$(get_record_id NamedCredential DeveloperName "$namedCredentialDeveloperName")
  echo_keypair taxMerchantCredentialId "$taxMerchantCredentialId"
  echo_color green "Checking for existing TaxEngine $taxProviderClassName"
  taxEngineId=$(get_record_id TaxEngine TaxEngineName "$taxProviderClassName")
  if [ -z "$taxEngineId" ]; then
    echo_color green "Creating TaxEngine $taxProviderClassName"
    $sfdx data create record -s TaxEngine -v "TaxEngineName='$taxProviderClassName' MerchantCredentialId=$taxMerchantCredentialId TaxEngineProviderId=$taxEngineProviderId Status='Active' SellerCode='Billing2' TaxEngineCity='San Francisco' TaxEngineCountry='United States' TaxEnginePostalCode='94105' TaxEngineState='California'"
    echo_color green "Getting Id for TaxEngine $taxProviderClassName"
    taxEngineId=$(get_record_id TaxEngine TaxEngineName "$taxProviderClassName")
  fi
  echo_color green "$taxProviderClassName Tax Engine Id:"
  echo_keypair taxEngineId "$taxEngineId"
}