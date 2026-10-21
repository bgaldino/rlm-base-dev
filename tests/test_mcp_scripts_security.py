#!/usr/bin/env python3
"""
Offline security invariants for scripts/mcp/ (no org, no network, no real secrets).

    python tests/test_mcp_scripts_security.py

Covers: secret-bearing files are created 0600 (even over a pre-existing 0644 file),
no command prints a consumer secret, a repointed alias drops the old org's cached secret,
a new org id (a refreshed sandbox) re-resolves the cached user id and consumer key,
refresh is lock-serialised and re-reads the stored token, a transient refresh failure
keeps the cache and opens no browser, `login` fails when no refresh token was cached, the proxy returns a JSON-RPC
error (not a doomed tools/call) after a failed upstream initialize or a non-JSON-RPC
upstream answer, reopens an upstream once on a session 404, and picks the response out of an SSE stream; the host probe
prefers a base that serves the first upstream, falls back to later upstreams, re-mints once on 401, reports a dead token as an auth error (not unreachable hosts), backs
off after a failure, and a cold-cache upstream that fails contributes no tools; a stale
tool-list cache is refetched, kept when the refetch fails (once per process), and never
replaced by an empty list.
"""
import io
import contextlib
import importlib
import json
import os
import stat
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
MCP = REPO / "scripts" / "mcp"
sys.path.insert(0, str(MCP))

SECRET = "SUPERSECRET-consumer-value-123"
RESULTS = []


def check(name, ok, detail=""):
    RESULTS.append((name, bool(ok), detail))


def mode(p):
    return stat.S_IMODE(os.stat(p).st_mode)


def capture(fn, *a, **k):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        try:
            rv = fn(*a, **k)
        except SystemExit as e:
            rv = e.code
    return rv, out.getvalue(), err.getvalue()


# A successful MCP initialize answer; the proxy opens or picks nothing without one.
INIT_OK = json.dumps({"jsonrpc": "2.0", "id": 0, "result": {"protocolVersion": "2025-06-18"}})
INIT_ERR = json.dumps({"jsonrpc": "2.0", "id": 0, "error": {"code": -32602, "message": "Unsupported protocol version"}})


def load(name, env):
    for k in ("SF_INSTANCE", "SF_CID", "SF_USER_ID", "SF_CSEC", "SF_AUTH_MODE", "SF_MCP_BASES", "SF_MCP_BASE", "SF_MCP_SERVERS",
              "RLM_MCP_CUSTOM_SERVER", "RLM_MCP_ORG", "RLM_MCP_ECA", "RLM_MCP_PROFILES", "RLM_MCP_STATE", "RLM_MCP_AUTH_DIR"):
        os.environ.pop(k, None)
    os.environ.update(env)
    sys.modules.pop(name, None)
    for dep in ("mcp_org", "mcp_auth"):  # imported by the others; reload under this env too
        sys.modules.pop(dep, None)
    return importlib.import_module(name)


