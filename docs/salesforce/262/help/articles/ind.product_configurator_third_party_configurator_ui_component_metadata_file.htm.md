---
article_id: ind.product_configurator_third_party_configurator_ui_component_metadata_file.htm
title: Third-Party Configurator UI Component Metadata Configuration File
source_url: https://help.salesforce.com/s/articleView?id=ind.product_configurator_third_party_configurator_ui_component_metadata_file.htm&type=5&release=262
release: 262
release_name: Summer '26
area: configurator
fetched_at: 2026-05-12
---

# Third-Party Configurator UI Component Metadata Configuration File

The configuration file defines the metadata values for the component, including supported targets and the design configuration.

REQUIRED EDITIONS

The configuration file follows the naming convention componentName.js-meta.xml, such as myComponent.js-meta.xml.

Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions of Revenue Cloud with the Revenue Cloud Growth license or the Revenue Cloud Advanced license

Set up the js-meta.xml file to expose the component to Lightning Flow and add it to the Product Configurator flow template.

This example includes the input properties you can import from the Data Manager component or other variables on the default product configurator flow. If you create a custom configurator flow with other properties, you can add those to your js-meta.xml file.

<?xml version="1.0" encoding="UTF-8"?>
<!--
  ~ Copyright 2024 salesforce.com, inc. 
  ~ All Rights Reserved 
  ~ Company Confidential
  -->

