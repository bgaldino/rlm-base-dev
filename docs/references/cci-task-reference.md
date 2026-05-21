# CumulusCI Task Reference

The maintained task reference for this repository is generated from
`cumulusci.yml` at:

- `.cursor/skills/cci-orchestration/tasks-reference.md`
- `.cursor/skills/cci-orchestration/flows-reference.md`
- `.cursor/skills/cci-orchestration/feature-flags.md`

Regenerate those files after any `cumulusci.yml` task, flow, option, or feature
flag change:

```bash
python scripts/ai/generate_cci_reference.py
```

This file intentionally stays thin so task listings do not drift from the
generated CCI reference files.