def test_mcp_org(tmp):
    prof = os.path.join(tmp, "orgs.json")
    Path(prof).write_text("{}")
    os.chmod(prof, 0o644)
    ro = load("mcp_org", {"RLM_MCP_PROFILES": prof, "SF_CSEC": SECRET})
    umask = os.umask(0o022)
    try:
        # sf CLI + metadata retrieve stubbed out
        state = {"inst": "https://a.example.com", "id": "00DA"}
        state.update(user="005U", username="u")
        user_calls = []
        ro._sf_json = lambda args: (
            user_calls.append(1) or {"status": 0, "result": {
                "id": state["user"], "username": state["username"], "accessToken": "CLI-TOKEN"}}
            if "user" in args else {"status": 0, "result": {
                "instanceUrl": state["inst"], "id": state["id"], "username": state["username"],
                "apiVersion": "68.0"}})
        ro._retrieve_consumer_key = lambda alias: "KEY-" + state["id"]
        r = ro.resolve("al")
        check("mcp_org profile file is 0600 (replaced a 0644 file)", mode(prof) == 0o600, oct(mode(prof)))
        check("resolve() carries the alias's user id and keys the Keychain on it",
              r["user_id"] == "005U" and r["keychain_account"].endswith("|005U"), str(r))
        ro.resolve("al")
        check("the user id is cached, not looked up on every resolve", user_calls == [1], str(user_calls))
        real_sf = ro._sf_json
        ro._sf_json = lambda args: {"status": 1, "result": {}}
        rv, _, _ = capture(ro._user_id, "al")
        ro._sf_json = real_sf
        check("an unreadable user id fails the resolve", isinstance(rv, str) and "user id" in rv, str(rv))
        _, out, _ = capture(ro.main, ["mcp_org.py", "env", "al"])
        check("env exports SF_USER_ID", "export SF_USER_ID='005U'" in out, out)
        printed = "".join("".join(capture(ro.main, ["mcp_org.py", c, "al"])[1:]) for c in ("json", "show", "env"))
        check("the CLI's access token is never printed or saved",
              "CLI-TOKEN" not in printed + Path(prof).read_text())
        # The alias re-pointed at another user of the same org: a new lookup and a new key.
        state.update(user="005V", username="v")
        rv = ro.resolve("al")
        check("an alias re-pointed at another user of the org gets that user's key",
              rv["user_id"] == "005V" and rv["keychain_account"].endswith("|005V")
              and json.load(open(prof))["al"]["user_id"] == "005V", str(rv))
        # A renamed username (same user) is saved, so it is looked up once, not every time.
        state.update(username="v2")
        ro.resolve("al"); user_calls.clear(); ro.resolve("al")
        check("a renamed username is saved and not looked up again",
              user_calls == [] and json.load(open(prof))["al"]["username"] == "v2", str(user_calls))
        # A refreshed sandbox: same username and host, a new org id and new user ids.
        state.update(id="00DB", user="005W")
        rv = ro.resolve("al")
        check("a refreshed sandbox (new org id, same username) looks the user and key up again",
              rv["user_id"] == "005W" and rv["consumer_key"] == "KEY-00DB"
              and json.load(open(prof))["al"]["org_id"] == "00DB", str(rv))
        state.update(id="00DA", user="005U", username="u")
        ro.resolve("al")
        user_calls.clear()
        ro2 = load("mcp_org", {"RLM_MCP_PROFILES": "rel/orgs.json", "SF_CSEC": SECRET})
        check("a relative RLM_MCP_PROFILES resolves against the repo root",
              ro2.PROFILES == os.path.join(ro2.REPO_ROOT, "rel", "orgs.json"), ro2.PROFILES)
        os.environ["RLM_MCP_PROFILES"] = prof
        os.environ["RLM_MCP_STATE"] = "rel/state"
        check("a relative RLM_MCP_STATE gives an absolute state dir under the repo root",
              ro.resolve("al")["auth_dir"] == os.path.join(ro.REPO_ROOT, "rel", "state", "00DA"))
        os.environ.pop("RLM_MCP_STATE")
        check("resolve() result carries no secret", SECRET not in json.dumps(r) and "consumer_secret" not in r)
        check("no temp files left behind", [f for f in os.listdir(tmp) if f.startswith(".tmp-")] == [])
        for cmd in ("json", "show", "env"):
            _, out, err = capture(ro.main, ["mcp_org.py", cmd, "al"])
            check(f"mcp_org {cmd} does not print the secret (env var set)", SECRET not in out + err)
        os.environ.pop("SF_CSEC")
        _, out, err = capture(ro.main, ["mcp_org.py", "env", "al"])
        check("env WITHOUT SF_AUTH_MODE=client_credentials emits no jq secret line and unsets SF_CSEC",
              SECRET not in out + err and "jq -r" not in out and "unset SF_CSEC" in out, out)
        check("env does not pin the server list (RLM_MCP_CUSTOM_SERVER stays effective)",
              "SF_MCP_SERVERS" not in out, out)
        os.environ["SF_AUTH_MODE"] = "client_credentials"
        _, out, err = capture(ro.main, ["mcp_org.py", "env", "al"])
        check("env (secret only in profile, client_credentials opted in) emits jq read, not the value",
              SECRET not in out + err and "jq -r" in out and "client_credentials" in out)
        os.environ.pop("SF_AUTH_MODE")
        check("get_consumer_secret reads the cached secret", ro.get_consumer_secret("al") == SECRET)
        # An SF_CSEC eval'd for another org must not be handed out for this one.
        os.environ.update(SF_INSTANCE="https://other.example.com", SF_CSEC="OTHER-ORG-SECRET")
        check("get_consumer_secret ignores an SF_CSEC exported for another org",
              ro.get_consumer_secret("al") == SECRET)
        os.environ["SF_INSTANCE"] = state["inst"]
        check("get_consumer_secret honours an SF_CSEC exported for this org",
              ro.get_consumer_secret("al") == "OTHER-ORG-SECRET")
        os.environ.pop("SF_CSEC")
        # Overrides left over from another org's eval are unset on a switch, not inherited.
        os.environ.update(SF_MCP_SERVERS="x/y", SF_MCP_BASE="https://gw.invalid/a")
        _, out, _ = capture(ro.main, ["mcp_org.py", "env", "al"])
        check("env for the same org keeps its server and base overrides", "unset SF_MCP" not in out, out)
        os.environ["SF_INSTANCE"] = "https://other.example.com"
        _, out, _ = capture(ro.main, ["mcp_org.py", "env", "al"])
        check("env switching orgs unsets the other org's SF_MCP_SERVERS and SF_MCP_BASE",
              "unset SF_MCP_SERVERS SF_MCP_BASE" in out, out)
        os.environ.pop("SF_INSTANCE"); os.environ.pop("SF_MCP_SERVERS"); os.environ.pop("SF_MCP_BASE")
        # alias repointed to another org: old secret must be discarded
        state.update(inst="https://b.example.com", id="00DB")
        r2 = ro.resolve("al")
        check("repointed alias drops the old org's cached secret",
              not r2["has_secret"] and ro.get_consumer_secret("al") is None
              and "consumer_secret" not in json.load(open(prof))["al"])

        # A key cached for another ECA is re-retrieved, then reused.
        pulls = []
        ro._retrieve_consumer_key = lambda alias: pulls.append(ro.ECA_NAME) or "KEY-" + ro.ECA_NAME
        ro.ECA_NAME = "Other_Eca"
        real_update, updates = ro._update_profiles, []
        ro._update_profiles = lambda m: (updates.append(1), real_update(m))[1]
        r3 = ro.resolve("al")
        ro._update_profiles = real_update
        check("resolve() saves the profile through the locked update", updates == [1], str(updates))
        ro.resolve("al")
        check("changing RLM_MCP_ECA re-retrieves the key once",
              pulls == ["Other_Eca"] and r3["consumer_key"] == "KEY-Other_Eca"
              and json.load(open(prof))["al"]["eca"] == "Other_Eca", f"{pulls} {r3['consumer_key']}")
        # A secret another process caches for this alias (same instance + key) while this one
        # is retrieving the key survives: the carry-over reads the map under the lock.
        def racing_retrieve(alias):
            ro._update_profiles(lambda p: p["al"].update(consumer_secret="LATE"))
            return "KEY-" + ro.ECA_NAME
        ro._retrieve_consumer_key = racing_retrieve
        ro.resolve("al", refresh=True)
        check("refresh keeps a secret cached under the lock for the same key",
              json.load(open(prof))["al"].get("consumer_secret") == "LATE")

        # Concurrent resolves for two aliases: B's update waits for A's, so neither is lost.
        if ro.fcntl is not None:
            import threading, time as _t
            done, started = [], threading.Event()
            with ro._profiles_lock():
                data = ro._load_profiles()
                w = threading.Thread(target=lambda: (
                    started.set(), ro._update_profiles(lambda p: p.__setitem__("b", {"x": 1})),
                    done.append(1)))
                w.start()
                began = started.wait(5)
                _t.sleep(0.3)
                blocked = began and not done
                data["a"] = {"x": 2}
                ro._save_profiles(data)
            w.join(5)
            both = json.load(open(prof))
            check("profile update waits for the profile lock", blocked and done == [1], str(done))
            check("concurrent profile writers keep both aliases",
                  both.get("a") == {"x": 2} and both.get("b") == {"x": 1} and "al" in both, str(both))
    finally:
        os.umask(umask)


