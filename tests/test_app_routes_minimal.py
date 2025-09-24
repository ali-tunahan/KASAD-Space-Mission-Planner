from urllib.parse import urlparse

# Testing library and framework: pytest with Flask test_client.

def _loc(resp):
    return urlparse(resp.headers.get("Location", "")).path

def test_dashboard_requires_login_and_astronaut(client):
    # Not logged in: should redirect to login via check_logged_in
    resp = client.get("/dashboard")
    assert resp.status_code == 302
    assert _loc(resp).endswith("/login")

    # Logged in but wrong account type: still redirects (astronaut_pageguard)
    with client.session_transaction() as sess:
        sess["loggedin"] = True
        sess["accounttype"] = "company"
    resp = client.get("/dashboard")
    assert resp.status_code == 302
    assert _loc(resp).endswith("/login")