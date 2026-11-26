#!/usr/bin/env python3
"""Standalone browser checks for a live org: frontdoor login, screenshot, shadow-DOM text.

For agents and humans who need to look at a Lightning page once, without a Robot suite.
Selenium and Chrome for Testing only; the org login comes from the sf CLI.

    python scripts/ui_check/ui_check.py shot --org <sf alias or username> \
        --path /lightning/o/Quote/list --out shot.png [--text]
    UI_CHECK_PASSWORD=<new password> python scripts/ui_check/ui_check.py set-password \
        --org <sf alias> --username <user> --password-env UI_CHECK_PASSWORD
    python scripts/ui_check/ui_check.py user-shot --org <sf alias> --username <user> \
        --password-env UI_CHECK_PASSWORD --path /lightning/page/home --out shot.png

``shot`` logs in as the org's sf user with the frontdoor URL. ``set-password`` and
``user-shot`` use another (test) user: a password set over REST, then the
identity-first login page. Passwords are read from the named environment variable
only; they are never accepted on the command line and never printed.

The frontdoor URL is a live session. It is read inside this process, used for one
``driver.get`` and never printed, logged or put in an exception message; a screenshot
is a viewport capture and shows no URL bar. Do not write the URL, the sid or the
password to files. Environment: CHROME_BINARY and CHROMEDRIVER_PATH (Chrome for
Testing; stock Chrome is blocked on managed workstations), HEADED=1 for a visible
window. Run it with a Python that has selenium (the CumulusCI pipx venv does).
"""

import argparse
import importlib.util
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from urllib.parse import urlparse

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from sf_token import org_auth  # noqa: E402

# tasks/soql_utils.py is stdlib-only; load it by path because tasks/__init__ pulls in CumulusCI.
_spec = importlib.util.spec_from_file_location(
    "soql_utils", Path(__file__).resolve().parents[2] / "tasks" / "soql_utils.py")
_soql_utils = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_soql_utils)
soql_quote = _soql_utils.soql_quote

# The same sid/otp/cshc pattern as robot/rlm-base/resources/SessionUrlGuard.py, duplicated
# because that module imports Robot Framework and this helper must run with Selenium alone.
_SECRET = re.compile(r"(sid|otp|cshc)=[^&\s\"']+", re.I)

# Collects visible text through open shadow roots; LWC synthetic shadow needs no
# special handling because its elements are ordinary light-DOM nodes.
_TEXT_JS = """
const out = [];
const walk = (root) => {
  for (const el of root.querySelectorAll('*')) {
    if (el.shadowRoot) walk(el.shadowRoot);
  }
  for (const n of root.querySelectorAll('h1,h2,h3,button,a,label,th,td,span,p,lightning-formatted-text')) {
    const t = (n.innerText || n.textContent || '').trim();
    if (t && t.length < 200) out.push(t);
  }
};
walk(document);
return Array.from(new Set(out));
"""


def _scrub(text):
    return _SECRET.sub(r"\1=<redacted>", str(text))


def _frontdoor_url(org, path="/lightning/page/home"):
    """The one-time frontdoor URL, landing on ``path``, from `sf org open --url-only -p`; never printed."""
    proc = subprocess.run(
        ["sf", "org", "open", "--url-only", "-p", path, "--json", "--target-org", org],
        capture_output=True, text=True, timeout=120,
    )
    try:
        return json.loads(proc.stdout)["result"]["url"]
    except (ValueError, KeyError, TypeError):
        raise SystemExit("sf org open --url-only returned no URL (exit %s)" % proc.returncode)


def make_driver(headed=None):
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service

    options = webdriver.ChromeOptions()
    binary = os.environ.get("CHROME_BINARY") or os.environ.get("CHROME_BIN")
    if binary:
        options.binary_location = binary
    if not (headed if headed is not None else os.environ.get("HEADED") == "1"):
        options.add_argument("--headless=new")
    for arg in ("--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu", "--window-size=1600,1000"):
        options.add_argument(arg)
    driver_path = os.environ.get("CHROMEDRIVER_PATH")
    service = Service(driver_path) if driver_path else Service()
    return webdriver.Chrome(service=service, options=options)


def frontdoor_login(driver, org, path="/lightning/page/home"):
    """Log the sf user in and land on ``path``. The URL never leaves this function."""
    url = _frontdoor_url(org, path)
    try:
        driver.get(url)
    except Exception as exc:  # selenium messages can echo the URL
        raise SystemExit("frontdoor navigation failed: " + _scrub(str(exc).replace(url, "<url>")))


def wait_ready(driver, seconds=40):
    from selenium.webdriver.support.ui import WebDriverWait

    WebDriverWait(driver, seconds).until(
        lambda d: d.execute_script("return document.readyState") == "complete")
    time.sleep(4)  # Lightning keeps rendering after load


def page_text(driver):
    return driver.execute_script(_TEXT_JS)


