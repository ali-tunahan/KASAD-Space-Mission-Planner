import re
from pathlib import Path

import jinja2

# Utility: create a Jinja2 environment pointing at the app/templates dir
# This keeps the tests focused on the template under test without requiring the full web framework runtime.
TEMPLATES_DIR = Path("app") / "templates"
ENV = jinja2.Environment(
    loader=jinja2.FileSystemLoader(str(TEMPLATES_DIR)),
    autoescape=True,
)

def render(template_name="main.html", **context):
    tmpl = ENV.get_template(template_name)
    return tmpl.render(**context)

def norm_space(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()

def test_renders_welcome_header_only_when_no_context():
    html = render()
    assert "Welcome to KASAD" in html
    assert "Your Employer:" not in html
    assert "Astronaut Details" not in html
    assert "Accepted Missions" not in html
    assert "Accepted Bids" not in html

def test_person_employer_header_and_full_name_with_all_parts():
    person = {
        "title": "Dr.",
        "first_name": "Mae",
        "middle_name": "C.",
        "last_name": "Jemison",
    }
    html = render(person=person)
    assert "Your Employer:" in html
    # Full name line should include all, space-normalized and no extra spaces
    assert "Dr. Mae C. Jemison" in norm_space(html)

def test_person_full_name_omits_empty_parts_cleanly():
    person = {
        "title": "",
        "first_name": "Neil",
        "middle_name": "",
        "last_name": "Armstrong",
    }
    html = render(person=person)
    # Ensure no double spaces and no leading/trailing spaces
    assert "Neil Armstrong" in norm_space(html)
    assert "  " not in html

def test_company_block_displays_core_fields_without_astronaut():
    company = {
        "name": "Lunar Logistics",
        "street": "123 Moon Rd",
        "city": "Tranquility",
        "state": "SEA",
        "postal_code": "00001",
        "founding_date": "1969-07-20",
        "area_code": "555",
        "phone_number": "867-5309",
        "balance": "424242.00",
    }
    html = render(company=company)
    assert "Lunar Logistics" in html
    assert "Address: 123 Moon Rd, Tranquility, SEA 00001" in norm_space(html)
    assert "Founded on: 1969-07-20" in html
    assert "Phone: (555) 867-5309" in html
    assert "Balance: $424242.00" in html
    # When astronaut is not provided (falsy), missions/bids sections should appear
    assert "Accepted Missions" in html
    assert "Accepted Bids" in html

def test_missions_and_bids_render_when_not_astronaut():
    company = {"name": "Orbital Ops", "street": "", "city": "", "state": "", "postal_code": "", "founding_date": "", "area_code": "", "phone_number": "", "balance": ""}
    missions = [{"title": "Survey Mare Imbrium"}, {"title": "Deploy Satellite"}]
    bids = [{"title": "Resupply ISS", "name": "Alpha Team"}, {"title": "Repair Hubble", "name": "Bravo Team"}]
    html = render(company=company, missions=missions, bids=bids)
    # Headers visible
    assert "Accepted Missions" in html
    assert "Accepted Bids" in html
    # Items rendered
    assert "Title: Survey Mare Imbrium" in html
    assert "Title: Deploy Satellite" in html
    assert "Title: Resupply ISS Assigned to: Alpha Team" in norm_space(html)
    assert "Title: Repair Hubble Assigned to: Bravo Team" in norm_space(html)

def test_empty_missions_and_bids_lists_still_show_headers_without_items():
    company = {"name": "Void Ventures", "street": "", "city": "", "state": "", "postal_code": "", "founding_date": "", "area_code": "", "phone_number": "", "balance": ""}
    html = render(company=company, missions=[], bids=[])
    assert "Accepted Missions" in html
    assert "Accepted Bids" in html
    # No list items present
    assert 'class="list-group-item' not in html

def test_astronaut_details_render_and_hide_missions_bids_when_truthy():
    astronaut = {
        "date_of_birth": "1970-01-01",
        "nationality": "USA",
        "rank": "Commander",
        "years_of_experience": 15,
    }
    company = {
        "name": "Stellar Systems",
        "street": "1 Galaxy Way",
        "city": "Andromeda",
        "state": "SPC",
        "postal_code": "42424",
        "founding_date": "2000-01-01",
        "area_code": "321",
        "phone_number": "123-4567",
        "balance": "1000.00",
    }
    html = render(company=company, astronaut=astronaut)
    # Astronaut section visible
    assert "Astronaut Details" in html
    assert "Date of Birth: 1970-01-01" in html
    assert "Nationality: USA" in html
    assert "Rank: Commander" in html
    assert "Years of Experience: 15" in html
    # Missions/bids hidden due to `{% if not astronaut %}`
    assert "Accepted Missions" not in html
    assert "Accepted Bids" not in html
    # Company info still shows
    assert "Stellar Systems" in html

def test_person_and_company_together_show_employer_header_and_company_info():
    person = {"title": "Ms.", "first_name": "Sally", "middle_name": None, "last_name": "Ride"}
    company = {"name": "Jet Propulsion Lab", "street": "4800 Oak Grove Dr", "city": "Pasadena", "state": "CA", "postal_code": "91109", "founding_date": "1936-01-01", "area_code": "626", "phone_number": "395-1361", "balance": "500.00"}
    html = render(person=person, company=company)
    assert "Your Employer:" in html
    assert "Jet Propulsion Lab" in html
    assert "Ms. Sally Ride" in norm_space(html)

def test_handles_missing_optional_person_fields_without_breaking():
    # Middle name and title missing; ensure no KeyError and clean output
    person = {"first_name": "Chris", "last_name": "Hadfield"}
    html = render(person=person)
    assert "Chris Hadfield" in norm_space(html)

def test_handles_none_values_in_person_fields_by_omitting():
    person = {"title": None, "first_name": "Yuri", "middle_name": None, "last_name": "Gagarin"}
    html = render(person=person)
    assert "Yuri Gagarin" in norm_space(html)
    assert "None" not in html

def test_company_fields_are_escaped_and_rendered_safely():
    # Ensure autoescaping prevents raw HTML injection
    company = {
        "name": "<b>Unsafe Co</b>",
        "street": "<script>alert(1)</script>",
        "city": "X",
        "state": "Y",
        "postal_code": "Z",
        "founding_date": "2001-02-03",
        "area_code": "000",
        "phone_number": "000-0000",
        "balance": "0.00",
    }
    html = render(company=company)
    # Escaped content should include the literal entities, not interpreted tags
    assert "&lt;b&gt;Unsafe Co&lt;/b&gt;" in html
    assert "<b>Unsafe Co</b>" not in html
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in html
