/**
 * setOrgCompanyInfo.apex
 *
 * Populates the Organization record's company information fields on fresh scratch orgs.
 * Scratch orgs are created with a blank Organization (Name = scratch org alias, all
 * address/phone/fax fields null). The RLM_Seller_*__c formula fields on Quote fall back
 * to $Organization.* for internal users, so blank org info produces blank seller tokens
 * in generated documents.
 *
 * TODO: Replace the placeholder values below with your company's actual information,
 * or drive the values from org-specific custom settings / environment variables so the
 * same script works across different partner scratch org pools.
 *
 * Run via: cci task run anon_apex -o path scripts/apex/setOrgCompanyInfo.apex --org <org>
 * (A dedicated set_org_company_info CCI task is planned — see cumulusci.yml TODO before insert_scratch_data.)
 */

// TODO: Populate with real company values before enabling this script in prepare_scratch.
Organization org = [SELECT Id FROM Organization LIMIT 1];
// org.Name            = 'Your Company Name';
// org.Phone           = '+1 (555) 000-0000';
// org.Fax             = '+1 (555) 000-0001';
// org.Street          = '123 Main St';
// org.City            = 'San Francisco';
// org.State           = 'CA';
// org.PostalCode      = '94105';
// org.Country         = 'US';
// update org;
System.debug('setOrgCompanyInfo: TODO — uncomment the field assignments above and provide real values.');
