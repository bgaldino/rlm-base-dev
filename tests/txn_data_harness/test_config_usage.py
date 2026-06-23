"""Tests for the usage: block in scenario config."""

from __future__ import annotations

import argparse

import pytest

from scripts.txn_data_harness.config import ConfigError, load_scenarios


def _args(**overrides) -> argparse.Namespace:
    defaults = {
        "config": None,
        "target_stage": None,
        "account": None,
        "product": None,
        "opportunity_stage": None,
        "count": None,
        "with_opportunity": False,
    }
    defaults.update(overrides)
    return argparse.Namespace(**defaults)


def _write(tmp_path, text: str) -> str:
    path = tmp_path / "scenario.yaml"
    path.write_text(text, encoding="utf-8")
    return str(path)


def test_usage_block_parses_minimum_fields(tmp_path) -> None:
    config = _write(
        tmp_path,
        """
scenarios:
  - target_stage: usage
    products:
      - sku: QB-DB
        usage:
          quantity: [100, 500]
          records_per_line: [5, 10]
""",
    )
    spec = load_scenarios(_args(config=config))[0]
    opt = spec.products[0]
    assert opt.usage is not None
    assert opt.usage.quantity == (100.0, 500.0)
    assert opt.usage.records_per_line == (5, 10)
    assert opt.usage.days_back == 0
    assert opt.usage.resource is None
    assert opt.usage.unit_of_measure is None


def test_usage_block_accepts_scalar_quantity_and_records(tmp_path) -> None:
    config = _write(
        tmp_path,
        """
scenarios:
  - products:
      - sku: QB-DB
        usage:
          quantity: 250
          records_per_line: 3
          days_back: 14
          resource: UR-CPUTIME
          unit_of_measure: hr
""",
    )
    spec = load_scenarios(_args(config=config))[0]
    opt = spec.products[0]
    assert opt.usage.quantity == (250.0, 250.0)
    assert opt.usage.records_per_line == (3, 3)
    assert opt.usage.days_back == 14
    assert opt.usage.resource == "UR-CPUTIME"
    assert opt.usage.unit_of_measure == "hr"


def test_usage_block_requires_quantity(tmp_path) -> None:
    config = _write(
        tmp_path,
        """
scenarios:
  - products:
      - sku: QB-DB
        usage:
          records_per_line: 5
""",
    )
    with pytest.raises(ConfigError, match="usage requires 'quantity'"):
        load_scenarios(_args(config=config))


def test_usage_block_requires_records_per_line(tmp_path) -> None:
    config = _write(
        tmp_path,
        """
scenarios:
  - products:
      - sku: QB-DB
        usage:
          quantity: 100
""",
    )
    with pytest.raises(ConfigError, match="records_per_line"):
        load_scenarios(_args(config=config))


def test_usage_unit_of_measure_without_resource_rejected(tmp_path) -> None:
    config = _write(
        tmp_path,
        """
scenarios:
  - products:
      - sku: QB-DB
        usage:
          quantity: 100
          records_per_line: 5
          unit_of_measure: TB
""",
    )
    with pytest.raises(ConfigError, match="unit_of_measure requires"):
        load_scenarios(_args(config=config))


def test_usage_days_back_must_be_non_negative(tmp_path) -> None:
    config = _write(
        tmp_path,
        """
scenarios:
  - products:
      - sku: QB-DB
        usage:
          quantity: 100
          records_per_line: 5
          days_back: -1
""",
    )
    with pytest.raises(ConfigError, match="days_back must be >= 0"):
        load_scenarios(_args(config=config))


def test_usage_target_stage_recognised(tmp_path) -> None:
    config = _write(
        tmp_path,
        """
scenarios:
  - target_stage: usage
    products:
      - sku: QB-DB
""",
    )
    spec = load_scenarios(_args(config=config))[0]
    assert spec.target_stage == "usage"
