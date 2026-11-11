# Knowledge Sources — Repo, Snapshot, or Live Org

Read this when deciding which rules a plan can model from the repo and which need a
live org. Parent: [commercial-model-planning](SKILL.md).

## The decision rule

**The repo decides** when one of these holds:
- a skill holds a dated, measured fact or a shipped reference (XML, dataset, overlay)
  for the exact feature;
- the release's snapshot (Help or developer guide) documents the feature and nothing
  measured in the repo contradicts it.

**Having no skill is not a trigger on its own.** A feature with no skill but with
snapshot coverage is decided by the snapshot. Record it as a skill gap, not as a live
spike. Model the rule directly; its build gate proves it.

**A live org decides** when one of these holds:

| Trigger | Typical cases |
|---|---|
| (a) The snapshot and the skills are both silent on the rule | A behaviour no article or skill describes |
| (b) The repo measured behaviour that differs from, or isn't in, the docs | A header discount applying twice with an active procedure plan; a quantity edit on an amendment line resetting its attributes; a cancellation credit that doesn't prorate; an API-built ramped bundle that can't be amended (`ramped-quotes`) |
| (c) The rule is about numbers across the lifecycle | Amend, cancel and renew values: Help describes setup, not values |
| (d) The docs disagree, describe a preview with limitations, or lost information in capture | A considerations page for a preview feature; a support table whose values were icons and came through the snapshot blank |

While a release is pre-GA, a live org outranks its documentation (`AGENTS.md`). A live
answer that contradicts a skill or the snapshot is a finding: record it, and propose the
skill fix.

## The coverage sweep

Count coverage per area before deciding. From the repo root, for the release in
`.claude/skill-manifest.yml` (`salesforce_release_active`):

```bash
R=docs/salesforce/<release>
cover() {  # cover <label> <extended regex, use \b word boundaries>
  h=$(grep -rliE "$2" $R/help/articles | wc -l | tr -d ' ')
  d=$(grep -rliE "$2" $R/dev-guide* | wc -l | tr -d ' ')
  s=$(grep -rliE "$2" .cursor/skills --exclude-dir=commercial-model-planning --exclude=README.md \
      | sed -E 's#^\.cursor/skills/##' | tr '\n' ' ')
  printf "%-22s help=%-4s dev=%-4s files: %s\n" "$1" "$h" "$d" "$s"
}
cover cost-book "\bcost books?\b"
cover volume-tier "\bvolume tiers?\b|\btier(ed)? (pricing|adjustments?)\b"
cover approvals "\badvanced approvals?\b"
cover line-editor "\btransaction line editor\b"
```

- **Exclude this skill and the skills README.** They mention every area, so they would
  show as coverage everywhere.
- **Use word boundaries.** "rounding" also matches "grounding" and "surrounding";
  "clone" matches dozens of files. Record the regex next to each count in the plan.
- **List files, not skills.** A skill that mentions a term once in a table looks the
  same, by skill name, as one with a sub-file about it. The sweep prints each matching
  file; open the ones that look like coverage.
- **Search by mechanism as well as by feature name.** The docs often describe a
  feature through its building blocks rather than its business name. For example,
  "set a component quantity from an answer" is documented as cardinality constraints
  and `ceil()` in the CML articles, not under "sizing". Grep the developer guide's
  article titles for the area (`ls $R/dev-guide/articles | grep -i <area>`) before
  calling it silent.
- **Read before deciding.** A count says where to look, not what is true:
    - Zero hits in both the snapshot and the skills, after the mechanism search, is
      trigger (a).
    - A skill that only *mentions* a feature (in a schema list or a demo script) doesn't
      cover it.
    - A considerations or limitations page for a preview is trigger (d).
- **Check what's new.** Read `docs/salesforce/<release>/feature-index.md`: features new
  in the release are the likeliest to differ from older skill content.

## Recording the decision

Put this table in the plan, one row per area:

| Area | Repo skills (files) | Snapshot coverage (regex: counts, key articles) | Prior measured knowledge | Decided by | Why |
|---|---|---|---|---|---|
| \<area\> | `skill/sub-file.md` | `\bterm\b`: help 12, dev 3; `article-name` | dated measurements, from skills or earlier builds | **Repo** / **Snapshot** / **Live (a–d)** | one line |

Every **Live** row becomes a spike, with:
- the source value it must hit,
- the skills and articles to read before touching the org,
- the smallest case that proves it.

Every **Repo** or **Snapshot** row is proved at its build gate. A **Snapshot** row with no
skill is also listed in the plan's skill gaps.

## After the build

- Each spike's result goes into the plan's rule decision record.
- A spike that found knowledge no skill held becomes a skill extension, or a new skill
  if it needs its own routing (see `skill-authoring`).
- A live result that contradicts a skill gets a fix to that skill in the same change
  that records it.
