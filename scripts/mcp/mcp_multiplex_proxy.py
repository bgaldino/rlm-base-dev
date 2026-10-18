#!/usr/bin/env python3
"""stdio→HTTP MCP MULTIPLEX proxy — fronts BOTH Revenue Cloud MCP servers behind one connector.

WHY: the standard `industries/revenue-cloud` server (14 tools) and the custom
`custom/RLMSalesTransactions` server (placeSalesTransaction + cloneSalesTransaction) live on
two different MCP servers on the same org. This proxy exposes ALL of their tools through a
SINGLE Claude Code connector, routing each `tools/call` to the correct upstream by tool name,
over ONE warm mcp_auth token. With the custom server off (RLM_MCP_CUSTOM_SERVER=0) there is
one upstream, and write_connector_config.py skips this proxy except for client_credentials.

LOW-OVERHEAD DESIGN (a session that only uses the standard tools pays nothing for the custom server):
  - `initialize` is answered LOCALLY (advertising only the `tools` capability) — no upstream
    round-trip, and Claude Code never calls prompts/resources list.
  - `tools/list` is served from the per-server DISK CACHE (toollist-<server>.json, written by
    `--prime`) and MERGED — instant, no gateway hit on a warm start. A cold cache, or one
    older than TOOLLIST_MAX_AGE, is fetched live once and written back (see _fetch_toollist).
  - each upstream's MCP session (initialize → notifications/initialized) is opened LAZILY, on
    the FIRST tools/call routed to it (or by a cold- or stale-cache tools/list fetch). Otherwise
    a session that never calls a custom tool never opens that upstream.

CONFIG (.mcp.json / claude mcp add): one server entry. write_connector_config.py writes it with
SF_MCP_SERVERS fixed at write time (so a later RLM_MCP_CUSTOM_SERVER change needs a re-write).
Run by hand without SF_MCP_SERVERS, the upstream set comes from mcp_org.servers_for: hosted +
custom by default, hosted only with RLM_MCP_CUSTOM_SERVER=0. SF_MCP_SERVERS (comma list of
gateway suffixes, for this SF_INSTANCE) overrides both.
  {
    "mcpServers": {
      "revenue-cloud": {
        "command": "python3",
        "args": ["<abs>/scripts/mcp/mcp_multiplex_proxy.py"],
        "env": {
          "SF_INSTANCE": "https://<my>.salesforce.com",
          "SF_CID": "<ECA consumer key>", "SF_CSEC": "<ECA consumer secret>"
        }
      }
    }
  }
Prereq: `python3 scripts/mcp/mcp_auth.py login` ONCE (warm refresh token). Then non-interactive.

Env: SF_INSTANCE SF_CID [SF_CSEC optional]  [RLM_MCP_CUSTOM_SERVER=0]  [SF_MCP_SERVERS=<a/b,c/d>]
     [SF_MCP_BASE | SF_MCP_BASES]   default: org-pinned, derived from SF_INSTANCE (mcp_org.gateway_bases)
"""
import json, os, sys, threading, urllib.request, urllib.error

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))   # mcp_auth is a sibling in this directory
import mcp_auth  # noqa: E402
import mcp_org  # noqa: E402

PROTOCOL = "2025-06-18"

# The upstreams fronted by this one connector. Order = merge precedence for tools/list.
# Honours SF_MCP_SERVERS (for this SF_INSTANCE) and RLM_MCP_CUSTOM_SERVER.
SERVERS = [s.strip() for s in mcp_org.servers_for(os.environ.get("SF_INSTANCE", "")).split(",")
           if s.strip()]

# Gateway host selection. Single candidate => no startup probe. Without an explicit
# SF_MCP_BASE(S), derive the org-pinned base (plus any fallback) from SF_INSTANCE.
_BASES = ([os.environ["SF_MCP_BASE"].rstrip("/")] if os.environ.get("SF_MCP_BASE") else
          [b.strip().rstrip("/") for b in
           (os.environ.get("SF_MCP_BASES")
            or mcp_org.gateway_bases(os.environ.get("SF_INSTANCE", ""))).split(",")
           if b.strip()])

