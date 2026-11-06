# Recipes

Published bundles exported from MeshMesh, Claude, and Cursor. Each tool has its own directory. Each bundle is one directory under that tool, with its entry file at the root of the bundle.

MeshMesh is the only one of the three that uses a recipe. Claude and Cursor use skills.

| Tool | Path | Entry file |
|------|------|------------|
| MeshMesh | `recipes/meshmesh/<name>/` | `recipe.md` |
| Claude | `recipes/claude/<name>/` | `SKILL.md` |
| Cursor | `recipes/cursor/<name>/` | `SKILL.md` |

Keep every file the entry file refers to as a sibling of that entry file. Supporting metadata, JSON, Markdown, and PDFs stay inside the bundle directory.

Cursor and Claude load the skills they run from `.cursor/skills/`. This tree is the published copy of an exported bundle.

Salesforce metadata that ships inside a bundle stays in that bundle. UX metadata for the org build stays in `templates/`.
