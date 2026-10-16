---
page_id: cml_best_practice_parent_products.htm
title: Configure Child or Grandchild Products Based on Parent Product
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/cml_best_practice_parent_products.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Configurator
parent_page: cml_cml_best_practices.htm
fetched_at: 2026-09-29
---

# Configure Child or Grandchild Products Based on Parent Product

Use the parent keyword to configure child and grandchild products dynamically based on
    the parent product.

    

Use the `parent` keyword to configure child and
      grandchild products dynamically based on the parent product. Control visibility or
      availability for the child or grandchild using the keyword.

    

#### Note

The `parent` keyword isn't supported with
      Group Type. When you organize components in Product Component Groups, the Group Type becomes
      an intermediate parent in the hierarchy. To reach the bundle root, use parent(attribute, 1)
      to skip the group, or use the dot-notation pattern from the bundle level,
      groupVariable.childRelation.attribute, instead of parent(). See [Group Type](./cml_group_type.htm.md).

    

In this example, grandchild products are excluded based on which parent product they belong
      to.

    

```
type LineItem;

/*
 * Parent 1: Industrial Bundle
 * Sets the context 'ApplicationType' to "Industrial"
 */
type IndustrialGeneratorBundle : LineItem {
    relation enclosurePackage : EnclosurePackage[1..999];

    relation enclosurePackage1 : EnclosurePackage[1..999];

    relation enclosurePackage2 : EnclosurePackage;

    string ApplicationType = "Industrial";
}

/*
 * Parent 2: Residential Bundle
 * Sets the context 'ApplicationType' to "Residential"
 */
type ResidentialGeneratorBundle : LineItem {
    relation enclosurePackage3 : EnclosurePackage[1..999];

    relation enclosurePackage4 : EnclosurePackage;

    string ApplicationType = "Residential";
}

/*
 * Shared Component: Enclosure Package
 * Uses parent() to read the ApplicationType and excludes items accordingly.
 */
type EnclosurePackage : LineItem {
    relation soundInsulation : SoundInsulation[0..999];
    relation weatherProofing : WeatherProofing[0..999];
    relation heater : Heater[0..999];
    relation lighting : InternalLighting[0..999];

// Retrieve the context tag from the parent bundle
    string parentApp = parent(ApplicationType);

    message(true, parentApp);

    // Logic 1: Exclude Lighting and Heater for BOTH bundles
    exclude(parentApp == "Industrial" || parentApp == "Residential", lighting[InternalLighting]);
    exclude(parentApp == "Industrial" || parentApp == "Residential", heater[Heater]);

    // Logic 2: Residential (Basic) excludes Sound Insulation
    exclude(parentApp == "Residential", soundInsulation[SoundInsulation]);

    // Logic 3: Industrial (Pro) excludes Weather Proofing
    exclude(parentApp == "Industrial", weatherProofing[WeatherProofing]);
}

// --- Sub-components ---

type SoundInsulation : LineItem {
    @(defaultValue = "Foam")
    string Material = ["Foam", "Fiberglass"];
}

type WeatherProofing : LineItem {
    @(defaultValue = "Standard")
    string Grade = ["Standard", "Marine"];
}

type Heater : LineItem;

type InternalLighting : LineItem;
```
