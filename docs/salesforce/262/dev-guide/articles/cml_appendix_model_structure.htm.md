---
page_id: cml_appendix_model_structure.htm
title: Model Structure
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/cml_appendix_model_structure.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Constraint Modeling Language
parent_page: cml_what_is_constraint_modeling_language.htm
fetched_at: 2026-06-09
---

# Model Structure

The tables on the following pages show the structure for the constraint model in Core
Concept Examples.

See [Core Concept Examples](./cml_core_concept_examples.htm.md "These examples illustrate core Constraint Modeling Language (CML) concepts including type, relationships, constraints, and so on.").

| Level | Product Group | Product | Product Type Name | Product Attribute | API Name OR CML Variable | Configurable or Static | Type | Comments |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | Bundle | Generator Set | GeneratorSet |  |  |  |  |  |
|  |  |  |  | Required KW | requiredKW | CONFIGURABLE | int |  |
|  |  |  |  | Surge Load KW | surgeLoadKW | EXPRESSION | decimal | requiredKW \* 1.25 |
|  |  |  |  | Reserve Capacity KW | reserveCapacityKW | EXPRESSION | decimal | surgeLoadKW - requiredKW |
|  |  |  |  | Voltage | voltage | CONFIGURABLE | Picklist Voltage ["220/380","240/416","255/440","277/480","347/600","2400/4160","7200/12470","7621/13200","7976/13800"] |  |
|  |  |  |  | Duty Rating | dutyRating | CONFIGURABLE | Picklist DutyRating ["Prime Power", "Continuous Power", "Data Center Continuous", "Emergency Standby Power"] |  |
|  |  |  |  | Standards and Compliance | standardsAndCompliance |  | Picklist standardsAndCompliance ["Certification-CSA", "Listing-UL 2200"] |  |
|  |  |  |  | max dB level | dBMax | CONFIGURABLE | int |  |
|  |  |  |  | Nominal Power Output | nominalPowerOutput |  | Picklist Power Output Picklist ["100 kW", "300 kW", "500 kW", "700 kW"] |  |
| 1 | General |  |  |  |  |  |  |  |
| 2 | General - Model |  | GeneralModel |  |  |  |  |  |
|  |  |  |  | Power KW | powerKW | STATIC | Picklist powerKW [900, 1750, 2500] | powerKW >= Needs.requiredKW |
|  |  |  |  | dB | dB | STATIC | Picklist dB [78, 90, 94] |  |
|  |  | General Model 900 | GeneralModel900 |  |  |  |  |  |
|  |  | General Model 1750 | GeneralModel1750 |  |  |  |  |  |
|  |  | General Model 2500 | GeneralModel2500 |  |  |  |  |  |
| 2 | General - Voltage Connection |  | VoltageConnection |  |  |  |  |  |
|  |  |  |  | Voltage | voltage | STATIC | Picklist voltage ["220/380", "240/416", "255/440"] | voltage == Needs.voltage |
|  |  |  |  | Cable Entry | cableEntry | CONFIGURABLE | Picklist cableEntry ["Top Entry", "Bottom Entry", "Side Entry"] |  |
|  |  | 220/380,3 Phase,Wye,4 Wire | VoltageConnection\_220\_380 |  |  |  |  |  |
|  |  | 240/416,3 Phase,Wye,4 Wire | VoltageConnection\_240\_416 |  |  |  |  |  |
|  |  | 255/440,3 Phase,Wye,4 Wire | VoltageConnection\_255\_440 |  |  |  |  |  |
| 1 | Alternator |  |  |  |  |  |  |  |
| 2 | Alternator - Main Alternator |  | MainAlternator |  |  |  |  |  |
|  |  |  |  |  | voltage | STATIC | Picklist Voltage | Needs.voltage == voltage |
|  |  |  |  |  | PRP | STATIC | boolean | constraint(Needs.dutyRating=="Prime Power"->PRP==true) |
|  |  |  |  |  | COP | STATIC | boolean | constraint(Needs.dutyRating=="Continuous Power"->COP==true) |
|  |  |  |  |  | DCC | STATIC | boolean | constraint(Needs.dutyRating=="Data Center Continuous"->DCC==true) |
|  |  |  |  |  | ESP | STATIC | boolean | constraint(Needs.dutyRating=="Emergency Standby Power"->ESP==true) |
|  |  | Alt-60Hz,Wye,220/380V,150/125/105C-SD/P/C,40C amb | FESBA\_B595\_2 |  |  |  |  |  |
|  |  | Alternator-60Hz,Wye,240/416 Volt,105/80C-StbyPrm | FESBA\_B715\_2 |  |  |  |  |  |
|  |  | Alt-60Hz,Wye,440V,150/125SP,40C amb | FESBA\_B691\_2 |  |  |  |  |  |
| 2 | Alternator - Heater |  |  |  |  |  |  |  |
| 2 | Alternator - Temperature Sensors |  | TemperatureSensor |  |  |  |  |  |
|  |  |  |  | Max Operating KW | maxOperatingKW | STATIC |  |  |
|  |  |  |  | Parent Required KW | parentRequiredKW | EXPRESSION |  |  |
|  |  | Temp Sens-Stator, 2 RTD/Ph | StatorTemperatureSensor |  |  |  |  |  |
|  |  | Bearing,1 RTD NDE | BearingTemperatureSensor |  |  |  |  |  |
| 2 | Alternator - Output Terminals |  | OutputTerminal |  |  |  |  |  |
|  |  | Output Terminals-2-Hole Lug, NEMA | OutputTerminals2HoleLugNEMA |  |  |  |  |  |
| 1 | Engine |  |  |  |  |  |  |  |
| 2 | Engine - Engine Model |  | EngineModel |  |  |  |  |  |
|  |  | Engine - QSK60-G6 | FESBA\_2940 |  |  |  |  |  |
| 2 | Engine - Starter Motor |  | StarterMotor |  |  |  |  |  |
|  |  | Electric Starter Motor - 24V DC | FESBA\_A334-2 |  |  |  |  |  |
| 2 | Engine - Fuel Filter |  | FuelFilter |  |  |  |  |  |
|  |  | Fuel Filters-Engine, Standard | FESBA\_3090 |  |  |  |  |  |
|  |  | Fuel Filters-Engine, Duplex | FESBA\_C278-2 |  |  |  |  |  |
| 1 | Control |  |  |  |  |  |  |  |
| 2 | Control - Control Main |  | Control |  |  |  |  |  |
|  |  |  |  | Control Placement | controlPlacement | CONFIGURABLE | Picklist ["Left", "Right", "Top"] |  |
|  |  |  |  | Commissioning Scope | commissioningScope | CONFIGURABLE | Picklist ["None", "Remote Support", "On-site Commissioning"] |  |
|  |  |  |  | Control Language | controlLanguage | CONFIGURABLE | Picklist ["English", "Danish", "French"] |  |
|  |  | PowerCommand 3.3 | FESBA\_H704\_2 |  |  |  |  |  |
|  |  | PowerCommand 3.3 with MLD | FESBA\_KX21\_2 |  |  |  |  |  |
| 2 | Control - Control Cabinet Heater |  | ControlCabinetHeater |  |  |  |  |  |
|  |  | 120/240VAC compatible | FESBA\_A460\_2 |  |  |  |  |  |
| 1 | Services |  |  |  |  |  |  |  |
| 2 | Services - Warranty |  | Warranty |  |  |  |  |  |
|  |  | Warranty PRP | Warranty\_PRP |  |  |  |  |  |
|  |  | Warranty DCC | Warranty\_DCC |  |  |  |  |  |
|  |  | Warranty ESP | Warranty\_ESP |  |  |  |  |  |
| 2 | Services - Maintenance |  | Maintenance |  |  |  |  |  |
|  |  |  |  | Maintenance Duration | maintenanceDuration | CONFIGURABLE | int [12..60] |  |
|  |  |  |  | Coverage Level | coverageLevel | CONFIGURABLE | Picklist ["Standard", "Premium"] |  |
|  |  | Standard Maintenance Kit | StandardMaintenanceKit |  |  |  |  |  |
| 2 | Services - Testing |  | Test |  |  |  |  |  |
|  |  | Test - Standard Factory | StandardFactoryTest |  |  |  |  |  |
|  |  | Test Record-Certified | TestRecord |  |  |  |  |  |
|  |  | Test-Independent Laboratory | IndependentLaboratoryTest |  |  |  |  |  |
|  |  | Test - Witness | WitnessTest |  |  |  |  |  |
|  |  | Test-Extended, Standby Load, 2 | WitnessTestService |  |  |  |  |  |
| 1 | Accessories |  |  |  |  |  |  |  |
| 2 | Accessories - Main |  | Accessory |  |  |  |  |  |
|  |  |  |  | Category | category | CONFIGURABLE | Picklist |  |
|  |  |  |  | Weight | weight |  |  |  |
| 2 | Accessories - Enclosure |  | Enclosure |  |  |  |  |  |
|  |  |  |  | dB Reduction | dBReduction | STATIC | Picklist dBReduction [0, 1, 3, 6, 9] |  |
|  |  | Enclosure None | Enclosure\_None |  |  |  |  |  |
|  |  | Enclosure Weather | Enclosure\_Weather |  |  |  |  |  |
|  |  | Enclosure SA1 | Enclosure\_SA1 |  |  |  |  |  |
|  |  | Enclosure SA2 | Enclosure\_SA2 |  |  |  |  |  |
|  |  | Enclosure SA3 | Enclosure\_SA3 |  |  |  |  |  |
| 1 | Install & Misc |  |  |  |  |  |  |  |
| 2 | Install & Misc - Installation |  | install |  |  |  |  |  |
