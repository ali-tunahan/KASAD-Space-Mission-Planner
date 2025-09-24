import types
import datetime as _dt
import uuid as _uuid
import pytest

class FakeCursor:
    def __init__(self, state):
        self.state = state
        self._last_result = None
        self._last_one = None
        self.executed = []

    def execute(self, sql, params=None):
        self.executed.append((sql, params))
        s = " ".join(sql.split()).lower()

        # Admin check
        if "from admin" in s and "select 1" in s:
            uid = params[0] if params else None
            self._last_one = {"exists": 1} if uid in self.state.get("admin_ids", set()) else None
            self._last_result = [self._last_one] if self._last_one else []

        # Download report
        elif "from systemreport" in s and "where report_id" in s and "select title, content" in s:
            rid = params[0]
            rep = self.state.get("reports", {}).get(rid)
            self._last_one = rep
            self._last_result = [rep] if rep else []

        # Trainings by astronaut
        elif "from training t join astronaut_completes_training act" in s:
            aid = params[0]
            rows = [
                dict(row, **{"status": row["status"], "training_id": row["training_id"]})
                for row in self.state.get("trainings_by_astronaut", {}).get(aid, [])
            ]
            self._last_result = rows
            self._last_one = rows[0] if rows else None

        # Missions by astronaut
        elif "from mission m join astronaut_accepted_missions am" in s:
            aid = params[0]
            rows = []
            for row in self.state.get("missions_by_astronaut", {}).get(aid, []):
                d = dict(row)
                d.setdefault("mission_id", d.get("mission_id", _uuid.uuid4().hex))
                rows.append(d)
            self._last_result = rows
            self._last_one = rows[0] if rows else None

        # Login user lookup
        elif "from user" in s and "where email" in s and "password" in s and "select *" in s:
            email, password = params
            user = self.state.get("users", {}).get((email, password))
            self._last_one = user
            self._last_result = [user] if user else []

        # Company by id
        elif "from company" in s and "where id" in s and "select *" in s:
            uid = params[0]
            company = self.state.get("companies_by_id", {}).get(uid)
            self._last_one = company
            self._last_result = [company] if company else []

        # Astronaut by id
        elif "from astronaut" in s and "where id" in s and "select *" in s:
            uid = params[0]
            astro = self.state.get("astronauts_by_id", {}).get(uid)
            self._last_one = astro
            self._last_result = [astro] if astro else []

        # Person by id
        elif "from person" in s and "where id" in s and "select *" in s:
            uid = params[0]
            person = self.state.get("persons_by_id", {}).get(uid)
            self._last_one = person
            self._last_result = [person] if person else []

        # Companies listing
        elif "from company" in s and "select id, name" in s:
            self._last_result = self.state.get("companies_list", [])
            self._last_one = self._last_result[0] if self._last_result else None

        else:
            # Default: empty result set
            self._last_result = []
            self._last_one = None

    def fetchone(self):
        return self._last_one

    def fetchall(self):
        return list(self._last_result)

class FakeConnection:
    def __init__(self, state=None):
        self.state = state or {}
        self._begun = False
    def cursor(self, *_args, **_kwargs):
        return FakeCursor(self.state)
    def commit(self): pass
    def rollback(self): pass
    def begin(self): self._begun = True

class FakeMySQL:
    def __init__(self, state=None):
        self.connection = FakeConnection(state or {})

@pytest.fixture
def fake_state():
    today = _dt.date.today()
    # Prepare default fake DB state
    return {
        "admin_ids": set(),
        "reports": {
            "rep1": {"title": "R1", "content": "Report 1 content"},
        },
        "trainings_by_astronaut": {
            "astro1": [
                {"training_id": "t1", "status": 0, "name": "Basics"},
                {"training_id": "t2", "status": 1, "name": "Advanced"},
            ]
        },
        "missions_by_astronaut": {
            "astro1": [
                {"mission_id": "m_future", "launch_date": today + _dt.timedelta(days=10), "title": "Fut"},
                {"mission_id": "m_past", "launch_date": today - _dt.timedelta(days=5), "title": "Past"},
            ]
        },
        "users": {
            ("user@example.com", "secret"): {"id": "u1", "email": "user@example.com"},
        },
        "companies_list": [{"id": "c1", "name": "Acme"}],
        "companies_by_id": {},
        "astronauts_by_id": {},
        "persons_by_id": {},
    }

@pytest.fixture
def flask_app(monkeypatch, fake_state):
    # Import the app module and patch dependencies
    import importlib
    mod = importlib.import_module("app.app")

    # Patch mysql with fake
    monkeypatch.setattr(mod, "mysql", FakeMySQL(fake_state), raising=True)

    # Make sure testing mode is on and secret key set
    mod.app.config["TESTING"] = True
    mod.app.secret_key = "test-secret"

    # Patch render_template to avoid needing actual templates
    def fake_render_template(name, **context):
        # Return a deterministic string to assert in tests if needed
        return f"render:{name}"
    monkeypatch.setattr(mod, "render_template", fake_render_template, raising=True)

    return mod.app

@pytest.fixture
def client(flask_app):
    return flask_app.test_client()