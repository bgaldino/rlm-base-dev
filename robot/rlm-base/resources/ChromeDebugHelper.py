"""Helper library for running Chrome in headed mode with CDP debugging.

Extends the headless-only ChromeOptionsHelper with visible Chrome options
and a remote debugging port (default 9222) so external tools (Chrome DevTools,
Claude Code via CDP) can connect and inspect the DOM, shadow roots, and
component hierarchies in real time.

Usage in robot file:
    Library    ../../resources/ChromeDebugHelper.py
"""

import logging

import requests
from selenium import webdriver

_logger = logging.getLogger(__name__)

DEFAULT_CDP_PORT = 9222


def get_visible_chrome_options(debug_port=DEFAULT_CDP_PORT):
    """Create Chrome options for headed (visible) execution with CDP debugging.

    Args:
        debug_port: Remote debugging port (default: 9222).

    Returns:
        selenium.webdriver.ChromeOptions: Configured for visible execution
        with remote debugging enabled.
    """
    options = webdriver.ChromeOptions()

    # No --headless flag — Chrome runs visibly
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-software-rasterizer")
    options.add_argument("--disable-notifications")

    # Enable CDP remote debugging
    options.add_argument(f"--remote-debugging-port={debug_port}")

    return options


def get_cdp_websocket_url(port=DEFAULT_CDP_PORT):
    """Get the CDP WebSocket URL for connecting to the running Chrome instance.

    Chrome must already be running with --remote-debugging-port.

    Args:
        port: The remote debugging port Chrome is listening on.

    Returns:
        The WebSocket debugger URL string, or None if Chrome is not reachable.
    """
    try:
        resp = requests.get(f"http://localhost:{port}/json/version", timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            ws_url = data.get("webSocketDebuggerUrl", "")
            _logger.info("CDP WebSocket URL: %s", ws_url)
            return ws_url
    except Exception as e:
        _logger.warning("Could not connect to Chrome CDP on port %s: %s", port, e)
    return None


def get_cdp_targets(port=DEFAULT_CDP_PORT):
    """List all CDP targets (pages/tabs) in the running Chrome instance.

    Args:
        port: The remote debugging port Chrome is listening on.

    Returns:
        List of target dictionaries with id, title, url, webSocketDebuggerUrl.
    """
    try:
        resp = requests.get(f"http://localhost:{port}/json", timeout=5)
        if resp.status_code == 200:
            return resp.json()
    except Exception as e:
        _logger.warning("Could not list CDP targets on port %s: %s", port, e)
    return []