_base = None            # chosen gateway base (host), shared by all upstreams
_access = None          # warm token, minted once
_probe_failed = None    # (monotonic time, message) of the last failed host probe
_sessions = {}          # server suffix -> Mcp-Session-Id (set when the upstream is opened)
_opened = set()         # servers whose initialize+initialized handshake has run
_route = None           # tool name -> server suffix (built from the merged cache)

# ---- Concurrency (threaded dispatch; live-verified for the parallel-agent path) ----
# The read loop dispatches each request on its own thread so two subagents' blocking
# tools/call HTTP round-trips overlap instead of serializing on the stdin loop.
# urllib releases the GIL during the socket wait, so threads (not asyncio) suffice.
# Two locks protect the only shared mutable state:
#   _write_lock — serialize stdout writes so interleaved responses stay whole lines.
#   _init_lock  — guard the lazy one-time globals (_base/_access/_route + _open_upstream
#                 handshake) so two cold calls don't double-initialize an upstream.
# The blocking tools/call _http itself runs OUTSIDE _init_lock — that is the whole point.
_write_lock = threading.Lock()
_init_lock = threading.RLock()


def log(m):
    # stderr ONLY — stdout is the MCP stdio channel and must stay pure JSON-RPC.
    sys.stderr.write(f"[mcp_mux] {m}\n"); sys.stderr.flush()


# ---- Optional timing trace (off unless $MUX_TIMING_LOG is set; diagnostic only) ----
# Writes wall-clock RECV/SEND/HTTP markers to $MUX_TIMING_LOG so a live parallel run
# shows WHERE overlap dies: if two RECV lines arrive back-to-back before the first
# SEND, the client is streaming both calls (proxy can parallelize). If RECV #2 only
# lands after SEND #1, the CLIENT serialized and no proxy change helps. If the two
# HTTP spans don't overlap despite concurrent dispatch, the GATEWAY serialized.
import time as _time
_TLOG = os.environ.get("MUX_TIMING_LOG")


def tlog(ev, mid=None, extra=""):
    if not _TLOG:
        return
    try:
        with open(_TLOG, "a") as f:
            f.write(f"{_time.time():.4f} {ev:5} id={mid} {extra}\n")
    except Exception:
        pass


def _token(force=False):
    global _access
    with _init_lock:
        if _access is None or force:
            try:
                _access = mcp_auth.get_access_token(interactive=False, force=force)
            except SystemExit as e:
                # mcp_auth exits on a dead or unrefreshable token (it has already said why on
                # stderr). In serve mode this runs in a handler thread, where SystemExit would
                # end the thread with no JSON-RPC response and leave the client hanging.
                raise RuntimeError(f"no usable access token (mcp_auth exit {e.code}); "
                                   f"re-run mcp_auth.py login") from None
        return _access


REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _state_dir():
    """Where the tool-list cache lives.

    A RELATIVE RLM_MCP_AUTH_DIR resolves against the REPO ROOT, not the process cwd — a config
    file can then use a portable relative path without depending on how the client launched
    the server (the cwd of an MCP subprocess is client-defined and not guaranteed).
    """
    d = os.environ.get("RLM_MCP_AUTH_DIR") or os.path.expanduser("~/.config/rlm-mcp")
    d = os.path.expanduser(d)
    if not os.path.isabs(d):
        d = os.path.join(REPO_ROOT, d)
    return d


# A cached tools/list older than this is refetched, so a rebuilt or upgraded org's tools
# show up without a manual --prime. If that fetch fails, the stale list is still served.
TOOLLIST_MAX_AGE = 24 * 3600


def _cache_path(server):
    d = _state_dir()
    try:
        os.makedirs(d, mode=0o700, exist_ok=True)
    except OSError:
        pass                                  # live fetch still works; caching is optional
    return os.path.join(d, f"toollist-{server.replace('/', '_')}.json")


def _pick_base():
    """Choose the gateway base URL once. Single candidate => no probe (fast path)."""
    global _base
    with _init_lock:
        return _pick_base_locked()


_LIVE_FETCH = True      # live tools/list for a cold or stale cache; off under --selftest
_refresh_failed = set()  # servers whose stale cache failed to refresh; not retried this process
PROBE_RETRY_AFTER = 30  # seconds before a failed host probe is retried


