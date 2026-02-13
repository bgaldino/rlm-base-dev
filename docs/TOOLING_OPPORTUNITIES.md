# Revenue Cloud Tooling Opportunities - Spring '26 (Release 260)

Based on evaluation of the [Revenue Cloud Developer Guide (Release 260)](https://developer.salesforce.com/docs/atlas.en-us.260.0.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/rlm_get_started.htm) and [Revenue Cloud Help Documentation](https://help.salesforce.com/s/articleView?id=ind.revenue_lifecycle_management_get_started.htm&type=5), here are opportunities for creating new CumulusCI tasks and tools.

## Current Tooling Coverage

The project already includes management tasks for:
- ✅ **Decision Tables** (`manage_decision_tables`) - List (with UsageType), query, refresh (full/incremental), activate, deactivate, validate_lists; category refresh tasks and org utility flows
- ✅ **Flows** (`manage_flows`) - List, query, activate, deactivate
- ✅ **Expression Sets** (`manage_expression_sets`) - List, query, version management
- ✅ **Context Definitions** (`extend_stdctx`, `modify_context`) - Extend and modify context definitions
- ✅ **Pricing Data** (`sync_pricing_data`) - Sync pricing data
- ✅ **Permission Sets** (`assign_permission_set_groups_tolerant`) - Tolerant PSG assignment

## New Tooling Opportunities from Spring '26

### 1. Promotions Management

**Spring '26 Feature**: New Promotions engine with REST API support for retrieving promotions, eligibility rules, and promotion display in pricing.

**Potential Tasks:**
- `manage_promotions` - List, query, activate/deactivate promotions
- `query_promotion_eligibility` - Check promotion eligibility for products/transactions
- `sync_promotions` - Sync promotions from external systems

**API Endpoints to Use:**
- REST API for promotions (documented in Spring '26)
- Tooling API for promotion metadata

**Reference**: [Spring '26 Revenue Cloud Features](https://thecloudupdate.co/spring-26-revenue-cloud-features-walkthrough/)

---

### 2. Product Catalog Management (PCM) Cache Operations

**Spring '26 Feature**: Simplified cache operations (refresh, empty) for product data syncs. Support for Enterprise Product Catalog (EPC) as catalog source via REST API.

**Potential Tasks:**
- `manage_pcm_cache` - Refresh, empty, or monitor product catalog cache
- `validate_pcm_config` - Validate catalog search configuration and limits
- `sync_epc_catalog` - Sync Enterprise Product Catalog data
- `audit_pcm_attributes` - Audit searchable/filterable attributes (increased limits in Spring '26)

**API Endpoints to Use:**
- PCM Connect REST APIs
- Product Catalog metadata via Tooling API

**Reference**: [Agentforce Revenue Management Spring '26 Notes](https://www.stratuscarta.com/post/agentforce-revenue-management-spring-26-260-release-notes-highlights)

---

### 3. Pricing Procedure Linter/Validator

**Spring '26 Feature**: 
- New IF statements in formula elements
- Unique element names and auto-numbering
- Enhanced logging/diagnostics for pricing elements
- Smarter price propagation across nested quote levels

**Potential Tasks:**
- `validate_pricing_procedures` - Validate pricing procedures for:
  - Proper use of IF statements
  - Unique element names and descriptions
  - Nested level consistency (up to 5 levels)
  - Missing or incorrectly used conditional logic
- `audit_pricing_logs` - Extract and analyze pricing diagnostic logs
- `compare_pricing_templates` - Compare custom procedures against baseline templates
- `extract_pricing_metadata` - Extract pricing procedure metadata for documentation

**API Endpoints to Use:**
- Metadata API (Expression Sets, Pricing Procedure metadata)
- Tooling API for pricing procedure queries
- REST endpoints if exposed for diagnostics

**Reference**: [Spring '26 Revenue Cloud Features](https://thecloudupdate.co/salesforce-revenue-cloud-spring-26-new-features/)

---

### 4. Context Mapping Verifier

**Spring '26 Feature**: Enhanced Context Mapping UI with inline search, filtering (mapped vs unmapped), and unified UI for sObject mappings.

**Potential Tasks:**
- `verify_context_mappings` - Verify context definitions and mappings:
  - Compare against baseline mappings
  - Identify unmapped or misconfigured context sObject mappings
  - Enforce naming conventions
  - Validate filter configurations
- `audit_context_coverage` - Ensure all required context attributes are mapped
- `sync_context_mappings` - Sync context mappings across orgs

**API Endpoints to Use:**
- Metadata API for Context Definition
- Tooling API for context mapping queries
- Describe calls for sObject mappings

**Reference**: [Spring '26 Revenue Cloud Features](https://thecloudupdate.co/spring-26-revenue-cloud-features-walkthrough/)

---

### 5. Product Configurator Validator

**Spring '26 Feature**:
- Clone functionality for product instances
- Edit child product attributes from parent option cards
- Persistent validation/error messages during scroll

**Potential Tasks:**
- `validate_configurator_flows` - Validate configurator flow metadata
- `test_configurator_attributes` - Verify attribute inheritance and validation
- `scan_configurations` - Scan large configurations for issues
- `extract_configurator_metadata` - Extract configuration metadata for quality checks

**API Endpoints to Use:**
- Flow metadata (for configurator flows)
- Product configuration metadata via Tooling API
- Validation API endpoints if available

**Reference**: [Spring '26 Revenue Cloud Features](https://thecloudupdate.co/spring-26-revenue-cloud-features-walkthrough/)

---

### 6. Flow Enhancement Tools

**Spring '26 Feature**: 
- Data table enhancements (inline editing, hyperlinks)
- Flow debugging improvements (saving input values)
- Canvas scrolling options
- New `Flow PageReference` type for navigation from Lightning components

**Potential Tasks:**
- `audit_flow_metadata` - Verify flow metadata (fields, elements, versions)
- `check_flow_deprecations` - Check for deprecated flow components or configurations
- `generate_flow_navigation` - Auto-generate UI navigation links using Flow PageReference
- `export_flow_debug_data` - Export flow debugging data and input values

**API Endpoints to Use:**
- Tooling API (`FlowDefinition`, `Flow` objects)
- Flow metadata via Metadata API
- REST API for flow debugging if available

**Reference**: [Spring '26 Flow Features](https://salesforcetime.com/2025/12/11/new-flow-features-of-spring-26-release/)

---

### 7. Template Change Detector

**Spring '26 Feature**: Unique element names, descriptions, and auto-numbering in expression sets/templates.

**Potential Tasks:**
- `detect_template_changes` - Detect when underlying standard templates change:
  - Compare baseline template metadata
  - Identify custom procedures that need updates
  - Track changes in unique element names and descriptions
- `sync_template_updates` - Sync template updates to custom procedures
- `validate_template_compliance` - Ensure custom templates follow naming conventions

**API Endpoints to Use:**
- Metadata API for template comparison
- Tooling API for expression set queries
- Version control metadata

**Reference**: [Spring '26 Revenue Cloud Features](https://thecloudupdate.co/spring-26-revenue-cloud-features-walkthrough/)

---

## Implementation Considerations

### API Version Compatibility

- **Target API Version**: 66.0 (Release 260)
- **My Domain Enforcement**: Spring '26 enforces My Domain URLs for API traffic
- **Deprecated APIs**: SOAP API `login()` for versions 31.0–64.0 will be retired by Summer '27

**Recommendations:**
- Use My Domain URLs for all API calls
- Ensure tools use API version 66.0 or later
- Test behavior in both Sandbox and Production environments

### Field Availability Validation

Some fields may not be available in all orgs or license types:
- Use `describe` calls to validate field availability
- Implement fallback logic for missing fields
- Test in target orgs before production use

### Beta/Pilot Features

Some Spring '26 features may be in Pilot or Beta:
- Check feature availability before building tools
- Implement feature detection logic
- Provide graceful degradation for unavailable features

---

## Recommended Priority

Based on current project needs and Spring '26 capabilities:

1. **High Priority:**
   - `manage_pcm_cache` - Product catalog cache management is critical for data sync
   - `validate_pricing_procedures` - Pricing validation is essential for accuracy
   - `verify_context_mappings` - Context mapping verification prevents configuration errors

2. **Medium Priority:**
   - `manage_promotions` - Promotions are new in Spring '26, good for future-proofing
   - `audit_pricing_logs` - Diagnostic capabilities improve troubleshooting
   - `detect_template_changes` - Template change detection helps maintain consistency

3. **Low Priority:**
   - `validate_configurator_flows` - Configurator validation is useful but less critical
   - `generate_flow_navigation` - Nice-to-have enhancement for flow management

---

## Next Steps

1. **Review Official Documentation**: Deep dive into the [Revenue Cloud Developer Guide (Release 260)](https://developer.salesforce.com/docs/atlas.en-us.260.0.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/rlm_get_started.htm) for specific API endpoints and metadata types

2. **Validate API Availability**: Test API endpoints and metadata queries in a Spring '26 org to confirm availability

3. **Prototype Tasks**: Start with high-priority tasks, using existing task patterns (`manage_decision_tables`, `manage_flows`) as templates

4. **Document Examples**: Create example documentation similar to `DECISION_TABLE_EXAMPLES.md` and `TASK_EXAMPLES.md`

---

## References

- [Revenue Cloud Developer Guide (Release 260)](https://developer.salesforce.com/docs/atlas.en-us.260.0.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/rlm_get_started.htm)
- [Revenue Cloud Help Documentation](https://help.salesforce.com/s/articleView?id=ind.revenue_lifecycle_management_get_started.htm&type=5)
- [Spring '26 Release Notes](https://www.salesforce.com/releases/)
- [Agentforce Revenue Management Spring '26 Highlights](https://www.stratuscarta.com/post/agentforce-revenue-management-spring-26-260-release-notes-highlights)
