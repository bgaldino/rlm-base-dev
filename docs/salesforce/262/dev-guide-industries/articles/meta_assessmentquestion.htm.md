---
page_id: meta_assessmentquestion.htm
title: AssessmentQuestion
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/meta_assessmentquestion.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Discovery Framework
parent_page: discovery_framework_metadata_api_parent.htm
fetched_at: 2026-06-25
---

# AssessmentQuestion

Represents the container object that stores the questions
required for an assessment.

## Parent Type

This type extends the Metadata metadata type and inherits its
fullName field.

## File Suffix and Directory Location

AssessmentQuestion components have the suffix
.AssessmentQuestion and are stored in the
AssessmentQuestions folder.

## Version

AssessmentQuestion components are available in API version 55.0 and later.

## Fields

| Field Name | Description |
| --- | --- |
| assessmentQuestionVersion | Field Type  [AssessmentQuestionVersion](#AssesQVer)  Description  The object that stores the question versions for the assessment questions. |
| dataType | Field Type  string  Description  Required.  The data type of the assessment question. |
| developerName | Field Type  string  Description  Required.  The developer name of the assessment question. Can contain only underscores and alphanumeric characters and must be unique in your org. It must begin with a letter, not include spaces, not end with an underscore, and not contain two consecutive underscores. |
| displayTextCategory | Field Type  string  Description  Specifies the category of the display text when the data type is Text Block. |
| formulaResponseDataType | Field Type  string  Description  Specifies the data type of the question response calculated by a formula. |
| name | Field Type  string  Description  Required.  The name of the record. |
| questionCategory | Field Type  string  Description  Required.  Stores the question category. |
| relatedQuestion | Field Type  string  Description  Specifies the related question. Used to define a question hierarchy. |

## AssessmentQuestionVersion​​

Stores the question versions for the assessment questions.

| Field Name | Description |
| --- | --- |
| additionalInformation | Field Type  string  Description  The additional details for a UI element, such as the disclosure text. |
| description | Field Type  string  Description  The description for the assessment question. This text isn’t rendered on the assessment. |
| guidanceInformation | Field Type  string  Description  The guidance for the assessment question. |
| helpText | Field Type  string  Description  The text that's added as an info bubble in the UI element related to the assessment question. |
| isActive | Field Type  boolean  Description  Required.  Indicates whether the current version of the assessment question is set to active (`true`) or not (`false`).  The default value is `false`. |
| name | Field Type  string  Description  Required.  Name of the assessment question version record. |
| optionSourceResponseValue | Field Type  boolean  Description  Indicates whether the response value source for an assessment question is configured as custom (`true`) or sObject in the OmniStudio designer (`false`).  The default value is `false`. |
| questionText | Field Type  string  Description  Required.  The assessment question text. Contains the label for the assessment question that appears on the assessment. |
| responseValues | Field Type  string  Description  Holds the values to be defined in the picklist, multiselect picklist, or radio buttons. |
| status | Field Type  string  Description  Required.  Status of the assessment question version. Possible values are Draft, Active, or Archived. |
| versionNumber | Field Type  int  Description  Required.  The assessment question version number. |

## Declarative Metadata Sample Definition

The following is an example of an AssessmentQuestion component.

```
<?xml version="1.0" encoding="UTF-8"?>
<AssessmentQuestion
	xmlns="http://soap.sforce.com/2006/04/metadata">
	<assessmentQuestionVersion>
		<additionalInformation>ParentQuestionDevName AI</additionalInformation>
		<description>ParentQuestionDevName Desc</description>
		<helpText>ParentQuestionDevName HT</helpText>
		<isActive>true</isActive>
		<name>ParentQuestionDevName</name>
		<optionSourceResponseValue>true</optionSourceResponseValue>
		<questionText>ParentQuestionDevName Text</questionText>
		<status>Active</status>
		<versionNumber>1</versionNumber>
	</assessmentQuestionVersion>
	<dataType>DateTime</dataType>
	<developerName>ParentQuestionDevName</developerName>
	<name>ParentQuestionDevName</name>
	<questionCategory>Demographic</questionCategory>
</AssessmentQuestion>
```

The following is an example `package.xml` that
references the previous definition.

```
<?xml version="1.0" encoding="UTF-8"?>
<Package
	xmlns="http://soap.sforce.com/2006/04/metadata">
	<types>
		<members>*</members>
		<name>AssessmentQuestion</name>
	</types>
	<version>55.0</version>
</Package>
```

## Wildcard Support in the Manifest File

This metadata type supports the wildcard character `*` (asterisk) in the package.xml manifest
file. For information about using the manifest file, see Deploying and Retrieving Metadata with the Zip File.

## Usage

Before you retrieve assessment questions, we recommend that you review these considerations.

- When you retrieve an assessment question, you also get the related
  assessment question version with the status Active..

  ![Note](/docs/resources/img/en-us/262.0?doc_id=images%2Ficon_note.png&folder=industries_reference)

  #### Note

  If an active
  assessment question version doesn’t exist for the assessment question,
  then the latest assessment question version with Status as Draft is
  retrieved.
- The value for the `<status>` tag in
  the XML definition must match the status of the related assessment question
  version.
- If an assessment question has a related assessment question (parent
  question), the XML definition must include the developer name of the related
  assessment question.
- If the fields of an assessment question contain values, the XML definition
  must contain tags with those values when retrieving it.

Before you deploy assessment questions, we recommend that you review these considerations.

- If the Related Question isn’t available in the target org, deploying the
  assessment question fails.
- If an assessment question with the same developer name exists in the target
  org, deploying the assessment question updates the values of the other
  fields in the target org.
- If the `<versionNumber>` tag is
  present in the XML definition of an assessment question, deploying creates a
  version for that question in the target org.
- If the Related Questions aren’t available in target org but available in the
  package, then deploying the questions inserts the Related Questions in the
  correct order.
- If the assessment questions are associated with flows of type Discovery
  Framework Data Capture Flow, then deploy the assessment questions first.
  After deploying the assessment questions, deploy the flows.
