# CumulusCI Reference

This page is the stable human-facing entry point for CumulusCI reference
material. The maintained task, flow, and feature flag references are generated
from `cumulusci.yml` at:

- `.cursor/skills/cci-orchestration/tasks-reference.md`
- `.cursor/skills/cci-orchestration/flows-reference.md`
- `.cursor/skills/cci-orchestration/feature-flags.md`

The generated files include task classes/options, flow step trees, and feature
flag usage. Keeping the detailed listings generated avoids drift between
documentation and the actual CCI configuration.

Regenerate those files after any `cumulusci.yml` task, flow, option, or feature
flag change:

```bash
python scripts/ai/generate_cci_reference.py
```

This file intentionally stays thin. If this repository is published through a
docs site or shared externally, keep this page as the stable link target and make
sure the generated `.cursor/skills/cci-orchestration/` files are available to
readers.