def test_gateway_bases():
    ro = load("mcp_org", {})
    g = ro.GATEWAY
    gb = ro.gateway_bases
    check("gateway_bases: prod my-domain -> single pinned base",
          gb("https://acme.my.salesforce.com") == f"{g}/d/acme")
    for host in ("acme--uat.sandbox.my.salesforce.com", "x.scratch.my.salesforce.com"):
        pre = host.split(".")[0]
        check(f"gateway_bases: {host} -> pinned + /sandbox",
              gb("https://" + host) == f"{g}/d/{pre},{g}/sandbox", gb("https://" + host))
    for host in ("x.develop.my.salesforce.com", "x.demo.my.salesforce.com"):
        check(f"gateway_bases: {host} -> pinned + plain",
              gb("https://" + host) == f"{g}/d/x,{g}", gb("https://" + host))
    check("gateway_bases: pre-enhanced sandbox host -> sandbox fallback",
          gb("https://acme--uat.my.salesforce.com") == f"{g}/d/acme--uat,{g}/sandbox")
    check("gateway_bases: pre-enhanced sandbox with instance label -> sandbox fallback",
          gb("https://acme--uat.cs42.my.salesforce.com") == f"{g}/d/acme--uat,{g}/sandbox")
    check("gateway_bases: pre-enhanced Developer Edition -> pinned + plain",
          gb("https://acme-dev-ed.my.salesforce.com") == f"{g}/d/acme-dev-ed,{g}")
    check("gateway_bases: non-my-domain -> legacy base", gb("https://a.example.com") == g)
    # An override exported for org A (with SF_INSTANCE=A) must not follow the shell to org B.
    os.environ["SF_INSTANCE"] = "https://a.my.salesforce.com"
    os.environ["SF_MCP_BASES"] = f"{g}/d/a"
    check("gateway_bases: inherited override for another org is ignored",
          gb("https://b.my.salesforce.com") == f"{g}/d/b")
    check("gateway_bases: override for the same org still wins",
          gb("https://a.my.salesforce.com/") == f"{g}/d/a")
    os.environ.pop("SF_INSTANCE"); os.environ.pop("SF_MCP_BASES")
    os.environ["SF_MCP_BASES"] = "https://override.invalid/x"
    check("gateway_bases: SF_MCP_BASES override wins",
          gb("https://acme.my.salesforce.com") == "https://override.invalid/x")
    os.environ["SF_MCP_BASE"] = "https://single.invalid/y/"
    check("gateway_bases: SF_MCP_BASE wins over SF_MCP_BASES, as in the proxy",
          gb("https://acme.my.salesforce.com") == "https://single.invalid/y")
    os.environ.pop("SF_MCP_BASES")
    check("gateway_bases: SF_MCP_BASE alone is honored",
          gb("https://acme.my.salesforce.com") == "https://single.invalid/y")
    os.environ["SF_INSTANCE"] = "https://a.my.salesforce.com"
    check("gateway_bases: SF_MCP_BASE for another org is ignored",
          gb("https://b.my.salesforce.com") == f"{g}/d/b")
    os.environ.pop("SF_INSTANCE"); os.environ.pop("SF_MCP_BASE")


