#!/usr/bin/env python3
"""stdio→HTTP MCP MULTIPLEX proxy — fronts BOTH ramp servers behind one connector (pack 099).

WHY: the cohort demo (standard `industries/revenue-cloud`, 14 tools) and the native-groups
path (`custom/rampdealsconnect`, placeSalesTransaction + cloneSalesTransaction) live on two
different MCP servers on the same org. This proxy exposes ALL of their tools through a SINGLE
Claude Code connector, routing each `tools/call` to the correct upstream by tool name, over
ONE warm ramp_auth token. It is the multi-server sibling of mcp_proxy.py (which pins one).

NO-REGRESSION DESIGN (why a pure-cohort session pays nothing for the native path):
  - `initialize` is answered LOCALLY (advertising only the `tools` capability) — no upstream
    round-trip, and Claude Code never calls prompts/resources list.
  - `tools/list` is served from the per-server DISK CACHE (toollist-<server>.json, written by
    mcp_proxy.py / primed once) and MERGED — instant, no gateway hit at startup.
  - each upstream's MCP session (initialize → notifications/initialized) is opened LAZILY, on
    the FIRST tools/call routed to it. A cohort-only run never opens the native upstream.
So the only gateway traffic in a cohort run is the actual cohort tools/call — same as the
single-server proxy. (Cohort e2e is LLM-bound; MCP is <10% of wall-clock — see AB-RECONCILIATION.)

CONFIG (.mcp.json / claude mcp add): one server entry, no SF_MCP_SERVER pin. The upstream set
is fixed below (SERVERS) but overridable via SF_MCP_SERVERS (comma list of gateway suffixes).
  {
    "mcpServers": {
      "revenue-cloud": {
        "command": "python3",
        "args": ["<abs>/tools/mcp_multiplex_proxy.py"],
        "env": {
          "SF_INSTANCE": "https://<my>.salesforce.com",
          "SF_CID": "<ECA consumer key>", "SF_CSEC": "<ECA consumer secret>"
        }
      }
    }
  }
Prereq: `python3 tools/ramp_auth.py login` ONCE (warm refresh token). Then non-interactive.

Env: SF_INSTANCE SF_CID [SF_CSEC optional]  [SF_MCP_SERVERS=industries/revenue-cloud,custom/rampdealsconnect]
     [SF_MCP_BASE | SF_MCP_BASES]
"""
import json, os, sys, threading, urllib.request, urllib.error

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))   # ramp_auth is a sibling in tools/
import ramp_auth  # noqa: E402

PROTOCOL = "2025-06-18"

# The upstreams fronted by this one connector. Order = merge precedence for tools/list.
SERVERS = ([s.strip() for s in os.environ["SF_MCP_SERVERS"].split(",") if s.strip()]
           if os.environ.get("SF_MCP_SERVERS") else
           ["industries/revenue-cloud", "custom/rampdealsconnect"])

# Gateway host selection — same policy as mcp_proxy.py. Single candidate => no startup probe.
_BASES = ([os.environ["SF_MCP_BASE"].rstrip("/")] if os.environ.get("SF_MCP_BASE") else
          [b.strip().rstrip("/") for b in os.environ["SF_MCP_BASES"].split(",")]
          if os.environ.get("SF_MCP_BASES") else
          ["https://api.salesforce.com/platform/mcp/v1"])

_base = None            # chosen gateway base (host), shared by all upstreams
_access = None          # warm token, minted once
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
            _access = ramp_auth.get_access_token(interactive=False, force=force)
        return _access


KIT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _state_dir():
    """Where the tool-list cache lives.

    A RELATIVE RAMP_AUTH_DIR resolves against the KIT ROOT, not the process cwd — a config
    file can then use a portable relative path without depending on how the client launched
    the server (the cwd of an MCP subprocess is client-defined and not guaranteed).
    """
    d = os.environ.get("RAMP_AUTH_DIR") or os.path.expanduser("~/.config/rlm-ramp")
    d = os.path.expanduser(d)
    if not os.path.isabs(d):
        d = os.path.join(KIT_ROOT, d)
    return d


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


def _pick_base_locked():
    global _base
    if _base:
        return _base
    if len(_BASES) == 1:
        _base = _BASES[0]; log(f"host {_base} (pinned, no probe)")
        return _base
    # Multiple candidates: probe with the first upstream to disambiguate (e.g. on/off Zscaler).
    for base in _BASES:
        try:
            st, _, _ = _http(f"{base}/{SERVERS[0]}",
                             {"jsonrpc": "2.0", "id": 0, "method": "initialize",
                              "params": {"protocolVersion": PROTOCOL, "capabilities": {},
                                         "clientInfo": {"name": "cc-mux", "version": "1.0"}}},
                             timeout=8)
            if st == 200:
                _base = base; log(f"host {base}")
                return base
        except Exception as e:
            log(f"host {base} unreachable: {e}")
    log("ABORT: no gateway host routed"); sys.exit(1)


def _http(url, body, sid=None, timeout=200, _retried=False):
    """One HTTP POST to the gateway. Returns (status, response_sid, body_text).

    On 401 the token is re-minted ONCE and the call replayed. An access token can age out
    mid-session (the proxy is long-lived — it outlives a token's lifetime on a long demo),
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


def _extract_json(raw):
    """Gateway answers application/json OR text/event-stream. Return the JSON-RPC object text."""
    raw = raw.strip()
    if raw.startswith("{"):
        return raw
    for ln in raw.splitlines():
        ln = ln.strip()
        if ln.startswith("data:"):
            ln = ln[5:].strip()
        if ln.startswith("{"):
            return ln
    return raw


def _open_upstream(server):
    """LAZY per-upstream MCP handshake: initialize -> notifications/initialized. Runs once.

    The SF gateway returns an EMPTY body on tools/list / tools/call until `initialized` is sent
    (live-confirmed, pack 091). We only pay this for a server the session actually uses.
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
                                        "clientInfo": {"name": "cc-mux", "version": "1.0"}}})
    if st != 200:
        log(f"upstream {server}: initialize HTTP {st}"); return
    _sessions[server] = sid
    # initialized notification (no id -> no response)
    _http(url, {"jsonrpc": "2.0", "method": "notifications/initialized"}, sid=sid)
    _opened.add(server)
    log(f"upstream {server} opened (session={sid})")


