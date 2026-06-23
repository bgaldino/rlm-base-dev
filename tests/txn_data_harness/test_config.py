"""Tests for scripts.txn_data_harness.config."""

from __future__ import annotations

import argparse
from datetime import date

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


def _write_yaml(tmp_path, text: str) -> str:
    path = tmp_path / "scenario.yaml"
    path.write_text(text, encoding="utf-8")
    return str(path)


class TestStartDate:
    def test_accepts_exact_start_date(self, tmp_path) -> None:
        config = _write_yaml(
            tmp_path,
            """
scenarios:
  - start_date: "2026-03-15"
""",
        )
        spec = load_scenarios(_args(config=config))[0]
        assert spec.start_date == (date(2026, 3, 15), date(2026, 3, 15))

    def test_accepts_range_list(self, tmp_path) -> None:
        config = _write_yaml(
            tmp_path,
            """
scenarios:
  - start_date: ["2026-01-01", "2026-03-31"]
""",
        )
        spec = load_scenarios(_args(config=config))[0]
        assert spec.start_date == (date(2026, 1, 1), date(2026, 3, 31))

    def test_accepts_window_map(self, tmp_path) -> None:
        config = _write_yaml(
            tmp_path,
            """
scenarios:
  - start_date:
      around: "2026-06-15"
      plus_or_minus: 2
""",
        )
        spec = load_scenarios(_args(config=config))[0]
        assert spec.start_date == (date(2026, 6, 13), date(2026, 6, 17))

    def test_rejects_reversed_range(self, tmp_path) -> None:
        config = _write_yaml(
            tmp_path,
            """
scenarios:
  - start_date: ["2026-03-31", "2026-01-01"]
""",
        )
        with pytest.raises(ConfigError, match="start_date range start"):
            load_scenarios(_args(config=config))


class TestNumericValidation:
    def test_rejects_fractional_quantity(self, tmp_path) -> None:
        config = _write_yaml(
            tmp_path,
            """
scenarios:
  - quantity: 1.5
""",
        )
        with pytest.raises(ConfigError, match="quantity .* integer"):
            load_scenarios(_args(config=config))

    def test_rejects_discount_outside_percent_range(self, tmp_path) -> None:
        config = _write_yaml(
            tmp_path,
            """
scenarios:
  - discount: [10, 120]
""",
        )
        with pytest.raises(ConfigError, match="discount percent"):
            load_scenarios(_args(config=config))


class TestProductsAndPrecedence:
    def test_product_shorthand_builds_single_product_pool(self, tmp_path) -> None:
        config = _write_yaml(
            tmp_path,
            """
defaults:
  product: QB-API-FLEX
  quantity: 3
""",
        )
        spec = load_scenarios(_args(config=config))[0]
        assert len(spec.products) == 1
        assert spec.products[0].sku == "QB-API-FLEX"
        assert spec.products[0].quantity == (3, 3)

    def test_products_entry_overrides_scenario_quantity_and_discount(self, tmp_path) -> None:
        config = _write_yaml(
            tmp_path,
            """
scenarios:
  - quantity: 10
    discount: 5
    products:
      - sku: QB-API-FLEX
        quantity: [1, 2]
        discount: [20, 25]
""",
        )
        product = load_scenarios(_args(config=config))[0].products[0]
        assert product.quantity == (1, 2)
        assert product.discount == (20.0, 25.0)

    def test_scenario_target_stage_wins_over_cli_flag(self, tmp_path) -> None:
        config = _write_yaml(
            tmp_path,
            """
defaults:
  target_stage: quote
scenarios:
  - target_stage: post
""",
        )
        spec = load_scenarios(_args(config=config, target_stage="order"))[0]
        assert spec.target_stage == "post"


class TestProrationFields:
    def test_accepts_valid_proration_picklists(self, tmp_path) -> None:
        config = _write_yaml(
            tmp_path,
            """
scenarios:
  - products:
      - sku: QB-LIC-CLOUD
        period_boundary: Anniversary
        billing_frequency: Monthly
""",
        )
        product = load_scenarios(_args(config=config))[0].products[0]
        assert product.period_boundary == "Anniversary"
        assert product.billing_frequency == "Monthly"

    def test_rejects_invalid_proration_picklist(self, tmp_path) -> None:
        config = _write_yaml(
            tmp_path,
            """
scenarios:
  - products:
      - sku: QB-LIC-CLOUD
        period_boundary: NotARealBoundary
""",
        )
        with pytest.raises(ConfigError, match="period_boundary"):
            load_scenarios(_args(config=config))