def _pick_base_locked():
    global _base, _probe_failed
    if _base:
        return _base
    # Don't re-probe (and re-mint, rotating the refresh token) on every request after a failure.
    if _probe_failed and _time.monotonic() - _probe_failed[0] < PROBE_RETRY_AFTER:
        raise RuntimeError(_probe_failed[1])

    def mint(force):
        # Outside the per-base try below: a missing or dead token is an auth failure with its
        # own message, not N "unreachable" hosts. Remembered like any failed probe.
        global _probe_failed
        try:
            _token(force=force)
        except RuntimeError as e:
            _probe_failed = (_time.monotonic(), str(e))
            log(f"ABORT: {e}")
            raise

    if len(_BASES) == 1:
        # No probe: a token problem surfaces from the first _http call instead.
        _base = _BASES[0]; log(f"host {_base} (pinned, no probe)")
        return _base
    mint(False)
    # Multiple candidates: probe each to disambiguate (e.g. on/off Zscaler). Every base is tried
    # with the first upstream before any is tried with the next, so a base that serves the
    # first one wins; a later upstream decides only when no base serves the first (revenue-cloud
    # unserved without RevMCP while the custom server works). An unreachable host is skipped.
    # A base that answers 401 may just be the wrong base, so a probe does not re-mint per base
    # (each re-mint spends and rotates the refresh token). When some base answered 401 and none
    # answered 200, the token itself is suspect (revoked before expiry): re-mint once, re-probe.
    for attempt in (1, 2):
        seen = {base: [] for base in _BASES}
        for server in SERVERS:
            for base in _BASES:
                if None in seen[base]:
                    continue
                try:
                    st, _, _ = _http(f"{base}/{server}",
                                     {"jsonrpc": "2.0", "id": 0, "method": "initialize",
                                      "params": {"protocolVersion": PROTOCOL, "capabilities": {},
                                                 "clientInfo": {"name": "rlm-mcp-mux", "version": "1.0"}}},
                                     timeout=8, _retried=True)
                except Exception as e:
                    seen[base].append(None)
                    log(f"host {base} unreachable: {e}")
                    continue
                seen[base].append(st)
                if st == 200:
                    _base = base; log(f"host {base}")
                    return base
        statuses = [st for got in seen.values() for st in got]
        if attempt == 1 and 401 in statuses:
            log("a host answered 401 and none answered 200; re-minting the token once")
            mint(True)
            continue
        break
    # Raise, not sys.exit: in serve mode this runs in a handler thread, where SystemExit
    # would kill the thread without a JSON-RPC response and leave the client hanging.
    report = ", ".join(f"{b} -> " + "/".join(str(st or "unreachable") for st in got)
                       for b, got in seen.items())
    hint = " (401 after a fresh token: re-run mcp_auth.py login)" if 401 in statuses else ""
    message = f"no gateway host routed: {report}{hint}"
    log(f"ABORT: {message}")
    _probe_failed = (_time.monotonic(), message)
    raise RuntimeError(message)


def _http(url, body, sid=None, timeout=200, _retried=False):
    """One HTTP POST to the gateway. Returns (status, response_sid, body_text).

    On 401 the token is re-minted ONCE and the call replayed. An access token can age out
    mid-session (the proxy is long-lived — it outlives a token's lifetime),
    and without this the first call after expiry fails the build instead of self-healing.
    """
    h = {"Authorization": f"Bearer {_token()}", "Content-Type": "application/json",
         "Accept": "application/json, text/event-stream", "MCP-Protocol-Version": PROTOCOL}
    if sid:
        h["Mcp-Session-Id"] = sid
    req = urllib.request.Request(url, data=json.dumps(body).encode(), headers=h)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, resp.headers.get("Mcp-Session-Id"), resp.read().decode()
    except urllib.error.HTTPError as e:
        if e.code == 401 and not _retried:
            log("gateway 401 — re-minting the access token and retrying once")
            _token(force=True)
            return _http(url, body, sid=sid, timeout=timeout, _retried=True)
        return e.code, e.headers.get("Mcp-Session-Id"), e.read().decode()