def _merged_toollist():
    """Merge each upstream's cached tools/list into one list, and build the name->server route.

    Reads ONLY the disk cache (no gateway). A server with no cache yet contributes nothing and
    logs a warning — prime it once via mcp_proxy.py or a probe. First writer of a name wins the
    route (SERVERS order = precedence); the two ramp servers do not share tool names.
    """
    global _route
    with _init_lock:
        return _merged_toollist_locked()


def _fetch_toollist(server):
    """Live tools/list from the gateway, used when the disk cache is cold.

    WHY (this overrides the cache-only rule above): a cache-only tools/list means a
    workstation that never ran --prime advertises ZERO tools, and the client reports a
    connected-but-useless server — a silent failure. Falling back to a live fetch makes a
    config file self-sufficient: no priming step to forget, nothing to copy between machines.
    The cache still short-circuits this on every warm start, so the fast path is unchanged.
    """
    _open_upstream(server)
    if server not in _opened:
        return None
    st, _, raw = _http(f"{_pick_base()}/{server}",
                       {"jsonrpc": "2.0", "id": 1, "method": "tools/list"},
                       sid=_sessions.get(server))
    if st != 200:
        log(f"WARN: live tools/list for {server} failed HTTP {st}")
        return None
    try:
        result = json.loads(_extract_json(raw))["result"]
    except Exception as e:
        log(f"WARN: could not parse live tools/list for {server}: {e}")
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
        result = None
        if os.path.exists(p):
            try:
                result = json.load(open(p))
            except Exception as e:
                log(f"WARN: unreadable cache for {server}: {e}")
        if not result:
            log(f"no tools/list cache for {server} — fetching live from the gateway")
            result = _fetch_toollist(server)
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
            "serverInfo": {"name": "revenue-cloud-mux", "version": "1.0.0"}}})

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
        url = f"{_pick_base()}/{server}"
        tlog("HTTP>", mid, f"{name} -> {server}")
        st, _, raw = _http(url, msg, sid=_sessions.get(server))
        tlog("HTTP<", mid, f"{name} http={st}")
        return _extract_json(raw)

    # anything else with an id (ping, etc.): forward to the first opened upstream, or error.
    if method == "ping":
        return json.dumps({"jsonrpc": "2.0", "id": mid, "result": {}})
    return json.dumps({"jsonrpc": "2.0", "id": mid, "error": {
        "code": -32601, "message": f"Method not supported by multiplexer: {method}"}})


def main():
    for k in ("SF_INSTANCE", "SF_CID"):   # SF_CSEC optional: PKCE, see ramp_auth._cid_csec
        if not os.environ.get(k):
            log(f"FATAL: {k} not set"); sys.exit(2)
    log(f"multiplexing {SERVERS} (threaded dispatch)")

    def _serve(msg):
        try:
            out = handle(msg)
        except Exception as e:
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

    WHY THIS EXISTS: the multiplexer only READS the per-server tools/list caches (so a cohort-only
    startup never hits the gateway). It does NOT populate a missing cache — that would reintroduce
    the startup round-trip the no-regression design forbids. The single-server mcp_proxy.py writes
    the cache for whatever server it's pinned to, so a workstation that only ran the COHORT setup
    has `toollist-industries_revenue-cloud.json` but NOT the native one — and the native tools would
    silently be absent from /mcp. This primes every server in SERVERS in one shot.

    Idempotent: overwrites with a fresh fetch. Requires SF_INSTANCE/SF_CID/SF_CSEC + a warm token
    (`ramp_auth.py login` once) + gateway reachability (Zscaler for test.api).
    """
    for k in ("SF_INSTANCE", "SF_CID"):   # SF_CSEC optional: PKCE, see ramp_auth._cid_csec
        if not os.environ.get(k):
            print(f"FATAL: {k} not set"); sys.exit(2)
    base = _pick_base()
    ok = True
    for server in SERVERS:
        url = f"{base}/{server}"
        # handshake, then tools/list
        st, sid, _ = _http(url, {"jsonrpc": "2.0", "id": 0, "method": "initialize",
                                 "params": {"protocolVersion": PROTOCOL, "capabilities": {},
                                            "clientInfo": {"name": "cc-mux-prime", "version": "1.0"}}})
        if st != 200:
            print(f"FAIL {server}: initialize HTTP {st}"); ok = False; continue
        _http(url, {"jsonrpc": "2.0", "method": "notifications/initialized"}, sid=sid)
        st, _, raw = _http(url, {"jsonrpc": "2.0", "id": 1, "method": "tools/list"}, sid=sid)
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
                  f"        export RAMP_MCP_STATE=\"$PWD/.ramp/state\"  (then re-run --prime)\n"
                  f"      or skip priming if {_cache_path(server)} already has {n} tools.")
            ok = False
    print("PRIME", "OK" if ok else "FAIL")
    sys.exit(0 if ok else 1)


# ---- offline self-test (no gateway, no token) --------------------------------
def _selftest():
    """Assert the merge + route table are correct from the disk caches. Exit 0 pass / 1 fail."""
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
