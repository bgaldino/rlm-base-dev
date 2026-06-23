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


class TestTermCoercion:
    """``_coerce_term`` accepts bare int + ``{count, unit}`` shapes; the runner
    enforces PSM-unit consistency post-resolution. These tests exercise just
    the parse layer.
    """

    def test_bare_int_lands_with_unit_sentinel(self, tmp_path) -> None:
        config = _write_yaml(
            tmp_path,
            """
scenarios:
  - products:
      - sku: QB-API-FLEX
        term: 36
""",
        )
        opt = load_scenarios(_args(config=config))[0].products[0]
        assert opt.term is not None
        assert opt.term.count == 36
        # Bare int -> unit is None; runner promotes from the PSM.
        assert opt.term.unit is None

    def test_mapping_with_explicit_unit(self, tmp_path) -> None:
        config = _write_yaml(
            tmp_path,
            """
scenarios:
  - products:
      - sku: QB-LIC-CLOUD
        term: {count: 3, unit: Annual}
""",
        )
        opt = load_scenarios(_args(config=config))[0].products[0]
        assert opt.term is not None
        assert opt.term.count == 3
        assert opt.term.unit == "Annual"

    def test_years_alias_maps_to_annual(self, tmp_path) -> None:
        config = _write_yaml(
            tmp_path,
            """
scenarios:
  - products:
      - sku: QB-LIC-CLOUD
        term: {count: 3, unit: Years}
""",
        )
        opt = load_scenarios(_args(config=config))[0].products[0]
        assert opt.term is not None
        assert opt.term.unit == "Annual"

    def test_rejects_invalid_unit(self, tmp_path) -> None:
        config = _write_yaml(
            tmp_path,
            """
scenarios:
  - products:
      - sku: QB-LIC-CLOUD
        term: {count: 30, unit: Days}
""",
        )
        with pytest.raises(ConfigError, match="term.unit"):
            load_scenarios(_args(config=config))

    def test_rejects_term_count_typo_over_cap(self, tmp_path) -> None:
        config = _write_yaml(
            tmp_path,
            """
scenarios:
  - products:
      - sku: QB-API-FLEX
        term: 360
""",
        )
        with pytest.raises(ConfigError, match="term must be <="):
            load_scenarios(_args(config=config))

    def test_rejects_zero_term(self, tmp_path) -> None:
        config = _write_yaml(
            tmp_path,
            """
scenarios:
  - products:
      - sku: QB-API-FLEX
        term: 0
""",
        )
        with pytest.raises(ConfigError, match="term must be >= 1"):
            load_scenarios(_args(config=config))

    def test_scenario_level_term_default(self, tmp_path) -> None:
        config = _write_yaml(
            tmp_path,
            """
scenarios:
  - term: {count: 2, unit: Annual}
    products:
      - sku: QB-LIC-CLOUD
""",
        )
        spec = load_scenarios(_args(config=config))[0]
        assert spec.term is not None
        assert spec.term.count == 2
        assert spec.term.unit == "Annual"

    def test_selling_model_pin_round_trips(self, tmp_path) -> None:
        config = _write_yaml(
            tmp_path,
            """
scenarios:
  - products:
      - sku: QB-LIC-CLOUD
        selling_model: "Term Based - Quarterly"
        term: {count: 4, unit: Quarterly}
""",
        )
        opt = load_scenarios(_args(config=config))[0].products[0]
        assert opt.selling_model == "Term Based - Quarterly"


