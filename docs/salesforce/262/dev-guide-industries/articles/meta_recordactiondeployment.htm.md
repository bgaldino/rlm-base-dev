---
page_id: meta_recordactiondeployment.htm
title: RecordActionDeployment
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/meta_recordactiondeployment.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Action Launcher
parent_page: action_launcher_metadata_apis_parent.htm
fetched_at: 2026-06-25
---

# RecordActionDeployment

Represents configuration settings for the Actions
& Recommendations, Action Launcher, and Bulk Action Panel components. For example, you can
have a deployment that specifies which types of actions to display, default actions for
channels, and the actions that users can add at runtime. If the component shows Next Best
Action recommendations, the deployment configures which strategies to use and how
recommendations appear. This type extends the Metadata metadata type and inherits its
fullName field.

![Important](/docs/resources/img/en-us/262.0?doc_id=images%2Ficon_note_important.png&folder=industries_reference)

#### Important

Where possible, we changed noninclusive terms to align with our company
value of Equality. We maintained certain terms to avoid any effect on customer
implementations.

## File Suffix and Directory Location

RecordActionDeployment values are stored in the
developer\_name.deployment file in the
recordActionDeployments directory.

![Note](/docs/resources/img/en-us/262.0?doc_id=images%2Ficon_note.png&folder=industries_reference)

#### Note

We don’t recommend programmatically changing the API name of a
RecordActionDeployment.

## Version

RecordActionDeployment is available in API version 45.0 and later.

## Fields

