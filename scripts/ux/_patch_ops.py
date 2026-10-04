"""
Flexipage patch types — one entry per type in ``FLEXIPAGE_OPS``.

Each patch type in ``templates/flexipages/patches/<feature>/<Page>.yml`` has
four operations, kept side by side so a new type cannot be half-supported:

  apply    (root, patch, logger)                 assembly: add the patch to a page
  reverse  (root, patch, template_root, logger)  writeback: take it out of an org page;
                                                 returns REMOVED, ABSENT or FAILED
  describe (patch) -> str                        manifest text
  refresh  (patch, page) -> patch or None        writeback: re-derive the patch from
                                                 the org page; None drops it

``template_root`` is the page's current template. ``page`` is a ``PagePair`` of
the regenerated template and the org page.
"""
import copy
import re
import xml.etree.ElementTree as ET
from typing import Any, Callable, Dict, Iterable, List, NamedTuple, Optional, Set

from scripts.ux._flags import SALES_TXN_LINE_EDITOR_IDENTIFIER
from scripts.ux._xml import (
    SF_NS_TAG,
    child_text,
    component_value_list,
    find_elem,
    findall_elem,
    item_value,
    list_values,
    local_tag,
    make_elem,
    make_value_item,
    normalize_xml,
    parse_fragment,
    remove_values,
    sub_elem,
    value_items,
    value_lists,
)

#: Results of a reverse operation.
REMOVED = "removed"   # element found and removed
ABSENT = "absent"     # already absent (idempotent success)
FAILED = "failed"     # reverse could not be applied

Patch = Dict[str, Any]


class PagePair(NamedTuple):
    """A page's regenerated template and its org state, as trees and indented text."""
    base_root: ET.Element
    org_root: ET.Element
    base_text: str
    org_text: str


class PatchOp(NamedTuple):
    apply: Callable[[ET.Element, Patch, Any], None]
    reverse: Callable[[ET.Element, Patch, Optional[ET.Element], Any], str]
    describe: Callable[[Patch], str]
    refresh: Callable[[Patch, PagePair], Optional[Patch]]


def _found(removed: bool) -> str:
    return REMOVED if removed else ABSENT


def _action_name(action: Any) -> str:
    """An insert_action entry is either a bare action name (str) or a dict with
    a 'name' key plus optional 'visibility' criteria."""
    if isinstance(action, dict):
        return action.get("name", "")
    return action


def _patch_field_values(patch: Patch) -> List[str]:
    """Normalize a patch that accepts either `field` or `fields`."""
    fields = patch.get("fields")
    if fields:
        return [field for field in fields if field]
    field = patch.get("field")
    return [field] if field else []


def _all_values(root: ET.Element, prop_name: str) -> List[str]:
    return [v for vlist in value_lists(root, prop_name) for v in list_values(vlist)]


# ---------------------------------------------------------------------------
# remove_action
# ---------------------------------------------------------------------------


def _apply_remove_action(root: ET.Element, patch: Patch, logger) -> None:
    action = patch.get("action")
    if not action:
        logger.warning(f"remove_action patch missing 'action': {patch}")
        return
    for vlist in value_lists(root, "actionNames"):
        for item in value_items(vlist):
            if item_value(item) == action:
                vlist.remove(item)
                return
    if not patch.get("ignore_missing", False):
        logger.warning(f"remove_action: action '{action}' not found in flexipage")


def _remove_action_lists(template_root: ET.Element, root: ET.Element, action: str):
    """The actionNames lists a remove_action patch touched, as ``(t_list, org_list)``.

    ``t_list`` is the first template list holding ``action``, the one the forward
    patch removed it from. ``org_list`` is the org list that shares the most
    other actions with it; a tie goes to the list at the same position, and is
    otherwise ambiguous (None). Action names repeat across lists (``New`` is on
    many), so the org list must be matched rather than searched for the name.
    """
    t_lists = list(value_lists(template_root, "actionNames"))
    t_index = next((i for i, v in enumerate(t_lists) if action in list_values(v)), None)
    if t_index is None:
        return None, None
    t_list = t_lists[t_index]
    others = set(list_values(t_list)) - {action}
    org_lists = list(value_lists(root, "actionNames"))
    overlap = [len(others & set(list_values(v))) for v in org_lists]
    best = max(overlap, default=0)
    if not best:
        return t_list, None
    tied = [i for i, n in enumerate(overlap) if n == best]
    if len(tied) == 1:
        return t_list, org_lists[tied[0]]
    return t_list, (org_lists[t_index] if t_index in tied else None)