class TestEndDateCoercion:
    """``_coerce_end_date`` accepts absolute dates, bare-int days, and
    suffixed offsets (``d``/``mo``/``q``/``y``); rejects ambiguous ``m``,
    zero/negative, bool, empty, and overflow. The override is carried
    through unresolved -- resolution against the line's StartDate happens
    inside the lifecycle so a scenario-level override co-terms every line.
    """

    def test_absolute_iso_date_string(self, tmp_path) -> None:
        config = _write_yaml(
            tmp_path,
            """
scenarios:
  - products:
      - sku: QB-API-FLEX
        term: 12
        end_date: "2027-01-14"
""",
        )
        opt = load_scenarios(_args(config=config))[0].products[0]
        assert opt.end_date is not None
        assert opt.end_date.absolute == date(2027, 1, 14)
        assert opt.end_date.days is None
        assert opt.end_date.months is None

    def test_yaml_native_date_treated_as_absolute(self, tmp_path) -> None:
        # PyYAML parses bare YYYY-MM-DD as a python ``date``.
        config = _write_yaml(
            tmp_path,
            """
scenarios:
  - products:
      - sku: QB-API-FLEX
        term: 12
        end_date: 2027-01-14
""",
        )
        opt = load_scenarios(_args(config=config))[0].products[0]
        assert opt.end_date is not None
        assert opt.end_date.absolute == date(2027, 1, 14)

    def test_bare_int_is_days(self, tmp_path) -> None:
        config = _write_yaml(
            tmp_path,
            """
scenarios:
  - products:
      - sku: QB-API-FLEX
        term: 12
        end_date: 364
""",
        )
        opt = load_scenarios(_args(config=config))[0].products[0]
        assert opt.end_date is not None
        assert opt.end_date.days == 364
        assert opt.end_date.absolute is None
        assert opt.end_date.months is None

    def test_suffix_days(self, tmp_path) -> None:
        config = _write_yaml(
            tmp_path,
            """
scenarios:
  - products:
      - sku: QB-API-FLEX
        term: 12
        end_date: "364d"
""",
        )
        opt = load_scenarios(_args(config=config))[0].products[0]
        assert opt.end_date is not None
        assert opt.end_date.days == 364

    def test_suffix_months_collapses_to_months(self, tmp_path) -> None:
        config = _write_yaml(
            tmp_path,
            """
scenarios:
  - products:
      - sku: QB-API-FLEX
        term: 12
        end_date: "12mo"
""",
        )
        opt = load_scenarios(_args(config=config))[0].products[0]
        assert opt.end_date is not None
        assert opt.end_date.months == 12

    def test_suffix_quarters_multiplies_by_three(self, tmp_path) -> None:
        config = _write_yaml(
            tmp_path,
            """
scenarios:
  - products:
      - sku: QB-API-FLEX
        term: 12
        end_date: "3q"
""",
        )
        opt = load_scenarios(_args(config=config))[0].products[0]
        assert opt.end_date is not None
        assert opt.end_date.months == 9

    def test_suffix_years_multiplies_by_twelve(self, tmp_path) -> None:
        config = _write_yaml(
            tmp_path,
            """
scenarios:
  - products:
      - sku: QB-API-FLEX
        term: 12
        end_date: "1y"
""",
        )
        opt = load_scenarios(_args(config=config))[0].products[0]
        assert opt.end_date is not None
        assert opt.end_date.months == 12

    def test_rejects_ambiguous_m_suffix(self, tmp_path) -> None:
        config = _write_yaml(
            tmp_path,
            """
scenarios:
  - products:
      - sku: QB-API-FLEX
        term: 12
        end_date: "12m"
""",
        )
        with pytest.raises(ConfigError, match="ambiguous"):
            load_scenarios(_args(config=config))

    def test_rejects_zero_offset(self, tmp_path) -> None:
        config = _write_yaml(
            tmp_path,
            """
scenarios:
  - products:
      - sku: QB-API-FLEX
        term: 12
        end_date: 0
""",
        )
        with pytest.raises(ConfigError, match="end_date offset must be positive"):
            load_scenarios(_args(config=config))

    def test_rejects_negative_int(self, tmp_path) -> None:
        config = _write_yaml(
            tmp_path,
            """
scenarios:
  - products:
      - sku: QB-API-FLEX
        term: 12
        end_date: -30
""",
        )
        with pytest.raises(ConfigError, match="end_date offset must be positive"):
            load_scenarios(_args(config=config))

    def test_rejects_negative_suffixed(self, tmp_path) -> None:
        # "-30d" doesn't end with a valid suffix in the longest-match search
        # because the leading sign isn't part of an int; the parser surfaces
        # the offset-must-be-positive message via the int-coerce branch.
        config = _write_yaml(
            tmp_path,
            """
scenarios:
  - products:
      - sku: QB-API-FLEX
        term: 12
        end_date: "-30d"
""",
        )
        with pytest.raises(ConfigError, match="positive"):
            load_scenarios(_args(config=config))

    def test_rejects_bool(self, tmp_path) -> None:
        config = _write_yaml(
            tmp_path,
            """
scenarios:
  - products:
      - sku: QB-API-FLEX
        term: 12
        end_date: true
""",
        )
        with pytest.raises(ConfigError, match="bool"):
            load_scenarios(_args(config=config))

    def test_rejects_empty_string(self, tmp_path) -> None:
        config = _write_yaml(
            tmp_path,
            """
scenarios:
  - products:
      - sku: QB-API-FLEX
        term: 12
        end_date: ""
""",
        )
        with pytest.raises(ConfigError, match="empty"):
            load_scenarios(_args(config=config))

    def test_rejects_overflow_days(self, tmp_path) -> None:
        config = _write_yaml(
            tmp_path,
            """
scenarios:
  - products:
      - sku: QB-API-FLEX
        term: 12
        end_date: 10000
""",
        )
        with pytest.raises(ConfigError, match="exceeds"):
            load_scenarios(_args(config=config))

    def test_rejects_overflow_years(self, tmp_path) -> None:
        config = _write_yaml(
            tmp_path,
            """
scenarios:
  - products:
      - sku: QB-API-FLEX
        term: 12
        end_date: "30y"
""",
        )
        with pytest.raises(ConfigError, match="exceeds"):
            load_scenarios(_args(config=config))

    def test_rejects_unknown_suffix(self, tmp_path) -> None:
        config = _write_yaml(
            tmp_path,
            """
scenarios:
  - products:
      - sku: QB-API-FLEX
        term: 12
        end_date: "5w"
""",
        )
        with pytest.raises(ConfigError, match="end_date"):
            load_scenarios(_args(config=config))

    def test_scenario_level_end_date_lands_on_spec(self, tmp_path) -> None:
        """Scenario-level ``end_date`` is co-term shorthand -- the runner
        falls every TermDefined line that doesn't pin its own ``end_date``
        through to this default."""
        config = _write_yaml(
            tmp_path,
            """
scenarios:
  - term: {count: 1, unit: Annual}
    end_date: "2027-01-14"
    products:
      - sku: QB-LIC-CLOUD
""",
        )
        spec = load_scenarios(_args(config=config))[0]
        assert spec.end_date is not None
        assert spec.end_date.absolute == date(2027, 1, 14)
