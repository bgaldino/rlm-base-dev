# Adding a New Feature — Complete Guide

Step-by-step guide with code templates for adding a new feature to the
rlm-base-dev repository.

---

## 1. Feature Flag

Add a boolean flag under `project.custom` in `cumulusci.yml`:

```yaml
project:
  custom:
    myfeature: true
```

## 2. Metadata

If creating a new `unpackaged/post_<feature>/` bundle, create a deploy task:

```yaml
tasks:
  deploy_post_myfeature:
    description: Deploy My Feature Metadata
    class_path: cumulusci.tasks.salesforce.Deploy
    group: Revenue Lifecycle Management
    options:
      path: unpackaged/post_myfeature
```

## 3. Data Plan (if needed)

Create `datasets/sfdmu/qb/en-US/qb-myfeature/`:
- `export.json` with objects, externalIds, operations
- CSV files for each object

Add a dataset path anchor and register tasks:

```yaml
project:
  custom:
    myfeature_dataset: &myfeature_dataset "datasets/sfdmu/qb/en-US/qb-myfeature"

tasks:
  insert_qb_myfeature_data:
    group: Revenue Lifecycle Management
    description: Insert My Feature Data
    class_path: tasks.rlm_sfdmu.LoadSFDMUData
    options:
      pathtoexportjson: *myfeature_dataset

  delete_qb_myfeature_data:
    group: Data Maintenance
    description: Delete My Feature data in dependency order
    class_path: cumulusci.tasks.apex.anon.AnonymousApexTask
    options:
      path: scripts/apex/deleteMyFeatureData.apex

  extract_qb_myfeature_data:
    group: Data Management - Extract
    description: "Extract qb-myfeature from org to CSV."
    class_path: tasks.rlm_sfdmu.ExtractSFDMUData
    options:
      pathtoexportjson: *myfeature_dataset

  test_qb_myfeature_idempotency:
    group: Data Management - Idempotency
    description: Idempotency test for qb-myfeature.
    class_path: tasks.rlm_sfdmu.TestSFDMUIdempotency
    options:
      pathtoexportjson: *myfeature_dataset
      use_extraction_roundtrip: false
```

## 4. Permission Sets (if needed)

```yaml
project:
  custom:
    ps_myfeature: &ps_myfeature
      - RLM_MyFeature

# In the flow:
    task: assign_permission_sets
    when: project_config.project__custom__myfeature
    options:
      api_names: *ps_myfeature
```

## 5. Context Definition (if needed)

```yaml
tasks:
  apply_context_myfeature:
    group: Revenue Lifecycle Management
    description: Apply MyFeature context attributes
    class_path: tasks.rlm_context_service.ManageContextDefinition
    options:
      developer_name: RLM_SalesTransactionContext
      plan_file: datasets/context_plans/MyFeature/manifest.json
      translate_plan: true
      activate: true
```

## 6. Sub-Flow

```yaml
flows:
  prepare_myfeature:
    group: Revenue Lifecycle Management
    description: >
      Deploy and configure My Feature.
    steps:
      1:
        task: deploy_post_myfeature
        when: project_config.project__custom__myfeature
      2:
        task: insert_qb_myfeature_data
        when: project_config.project__custom__myfeature and project_config.project__custom__qb
      3:
        task: apply_context_myfeature
        when: project_config.project__custom__myfeature
      4:
        task: assign_permission_sets
        when: project_config.project__custom__myfeature
        options:
          api_names: *ps_myfeature
```

## 7. Wire into `prepare_rlm_org`

```yaml
flows:
  prepare_rlm_org:
    steps:
      XX:
        flow: prepare_myfeature
```

## 8. UX Changes (if needed)

```
templates/flexipages/standalone/myfeature/RLM_MyObject_Record_Page.flexipage-meta.xml
templates/layouts/myfeature/MyObject-RLM MyObject Layout.layout-meta.xml
templates/profiles/patches/myfeature/Admin.profile.patch.xml
```

## 9. Custom Python Task (if needed)

```
tasks/rlm_myfeature.py
```

See `.cursor/skills/cci-orchestration/custom-task-authoring.md`.

## 10. Regenerate CCI References

```bash
python scripts/ai/generate_cci_reference.py
```

## 11. `.forceignore` Updates (if needed)

If UX metadata moved from `force-app/` or `unpackaged/post_*/` to
`templates/`, add `.forceignore` entries.

---

## Updating Existing Features

### Adding a field to an existing object
1. Add field XML to `force-app/` or `unpackaged/post_<feature>/objects/`
2. Update permission sets for FLS
3. Update layout template in `templates/layouts/` (not `force-app/`)

### Adding a record to an existing data plan
1. Add row to CSV in `datasets/sfdmu/qb/en-US/qb-<plan>/`
2. If new object, add to `export.json` (parent→child order)
3. Run idempotency test

### Adding a step to an existing flow
1. Add step in `cumulusci.yml` with `when:` condition
2. Regenerate CCI references