def _reverse_remove_action(root, patch, template_root, logger) -> str:
    """Put back the action the patch removed, copied from the template and placed
    after the nearest template action that precedes it in the matching org list."""
    action = patch.get("action")
    if not action:
        return ABSENT
    if template_root is None:
        return FAILED
    t_list, vlist = _remove_action_lists(template_root, root, action)
    if t_list is None:
        return ABSENT if action in _all_values(root, "actionNames") else FAILED
    if vlist is None:
        return FAILED
    org_items = {item_value(item): item for item in value_items(vlist)}
    if action in org_items:
        return ABSENT
    t_items = value_items(t_list)
    names = [item_value(item) for item in t_items]
    idx = names.index(action)
    anchor = next((org_items[n] for n in reversed(names[:idx]) if n in org_items), None)
    at = list(vlist).index(anchor) + 1 if anchor is not None else 0
    vlist.insert(at, copy.deepcopy(t_items[idx]))
    return REMOVED


def _refresh_remove_action(patch: Patch, page: PagePair) -> Optional[Patch]:
    """Drop the patch once the org list it removed from has the action again."""
    action = patch.get("action")
    t_list, vlist = _remove_action_lists(page.base_root, page.org_root, action)
    if t_list is None:
        return None if action in _all_values(page.org_root, "actionNames") else patch
    return None if vlist is not None and action in list_values(vlist) else patch


# ---------------------------------------------------------------------------
# insert_action
# ---------------------------------------------------------------------------


def _append_visibility_rule(item: ET.Element, criteria: List[Dict[str, Any]]) -> None:
    """Add a <visibilityRule> with one <criteria> per entry. Multiple criteria are
    ANDed (FlexiPage default with no booleanFilter). Each criteria entry is
    {field, operator, value}; field may be 'Record.X' or a full '{!Record.X}'."""
    if not criteria:
        return
    vr = sub_elem(item, "visibilityRule")
    for crit in criteria:
        field = str(crit.get("field", "")).strip()
        left = field if field.startswith("{!") else "{!" + field + "}"
        c = sub_elem(vr, "criteria")
        sub_elem(c, "leftValue", left)
        sub_elem(c, "operator", str(crit.get("operator", "EQUAL")))
        sub_elem(c, "rightValue", str(crit.get("value", "")))


def _apply_insert_action(root: ET.Element, patch: Patch, logger) -> None:
    """Insert action valueListItems immediately after the anchor action.
    Skips actions already present anywhere in the list (idempotent). Each action
    is either a bare name (str) or a dict {name, visibility:[{field,operator,value}]}."""
    anchor = patch.get("after") or patch.get("before")
    actions = patch.get("actions", [])
    if not anchor or not actions:
        logger.warning(f"insert_action patch missing 'after' or 'actions': {patch}")
        return
    for vlist in value_lists(root, "actionNames"):
        children = list(vlist)
        existing = {item_value(item) for item in children}
        for i, item in enumerate(children):
            if item_value(item) != anchor:
                continue
            offset = 0
            for action in actions:
                name = _action_name(action)
                if not name or name in existing:
                    continue  # missing name or already present, skip
                new_item = make_value_item(name)
                if isinstance(action, dict):
                    _append_visibility_rule(new_item, action.get("visibility", []))
                vlist.insert(i + 1 + offset, new_item)
                offset += 1
            return
    logger.warning(f"insert_action anchor '{anchor}' not found in flexipage")


def _insert_action_list(root: ET.Element, anchor: Optional[str], names: Iterable[str]):
    """The actionNames list an insert_action patch targets, as ``(vlist, ambiguous)``.

    That is the list holding the ``after`` anchor, as the forward patch picks it.
    If the org has dropped the anchor, it is the one list still holding any of
    ``names``; ``ambiguous`` is True when several lists hold them.
    """
    vlists = list(value_lists(root, "actionNames"))
    for vlist in vlists:
        if anchor and anchor in list_values(vlist):
            return vlist, False
    names = set(names)
    holding = [vlist for vlist in vlists if names & set(list_values(vlist))]
    if len(holding) > 1:
        return None, True
    return (holding[0] if holding else None), False


def reverse_insert_action(root: ET.Element, patch: Patch, template_root: Optional[ET.Element] = None) -> str:
    """Remove the actions an insert_action patch inserted; return REMOVED, ABSENT or FAILED.

    Mirrors the forward patch: it targets the actionNames list holding the
    ``after`` anchor and never inserts an action that list already has, so the
    template's own actions in that list are left alone. If the org dropped the
    anchor, the one list still holding the inserted actions is used.

    FAILED when several lists hold the actions, or when an inserted action the
    template lacks survives in another list (the org moved it), since writing
    the page back would then bake it into the template.
    """
    anchor = patch.get("after")
    names = {_action_name(a) for a in patch.get("actions", [])} - {""}
    owned: Set[str] = set()
    if template_root is not None:
        owned = set(_all_values(template_root, "actionNames"))
        t_list, _ = _insert_action_list(template_root, anchor, ())
        names -= set(list_values(t_list)) if t_list is not None else owned
    vlist, ambiguous = _insert_action_list(root, anchor, names)
    if ambiguous:
        return FAILED
    removed = vlist is not None and remove_values(vlist, names)
    if (names - owned) & set(_all_values(root, "actionNames")):
        return FAILED
    return _found(removed)


