#!/usr/bin/env python3
"""Canonical Context Service REST resource paths (relative to /services/data/vXX.0/).

Confirmed against the public **Context Service API REST Reference**
(developer.salesforce.com → industries_reference → context_*_management),
Release 262 / API v67.0. Centralizing them here keeps the apply / delete / mutate
verbs from drifting on path spelling and documents the create/update-vs-delete-by-id
split plus the "since" version for each.

Naming: ``*_COLLECTION`` = the create/update (POST/PATCH) resource;
``*_ITEM`` = the GET+DELETE-by-id resource. All are ``str.format`` templates.

Notes / gotchas surfaced by the reference:
- Every artifact (mapping, node-mapping, attribute-mapping, node, attribute,
  tag) has a **granular GET+DELETE-by-id** resource (all since 59.0). This is
  what ``delete_context.py`` uses; reverse-order deletion is:
  attribute-mappings -> node-mappings -> mappings, and tags/attributes -> nodes
  -> definition.
- ``ATTR_MAPPING_COLLECTION`` (context-node-mappings/{id}/context-attribute-mappings)
  writes ONE attribute mapping at a time and accepts ``hydrationDetails``
  directly — a granular alternative to the whole-``context-mappings`` PATCH the
  CCI task uses (which wipes hydration via isDeleteExistingHydrationDetail).
- ``NODE_CONFIGURE_RELATIONSHIP`` (since 61.0) attaches EXISTING nodes as
  children of a node — hierarchy assembly after node creation.
- The node-mapping POST/PATCH body field ``mappedContextNodeId`` is NOT in the
  public docs but is set by the CCI task and works for DocGen child nodes
  (live-confirmed) — undocumented-but-functional.
"""

# --- Definitions ---------------------------------------------------------- #
# Collection: GET (list), POST (create / clone via sourceDefinitionId /
#   extend a file-based base via baseReference / persist a whole definition via
#   the `payload` field). Item: GET, PATCH, DELETE (all since 59.0).
DEFINITION_COLLECTION = "connect/context-definitions"
DEFINITION_ITEM = "connect/context-definitions/{context_definition_id}"
DEFINITION_UPGRADES = "connect/context-definitions/upgrades"  # PATCH, upgradeMode Sync/Preview/Override
DEFINITION_QUERY_TAGS = "connect/context-definitions/query-tags"
# Context Definition Filters (criteria that refine/limit data operations).
DEFINITION_FILTERS = "connect/context-definitions/{context_definition_id}/filters"  # GET, POST
DEFINITION_FILTER_ITEM = (
    "connect/context-definitions/{context_definition_id}/filters/{filter_id}"
)  # GET, PATCH, DELETE

# --- Undocumented-but-functional (docs omit these; code + live runs prove them) #
#   * PATCH DEFINITION_ITEM with {"isActive": "true"|"false"} activates/deactivates
#     (the REST reference documents only `definition`/`description` on that PATCH).
#   * POST DEFINITION_COLLECTION with `baseReference` extends a standard base
#     (the reference documents only `sourceDefinitionId` as the source field).
#   * GET DEFINITION_COLLECTION accepts ?includeInactive=true&includeUpgrade=true
#     (no query params are documented, but the read scripts rely on them).

# --- Context Mappings ----------------------------------------------------- #
MAPPING_COLLECTION = "connect/context-definitions/{context_definition_id}/context-mappings"
MAPPING_ITEM = (
    "connect/context-definitions/{context_definition_id}/context-mappings/{context_mapping_id}"
)  # GET, DELETE (59.0)

# --- Context Node Mappings ------------------------------------------------ #
NODE_MAPPING_COLLECTION = "connect/context-mappings/{context_mapping_id}/context-node-mappings"
NODE_MAPPING_ITEM = (
    "connect/context-mappings/{context_mapping_id}/context-node-mappings/{context_node_mapping_id}"
)  # GET, DELETE (59.0)

# --- Context Attribute Mappings ------------------------------------------- #
# Granular single-attribute write (POST/PATCH); accepts hydrationDetails directly.
ATTR_MAPPING_COLLECTION = (
    "connect/context-node-mappings/{context_node_mapping_id}/context-attribute-mappings"
)
ATTR_MAPPING_ITEM = (
    "connect/context-node-mappings/{context_node_mapping_id}"
    "/context-attribute-mappings/{context_attribute_mapping_id}"
)  # GET, DELETE (59.0)

# --- Context Nodes -------------------------------------------------------- #
NODE_COLLECTION = "connect/context-definitions/{context_definition_id}/context-nodes"
NODE_ITEM = (
    "connect/context-definitions/{context_definition_id}/context-nodes/{context_node_id}"
)  # GET, DELETE (59.0)
NODE_CONFIGURE_RELATIONSHIP = "connect/context-nodes/{context_node_id}/configurerelationship"  # POST (61.0)

# --- Context Attributes --------------------------------------------------- #
ATTRIBUTE_COLLECTION = "connect/context-nodes/{context_node_id}/context-attributes"
ATTRIBUTE_ITEM = (
    "connect/context-nodes/{context_node_id}/context-attributes/{context_attribute_id}"
)  # GET, DELETE (59.0)

# --- Context Tags --------------------------------------------------------- #
TAG_COLLECTION = "connect/context-definitions/{context_definition_id}/context-tags"
TAG_ITEM = (
    "connect/context-definitions/{context_definition_id}/context-tags/{context_tag_id}"
)  # GET, DELETE (59.0)

