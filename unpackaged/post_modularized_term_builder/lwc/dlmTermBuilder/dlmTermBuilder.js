import { LightningElement, api } from "lwc";

/**
 * Modularized Delta Term Builder — thin all-in-one orchestrator.
 *
 * Lays out the three composable tiles (c/dlmNegotiationContext header, c/dlmTermsRail, and
 * c/dlmTermWorkspace) in the original app's two-column arrangement so the modularized build can be
 * dropped as a single block, exactly like the monolith c/dlTermBuilder. It carries NO wiring logic:
 * the tiles synchronize entirely over the DLM_TermBuilderChannel message channel. The only props it
 * forwards are the header's optional deep-link preselects (accountId / quoteRecordId); everything
 * else is configured per tile when they are placed individually on a Lightning page instead.
 */
export default class DlmTermBuilder extends LightningElement {
  // Optional deep-link preselects, passed straight through to the header tile. The header also
  // honors ?c__accountId= / ?c__quoteId= URL state on its own.
  @api accountId;
  @api quoteRecordId;
}
