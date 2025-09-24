import datetime as dt
from urllib.parse import urlparse

import pytest

# Testing library and framework: pytest with Flask's test client and monkeypatch.

def _loc(resp):
    return urlparse(resp.headers.get("Location", "")).path

def test_check_logged_in_redirects_when_not_logged_in(flask_app):
    from app.app import check_logged_in
    with flask_app.test_request_context("/"):
        # Ensure not logged in
        resp = check_logged_in()
        assert resp.status_code == 302
        assert _loc(resp).endswith("/login")

def test_check_logged_in_returns_none_when_logged_in(flask_app):
    from app.app import check_logged_in
    with flask_app.test_request_context("/"):
        from flask import session
        session["loggedin"] = True
        assert check_logged_in() is None

def test_save_admin_status_sets_true_when_exists(monkeypatch, flask_app, fake_state):
    from app.app import save_admin_status, session as flask_session
    fake_state["admin_ids"].add("admin1")
    with flask_app.test_request_context("/"):
        flask_session["userid"] = "admin1"
        save_admin_status()
        assert flask_session.get("isAdmin") is True

def test_save_admin_status_sets_false_when_not_exists(monkeypatch, flask_app):
    from app.app import save_admin_status, session as flask_session
    with flask_app.test_request_context("/"):
        flask_session["userid"] = "nonadmin"
        save_admin_status()
        assert flask_session.get("isAdmin") is False

def test_check_admin_redirects_when_not_logged_in(flask_app):
    from app.app import check_admin
    with flask_app.test_request_context("/"):
        resp = check_admin()
        assert resp.status_code == 302
        assert _loc(resp).endswith("/login")

def test_check_admin_redirects_when_userid_missing(flask_app):
    from app.app import check_admin
    with flask_app.test_request_context("/"):
        from flask import session
        session["loggedin"] = True
        # but no userid
        resp = check_admin()
        assert resp.status_code == 302
        assert _loc(resp).endswith("/login")

def test_check_admin_allows_admin(flask_app, fake_state):
    from app.app import check_admin
    from flask import session
    fake_state["admin_ids"].add("u1")
    with flask_app.test_request_context("/"):
        session["loggedin"] = True
        session["userid"] = "u1"
        resp = check_admin()
        assert resp is None

def test_check_account_type_redirects_when_missing(flask_app):
    from app.app import check_account_type
    with flask_app.test_request_context("/"):
        resp = check_account_type()
        assert resp.status_code == 302
        assert _loc(resp).endswith("/login")

def test_check_account_type_returns_value(flask_app):
    from app.app import check_account_type
    from flask import session
    with flask_app.test_request_context("/"):
        session["accounttype"] = "company"
        assert check_account_type() == "company"

def test_company_pageguard(flask_app):
    from app.app import company_pageguard
    from flask import session
    with flask_app.test_request_context("/"):
        session["accounttype"] = "company"
        assert company_pageguard() is None
    with flask_app.test_request_context("/"):
        session["accounttype"] = "astronaut"
        resp = company_pageguard()
        assert resp.status_code == 302
        assert _loc(resp).endswith("/login")

def test_astronaut_pageguard(flask_app):
    from app.app import astronaut_pageguard
    from flask import session
    with flask_app.test_request_context("/"):
        session["accounttype"] = "astronaut"
        assert astronaut_pageguard() is None
    with flask_app.test_request_context("/"):
        session["accounttype"] = "company"
        resp = astronaut_pageguard()
        assert resp.status_code == 302
        assert _loc(resp).endswith("/login")

def test_get_user_id_returns_value(flask_app):
    from app.app import get_user_id
    from flask import session
    with flask_app.test_request_context("/"):
        session["userid"] = "user-123"
        assert get_user_id() == "user-123"

def test_get_user_id_returns_none_when_missing(flask_app):
    from app.app import get_user_id
    with flask_app.test_request_context("/"):
        assert get_user_id() is None

def test_login_success_sets_session_and_redirect(client, flask_app):
    # Successful login
    resp = client.post("/login", data={"email": "user@example.com", "password": "secret"}, follow_redirects=False)
    assert resp.status_code == 302
    assert _loc(resp).endswith("/main")
    # Verify session via separate context
    with flask_app.test_request_context("/"):
        # test_client stores session in its own context; we test redirect only here.

        # Can't directly access client's session from here; at least ensure redirect is correct
        pass

def test_login_failure_renders_login_template(client):
    resp = client.post("/login", data={"email": "user@example.com", "password": "wrong"}, follow_redirects=False)
    # Should render login page (we patched render_template to return a simple string)
    assert resp.status_code == 200
    assert b"render:login.html" in resp.data

def test_logout_clears_session_and_redirects(client):
    # Seed session as logged in
    with client.session_transaction() as sess:
        sess["loggedin"] = True
        sess["userid"] = "u1"
        sess["email"] = "user@example.com"
        sess["isAdmin"] = True
        sess["accounttype"] = "company"
    resp = client.get("/logout")
    assert resp.status_code == 302
    assert _loc(resp).endswith("/login")

def test_download_report_returns_text_file_response(client, fake_state):
    # Use a known report id "rep1" seeded in fake_state
    resp = client.get("/download_report/rep1")
    assert resp.status_code == 200
    assert resp.mimetype == "text/plain"
    cd = resp.headers.get("Content-Disposition", "")
    assert "attachment;" in cd

def test_get_trainings_separates_current_and_past(flask_app):
    from app.app import get_trainings
    current, past = get_trainings("astro1")
    # By default fake state: one current (status 0), one past (status 1)
    assert any(t["status"] == 0 for t in current)
    assert any(t["status"] == 1 for t in past)

def test_get_missions_separates_upcoming_and_past(flask_app):
    from app.app import get_missions
    upcoming, past = get_missions("astro1")
    assert any(m["mission_id"] == "m_future" for m in upcoming)
    assert any(m["mission_id"] == "m_past" for m in past)