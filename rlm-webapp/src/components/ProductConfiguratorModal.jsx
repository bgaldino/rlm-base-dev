import { useState, useEffect, useCallback, useRef } from 'react';
import {
  headlessConfigLoad,
  headlessConfigSet,
  headlessConfigGet,
  headlessConfigAddNodes,
  headlessConfigUpdateNodes,
  headlessConfigDeleteNodes,
  headlessConfigSetQuantity,
  headlessConfigSave,
  fetchQuoteEntitiesMappingId,
  executePriceContext,
  placeSalesTransaction,
  pollAsyncStatus,
  fetchStandardPricebook,
  fetchPricebookEntries,
  fetchQuoteLinePricing,
  fetchStandardPrices,
  getProductDetails,
  formatCurrency,
} from '../utils/rlmApi';
import Spinner from './Spinner';

// ─────────────────────────────────────────────────────────────────────────────
// Product Configurator Modal
//
// Supports two modes:
//
//   HEADLESS MODE  (transactionId provided, or auto-created)
//     1. If no transactionId, calls placeSalesTransaction (v66 Rev API) to create
//        a draft Quote with the product at default qty — real pricing via the full
//        pricing engine AND a transactionId to load the headless configurator with.
//     2. Load(transactionId) → contextId
//     3. Get(contextId) → SalesTransaction / SalesTransactionItem tree
//     4. AddNodes / UpdateNodes / DeleteNodes / SetQuantity → mutate context
//     5. Save(contextId) → persists changes to the Quote
//
//   FALLBACK MODE  (placeSalesTransaction failed)
//     Shows product details and bundle component info from the CPQ catalog.
//     Price is not available. User can still add to cart without a configurator.
//
// Props:
//   product           — product object from the catalog
//   auth              — { accessToken, instanceUrl }
//   catalogId         — active catalog id (optional, for product details lookup)
//   transactionId     — existing Quote/Order id (optional — auto-created if absent)
//   transactionLineId — existing QuoteLineItem id (optional — auto-populated if absent)
//   onClose()         — dismiss without saving
//   onSave(result)    — called with { contextId, transactionId, lineItemId, pricing, configData }
// ─────────────────────────────────────────────────────────────────────────────

