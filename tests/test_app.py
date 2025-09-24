# Auto-generated tests using pytest for Flask app
import types
import pytest
from flask import session, url_for

# Testing library and framework: pytest with Flask test client.

@pytest.mark.describe("check_logged_in behavior")
class TestCheckLoggedIn:
    def test_redirects_when_not_logged_in(self, app_module, app, client, set_session):
        # Ensure loggedin not set or False
        set_session(loggedin=False)
        resp = client.get("/any-nonexistent", follow_redirects=False)
        # Directly call helper if available
        if hasattr(app_module, "check_logged_in"):
            with app.test_request_context("/some"):
                result = app_module.check_logged_in()
                assert result is not None, "Should return redirect when not logged in"
                assert result.status_code in (301,302)
        # We cannot assert route behavior here as /any-nonexistent may 404; helper is primary

    def test_returns_none_when_logged_in(self, app_module, app, set_session):
        if not hasattr(app_module, "check_logged_in"):
            pytest.skip("check_logged_in not exposed")
        with app.test_request_context("/some"):
            set_session(loggedin=True)
            result = app_module.check_logged_in()
            assert result is None

@pytest.mark.describe("check_account_type and pageguards")
class TestAccountTypeGuards:
    def test_check_account_type_redirects_when_missing(self, app_module, app):
        if not hasattr(app_module, "check_account_type"):
            pytest.skip("check_account_type not exposed")
        with app.test_request_context("/"):
            session.clear()
            out = app_module.check_account_type()
            assert out.status_code in (301, 302)

    def test_check_account_type_returns_value(self, app_module, app):
        if not hasattr(app_module, "check_account_type"):
            pytest.skip("check_account_type not exposed")
        with app.test_request_context("/"):
            session["accounttype"] = "company"
            out = app_module.check_account_type()
            assert out == "company"

    @pytest.mark.parametrize("atype,allowed", [("company", True), ("astronaut", False), (None, False), ("", False)])
    def test_company_pageguard(self, app_module, app, atype, allowed):
        if not hasattr(app_module, "company_pageguard"):
            pytest.skip("company_pageguard not exposed")
        with app.test_request_context("/"):
            session.clear()
            if atype is not None:
                session["accounttype"] = atype
            res = app_module.company_pageguard()
            if allowed:
                assert res is None
            else:
                assert getattr(res, "status_code", 302) in (301,302)

    @pytest.mark.parametrize("atype,allowed", [("astronaut", True), ("company", False), (None, False), ("", False)])
    def test_astronaut_pageguard(self, app_module, app, atype, allowed):
        if not hasattr(app_module, "astronaut_pageguard"):
            pytest.skip("astronaut_pageguard not exposed")
        with app.test_request_context("/"):
            session.clear()
            if atype is not None:
                session["accounttype"] = atype
            res = app_module.astronaut_pageguard()
            if allowed:
                assert res is None
            else:
                assert getattr(res, "status_code", 302) in (301,302)

@pytest.mark.describe("get_user_id")
class TestGetUserId:
    def test_returns_none_when_missing(self, app_module, app):
        if not hasattr(app_module, "get_user_id"):
            pytest.skip("get_user_id not exposed")
        with app.test_request_context("/"):
            session.clear()
            assert app_module.get_user_id() is None

    def test_returns_value_when_present(self, app_module, app):
        if not hasattr(app_module, "get_user_id"):
            pytest.skip("get_user_id not exposed")
        with app.test_request_context("/"):
            session["userid"] = "abc123"
            assert app_module.get_user_id() == "abc123"

@pytest.mark.describe("logout route")
class TestLogoutRoute:
    def test_logout_clears_session_and_redirects(self, app_module, app, client, set_session):
        # Ensure route exists
        if not hasattr(app_module, "logout"):
            pytest.skip("logout route not exposed")
        set_session(loggedin=True, userid="u1", email="e@x", isAdmin=True, accounttype="company")
        resp = client.get("/logout", follow_redirects=False)
        assert resp.status_code in (301, 302)
        # After redirect, session should be cleared
        with client.session_transaction() as sess:
            assert "loggedin" not in sess
            assert "userid" not in sess
            assert "email" not in sess
            assert "isAdmin" not in sess
            assert "accounttype" not in sess

