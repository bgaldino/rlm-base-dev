#!/usr/bin/env python3
"""Portable, one-click-per-workstation OAuth for the ramp-MCP planner (pack 094 / 093).

WHY THIS EXISTS
  The SF MCP gateway rejects the `sf` CLI's own session token (401 "Invalid token" —
  probed 2026-07-31 on both test.api and api hosts): the gateway needs a token minted
  with the `mcp_api` OAuth scope, which the CLI connected app does not carry. So the
  ECA + user-OAuth path is genuinely required — there is no CLI-token shortcut.

  What we CAN remove is repeating the browser dance. `ramp_planner.oauth()` requested
  `refresh_token` scope but threw the refresh token away (access token in memory only),
  so every run re-opened the browser. The ECA's refresh-token policy on this org is
  SpecificLifetime / 8760 Days (~24 years), so a cached refresh token is effectively
  permanent. This helper does the PKCE loopback ONCE, caches the refresh token, and
  thereafter mints access tokens silently — the planner (and any build-automation
  standup, pack 093) becomes non-interactive after a single per-workstation login.

STORAGE (portable, no new pip dependency)
  - macOS: the login Keychain via the `security` CLI (generic password).
  - elsewhere (Linux / devcontainer): a 0600 file under $RAMP_AUTH_DIR or ~/.config/rlm-ramp.
  The secret stored is the REFRESH TOKEN only (never the access token, never the
  consumer secret). Cache key = org instance host + ECA consumer key, so multiple
  orgs / ECAs don't collide.

TWO MODES
  default                     authorization_code + PKCE, refresh token cached (below).
                              One browser click per workstation, then silent.
  SF_AUTH_MODE=client_credentials + SF_CSEC
                              mint from consumer key + secret. No browser, no refresh
                              token, no Keychain, no disk state — so the same config works
                              on any workstation with nothing to log in to. Needs the ECA's
                              client credentials flow enabled in the OAuth POLICY plus a
                              clientCredentialsFlowUser. See _client_credentials().

USAGE
  export SF_CID=...  SF_INSTANCE=https://<my>.salesforce.com     # SF_CSEC optional (PKCE)

  Multi-org: don't set these by hand. One alias resolves everything —
      eval "$(python3 tools/ramp_org.py env <sf-alias>)"          # or RAMP_MCP_ORG=<alias>
  which also namespaces RAMP_AUTH_DIR per org id, so two orgs never share a tool-list cache.
  python3 tools/ramp_auth.py login       # one-time browser consent, caches refresh token
  python3 tools/ramp_auth.py token        # prints a fresh access token (for scripts)
  python3 tools/ramp_auth.py status       # is a refresh token cached for this org/ECA?
  python3 tools/ramp_auth.py logout        # forget the cached refresh token

  As a library (what ramp_planner uses):
      from ramp_auth import get_access_token
      access = get_access_token()          # silent if cached; else prints OPEN_THIS_URL and waits
"""
import base64, hashlib, http.server, json, os, secrets, socket, subprocess, sys, threading, time
import urllib.parse, urllib.request, urllib.error

PORT   = int(os.environ.get("SF_PORT", "8080"))
REDIR  = f"http://localhost:{PORT}/callback"
SCOPE  = "mcp_api refresh_token api"
SERVICE = "rlm-ramp-mcp"                      # keychain service / file namespace

# Auth mode. "" (default) = authorization_code + PKCE with a cached, rotating refresh token.
# "client_credentials" = mint straight from consumer key + secret: no browser, no refresh
# token, no Keychain, nothing cached on disk — so a config file alone is portable to any
# workstation. Explicit rather than inferred from SF_CSEC's presence, because SF_CSEC is
# also a legitimate (optional) input to the PKCE path and must not silently switch modes.
MODE   = os.environ.get("SF_AUTH_MODE", "").strip().lower().replace("-", "_")
CLIENT_CREDENTIALS = MODE in ("client_credentials", "cc")