# --- Request-body facts (Context Service API "Request Bodies" reference) --- #
# Confirmed against the connect_requests_*_input pages (262 / v67.0). These document
# the *shapes* the collections above accept; the writers in _apply/_payload
# already emit them. Recorded here so the payload contract lives next to paths.
#
# Context Definition Input (DEFINITION_COLLECTION POST):
#   required: name, developerName, startDate
#   optional (documented): description, endDate, isActive(Boolean), payload(String
#     — whole-definition JSON), sourceDefinitionId(String — clone source), contextTtl(Integer)
#   undocumented-but-functional (task uses, docs omit): baseReference, contextType
#
# Context Mappings Input (MAPPING_COLLECTION POST/PATCH), per contextMappings[] entry:
#   required: name, contextMappingId(update only)
#   optional: description, isDefault(Boolean), contextNodeMappings[],
#     intents(List<String>, since 61.0) — enum HYDRATION | PERSISTENCE |
#     ASSOCIATION | TRANSLATION. (mappedContextDefinitionName is NOT documented
#     here — we set MappedContextDefinition via SObject REST instead.)
#
# Context Attribute Mappings Input (ATTR_MAPPING_COLLECTION, and nested under a
# node mapping), per contextAttributeMappings[] entry:
#   required: contextAttributeId; contextAttributeMappingId(update only)
#   optional: contextInputAttributeName, hydrationDetails
#   hydrationDetails wraps ONE of two arrays by mapping kind:
#     * SObject:          "contextAttrHydrationDetails":       [{sObjectDomain, queryAttribute}]
#     * context-to-context:"contextAttrContextHydrationDetails":[{queryAttribute, parentAttributeMappingId}]
#
# Context Attribute Hydration Details Input (traversal, Connect-native — an
# ALTERNATIVE to the SObject-REST ContextAttrHydrationDetail path _apply uses):
#   sObjectDomain(opt), queryAttribute(opt), parentAttributeMappingId(req),
#   parentDetailId(req), childDetails[](req, nested), contextAttrHydrationDetailId(update only)

# --- SObject-REST-only operations (Connect PATCH can't do these) ---------- #
# MappedContextDefinition on a ContextNodeMapping; IsTransient on a
# ContextAttribute; relationship-traversal hydration (ContextAttributeMapping +
# ContextAttrHydrationDetail). Built via _client.sobjects_request(...).
SOBJECT_CONTEXT_NODE_MAPPING = "ContextNodeMapping"
SOBJECT_CONTEXT_ATTRIBUTE = "ContextAttribute"
SOBJECT_CONTEXT_ATTRIBUTE_MAPPING = "ContextAttributeMapping"
SOBJECT_CONTEXT_ATTR_HYDRATION_DETAIL = "ContextAttrHydrationDetail"

# ========================================================================== #
# RUNTIME resources (context INSTANCE lifecycle)                             #
# ========================================================================== #
# These operate on a hydrated context **instance**, not a design-time
# **definition** — a different half of the Context Service surface. Confirmed
# against the public "Runtime Context Instance Management" and "Persistence
# Context Management" REST references (262 / v67.0); the two PATCH bodies
# (attributes, write-through-tags) are grounded in internal sources and marked
# verify-live in _runtime.py / the runtime sub-file. The "since" version on each
# line is the API version that added the resource.
#
# Runtime identity: a runtime ``contextId`` is a request-scoped **cache handle**
# (an opaque UUID/hex string, NOT a 15/18-char SObject id and NOT prefix-typed).
# The create doc is explicit that a context object "applies only to a single
# request and cannot pass data across multiple requests" unless the org's
# "Runtime Context Instance Reuse to Improve Response Times" setting is on and
# the call is within contextTtl. Do not prefix-validate a contextId.
#
# NB: distinct from the design-time DEFINITION_QUERY_TAGS
# (connect/context-definitions/query-tags) above — the runtime tag reads below
# hang off connect/contexts/ and take a live contextId, not a definition id.
CONTEXTS_COLLECTION = "connect/contexts"                       # POST create (59.0)
CONTEXT_ITEM = "connect/contexts/{context_id}"                 # GET, DELETE (59.0)
CONTEXT_QUERY_RECORD = "connect/contexts/query-record"         # POST (+ ?children=) (59.0)
CONTEXT_ATTRIBUTES = "connect/contexts/attributes"             # PATCH (59.0)
CONTEXT_QUERY_TAGS = "connect/contexts/query-tags"             # POST (59.0)
CONTEXT_QUERY_TAGS_LEANER = "connect/contexts/query-tags-leaner"  # POST (66.0)
CONTEXT_WRITE_THROUGH_TAGS = "connect/contexts/write-through-tags"  # PATCH (63.0)
CONTEXT_PERSIST_RECORDS = "connect/contexts/persist-records"   # POST (59.0)
# DELETE + ?contextDefinitionName=&contextMappingNames= — evicts the cached
# runtime schema so the next hydration re-reads the definition (65.0).
CONTEXT_RUNTIME_SCHEMA_CLEAR = "connect/context-runtime-schema/clear"  # DELETE (65.0)
# Definition interfaces are not tied to a specific definition instance.
CONTEXT_DEFINITION_INTERFACES = "connect/context-definition-interfaces"  # GET (62.0)
CONTEXT_DEFINITION_INTERFACE_ITEM = "connect/context-definition-interfaces/{name}"  # GET (62.0)