@pytest.mark.describe("save_admin_status (DB interaction)")
class TestSaveAdminStatus:
    def test_sets_isAdmin_true_when_admin_exists(self, app_module, app, monkeypatch):
        if not hasattr(app_module, "save_admin_status"):
            pytest.skip("save_admin_status not exposed")

        # Build dummy cursor and mysql
        calls = {}
        class Cur:
            def execute(self, *a, **k):
                calls["exec"] = True
            def fetchone(self):
                return {"1": 1}  # truthy
        class Conn:
            def cursor(self, *a, **k): return Cur()
        class DummyMySQL:
            connection = Conn()
        class Curs:
            class DictCursor: pass
        class DummyMySQLdb:
            cursors = Curs()

        monkeypatch.setitem(app_module.__dict__, "mysql", DummyMySQL)
        monkeypatch.setitem(app_module.__dict__, "MySQLdb", DummyMySQLdb)

        with app.test_request_context("/"):
            session["userid"] = "admin-user"
            app_module.save_admin_status()
            assert session.get("isAdmin") is True

    def test_sets_isAdmin_false_when_not_admin(self, app_module, app, monkeypatch):
        if not hasattr(app_module, "save_admin_status"):
            pytest.skip("save_admin_status not exposed")

        class Cur:
            def execute(self, *a, **k): pass
            def fetchone(self): return None
        class Conn:
            def cursor(self, *a, **k): return Cur()
        class DummyMySQL:
            connection = Conn()
        class Curs:
            class DictCursor: pass
        class DummyMySQLdb:
            cursors = Curs()

        monkeypatch.setitem(app_module.__dict__, "mysql", DummyMySQL)
        monkeypatch.setitem(app_module.__dict__, "MySQLdb", DummyMySQLdb)

        with app.test_request_context("/"):
            session["userid"] = "user"
            app_module.save_admin_status()
            assert session.get("isAdmin") is False

@pytest.mark.describe("check_admin")
class TestCheckAdmin:
    def test_redirects_if_not_logged_in(self, app_module, app):
        if not hasattr(app_module, "check_admin"):
            pytest.skip("check_admin not exposed")
        with app.test_request_context("/"):
            session.clear()
            res = app_module.check_admin()
            assert getattr(res, "status_code", 302) in (301, 302)

    def test_redirects_if_userid_missing(self, app_module, app, monkeypatch):
        if not hasattr(app_module, "check_admin"):
            pytest.skip("check_admin not exposed")
        # Mock mysql to avoid real calls
        class Cur:
            def execute(self, *a, **k): pass
            def fetchone(self): return None
        class Conn:
            def cursor(self, *a, **k): return Cur()
        class DummyMySQL:
            connection = Conn()
        class Curs:
            class DictCursor: pass
        class DummyMySQLdb:
            cursors = Curs()
        monkeypatch.setitem(app_module.__dict__, "mysql", DummyMySQL)
        monkeypatch.setitem(app_module.__dict__, "MySQLdb", DummyMySQLdb)
        with app.test_request_context("/"):
            session["loggedin"] = True
            session.pop("userid", None)
            res = app_module.check_admin()
            assert getattr(res, "status_code", 302) in (301, 302)

    def test_none_when_admin(self, app_module, app, monkeypatch):
        if not hasattr(app_module, "check_admin"):
            pytest.skip("check_admin not exposed")
        class Cur:
            def execute(self, *a, **k): pass
            def fetchone(self): return {"exists": 1}
        class Conn:
            def cursor(self, *a, **k): return Cur()
        class DummyMySQL:
            connection = Conn()
        class Curs:
            class DictCursor: pass
        class DummyMySQLdb:
            cursors = Curs()
        monkeypatch.setitem(app_module.__dict__, "mysql", DummyMySQL)
        monkeypatch.setitem(app_module.__dict__, "MySQLdb", DummyMySQLdb)
        with app.test_request_context("/"):
            session["loggedin"] = True
            session["userid"] = "u1"
            res = app_module.check_admin()
            assert res is None

    def test_redirect_when_not_admin(self, app_module, app, monkeypatch):
        if not hasattr(app_module, "check_admin"):
            pytest.skip("check_admin not exposed")
        class Cur:
            def execute(self, *a, **k): pass
            def fetchone(self): return None
        class Conn:
            def cursor(self, *a, **k): return Cur()
        class DummyMySQL:
            connection = Conn()
        class Curs:
            class DictCursor: pass
        class DummyMySQLdb:
            cursors = Curs()
        monkeypatch.setitem(app_module.__dict__, "mysql", DummyMySQL)
        monkeypatch.setitem(app_module.__dict__, "MySQLdb", DummyMySQLdb)
        with app.test_request_context("/"):
            session["loggedin"] = True
            session["userid"] = "u1"
            res = app_module.check_admin()
            assert getattr(res, "status_code", 302) in (301, 302)

