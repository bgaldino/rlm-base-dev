"""Regression tests for the generated CCI reference helpers."""

from scripts.ai.generate_cci_reference import _scan_when_clauses


def test_scan_when_clauses_matches_complete_feature_flag_names():
    data = {
        "project": {
            "custom": {
                "billing": True,
                "billing_portal": True,
                "billing_portal_deploy": True,
                "billing_ui": True,
            }
        },
        "flows": {
            "prepare_billing": {
                "steps": {
                    1: {
                        "task": "deploy_billing",
                        "when": "project_config.project__custom__billing",
                    },
                    2: {
                        "task": "deploy_billing_ui",
                        "when": (
                            "project_config.project__custom__billing and "
                            "project_config.project__custom__billing_ui"
                        ),
                    },
                }
            },
            "prepare_billing_portal": {
                "steps": {
                    1: {
                        "task": "create_billing_portal",
                        "when": "project_config.project__custom__billing_portal",
                    },
                    2: {
                        "task": "deploy_billing_portal",
                        "when": (
                            "project_config.project__custom__billing_portal and "
                            "project_config.project__custom__billing_portal_deploy"
                        ),
                    },
                }
            },
        },
    }

    usage = _scan_when_clauses(data)

    assert usage["billing"] == [
        "`prepare_billing` step 1 → `deploy_billing`",
        "`prepare_billing` step 2 → `deploy_billing_ui`",
    ]
    assert usage["billing_ui"] == [
        "`prepare_billing` step 2 → `deploy_billing_ui`"
    ]
    assert usage["billing_portal"] == [
        "`prepare_billing_portal` step 1 → `create_billing_portal`",
        "`prepare_billing_portal` step 2 → `deploy_billing_portal`",
    ]
    assert usage["billing_portal_deploy"] == [
        "`prepare_billing_portal` step 2 → `deploy_billing_portal`"
    ]


def test_scan_when_clauses_does_not_treat_a_longer_flag_as_a_prefix_match():
    data = {
        "project": {
            "custom": {
                "billing_portal": True,
                "billing_portal_deploy": True,
            }
        },
        "flows": {
            "synthetic": {
                "steps": {
                    1: {
                        "task": "deploy",
                        "when": "project_config.project__custom__billing_portal_deploy",
                    }
                }
            }
        },
    }

    usage = _scan_when_clauses(data)

    assert "billing_portal" not in usage
    assert usage["billing_portal_deploy"] == ["`synthetic` step 1 → `deploy`"]