def _inst():
    inst = os.environ.get("SF_INSTANCE", "").rstrip("/")
    if not inst:
        sys.stderr.write("FATAL: SF_INSTANCE not set\n"); raise SystemExit(2)
    return inst


def _cid_csec():
    """SF_CID is required; SF_CSEC is OPTIONAL.

    The ECA sets `isConsumerSecretOptional=true`, so authorization_code + PKCE (S256)
    completes with the consumer key alone — verified live on 264-upgrade with SF_CSEC
    unset. Dropping the secret is what lets an org be selected by alias alone
    (`RAMP_MCP_ORG`, see ramp_org.py) with no per-org secret in any config file.
    A secret is still honoured when supplied, for ECAs configured to require one.
    """
    cid, csec = os.environ.get("SF_CID"), os.environ.get("SF_CSEC")
    if not cid:
        sys.stderr.write("FATAL: SF_CID (ECA consumer key) must be set\n")
        raise SystemExit(2)
    return cid, (csec or None)


def _drop_none(d):
    """Omit absent form fields. Sending `client_secret=` (empty) is NOT the same as
    omitting it — Salesforce rejects the empty value, so the key must disappear."""
    return {k: v for k, v in d.items() if v is not None}


def _account(inst, cid):
    """Cache key: stable per (org host, ECA). Keeps multiple orgs/ECAs from colliding."""
    host = urllib.parse.urlparse(inst).netloc or inst
    return f"{host}|{cid}"


# ---- storage backends -------------------------------------------------------
def _is_macos():
    return sys.platform == "darwin"


def _file_path():
    d = os.environ.get("RAMP_AUTH_DIR") or os.path.expanduser("~/.config/rlm-ramp")
    os.makedirs(d, mode=0o700, exist_ok=True)
    return os.path.join(d, "refresh-tokens.json")


def _raw_get(account):
    if _is_macos():
        r = subprocess.run(["security", "find-generic-password", "-s", SERVICE,
                            "-a", account, "-w"], capture_output=True, text=True)
        return r.stdout.strip() if r.returncode == 0 and r.stdout.strip() else None
    p = _file_path()
    if not os.path.exists(p):
        return None
    try:
        return json.load(open(p)).get(account)
    except Exception:
        return None


