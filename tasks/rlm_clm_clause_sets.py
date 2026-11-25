"""Load the qb-clm DocumentClauseSet rows with a portable `Category`.

`DocumentClauseSet.Category` is a required, restricted picklist whose values are the 15
character Ids of the org's ClauseCatgConfiguration records (`CategoryReferenceId` is read
only). No SFDMU CSV can carry an Id that differs per org, so the plan's export.json leaves
DocumentClauseSet out and this task inserts the CSV's rows after `insert_clm_data` has
loaded the categories. Rows already on the org (same Name and category) are left alone, so
a rerun adds nothing. `Status` is not writable (a clause set is created in Draft).
"""

import csv
import os

try:
    from cumulusci.core.exceptions import CommandException, TaskOptionsError
    from cumulusci.tasks.salesforce import BaseSalesforceApiTask
except ImportError:
    BaseSalesforceApiTask = object  # type: ignore
    CommandException = Exception  # type: ignore
    TaskOptionsError = Exception  # type: ignore

DEFAULT_CSV = "datasets/sfdmu/qb/en-US/qb-clm/DocumentClauseSet.csv"
CATEGORY_COLUMN = "CategoryReference.DeveloperName"


def category_value(record_id: str) -> str:
    """The picklist value for a ClauseCatgConfiguration record: its 15 character Id.

    Also the form `Category` is compared in: a query may return either length, so both sides
    of an existence check go through here."""
    return str(record_id or "")[:15]


def plan_rows(csv_path: str) -> list:
    """The CSV's (Name, category DeveloperName, DefaultLanguage) rows."""
    return [row[:3] for row in plan_rows_with_status(csv_path)]


def plan_rows_with_status(csv_path: str) -> list:
    """The CSV's (Name, category DeveloperName, DefaultLanguage, Status) rows."""
    with open(csv_path, newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.DictReader(handle))
    for column in ("Name", CATEGORY_COLUMN, "DefaultLanguage"):
        if rows and column not in rows[0]:
            raise TaskOptionsError(f"{csv_path}: missing column {column}")
    return [(r["Name"], r[CATEGORY_COLUMN], r["DefaultLanguage"], r.get("Status", "")) for r in rows]


def ignored_status_count(rows: list) -> int:
    """How many rows ask for a Status other than Draft, which the platform ignores."""
    return sum(1 for row in rows if len(row) > 3 and row[3] not in ("", "Draft"))


def missing_rows(rows: list, categories: dict, existing: set) -> list:
    """The rows to insert, as field dicts. A category absent from `categories` raises."""
    existing = {(name, category_value(value)) for name, value in existing}
    out = []
    for name, category, language in rows:
        if category not in categories:
            raise CommandException(
                f"DocumentClauseSet {name!r}: no ClauseCatgConfiguration with DeveloperName "
                f"{category!r} on the org (load qb-clm first)")
        value = category_value(categories[category])
        if (name, value) in existing:
            continue
        out.append({"Name": name, "DefaultLanguage": language, "Category": value})
    return out


class LoadClmClauseSets(BaseSalesforceApiTask):
    """Insert the qb-clm DocumentClauseSet rows, resolving Category to the org's category Ids."""

    task_options = {
        "csv": {
            "description": f"Clause set CSV (default {DEFAULT_CSV}).",
            "required": False,
        },
    }

    def _run_task(self):
        path = self.options.get("csv") or DEFAULT_CSV
        if not os.path.isabs(path):
            path = os.path.join(self.project_config.repo_root, path)
        full_rows = plan_rows_with_status(path)
        rows = [row[:3] for row in full_rows]
        ignored = ignored_status_count(full_rows)
        if ignored:
            self.logger.warning(
                f"{ignored} of {len(rows)} DocumentClauseSet row(s) in the CSV ask for a Status other "
                "than Draft; Status is not writable, so every clause set loads as Draft.")
        categories = {
            r["DeveloperName"]: r["Id"]
            for r in self.sf.query_all("SELECT Id, DeveloperName FROM ClauseCatgConfiguration")["records"]
        }
        existing = {
            (r["Name"], r["Category"])
            for r in self.sf.query_all("SELECT Name, Category FROM DocumentClauseSet")["records"]
        }
        todo = missing_rows(rows, categories, existing)
        failed = []
        for fields in todo:
            try:
                self.sf.DocumentClauseSet.create(fields)
            except Exception as exc:  # one rejected row should not hide the rest
                failed.append(f"{fields['Name']}: {exc}")
        self.logger.info(
            f"DocumentClauseSet: {len(rows)} in CSV, {len(rows) - len(todo)} already on the org, "
            f"{len(todo) - len(failed)} inserted")
        if failed:
            raise CommandException("DocumentClauseSet rows rejected:\n" + "\n".join(failed))
