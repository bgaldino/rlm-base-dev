# Multi-version orgs

Progressive-disclosure sub-file of `.cursor/skills/expression-sets/SKILL.md`. Which version executes, and how the tools edit, re-rank, overlay, import and deploy on a set with several versions.

## <a name="multi-version-orgs"></a>Multi-version orgs

An expression set can hold several versions, several of them **active at once**,
and the runtime runs one: the **highest Rank** among enabled versions whose start/end
windows cover the call's effective date [Dev guide:
`sforce_api_objects_expressionsetversion`] [Measured: 2026-11-24, 264, QB scratch
build, disposable sets], and among null Ranks the **earliest created** [Measured:
2026-11-25, 264, QB scratch build, disposable sets]. Equal numeric Ranks cannot be
set up by deploy ("Assign a unique rank to expression set version …") [Measured:
2026-11-24, 264, QB scratch build, disposable sets]. [Open: which version runs when
two active versions share a numeric Rank; settle it by setting an inactive
version's Rank equal to the active one's with an sObject update, activating it and
invoking the set, or record that the activation is refused.] The tools resolve it
with `scripts/expression_sets/_guards.executing_version`, using now as the date. An
upgraded org can carry `RLM_DefaultPricingProcedure` as such a chain: v1 to v4, v1,
v3 and v4 active, v4 executing, with the ramp-uplift child named `Uplift` in v1 to v3
and `CompoundUplift` in v4 [Measured: 2026-09-03, 264, upgraded org]. Before any
edit, list the versions:
`SELECT ApiName, VersionNumber, IsActive, Rank, StartDateTime, EndDateTime FROM ExpressionSetVersion WHERE ExpressionSetId = '<9QL>'`.

- **Edit the executing version.** A constant written into a lower version changed no
  price; written into the executing one it changed every price [Measured: 2026-09-03,
  264, upgraded org]. Use
  `set_step_formula.py`: it targets the executing version unless
  `--version-api-name` names another (and warns then), selects the step by `--step`
  or by its version-stable `--parent-step`, runs the deactivate → Tooling
  `Metadata` PATCH → reactivate lifecycle (reactivating even if the PATCH fails,
  since a Tooling sObject update is atomic), and exits 1 when the read-back formula,
  the version state or any referencing `ProcedurePlanDefinitionVersion.IsActive`
  differs from what it should be.
- **A version with no Rank cannot be cycled.** The API refuses to activate a version
  without a Rank ("Enter a valid rank to enable …") [Measured: 2026-11-25, 264, QB
  scratch build, disposable sets], so the toolkit mutators with activation on
  (`set_step_formula`, relabel, import, overlay), `activate_expression_set --activate`,
  the whole-set delete (its rollback reactivates) and the CCI import, overlay and
  delete tasks refuse a null-Rank version before any write. Give it a Rank first, or
  run without activation. The CCI `ManageExpressionSets` tasks
  (`activate_expression_sets`, `activate_prm_expression_sets`,
  `activate_procedure_plan_expression_sets`, `manage_expression_sets`
  `activate_version(s)`) do not pre-check: they only set the status, so a null-Rank
  version fails at the platform's refusal with nothing else written for it. An
  sObject update of `Rank` works on an inactive version; an active one refuses every
  update ("An enabled Expression Set Version cannot be
  updated/deleted."), so deactivate it without cascading, set a numeric Rank (higher
  than every other active version's if it should execute; equal Ranks are refused)
  and activate it again without cascading [Measured: 2026-11-25, 264, QB scratch
  build, disposable sets].
- **An overlay sends every version.** `apply_expression_set_overlay` PATCHes the
  whole GET, which succeeded when the versions carried their own labels and was
  rejected on a version-name collision when the GET returned one name for both; an
  sObject update of `Name` does not change the name the GET returns [Measured:
  2026-11-25, 264, QB scratch build, disposable sets]. Both surfaces refuse that
  before any write, and refuse while any version other than the executing one is
  active, since the run deactivates only that one. [Open: whether a PATCH that
  rewrites an active version is accepted; settle it with an overlay on a disposable
  set with two active own-label versions, guard bypassed.] With no version named,
  the overlay edits the executing version.
- **A whole-set import works in one shape only.** On a multi-version set both
  `import_expression_set` surfaces allow only a payload with exactly one version,
  the one the import targets, and no other version sharing its label; everything
  else is refused before any write. Two-version payloads failed (named alike:
  version-name collision; target first with the other version renamed in the
  payload: duplicate `CalculationProcedureId`) [Measured: 2026-11-24, 264, QB scratch
  build, disposable sets], and a one-version payload failed whenever another
  version's `Name` equalled its label and succeeded otherwise, including on versions
  deployed with their own labels [Measured: 2026-11-25, 264, QB scratch build,
  disposable sets]. [Open: the platform's answer to a two-version payload on
  versions with their own labels; the guard refuses it first, so settle it with a
  raw Connect PATCH on a disposable set.] Platform version chains share one label.
- **A deploy is read back.** `activate_and_deploy_expression_sets` fails when a
  deployed repo version is missing, sits under a different `VersionNumber` than the
  package, is inactive, or is not the version that executes. The deploy handler
  matches versions by number, and its code path suggests such a version can be
  skipped silently [Platform behaviour, traced]; the one construction measured (lower
  version deleted, `_V1` redeployed at the freed number) failed the deploy loudly
  instead [Measured: 2026-11-24, 264, QB scratch build, disposable sets]. The
  read-back reports any mismatch either way. When it fails, the deploy is already
  applied and the step cannot be re-run on a built org (the redeploy is refused:
  "You can't update the expression set version … because it's active") [Measured:
  2026-11-24, 264, QB scratch build]: run the build's remaining steps after it, in
  order (`cci flow info prepare_rlm_org` lists them; a build-harness `resume` restarts
  at the failed step, so it would re-run it) and, if the wrong version executes, edit
  or re-rank the executing version (`set_step_formula.py` for formulas). For future
  builds on an org whose chain is known, set the check to warn: `-o version_check
  warn` on `cci task run activate_and_deploy_expression_sets`, or `-o
  activate_and_deploy_expression_sets__version_check warn` on `cci flow run
  prepare_rlm_org`. The read-back is not a way to audit a built org. Toolkit detail:
  `scripts/expression_sets/README.md` → *Multi-version expression sets*.