def _rpc_messages(raw):
    """The JSON objects in a gateway body: application/json, or text/event-stream events.

    An SSE event's JSON can span several `data:` lines (joined with newlines), and a stream
    can carry notifications (progress, log messages) before the response.
    """
    raw = raw.strip()
    if raw.startswith("{"):
        chunks = [raw]
    else:
        chunks, data = [], []
        for ln in raw.splitlines() + [""]:
            if ln.startswith("data:"):
                data.append(ln[5:].lstrip())
            elif not ln.strip() and data:       # a blank line ends the event
                chunks.append("\n".join(data))
                data = []
    for chunk in chunks:
        try:
            obj = json.loads(chunk)
        except Exception:
            continue
        if isinstance(obj, dict):
            yield obj


def _response(raw, mid=None):
    """The JSON-RPC response in `raw` (result or error), preferring the one for `mid`, or None."""
    found = [o for o in _rpc_messages(raw)
             if o.get("jsonrpc") == "2.0" and ("result" in o or "error" in o)]
    for o in found:
        if mid is not None and o.get("id") == mid:
            return o
    return found[0] if found else None


def _extract_json(raw):
    """Gateway answers application/json OR text/event-stream. Return the JSON-RPC response text."""
    obj = _response(raw)
    return json.dumps(obj) if obj is not None else raw.strip()


def _call_response(mid, st, raw):
    """The client-facing response to a forwarded tools/call.

    A JSON-RPC response from upstream (result or error) is passed on, re-serialised onto one
    line (stdio framing is newline-delimited) and with this request's id (an upstream error
    may carry `"id": null`, which the client could never match). Anything else (an empty
    body, a Salesforce error array, HTML from a 403/429/500) is not valid JSON-RPC on the
    stdio channel: the client would hang or fail opaquely. Turn it into an error carrying
    this request's id instead.
    """
    obj = _response(raw, mid)
    if obj is not None:
        obj["id"] = mid
        return json.dumps(obj)
    detail = " ".join(raw.split())[:200] or "empty body"
    return json.dumps({"jsonrpc": "2.0", "id": mid, "error": {
        "code": -32603, "message": f"Upstream answered http={st} without a JSON-RPC response: {detail}"}})


def _open_upstream(server):
    """LAZY per-upstream MCP handshake: initialize -> notifications/initialized. Runs once.

    The SF gateway returns an EMPTY body on tools/list / tools/call until `initialized` is sent
    (live-confirmed). We only pay this for a server the session actually uses.
    """
    with _init_lock:
        if server in _opened:
            return
        _open_upstream_locked(server)


def _open_upstream_locked(server):
    base = _pick_base()
    url = f"{base}/{server}"
    st, sid, _ = _http(url, {"jsonrpc": "2.0", "id": 0, "method": "initialize",
                             "params": {"protocolVersion": PROTOCOL, "capabilities": {},
                                        "clientInfo": {"name": "rlm-mcp-mux", "version": "1.0"}}})
    if st != 200:
        log(f"upstream {server}: initialize HTTP {st}"); return
    # initialized notification (no id -> no JSON-RPC response, just a 2xx). Without it the
    # session stays uninitialised, so a failure leaves the server unopened, to retry next call.
    st, _, _ = _http(url, {"jsonrpc": "2.0", "method": "notifications/initialized"}, sid=sid)
    if not 200 <= (st or 0) < 300:
        log(f"upstream {server}: notifications/initialized HTTP {st}"); return
    _sessions[server] = sid
    _opened.add(server)
    log(f"upstream {server} opened (session={sid})")


def _merged_toollist():
    """Merge each upstream's cached tools/list into one list, and build the name->server route.

    Reads the disk cache; a server with no cache, or a stale one, is fetched live
    (_fetch_toollist). If that fails, a stale list is still served and not retried in this
    process; a server with no cache contributes nothing, with a warning. First writer of a name wins the
    route (SERVERS order = precedence); the two servers do not share tool names.
    """
    global _route
    with _init_lock:
        return _merged_toollist_locked()


