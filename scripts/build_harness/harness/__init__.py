"""Modularized internals of the build harness CLI.

Submodules:
    config         - cumulusci.yml loading, scenario composition, workspace setup
    execution      - subprocess runner with structured result capture
    failure        - failure-signature heuristics (transient vs deterministic)
    io             - JSON/JSONL helpers + UTC timestamp helper
    provenance     - build_provenance.json generation
    reporting      - run analysis artifacts and human-readable report
    scenario_runner - per-scenario orchestration loop
"""
