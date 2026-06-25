# Expression Set Business APIs — Link Index

Curated links for Expression Set developer documentation (Industries Common Resources).

## Primary page

- [Expression Set Business APIs](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/expression_set_connect_apis.htm)

## Related pages

- [Expression Set (overview)](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/expression_set_parent.htm)
- [Expression Set Invocation (POST)](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_resources_bre_expression_set.htm)
- [Expression Set (PATCH)](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_resources_bre_expression_set_id_patch.htm)
- [Expression Set Actions (Invocable)](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/actions_obj_expression_set.htm)
- [ExpressionSetDefinition (Tooling API)](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/tooling_api_objects_expressionsetdefinition.htm)
- [Expression Set Standard Objects](https://developer.salesforce.com/docs/atlas.en-us.psc_api.meta/psc_api/expression_set_standard_objects.htm)

## Request bodies

- [Request Bodies (index)](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/expression_set_requests.htm)
- [Business Rules Input](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_requests_business_rules_input.htm)
- [Expression Set Input](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_requests_expression_set_input.htm)

### Request body types listed by Salesforce

- `Business Rules Input`
- `Context Definition Input`
- `Expression Set Advanced Condition Step Input`
- `Expression Set Aggregation Step Input`
- `Expression Set Assignment Step Input`
- `Expression Set Condition Criteria Input`
- `Expression Set Condition Expression Step`
- `Expression Set Custom Element Parameter Input`
- `Expression Set Custom Element Step Input`
- `Expression Set DES Token Mapping Input`
- `Expression Set Input`
- `Expression Set Lookup Table Step Input`
- `Expression Set Options Input`
- `Expression Set SubExpression Step Input`
- `Expression Set Version Input`
- `Expression Set Version Step Input`
- `Expression Set Version Variable Input`

### Schema highlights extracted

- **`Business Rules Input`**
  - Properties:
    - `inputs` — `Map<String, Object>[]` (**Required**, available from v55.0)
    - `options` — `Expression Set Options Input` (**Optional**, available from v55.0)
  - Notes:
    - Use `__actionContextCode` per input when needed.
    - For field-alias variables, append `Id` to the alias owner object name and pass the source record Id.
    - For context-definition variables, append `Id` to the context definition developer name and pass the context Id.

- **`Expression Set Input`** (create/update payload)
  - Properties:
    - `apiName` — `String` (**Required**, v58.0)
    - `contextDefinitions` — `Context Definition Input` (**Optional**, v58.0)
    - `description` — `String` (**Optional**, v58.0)
    - `name` — `String` (**Required**, v58.0)
    - `usageType` — `String` (**Required**, v58.0). NOTE: the doc page lists only
      `Bre`, but this is **stale** — the generated OAS enum also includes
      `DefaultPricing` and `PricingDiscovery` (a pricing procedure is
      `usageType: DefaultPricing`). See
      `docs/references/expression-set-connect-api-reference.md` → Verified schema
      for the OAS-confirmed enum set.
    - `versions` — `Expression Set Version Input[]` (**Optional**, v58.0)

## Notes

- These links are external Salesforce Developer docs and complement the local snapshot corpus under `docs/salesforce/262/dev-guide/articles/`.
- This is a manually curated index intended for quick lookup.
- For the local task-level guidance on reading/mutating Expression Sets, see the
  **Expression Sets skill** (`.cursor/skills/expression-sets/SKILL.md`) and its
  reference (`docs/references/expression-set-connect-api-reference.md`).