def _fetch_toollist(server):
    """Live tools/list from the gateway, used when the disk cache is cold or stale.

    Disabled (returns None) when _LIVE_FETCH is False, which --selftest sets so it stays offline.

    WHY: a cache-only tools/list would mean a
    workstation that never ran --prime advertises ZERO tools, and the client reports a
    connected-but-useless server — a silent failure. Falling back to a live fetch makes a
    config file self-sufficient: no priming step to forget, nothing to copy between machines.
    The cache still short-circuits this on every warm start, so the fast path is unchanged.
    """
    if not _LIVE_FETCH:
        return None
    try:
        _open_upstream(server)
        if server not in _opened:
            return None
        st, _, raw = _http(f"{_pick_base()}/{server}",
                           {"jsonrpc": "2.0", "id": 1, "method": "tools/list"},
                           sid=_sessions.get(server))
    except Exception as e:  # one unreachable upstream must not empty the merged list
        log(f"WARN: live tools/list for {server} failed: {e}")
        return None
    if st != 200:
        log(f"WARN: live tools/list for {server} failed HTTP {st}")
        return None
    try:
        result = json.loads(_extract_json(raw))["result"]
    except Exception as e:
        log(f"WARN: could not parse live tools/list for {server}: {e}")
        return None
    if not result.get("tools"):
        log(f"WARN: live tools/list for {server} returned no tools — not cached")
        return None
    try:                                     # best effort — a read-only FS must not be fatal
        with open(_cache_path(server), "w") as f:
            json.dump(result, f)
    except OSError as e:
        log(f"note: could not cache tools/list for {server} ({e}) — refetching each start")
    return result


def _merged_toollist_locked():
    global _route
    tools, route, seen = [], {}, set()
    for server in SERVERS:
        p = _cache_path(server)
        result = stale = None
        if os.path.exists(p):
            try:
                result = json.load(open(p))
            except Exception as e:
                log(f"WARN: unreadable cache for {server}: {e}")
            if (result and server not in _refresh_failed
                    and _time.time() - os.path.getmtime(p) > TOOLLIST_MAX_AGE):
                stale, result = result, None
        if not result:
            log(f"{'stale' if stale else 'no'} tools/list cache for {server} — fetching live from the gateway")
            result = _fetch_toollist(server)
            if not result and stale:
                log(f"WARN: refresh of {server} failed — serving the stale cached tools/list")
                _refresh_failed.add(server)
                result = stale
        if not result:
            log(f"WARN: {server} contributed no tools")
            continue
        for t in result.get("tools", []):
            name = t.get("name")
            if not name or name in seen:
                if name in seen:
                    log(f"WARN: duplicate tool name {name!r} across upstreams — keeping first ({route.get(name)})")
                continue
            seen.add(name); route[name] = server; tools.append(t)
    _route = route
    log(f"merged {len(tools)} tools across {len(SERVERS)} upstreams: "
        + ", ".join(f"{s}={sum(1 for v in route.values() if v==s)}" for s in SERVERS))
    return tools


def handle(msg):
    """Map one client JSON-RPC message to a response string (or None for notifications)."""
    method = msg.get("method")
    mid = msg.get("id")

    # notifications from the client (initialized, cancelled, …): swallow — nothing upstream needs them.
    if "id" not in msg:
        return None

    if method == "initialize":
        # Answer locally. Advertise ONLY tools so the client never asks for prompts/resources.
        return json.dumps({"jsonrpc": "2.0", "id": mid, "result": {
            "protocolVersion": PROTOCOL,
            "capabilities": {"tools": {"listChanged": False}},
            "serverInfo": {"name": "rlm-mcp-mux", "version": "1.0.0"}}})

    if method == "tools/list":
        return json.dumps({"jsonrpc": "2.0", "id": mid, "result": {"tools": _merged_toollist()}})

    if method == "tools/call":
        name = (msg.get("params") or {}).get("name")
        server = (_route or {}).get(name)
        if server is None:
            # cache may be cold (route not built yet): build it, retry once.
            _merged_toollist()
            server = (_route or {}).get(name)
        if server is None:
            return json.dumps({"jsonrpc": "2.0", "id": mid, "error": {
                "code": -32601, "message": f"Unknown tool: {name}"}})
        _open_upstream(server)                       # lazy — first call to this upstream only
        if server not in _opened:
            # Handshake failed (logged by _open_upstream). The gateway answers an
            # un-initialized session with an empty body / error, so don't send a call that
            # is guaranteed to be invalid: tell the client now.
            return json.dumps({"jsonrpc": "2.0", "id": mid, "error": {
                "code": -32603,
                "message": f"Upstream {server} could not be initialized; tools/call not sent"}})
        url = f"{_pick_base()}/{server}"
        tlog("HTTP>", mid, f"{name} -> {server}")
        st, _, raw = _http(url, msg, sid=_sessions.get(server))
        tlog("HTTP<", mid, f"{name} http={st}")
        return _call_response(mid, st, raw)

    # anything else with an id (ping, etc.): forward to the first opened upstream, or error.
    if method == "ping":
        return json.dumps({"jsonrpc": "2.0", "id": mid, "result": {}})
    return json.dumps({"jsonrpc": "2.0", "id": mid, "error": {
        "code": -32601, "message": f"Method not supported by multiplexer: {method}"}})