| Field Name | Field Type | Description |
| --- | --- | --- |
| channelConfigurations | [RecordActionDeploymentChannel](#recordActionDeploymentChannel) | Specifies configuration settings for different channels in an Actions & Recommendations deployment. |
| componentName | ComponentName (enumeration of type string) | Specifies the name of the component used in the deployment:  - `ActionsAndRecommendations`—0 - `ActionLauncher`—1 - `BulkActionPanel`—2. This value is   available in API version 60.0 and later  For example, a value of 1 indicates that 1 is stored in the database if Action Launcher is used to create a deployment. Available in API version 56.0 and later. |
| deploymentContexts | [RecordActionDeploymentContext](#recordActionDeploymentContext) | Specifies the object context for quick actions and Next Best Action strategies. Available in API version 46.0 and later. |
| hasComponents | boolean | Indicates whether the record actions deployment includes components (`true`) or not (`false`). Available in API version 61.0 and later. |
| hasGuidedActions | boolean | Specifies that the component shows standard actions; for example, flows and quick actions. Available in API version 46.0 and later. |
| hasOmniscripts | boolean | Indicates whether the record actions deployment includes OmniScripts (`true`) or not (`false`). Available in API version 56.0 and later. The default value is `false`. |
| hasRecommendations | boolean | Specifies that the component shows recommendations from a Next Best Action strategy. Available in API version 46.0 and later. |
| masterLabel | string | Required. Specifies the name of the deployment. |
| recommendation | [RecordActionRecommendation](#recordActionRecommendation) | Specifies settings for how Next Best Action recommendations appear in the component. Available in API version 46.0 and later. |
| selectableItems | [RecordActionDeploymentSelectableItems](#recordActionDeploymentSelectableItems) | Specifies the actions that users can add at runtime. |
| shouldLaunchActionOnReject | boolean | Required. If `true`, launch the flow when the recommendation is rejected  by the agent. Available in API version 48.0 and later. |

## RecordActionDefaultItem

Represents actions and attributes specified as channel defaults in a deployment.

| Field Name | Field Type | Description |
| --- | --- | --- |
| action | string | Required. Specifies the API name of an action. For example, the API name of a flow, such as `Verify_Information`. |
| isMandatory | boolean | Specifies whether the action is marked as mandatory. The default value is `false`. |
| isUiRemoveHidden | boolean | Specifies whether the remove option is hidden in the UI. The default value is false. If `true`, the UI hides the ability to remove the action from the list. |
| pinned | PinnedAction (enumeration of type string) | Required. Indicates whether the action is pinned to the `Top` or `Bottom`, or unpinned (`None`). The default value is `None`. |
| position | int | Required. Indicates the order of the action among all actions associated with this record. |
| type | RecordActionType (enumeration of type string) | Required. The type of action that’s associated with the record. Valid values are:  - `Flow` - `QuickAction` (Available in API version   46.0 and later.) - `OmniScript` (Available in API version 56.0   and later.) - `LWC` (Available in API version 62.0 and   later.) - `SvcCatalogItemDef` (Available in API   version 62.0 and later.) - `WebLink` (Available in API version 62.0   and later.) |

## RecordActionDeploymentChannel

Specifies channel-specific defaults to show in the Actions & Recommendations component.
The component displays the channel defaults when the list is otherwise empty.

| Field Name | Field Type | Description |  |
| --- | --- | --- | --- |
| channel | ChannelSource (enumeration of type string) | Required. Specifies the channel. Valid values are `Phone`, `Chat`, or `Default`. |  |
| channelItems | [RecordActionDefaultItem](#recordActionDefaultItem) | Specifies default actions for a channel and attributes for each action, such as whether the action is pinned to the list top or bottom or whether an action is considered mandatory. |  |
| isAutopopEnabled | boolean | Specifies whether the first action in the list is launched when the record page opens. If `true`, the first action is launched. The default value is `false`. |  |

## RecordActionDeploymentContext

Specifies an object that provides context for quick actions and Next Best Action
strategies. When the component appears on this type of page, it includes object-specific
quick actions and uses an object-specific strategy to filter recommendations. Available in
API version 46.0 and later.

![Note](/docs/resources/img/en-us/262.0?doc_id=images%2Ficon_note.png&folder=industries_reference)

#### Note

We support a maximum of 10 objects that provide context within a deployment.

| Field Name | Field Type | Description |
| --- | --- | --- |
| entityName | string | Required. Specifies the API name of an object to use as context. |
| recommendationStrategy | string | Specifies the API name of a Next Best Action strategy that overrides the default strategy on this page. A strategy is a metadata type RecommendationStrategy. |

## RecordActionRecommendation

Specifies settings to display Next Best Action recommendations in the component. Available
in API version 46.0 and later.

| Field Name | Field Type | Description |
| --- | --- | --- |
| defaultStrategy | string | Specifies the API name of the default Next Best Action strategy, which is a metadata type, RecommendationStrategy. |
| hasDescription | boolean | Required. If `true`, display the description for the recommendation. |
| hasImage | boolean | Required. If `true`, display the image for the recommendation. |
| hasRejectAction | boolean | Required. If `true`, display the label that the user clicks to reject the recommendation. |
| hasTitle | boolean | Required. If `true`, display the title for the recommendation. |
| maxDisplayRecommendations | int | Required. Specifies the maximum number of recommendations to display. Valid values are 1–4. |

## RecordActionSelectableItem

Represents the set of actions available for users to add to the component at runtime.

| Field Name | Field Type | Description |
| --- | --- | --- |
| action | string | Required. Specifies the API name of an action. For example, the API name of a flow, such as `Verify_Information`. |
| type | RecordActionType (enumeration of type string) | Required. The type of action that’s associated with the record. Valid values are:  - `Flow` - `QuickAction` (Available in API version   46.0 and later.) - `OmniScript` (Available in API version 56.0   and later.) - `LWC` (Available in API version 62.0 and   later.) - `SvcCatalogItemDef` (Available in API   version 62.0 and later.) - `WebLink` (Available in API version 62.0   and later.) |
| isFrequentAction | boolean | Indicates whether an action is frequently accessed by users (`true`) or not (`false`). Available in version 57.0 and later. This field applies only to Action Launcher. |
| frequentActionSequenceNbr | integer | The sequence number that's assigned to a frequently used action that's shown on Action Launcher. Available in version 57.0 and later. This field applies only to Action Launcher. |

## Wildcard Support in the Manifest File

This metadata type supports the wildcard character `*` (asterisk) in the package.xml manifest
file. For information about using the manifest file, see Deploying and Retrieving Metadata with the Zip File.

## Declarative Metadata Sample Definition

The following is a sample of a `recordActionDeployment`
file.

```
<RecordActionDeployment xmlns="http://soap.sforce.com/2006/04/metadata">
    <channelConfigurations>
        <channel>Phone</channel>
        <channelItems>
            <action>Sample_Flow</action>
            <isMandatory>false</isMandatory>
            <isUiRemoveHidden>false</isUiRemoveHidden>
            <position>1</position>
            <pinned>Top</pinned>
            <type>Flow</type>
        </channelItems>
        <channelItems>
            <action>Another_Sample_Flow</action>
            <isMandatory>false</isMandatory>
            <isUiRemoveHidden>true</isUiRemoveHidden>
            <position>2</position>
            <pinned>Top</pinned>
            <type>Flow</type>
        </channelItems>
        <isAutopopEnabled>true</isAutopopEnabled>
    </channelConfigurations>
    <masterLabel>Sample Deployment</masterLabel>
    <selectableItems>
        <action>Sample_Flow</action>
        <type>Flow</type>
        <isFrequentAction>true</isFrequentAction>
        <frequentActionSequenceNbr>1</frequentActionSequenceNbr>
    </selectableItems>
    <selectableItems>
        <action>Sample_Flow_2</action>
        <type>Flow</type>
        <isFrequentAction>false</isFrequentAction>
    </selectableItems>
    <hasGuidedActions>true</hasGuidedActions>
    <hasRecommendations>true</hasRecommendations>
    <recommendation>
        <defaultStrategy>Sample_Global_Strategy</defaultStrategy>
        <maxDisplayRecommendations>4</maxDisplayRecommendations>
        <hasImage>true</hasImage>
        <hasDescription>true</hasDescription>
        <hasRejectAction>true</hasRejectAction>
        <hasTitle>true</hasTitle>
    </recommendation>
    <deploymentContexts>
        <entityName>Case</entityName>
        <recommendationStrategy>Sample_Case_Strategy</recommendationStrategy>
    </deploymentContexts>
    <deploymentContexts>
        <entityName>Account</entityName>
        <recommendationStrategy>Sample_Acc_Strategy</recommendationStrategy>
    </deploymentContexts>
</RecordActionDeployment>
```

The following is an example `package.xml` that
references the previous definition.

```
<?xml version="1.0" encoding="UTF-8"?>
<Package xmlns="http://soap.sforce.com/2006/04/metadata">
    <fullName>SecondTest</fullName>
    <types>
        <members>Sample_Flow</members>
        <members>Another_Sample_Flow</members>
        <members>Sample_Flow_2</members>
        <name>Flow</name>
    </types>
    <types>
        <members>SampleDeployment</members>
        <name>RecordActionDeployment</name>
    </types>
    <version>45.0</version>
</Package>
```
