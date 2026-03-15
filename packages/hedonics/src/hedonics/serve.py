"""
Shared UI server for the Hedonics ecosystem.

Serves dashboard HTML files via a local HTTP server and opens the browser.
Used by all 5 packages via their `ui` CLI command.
"""

import http.server
import threading
import webbrowser
import os
from pathlib import Path


def serve_dashboard(html_path: str | Path, port: int = 0, open_browser: bool = True):
    """Serve a dashboard HTML file and open it in the browser.

    Args:
        html_path: Path to the HTML file
        port: Port to serve on (0 = auto-pick available port)
        open_browser: Whether to open the browser automatically
    """
    html_path = Path(html_path)
    if not html_path.exists():
        print(f"  Dashboard not found: {html_path}")
        return

    directory = str(html_path.parent)
    filename = html_path.name

    handler = lambda *args: http.server.SimpleHTTPRequestHandler(*args, directory=directory)

    server = http.server.HTTPServer(("127.0.0.1", port), handler)
    actual_port = server.server_address[1]

    url = f"http://localhost:{actual_port}/{filename}"
    print(f"\n  Dashboard running at: {url}")
    print(f"  Press Ctrl+C to stop.\n")

    if open_browser:
        webbrowser.open(url)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  Dashboard stopped.")
        server.shutdown()


def get_package_dashboard(package_name: str) -> Path | None:
    """Find the dashboard.html for a package."""
    # Try the installed package location
    try:
        import importlib.resources
        pkg = importlib.import_module(package_name)
        pkg_dir = Path(pkg.__file__).parent
        dashboard = pkg_dir / "dashboard.html"
        if dashboard.exists():
            return dashboard
    except (ImportError, AttributeError):
        pass
    return None