<LightningComponentBundle xmlns="http://soap.sforce.com/2006/04/metadata">
    <apiVersion>60.0</apiVersion>
    <isExposed>true</isExposed>
    <masterLabel>My Third Party Configurator Component</masterLabel>
    <description>My custom component that I will use in the 
        Configurator UI</description>
    <targets>
        <target>lightning__FlowScreen</target>
    </targets>
    <targetConfigs>
        <targetConfig targets="lightning__FlowScreen">
            <!-- INPUT PROPERTIES -->
            <property
                    name="transactionLineId"
                    type="String"
                    required="true"
                    label="Line Item ID"
                    description="Enter the ID of the transaction line to configure."
                    role="inputOnly" />
            <property
                    name="currentTransactionLineId"
                    type="String"
                    required="true"
                    label="Current Line Item ID"
                    description="The ID of the transaction line to launch the configurator."
                    role="inputOnly" />
            <property
                    name="transactionId"
                    type="String"
                    required="true"
                    label="Transaction ID"
                    description="Enter the ID of the transaction to configure."
                    role="inputOnly" />
            <property
                    name="addedNodes"
                    type="apex://ProductConfig.SalesTransactionItem[]"
                    label="Added Nodes"
                    description="Enter the API name of the flow resource that contains a collection of Apex ProductConfig__SalesTransactionItem records associated with the parent record transaction."
                    role="inputOnly" />
            <property
                    name="parentName"
                    type="String"
                    required="true"
                    label="Parent Name"
                    description="Enter the name or title of the parent transaction that the configuration pertains to."
                    role="inputOnly" />
            <property
                    name="origin"
                    type="String"
                    required="true"
                    label="Object Name"
                    description="Enter the API name of the transaction record's parent object."
                    role="inputOnly" />
            <property
                    name="messages"
                    type="apex://ProductConfig.Message[]"
                    label="Messages"
                    description="A collection of Apex ProductConfig__Message records that contain alerts, warnings, and errors encountered by the component."
                    role="inputOnly" />
            <property
                    name="optionGroups"
                    type="apex://ProductConfig.OptionGroup[]"
                    label="Option Groups"
                    description="A collection of ProductConfig__OptionGroup records that contain product option data grouped by product category."
                    role="inputOnly" />
            <property
                    name="summary"
                    type="apex://ProductConfig.PricingSummary"
                    label="Transaction Summary"
                    description="An Apex ProductConfig__PricingSummary record that contains summary information for the specified transaction ID, including all price-related details."
                    role="inputOnly" />
            <property
                    name="attributeCategories"
                    type="apex://ProductConfig.AttributeCategory[]"
                    label="Attribute Categories"
                    description="A collection of Apex ProductConfig__AttributeCategory records that contain details about the attributes groups that are grouped by attribute category."
                    role="inputOnly" />
            <property
                    name="header"
                    type="apex://ProductConfig.Product"
                    label="Product Details"
                    description="An Apex ProductConfig__Product record that contains details about the root-level product, including product name, description, and pricing."
                    role="inputOnly" />
            <property
                    name="navigationRoute"
                    type="apex://ProductConfig.NavigationInfo[]"
                    label="Navigation Information"
                    description="A collection of Apex ProductConfig__NavigationInfo records that contain breadcrumb navigation information for the UI."
                    role="inputOnly" />
            <property
                    name="searchInfo"
                    type="apex://ProductConfig.SearchItemInfo[]"
                    label="Search Info"
                    description="A collection of Apex ProductConfig__SearchItemInfo records that contain option information for the search bar."
                    role="inputOnly" />
            <property
                    name="currencyCode"
                    type="String"
                    label="Currency Code"
                    description="The currency code used for the transaction."
                    role="inputOnly" />
            <property
                    name="transactionRecord"
                    type="apex://ProductConfig.TransactionRecord"
                    label="Transaction Record"
                    description="An Apex ProductConfig__TransactionRecord record that contains transaction record details, including transaction origin, parent name, and ID."
                    role="inputOnly"/>
            <property
                    name="isClassContext"
                    type="Boolean"
                    label="Product Classification Preview Mode"
                    description="A Boolean value that indicates whether the record being previewed was a product classification record."
                    role="inputOnly" />
            <property
                    name="isDesignTime"
                    type="Boolean"
                    label="Preview Mode"
                    description="A Boolean value that indicates whether a product or product classification record was viewed in preview mode."
                    role="inputOnly" />
            <property
                    name="headerTitle"
                    type="String"
                    label="Configurator Title"
                    description="The title that was used for the configurator screen heading."
                    role="inputOnly" />
            <property
                    name="isInstantPricingToggleEnabled"
                    type="Boolean"
                    label="Show Instant Pricing Toggle"
                    description="A Boolean value that indicates whether the instant pricing toggle was shown."
                    role="inputOnly" />
            <property
                    name="isCompactLayoutEnabled"
                    type="Boolean"
                    label="Compact Mode"
                    description="A boolean value that indicates whether compact mode is enabled."
                    role="inputOnly" />
            <property
                    name="isInstantPricingEnabled"
                    type="Boolean"
                    label="Instant Pricing"
                    description="A Boolean value that indicates whether the instant pricing toggle was enabled. If false, the Update Prices button is shown for manual price refresh."
                    role="inputOnly" />
            <property
                    name="isProductValidationEnabled"
                    type="Boolean"
                    label="Product Validation"
                    description="A Boolean value that indicates whether product validation was enabled."
                    role="inputOnly" />
            <property
                    name="showPrices"
                    type="Boolean"
                    label="Price Visibility"
                    description="A Boolean value that indicates whether pricing information was shown at runtime."
                    role="inputOnly" />
            <property
                    name="isConfiguratorDisabled"
                    type="Boolean"
                    label="Disabled"
                    description="A Boolean value that indicates whether this component was disabled."
                    role="inputOnly" />
            <property
                    name="isApiInProgress"
                    type="Boolean"
                    label="API Call Status"
                    description="A Boolean value that indicates whether the API call is in progress."
                    role="inputOnly" />
            <property
                    name="isPriceRampEnabled"
                    type="Boolean"
                    label="Ramp Deals Enabled"
                    description="A Boolean value that indicates whether Ramp Deals are enabled for this product."
                    role="inputOnly" />
            <property
                    name="tabs"
                    type="apex://ProductConfig.NavigationInfo[]"
                    label="Navigation Tabs"
                    description="A collection of Apex ProductConfig__NavigationInfo records to display tabs in the Configurator."
                    role="inputOnly" />
            <property
                    name="salesTransactionItems"
                    type="apex://ProductConfig.SalesTransactionItem[]"
                    label="Sales Transaction Items"
                    description="A collection of Apex ProductConfig__SalesTransactionItem records that contain sales transaction item details."
                    role="inputOnly" />
            <property
                    name="searchResultOptionId"
                    type="String"
                    label="Search Result Option Id"
                    description="The ID of the option selected from the search bar."
                    role="inputOnly" />
        </targetConfig>
    </targetConfigs>
</LightningComponentBundle>
SEE ALSO
Create a Third-Party Configurator UI Component