def _raw_set(account, value):
    if _is_macos():
        # -U updates if present; label + service + account identify the item.
        subprocess.run(["security", "add-generic-password", "-U", "-s", SERVICE,
                        "-a", account, "-l", f"{SERVICE} auth", "-w", value],
                       capture_output=True, text=True, check=True)
        return
    p = _file_path()
    data = {}
    if os.path.exists(p):
        try:
            data = json.load(open(p))
        except Exception:
            data = {}
    data[account] = value
    fd = os.open(p, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w") as f:
        json.dump(data, f)
    os.chmod(p, 0o600)


def _store_get(account):
    """Return the stored auth blob {refresh_token, access_token, access_expiry}.

    Backward-compatible: a bare-string value (old format = just the refresh token) is read as
    {refresh_token: <str>}. Returns {} if nothing stored.
    """
    raw = _raw_get(account)
    if not raw:
        return {}
    try:
        blob = json.loads(raw)
        return blob if isinstance(blob, dict) else {"refresh_token": raw}
    except Exception:
        return {"refresh_token": raw}   # legacy bare token


def _store_set(account, blob):
    _raw_set(account, json.dumps(blob))


def _store_del(account):
    if _is_macos():
        subprocess.run(["security", "delete-generic-password", "-s", SERVICE, "-a", account],
                       capture_output=True, text=True)
        return
    p = _file_path()
    if os.path.exists(p):
        try:
            data = json.load(open(p))
        except Exception:
            data = {}
        data.pop(account, None)
        fd = os.open(p, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with os.fdopen(fd, "w") as f:
            json.dump(data, f)


# ---- OAuth ------------------------------------------------------------------
def _token_endpoint(inst):
    return f"{inst}/services/oauth2/token"


def _post_form(url, form):
    req = urllib.request.Request(url, data=urllib.parse.urlencode(form).encode(),
                                 headers={"Content-Type": "application/x-www-form-urlencoded"})
    with urllib.request.urlopen(req, timeout=45) as r:
        return json.loads(r.read())


def _browser_login(inst, cid, csec):
    """PKCE + loopback authorization_code. Returns the token response dict."""
    verifier = base64.urlsafe_b64encode(secrets.token_bytes(64)).rstrip(b"=").decode()
    challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b"=").decode()
    state = secrets.token_urlsafe(16)
    auth_url = f"{inst}/services/oauth2/authorize?" + urllib.parse.urlencode({
        "response_type": "code", "client_id": cid, "redirect_uri": REDIR,
        "scope": SCOPE, "state": state,
        "code_challenge": challenge, "code_challenge_method": "S256"})
    got = {}

    class H(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            got.update({k: v[0] for k, v in urllib.parse.parse_qs(
                urllib.parse.urlparse(self.path).query).items()})
            self.send_response(200); self.send_header("Content-Type", "text/html"); self.end_headers()
            self.wfile.write(b"<h2>Authorized - close this tab.</h2>")
            threading.Thread(target=self.server.shutdown, daemon=True).start()

        def log_message(self, *a):
            pass

    class DualStack(http.server.HTTPServer):
        # macOS resolves localhost to ::1 first; IPv4-only bind silently never gets the
        # code (cost a round historically — do not regress). Bind dual-stack.
        address_family = socket.AF_INET6

        def server_bind(self):
            self.socket.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 0)
            super().server_bind()

    srv = DualStack(("::", PORT), H)
    print(f"OPEN_THIS_URL: {auth_url}", flush=True)
    srv.serve_forever()
    if got.get("state") != state or "code" not in got:
        sys.stderr.write("FAILED: bad OAuth callback\n"); raise SystemExit(1)
    return _post_form(_token_endpoint(inst), _drop_none({
        "grant_type": "authorization_code", "code": got["code"],
        "client_id": cid, "client_secret": csec, "redirect_uri": REDIR,
        "code_verifier": verifier}))


def _refresh(inst, cid, csec, refresh_token):
    """Silent access-token mint from a cached refresh token.

    Returns (token_dict, dead) where:
      - token_dict is the token response on success, else None.
      - dead is True ONLY when the refresh token is definitively invalid (OAuth `invalid_grant`
        — revoked/expired), meaning the cache should be discarded and re-auth is required.
        dead is False for transient failures (network error, 5xx, timeout) — KEEP the cache and
        just retry later; wiping it on a blip would force an unnecessary browser login (that
        aggressive behavior bit us mid-session 2026-07-31).
    """
    try:
        return _post_form(_token_endpoint(inst), _drop_none({
            "grant_type": "refresh_token", "refresh_token": refresh_token,
            "client_id": cid, "client_secret": csec})), False
    except urllib.error.HTTPError as e:
        body = e.read().decode()[:300]
        # SF returns 400 {"error":"invalid_grant"} for a revoked/expired refresh token.
        dead = (e.code == 400 and "invalid_grant" in body)
        sys.stderr.write(f"  refresh failed (HTTP {e.code}): {body}\n")
        return None, dead
    except Exception as e:  # network/timeout/DNS — transient, do NOT wipe the cache
        sys.stderr.write(f"  refresh error ({type(e).__name__}: {e}) — transient, keeping cache\n")
        return None, False


# ---- client_credentials (no browser, no refresh token, no disk state) ----
# Cached for the life of the PROCESS only. Deliberately not persisted: the whole point of
# this mode is that a workstation holds no auth state, so there is nothing to go stale,
# collide between orgs, or need a Keychain prompt. A cold mint costs ~1s.
_cc_cache = {"access_token": None, "expiry": 0.0}


def _client_credentials(inst, cid, csec):
    """Mint an access token from consumer key + secret alone.

    ECA prerequisites (all three, or the token endpoint refuses):
      - isClientCredentialsFlowEnabled=true in ExtlClntAppGlobalOauthSettings, AND
      - isClientCredentialsFlowEnabled=true in ExtlClntAppOauthConfigurablePolicies, AND
      - clientCredentialsFlowUser = the run-as username (needs API Only permission).

    Verified live on laulima26 2026-08-11: returns scopes `sfap_api mcp_api api` as a
    named-user JWT whose `aud` includes api.salesforce.com, and the prod hosted-MCP
    gateway accepts it (initialize -> HTTP 200). Contrary to widely repeated advice that
    hosted MCP requires interactive PKCE, this works — so it is the portable path.
    """
    if not csec:
        sys.stderr.write("FATAL: SF_AUTH_MODE=client_credentials requires SF_CSEC "
                         "(the ECA consumer secret).\n")
        raise SystemExit(2)
    try:
        return _post_form(_token_endpoint(inst), {"grant_type": "client_credentials",
                                                 "client_id": cid, "client_secret": csec})
    except urllib.error.HTTPError as e:
        body = e.read().decode()[:300]
        hint = ""
        if "unsupported_grant_type" in body:
            hint = ("\n       -> the client credentials flow is not fully enabled on the ECA. "
                    "Enable it in the OAuth POLICY (not just the global settings) and set "
                    "clientCredentialsFlowUser.")
        elif "invalid_client" in body:
            hint = "\n       -> SF_CSEC does not match this ECA's consumer secret."
        elif "inactive_user" in body or "user_deleted" in body:
            hint = "\n       -> the run-as user (clientCredentialsFlowUser) is frozen or deleted."
        sys.stderr.write(f"FATAL: client_credentials failed (HTTP {e.code}): {body}{hint}\n")
        raise SystemExit(5)


def _cc_token(inst, cid, csec, force=False):
    now = time.time()
    if not force and _cc_cache["access_token"] and now < _cc_cache["expiry"] - 120:
        return _cc_cache["access_token"]
    tok = _client_credentials(inst, cid, csec)
    at = tok.get("access_token")
    if not at:
        sys.stderr.write(f"FATAL: client_credentials returned no access token: {tok}\n")
        raise SystemExit(5)
    try:
        ttl = int(tok.get("expires_in") or 1800)
    except (TypeError, ValueError):
        ttl = 1800
    _cc_cache.update(access_token=at, expiry=now + ttl)
    return at


def _persist(acct, blob, tok):
    """Merge a token response into the stored blob: rotated refresh token + access token + expiry.

    This ECA ROTATES the refresh token on every refresh grant (single-use) — so we MUST persist
    the new refresh_token each time, and we CACHE the access token + its expiry so we don't do a
    refresh (and thus don't rotate) on every call. Refreshing per-call is what caused
    `invalid_grant` races between processes (proxy + CLI) — the whole point of caching the access
    token is to avoid that.
    """
    if tok.get("refresh_token"):
        blob["refresh_token"] = tok["refresh_token"]
    blob["access_token"] = tok["access_token"]
    # SF returns expires_in (seconds) on the refresh/auth response; default 2h if absent.
    try:
        ttl = int(tok.get("expires_in") or 7200)
    except (TypeError, ValueError):
        ttl = 7200
    blob["access_expiry"] = time.time() + ttl
    _store_set(acct, blob)


def get_access_token(interactive=True, force=False):
    """Return a valid access token.

    SF_AUTH_MODE=client_credentials short-circuits everything below: mint from key+secret,
    cache in-process only. No browser, no refresh token, no Keychain — the portable path.

    Otherwise (default) authorization_code + PKCE, minimizing refresh grants because this
    ECA rotates refresh tokens:
      1. Reuse the cached ACCESS token if it's still valid (>2 min headroom) — NO refresh, NO
         rotation, no cross-process race. This is the hot path during a demo.
      2. Else refresh with the cached refresh token, persist the rotated one + new access token.
      3. Else (no cache, or invalid_grant) browser login if interactive.

    `force` discards the cached access token and mints a new one — used by the proxy when the
    gateway answers 401 mid-session (token aged out), so a long demo self-heals.
    """
    inst = _inst(); cid, csec = _cid_csec()
    if CLIENT_CREDENTIALS:
        return _cc_token(inst, cid, csec, force=force)
    acct = _account(inst, cid)
    blob = _store_get(acct)
    if force:
        blob.pop("access_token", None)
        blob.pop("access_expiry", None)

    # 1) reuse a still-valid access token — the whole fix for the rotation race.
    at = blob.get("access_token")
    exp = blob.get("access_expiry")
    if at and exp and time.time() < (exp - 120):
        return at

    # 2) refresh with the cached refresh token (rotates it — persist the new one).
    rt = blob.get("refresh_token")
    if rt:
        tok, dead = _refresh(inst, cid, csec, rt)
        if tok and tok.get("access_token"):
            _persist(acct, blob, tok)
            return tok["access_token"]
        if dead:
            sys.stderr.write("  cached refresh token is invalid (revoked/expired) — re-authenticating\n")
            _store_del(acct)
        elif not interactive:
            sys.stderr.write("FATAL: refresh failed transiently (cache kept). Retry shortly, or run "
                             "`ramp_auth.py login` if it persists.\n")
            raise SystemExit(4)

    # 3) browser login.
    if not interactive:
        sys.stderr.write("FATAL: no cached credential and interactive=False. "
                         "Run `ramp_auth.py login` once on this workstation.\n")
        raise SystemExit(3)
    tok = _browser_login(inst, cid, csec)
    if not tok.get("access_token"):
        sys.stderr.write(f"FATAL: login returned no access token: {tok}\n"); raise SystemExit(1)
    if tok.get("refresh_token"):
        _persist(acct, {}, tok)
        print(f"  cached auth for {acct} ({'Keychain' if _is_macos() else _file_path()})", flush=True)
    else:
        sys.stderr.write("  WARNING: no refresh_token in response — check ECA refresh-token "
                         "policy; runs will stay interactive.\n")
    return tok["access_token"]


# ---- CLI --------------------------------------------------------------------
def main(argv):
    cmd = argv[0] if argv else "login"
    if CLIENT_CREDENTIALS and cmd in ("login", "logout"):
        # Nothing to log in to or forget — this mode holds no state between processes.
        print(f"SF_AUTH_MODE=client_credentials: '{cmd}' is a no-op (no cached credential).\n"
              f"Verify instead with:  ramp_auth.py status")
        return 0
    if cmd == "login":
        get_access_token(interactive=True)
        print("LOGIN OK — refresh token cached. Future runs are non-interactive.")
        return 0
    if cmd == "token":
        print(get_access_token(interactive=True))
        return 0
    if cmd == "status" and CLIENT_CREDENTIALS:
        inst = _inst(); cid, csec = _cid_csec()
        print(f"mode=client_credentials  secret={'set' if csec else 'MISSING'}  instance={inst}")
        _cc_token(inst, cid, csec, force=True)
        left = int(_cc_cache["expiry"] - time.time())
        print(f"OK — minted an access token from key+secret (valid ~{left // 60}m). "
              f"No browser, no Keychain, nothing cached on disk.")
        return 0
    if cmd == "status":
        inst = _inst(); cid, _ = _cid_csec(); acct = _account(inst, cid)
        blob = _store_get(acct)
        loc = "Keychain" if _is_macos() else _file_path()
        has_rt = bool(blob.get("refresh_token"))
        at, exp = blob.get("access_token"), blob.get("access_expiry")
        at_state = "none"
        if at and exp:
            secs = int(exp - time.time())
            at_state = f"valid ~{secs // 60}m left" if secs > 0 else "expired"
        print(f"{'CACHED' if has_rt else 'NOT CACHED'}  refresh_token={'yes' if has_rt else 'no'}  "
              f"access_token={at_state}  account={acct}  store={loc}")
        return 0 if has_rt else 1
    if cmd == "logout":
        inst = _inst(); cid, _ = _cid_csec(); acct = _account(inst, cid)
        _store_del(acct)
        print(f"forgot cached refresh token for {acct}")
        return 0
    sys.stderr.write(f"unknown command '{cmd}'. Use: login | token | status | logout\n")
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