def test_write_connector_config(tmp):
    wc = load("write_connector_config", {})
    d = os.path.join(tmp, "proj")
    os.mkdir(d)
    target = os.path.join(d, ".mcp.json")
    Path(target).write_text("{}")
    os.chmod(target, 0o644)
    os.umask(0o022)
    path = wc.write_config(d, wc.proxy_entry({"SF_CSEC": SECRET}))
    check(".mcp.json is 0600 (replaced a 0644 file)", mode(path) == 0o600, oct(mode(path)))
    check(".mcp.json content correct", json.load(open(path))["mcpServers"]["revenue-cloud"]["env"]["SF_CSEC"] == SECRET)
    check(".mcp.json no temp leftovers", [f for f in os.listdir(d) if f != ".mcp.json"] == [])
    Path(target).write_text(json.dumps({"mcpServers": {"other": {"command": "x"},
                                                       "revenue-cloud": {"command": "old"}},
                                        "setting": 1}))
    cfg = json.load(open(wc.write_config(d, {"command": "new"})))
    check(".mcp.json keeps other connectors and settings, replaces only ours",
          cfg == {"mcpServers": {"other": {"command": "x"}, "revenue-cloud": {"command": "new"}},
                  "setting": 1}, str(cfg))
    for bad in ("not json", "[]", '{"mcpServers": []}'):
        Path(target).write_text(bad)
        try:
            wc.write_config(d, {"command": "new"}); refused = False
        except SystemExit:
            refused = True
        check(f".mcp.json {bad!r} is refused and left unchanged",
              refused and Path(target).read_text() == bad)
    os.unlink(target)
    os.mkdir(target)
    try:
        wc.write_config(d, {"command": "new"}); msg = ""
    except SystemExit as e:
        msg = str(e.code)
    check("an unreadable .mcp.json is refused with a FATAL message", msg.startswith("FATAL: cannot read"), msg)
    os.rmdir(target)

    # Custom server off: one upstream, so PKCE goes direct (no proxy); cc keeps the proxy.
    A, B = "https://a.my.salesforce.com", "https://b.my.salesforce.com"
    mo = load("mcp_org", {})
    check("default server list has the custom server", mo.servers_for(A).endswith(mo.CUSTOM_SERVER))
    for off in ("0", "false", "OFF"):
        mo = load("mcp_org", {"RLM_MCP_CUSTOM_SERVER": off})
        check(f"RLM_MCP_CUSTOM_SERVER={off} drops the custom server", mo.servers_for(A) == mo.HOSTED_SERVER)
    mo = load("mcp_org", {"RLM_MCP_CUSTOM_SERVER": "0", "SF_MCP_SERVERS": "a/b,c/d"})
    check("explicit SF_MCP_SERVERS wins over RLM_MCP_CUSTOM_SERVER", mo.servers_for(A) == "a/b,c/d")
    mo = load("mcp_org", {"SF_MCP_SERVERS": "a/b", "SF_INSTANCE": A})
    check("SF_MCP_SERVERS for org A does not follow the shell to org B",
          mo.servers_for(A) == "a/b" and mo.servers_for(B) == mo.DEFAULT_SERVERS)
    mo = load("mcp_org", {"SF_MCP_SERVERS": ""})
    check("empty SF_MCP_SERVERS falls back to the default", mo.servers_for(A) == mo.DEFAULT_SERVERS)
    px = load("mcp_multiplex_proxy", {"RLM_MCP_CUSTOM_SERVER": "0"})
    check("proxy follows RLM_MCP_CUSTOM_SERVER", px.SERVERS == ["industries/revenue-cloud"], px.SERVERS)

    wc = load("write_connector_config", {})
    one = {"servers": "industries/revenue-cloud", "consumer_key": "KEY",
           "bases": "https://gw.invalid/v1/d/acme,https://gw.invalid/v1"}
    check("one server + PKCE is direct", wc.is_direct(one, {}))
    check("one server + client_credentials keeps the proxy", not wc.is_direct(one, {"SF_CSEC": SECRET}))
    check("two servers keep the proxy",
          not wc.is_direct(dict(one, servers="industries/revenue-cloud,custom/X"), {}))
    e = wc.direct_entry(one)
    check("direct entry is HTTP to the first base with the ECA key",
          e == {"type": "http", "url": "https://gw.invalid/v1/d/acme/industries/revenue-cloud",
                "oauth": {"clientId": "KEY", "callbackPort": 8080}}, e)
    path = wc.write_config(d, e)
    check("direct .mcp.json has no command/env (no proxy)",
          "command" not in json.load(open(path))["mcpServers"]["revenue-cloud"] and mode(path) == 0o600)

    resolved = dict(one, alias="al", org_id="00D", instance="https://acme.my.salesforce.com",
                    user_id="005U", auth_dir=tmp, client_credentials=False, consumer_secret=None)
    check("proxy env carries the user the token cache is keyed on",
          wc.build_env(resolved)["SF_USER_ID"] == "005U")
    os.environ["SF_MCP_BASE"] = "https://other-org.invalid"
    os.environ["SF_INSTANCE"] = resolved["instance"]
    px = load("mcp_multiplex_proxy", dict(os.environ, **wc.build_env(resolved)))
    check("an SF_MCP_BASE inherited from the shell does not override the written bases",
          px._BASES == [b.rstrip("/") for b in resolved["bases"].split(",")], px._BASES)
    wc.resolve = lambda alias: resolved
    ran = []
    real_run = wc.subprocess.run
    wc.subprocess.run = lambda *a, **k: ran.append(a)
    try:
        rv, out, _ = capture(wc.main, ["x", "al", d, "--prime"])
    finally:
        wc.subprocess.run = real_run
    check("direct main: writes, skips --prime, never runs the proxy",
          rv == 0 and ran == [] and "--prime skipped" in out and "NOTE" in out, f"{rv} {out!r}")


