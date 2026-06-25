---
page_id: meta_assessmentquestionset.htm
title: AssessmentQuestionSet
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/meta_assessmentquestionset.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Discovery Framework
parent_page: discovery_framework_metadata_api_parent.htm
fetched_at: 2026-06-25
---

# AssessmentQuestionSet

Represents the container object for Assessment
Questions.

## Parent Type

This type extends the Metadata metadata type and inherits its
fullName field.

## File Suffix and Directory Location

AssessmentQuestionSet components have the suffix
.AssessmentQuestionSet and are stored in the
AssessmentQuestionSets folder.

## Version

AssessmentQuestionSet components are available in API version 55.0 and later.

## Fields

| Field Name | Description |
| --- | --- |
| assessmentQuestionDeveloperNames | Field Type  string[]  Description  The developer names for the assessment question. Can contain only underscores and alphanumeric characters and must be unique in your org. It must begin with a letter, not include spaces, not end with an underscore, and not contain two consecutive underscores. |
| developerName | Field Type  string  Description  Required.  The developer name for the assessment question set. Can contain only underscores and alphanumeric characters and must be unique in your org. It must begin with a letter, not include spaces, not end with an underscore, and not contain two consecutive underscores. |
| name | Field Type  string  Description  Required.  The question set name. |

## Declarative Metadata Sample Definition

The following is an example of an AssessmentQuestionSet component.

```
<?xml version="1.0" encoding="UTF-8"?>
<AssessmentQuestionSet
	xmlns="http://soap.sforce.com/2006/04/metadata">
	<developerName>QuestionSetDevName</developerName>
	<name>QuestionSetName</name>
	<assessmentQuestionDeveloperNames>QuestionDevName</assessmentQuestionDeveloperNames>
</AssessmentQuestionSet>
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
	<types>
		<members>*</members>
		<name>AssessmentQuestionSet</name>
	</types>
	<version>55.0</version>
</Package>
```

## Wildcard Support in the Manifest File

This metadata type supports the wildcard character `*` (asterisk) in the package.xml manifest
file. For information about using the manifest file, see Deploying and Retrieving Metadata with the Zip File.

## Usage

Before you retrieve assessment question sets, we recommend that you review these considerations.

- When retrieving an assessment question set, if its fields contain values,
  then the XML definition must contain tags with those values.
- When retrieving an assessment question set, if that set is associated with
  multiple questions, then the XML definition must contain developer names of
  all the associated questions.

Before you deploy assessment question sets, we recommend that you review these considerations.

- When deploying an assessment question set, if an assessment question set
  with the same developer name doesn't exist in the target org, deploying
  creates one with that name.
- If an assessment question set with the same developer name exists in the
  target org, then deploying the question set updates the values of the other
  fields in the target org.
- If the questions associated with the assessment question set don't exist in
  the target org, deploying the assessment question set fails.
- If the questions associated with the assessment question set don’t exist in
  the target org but are available in the package, then deploying the
  assessment question sets inserts the questions in the correct order.
