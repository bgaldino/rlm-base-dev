---
page_id: tooling_api_objects_batchjobdefinition.htm
title: BatchJobDefinition
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/tooling_api_objects_batchjobdefinition.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Data Processing Engine, Batch Management, and Monitor Workflow Services
parent_page: batch_common_setup_objects.htm
fetched_at: 2026-06-25
---

# BatchJobDefinition

Represents the definition of a batch job. This object is available in API
version 51.0 and later.

![Note](/docs/resources/img/en-us/262.0?doc_id=images%2Ficon_note.png&folder=industries_reference)

#### Note

Where possible, we changed noninclusive terms to align with our company value of
Equality. We maintained certain terms to avoid any effect on customer
implementations.

## Supported SOAP API Calls

`describeSObjects()`, `query()`, `retrieve()`

## Supported REST API Methods

`GET, HEAD, Query`

## Fields

| Field | Details |
| --- | --- |
| Description | Type  textarea  Properties  Filter, Group, Nillable, Sort  Description  The description of the batch job definition. |
| DeveloperName | Type  string  Properties  Filter, Group, Sort  Description  The developer name of the batch job. |
| Language | Type  picklist  Properties  Filter, Group, Restricted picklist, Sort  Description  The language in which the batch job is created.  Possible values are:  - `af`—Afrikaans - `am`—Amharic - `ar`—Arabic - `ar_AE`—Arabic (United Arab   Emirates) - `ar_BH`—Arabic (Bahrain) - `ar_DZ`—Arabic (Algeria) - `ar_EG`—Arabic (Egypt) - `ar_IQ`—Arabic (Iraq) - `ar_JO`—Arabic (Jordan) - `ar_KW`—Arabic (Kuwait) - `ar_LB`—Arabic (Lebanon) - `ar_LY`—Arabic (Libya) - `ar_MA`—Arabic (Morocco) - `ar_OM`—Arabic (Oman) - `ar_QA`—Arabic (Qatar) - `ar_SA`—Arabic (Saudi   Arabia) - `ar_SD`—Arabic (Sudan) - `ar_SY`—Arabic (Syria) - `ar_TN`—Arabic (Tunisia) - `ar_YE`—Arabic (Yemen) - `bg`—Bulgarian - `bn`—Bengali - `bs`—Bosnian - `ca`—Catalan - `cs`—Czech - `cy`—Welsh - `da`—Danish - `de`—German - `de_AT`—German (Austria) - `de_BE`—German (Belgium) - `de_CH`—German   (Switzerland) - `de_LU`—German   (Luxembourg) - `el`—Greek - `en_AU`—English   (Australian) - `en_CA`—English   (Canadian) - `en_GB`—English (UK) - `en_HK`—English (Hong   Kong) - `en_IE`—English (Ireland) - `en_IN`—English (Indian) - `en_MY`—English   (Malaysian) - `en_NZ`—English (New   Zealand) - `en_PH`—English   (Phillipines) - `en_SG`—English   (Singapore) - `en_US`—English - `en_ZA`—English (South   Africa) - `eo`—Esperanto (Pseudo) - `es`—Spanish - `es_AR`—Spanish   (Argentina) - `es_BO`—Spanish (Bolivia) - `es_CL`—Spanish (Chile) - `es_CO`—Spanish   (Colombia) - `es_CR`—Spanish (Costa   Rica) - `es_DO`—Spanish (Dominican   Republic) - `es_EC`—Spanish (Ecuador) - `es_GT`—Spanish   (Guatemala) - `es_HN`—Spanish   (Honduras) - `es_MX`—Spanish (Mexico) - `es_NI`—Spanish   (Nicaragua) - `es_PA`—Spanish (Panama) - `es_PE`—Spanish (Peru) - `es_PR`—Spanish (Puerto   Rico) - `es_PY`—Spanish   (Paraguay) - `es_SV`—Spanish (El   Salvador) - `es_US`—Spanish (United   States) - `es_UY`—Spanish (Uruguay) - `es_VE`—Spanish   (Venezuela) - `et`—Estonian - `eu`—Basque - `fa`—Farsi - `fi`—Finnish - `fr`—French - `fr_BE`—French (Belgium) - `fr_CA`—French (Canadian) - `fr_CH`—French   (Switzerland) - `fr_LU`—French   (Luxembourg) - `ga`—Irish - `gu`—Gujarati - `hi`—Hindi - `hr`—Croatian - `hu`—Hungarian - `hy`—Armenian - `in`—Indonesian - `is`—Icelandic - `it`—Italian - `it_CH`—Italian   (Switzerland) - `iw`—Hebrew - `iw_EO`—Esperanto RTL   (Pseudo) - `ja`—Japanese - `ka`—Georgian - `km`—Khmer - `kn`—Kannada - `ko`—Korean - `lb`—Luxembourgish - `lt`—Lithuanian - `lv`—Latvian - `mi`—Te reo - `mk`—Macedonian - `ml`—Malayalam - `mr`—Marathi - `ms`—Malay - `mt`—Maltese - `my`—Burmese - `nl_BE`—Dutch (Belgium) - `nl_NL`—Dutch - `no`—Norwegian - `pl`—Polish - `pt_BR`—Portuguese   (Brazil) - `pt_PT`—Portuguese   (European) - `rm`—Romansh - `ro`—Romanian - `ro_MD`—Romanian   (Moldova) - `ru`—Russian - `sh`—Serbian (Latin) - `sh_ME`—Montenegrin - `sk`—Slovak - `sl`—Slovene - `sq`—Albanian - `sr`—Serbian (Cyrillic) - `sv`—Swedish - `sw`—Swahili - `ta`—Tamil - `te`—Telugu - `th`—Thai - `tl`—Tagalog - `tr`—Turkish - `uk`—Ukrainian - `ur`—Urdu - `vi`—Vietnamese - `xh`—Xhosa - `zh_CN`—Chinese   (Simplified) - `zh_HK`—Chinese (Hong   Kong) - `zh_SG`—Chinese   (Singapore) - `zh_TW`—Chinese   (Traditional) - `zu`—Zulu |
| MasterLabel | Type  string  Properties  Filter, Group, Sort  Description  The label of the batch job. |
| ProcessGroup | Type  string  Properties  Filter, Group, Sort  Description  The group or team that's using the batch job. This field is only applicable to Batch Management jobs. |
| Status | Type  picklist  Properties  Defaulted on create, Filter, Group, Restricted picklist, Sort  Description  The status of the batch job.  Possible values are:  - `Active` - `Inactive` |
| Type | Type  picklist  Properties  Defaulted on create, Filter, Group, Restricted picklist, Sort  Description  Specifies the type of batch job.  Possible values are:  - `BulkUpdate` - `Calc`—Data Processing   Engine - `ConsumptionOveragesCalculation` - `DecisionTableRefresh` - `DeepCloneSalesAgreement` - `FlattenAccountIOUHierarchyBatchJob` - `Flow` - `EnergyUseRecordCreationBatchJob` - `EntitlementCreationBatchJob` - `HighScaleBreProcess` - `IndustriesLSCommercial` - `InvoiceDTPRunBatchJob` - `InvoiceRecoveryRunBatchJob` - `InvoiceRunBatchJob` - `LifeSciProviderActivityGoalSharingBatchJob` - `LoyaltyProgramProcess` - `NetUnitRateCalculation` - `NextGenCommitmentBatchProcessingJob` - `ManagerProvisioning` - `PbbToOptyConversion` - `ProductCatalogCacheRefresh` - `PromotionChannelPropagationBatchJob` - `RatableSummaryCreation` - `ServiceProcess` - `StoreAssortmentPropagationBatchJob` - `SummaryCreation` - `WorkDotComToHRManagerProvisioning`   When Data Processing Engine or Batch Management is available in a Salesforce org, the default values are Calc or Flow respectively. Other types may be available to you depending on the licenses available in your org. |