def main():
    for k in ("SF_INSTANCE", "SF_CID"):   # SF_CSEC optional: PKCE, see mcp_auth._cid_csec
        if not os.environ.get(k):
            log(f"FATAL: {k} not set"); sys.exit(2)
    log(f"multiplexing {SERVERS} (threaded dispatch)")

    def _serve(msg):
        try:
            out = handle(msg)
        except BaseException as e:  # incl. SystemExit: always answer, or the client hangs
            log(f"handler error: {e}")
            out = json.dumps({"jsonrpc": "2.0", "id": msg.get("id"),
                              "error": {"code": -32603, "message": f"multiplexer: {e}"}})
        if out is not None:
            with _write_lock:
                tlog("SEND", msg.get("id"), msg.get("method"))
                sys.stdout.write(out + "\n"); sys.stdout.flush()

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except Exception:
            continue
        tlog("RECV", msg.get("id"), msg.get("method"))
        # Each request on its own thread: two subagents' blocking tools/call HTTP
        # round-trips overlap instead of serializing on this read loop. daemon so a
        # stuck upstream never blocks interpreter exit when stdin closes.
        threading.Thread(target=_serve, args=(msg,), daemon=True).start()


# ---- one-time cache priming (needs token + gateway) --------------------------
def _prime():
    """Fetch tools/list from EACH upstream and write its disk cache. Run ONCE per workstation.

    WHY THIS EXISTS: the multiplexer serves tools/list from the per-server caches, so a warm
    start never hits the gateway. A cold cache costs a live fetch on the first tools/list
    (_fetch_toollist); priming moves that round-trip off the client's startup and reports
    per-server failures legibly. This primes every server in SERVERS in one shot.

    Idempotent: overwrites with a fresh fetch. Requires SF_INSTANCE/SF_CID/SF_CSEC + a warm token
    (`mcp_auth.py login` once) + gateway reachability (Zscaler for test.api).
    """
    for k in ("SF_INSTANCE", "SF_CID"):   # SF_CSEC optional: PKCE, see mcp_auth._cid_csec
        if not os.environ.get(k):
            print(f"FATAL: {k} not set"); sys.exit(2)
    try:
        base = _pick_base()
    except RuntimeError as e:
        print(f"FATAL: {e}"); sys.exit(1)
    ok = True
    for server in SERVERS:
        url = f"{base}/{server}"
        # handshake, then tools/list
        st, sid, _ = _http(url, {"jsonrpc": "2.0", "id": 0, "method": "initialize",
                                 "params": {"protocolVersion": PROTOCOL, "capabilities": {},
                                            "clientInfo": {"name": "rlm-mcp-mux-prime", "version": "1.0"}}})
        if st != 200:
            print(f"FAIL {server}: initialize HTTP {st}"); ok = False; continue
        st, _, _ = _http(url, {"jsonrpc": "2.0", "method": "notifications/initialized"}, sid=sid)
        if not 200 <= (st or 0) < 300:
            print(f"FAIL {server}: notifications/initialized HTTP {st}"); ok = False; continue
        st, _, raw = _http(url, {"jsonrpc": "2.0", "id": 1, "method": "tools/list"}, sid=sid)
        if st != 200:
            print(f"FAIL {server}: tools/list HTTP {st}"); ok = False; continue
        try:
            obj = json.loads(_extract_json(raw))
            result = obj["result"]
            n = len(result.get("tools", []))
            if n == 0:
                print(f"FAIL {server}: tools/list empty (did initialized get sent?)"); ok = False; continue
        except Exception as e:
            print(f"FAIL {server}: could not parse tools/list: {e}"); ok = False; continue
        # Fetch succeeded (n tools in hand). A separate try so a blocked disk write is NOT
        # misreported as a parse failure — the common restricted-sandbox case, where ~/.config
        # is unwritable but the cache there may already be complete from a prior host run.
        try:
            with open(_cache_path(server), "w") as f:
                json.dump(result, f)
            print(f"ok: {server} -> {n} tools cached at {_cache_path(server)}")
        except OSError as e:
            print(f"FAIL {server}: fetched {n} tools but cache write blocked: {e}\n"
                  f"      sandbox? redirect the cache to a writable dir, e.g.:\n"
                  f"        export RLM_MCP_STATE=\"$PWD/.mcp-state/state\"\n"
                  f"        eval \"$(python3 scripts/mcp/mcp_org.py env <sf-alias>)\"   # re-derives RLM_MCP_AUTH_DIR\n"
                  f"        then re-run --prime (off macOS, also mcp_auth.py login: the token file moves too)\n"
                  f"      or skip priming if {_cache_path(server)} already has {n} tools.")
            ok = False
    print("PRIME", "OK" if ok else "FAIL")
    sys.exit(0 if ok else 1)


