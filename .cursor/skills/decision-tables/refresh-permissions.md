# Decision Tables - Who Can Refresh, and Through Which Surface

Detail behind Quick Rule 1 of [SKILL.md](SKILL.md). Read it when a refresh queues for one user
and not another, when a flow's refresh step faults, or before giving a persona refresh access.
Every row is a measurement on a 264 scratch build unless tagged otherwise; the permission
names are the ones the running user holds, not the ones a flow's author holds.

**The Refresh Decision Table action is admin-only, with measured exceptions.** It refreshed for
a non-admin in a flow running in System Context Without Sharing, in the Default-mode
`RLM_Refresh_Decision_Tables_Bulk` started from `without sharing` Apex, and in the repo's
contract- and order-activation flows (*In a flow, run mode decides…*, below). Otherwise it
queued only for a user with Modify All Data *and* Customize Application, whether run by the
flow action in a Default-mode autolaunched flow the user starts or by
`POST /services/data/v68.0/actions/standard/refreshDecisionTable` [Measured:
2026-11-18, 264, scratch, one org]. Modify All Data alone, Customize Application alone, each
of Rule Engine Designer, Salesforce Pricing Design Time User and `RLM_DecisionTableManager`
alone, and all three sets together, were refused. REST returned HTTP 400
`INSUFFICIENT_ACCESS_OR_READONLY` ("Unsupported action type: REFRESH_DECISION_TABLE"). A flow
took its fault path: "We couldn't execute the ... action element of the refreshDecisionTable
type. Review your action name and version and try again.", which
names no permission, so check both permissions on the running user. Two-of-three subsets of the
sets were not run [Measured: 2026-11-18, 264, scratch, one org]. A schedule-triggered flow ran as
the admin who deployed and scheduled it, not as Automated Process, and its refresh queued
[Measured: 2026-11-18, 264, scratch, one org]. Whether a later edit or activation by another user
changes the running user was not tested. [Open: whether a schedule-triggered flow refreshes when a
non-admin scheduled it]
**In a flow, run mode decides whether that check applies** [Measured: 2026-11-19, 264, scratch,
one org]. For a user with neither admin permission, a one-step autolaunched flow calling the
action took its fault path in Default mode and in System Context With Sharing, and refreshed
(`LastSyncDate` moved) in System Context Without Sharing. Started with `Flow.Interview`, the
Default-mode `RLM_Refresh_Decision_Tables_Bulk` queued nothing for that user from a `with
sharing` Apex class, as the Manager is, and queued from a `without sharing` one. The
contract-activation (record-triggered) and order-activation (Platform Event) flows set no run
mode, and both refreshed for that user. Activating a contract
(`RLM_Contract_Activation_Refresh_Pricing_Tables`) refreshed its three tables within 13 seconds;
the order-activation flow took about four minutes (above). Inferred: a Default-mode flow takes
its caller's context, and record-triggered and Platform Event flows run in system context without
sharing, which would explain both activation flows. Inferred: the check is skipped for any
running user in system context without sharing, so anyone who can start or trigger such a flow,
or call `without sharing` Apex that starts a Default-mode refresh flow, refreshes the tables it
names.
A Connect resource has a different gate: `POST /services/data/v68.0/connect/decision-table/refresh`
with `{"decisionTableId": "<Id>"}` returned 201 `Queued` for a user with Rule Engine Designer alone,
for one with Salesforce Pricing Design Time User alone, for one with Modify All Data and Customize
Application together and no designer set, and for the three-set user the action refused; a user with
none of these, or with either admin permission alone, got 403 `FUNCTIONALITY_NOT_ENABLED`
[Measured: 2026-11-18, 264, scratch, one org]. The 264 Help and developer guide document no such
resource, so use the action in build code, flows and tasks, and the route only for an ad-hoc API
refresh by a designer or Design Time user without both admin permissions. A second request while a
refresh of the same table was pending returned 201 with `status` `Failed` and no `errorMessage`
[Measured: 2026-11-18, 264, scratch, one org]. Don't resend: poll freshness. Whether the hourly
refresh limit returns the same shape is not established. Refreshes queued through the route moved
`LastIncrementalSyncDate`, not `LastSyncDate` [Measured: 2026-11-18, 264, scratch, one org]; the
request had no refresh-type field, and the type is chosen by the platform (*Release 264 chooses the
refresh type* in `lifecycle-and-refresh.md`). Versioned CSV tables were not tried.
**Setup's Refresh button** (a table's detail page, Setup → Decision Tables) calls an Aura action,
not the flow action. What follows was measured on an Active table [Measured: 2026-11-19, 264,
scratch, one org]. Every user needed read access to the table's source object: without it the
detail page opened two error dialogs that blame the source object's configuration, with no
button. Modify All Data plus Customize Application had that access with no permission set. The
measured table was a rate card table, whose source object is `RateCardEntry`; separate test users
(Standard User, no rating or pricing permission set) with only Customize Application, or only
Modify All Data, got `NOT_FOUND` from `sf sobject describe RateCardEntry`, and the one with both
could describe it [Measured: 2026-11-19, 264, scratch, one org]. Inferred: the page checks that
same read access. With that read access, the button showed for Customize Application or Modify
All Data, and the click admitted the same users as the Connect route above. Customize Application
alone, and Modify All Data alone, got the refusal toast ("We can't refresh the decision
table..."). Modify All Data plus Customize Application, and Customize Application plus Rule
Engine Designer or Salesforce Pricing Design Time User, refreshed (`LastIncrementalSyncDate`
moved, not `LastSyncDate`). Either designer set without Customize Application had no button. The
list page (Decision Tables in the Setup tree) showed for Modify All Data plus Customize
Application; Customize Application, Modify All Data, Rule Engine Designer, and Customize
Application with read access saw only Settings. Salesforce Pricing Design Time User, alone or
with Customize Application, and Rule Engine Designer with Customize Application, were not
checked.
**Sync Pricing Data** (Setup → Salesforce Pricing Setup) is gated separately [Measured:
2026-11-19, 264, scratch, one org; the same users]. It ran for Modify All Data plus Customize
Application (13 tables queued) and for Customize Application plus Salesforce Pricing Design Time
User (12). Customize Application, and Customize Application plus Rule Engine Designer, got "You
don't have access to Salesforce Pricing setup"; Modify All Data, and either designer set without
Customize Application, got "Page not found". Because Modify All Data alone gets "Page not found",
the page can't show whether it would pass the pricing check behind it. The pricing recipe API
can: `GET /services/data/v68.0/connect/core-pricing/recipe` returned `FUNCTIONALITY_NOT_ENABLED`
to the Standard User test users above with only Customize Application or only Modify All Data,
and recipes to the one with both [Measured: 2026-11-19, 264, scratch, one org]. So the pair, not
Modify All Data, passes that check; that the page uses the same check is inferred.
The Manager shows freshness to any user with `RLM_DecisionTableManager` but disables Refresh unless the user has both Modify All
Data and Customize Application [Repo: `RLM_DecisionTableManagerController.canRefreshTables`].

**After an in-org account reset** [Measured: 2026-11-26, 264, scratch, one org]: the decision-table
refresh the reset queues needs Modify All Data **and** Customize Application. An administrator
with Modify All Data and View All Data but without Customize Application completes the reset and
queues no refresh, so run the freshness check afterwards. The reset itself is admin-only
(Modify All Data and View All Data).

## The order-activation flow

The exception is the tables named in the order-activation flow
`RLM_Platform_Event_CreateAssetOrderEvent_Stamp_Asset_Renewal_Info` (the asset and
binding-object tables and `Commitment_based_Rate_Adjustment`), which that flow queues
for refresh on order activation. Its start element sets `flowRunAsUser` TriggeringUser
[Repo], and the flow ran as the user who activated the order: debug logs showed the event
process switch from Automated Process to that user before the flow ran, for an admin and
for a sales rep [Measured: 2026-11-18, 264, scratch, one org]. When the sales rep, without
Modify All Data or Customize Application, activated an order with the refresh queue empty,
every table the flow names refreshed within about four minutes (*Asset Action Source Entries
V2* moved `LastIncrementalSyncDate`, the other 13 `LastSyncDate`) [Measured: 2026-11-18, 264,
scratch, one org], so the admin check below didn't stop this flow. Inferred: although it runs as
the activating user, it runs in system context without sharing (*In a flow, run mode decides…*,
below).
*Asset Action Source Entries V2* still read Stale six minutes after one activation and an
amendment priced in that window was wrong [Measured: 2026-11-16, 264, scratch]: refresh once
(*Refreshing*), then poll until Fresh and don't re-trigger before the next change
(`asset-lifecycle-changes/verification.md` step 7). [Open: whether a busy refresh queue
explains that delay] See
`lifecycle-and-refresh.md` → *After editing setup data*.