def _reverse_insert_action(root, patch, template_root, logger) -> str:
    return reverse_insert_action(root, patch, template_root)


def _describe_insert_action(patch: Patch) -> str:
    names = [_action_name(a) for a in patch.get("actions", [])]
    return f"insert actions: {', '.join(n for n in names if n)}"


def _criteria_key(crit: Dict[str, Any]):
    field = str(crit.get("field", "")).strip()
    left = field if field.startswith("{!") else "{!" + field + "}"
    return (left, str(crit.get("operator", "EQUAL")), str(crit.get("value", "")))


def _org_visibility(item: ET.Element) -> List[Dict[str, Any]]:
    """An action item's visibilityRule criteria, in the patch's {field, operator, value} form."""
    vr = find_elem(item, "visibilityRule")
    criteria = []
    for c in findall_elem(vr, "criteria") if vr is not None else []:
        left = child_text(c, "leftValue") or ""
        field = left[2:-1] if left.startswith("{!") and left.endswith("}") else left
        criteria.append({
            "field": field,
            "operator": child_text(c, "operator") or "EQUAL",
            "value": child_text(c, "rightValue") or "",
        })
    return criteria


def refresh_insert_action(patch: Patch, page: PagePair) -> Optional[Patch]:
    """Keep the patch actions still present in the org, with the org's visibility
    criteria. An entry stays a bare name until the org gives it criteria."""
    actions = patch.get("actions", [])
    anchor = patch.get("after")
    names = {_action_name(a) for a in actions}
    vlist, ambiguous = _insert_action_list(page.org_root, anchor, names)
    if ambiguous:
        return patch  # cannot tell which list is the patch's; diff reports the drift
    items = value_items(vlist) if vlist is not None else []
    org_items: Dict[str, ET.Element] = {item_value(item): item for item in items}
    if anchor and vlist is not None and anchor not in org_items:
        # The org dropped the anchor: re-anchor after the nearest action before
        # the first inserted one that the patch does not own.
        values = [item_value(item) for item in items]
        first = min(i for i, v in enumerate(values) if v in names)
        preceding = [v for v in values[:first] if v and v not in names]
        if not preceding:
            return patch  # nothing to anchor to; diff reports the drift
        patch = {**patch, "after": preceding[-1]}
    refreshed = []
    for action in actions:
        name = _action_name(action)
        item = org_items.get(name)
        if item is None:
            continue
        org_crit = _org_visibility(item)
        old_crit = action.get("visibility", []) if isinstance(action, dict) else []
        if [_criteria_key(c) for c in org_crit] == [_criteria_key(c) for c in old_crit]:
            refreshed.append(action)
        elif org_crit:
            refreshed.append({**(action if isinstance(action, dict) else {"name": name}),
                              "visibility": org_crit})
        else:
            refreshed.append(name)
    if refreshed == actions:
        return patch
    return {**patch, "actions": refreshed} if refreshed else None


# ---------------------------------------------------------------------------
# add_display_field
# ---------------------------------------------------------------------------


def _apply_add_display_field(root: ET.Element, patch: Patch, logger) -> None:
    """Append a display field to the displayFields valueList (idempotent)."""
    field = patch.get("field")
    if not field:
        logger.warning(f"add_display_field patch missing 'field': {patch}")
        return
    for vlist in value_lists(root, "displayFields"):
        if field not in {item_value(item) for item in value_items(vlist)}:
            vlist.append(make_value_item(field))
        return
    logger.warning("add_display_field: displayFields valueList not found")


def _reverse_add_display_field(root, patch, template_root, logger) -> str:
    """Mirrors the forward patch: the first displayFields list only, and never a
    field the template already has (the forward patch skips those)."""
    field = patch.get("field")
    if not field or (template_root is not None and field in _all_values(template_root, "displayFields")):
        return ABSENT
    vlist = next(value_lists(root, "displayFields"), None)
    removed = vlist is not None and remove_values(vlist, {field})
    if field in _all_values(root, "displayFields"):
        return FAILED  # moved to another list; writing back would bake it in
    return _found(removed)


def _refresh_add_display_field(patch: Patch, page: PagePair) -> Optional[Patch]:
    return patch if patch.get("field", "") in _all_values(page.org_root, "displayFields") else None


# ---------------------------------------------------------------------------
# add_sales_txn_line_editor_field
# ---------------------------------------------------------------------------


def _line_editor_target(patch: Patch):
    return (
        patch.get("component_identifier", SALES_TXN_LINE_EDITOR_IDENTIFIER),
        patch.get("property", "displayFields"),
    )


