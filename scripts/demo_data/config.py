"""Config spec load / validate / merge for the demo data generator.

A run is described by a list of :class:`ScenarioSpec` -- each spec is one
account/product shape repeated ``count`` times. With no config file the tool
synthesizes a single spec from CLI flags + built-in defaults, so it runs against
a fresh org with zero configuration; a ``--config`` file lets one run mix several
shapes (e.g. billable Infinitech ``post`` orders + Global Media ``quote``-only
pipeline data).

Specs here are *un-resolved*: they carry account *names* and product *SKUs*, not
org ids. ``generate.py`` resolves them against discovery so this module stays a
pure parse/validate/merge layer with no org dependency.

Precedence (most specific wins):

    per-scenario field  >  CLI flag  >  config ``defaults``  >  built-in default

CLI flags override the broad ``defaults`` block; an explicit per-scenario value
is the most specific intent and wins over everything. ``--with-opportunity`` is a
store_true flag, so it can only *enable* (never force-disable) -- pin
``with_opportunity: false`` per scenario in config to opt a scenario out.
"""

from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass
from typing import Any, Optional

log = logging.getLogger("demo_data.config")

# Built-in defaults (lowest precedence). target_stage caps/resolution happen in
# generate.py against the resolved account -- this is just the requested stage.
_BUILTIN_DEFAULTS: dict[str, Any] = {
    "target_stage": "post",
    "with_opportunity": False,
    "opportunity_stage": None,
    "account": None,
    "product": None,
    "quantity": 1,
    "count": 1,
}

_VALID_STAGES = {"opportunity", "quote", "order", "activate", "invoice", "post"}


class ConfigError(RuntimeError):
    """The config file is malformed or contains an invalid value."""


@dataclass
class ScenarioSpec:
    """One un-resolved transaction shape, run ``count`` times.

    ``account`` / ``product_sku`` are ``None`` => auto-discover (default
    billing-ready account / preferred QB product).
    """

    account: Optional[str]
    product_sku: Optional[str]
    target_stage: str
    with_opportunity: bool
    opportunity_stage: Optional[str]
    quantity: int
    count: int


def _load_file(path: str) -> dict:
    if not os.path.exists(path):
        raise ConfigError(f"config file not found: {path}")
    with open(path) as f:
        text = f.read()
    # JSON is a YAML subset; PyYAML parses both, but only import it when needed.
    try:
        import yaml
    except ImportError as exc:  # pragma: no cover - yaml is a hard dep in practice
        raise ConfigError(
            "PyYAML is required to read --config files (pip install pyyaml)"
        ) from exc
    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        raise ConfigError(f"could not parse config {path}: {exc}") from exc
    if data is None:
        return {}
    if not isinstance(data, dict):
        raise ConfigError(f"config {path} must be a mapping at the top level")
    return data


def _cli_overrides(args: Any) -> dict[str, Any]:
    """Pick the CLI flags the user explicitly set (None == not set).

    ``with_opportunity`` is store_true: only a True value is treated as an
    override (a flag can't express "force false").
    """
    overrides: dict[str, Any] = {}
    if getattr(args, "target_stage", None) is not None:
        overrides["target_stage"] = args.target_stage
    if getattr(args, "account", None) is not None:
        overrides["account"] = args.account
    if getattr(args, "product", None) is not None:
        overrides["product"] = args.product
    if getattr(args, "opportunity_stage", None) is not None:
        overrides["opportunity_stage"] = args.opportunity_stage
    if getattr(args, "count", None) is not None:
        overrides["count"] = args.count
    if getattr(args, "with_opportunity", False):
        overrides["with_opportunity"] = True
    return overrides


def _coerce_spec(merged: dict[str, Any], where: str) -> ScenarioSpec:
    stage = merged.get("target_stage") or "post"
    if stage not in _VALID_STAGES:
        raise ConfigError(
            f"{where}: invalid target_stage '{stage}' "
            f"(valid: {', '.join(sorted(_VALID_STAGES))})"
        )

    # A scenario may carry either `product: "SKU"` or a `products:` list; we
    # place a single line per quote today, so take the first and warn on extras.
    product_sku = merged.get("product")
    quantity = merged.get("quantity", 1)
    products = merged.get("products")
    if products:
        if not isinstance(products, list):
            raise ConfigError(f"{where}: 'products' must be a list")
        first = products[0]
        if not isinstance(first, dict) or not first.get("sku"):
            raise ConfigError(f"{where}: each product needs an 'sku'")
        product_sku = first["sku"]
        quantity = first.get("quantity", quantity)
        if len(products) > 1:
            log.warning(
                "%s: %d products listed but only the first (%s) is placed "
                "(multi-line orders are not yet supported); the rest are ignored",
                where, len(products), product_sku,
            )

    try:
        count = int(merged.get("count", 1))
        quantity = int(quantity)
    except (TypeError, ValueError) as exc:
        raise ConfigError(f"{where}: count/quantity must be integers") from exc
    if count < 1:
        raise ConfigError(f"{where}: count must be >= 1 (got {count})")
    if quantity < 1:
        raise ConfigError(f"{where}: quantity must be >= 1 (got {quantity})")

    return ScenarioSpec(
        account=merged.get("account"),
        product_sku=product_sku,
        target_stage=stage,
        with_opportunity=bool(merged.get("with_opportunity", False)),
        opportunity_stage=merged.get("opportunity_stage"),
        quantity=quantity,
        count=count,
    )


def load_scenarios(args: Any) -> list[ScenarioSpec]:
    """Resolve the run into a list of un-resolved scenario specs.

    No ``--config`` -> one spec from CLI flags + built-ins. With ``--config``,
    each entry under ``scenarios:`` becomes a spec (layered defaults < config
    ``defaults`` < CLI < per-scenario); a config with no ``scenarios:`` yields a
    single spec from the merged defaults, honoring ``volume.scenarios`` as count.
    """
    cli = _cli_overrides(args)
    config_path = getattr(args, "config", None)

    if not config_path:
        merged = {**_BUILTIN_DEFAULTS, **cli}
        return [_coerce_spec(merged, "cli")]

    data = _load_file(config_path)
    config_defaults = data.get("defaults") or {}
    if not isinstance(config_defaults, dict):
        raise ConfigError("config 'defaults' must be a mapping")
    base = {**_BUILTIN_DEFAULTS, **config_defaults, **cli}

    scenarios = data.get("scenarios")
    if scenarios is None:
        # No explicit scenarios: one merged spec; volume.scenarios sets count
        # unless CLI --count overrode it.
        volume = data.get("volume") or {}
        if "count" not in cli and isinstance(volume, dict) and volume.get("scenarios"):
            base = {**base, "count": volume["scenarios"]}
        return [_coerce_spec(base, "defaults")]

    if not isinstance(scenarios, list) or not scenarios:
        raise ConfigError("config 'scenarios' must be a non-empty list")
    specs: list[ScenarioSpec] = []
    for i, raw in enumerate(scenarios):
        if not isinstance(raw, dict):
            raise ConfigError(f"scenarios[{i}] must be a mapping")
        # Per-scenario fields win over CLI/defaults, EXCEPT account/product which
        # a CLI override should not silently rewrite across a multi-account
        # config; only let CLI override those when the scenario didn't pin them.
        merged = {**base, **raw}
        specs.append(_coerce_spec(merged, f"scenarios[{i}]"))
    return specs
