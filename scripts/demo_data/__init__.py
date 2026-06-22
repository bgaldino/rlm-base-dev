"""Demo Sales Data Generator.

Standalone, config-driven tool that mints realistic Revenue Cloud demo data by
driving the real transaction lifecycle against a target org:

    (Opportunity) -> Quote (Place Sales Transaction) -> Order
        -> Activate -> Generate Invoice -> Post Invoice

Not part of ``prepare_rlm_org`` -- a one-off, re-runnable, additive tool. See
``scripts/demo_data/CONTRACTS.md`` for the live-verified endpoint/body/response
contracts that ``lifecycle.py`` transcribes, and ``README.md`` for usage.

Invoke as::

    python -m scripts.demo_data.generate --org <sf-alias> [--config <file>] [options]

``--org`` accepts an ``sf`` CLI alias / username only (NOT a CCI alias).
"""