def _apply_add_sales_txn_line_editor_field(root: ET.Element, patch: Patch, logger) -> None:
    """Add values to the Line Editor property's valueList, skipping ones already
    present; inserted after ``after`` when given, else appended."""
    fields = _patch_field_values(patch)
    if not fields:
        logger.warning(f"add_sales_txn_line_editor_field patch missing 'field' or 'fields': {patch}")
        return
    component_identifier, prop_name = _line_editor_target(patch)
    after = patch.get("after")
    vlist = component_value_list(root, component_identifier, prop_name)
    if vlist is not None:
        children = list(vlist)
        existing = {item_value(item) for item in children}
        to_add = [f for f in fields if f not in existing]
        insert_at = len(children)
        if to_add and after:
            insert_at = next((i + 1 for i, item in enumerate(children) if item_value(item) == after), -1)
        if insert_at >= 0:
            for offset, value in enumerate(to_add):
                vlist.insert(insert_at + offset, make_value_item(value))
            return
    logger.warning(
        "add_sales_txn_line_editor_field: "
        f"{component_identifier}.{prop_name} valueList or anchor '{after}' not found"
    )


def _reverse_add_sales_txn_line_editor_field(root, patch, template_root, logger) -> str:
    target = _line_editor_target(patch)
    keep = set()
    if template_root is not None:
        t_vlist = component_value_list(template_root, *target)
        keep = set(list_values(t_vlist)) if t_vlist is not None else set()
    fields = set(_patch_field_values(patch)) - keep
    vlist = component_value_list(root, *target)
    return _found(bool(fields) and vlist is not None and remove_values(vlist, fields))


def _describe_add_sales_txn_line_editor_field(patch: Patch) -> str:
    fields = patch.get("fields") or [patch.get("field", "?")]
    prop_name = patch.get("property", "displayFields")
    return f"add Sales Transaction Line Editor {prop_name}: {', '.join(fields)}"


def _refresh_add_sales_txn_line_editor_field(patch: Patch, page: PagePair) -> Optional[Patch]:
    """Keep only patched Line Editor fields still present in the org state."""
    fields = _patch_field_values(patch)
    vlist = component_value_list(page.org_root, *_line_editor_target(patch))
    if not fields or vlist is None:
        # Component/property/valueList not found in the org state — cannot
        # determine which fields survive, so leave the patch unchanged rather
        # than dropping all of its fields (the org may use a different
        # component identifier or property name).
        return patch
    org_fields = set(list_values(vlist))
    surviving = [field for field in fields if field in org_fields]
    if surviving == fields:
        return patch
    if not surviving:
        return None
    if "fields" in patch:
        return {**patch, "fields": surviving}
    if len(surviving) == 1:
        return {**patch, "field": surviving[0]}
    updated = {k: v for k, v in patch.items() if k != "field"}
    updated["fields"] = surviving
    return updated


# ---------------------------------------------------------------------------
# add_facet_field
# ---------------------------------------------------------------------------


def _facet_regions(root: ET.Element) -> List[ET.Element]:
    return [r for r in findall_elem(root, "flexiPageRegions") if child_text(r, "type") == "Facet"]


def _field_item(item: ET.Element) -> Optional[str]:
    fi = find_elem(item, "fieldInstance")
    return child_text(fi, "fieldItem") if fi is not None else None


def get_facet_field_items(root: ET.Element) -> List[str]:
    """All fieldItem values (without 'Record.') across all Facet regions, in document order."""
    result: List[str] = []
    for region in _facet_regions(root):
        for item in findall_elem(region, "itemInstances"):
            val = _field_item(item)
            if val:
                result.append(val[len("Record."):] if val.startswith("Record.") else val)
    return result


def _make_field_instance_item(field_api_name: str) -> ET.Element:
    """Build an <itemInstances><fieldInstance>...<fieldItem>Record.FIELD</fieldItem>"""
    item = make_elem("itemInstances")
    fi = sub_elem(item, "fieldInstance")
    fip = sub_elem(fi, "fieldInstanceProperties")
    sub_elem(fip, "name", "uiBehavior")
    sub_elem(fip, "value", "none")
    sub_elem(fi, "fieldItem", f"Record.{field_api_name}")
    sub_elem(fi, "identifier", f"Record{field_api_name}Field")
    return item


def _facet_columns_uuid(regions: List[ET.Element], facet_label: str) -> Optional[str]:
    """The ``columns`` facet name of the fieldSection labelled ``facet_label``."""
    found = None
    for region in regions:
        for item in findall_elem(region, "itemInstances"):
            ci = find_elem(item, "componentInstance")
            if ci is None:
                continue
            props = {
                child_text(p, "name"): child_text(p, "value")
                for p in findall_elem(ci, "componentInstanceProperties")
                if find_elem(p, "name") is not None and find_elem(p, "value") is not None
            }
            if props.get("label") == facet_label and props.get("columns"):
                found = props["columns"]
    return found