# ---- offline self-test (no gateway, no token) --------------------------------
def _selftest():
    """Assert the merge + route table are correct from the disk caches. Exit 0 pass / 1 fail."""
    global _LIVE_FETCH
    _LIVE_FETCH = False  # offline: a cold cache is skipped, never fetched (and never opens one)
    ok = True
    tools = _merged_toollist()
    names = [t["name"] for t in tools]
    # 1) no duplicate names
    if len(names) != len(set(names)):
        print("FAIL: duplicate tool names in merged list"); ok = False
    # 2) every tool routes to a server in SERVERS
    for n in names:
        if _route.get(n) not in SERVERS:
            print(f"FAIL: tool {n} routes to {_route.get(n)!r} (not in SERVERS)"); ok = False
    # 3) each cached upstream contributed at least one tool (if its cache exists)
    for s in SERVERS:
        if os.path.exists(_cache_path(s)):
            cnt = sum(1 for v in _route.values() if v == s)
            if cnt == 0:
                print(f"FAIL: upstream {s} has a cache but contributed 0 tools"); ok = False
            else:
                print(f"ok: {s} -> {cnt} tools")
        else:
            print(f"skip: {s} has no cache yet ({_cache_path(s)})")
    # 4) initialize is answered locally with tools capability
    init = json.loads(handle({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}))
    if "tools" not in init.get("result", {}).get("capabilities", {}):
        print("FAIL: initialize does not advertise tools capability"); ok = False
    else:
        print("ok: initialize advertises tools capability, answered locally")
    # 5) tools/list served locally with the merged set
    tl = json.loads(handle({"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}))
    if len(tl.get("result", {}).get("tools", [])) != len(names):
        print("FAIL: tools/list count mismatch"); ok = False
    else:
        print(f"ok: tools/list serves {len(names)} merged tools")
    # 6) unknown tool -> error, no upstream opened
    err = json.loads(handle({"jsonrpc": "2.0", "id": 3, "method": "tools/call",
                             "params": {"name": "definitelyNotATool", "arguments": {}}}))
    if "error" not in err:
        print("FAIL: unknown tool did not error"); ok = False
    elif _opened:
        print(f"FAIL: unknown tool opened an upstream: {_opened}"); ok = False
    else:
        print("ok: unknown tool -> error, no upstream opened (lazy invariant holds)")
    print("SELFTEST", "PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        _selftest()
    elif "--prime" in sys.argv:
        _prime()
    else:
        main()