def test_mcp_auth(tmp):
    env = {"SF_INSTANCE": "https://a.example.com", "SF_CID": "KEY", "RLM_MCP_AUTH_DIR": tmp}
    ra = load("mcp_auth", env)
    ra._is_macos = lambda: False            # exercise the file backend on every platform
    os.umask(0o022)
    fp = ra._file_path()
    Path(fp).write_text("{}")
    os.chmod(fp, 0o644)
    ra._store_set("acct", {"refresh_token": "RT0"})
    check("token cache file is 0600 (replaced a 0644 file)", mode(fp) == 0o600, oct(mode(fp)))
    real_root, ra.REPO_ROOT = ra.REPO_ROOT, tmp
    os.environ["RLM_MCP_AUTH_DIR"] = "rel/auth"
    check("relative RLM_MCP_AUTH_DIR resolves against the repo root, as in the proxy",
          ra._file_path() == os.path.join(tmp, "rel", "auth", "refresh-tokens.json"), ra._file_path())
    ra.REPO_ROOT = real_root
    os.environ["RLM_MCP_AUTH_DIR"] = tmp
    ra._store_del("nothing")
    check("token cache stays 0600 after delete rewrite", mode(fp) == 0o600)

    # Every account shares the one file: a writer for B waits while A's read-modify-replace
    # holds the file lock, so neither replaces the file with a copy missing the other.
    if ra.fcntl is not None:
        import threading, time as _t
        done, started = [], threading.Event()
        with ra._file_lock():
            data = json.loads(Path(fp).read_text())
            w = threading.Thread(target=lambda: (started.set(), ra._raw_set("B", "vb"), done.append(1)))
            w.start()
            began = started.wait(5)
            _t.sleep(0.3)                   # the thread is at _raw_set; give it time to finish if unlocked
            blocked = began and not done
            data["A"] = "va"
            ra._write_private(fp, json.dumps(data))
        w.join(5)
        both = json.loads(Path(fp).read_text())
        check("file-backend write waits for the file lock", blocked and done == [1], str(done))
        check("concurrent writers for two accounts keep both entries",
              both.get("A") == "va" and both.get("B") == "vb", str(both))
        ra._store_del("B")
        check("delete keeps the other accounts' entries",
              "B" not in json.loads(Path(fp).read_text()) and json.loads(Path(fp).read_text()).get("A") == "va")

    # refresh omits client_secret when SF_CSEC is absent
    posted = []
    ra._post_form = lambda url, form: (posted.append(form), {"access_token": "AT1", "refresh_token": "RT1", "expires_in": 7200})[1]
    ra._refresh("https://a.example.com", "KEY", None, "RT0")
    check("refresh grant omits client_secret when no secret", "client_secret" not in posted[0])

    # lock + re-read: another process rotated RT0->RT_other while we waited for the lock
    acct = ra._account("https://a.example.com", "KEY")
    ra._store_set(acct, {"refresh_token": "RT0"})
    used, locked = [], []
    real_lock = ra._account_lock

    import contextlib as cl

    @cl.contextmanager
    def lock_spy(a):
        with real_lock(a):
            locked.append(a)
            # simulate the competing process finishing its refresh before we got the lock
            ra._store_set(a, {"refresh_token": "RT_other", "access_token": "AT_other",
                              "access_expiry": __import__("time").time() + 3600})
            yield
    ra._account_lock = lock_spy
    ra._refresh = lambda *a: used.append(a[3]) or ({"access_token": "X"}, False)
    at = ra.get_access_token(interactive=False)
    check("refresh happens under the account lock", locked == [acct])
    check("re-read after lock reuses the other process's fresh access token",
          at == "AT_other" and used == [], f"at={at} refreshed_with={used}")

    # if the other process's access token is expired, we refresh with the RE-READ (rotated) token
    used.clear()
    def lock_spy2(a):
        @cl.contextmanager
        def c():
            with real_lock(a):
                ra._store_set(a, {"refresh_token": "RT_rotated", "access_token": "old", "access_expiry": 0})
                yield
        return c()
    ra._account_lock = lock_spy2
    ra._store_set(acct, {"refresh_token": "RT0"})
    ra.get_access_token(interactive=False)
    check("refresh uses the re-read rotated token, not the stale one", used == ["RT_rotated"], str(used))

    # A transient refresh failure keeps the cache and exits; it never opens a browser login.
    browsed = []
    ra._refresh = lambda *a: (None, False)
    ra._browser_login = lambda *a: browsed.append(1) or {"access_token": "AT"}
    ra._account_lock = real_lock
    ra._store_set(acct, {"refresh_token": "RT0"})
    rv, _, err = capture(ra.get_access_token, True)
    check("a transient refresh failure (interactive) exits 4, keeps the cache, opens no browser",
          rv == 4 and browsed == [] and ra._store_get(acct).get("refresh_token") == "RT0",
          f"{rv} {browsed} {err!r}")

    # a login response without an access token must not echo the refresh token
    ra._browser_login = lambda *a: {"error": "x", "refresh_token": SECRET}
    ra._store_get = lambda a: {}
    _, out, err = capture(ra.get_access_token, True)
    check("failed login does not echo token response", SECRET not in out + err)

    # Two users of one org: separate cache entries, and a login as the wrong user caches nothing.
    os.environ["SF_USER_ID"] = "005AAAAAAAAAAAAAAA"
    a_key = ra._account("https://a.example.com", "KEY")
    os.environ["SF_USER_ID"] = "005BBBBBBBBBBBBBBB"
    check("the token cache key differs per user of one org",
          a_key != ra._account("https://a.example.com", "KEY") and a_key.endswith("|005AAAAAAAAAAAAAAA"))
    stored = []
    ra._store_set = lambda a, b: stored.append(a)
    ra._browser_login = lambda *a: {"access_token": "AT", "refresh_token": "RT",
                                    "id": "https://login.example.com/id/00DX/005AAAAAAAAAAAAAAA"}
    rv, _, err = capture(ra.get_access_token, True)
    check("a browser login as another user fails and caches nothing",
          rv == 1 and stored == [] and "005BBBBBBBBBBBBBBB" in err, f"{rv} {stored} {err!r}")
    ra._browser_login = lambda *a: {"access_token": "AT", "refresh_token": "RT",
                                    "id": "https://login.example.com/id/00DX/005BBBBBBBBBBBBBBB"}
    rv, _, _ = capture(ra.get_access_token, True)
    check("a browser login as the alias's user is cached under its key",
          rv == "AT" and stored == [ra._account("https://a.example.com", "KEY")], f"{rv} {stored}")
    check("a 15-character id in the token matches the 18-character SF_USER_ID",
          ra._token_user_matches({"id": "https://x/id/00DX/005BBBBBBBBBBBB"}))
    check("a token response without an id fails closed", not ra._token_user_matches({}))
    # `login` succeeds only if a refresh token was actually cached.
    ra._browser_login = lambda *a: {"access_token": "AT",
                                    "id": "https://login.example.com/id/00DX/005BBBBBBBBBBBBBBB"}
    rv, out, err = capture(ra.main, ["login"])
    check("login with no refresh token in the response fails instead of claiming one was cached",
          rv == 1 and "LOGIN OK" not in out and "no refresh token" in err, f"{rv} {out!r} {err!r}")
    ra._store_get = lambda a: {"refresh_token": "RT", "access_token": "AT",
                               "access_expiry": __import__("time").time() + 3600}
    rv, out, _ = capture(ra.main, ["login"])
    check("login with a cached refresh token reports LOGIN OK", rv == 0 and "LOGIN OK" in out, f"{rv} {out!r}")
    os.environ.pop("SF_USER_ID")