def _insert_facet_fields(root: ET.Element, fields: List[str], after, facet_label) -> bool:
    """Insert field instances after the ``after`` field, or at the end of the
    ``facet_label`` section's columns facet. False if the anchor is missing."""
    regions = findall_elem(root, "flexiPageRegions")
    if after:
        for region in regions:
            for item in findall_elem(region, "itemInstances"):
                if _field_item(item) == f"Record.{after}":
                    at = list(region).index(item) + 1
                    for j, field in enumerate(fields):
                        region.insert(at + j, _make_field_instance_item(field))
                    return True
        return False
    if facet_label:
        target = _facet_columns_uuid(regions, facet_label)
        for region in _facet_regions(root):
            name_el = find_elem(region, "name")
            if target and name_el is not None and name_el.text == target:
                # Insert before the <name> element (which is at the end)
                at = list(region).index(name_el)
                for j, field in enumerate(fields):
                    region.insert(at + j, _make_field_instance_item(field))
                return True
    return False


def _apply_add_facet_field(root: ET.Element, patch: Patch, logger) -> None:
    """Skips fields already present in any Facet region (idempotent)."""
    fields = patch.get("fields", [])
    after = patch.get("after")
    facet_label = patch.get("facet")
    if not fields:
        logger.warning(f"add_facet_field patch missing 'fields': {patch}")
        return
    existing = set(get_facet_field_items(root))
    fields = [f for f in fields if f not in existing]
    if fields and not _insert_facet_fields(root, fields, after, facet_label):
        logger.warning(f"add_facet_field: anchor '{after or facet_label}' not found")


def _reverse_add_facet_field(root, patch, template_root, logger) -> str:
    """Mirrors the forward patch: one instance per field, preferring the region
    holding the ``after`` anchor, and never a field the template already has."""
    keep = set(get_facet_field_items(template_root)) if template_root is not None else set()
    owned = [f for f in patch.get("fields", []) if f not in keep]
    targets = {f"Record.{f}" for f in owned}
    after = f"Record.{patch.get('after')}" if patch.get("after") else None
    regions = sorted(
        _facet_regions(root),
        key=lambda r: not any(_field_item(i) == after for i in findall_elem(r, "itemInstances")),
    )
    removed_any = False
    for region in regions:
        for item in findall_elem(region, "itemInstances"):
            field = _field_item(item)
            if field in targets:
                region.remove(item)
                targets.discard(field)
                removed_any = True
    if set(owned) & set(get_facet_field_items(root)):
        return FAILED  # another copy survives; writing back would bake it in
    return _found(removed_any)


def _describe_add_facet_field(patch: Patch) -> str:
    return f"add fields to {patch.get('facet', '')}: {', '.join(patch.get('fields', []))}"


def _refresh_add_facet_field(patch: Patch, page: PagePair) -> Optional[Patch]:
    """Keep the patch fields the org has and the regenerated template lacks
    (other patches may add fields to the same facet)."""
    fields = patch.get("fields", [])
    base_fields = set(get_facet_field_items(page.base_root))
    relevant = [
        f for f in get_facet_field_items(page.org_root)
        if f not in base_fields and f in fields
    ]
    if relevant == fields:
        return patch
    return {**patch, "fields": relevant} if relevant else None


# ---------------------------------------------------------------------------
# add_component
# ---------------------------------------------------------------------------


def _component_item(item: ET.Element, identifier: str) -> bool:
    ci = find_elem(item, "componentInstance")
    return ci is not None and child_text(ci, "identifier") == identifier


def _patch_identifier(patch: Patch) -> str:
    return patch.get("identifier", patch.get("component", ""))


def _apply_add_component(root: ET.Element, patch: Patch, logger) -> None:
    """Add a componentInstance to a named region's itemInstances. Inserts before
    ``before_identifier`` if given, else after ``after_identifier`` if given,
    else after the region's last itemInstances."""
    region_name = patch.get("region")
    component_name = patch.get("component")
    if not region_name or not component_name:
        logger.warning(f"add_component patch missing 'region' or 'component': {patch}")
        return
    for region in findall_elem(root, "flexiPageRegions"):
        if child_text(region, "name") != region_name:
            continue
        items = findall_elem(region, "itemInstances")

        new_ci = make_elem("componentInstance")
        for prop_name, prop_val in patch.get("properties", {}).items():
            cip = sub_elem(new_ci, "componentInstanceProperties")
            sub_elem(cip, "name", prop_name)
            sub_elem(cip, "value", prop_val)
        sub_elem(new_ci, "componentName", component_name)
        sub_elem(new_ci, "identifier", patch.get("identifier", component_name))
        new_item = make_elem("itemInstances")
        new_item.append(new_ci)

        for key, offset in (("before_identifier", 0), ("after_identifier", 1)):
            anchor = patch.get(key)
            match = next((i for i in items if anchor and _component_item(i, anchor)), None)
            if match is not None:
                region.insert(list(region).index(match) + offset, new_item)
                return

        # Preserve metadata schema order by keeping all itemInstances contiguous
        # at the front of the region (before mode/name/type).
        children = list(region)
        insert_before = next(
            (i for i, child in enumerate(children) if local_tag(child) != "itemInstances"),
            len(children),
        )
        region.insert(insert_before, new_item)
        return
    logger.warning(f"add_component: region '{region_name}' not found")