def _save(driver, out, want_text):
    driver.save_screenshot(out)
    print("screenshot:", out)
    print("title:", driver.title)
    print("path:", urlparse(driver.current_url).path)
    if want_text:
        for line in page_text(driver)[:150]:
            print("  ", _scrub(line))


def cmd_shot(args):
    driver = make_driver()
    try:
        frontdoor_login(driver, args.org, args.path)
        wait_ready(driver)
        _save(driver, args.out, args.text)
    finally:
        driver.quit()


def _rest(instance, token, method, path, body=None):
    req = urllib.request.Request(
        instance + "/services/data/v68.0" + path, method=method,
        data=json.dumps(body).encode() if body is not None else None,
        headers={"Authorization": "Bearer " + token, "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            raw = resp.read()
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as exc:
        raise SystemExit("REST %s %s failed: HTTP %s %s" % (method, path, exc.code, exc.read()[:300]))


def _password(args):
    value = os.environ.get(args.password_env)
    if not value:
        raise SystemExit("set the password in the environment variable %s" % args.password_env)
    return value


def cmd_set_password(args):
    """Set a password through the REST password resource (sf org generate password needs
    the user to be an org-authenticated user, which test users are not)."""
    password = _password(args)
    instance, token = org_auth(args.org)
    soql = "SELECT Id FROM User WHERE Username = " + soql_quote(args.username)
    rows = _rest(instance, token, "GET", "/query?q=" + urllib.parse.quote(soql))["records"]
    if not rows:
        raise SystemExit("no such user")
    _rest(instance, token, "POST", "/sobjects/User/%s/password" % rows[0]["Id"], {"NewPassword": password})
    print("password set for", args.username)


def _login_as(driver, instance, username, password, new_password=None):
    """Identity-first login page, then the forced change-password page if the org shows it.

    An admin-set password makes the first login stop on /_ui/system/security/ChangePassword;
    ``new_password`` is what it is changed to (the user's password afterwards).
    """
    from selenium.webdriver.common.by import By

    driver.get(instance + "/")
    wait_ready(driver, 30)
    driver.find_element(By.ID, "username").send_keys(username)
    pw = driver.find_elements(By.ID, "password")
    if not pw or not pw[0].is_displayed():
        driver.find_element(By.ID, "Login").click()  # identity-first: continue, then password
        time.sleep(3)
        pw = driver.find_elements(By.ID, "password")
    pw[0].send_keys(password)
    driver.find_element(By.ID, "Login").click()
    wait_ready(driver, 40)
    if driver.find_elements(By.ID, "newpassword"):
        if not new_password:
            raise SystemExit("the org asks this user to change the password on first login: "
                             "pass --new-password-env")
        driver.find_element(By.ID, "newpassword").send_keys(new_password)
        driver.find_element(By.ID, "confirmpassword").send_keys(new_password)
        for answer in driver.find_elements(By.ID, "answer"):
            answer.send_keys("test")  # the security-question answer; not a secret
        driver.find_element(By.ID, "password-button").click()
        wait_ready(driver, 40)


def cmd_user_shot(args):
    instance, _ = org_auth(args.org)
    password = _password(args)
    driver = make_driver()
    try:
        new_password = os.environ.get(args.new_password_env) if args.new_password_env else None
        _login_as(driver, instance, args.username, password, new_password)
        if args.app_path:  # open the app first: record pages render under the last-used app
            driver.get(instance + args.app_path)
            wait_ready(driver)
        driver.get(instance + args.path)
        wait_ready(driver)
        _save(driver, args.out, args.text)
    finally:
        driver.quit()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="cmd", required=True)
    shot = sub.add_parser("shot", help="frontdoor login as the sf user, screenshot a path")
    shot.add_argument("--org", required=True)
    shot.add_argument("--path", default="/lightning/page/home")
    shot.add_argument("--out", required=True)
    shot.add_argument("--text", action="store_true", help="also print visible text through shadow roots")
    shot.set_defaults(func=cmd_shot)
    pw = sub.add_parser("set-password", help="set a user's password over REST")
    pw.add_argument("--org", required=True)
    pw.add_argument("--username", required=True)
    pw.add_argument("--password-env", required=True, help="env var holding the new password")
    pw.set_defaults(func=cmd_set_password)
    us = sub.add_parser("user-shot", help="log in as another user with a password, screenshot a path")
    us.add_argument("--org", required=True)
    us.add_argument("--username", required=True)
    us.add_argument("--password-env", required=True, help="env var holding the password")
    us.add_argument("--path", default="/lightning/page/home")
    us.add_argument("--new-password-env", help="env var holding the password to set on the "
                    "forced change-password page (needed after set-password)")
    us.add_argument("--app-path", help="e.g. /lightning/app/c__<DeveloperName>, opened before --path")
    us.add_argument("--out", required=True)
    us.add_argument("--text", action="store_true")
    us.set_defaults(func=cmd_user_shot)
    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