def test_proxy():
    px = load("mcp_multiplex_proxy", {"SF_INSTANCE": "https://a.example.com", "SF_CID": "KEY"})
    px._route = {"tool_a": "srv/a"}
    px._merged_toollist = lambda: None
    px._pick_base = lambda: "https://gw.invalid"
    px._opened.clear()
    calls = []
    px._http = lambda url, body, sid=None, **k: (calls.append(body.get("method")) or (500, None, ""))
    out = json.loads(capture(px.handle, {"jsonrpc": "2.0", "id": 7, "method": "tools/call",
                                         "params": {"name": "tool_a"}})[0])
    check("failed upstream initialize -> JSON-RPC error to client",
          out.get("id") == 7 and out.get("error", {}).get("code") == -32603, str(out))
    check("no tools/call sent upstream after failed initialize", "tools/call" not in calls, str(calls))
    # initialize succeeds but notifications/initialized fails: not opened, retried next call.
    calls.clear()
    px._http = lambda url, body, sid=None, **k: (calls.append(body.get("method")) or (
        (200, "S1", INIT_OK) if body.get("method") == "initialize" else (500, None, "")))
    capture(px._open_upstream, "srv/a")
    capture(px._open_upstream, "srv/a")
    check("a failed notifications/initialized leaves the server unopened and retries the handshake",
          "srv/a" not in px._opened and calls.count("initialize") == 2, str(calls))
    # A 200 whose body is a JSON-RPC error (or no response at all) is a failed initialize.
    for label, body0 in (("a JSON-RPC error", INIT_ERR), ("no JSON-RPC response", ""),
                         ("another id's result", INIT_OK.replace('"id": 0', '"id": 3'))):
        calls.clear()
        px._http = lambda url, body, sid=None, **k: (calls.append(body.get("method")) or (200, "S9", body0))
        capture(px._open_upstream, "srv/a")
        check(f"an initialize 200 with {label} leaves the server unopened, no initialized sent",
              "srv/a" not in px._opened and calls == ["initialize"], str(calls))
    null_err = INIT_ERR.replace('"id": 0', '"id": null')
    check("an initialize error with id null is reported as that error",
          px._init_error(200, null_err).startswith("JSON-RPC error") and "Unsupported" in px._init_error(200, null_err))
    check("an initialize answered as SSE is accepted",
          px._init_error(200, f"event: message\r\ndata: {INIT_OK}\r\n\r\n") is None)
    px._http = lambda url, body, sid=None, **k: (202, "S2", "") if "id" not in body else (200, "S2", INIT_OK)
    capture(px._open_upstream, "srv/a")
    check("a 202 to notifications/initialized opens the server", "srv/a" in px._opened
          and px._sessions.get("srv/a") == "S2", str(px._opened))

    # A 404 on a session the gateway dropped: reopen once, replay on the new session.
    calls.clear()
    def gw(url, body, sid=None, **k):
        calls.append((body.get("method"), sid))
        if body.get("method") == "initialize":
            return 200, "S3", INIT_OK
        if "id" not in body:
            return 202, None, ""
        return (404, None, "") if sid == "S2" else (200, None, json.dumps(
            {"jsonrpc": "2.0", "id": 5, "result": {"content": []}}))
    px._http = gw
    out = json.loads(capture(px.handle, {"jsonrpc": "2.0", "id": 5, "method": "tools/call",
                                         "params": {"name": "tool_a"}})[0])
    check("a 404 on an expired session reopens the upstream and replays the call once",
          out.get("result") == {"content": []} and px._sessions.get("srv/a") == "S3"
          and calls[0] == ("tools/call", "S2") and calls[-1] == ("tools/call", "S3"), str(calls))
    # A 404 carrying this request's JSON-RPC answer was processed: passed on, not replayed.
    calls.clear()
    tool_err = {"jsonrpc": "2.0", "id": 8, "error": {"code": -32602, "message": "record not found"}}
    px._http = lambda url, body, sid=None, **k: (calls.append(body.get("method")) or (
        404, None, json.dumps(tool_err)))
    out = json.loads(capture(px.handle, {"jsonrpc": "2.0", "id": 8, "method": "tools/call",
                                         "params": {"name": "tool_a"}})[0])
    check("a 404 with this request's JSON-RPC answer is passed on, not replayed",
          out == tool_err and calls == ["tools/call"] and px._sessions.get("srv/a") == "S3", f"{out} {calls}")
    # Same for the live tools/list behind a cold or stale cache.
    calls.clear()
    px._sessions["srv/a"] = "S2"
    real_cache, real_live = px._cache_path, px._LIVE_FETCH
    px._LIVE_FETCH = True
    px._cache_path = lambda server: os.devnull
    def gw_list(url, body, sid=None, **k):
        if body.get("method") == "tools/list" and sid == "S3":
            calls.append(("tools/list", sid))
            return 200, None, json.dumps({"jsonrpc": "2.0", "id": 1, "result": {"tools": [{"name": "t"}]}})
        calls.append((body.get("method"), sid))
        return gw(url, body, sid)
    px._http = gw_list
    rv, _, _ = capture(px._fetch_toollist, "srv/a")
    px._cache_path, px._LIVE_FETCH = real_cache, real_live
    check("a 404 on an expired session during a live tools/list reopens and replays it",
          rv and rv.get("tools") == [{"name": "t"}] and calls[0] == ("tools/list", "S2")
          and calls[-1] == ("tools/list", "S3"), f"{rv} {calls}")
    calls.clear()
    def gone(url, body, sid=None, **k):
        calls.append(body.get("method"))
        return 404, None, ""
    px._http = gone
    out = json.loads(capture(px.handle, {"jsonrpc": "2.0", "id": 6, "method": "tools/call",
                                         "params": {"name": "tool_a"}})[0])
    check("a 404 whose reopen fails returns an error with the request id, unopened, not replayed",
          out.get("id") == 6 and "error" in out and "srv/a" not in px._opened
          and calls == ["tools/call", "initialize"], f"{out} {calls}")
    px._opened.clear(); px._sessions.clear()

    # An initialized upstream that answers a call without a JSON-RPC response (empty body,
    # a Salesforce error array, HTML) becomes an error with the request id; a real JSON-RPC
    # response (result or error, JSON or SSE) is passed on as one line with the request id.
    px._opened.add("srv/a")
    call = {"jsonrpc": "2.0", "id": 9, "method": "tools/call", "params": {"name": "tool_a"}}
    for st, body in ((500, ""), (403, '[{"message":"no","errorCode":"FORBIDDEN"}]'),
                     (429, "<html>slow down</html>"), (200, '{"unexpected": true}')):
        px._http = lambda url, b, sid=None, _r=(st, None, body), **k: _r
        out = json.loads(capture(px.handle, call)[0])
        check(f"http={st} non-JSON-RPC body -> JSON-RPC error with the request id",
              out.get("id") == 9 and out.get("error", {}).get("code") == -32603
              and f"http={st}" in out["error"]["message"], str(out))
    upstream_err = {"jsonrpc": "2.0", "id": 9, "error": {"code": -32602, "message": "bad args"}}
    upstream_ok = {"jsonrpc": "2.0", "id": 9, "result": {"content": [{"type": "text", "text": "ok"}]}}
    progress = {"jsonrpc": "2.0", "method": "notifications/progress", "params": {"progress": 1}}
    cases = (
        ("error, JSON", 400, json.dumps(upstream_err), upstream_err),
        ("error, SSE", 400, "event: message\ndata: " + json.dumps(upstream_err) + "\n", upstream_err),
        ("result, pretty-printed JSON", 200, json.dumps(upstream_ok, indent=2), upstream_ok),
        ("result after a progress notification, SSE", 200,
         "event: message\ndata: " + json.dumps(progress) + "\n\n"
         "event: message\ndata: " + json.dumps(upstream_ok) + "\n\n", upstream_ok),
        ("result split over two data lines, SSE", 200,
         'data: {"jsonrpc": "2.0", "id": 9,\ndata: "result": {"content": []}}\n\n',
         {"jsonrpc": "2.0", "id": 9, "result": {"content": []}}),
        ("error, SSE with CRLF line endings", 400,
         "event: message\r\ndata: " + json.dumps(upstream_err) + "\r\n\r\n", upstream_err),
        ("error with id null gets the request id", 400,
         json.dumps(dict(upstream_err, id=None)), upstream_err),
    )
    for label, st, body, want in cases:
        px._http = lambda url, b, sid=None, _r=(st, None, body), **k: _r
        text = capture(px.handle, call)[0]
        check(f"upstream JSON-RPC response passes through: {label}",
              "\n" not in text and json.loads(text) == want, text)