def _reverse_add_component(root, patch, template_root, logger) -> str:
    identifier = _patch_identifier(patch)
    if not identifier:
        return REMOVED
    region_name = patch.get("region")
    removed = False
    for region in findall_elem(root, "flexiPageRegions"):
        if region_name and child_text(region, "name") != region_name:
            continue
        item = next((i for i in findall_elem(region, "itemInstances") if _component_item(i, identifier)), None)
        if item is not None:
            region.remove(item)
            removed = True
            break
    # The patch adds one copy. Any more than the template has (the org moved
    # it to another region, or duplicated it) would be written into the
    # template while the patch adds it again.
    def copies(tree):
        if tree is None:
            return 0
        return sum(1 for item in tree.iter(f"{SF_NS_TAG}itemInstances") if _component_item(item, identifier))
    if copies(root) > copies(template_root):
        return FAILED
    return _found(removed)


def _refresh_add_component(patch: Patch, page: PagePair) -> Optional[Patch]:
    """Drop the patch if the component is gone; otherwise carry the org's
    property values, when they are all plain name/value pairs the patch can hold."""
    identifier = _patch_identifier(patch)
    ci = next(
        (ci for ci in page.org_root.iter(f"{SF_NS_TAG}componentInstance")
         if child_text(ci, "identifier") == identifier),
        None,
    )
    if ci is None:
        return None
    org_props = {}
    for prop in findall_elem(ci, "componentInstanceProperties"):
        if find_elem(prop, "valueList") is not None:
            return patch  # structured property: not representable in the patch
        org_props[child_text(prop, "name")] = child_text(prop, "value") or ""
    old_props = {k: "" if v is None else str(v) for k, v in patch.get("properties", {}).items()}
    if org_props == old_props:
        return patch
    return {**patch, "properties": org_props}


# ---------------------------------------------------------------------------
# insert_after_xml (raw text insertion)
# ---------------------------------------------------------------------------


def _apply_insert_after_xml(root: ET.Element, patch: Patch, logger) -> None:
    """
    Text-based XML insertion as a fallback for structures not handled by
    the semantic patch operations. Operates on the serialized string of the
    root element and re-parses back into the root. Expensive — use sparingly.
    """
    anchor = patch.get("anchor")
    xml_fragment = patch.get("xml", "")
    if not anchor or not xml_fragment:
        logger.warning("insert_after_xml patch missing 'anchor' or 'xml'")
        return

    ET.indent(root, space="    ")
    text = ET.tostring(root, encoding="unicode")
    if anchor not in text:
        logger.warning(f"insert_after_xml anchor not found: {anchor!r}")
        return
    idx = text.index(anchor) + len(anchor)
    new_root = ET.fromstring(text[:idx] + "\n" + xml_fragment + text[idx:])
    # Replace root children with new_root children (in-place modification)
    for child in list(root):
        root.remove(child)
    for child in list(new_root):
        root.append(child)


def _identifiers(item: ET.Element) -> List[str]:
    """Identifiers of an itemInstances' componentInstance and fieldInstance."""
    found = []
    for kind in ("componentInstance", "fieldInstance"):
        el = find_elem(item, kind)
        ident = child_text(el, "identifier") if el is not None else None
        if ident:
            found.append(ident)
    return found


def _page_identifiers(root: Optional[ET.Element]) -> Set[str]:
    if root is None:
        return set()
    return {i for item in root.iter(f"{SF_NS_TAG}itemInstances") for i in _identifiers(item)}