export default function ProductConfiguratorModal({
  product,
  auth,
  catalogId,
  transactionId:     txIdProp,
  transactionLineId: txLineIdProp,
  onClose,
  onSave,
}) {
  const productId   = product?.id ?? product?.Id;
  const productName = product?.name ?? product?.Name ?? 'Product';

  // ── Effective IDs (may come from props OR from auto-created transaction) ───
  const [effectiveTxId,     setEffectiveTxId]     = useState(txIdProp   ?? null);
  const [effectiveLineId,   setEffectiveLineId]    = useState(txLineIdProp ?? null);

  // ── Configurator context state ────────────────────────────────────────────
  const [contextId,    setContextId]    = useState(null);
  const [txData,       setTxData]       = useState(null);   // SalesTransaction tree
  const [configData,   setConfigData]   = useState(null);   // fallback product details

  // ── UI state ──────────────────────────────────────────────────────────────
  const [pricing,        setPricing]        = useState(null);
  const [pricingLoading, setPricingLoading] = useState(false);
  const [loading,        setLoading]        = useState(true);
  const [loadingMsg,     setLoadingMsg]     = useState('Loading configuration…');
  const [saving,         setSaving]         = useState(false);
  const [error,          setError]          = useState('');
  const [quantity,       setQuantity]       = useState(1);
  const [isFallback,     setIsFallback]     = useState(false);

  // Prevent double-init in StrictMode
  const initRan = useRef(false);

  // ── Load headless configurator for a given transactionId ──────────────────

  const loadHeadless = useCallback(async (txId) => {
    setLoadingMsg('Loading configurator…');

    // Path 1 — auto-discover context via product-level mapping (requires the product
    // to have a Configurator Context Mapping set up in the org).
    let loadResult = await headlessConfigLoad(auth, { transactionId: txId })
      .catch(() => null);

    // Path 2 — explicit seed via headlessConfigSet using the QuoteEntitiesMapping ID.
    // This is the fallback when the product has no product-level mapping (e.g. the
    // setup_configurator_context CCI task has not been run yet for this product).
    if (!loadResult?.success) {
      const mappingId = await fetchQuoteEntitiesMappingId(auth);
      console.log('[Configurator] Path 2 mappingId:', mappingId);
      if (mappingId) {
        const transaction = JSON.stringify({
          Quote: [{ businessObjectType: 'Quote', id: txId }],
        });
        loadResult = await headlessConfigSet(auth, {
          contextMappingId: mappingId,
          transaction,
        }).catch(e => { console.warn('[Configurator] headlessConfigSet threw:', e.message); return null; });
        console.log('[Configurator] headlessConfigSet result:', loadResult);
      }
    }

    if (!loadResult?.success) {
      const msg = loadResult?.errors?.[0]?.message ?? 'Configurator load failed';
      throw new Error(msg);
    }
    const cid = loadResult.contextId;
    setContextId(cid);

    setLoadingMsg('Fetching line items…');
    const getResult = await headlessConfigGet(auth, { contextId: cid });
    console.log('[Configurator] headlessConfigGet result:', getResult);
    if (!getResult?.success) {
      const msg = getResult?.errors?.[0]?.message ?? 'Configurator get failed';
      throw new Error(msg);
    }
    setTxData(getResult.transaction);

    // Extract pricing from the headless response (SalesTransactionItem totals)
    const headlessPricing = extractHeadlessPricing(getResult.transaction);
    if (headlessPricing) setPricing(headlessPricing);

    // Extract first line item ID for quantity mutations (if not already set)
    const firstLineId = extractFirstLineItemId(getResult.transaction);
    if (firstLineId) setEffectiveLineId(prev => prev ?? firstLineId);

    return cid;
  }, [auth?.accessToken]);

  // ── Extract data from placeSalesTransaction v66 response ─────────────────
  // Response shape: { salesTransactionId, isSuccess, contextDetails: { contextId }, errorResponse }
  // Synchronous — no statusURL polling needed.

  function extractQuoteId(result) {
    // v66 placeSalesTransaction response
    return result?.salesTransactionId
      // Legacy placeQuote async response shape
      ?? result?.quoteId
      // Composite graph response (fallback)
      ?? result?.records?.find(r => r.referenceId === 'refQuote')?.id
      ?? result?.id;
  }

  function extractContextId(result) {
    // placeSalesTransaction may return a configurator contextId directly
    // when configurationMethod is "Run"
    const cid = result?.contextDetails?.contextId;
    return cid && cid !== '' ? cid : null;
  }

  // ── Initialise on mount ───────────────────────────────────────────────────

  useEffect(() => {
    if (!productId) return;
    if (initRan.current) return;
    initRan.current = true;

    setLoading(true);
    setError('');

    if (txIdProp) {
      // ── Already have a quote: go straight to headless mode
      loadHeadless(txIdProp)
        .catch(e => {
          console.warn('[Configurator] headless load failed:', e.message);
          setError(e.message);
        })
        .finally(() => setLoading(false));

    } else {
      // ── No existing quote: create one via placeQuote to get pricing + a transactionId.
      // placeQuote requires a pricebook entry, so fetch the standard pricebook first.
      setLoadingMsg('Creating configuration context…');

      // Use pricebook entry from product if already available, else fetch it
      const existingPbeId = product?.pricebookEntryId ?? product?.PricebookEntryId;

      const pricebookSetup = existingPbeId
        ? Promise.resolve({ pricebookId: null, pricebookEntryId: existingPbeId })
        : fetchStandardPricebook(auth)
            .then(pb => {
              if (!pb) return { pricebookId: null, pricebookEntryId: null };
              return fetchPricebookEntries(auth, [productId], pb.Id)
                .then(pbeMap => ({
                  pricebookId:     pb.Id,
                  pricebookEntryId: pbeMap[productId]?.Id ?? null,
                }));
            })
            .catch(() => ({ pricebookId: null, pricebookEntryId: null }));

      pricebookSetup
        .then(({ pricebookId, pricebookEntryId }) =>
          placeSalesTransaction(auth, {
            quoteName:  `Portal Config — ${productName}`,
            pricebookId,
            cartItems: [{ productId, quantity: 1, pricebookEntryId }],
          })
        )
        .then(async txResult => {
          const txId = extractQuoteId(txResult);
          if (!txId) {
            console.warn('[Configurator] unexpected placeSalesTransaction response:', txResult);
            throw new Error('No transaction ID returned from placeSalesTransaction');
          }

          setEffectiveTxId(txId);

          // Pricing strategy:
          // 1. executePriceContext  — POST /connect/core-pricing/price-contexts/{txId}
          //    Runs the pricing procedure on the transaction; response carries totals.
          // 2. fetchQuoteLinePricing fallback — SOQL on QuoteLineItem records.
          //    For bundles the parent QLI is $0; component QLIs carry the value.
          executePriceContext(auth, txId)
            .then(priceResult => {
              console.log('[Configurator] executePriceContext result:', JSON.stringify(priceResult)?.substring(0, 600));
              const total = parsePriceContextTotal(priceResult);
              if (total != null) {
                setPricing({
                  totalPrice: total.totalPrice,
                  unitPrice:  total.unitPrice,
                  currency:   total.currency,
                });
                return;
              }
              // Fallback: query QLIs directly
              return fetchQuoteLinePricing(auth, txId).then(priceMap => {
                console.log('[Configurator] fetchQuoteLinePricing priceMap (fallback):', priceMap);
                const items = Object.values(priceMap);
                if (items.length === 0) return;
                const totalPrice = items.reduce((sum, i) => sum + (i.totalPrice ?? 0), 0);
                const currency   = items[0]?.currency ?? 'USD';
                const unitPrice  = priceMap[productId]?.unitPrice ?? items[0]?.unitPrice ?? null;
                setPricing({ unitPrice, totalPrice, currency });
              });
            })
            .catch(() => {
              // Last resort: QLI query
              fetchQuoteLinePricing(auth, txId).then(priceMap => {
                const items = Object.values(priceMap);
                if (items.length === 0) return;
                const totalPrice = items.reduce((sum, i) => sum + (i.totalPrice ?? 0), 0);
                const currency   = items[0]?.currency ?? 'USD';
                const unitPrice  = priceMap[productId]?.unitPrice ?? items[0]?.unitPrice ?? null;
                setPricing({ unitPrice, totalPrice, currency });
              }).catch(() => {});
            });

          // placeSalesTransaction is synchronous (no statusURL polling needed).
          // If configurationMethod="Run", the platform may return a contextId directly.
          const inlineCtxId = extractContextId(txResult);
          if (inlineCtxId) {
            // Configurator context already created — skip headlessConfigLoad,
            // go straight to Get to fetch the transaction tree + pricing.
            setContextId(inlineCtxId);
            setLoadingMsg('Fetching line items…');
            try {
              const getResult = await headlessConfigGet(auth, { contextId: inlineCtxId });
              if (getResult?.success) {
                setTxData(getResult.transaction);
                const p = extractHeadlessPricing(getResult.transaction);
                if (p) setPricing(p);
                const lid = extractFirstLineItemId(getResult.transaction);
                if (lid) setEffectiveLineId(lid);
              }
            } catch (e) {
              console.warn('[Configurator] headlessConfigGet with inline contextId failed:', e.message);
            }
          } else {
            // No inline context — attempt headless configurator.
            // If the product doesn't support it, the QLI pricing fetch above still runs.
            setLoadingMsg('Loading configurator…');
            await loadHeadless(txId).catch(async e => {
              // Headless not available for this product — not a fatal error since
              // we still have a valid quote and can show pricing from QLI query.
              console.warn('[Configurator] headless load after create failed:', e.message);
              setError('');  // clear error — we have a quote and pricing
              // Fetch product details so we can show bundle components
              // in the left panel as a static informational display.
              setLoadingMsg('Loading bundle details…');
              try {
                const details = await getProductDetails(auth, productId, { catalogId });
                if (details) {
                  setConfigData(details);
                  // Bundle pricing: sum standard pricebook prices for all component products.
                  // The bundle parent QLI is $0 by design — components carry the value.
                  // Extract all component product IDs from every productComponentGroup.
                  const compIds = (details.productComponentGroups ?? []).flatMap(g =>
                    (g.components ?? g.productRelatedComponent ?? []).map(c => c.id ?? c.productId).filter(Boolean)
                  );
                  if (compIds.length > 0) {
                    fetchStandardPrices(auth, compIds)
                      .then(priceMap => {
                        // Store prices so selection changes can recalculate live.
                        setCompPriceMap(priceMap);
                        // Initial total: sum only default-selected components.
                        // compSelections may not be set yet; re-derive from configData.
                        const groups = details.productComponentGroups ?? [];
                        let total = 0;
                        let currency = 'USD';
                        for (const group of groups) {
                          const comps = group.components ?? group.productRelatedComponent ?? [];
                          for (const c of comps) {
                            const id = c.id ?? c.productId;
                            if (!id) continue;
                            const isSelected = c.isDefaultComponent || c.isComponentRequired;
                            if (isSelected && priceMap[id]) {
                              total   += (priceMap[id].UnitPrice ?? 0) * (c.productQuantity ?? 1);
                              currency = priceMap[id].CurrencyIsoCode ?? currency;
                            }
                          }
                        }
                        // Fall back to full sum if no defaults are priced
                        if (total === 0) {
                          total = Object.values(priceMap).reduce((s, e) => s + (e.UnitPrice ?? 0), 0);
                          currency = Object.values(priceMap)[0]?.CurrencyIsoCode ?? 'USD';
                        }
                        setPricing(prev => (!prev || prev.totalPrice === 0)
                          ? { totalPrice: total, unitPrice: null, currency }
                          : prev
                        );
                      })
                      .catch(() => {});
                  }
                }
              } catch (err) {
                console.warn('[Configurator] getProductDetails threw:', err.message);
              }
            });
          }
        })
        .catch(e => {
          // Auto-create failed — fall back to static product details
          console.warn('[Configurator] auto-create failed, falling back to catalog mode:', e.message);
          setIsFallback(true);
          setLoadingMsg('Loading product details…');
          return getProductDetails(auth, productId, { catalogId })
            .then(result => setConfigData(result))
            .catch(() => {}); // silently ok if this also fails
        })
        .finally(() => setLoading(false));
    }
  }, [productId]);

  // ── Handle quantity change ─────────────────────────────────────────────────

  async function handleQuantityChange(qty) {
    if (qty < 1) return;
    setQuantity(qty);

    if (contextId && effectiveTxId && effectiveLineId) {
      try {
        const result = await headlessConfigSetQuantity(auth, {
          contextId,
          transactionLinePath: [effectiveTxId, effectiveLineId],
          quantity: qty,
        });
        if (result?.success) {
          const getResult = await headlessConfigGet(auth, { contextId });
          if (getResult?.success) setTxData(getResult.transaction);
        }
      } catch (e) {
        console.warn('[Configurator] setQuantity failed:', e.message);
      }
    }
  }

  // ── Handle add child node (bundle component) ───────────────────────────────

  async function handleAddComponent(childProductId, prtId, prcId) {
    if (!contextId || !effectiveTxId) return;
    const refId     = `ref_${childProductId}_${Date.now()}`;
    const lineRefId = `ref_line_${Date.now()}`;
    try {
      const result = await headlessConfigAddNodes(auth, {
        contextId,
        addedNodes: [
          {
            path: [effectiveTxId, refId],
            addedObject: {
              id: refId,
              SalesTransactionItemSource: refId,
              businessObjectType: 'QuoteLineItem',
              Quantity: 1,
              Product: childProductId,
            },
          },
          ...(effectiveLineId ? [{
            path: [effectiveTxId, refId, lineRefId],
            addedObject: {
              id:                   lineRefId,
              businessObjectType:   'QuoteLineRelationship',
              MainItem:             effectiveLineId,
              AssociatedItem:       refId,
              ...(prtId && { ProductRelationshipType: prtId }),
              ...(prcId && { ProductRelatedComponent:  prcId }),
            },
          }] : []),
        ],
      });
      if (result?.success) {
        const getResult = await headlessConfigGet(auth, { contextId });
        if (getResult?.success) setTxData(getResult.transaction);
      } else {
        setError(result?.errors?.[0]?.message ?? 'Add component failed');
      }
    } catch (e) {
      setError(e.message);
    }
  }

  // ── Handle remove child node ───────────────────────────────────────────────

  async function handleRemoveComponent(nodeId) {
    if (!contextId || !effectiveTxId) return;
    try {
      const result = await headlessConfigDeleteNodes(auth, {
        contextId,
        deletedNodes: [{ path: [effectiveTxId, nodeId] }],
      });
      if (result?.success) {
        const getResult = await headlessConfigGet(auth, { contextId });
        if (getResult?.success) setTxData(getResult.transaction);
      } else {
        setError(result?.errors?.[0]?.message ?? 'Remove component failed');
      }
    } catch (e) {
      setError(e.message);
    }
  }

  // ── Handle update node attribute ───────────────────────────────────────────

  async function handleUpdateNodeAttr(nodeId, attributes) {
    if (!contextId || !effectiveTxId) return;
    try {
      const result = await headlessConfigUpdateNodes(auth, {
        contextId,
        updatedNodes: [{ path: [effectiveTxId, nodeId], updatedAttributes: attributes }],
      });
      if (result?.success) {
        const getResult = await headlessConfigGet(auth, { contextId });
        if (getResult?.success) setTxData(getResult.transaction);
      } else {
        setError(result?.errors?.[0]?.message ?? 'Update failed');
      }
    } catch (e) {
      setError(e.message);
    }
  }

  // ── Save ──────────────────────────────────────────────────────────────────

  async function handleSave() {
    setSaving(true);
    setError('');
    try {
      if (contextId) {
        const result = await headlessConfigSave(auth, { contextId });
        if (!result?.success) {
          throw new Error(result?.errors?.[0]?.message ?? 'Save failed');
        }
      }
      onSave({
        contextId,
        transactionId: effectiveTxId,
        lineItemId:    effectiveLineId,
        pricing,
        configData:    txData ?? configData,
      });
    } catch (e) {
      setError(e.message);
      setSaving(false);
    }
  }

  // ── Attribute selection state ─────────────────────────────────────────────
  // { [attributeId]: selectedCode }
  const [attrSelections, setAttrSelections] = useState({});

  function handleAttrChange(attrId, code) {
    setAttrSelections(prev => ({ ...prev, [attrId]: code }));
  }

  // ── Bundle component selection state ──────────────────────────────────────
  // { [productId]: { selected: bool, qty: number } }
  const [compSelections, setCompSelections] = useState({});

  // Standard pricebook prices for all component products.
  // { [product2Id]: { UnitPrice, CurrencyIsoCode } }
  const [compPriceMap, setCompPriceMap] = useState({});

  // Initialize compSelections from configData whenever it changes.
  useEffect(() => {
    if (!configData) return;
    const groups = configData.productComponentGroups ?? [];
    const initial = {};
    for (const group of groups) {
      const comps = group.components ?? group.productRelatedComponent ?? [];
      for (const c of comps) {
        const id = c.id ?? c.productId;
        if (!id) continue;
        initial[id] = {
          selected:          c.isDefaultComponent || c.isComponentRequired || false,
          qty:               c.productQuantity ?? 1,
          isRequired:        c.isComponentRequired ?? false,
          isQuantityEditable: c.isQuantityEditable ?? true,
        };
      }
    }
    setCompSelections(initial);
  }, [configData]);

  // Recalculate total price whenever the user changes component selections.
  useEffect(() => {
    const priceEntries = Object.keys(compPriceMap);
    if (priceEntries.length === 0) return;
    let total = 0;
    let currency = 'USD';
    for (const [id, sel] of Object.entries(compSelections)) {
      if (!sel.selected) continue;
      const p = compPriceMap[id];
      if (p) {
        total   += (p.UnitPrice ?? 0) * (sel.qty ?? 1);
        currency = p.CurrencyIsoCode ?? currency;
      }
    }
    setPricing(prev => prev ? { ...prev, totalPrice: total, currency } : null);
  }, [compSelections, compPriceMap]);

  function handleCompChange(productId, patch) {
    setCompSelections(prev => ({ ...prev, [productId]: { ...prev[productId], ...patch } }));
  }

  // ── Render ─────────────────────────────────────────────────────────────────

  const lineItems           = parseSalesTransactionItems(txData);
  const bundleGroups        = parseBundleComponentGroups(configData);
  const bundleComponents    = parseBundleComponents(configData);
  const attrCategories      = parseAttributeCategories(configData);
  const isHeadlessActive    = !!effectiveTxId;
  const showHeadlessContent = isHeadlessActive && !isFallback;

  return (
    <div className="sf-modal-overlay" onClick={onClose}>
      <div className="sf-configurator-modal" onClick={e => e.stopPropagation()}>

        {/* ── Header ────────────────────────────────────────────────────────── */}
        <div className="sf-configurator-header">
          <h2 className="sf-configurator-header__title">
            Configure {productName}
          </h2>
          <button className="sf-modal-close" onClick={onClose}>✕</button>
        </div>

        {/* ── Body ──────────────────────────────────────────────────────────── */}
        <div className="sf-configurator-body">

          {/* Left: configuration panels */}
          <div className="sf-configurator-left">
            {loading ? (
              <div className="sf-configurator-loading">
                <Spinner />
                <p>{loadingMsg}</p>
              </div>
            ) : showHeadlessContent ? (
              // ── Headless mode content
              error ? (
                <div className="sf-empty-state sf-empty-state--sm">
                  <p style={{ color: 'var(--sf2-danger, #c0392b)' }}>{error}</p>
                  <p style={{ marginTop: 8, fontSize: 13, color: 'var(--sf2-text-muted)' }}>
                    Could not load the configurator. The product may not support interactive
                    configuration or the session has expired.
                  </p>
                </div>
              ) : lineItems.length > 0 ? (
                <HeadlessLineItemList
                  transactionId={effectiveTxId}
                  lineItems={lineItems}
                  onUpdateQty={(nodeId, qty) => handleUpdateNodeAttr(nodeId, { Quantity: qty })}
                  onRemove={handleRemoveComponent}
                />
              ) : (
                <ConfiguratorContent
                  productName={productName}
                  configData={configData}
                  pricing={pricing}
                  quantity={quantity}
                  onQuantityChange={handleQuantityChange}
                  attrCategories={attrCategories}
                  attrSelections={attrSelections}
                  onAttrChange={handleAttrChange}
                  bundleGroups={bundleGroups}
                  compSelections={compSelections}
                  compPriceMap={compPriceMap}
                  onCompChange={handleCompChange}
                  effectiveTxId={effectiveTxId}
                  instanceUrl={auth?.instanceUrl}
                />
              )
            ) : (
              // ── Fallback (catalog) mode — same UI, no live quote
              <ConfiguratorContent
                productName={productName}
                configData={configData}
                pricing={pricing}
                quantity={quantity}
                onQuantityChange={handleQuantityChange}
                attrCategories={attrCategories}
                attrSelections={attrSelections}
                onAttrChange={handleAttrChange}
                bundleGroups={bundleGroups}
                compSelections={compSelections}
                compPriceMap={compPriceMap}
                onCompChange={handleCompChange}
                effectiveTxId={effectiveTxId}
                instanceUrl={auth?.instanceUrl}
              />
            )}

            {/* Interaction errors shown after load */}
            {error && !loading && showHeadlessContent && lineItems.length > 0 && (
              <div className="sf-error-banner" style={{ margin: '0 0 12px' }}>
                {error}
              </div>
            )}
          </div>

          {/* Right: pricing summary */}
          <div className="sf-configurator-right">
            <ConfiguratorSummary
              productName={productName}
              quantity={quantity}
              pricing={pricing}
              loading={loading || pricingLoading}
              attrCategories={attrCategories}
              attrSelections={attrSelections}
              bundleGroups={bundleGroups}
              compSelections={compSelections}
              compPriceMap={compPriceMap}
            />
          </div>
        </div>

        {/* ── Footer ────────────────────────────────────────────────────────── */}
        <div className="sf-configurator-footer">
          <button className="sf-btn sf-btn--ghost" onClick={onClose} disabled={saving}>
            Cancel
          </button>
          <button
            className="sf-btn sf-btn--primary"
            onClick={handleSave}
            disabled={saving || loading}
          >
            {saving ? 'Saving…' : effectiveTxId ? 'Save Configuration' : 'Add to Cart'}
          </button>
        </div>
      </div>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// HeadlessLineItemList — shows SalesTransactionItems from the Headless API
// ─────────────────────────────────────────────────────────────────────────────

function HeadlessLineItemList({ transactionId, lineItems, onUpdateQty, onRemove }) {
  return (
    <div className="sf-option-list">
      {lineItems.map((li, i) => (
        <HeadlessLineItemRow
          key={li.id ?? i}
          item={li}
          transactionId={transactionId}
          onUpdateQty={onUpdateQty}
          onRemove={onRemove}
        />
      ))}
    </div>
  );
}

function HeadlessLineItemRow({ item, onUpdateQty, onRemove }) {
  const [qty, setQty] = useState(item.Quantity ?? 1);
  const name = item.productName ?? item.Product ?? item.id ?? 'Line item';

  function commitQty(newQty) {
    setQty(newQty);
    onUpdateQty(item.id, newQty);
  }

  return (
    <div className="sf-option-row sf-option-row--selected">
      <div className="sf-option-row__info" style={{ flex: 1 }}>
        <div className="sf-option-row__name">{name}</div>
        {item.businessObjectType && (
          <div className="sf-option-row__desc" style={{ fontSize: 11 }}>
            {item.businessObjectType}
          </div>
        )}
      </div>

      <div className="sf-qty-control" style={{ marginRight: 8 }}>
        <button onClick={() => commitQty(Math.max(1, qty - 1))}>−</button>
        <input
          type="number"
          min="1"
          value={qty}
          onChange={e => setQty(parseInt(e.target.value) || 1)}
          onBlur={e => commitQty(parseInt(e.target.value) || 1)}
          style={{ width: 40 }}
        />
        <button onClick={() => commitQty(qty + 1)}>+</button>
      </div>

      <button
        className="sf-btn sf-btn--ghost sf-btn--sm"
        style={{ padding: '2px 8px', fontSize: 12 }}
        onClick={() => onRemove(item.id)}
        title="Remove"
      >
        ✕
      </button>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// AttributeCategoryForm — renders picklist / text attribute selectors
// ─────────────────────────────────────────────────────────────────────────────

function AttributeCategoryForm({ categories, selections, onChange }) {
  if (!categories?.length) return null;

  return (
    <div style={{ width: '100%' }}>
      {categories.map(cat => (
        <div key={cat.id ?? cat.code} style={{ marginBottom: 20 }}>
          <p style={{
            fontSize: 12, fontWeight: 600, color: 'var(--sf2-text-muted)',
            textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 10,
          }}>
            {cat.name}
          </p>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            {cat.attributes.map(attr => (
              <div key={attr.id} style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
                <label style={{ fontSize: 13, fontWeight: 500, color: 'var(--sf2-text, #111)' }}>
                  {attr.name}
                  {attr.isRequired && (
                    <span style={{ color: 'var(--sf2-danger, #c0392b)', marginLeft: 3 }}>*</span>
                  )}
                </label>

                {attr.values.length > 0 ? (
                  // Picklist attribute — render as select
                  <select
                    value={selections[attr.id] ?? ''}
                    onChange={e => onChange(attr.id, e.target.value)}
                    style={{
                      border: '1px solid var(--sf2-border, #d1d5db)',
                      borderRadius: 6,
                      padding: '6px 10px',
                      fontSize: 13,
                      background: 'var(--sf2-surface, #fff)',
                      color: 'var(--sf2-text, #111)',
                      cursor: 'pointer',
                      width: '100%',
                      maxWidth: 280,
                    }}
                  >
                    <option value="">— Select —</option>
                    {attr.values.map(v => (
                      <option key={v.code} value={v.code}>{v.display}</option>
                    ))}
                  </select>
                ) : (
                  // Free-text / numeric attribute
                  <input
                    type={attr.dataType === 'Number' ? 'number' : 'text'}
                    value={selections[attr.id] ?? ''}
                    onChange={e => onChange(attr.id, e.target.value)}
                    placeholder={attr.dataType === 'Number' ? '0' : 'Enter value…'}
                    style={{
                      border: '1px solid var(--sf2-border, #d1d5db)',
                      borderRadius: 6,
                      padding: '6px 10px',
                      fontSize: 13,
                      width: '100%',
                      maxWidth: 280,
                      background: 'var(--sf2-surface, #fff)',
                      color: 'var(--sf2-text, #111)',
                    }}
                  />
                )}
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// BundleComponentGroups — interactive bundle component selector grouped by PCG
// ─────────────────────────────────────────────────────────────────────────────

function BundleComponentGroups({ groups, selections, onChange }) {
  if (!groups?.length) return null;

  return (
    <div style={{ width: '100%' }}>
      <p style={{
        fontSize: 12, fontWeight: 600, color: 'var(--sf2-text-muted)',
        textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 12,
      }}>
        Bundle Components
      </p>
      {groups.map(group => (
        <div key={group.id ?? group.code} style={{ marginBottom: 20 }}>
          {/* PCG section heading */}
          <p style={{
            fontSize: 11, fontWeight: 700, color: 'var(--sf2-text-muted)',
            textTransform: 'uppercase', letterSpacing: '0.08em',
            marginBottom: 6, paddingBottom: 4,
            borderBottom: '1px solid var(--sf2-border, #e5e7eb)',
          }}>
            {group.name}
          </p>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
            {group.components.map(comp => {
              const sel = selections[comp.id] ?? {
                selected: comp.isDefault || comp.isRequired,
                qty: comp.defaultQty ?? 1,
              };
              const isChecked = sel.selected;
              const qty = sel.qty ?? comp.defaultQty ?? 1;

              return (
                <div
                  key={comp.id}
                  style={{
                    display: 'flex', alignItems: 'center', gap: 10,
                    padding: '6px 8px', borderRadius: 6,
                    background: isChecked ? 'var(--sf2-surface-hover, #f0f4ff)' : 'transparent',
                    border: '1px solid',
                    borderColor: isChecked ? 'var(--sf2-primary-light, #c7d7ff)' : 'transparent',
                  }}
                >
                  {/* Checkbox — disabled for required components */}
                  <input
                    type="checkbox"
                    checked={isChecked}
                    disabled={comp.isRequired}
                    onChange={e => onChange(comp.id, { selected: e.target.checked })}
                    style={{
                      width: 15, height: 15,
                      cursor: comp.isRequired ? 'default' : 'pointer',
                      flexShrink: 0,
                    }}
                  />

                  {/* Component name + required badge */}
                  <span style={{
                    flex: 1, fontSize: 13,
                    color: 'var(--sf2-text, #111)',
                    fontWeight: isChecked ? 500 : 400,
                  }}>
                    {comp.name ?? comp.id}
                    {comp.isRequired && (
                      <span style={{ marginLeft: 6, fontSize: 11, color: 'var(--sf2-text-muted)', fontWeight: 400 }}>
                        (required)
                      </span>
                    )}
                  </span>

                  {/* Quantity — editable spinner when selected + editable, static label otherwise */}
                  {isChecked && comp.isQuantityEditable ? (
                    <div className="sf-qty-control" style={{ gap: 3 }}>
                      <button
                        onClick={() => onChange(comp.id, { qty: Math.max(1, qty - 1) })}
                        style={{ width: 22, height: 22, fontSize: 14, padding: 0 }}
                      >−</button>
                      <input
                        type="number"
                        min="1"
                        value={qty}
                        onChange={e => onChange(comp.id, { qty: Math.max(1, parseInt(e.target.value) || 1) })}
                        style={{ width: 36, textAlign: 'center', fontSize: 13 }}
                      />
                      <button
                        onClick={() => onChange(comp.id, { qty: qty + 1 })}
                        style={{ width: 22, height: 22, fontSize: 14, padding: 0 }}
                      >+</button>
                    </div>
                  ) : isChecked ? (
                    <span style={{ fontSize: 12, color: 'var(--sf2-text-muted)', minWidth: 40, textAlign: 'right' }}>
                      Qty {qty}
                    </span>
                  ) : null}
                </div>
              );
            })}
          </div>
        </div>
      ))}
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// CatalogConfigurator — fallback when headless/create both fail
// ─────────────────────────────────────────────────────────────────────────────

function CatalogConfigurator({
  product, configData, bundleComponents,
  attrCategories = [], attrSelections = {}, onAttrChange,
  quantity, onQuantityChange,
}) {
  const description = product?.description ?? product?.Description
    ?? configData?.description ?? configData?.Description;
  const family = product?.family ?? product?.Family;
  const code   = product?.productCode ?? product?.ProductCode;

  return (
    <div className="sf-fallback-config">
      {family && <div className="sf-tag" style={{ marginBottom: 8 }}>{family}</div>}
      {code && <div className="sf-product-card__code" style={{ marginBottom: 8 }}>{code}</div>}
      {description && <p className="sf-fallback-config__desc">{description}</p>}

      {/* Attribute categories */}
      {attrCategories.length > 0 && (
        <div className="sf-fallback-config__attrs" style={{ marginBottom: 16 }}>
          <AttributeCategoryForm
            categories={attrCategories}
            selections={attrSelections}
            onChange={onAttrChange}
          />
        </div>
      )}

      {/* Bundle components */}
      {bundleComponents.length > 0 ? (
        <div className="sf-fallback-config__attrs">
          <h4>Bundle Components</h4>
          <p style={{ fontSize: 13, color: 'var(--sf2-text-muted)', marginBottom: 10 }}>
            This bundle includes the following components. Full interactive configuration
            is available after the product is added to your quote.
          </p>
          {bundleComponents.map((comp, i) => (
            <div key={comp.id ?? i} className="sf-option-row">
              <div className="sf-option-row__info">
                <div className="sf-option-row__name">{comp.name ?? comp.productName ?? '—'}</div>
                {comp.quantity != null && (
                  <div className="sf-option-row__desc">Qty: {comp.quantity}</div>
                )}
                {comp.isRequired && (
                  <span className="sf-tag" style={{ fontSize: 10 }}>Required</span>
                )}
              </div>
            </div>
          ))}
        </div>
      ) : attrCategories.length === 0 && (
        <div className="sf-empty-state sf-empty-state--sm">
          <p>This product is ready to add to your quote.</p>
          <p style={{ marginTop: 8, fontSize: 13, color: 'var(--sf2-text-muted)' }}>
            Interactive configuration is available on the quote after adding this product.
          </p>
        </div>
      )}
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// ConfiguratorContent — main left-panel content (product hero + tabs)
// ─────────────────────────────────────────────────────────────────────────────

function ConfiguratorContent({
  productName, configData, pricing, quantity, onQuantityChange,
  attrCategories, attrSelections, onAttrChange,
  bundleGroups, compSelections, compPriceMap, onCompChange,
  effectiveTxId, instanceUrl,
}) {
  // Resolve image URL: prefer instanceUrl + displayUrl (relative SF static resource),
  // then any absolute URL from the catalog response, else null.
  const rawImg  = configData?.displayUrl ?? configData?.defaultImage?.url ?? configData?.imageUrl ?? null;
  const imageUrl = rawImg
    ? (rawImg.startsWith('http') ? rawImg : (instanceUrl ? instanceUrl + rawImg : null))
    : null;
  const description = configData?.description ?? configData?.Description ?? null;

  // Compute per-PSM totals from selected components (using PSM prices from catalog).
  // These feed the hero price display and the label.
  let heroOneTime  = 0;
  let heroAnnual   = 0;
  let heroMonthly  = 0;
  for (const group of bundleGroups) {
    for (const comp of group.components) {
      const sel = compSelections[comp.id];
      if (!sel?.selected) continue;
      const qty   = sel.qty ?? 1;
      const psmData = comp.defaultPsm;
      const uprice  = psmData?.price ?? compPriceMap[comp.id]?.UnitPrice ?? 0;
      if (psmData?.psmType === 'Annual') heroAnnual   += uprice * qty;
      else if (psmData?.psmType === 'Monthly') heroMonthly += uprice * qty;
      else heroOneTime += uprice * qty;
    }
  }
  // Choose the most prominent total for the hero display
  const heroCurrency = pricing?.currency ?? compPriceMap[Object.keys(compPriceMap)[0]]?.CurrencyIsoCode ?? 'USD';
  let displayPrice = pricing?.totalPrice ?? 0;
  let displayPsmLabel = 'Total';
  if (heroAnnual > 0 && heroAnnual >= heroOneTime && heroAnnual >= heroMonthly) {
    displayPrice = heroAnnual; displayPsmLabel = 'Annual';
  } else if (heroMonthly > 0 && heroMonthly >= heroOneTime) {
    displayPrice = heroMonthly; displayPsmLabel = 'Monthly';
  } else if (heroOneTime > 0) {
    displayPrice = heroOneTime; displayPsmLabel = 'One-Time';
  }

  return (
    <div style={{ width: '100%' }}>

      {/* ── Product hero ─────────────────────────────────────────────────── */}
      <div style={{
        display: 'flex', gap: 16, marginBottom: 20,
        paddingBottom: 16, borderBottom: '1px solid var(--sf2-border, #e5e7eb)',
      }}>
        {/* Product image */}
        {imageUrl ? (
          <img src={imageUrl} alt={productName} style={{
            width: 80, height: 80, objectFit: 'cover', borderRadius: 8, flexShrink: 0,
          }} />
        ) : (
          <div style={{
            width: 80, height: 80, borderRadius: 8, flexShrink: 0,
            background: 'linear-gradient(135deg, #e8f0fe 0%, #c5d8f6 100%)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontSize: 28, color: '#0176d3',
          }}>⬡</div>
        )}

        {/* Name + description */}
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{ fontSize: 15, fontWeight: 600, color: 'var(--sf2-text, #111)' }}>
            {productName}
          </div>
          {description && (
            <div style={{ fontSize: 12, color: 'var(--sf2-text-muted)', marginTop: 3, lineHeight: 1.4 }}>
              {description}
            </div>
          )}
          {displayPrice > 0 && (
            <div style={{ marginTop: 8, fontSize: 18, fontWeight: 700, color: 'var(--sf2-text, #111)' }}>
              {formatCurrency(displayPrice, heroCurrency)}
              <span style={{ fontSize: 12, fontWeight: 400, color: 'var(--sf2-text-muted)', marginLeft: 6 }}>
                {displayPsmLabel}
              </span>
            </div>
          )}
        </div>

        {/* Quantity control */}
        <div style={{ flexShrink: 0, textAlign: 'right' }}>
          <label style={{ fontSize: 12, color: 'var(--sf2-text-muted)', display: 'block', marginBottom: 4 }}>
            Quantity
          </label>
          <input
            type="number" min="1" value={quantity}
            onChange={e => onQuantityChange(parseInt(e.target.value) || 1)}
            style={{
              width: 64, border: '1px solid var(--sf2-border, #d1d5db)',
              borderRadius: 6, padding: '5px 8px', fontSize: 14,
              textAlign: 'center', background: 'var(--sf2-surface, #fff)',
            }}
          />
        </div>
      </div>

      {/* ── Attribute category tabs ───────────────────────────────────────── */}
      {attrCategories.length > 0 && (
        <div style={{ marginBottom: 20 }}>
          <AttributeTabs
            categories={attrCategories}
            selections={attrSelections}
            onChange={onAttrChange}
          />
        </div>
      )}

      {/* ── Component group tabs ──────────────────────────────────────────── */}
      {bundleGroups.length > 0 && (
        <ComponentGroupTabs
          groups={bundleGroups}
          selections={compSelections}
          priceMap={compPriceMap}
          onChange={onCompChange}
        />
      )}

      {/* ── Empty state ───────────────────────────────────────────────────── */}
      {attrCategories.length === 0 && bundleGroups.length === 0 && effectiveTxId && (
        <div className="sf-empty-state sf-empty-state--sm">
          <p style={{ fontSize: 15 }}>✓ This product is ready to add to your quote.</p>
          <p style={{ marginTop: 8, fontSize: 13, color: 'var(--sf2-text-muted)' }}>
            Interactive configuration is available on the quote after adding.
          </p>
        </div>
      )}
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// ConfiguratorSummary — right-panel summary matching Salesforce configurator
// ─────────────────────────────────────────────────────────────────────────────

function ConfiguratorSummary({
  productName, quantity, pricing, loading,
  attrCategories, attrSelections,
  bundleGroups, compSelections, compPriceMap,
}) {
  const currency = pricing?.currency ?? compPriceMap[Object.keys(compPriceMap)[0]]?.CurrencyIsoCode ?? 'USD';

  // Flatten all attributes for summary display
  const allAttrs = attrCategories.flatMap(cat => cat.attributes);
  const selectedAttrs = allAttrs.filter(a => attrSelections[a.id] != null && attrSelections[a.id] !== '');

  // Compute per-component line amounts bucketed by PSM type.
  // Use PSM-aware prices from catalog (comp.defaultPsm) when available;
  // fall back to standard pricebook (compPriceMap).
  let oneTimeTotal = 0;
  let annualTotal  = 0;
  let monthlyTotal = 0;

  const groupSummaries = bundleGroups.map(group => ({
    ...group,
    selectedComponents: group.components
      .filter(c => compSelections[c.id]?.selected)
      .map(c => {
        const sel        = compSelections[c.id];
        const qty        = sel?.qty ?? 1;
        const psmData    = c.defaultPsm;
        const pricebook  = compPriceMap[c.id];
        const unitPrice  = psmData?.price ?? pricebook?.UnitPrice ?? 0;
        const priceCurr  = psmData?.currency ?? pricebook?.CurrencyIsoCode ?? currency;
        const psmType    = psmData?.psmType ?? 'OneTime';
        const amount     = unitPrice * qty;

        if (psmType === 'Annual')       annualTotal  += amount;
        else if (psmType === 'Monthly') monthlyTotal += amount;
        else                            oneTimeTotal += amount;

        return { ...c, qty, unitPrice, amount, psmType, priceCurrency: priceCurr };
      }),
  })).filter(g => g.selectedComponents.length > 0);

  // If we have headless/QLI-derived pricing and no PSM breakdown yet, use the total
  const hasPsmBreakdown = oneTimeTotal > 0 || annualTotal > 0 || monthlyTotal > 0;
  const displayOneTime  = hasPsmBreakdown ? oneTimeTotal : (pricing?.totalPrice ?? 0);
  const displayAnnual   = hasPsmBreakdown ? annualTotal  : null;
  const displayMonthly  = hasPsmBreakdown ? monthlyTotal : null;

  return (
    <div className="sf-config-summary" style={{ padding: 0, height: '100%', display: 'flex', flexDirection: 'column' }}>

      {/* Summary header */}
      <div style={{ padding: '16px 20px', borderBottom: '1px solid var(--sf2-border, #e5e7eb)' }}>
        <h3 style={{ fontSize: 18, fontWeight: 400, color: 'var(--sf2-text, #111)', margin: 0 }}>
          Summary
        </h3>
      </div>

      <div style={{ flex: 1, overflowY: 'auto', padding: '16px 20px' }}>

        {/* Product name + qty/amount row */}
        <div style={{ fontWeight: 700, fontSize: 14, marginBottom: 8 }}>{productName}</div>
        <div style={{
          display: 'grid', gridTemplateColumns: '1fr auto',
          background: 'var(--sf2-surface-alt, #f3f4f6)',
          padding: '8px 10px', borderRadius: 4, marginBottom: 16, fontSize: 13,
        }}>
          <div>
            <div style={{ color: 'var(--sf2-text-muted)', fontSize: 11, marginBottom: 2 }}>Quantity</div>
            <div>{quantity}</div>
          </div>
          <div style={{ textAlign: 'right' }}>
            <div style={{ color: 'var(--sf2-text-muted)', fontSize: 11, marginBottom: 2 }}>Net Amount</div>
            <div>{loading ? '…' : pricing ? formatCurrency(displayOneTime, currency) : '$0.00'}</div>
          </div>
        </div>

        {/* Attributes section */}
        {selectedAttrs.length > 0 && (
          <div style={{ marginBottom: 16 }}>
            <div style={{ fontSize: 13, fontWeight: 700, marginBottom: 8 }}>Attributes</div>
            {selectedAttrs.map(attr => {
              const raw = attrSelections[attr.id];
              const display = attr.values.find(v => v.code === raw)?.display ?? raw;
              return (
                <div key={attr.id} style={{
                  display: 'flex', gap: 6, fontSize: 13,
                  padding: '5px 0', borderBottom: '1px solid var(--sf2-border, #e5e7eb)',
                }}>
                  <span style={{ fontWeight: 600 }}>{attr.name}</span>
                  <span style={{ color: 'var(--sf2-text, #111)' }}>{display}</span>
                </div>
              );
            })}
          </div>
        )}

        {/* PCG sections with selected components */}
        {groupSummaries.map(group => (
          <div key={group.id} style={{ marginBottom: 16 }}>
            <div style={{ fontSize: 13, fontWeight: 700, marginBottom: 8 }}>{group.name}</div>
            {group.selectedComponents.map(comp => (
              <div key={comp.id} style={{
                border: '1px solid var(--sf2-border, #e5e7eb)',
                borderRadius: 6, padding: '10px 12px', marginBottom: 6,
              }}>
                <div style={{ color: 'var(--sf2-primary, #0176d3)', fontSize: 13, fontWeight: 600, marginBottom: 8 }}>
                  {comp.name}
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', fontSize: 12, gap: 4 }}>
                  <div>
                    <div style={{ color: 'var(--sf2-text-muted)', marginBottom: 2 }}>Quantity</div>
                    <div style={{ fontWeight: 500 }}>{comp.qty}</div>
                  </div>
                  <div style={{ textAlign: 'center' }}>
                    <div style={{ color: 'var(--sf2-text-muted)', marginBottom: 2 }}>Net Unit Price</div>
                    <div style={{ color: 'var(--sf2-primary, #0176d3)', textDecoration: 'underline' }}>
                      {formatCurrency(comp.unitPrice, comp.priceCurrency)}
                    </div>
                  </div>
                  <div style={{ textAlign: 'right' }}>
                    <div style={{ color: 'var(--sf2-text-muted)', marginBottom: 2 }}>Net Amount</div>
                    <div style={{ fontWeight: 600 }}>
                      {formatCurrency(comp.amount, comp.priceCurrency)}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ))}

        {loading && (
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, color: 'var(--sf2-text-muted)', fontSize: 13, marginBottom: 12 }}>
            <Spinner size="sm" /> Calculating price…
          </div>
        )}
      </div>

      {/* Totals pinned at bottom */}
      <div style={{
        padding: '14px 20px', borderTop: '2px solid var(--sf2-border, #e5e7eb)',
        background: 'var(--sf2-surface, #fff)',
        display: 'flex', flexDirection: 'column', gap: 6,
      }}>
        {/* One-Time Total — show when > 0 or when no PSM breakdown available */}
        {(displayOneTime > 0 || (!displayAnnual && !displayMonthly)) && (
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', fontWeight: 700, fontSize: 14 }}>
            <span style={{ color: 'var(--sf2-text-muted)', fontSize: 12 }}>One Time Total</span>
            <span style={{ fontSize: 16 }}>{loading ? '—' : formatCurrency(displayOneTime, currency)}</span>
          </div>
        )}
        {displayAnnual != null && displayAnnual > 0 && (
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', fontWeight: 700, fontSize: 14 }}>
            <span style={{ color: 'var(--sf2-text-muted)', fontSize: 12 }}>Annual Total</span>
            <span style={{ fontSize: 16, color: '#059669' }}>{loading ? '—' : formatCurrency(displayAnnual, currency)}</span>
          </div>
        )}
        {displayMonthly != null && displayMonthly > 0 && (
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', fontWeight: 700, fontSize: 14 }}>
            <span style={{ color: 'var(--sf2-text-muted)', fontSize: 12 }}>Monthly Total</span>
            <span style={{ fontSize: 16, color: '#7c3aed' }}>{loading ? '—' : formatCurrency(displayMonthly, currency)}</span>
          </div>
        )}
      </div>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// AttributeTabs — tabbed attribute categories with radio buttons for picklists
// ─────────────────────────────────────────────────────────────────────────────

function AttributeTabs({ categories, selections, onChange }) {
  const [activeIdx, setActiveIdx] = useState(0);
  if (!categories?.length) return null;
  const cat = categories[Math.min(activeIdx, categories.length - 1)];

  return (
    <div>
      {/* Tab bar */}
      <div style={{
        display: 'flex', gap: 0,
        borderBottom: '1px solid var(--sf2-border, #e5e7eb)', marginBottom: 12,
      }}>
        {categories.map((c, i) => (
          <button
            key={c.id ?? c.code}
            onClick={() => setActiveIdx(i)}
            style={{
              background: 'none', border: 'none', cursor: 'pointer',
              padding: '8px 14px', fontSize: 13, fontWeight: 500,
              color: i === activeIdx ? 'var(--sf2-primary, #0176d3)' : 'var(--sf2-text, #444)',
              borderBottom: i === activeIdx
                ? '2px solid var(--sf2-primary, #0176d3)'
                : '2px solid transparent',
              marginBottom: -1, whiteSpace: 'nowrap',
            }}
          >
            {c.name}
          </button>
        ))}
      </div>

      {/* Active category attributes */}
      <div style={{ paddingBottom: 4 }}>
        {cat.attributes.map(attr => (
          <div key={attr.id} style={{ marginBottom: 14 }}>
            <label style={{ fontSize: 13, fontWeight: 600, display: 'block', marginBottom: 6 }}>
              {attr.name}
              {attr.isRequired && (
                <span style={{ color: 'var(--sf2-danger, #c0392b)', marginLeft: 3 }}>*</span>
              )}
            </label>

            {attr.values.length > 0 ? (
              /* Picklist → radio buttons (matches Salesforce configurator UI) */
              <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                {attr.values.map(v => (
                  <label key={v.code} style={{ display: 'flex', alignItems: 'center', gap: 8, cursor: 'pointer', fontSize: 13 }}>
                    <input
                      type="radio"
                      name={`attr-${attr.id}`}
                      value={v.code}
                      checked={(selections[attr.id] ?? '') === v.code}
                      onChange={() => onChange(attr.id, v.code)}
                      style={{ width: 15, height: 15, accentColor: '#0176d3' }}
                    />
                    {v.display}
                  </label>
                ))}
              </div>
            ) : (
              /* Free-text / numeric */
              <input
                type={attr.dataType === 'Number' ? 'number' : 'text'}
                value={selections[attr.id] ?? ''}
                onChange={e => onChange(attr.id, e.target.value)}
                placeholder={attr.dataType === 'Number' ? '0' : 'Enter value…'}
                style={{
                  border: '1px solid var(--sf2-border, #d1d5db)', borderRadius: 6,
                  padding: '6px 10px', fontSize: 13,
                  background: 'var(--sf2-surface, #fff)', color: 'var(--sf2-text, #111)',
                  width: '100%', maxWidth: 220,
                }}
              />
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// ComponentGroupTabs — PCG-tabbed component selector
// ─────────────────────────────────────────────────────────────────────────────

function ComponentGroupTabs({ groups, selections, priceMap, onChange }) {
  const [activeIdx, setActiveIdx] = useState(0);
  if (!groups?.length) return null;
  const group = groups[Math.min(activeIdx, groups.length - 1)];

  return (
    <div>
      {/* Tab bar */}
      <div style={{
        display: 'flex', gap: 0, flexWrap: 'wrap',
        borderBottom: '1px solid var(--sf2-border, #e5e7eb)', marginBottom: 0,
      }}>
        {groups.map((g, i) => (
          <button
            key={g.id ?? g.code}
            onClick={() => setActiveIdx(i)}
            style={{
              background: 'none', border: 'none', cursor: 'pointer',
              padding: '8px 14px', fontSize: 13, fontWeight: 600,
              color: i === activeIdx ? 'var(--sf2-primary, #0176d3)' : 'var(--sf2-text, #444)',
              borderBottom: i === activeIdx
                ? '2px solid var(--sf2-primary, #0176d3)'
                : '2px solid transparent',
              marginBottom: -1, whiteSpace: 'nowrap',
            }}
          >
            {g.name}
          </button>
        ))}
      </div>

      {/* Component rows */}
      <div style={{ paddingTop: 12, display: 'flex', flexDirection: 'column', gap: 8 }}>
        {group.components.map(comp => (
          <ComponentRow
            key={comp.id}
            comp={comp}
            sel={selections[comp.id]}
            price={priceMap[comp.id]}
            onChange={onChange}
          />
        ))}
      </div>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// ComponentRow — individual bundle component row with checkbox, qty, price
// ─────────────────────────────────────────────────────────────────────────────

function ComponentRow({ comp, sel, price, onChange }) {
  const [expanded, setExpanded] = useState(false);

  const isChecked = sel?.selected ?? (comp.isDefault || comp.isRequired);
  const qty       = sel?.qty ?? comp.defaultQty ?? 1;

  // Use PSM-aware price from catalog API (comp.defaultPsm) if available,
  // fall back to standard pricebook flat price (price.UnitPrice).
  const psmData   = comp.defaultPsm ?? null;
  const unitPrice = psmData?.price ?? price?.UnitPrice ?? null;
  const currency  = psmData?.currency ?? price?.CurrencyIsoCode ?? 'USD';
  const lineTotal = unitPrice != null ? unitPrice * qty : null;

  // PSM type badge styling
  const psmType = psmData?.psmType ?? 'OneTime';
  const psmLabel = psmType === 'Annual' ? 'Annual' : psmType === 'Monthly' ? 'Monthly' : 'One-Time';
  const psmColors = {
    Annual:   { bg: '#ecfdf5', color: '#059669' },
    Monthly:  { bg: '#f5f3ff', color: '#7c3aed' },
    'One-Time': { bg: '#eff6ff', color: '#2563eb' },
  };
  const { bg: psmBg, color: psmColor } = psmColors[psmLabel] ?? psmColors['One-Time'];

  return (
    <div style={{
      border: `1px solid ${isChecked ? '#2563eb' : 'var(--sf2-border, #e5e7eb)'}`,
      borderRadius: 8,
      background: isChecked ? 'rgba(37, 99, 235, 0.04)' : 'var(--sf2-surface, #fff)',
      overflow: 'hidden',
      transition: 'border-color .15s, background .15s',
    }}>
      {/* Main row */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '10px 14px' }}>

        {/* Checkbox */}
        <input
          type="checkbox"
          checked={isChecked}
          disabled={comp.isRequired}
          onChange={e => onChange(comp.id, { selected: e.target.checked })}
          style={{
            width: 16, height: 16, flexShrink: 0,
            cursor: comp.isRequired ? 'default' : 'pointer',
            accentColor: '#2563eb',
          }}
        />

        {/* Component name + PSM badge */}
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{
            fontSize: 13, fontWeight: 600,
            color: 'var(--sf2-text, #111)',
            whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis',
          }}>
            {comp.name}
            {comp.isRequired && (
              <span style={{ marginLeft: 6, fontSize: 10, fontWeight: 400, color: 'var(--sf2-text-muted)' }}>
                required
              </span>
            )}
          </div>
          {/* PSM type badge — only show when price exists so it's meaningful */}
          {unitPrice != null && (
            <span style={{
              display: 'inline-block', marginTop: 2,
              fontSize: 10, fontWeight: 600, lineHeight: 1.4,
              padding: '1px 7px', borderRadius: 99,
              background: psmBg, color: psmColor,
            }}>
              {psmLabel}
            </span>
          )}
        </div>

        {/* Quantity — spinner when selected+editable, static label otherwise */}
        {isChecked && comp.isQuantityEditable ? (
          <input
            type="number" min="1" value={qty}
            onChange={e => onChange(comp.id, { qty: Math.max(1, parseInt(e.target.value) || 1) })}
            style={{
              width: 54, border: '1px solid var(--sf2-border, #d1d5db)',
              borderRadius: 5, padding: '3px 6px', fontSize: 13, textAlign: 'center',
              background: 'var(--sf2-surface, #fff)', color: 'var(--sf2-text, #111)',
            }}
          />
        ) : (
          <span style={{
            width: 54, textAlign: 'center', fontSize: 13,
            color: isChecked ? 'var(--sf2-text, #111)' : 'var(--sf2-text-muted)',
          }}>
            {qty}
          </span>
        )}

        {/* Line total */}
        {lineTotal != null ? (
          <span style={{
            fontSize: 13, fontWeight: isChecked ? 700 : 400,
            minWidth: 90, textAlign: 'right', flexShrink: 0,
            color: isChecked ? 'var(--sf2-text, #111)' : 'var(--sf2-text-muted)',
          }}>
            {formatCurrency(lineTotal, currency)}
          </span>
        ) : (
          <span style={{ minWidth: 90, textAlign: 'right', flexShrink: 0, fontSize: 11, color: 'var(--sf2-text-muted)' }}>
            —
          </span>
        )}

        {/* Expand chevron (only when description exists) */}
        {comp.description && (
          <button
            onClick={() => setExpanded(x => !x)}
            style={{
              background: 'none', border: 'none', cursor: 'pointer',
              color: 'var(--sf2-text-muted)', padding: '0 2px',
              fontSize: 13, lineHeight: 1, flexShrink: 0,
            }}
            title={expanded ? 'Collapse' : 'Expand'}
          >
            {expanded ? '▲' : '▼'}
          </button>
        )}
      </div>

      {/* Expanded description */}
      {expanded && comp.description && (
        <div style={{
          padding: '0 14px 10px 40px', fontSize: 12,
          color: 'var(--sf2-text-muted)', lineHeight: 1.55,
          borderTop: '1px solid var(--sf2-border, #e5e7eb)',
          paddingTop: 8, marginTop: 0,
        }}>
          {comp.description}
        </div>
      )}
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// Helpers
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Extract pricing from the headless Get response transaction tree.
 * SalesTransactionItem records carry TotalPrice / UnitPrice / CurrencyIsoCode.
 */
function extractHeadlessPricing(txData) {
  if (!txData) return null;
  const stList = txData.SalesTransaction ?? txData.salesTransaction ?? [];
  let totalPrice = 0;
  let currency = 'USD';
  let found = false;

  for (const st of stList) {
    // Top-level transaction total
    const stTotal = st.TotalAmount ?? st.totalAmount ?? st.GrandTotalAmount ?? st.grandTotalAmount;
    if (stTotal != null) {
      return {
        totalPrice: stTotal,
        unitPrice:  null,
        annualTotal:  null,
        oneTimeTotal: null,
        currency: st.CurrencyIsoCode ?? st.currencyIsoCode ?? 'USD',
      };
    }

    // Sum up line items if no header total
    const items = st.SalesTransactionItem ?? st.salesTransactionItem ?? [];
    for (const item of items) {
      const p = item.TotalPrice ?? item.totalPrice ?? item.UnitPrice ?? item.unitPrice;
      if (p != null) {
        totalPrice += Number(p);
        currency = item.CurrencyIsoCode ?? item.currencyIsoCode ?? currency;
        found = true;
      }
    }
  }

  if (found) return { totalPrice, unitPrice: null, annualTotal: null, oneTimeTotal: null, currency };
  return null;
}

/**
 * Extract the first SalesTransactionItem id from the headless Get transaction tree.
 * Used to identify the primary line item for quantity mutations.
 */
function extractFirstLineItemId(txData) {
  if (!txData) return null;
  const stList = txData.SalesTransaction ?? txData.salesTransaction ?? [];
  for (const st of stList) {
    const items = st.SalesTransactionItem ?? st.salesTransactionItem ?? [];
    if (items.length > 0) return items[0].id ?? items[0].Id ?? null;
  }
  return null;
}

/**
 * Extract a flat list of SalesTransactionItems from the headless Get response.
 * The transaction tree is: { SalesTransaction: [{ SalesTransactionItem: [...] }] }
 */
function parseSalesTransactionItems(txData) {
  if (!txData) return [];
  const stList = txData.SalesTransaction ?? txData.salesTransaction ?? [];
  const items  = [];
  for (const st of stList) {
    const stiList = st.SalesTransactionItem ?? st.salesTransactionItem ?? [];
    for (const sti of stiList) {
      items.push(sti);
    }
  }
  return items;
}

/**
 * Extract bundle components from CPQ product details response.
 *
 * The v66 product details API uses the SINGULAR key `productRelatedComponent`
 * (not the plural `productRelatedComponents`). Each item may have a nested
 * `childProduct` object containing the product name/id.
 *
 * Lookup order:
 *   1. productRelatedComponent (singular) — actual v66 API field
 *   2. productRelatedComponents (plural)  — kept as fallback
 *   3. productComponentGroups             — groups that nest components inside
 *   4. childProducts                      — simple flat array fallback
 */
function parseBundleComponents(configData) {
  if (!configData) return [];

  // ── Primary: productRelatedComponent (singular) — v66 API field name ─────
  const relComponents = configData?.productRelatedComponent        // singular — actual API
    ?? configData?.productRelatedComponents                        // plural — fallback
    ?? configData?.relatedComponents
    ?? configData?.result?.productRelatedComponent
    ?? configData?.result?.productRelatedComponents
    ?? null;

  if (relComponents?.length) {
    return relComponents.map(c => {
      // Items may nest product details under a `childProduct` object
      const child = c.childProduct ?? c;
      return {
        id:        c.id ?? child.id ?? child.productId ?? c.childProductId,
        name:      child.name ?? child.productName ?? c.childProductName ?? c.name,
        quantity:  c.quantity ?? c.minQuantity ?? c.defaultQuantity,
        isRequired: c.isComponentRequired ?? c.isRequired ?? false,
      };
    });
  }

  // ── Secondary: productComponentGroups — components nested inside groups ───
  const groups = configData?.productComponentGroups
    ?? configData?.result?.productComponentGroups
    ?? [];
  if (groups.length) {
    const components = [];
    for (const group of groups) {
      const gc = group.components               // v66 API: direct product objects
        ?? group.productRelatedComponent        // singular fallback
        ?? group.productRelatedComponents       // plural fallback
        ?? [];
      for (const c of gc) {
        const child = c.childProduct ?? c;
        components.push({
          id:        c.id ?? child.id ?? child.productId,
          name:      child.name ?? child.productName ?? c.name,
          quantity:  c.quantity ?? c.minQuantity,
          isRequired: c.isComponentRequired ?? c.isRequired ?? false,
          groupName: group.name ?? group.groupName,
        });
      }
    }
    if (components.length) return components;
  }

  // ── Tertiary: childProducts — simple flat array ───────────────────────────
  const childProds = configData?.childProducts ?? configData?.result?.childProducts ?? [];
  return childProds.map(cp => ({
    id:        cp.productId ?? cp.id,
    name:      cp.name ?? cp.productName,
    quantity:  cp.quantity ?? cp.defaultQuantity,
    isRequired: cp.isRequired ?? false,
  }));
}

/**
 * Extract bundle component groups from CPQ product details response.
 * Returns an array of groups for grouped rendering:
 *   [{
 *     id, name, code, sequence,
 *     components: [{
 *       id, name, productCode, isRequired, isDefault, isQuantityEditable, defaultQty
 *     }]
 *   }]
 */
function parseBundleComponentGroups(configData) {
  const groups = configData?.productComponentGroups
    ?? configData?.result?.productComponentGroups
    ?? [];
  if (!groups.length) return [];
  return groups
    .filter(g => !g.isExcluded)
    .sort((a, b) => (a.sequence ?? 0) - (b.sequence ?? 0))
    .map(g => ({
      id:       g.id ?? g.productComponentGroupId ?? g.code,
      name:     decodeHtml(g.name ?? g.groupName ?? g.code ?? 'Components'),
      code:     g.code,
      sequence: g.sequence ?? 0,
      components: (g.components ?? g.productRelatedComponent ?? g.productRelatedComponents ?? [])
        .map(c => {
          // Normalize PSM-aware prices from the catalog product's prices[] array.
          // Each entry has: { price, pricingModel: { pricingModelType, frequency, ... }, isDefault }
          const rawPrices = c.prices ?? [];
          const psmPrices = rawPrices.map(pe => {
            const pm = pe.pricingModel ?? pe.PricingModel ?? {};
            return {
              price:     pe.price ?? pe.Price ?? pe.unitPrice ?? pe.UnitPrice ?? 0,
              currency:  pe.currencyCode ?? pe.currencyIsoCode ?? pe.CurrencyIsoCode ?? 'USD',
              psmType:   getPsmType(pm),
              psmName:   pe.pricingModel?.name ?? pe.name ?? null,
              isDefault: pe.isDefault ?? false,
            };
          });

          // Bundle components often have empty prices[] but do have productSellingModelOptions
          // which carries the selling model type. Derive PSM type from PSMO when prices[] is empty.
          const psmoList = c.productSellingModelOptions ?? [];
          const psmoPrices = psmPrices.length === 0
            ? psmoList.map(opt => {
                const psm = opt.productSellingModel ?? {};
                return {
                  price:     null,   // no per-PSM price in PSMO; price comes from compPriceMap
                  currency:  'USD',
                  psmType:   getPsmType(psm),
                  psmName:   psm.name ?? null,
                  isDefault: opt.isDefault ?? false,
                };
              })
            : [];

          const allPsmOptions = psmPrices.length > 0 ? psmPrices : psmoPrices;

          // Prefer Annual first (matches catalog card default), then isDefault, then first.
          const defaultPsm =
            allPsmOptions.find(p => p.psmType === 'Annual') ??
            allPsmOptions.find(p => p.isDefault) ??
            allPsmOptions[0] ??
            null;

          return {
            id:                 c.id ?? c.productId,
            name:               decodeHtml(c.name ?? c.productName),
            description:        decodeHtml(c.description ?? c.productDescription ?? null),
            productCode:        c.productCode ?? c.code,
            isRequired:         c.isComponentRequired ?? c.isRequired ?? false,
            isDefault:          c.isDefaultComponent ?? false,
            isQuantityEditable: c.isQuantityEditable ?? true,
            defaultQty:         c.productQuantity ?? c.quantity ?? 1,
            psmPrices,    // All PSM prices from catalog API
            defaultPsm,   // The default/primary PSM price entry
          };
        })
        .filter(c => c.id),
    }))
    .filter(g => g.components.length > 0);
}

/**
 * Extract attribute categories from the CPQ product details response.
 * Returns a normalised array:
 *   [{
 *     id, code, name,
 *     attributes: [{
 *       id, name, dataType, isRequired, sequence,
 *       values: [{ code, display }]   // empty for free-text attrs
 *     }]
 *   }]
 */
function parseAttributeCategories(configData) {
  const cats = configData?.attributeCategories ?? configData?.result?.attributeCategories ?? [];
  return cats.map(cat => ({
    id:   cat.attributeCategoryId ?? cat.id ?? cat.code,
    code: cat.code,
    name: cat.name,
    attributes: (cat.records ?? []).map(r => ({
      id:         r.attributeId ?? r.id ?? r.attributeCategoryId,
      name:       r.attributeNameOverride ?? r.name,
      dataType:   r.attributePickList?.dataType ?? r.dataType ?? 'Text',
      isRequired: r.isRequired ?? false,
      sequence:   r.sequence ?? 0,
      values: (r.attributePickList?.values ?? [])
        .sort((a, b) => (a.sequence ?? 0) - (b.sequence ?? 0))
        .map(v => ({ code: v.code, display: v.displayValue ?? v.name ?? v.code })),
    })).sort((a, b) => a.sequence - b.sequence),
  }));
}

/**
 * Parse the executePriceContext response to extract a total price.
 * The response shape varies; we try several known structures.
 * Returns { totalPrice, unitPrice, currency } or null.
 */
function parsePriceContextTotal(result) {
  if (!result) return null;

  // Shape 1: { pricedItems: [...], totalAmount, currencyIsoCode }
  if (result.totalAmount != null) {
    return {
      totalPrice: Number(result.totalAmount),
      unitPrice:  null,
      currency:   result.currencyIsoCode ?? result.currency ?? 'USD',
    };
  }

  // Shape 2: { output: { totalAmount, ... } }
  if (result.output?.totalAmount != null) {
    return {
      totalPrice: Number(result.output.totalAmount),
      unitPrice:  null,
      currency:   result.output.currencyIsoCode ?? 'USD',
    };
  }

  // Shape 3: array of priced line items — sum them up
  const items = result.pricedItems ?? result.lineItems ?? result.items ?? [];
  if (items.length) {
    const total = items.reduce((s, i) => s + Number(i.totalPrice ?? i.TotalPrice ?? i.amount ?? 0), 0);
    const currency = items[0]?.currencyIsoCode ?? items[0]?.currency ?? 'USD';
    return { totalPrice: total, unitPrice: null, currency };
  }

  // Shape 4: nested under result/response key
  const nested = result.result ?? result.response ?? result.data;
  if (nested) return parsePriceContextTotal(nested);

  return null;
}

/**
 * Decode common HTML entities that Salesforce APIs sometimes return in string fields.
 * React renders strings as plain text so &amp; etc. appear literally without this.
 */
function decodeHtml(str) {
  if (!str) return str;
  return str
    .replace(/&amp;/g, '&')
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .replace(/&nbsp;/g, ' ');
}

/**
 * Derive PSM bucket from a pricingModel object.
 * Returns 'OneTime' | 'Annual' | 'Monthly'.
 *
 * pricingModel.pricingModelType values: 'OneTime', 'TermDefined', 'Evergreen'
 * For TermDefined, pricingModel.frequency / occurrence / pricingTermUnit tells us
 * Annual vs Monthly.
 */
function getPsmType(pricingModel) {
  const type = (
    pricingModel?.pricingModelType ??
    pricingModel?.sellingModelType ??
    ''
  ).trim();
  if (!type || type === 'OneTime') return 'OneTime';
  if (type === 'Evergreen') return 'Monthly';
  if (type === 'TermDefined') {
    const freq = (
      pricingModel?.frequency ??
      pricingModel?.occurrence ??
      pricingModel?.pricingTermUnit ??
      ''
    ).toLowerCase();
    if (freq.includes('annual') || freq.includes('year')) return 'Annual';
    return 'Monthly';
  }
  return 'OneTime';
}