def test_proxy_toollist_cache(tmp):
    px = load("mcp_multiplex_proxy", {"SF_INSTANCE": "https://a.example.com", "SF_CID": "KEY",
                                      "RLM_MCP_AUTH_DIR": tmp})
    px.SERVERS[:] = ["srv/a"]
    old, new = {"tools": [{"name": "old_tool"}]}, {"tools": [{"name": "new_tool"}]}
    p = px._cache_path("srv/a")
    fetched = []
    px._fetch_toollist = lambda s: fetched.append(s) or new

    def names():
        return [t["name"] for t in capture(px._merged_toollist)[0]]

    Path(p).write_text(json.dumps(old))
    check("a fresh tools/list cache is served without a gateway fetch",
          names() == ["old_tool"] and fetched == [], str(fetched))
    aged = px._time.time() - px.TOOLLIST_MAX_AGE - 60
    os.utime(p, (aged, aged))
    check("a stale tools/list cache is refetched", names() == ["new_tool"] and fetched == ["srv/a"])
    px._fetch_toollist = lambda s: fetched.append(s) or None
    check("a stale cache is still served when the refetch fails", names() == ["old_tool"])
    fetched.clear()
    check("a failed refresh is not retried in the same process", names() == ["old_tool"] and fetched == [])

    # The real fetch: a tools/list result is cached (refreshing its age); an empty one is not.
    px2 = load("mcp_multiplex_proxy", {"SF_INSTANCE": "https://a.example.com", "SF_CID": "KEY",
                                       "RLM_MCP_AUTH_DIR": tmp})
    px2._open_upstream = lambda s: px2._opened.add(s)
    px2._pick_base = lambda: "https://gw.invalid"
    for body, want in ((new, new), ({"tools": []}, old)):
        Path(p).write_text(json.dumps(old))
        px2._http = lambda url, b, sid=None, _r=body, **k: (200, None, json.dumps(
            {"jsonrpc": "2.0", "id": 1, "result": _r}))
        capture(px2._fetch_toollist, "srv/a")
        check(f"a live tools/list with {len(body['tools'])} tools: cache now holds "
              f"{want['tools'][0]['name']}", json.loads(Path(p).read_text()) == want)


