"""Self-contained toolkit for authoring **ramped Revenue Cloud quotes** headlessly.

A ramped quote is a pattern over two ordinary sObjects (``QuoteLineGroup`` = the
segment, ``QuoteLineItem`` = the line inside it) driven through the Place Sales
Transaction Connect API with a ``groupRampAction`` — there is no ramp sObject.
See ``.agents/artifacts/ramped-quote-skill/PLAN.md`` §4 for the data model and §8
for the call sequence.

Layout mirrors ``scripts/expression_sets/``: pure, dependency-free core modules
(``_schedule``, ``_payload``, ``_verify``) shared by the verb CLIs, the offline
tests, and the MCP façade so no logic is implemented twice. The pure modules
import nothing from ``tasks/`` and pull in no ``requests`` / CumulusCI / ``sf``
CLI — they operate on plain dicts and dates only, so they can be unit-tested with
no org (``python tests/test_ramp_deals_toolkit.py``).

Enums and field legality here were verified live on 264 / v68.0
(``.agents/artifacts/ramped-quote-skill/probe-264/E9-ramp-field-summary.md``).
"""

# Connect API version. 264 / Winter '27. The ramp `place`/`clone` ops and the
# `groupRampAction` field were verified live at this version.
API_VERSION = "v68.0"