def _reverse_insert_after_xml(root, patch, template_root, logger) -> str:
    """
    Remove elements that were added by an insert_after_xml patch.

    Parses the XML fragment from the patch, extracts identifiable elements
    (region names, component identifiers, field identifiers, action values),
    and removes matching elements from the tree.
    """
    xml_fragment = patch.get("xml", "")
    if not xml_fragment:
        return REMOVED
    try:
        wrapper = parse_fragment(xml_fragment)
    except ET.ParseError:
        logger.warning("insert_after_xml reverse: could not parse XML fragment")
        return FAILED

    removed_any = False

    # Case 1: Fragment contains flexiPageRegions — remove by <name>
    fragment_regions = findall_elem(wrapper, "flexiPageRegions")
    names = {child_text(r, "name") for r in fragment_regions} - {None, ""}
    for region in list(findall_elem(root, "flexiPageRegions")):
        if child_text(region, "name") in names:
            root.remove(region)
            removed_any = True
    # A renamed region still holds the fragment's components or fields.
    nested = {i for r in fragment_regions for item in findall_elem(r, "itemInstances") for i in _identifiers(item)}
    if nested & (_page_identifiers(root) - _page_identifiers(template_root)):
        return FAILED

    # Case 2: Fragment contains itemInstances — remove by component or field identifier
    fragment_items = findall_elem(wrapper, "itemInstances")
    identifiers = {i for item in fragment_items for i in _identifiers(item)}
    if identifiers:
        for region in findall_elem(root, "flexiPageRegions"):
            for item in list(findall_elem(region, "itemInstances")):
                if any(i in identifiers for i in _identifiers(item)):
                    region.remove(item)
                    removed_any = True

    # Case 3: Fragment holds only valueListItems — remove by value (values nested
    # in regions or items were handled above).
    if not fragment_regions and not fragment_items:
        values = set(map(item_value, findall_elem(wrapper, "valueListItems"))) - {None, ""}
        if values:
            for ci_props in root.iter(f"{SF_NS_TAG}componentInstanceProperties"):
                vlist = find_elem(ci_props, "valueList")
                if vlist is not None and remove_values(vlist, values):
                    removed_any = True

    # Case 4: any other element (e.g. a <visibilityRule> inserted after a
    # component's <identifier>) — remove a structurally identical sibling of
    # the anchor element. Anything short of that FAILS when the template had
    # the anchor: the org may have renamed the anchor or edited the element,
    # and writing the page back would keep the feature content in the base.
    handled = {"flexiPageRegions", "itemInstances", "valueListItems"}
    others = [el for el in wrapper if local_tag(el) not in handled]
    if others:
        anchor = patch.get("anchor", "")
        parents = _anchor_parents(root, anchor)
        t_parents = _anchor_parents(template_root, anchor) if template_root is not None else None
        tags = {el.tag for el in others}

        def tagged(ps):
            return sum(1 for p in ps or [] for c in p if c.tag in tags)

        if _remove_siblings(parents or [], others):
            removed_any = True
        elif _survives(root, template_root, others):
            return FAILED  # moved elsewhere unchanged
        elif not parents and t_parents:
            return FAILED  # anchor renamed or gone: the element cannot be checked
        elif tagged(parents) > tagged(t_parents):
            return FAILED  # edited in place beside the anchor

    # Not found usually means the org no longer has the inserted content.
    return _found(removed_any)


_SIMPLE_ELEMENT_RE = re.compile(r"^\s*<(\w+)>([^<]*)</\1>\s*$")


def _anchor_parents(root: ET.Element, anchor: str) -> Optional[List[ET.Element]]:
    """The parents of every element matching ``anchor``, or None if it cannot
    be located: only an anchor that is one complete simple element
    (``<tag>text</tag>``) is looked up, so nothing is matched on a guess."""
    match = _SIMPLE_ELEMENT_RE.match(anchor or "")
    if not match:
        return None
    anchor_tag, anchor_text = match.group(1), match.group(2).strip()
    return [
        parent for parent in root.iter()
        if any(local_tag(c) == anchor_tag and (c.text or "").strip() == anchor_text for c in parent)
    ]


def _remove_siblings(parents: List[ET.Element], fragment_elements: List[ET.Element]) -> bool:
    """Remove, from each of ``parents``, one child identical to each fragment element."""
    wanted = [normalize_xml(el) for el in fragment_elements]
    removed_any = False
    for parent in parents:
        children = list(parent)
        for target in wanted:
            for child in children:
                if child in parent and normalize_xml(child) == target:
                    parent.remove(child)
                    removed_any = True
                    break
    return removed_any


def _survives(root: ET.Element, template_root: Optional[ET.Element], elements: List[ET.Element]) -> bool:
    """True when the org has more copies of any of ``elements`` than the template."""
    def count(tree: Optional[ET.Element], target: ET.Element) -> int:
        if tree is None:
            return 0
        tag, wanted = target.tag, normalize_xml(target)
        return sum(1 for el in tree.iter(tag) if normalize_xml(el) == wanted)

    return any(count(root, el) > count(template_root, el) for el in elements)


def _describe_insert_after_xml(patch: Patch) -> str:
    anchor = patch.get("anchor", "")
    # Extract a recognizable identifier from the anchor
    for tag in ("identifier", "name", "value"):
        m = re.search(rf"<{tag}>(.*?)</{tag}>", anchor)
        if m:
            return f"insert XML after <{tag}>{m.group(1)}</{tag}>"
    return "insert XML block"


def _find_sync_marker(text: str, org_text: str) -> Optional[str]:
    """Find a multi-line chunk from *text* (base continuation) that uniquely
    locates where base content resumes in *org_text*.

    Strategy: walk forward through base continuation lines, accumulating a
    multi-line chunk. Once the chunk contains a unique identifier tag AND
    matches exactly once in the org text, return it.
    """
    unique_tag_re = re.compile(r"<(?:name|identifier|componentName|fieldItem)>")
    non_blank = [line for line in text.split("\n") if line.strip()]

    # Progressively longer chunks starting from the first non-blank line
    for end in range(1, len(non_blank) + 1):
        chunk = "\n".join(non_blank[:end])
        if unique_tag_re.search(chunk) and org_text.count(chunk) == 1:
            return chunk

    # Fallback: the longest chunk of up to five lines, even without a unique tag
    for end in range(min(5, len(non_blank)), 0, -1):
        chunk = "\n".join(non_blank[:end])
        if chunk.strip() and org_text.count(chunk) == 1:
            return chunk
    return None