def test_proxy_host_probe():
    px = load("mcp_multiplex_proxy", {"SF_INSTANCE": "https://a.example.com", "SF_CID": "KEY"})
    px._BASES[:] = ["https://gw.invalid/d/a", "https://gw.invalid/sandbox"]
    px._base, px._probe_failed = None, None
    # Per base, for every upstream: before the re-mint, then after it.
    mints, codes = [], {"first": [401, 404], "then": [404, 200]}
    state = {"round": "first"}

    def http(url, body, sid=None, timeout=200, _retried=False):
        i = next(n for n, b in enumerate(px._BASES) if url.startswith(b + "/"))
        st = codes[state["round"]][i]
        return st, None, INIT_OK if st == 200 else ""
    px._http = http

    def mint(force=False):
        mints.append(force)
        if force:
            state["round"] = "then"
        return "tok"
    px._token = mint
    base, _, _ = capture(px._pick_base)
    check("probe: a 401 with no 200 re-mints once, then routes", base == "https://gw.invalid/sandbox"
          and mints == [False, True], f"{base} {mints}")

    px._base, px._probe_failed = None, None
    mints.clear()
    px._token = lambda force=False: mints.append(force) or "tok"
    px._http = lambda url, body, sid=None, timeout=200, _retried=False: (401, None, "")
    try:
        capture(px._pick_base)
        raised = None
    except RuntimeError as e:
        raised = str(e)
    check("probe: still 401 after the re-mint -> RuntimeError naming each base and the login hint",
          raised and "-> 401" in raised and "mcp_auth.py login" in raised and [m for m in mints if m] == [True], f"{raised} {mints}")
    mints.clear()
    try:
        capture(px._pick_base)
    except RuntimeError:
        pass
    check("probe: a recent failure is not re-probed (no re-mint storm)", mints == [], str(mints))

    # The first upstream unserved (revenue-cloud without RevMCP) must not fail every base.
    px._base, px._probe_failed = None, None
    calls = []
    def by_server(url, body, sid=None, timeout=200, _retried=False):
        calls.append(url)
        return (200, None, INIT_OK) if url.endswith("/" + px.SERVERS[1]) else (404, None, "")
    px._http = by_server
    base, _, _ = capture(px._pick_base)
    check("probe: a base routes when a later upstream answers 200 and no base serves the first",
          base == px._BASES[0] and calls == [f"{b}/{px.SERVERS[0]}" for b in px._BASES]
          + [f"{px._BASES[0]}/{px.SERVERS[1]}"], f"{base} {calls}")
    # A base serving only a later upstream must not beat one that serves the first.
    px._base, px._probe_failed = None, None
    def partial(url, body, sid=None, timeout=200, _retried=False):
        first = url.endswith("/" + px.SERVERS[0])
        return (200, None, INIT_OK) if first == url.startswith(px._BASES[1] + "/") else (404, None, "")
    px._http = partial
    base, _, _ = capture(px._pick_base)
    check("probe: a base that serves the first upstream wins over one serving only a later one",
          base == px._BASES[1], str(base))
    # A base whose 200 carries a JSON-RPC error has not negotiated a session: not chosen.
    px._base, px._probe_failed = None, None
    px._http = lambda url, body, sid=None, timeout=200, _retried=False: (
        200, None, INIT_ERR if url.startswith(px._BASES[0] + "/") else INIT_OK)
    base, _, _ = capture(px._pick_base)
    check("probe: a base answering initialize with a JSON-RPC error is skipped", base == px._BASES[1], str(base))
    px._base, px._probe_failed = None, None
    calls.clear()
    def down(url, body, sid=None, timeout=200, _retried=False):
        calls.append(url)
        raise OSError("unreachable")
    px._http = down
    try:
        capture(px._pick_base)
    except RuntimeError:
        pass
    check("probe: an unreachable host is tried once, not once per upstream",
          calls == [f"{b}/{px.SERVERS[0]}" for b in px._BASES], str(calls))

    # A dead token (mcp_auth exits) surfaces as RuntimeError, so serve threads still answer.
    px2 = load("mcp_multiplex_proxy", {"SF_INSTANCE": "https://a.example.com", "SF_CID": "KEY"})
    def dead(**k):
        raise SystemExit(3)
    real_get = px2.mcp_auth.get_access_token
    px2.mcp_auth.get_access_token = dead
    try:
        try:
            capture(px2._token, True)
            kind = None
        except RuntimeError:
            kind = "RuntimeError"
        except SystemExit:
            kind = "SystemExit"
        check("_token: mcp_auth SystemExit becomes RuntimeError", kind == "RuntimeError", str(kind))

        # No token at all, two bases, REAL _http: an auth error, not "unreachable" hosts.
        px2._BASES[:] = ["https://gw.invalid/d/a", "https://gw.invalid/sandbox"]
        px2._base, px2._probe_failed, px2._access = None, None, None
        try:
            capture(px2._pick_base)
            raised = None
        except RuntimeError as e:
            raised = str(e)
        check("probe: no token -> auth error naming login, not unreachable hosts",
              raised and "mcp_auth.py login" in raised and "unreachable" not in raised, raised)
        check("probe: the auth failure is remembered for the backoff", px2._probe_failed is not None)
    finally:
        px2.mcp_auth.get_access_token = real_get

    # A cold-cache upstream that cannot be reached contributes nothing instead of failing the list.
    px2._open_upstream = lambda server: (_ for _ in ()).throw(RuntimeError("no gateway host routed"))
    rv, _, _ = capture(px2._fetch_toollist, "srv/x")
    check("_fetch_toollist: unreachable upstream -> None, not an exception", rv is None, str(rv))

    def unrouted():
        raise RuntimeError("no gateway host routed")
    px2._pick_base = unrouted
    rv, out, _ = capture(px2._prime)
    check("--prime: no routed host -> exit 1 with a FATAL line", rv == 1 and "FATAL" in out, f"{rv} {out!r}")
    px2._pick_base = lambda: "https://gw.invalid"
    px2._http = lambda url, body, sid=None, **k: (
        (200, "S", INIT_OK) if body.get("method") == "initialize" else (500, None, ""))
    rv, out, _ = capture(px2._prime)
    check("--prime: a failed notifications/initialized is reported as such",
          rv == 1 and "notifications/initialized HTTP 500" in out, f"{rv} {out!r}")
    def no_token(url, body, sid=None, **k):
        raise RuntimeError("no usable access token (mcp_auth exit 3); re-run mcp_auth.py login")
    px2._http = no_token
    rv, out, _ = capture(px2._prime)
    check("--prime: no usable token mid-run -> exit 1 with a FATAL line, no traceback",
          rv == 1 and out.startswith("FATAL: no usable access token"), f"{rv} {out!r}")
    px2._http = lambda url, body, sid=None, **k: (200, "S", INIT_ERR)
    rv, out, _ = capture(px2._prime)
    check("--prime: an initialize 200 carrying a JSON-RPC error fails, initialized not sent",
          rv == 1 and "initialize failed: JSON-RPC error" in out and "notifications" not in out, f"{rv} {out!r}")


def main():
    saved = dict(os.environ)
    umask = os.umask(0o022)
    try:
        for fn, wants_tmp in ((test_mcp_org, 1), (test_gateway_bases, 0), (test_write_connector_config, 1),
                              (test_mcp_auth, 1), (test_proxy, 0), (test_proxy_toollist_cache, 1),
                              (test_proxy_host_probe, 0)):
            with tempfile.TemporaryDirectory() as tmp:
                try:
                    fn(tmp) if wants_tmp else fn()
                except Exception as e:  # report, keep going
                    import traceback
                    check(f"{fn.__name__} ran", False, traceback.format_exc(limit=3))
    finally:
        os.umask(umask)
        os.environ.clear()
        os.environ.update(saved)
    width = max(len(n) for n, _, _ in RESULTS)
    for n, ok, d in RESULTS:
        print(f"  {'PASS' if ok else 'FAIL'}  {n:<{width}}  {'' if ok else d}")
    failed = sum(1 for _, ok, _ in RESULTS if not ok)
    print(f"{len(RESULTS) - failed}/{len(RESULTS)} checks passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
