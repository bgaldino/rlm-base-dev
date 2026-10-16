# Retrospective: the ERD count drift, and six rounds of gating it

Sub-file of `.cursor/skills/doc-consistency/SKILL.md`. Read it when you are **writing or
hardening a check over hand-copied figures**, or when a sweep of yours has just been
reported closed. For the ERD refresh procedure itself — where `tests/test_erd_doc_counts.py`
runs, and what `--patch` will and will not repair — `.cursor/skills/schema-validation/SKILL.md`
is canonical; this file does not restate it.

Numbers below are **history**, deliberately not gated: they record what a specific pass
found on the 264 ERD. The live figures are the ones the check computes.

## What was wrong

The headline ERD triple is swept on every refresh — it went 4,190 → 4,252 fields at 264 and
all seven citations were updated. The **per-domain** counts underneath it never were, and
the sweep does not look at them:

- 8 of the 9 rows in the Domain Overview table of `revenue-cloud-data-model/SKILL.md`
  disagreed with the data, summing to 185 against an actual 263 — directly beneath a
  correct "263 objects" headline.
- 7 of the 9 `domains/*.md` headlines were wrong too. **15 numbers in all.**

Three properties made this worth a check rather than one more sweep:

1. **Not uniformly stale-low.** `rates.md` claimed 15 Rate Management objects where the data
   has 11, so "add the new ones" would not have found it.
2. **They had stopped describing anything measurable** — most matched neither the ERD nor
   the file's own object table.
3. **The refresh did not stale them.** The per-domain counts in `erd-data.json` are
   byte-identical at `release/262`. They had never been right.

## The check kept having the defect it was written to catch

Two of its layers exist only for that reason, and both generalize:

- **Asking whether *any* citation matched** let a file that reworded or renamed its own
  citation leave the audit while the run reported clean — wrong numbers in a reworded
  `scripts/ai/README.md` passed 33/33. Every site is now asserted individually, and **the
  total check count is pinned**, which is what turns "one citation quietly stopped being
  audited" into a failure. When you add a citation or a site, expect the pin to fail and
  raise `EXPECTED_CHECKS` deliberately.
- **A restatement in another form escapes the pattern.** The Statistics bullet block in
  `docs/erds/README.md` gives all three totals as a bullet list; that file was audited at
  three prose citations while four bullets in it went unchecked.

A third instance is the sharpest: the map added to close the "bump the pin and accept an
unaudited domain" hole for two other maps **had the hole itself** — the layer keyed off its
diagram stems and never compared its domain values to anything.

⭐ *A count invariant is a good backstop and a bad explanation.* It says "something left the
audit" and prompts you to raise the pin, which accepts the unaudited thing. Pair it with a
check that names what is missing. A smoke alarm is not a diagnosis.

## The sweep that was declared closed at 15 of 32

Each group was found by a different method, which is the whole lesson:

| Group | Count | How it was found |
|---|---|---|
| Domain counts | 15 | 8 Domain Overview rows + 7 `domains/*.md` headlines |
| Mermaid inventory entries | 16 | 8 diagrams × the 2 inventories in `docs/erds/README.md` and `erd-quickstart.md` |
| Prose citation | 1 | `erd-quickstart.md`'s "all 54 billing domain objects" |

The inventories carried the identical stale set (11/14/15/4/37/27/22/54) **in a file the
sweep already had open**, because they *look* like a different quantity — and are one:
entities drawn in a diagram, which is organized around relationships and need not hold the
same entities as its domain. They had been populated from the domain counts, so they drifted
with them, and two of the eight coincidentally matched their diagram, which made the other
six look deliberate. The last entry escaped even the corrected sweep: a grep for the stale
*numbers* passed over it twice because it said "objects" rather than "entities", and it
surfaced only by enumerating every line naming a `.mermaid` file.

⭐ **When sweeping a class, enumerate every instance mechanically before claiming the class
is closed.** "I fixed the ones I found" is a different claim. A near-miss quantity is where
most of the rest hide; a different *label* for the same number is where the last one does.

That rule then had to be applied to itself. Two further citations of the object total —
"covering 263 objects" and "the full 263-object schema" — survived the corrected sweep,
both naming the figure in prose the triple pattern cannot match. They were found the way the
rule prescribes: list every numeral in these documents that `erd-data.json` can justify,
subtract the ones a check already covers, read what is left. That enumeration is about ten
lines of Python and finishes in a second, whereas three consecutive review rounds each found
exactly one more instance by reading.

⭐ **Enumerate against the data, not against the phrasings you already know** — and gate the
figures a definition quotes to justify itself, which read as prose and so escape the count
checks entirely.

## The shape no count check can gate

⭐ **A qualitative claim about the data is a citation too.** The note explaining *why* the
diagram inventories are gated separately asserted that most diagrams "draw well under half
their domain." Checked against the very counts the change had just established: only two of
nine are below half, four match their domain exactly, and one exceeds it. The claim was
invented to justify the layer, was false the day it was written, and had been copied to five
sites — while checks were being added for the numbers next to it. "Subset" was wrong for the
same reason, since one diagram is not a subset of its domain at all.

Prefer wording the data cannot contradict — "may draw fewer, all, or one more" — over a
ratio or a "most". A summary statistic in prose carries all the drift risk of a number and
none of the gateability. When a rationale genuinely needs a quantity, compute it and let a
check hold it.

## Carry-outs for the next check you write

1. Assert **per site**, never in aggregate; a missing file must fail, not `continue`.
2. **Pin the total check count**, and pair it with checks that name what is absent.
3. Compare against the **data**, never against a constant in the same file.
4. When a guard returns a sentinel instead of raising, **check every consumer** — otherwise
   the crash simply moves downstream.
5. Gate the figures your *rationale* quotes, and keep unquantified claims unquantified.
