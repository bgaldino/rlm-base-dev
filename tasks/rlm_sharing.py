"""Custom CumulusCI sharing tasks for Revenue Cloud Base Foundations.

Two tasks that make Org-Wide Default management safe and reproducible across org
shapes (TSO vs non-TSO) without the duplicate-listView side effect of the stock
``SetOrgWideDefaults`` task:

* ``SetOrgWideDefaultsSharingOnly`` — sets OWD by deploying ONLY the sharing
  elements (no listViews), and skips objects that don't exist on the target org.
* ``AssertSObjectOWDs`` — verifies OWD landed and raises if not (the stock
  ``CheckSObjectOWDs`` only returns true/false for MetaDeploy preflight gating).
"""
from cumulusci.core.exceptions import CumulusCIException
from cumulusci.tasks.metadata_etl.sharing import SetOrgWideDefaults
from cumulusci.tasks.preflight.sobjects import CheckSObjectOWDs


class SetOrgWideDefaultsSharingOnly(SetOrgWideDefaults):
    """``SetOrgWideDefaults`` that deploys ONLY the sharing elements and tolerates
    objects that are absent on the target org.

    Two differences from the stock task:

    1. **Sharing-only deploy.** Stock ``SetOrgWideDefaults`` retrieves each
       ``CustomObject`` in full and redeploys it — listViews included. On a
       *standard* object the platform cannot update its system listView via the
       Metadata API, so the redeploy creates a duplicate user-owned copy. That
       breaks the next run with ``Duplicate name 'X.All_...' specified`` and
       pollutes the org with extra "All X" list views (non-idempotent + UI
       clutter; the duplicates can't be removed via the API). We strip every
       child except ``sharingModel`` / ``externalSharingModel`` before deploy, so
       the deploy updates only the OWD. A Metadata API ``CustomObject`` deploy
       merges sub-components, so omitting listViews/fields leaves them untouched.

    2. **Shape tolerance.** Some configuration-model objects may not exist on
       every org shape (e.g. a non-TSO build). The stock task raises
       "Cannot find metadata file" when a requested object isn't retrieved. We
       prune the requested objects to those present in the org (via
       EntityDefinition) before retrieve, skipping the rest with a warning, so the
       same ``org_wide_defaults`` config works on any shape.

    Accepts the same ``org_wide_defaults`` YAML config as the stock task.
    """

    _SHARING_TAGS = {"sharingModel", "externalSharingModel"}

    def _retrieve(self):
        self._prune_to_existing_objects()
        if not self.api_names:
            self.logger.warning(
                "None of the requested Org-Wide Default objects exist on this org; "
                "nothing to set."
            )
            return
        super()._retrieve()

    def _prune_to_existing_objects(self):
        """Drop requested objects that don't exist on this org (shape difference)."""
        requested = sorted(self.owds.keys())
        if not requested:
            # No Org-Wide Defaults requested: clear api_names so _retrieve()
            # short-circuits gracefully instead of building an invalid
            # `WHERE QualifiedApiName IN ()` SOQL clause.
            self.api_names = set()
            return
        object_list = ", ".join(f"'{obj}'" for obj in requested)
        existing = {
            rec["QualifiedApiName"]
            for rec in self.sf.query(
                "SELECT QualifiedApiName FROM EntityDefinition "
                f"WHERE QualifiedApiName IN ({object_list})"
            )["records"]
        }
        missing = [obj for obj in requested if obj not in existing]
        if missing:
            self.logger.warning(
                "Skipping Org-Wide Defaults for objects not present on this org "
                f"shape: {', '.join(missing)}"
            )
        self.owds = {k: v for k, v in self.owds.items() if k in existing}
        self.api_names = {a for a in self.api_names if a in existing}

    def _transform_entity(self, metadata, api_name):
        metadata = super()._transform_entity(metadata, api_name)
        # Remove all non-sharing children so the redeploy never re-creates system
        # listViews (the 262 "Duplicate name" quirk). tag is namespaced
        # (e.g. "{http://soap.sforce.com/2006/04/metadata}listViews").
        for child in list(metadata._element):
            if child.tag.split("}")[-1] not in self._SHARING_TAGS:
                metadata._element.remove(child)
        return metadata


class AssertSObjectOWDs(CheckSObjectOWDs):
    """``CheckSObjectOWDs`` that RAISES when OWD doesn't match the expected spec.

    The stock task only sets ``return_values`` (true/false) for use as a MetaDeploy
    preflight gate; in a regular flow it would silently pass. This subclass turns a
    mismatch into a hard error so it can be used as a post-set verification step.

    Objects absent from the org are not returned by the EntityDefinition query and
    are therefore not checked — matching ``SetOrgWideDefaultsSharingOnly``'s shape
    tolerance (we only verify objects that exist).
    """

    def _run_task(self):
        super()._run_task()
        if not self.return_values:
            raise CumulusCIException(
                "Org-Wide Defaults verification failed: one or more present objects "
                "do not match the expected internal/external sharing model. Review "
                "the EntityDefinition query results above."
            )
        self.logger.info("Org-Wide Defaults verification passed.")
