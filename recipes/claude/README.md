# Claude skills

Claude Code loads skills, not recipes. One directory per exported skill. `SKILL.md` sits at the root of that directory. Supporting files stay beside it.

```text
recipes/claude/<name>/
  SKILL.md
  ...
```

The skills Claude Code loads in this repository are the shared catalog in `.cursor/skills/`, reached through `.claude/skills/`. Add a bundle here when publishing an export.
