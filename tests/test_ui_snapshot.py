
import subprocess
import re
import pytest
import requests
import time
import os
import signal

def test_ui_banner_and_sidebar():
    # Start Streamlit as a background process
    proc = subprocess.Popen([
        "streamlit", "run", "ui/app.py", "--server.headless=true", "--server.port=8502"
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        # Wait for the server to start
        started = False
        for _ in range(30):
            try:
                r = requests.get("http://localhost:8502")
                if r.status_code == 200:
                    started = True
                    break
            except Exception:
                pass
            time.sleep(1)
        assert started, "Streamlit app did not start in time"
        html = r.text
        # Check for the top banner
        assert "top-title-banner" in html or "Top blue app title bar" in html
        # Check for sidebar (Streamlit sidebar class or text)
        assert "sidebar" in html or "stSidebar" in html or "Sidebar" in html
        # Check for chatbox or chat input
        assert re.search(r"chat", html, re.IGNORECASE)
        # Optionally: check for no error messages
        assert "Traceback" not in html
        assert "Exception" not in html
    finally:
        # Kill the Streamlit process
        if proc.poll() is None:
            os.kill(proc.pid, signal.SIGTERM)
            try:
                proc.wait(timeout=10)
            except Exception:
                os.kill(proc.pid, signal.SIGKILL)

# To run: pytest tests/test_ui_snapshot.py