def extract_insert_after_xml(base_text: str, org_text: str, patch: Patch) -> Optional[str]:
    """The XML the org has after the anchor that the base does not.

    The org has: anchor + patch_content + base_continuation. Find where
    base_continuation starts in the org to isolate patch_content. None when the
    anchor is missing or nothing was inserted.
    """
    anchor = patch.get("anchor", "")
    if not anchor or anchor not in org_text or anchor not in base_text:
        return None

    base_after = base_text[base_text.index(anchor) + len(anchor):]
    org_after = org_text[org_text.index(anchor) + len(anchor):]
    if not base_after.strip():
        return None

    # Generic tags like <flexiPageRegions> appear many times, so locate the
    # continuation with a multi-line chunk that matches exactly once in the org.
    sync_chunk = _find_sync_marker(base_after, org_text)
    sync_idx = org_after.find(sync_chunk) if sync_chunk else -1
    if sync_idx < 0:
        return None

    inserted = org_after[:sync_idx].strip("\n")
    return inserted + "\n" if inserted.strip() else None


def _same_xml_fragment(a: str, b: str) -> bool:
    """True when two XML fragments differ only in whitespace/indentation."""
    try:
        return normalize_xml(parse_fragment(a)) == normalize_xml(parse_fragment(b))
    except ET.ParseError:
        return a.strip() == b.strip()


def _refresh_insert_after_xml(patch: Patch, page: PagePair) -> Optional[Patch]:
    new_xml = extract_insert_after_xml(page.base_text, page.org_text, patch)
    if new_xml is None:
        return None  # inserted content absent in the org
    if _same_xml_fragment(new_xml, patch.get("xml", "")):
        return patch
    return {**patch, "xml": new_xml}


# ---------------------------------------------------------------------------
# The table
# ---------------------------------------------------------------------------


FLEXIPAGE_OPS: Dict[str, PatchOp] = {
    "remove_action": PatchOp(
        _apply_remove_action, _reverse_remove_action,
        lambda p: f"remove action: {p.get('action', '?')}", _refresh_remove_action,
    ),
    "insert_action": PatchOp(
        _apply_insert_action, _reverse_insert_action,
        _describe_insert_action, refresh_insert_action,
    ),
    "add_display_field": PatchOp(
        _apply_add_display_field, _reverse_add_display_field,
        lambda p: f"add display field: {p.get('field', '?')}", _refresh_add_display_field,
    ),
    "add_sales_txn_line_editor_field": PatchOp(
        _apply_add_sales_txn_line_editor_field, _reverse_add_sales_txn_line_editor_field,
        _describe_add_sales_txn_line_editor_field, _refresh_add_sales_txn_line_editor_field,
    ),
    "add_facet_field": PatchOp(
        _apply_add_facet_field, _reverse_add_facet_field,
        _describe_add_facet_field, _refresh_add_facet_field,
    ),
    "add_component": PatchOp(
        _apply_add_component, _reverse_add_component,
        lambda p: f"add component: {p.get('component', '?')}", _refresh_add_component,
    ),
    "insert_after_xml": PatchOp(
        _apply_insert_after_xml, _reverse_insert_after_xml,
        _describe_insert_after_xml, _refresh_insert_after_xml,
    ),
}


def apply_patch(root: ET.Element, patch: Patch, logger) -> None:
    op = FLEXIPAGE_OPS.get(patch.get("type"))
    if op is None:
        logger.warning(f"Unknown patch type '{patch.get('type')}': {patch}")
        return
    op.apply(root, patch, logger)


def reverse_patch(root: ET.Element, patch: Patch, template_root: Optional[ET.Element], logger) -> str:
    op = FLEXIPAGE_OPS.get(patch.get("type"))
    if op is None:
        logger.warning(f"Unknown patch type for reverse: '{patch.get('type')}'")
        return FAILED
    return op.reverse(root, patch, template_root, logger)


def describe_patch(patch: Patch) -> str:
    """Short human-readable description of a patch for manifests."""
    op = FLEXIPAGE_OPS.get(patch.get("type"))
    return op.describe(patch) if op else patch.get("type", "")


def refresh_patch(patch: Patch, page: PagePair) -> Optional[Patch]:
    """The patch re-derived from the org page; None when the org no longer has it."""
    op = FLEXIPAGE_OPS.get(patch.get("type"))
    return op.refresh(patch, page) if op else patch