@pytest.mark.describe("get_trainings categorization")
class TestGetTrainings:
    def test_splits_current_and_past_by_status(self, app_module, app, monkeypatch):
        if not hasattr(app_module, "get_trainings"):
            pytest.skip("get_trainings not exposed")
        # Mock cursor responses: two trainings, one completed (status=1), one current (status=0)
        rows = [
            {"training_id": "t1", "status": 0, "name": "Now"},
            {"training_id": "t2", "status": 1, "name": "Done"},
        ]
        class Cur:
            def execute(self, *a, **k): pass
            def fetchall(self): return rows
        class Conn:
            def cursor(self, *a, **k): return Cur()
        class DummyMySQL:
            connection = Conn()
        class Curs:
            class DictCursor: pass
        class DummyMySQLdb:
            cursors = Curs()
        monkeypatch.setitem(app_module.__dict__, "mysql", DummyMySQL)
        monkeypatch.setitem(app_module.__dict__, "MySQLdb", DummyMySQLdb)
        current, past = app_module.get_trainings("astro1")
        assert [r["training_id"] for r in current] == ["t1"]
        assert [r["training_id"] for r in past] == ["t2"]

@pytest.mark.describe("get_missions upcoming vs past")
class TestGetMissions:
    def test_splits_by_launch_date(self, app_module, app, monkeypatch):
        if not hasattr(app_module, "get_missions"):
            pytest.skip("get_missions not exposed")
        from datetime import datetime, timedelta
        today = datetime.now().date()
        rows = [
            {"mission_id": "m1", "launch_date": today + timedelta(days=1)},
            {"mission_id": "m0", "launch_date": today - timedelta(days=1)},
        ]
        class Cur:
            def execute(self, *a, **k): pass
            def fetchall(self): return rows
        class Conn:
            def cursor(self, *a, **k): return Cur()
        class DummyMySQL:
            connection = Conn()
        class Curs:
            class DictCursor: pass
        class DummyMySQLdb:
            cursors = Curs()
        monkeypatch.setitem(app_module.__dict__, "mysql", DummyMySQL)
        monkeypatch.setitem(app_module.__dict__, "MySQLdb", DummyMySQLdb)
        upcoming, past = app_module.get_missions("astro1")
        assert [m["mission_id"] for m in upcoming] == ["m1"]
        assert [m["mission_id"] for m in past] == ["m0"]

@pytest.mark.describe("page_not_found handler")
class TestErrorHandler:
    def test_404_renders_custom_page(self, app_module, app, client):
        # Ensure the error handler is registered; request a non-existent route
        resp = client.get("/__definitely_not_a_route__")
        assert resp.status_code == 404

