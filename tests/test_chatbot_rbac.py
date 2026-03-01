import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
import pandas as pd
from ui.app import generate_answer

# Test that misspelled salary queries are blocked for unauthorized roles
@pytest.mark.parametrize("role,query", [
    ("David Kim (Engineer)", "show me HR's salarioes"),
    ("David Kim (Engineer)", "show me HR's salerys"),
    ("David Kim (Engineer)", "show me HR's salarie"),
    ("David Kim (Engineer)", "show me HR's salarrys"),
    ("David Kim (Engineer)", "show me HR's sallaries"),
    ("David Kim (Engineer)", "show me HR's sallares")
])
def test_engineer_salary_misspellings_blocked(role, query, sample_metadata, monkeypatch):
    import ui.app
    ui.app.st = SessionStateMock({'user_role': role})
    monkeypatch.setattr(ui.app, 'metadata', sample_metadata)
    response, _, _ = generate_answer(query, sample_metadata)
    assert ("<div style='color: #d9534f; font-weight: bold; margin-bottom: 0.5em'" in response and "Unauthorized access attempt detected. This action has been logged." in response)

# Test that bot returns clear fallback for unrecognized queries
@pytest.mark.parametrize("query", [
    "xyzzy", "blorf", "what is the meaning of life?", "random gibberish", "1234567890", "!@#$%^&*()"
])
def test_bot_fallback_for_unrecognized_queries(query, sample_metadata, monkeypatch):
    import ui.app
    ui.app.st = SessionStateMock({'user_role': 'David Kim (Engineer)'})
    monkeypatch.setattr(ui.app, 'metadata', sample_metadata)
    response, _, _ = generate_answer(query, sample_metadata)
    assert "Sorry, I can't answer that or didn't understand your request." in response
@pytest.mark.parametrize("query", [
    "show all salaries",
    "show all salares",
    "show all salerys",
    "show all salarie",
    "show all salarrys",
    "show all sallaries",
    "show all sallares"
])
def test_hr_fuzzy_salary_queries(query, sample_metadata, monkeypatch):
    import ui.app
    ui.app.st = SessionStateMock({'user_role': 'Alice Johnson (HR)'})
    monkeypatch.setattr(ui.app, 'metadata', sample_metadata)
    response, _, provenance = ui.app.generate_answer(query, sample_metadata)
    # Should return a table of all employee salaries
    assert "<table" in response or "Name" in response
    assert provenance == "payroll_confidential.txt"
import os
@pytest.mark.parametrize("query", [
    "show hr's salaries",
    "show hr salaries",
    "show hr salary",
    "show human resources salaries",
    "show human resources salary",
    "show hr's salary",
    "show hr department salary",
    "show hr department salaries"
])
def test_cto_hr_salary_block_audit(query, sample_metadata, monkeypatch, tmp_path):
    import ui.app
    audit_log_path = tmp_path / "access_audit.log"
    def fake_write_audit_log(message):
        with open(audit_log_path, 'a', encoding='utf-8') as f:
            f.write(message)
    monkeypatch.setattr(ui.app, 'write_audit_log', fake_write_audit_log)
    ui.app.st = SessionStateMock({'user_role': 'Olivia Zhang (CTO)'})
    monkeypatch.setattr(ui.app, 'metadata', sample_metadata)
    response, _, _ = generate_answer(query, sample_metadata)
# Test that CTO HR salary queries return the correct message and log the attempt
@pytest.mark.parametrize("query", [
    "show hr's salaries",
    "show hr salaries",
    "show hr salary",
    "show human resources salaries",
    "show human resources salary",
    "show hr's salary",
    "show hr department salary",
    "show hr department salaries"
])
def test_cto_hr_salary_block_audit(query, sample_metadata, monkeypatch, tmp_path):
    import ui.app
    # Patch audit log path
    audit_log_path = tmp_path / "access_audit.log"
    def fake_write_audit_log(message):
        with open(audit_log_path, 'a', encoding='utf-8') as f:
            f.write(message)
    monkeypatch.setattr(ui.app, 'write_audit_log', fake_write_audit_log)
    ui.app.st = SessionStateMock({'user_role': 'Olivia Zhang (CTO)'})
    monkeypatch.setattr(ui.app, 'metadata', sample_metadata)
    response, _, _ = generate_answer(query, sample_metadata)
    assert ("<div style='color: #d9534f; font-weight: bold; margin-bottom: 0.5em'" in response and "Unauthorized access attempt detected. This action has been logged." in response)
    with open(audit_log_path, "r", encoding="utf-8") as f:
        log_content = f.read()
        assert "Unauthorized access attempt by Olivia Zhang" in log_content

# Test that CTO cannot access HR salaries with various query patterns
@pytest.mark.parametrize("query", [
    "show hr's salaries",
    "show hr salaries",
    "show hr salary",
    "show human resources salaries",
    "show human resources salary",
    "show hr's salary",
    "show hr department salary",
    "show hr department salaries"
])
def test_cto_hr_salary_block(query, sample_metadata, monkeypatch):
    import ui.app
    ui.app.st = SessionStateMock({'user_role': 'Olivia Zhang (CTO)'})
    monkeypatch.setattr(ui.app, 'metadata', sample_metadata)
    response, _, _ = generate_answer(query, sample_metadata)
    # Assert warning is present and table is NOT present
    assert ("<div style='color: #d9534f; font-weight: bold; margin-bottom: 0.5em'" in response and "Unauthorized access attempt detected. This action has been logged." in response)
    assert "<table" not in response




def test_salary_source_provenance(sample_metadata, monkeypatch):
    import ui.app
    ui.app.st = SessionStateMock({'user_role': 'Alice Johnson (HR)'})
    monkeypatch.setattr(ui.app, 'metadata', sample_metadata)
    response, _, provenance = ui.app.generate_answer("show my salary", sample_metadata)
    assert provenance == "payroll_confidential.txt"

    ui.app.st = SessionStateMock({'user_role': 'Olivia Zhang (CTO)'})
    monkeypatch.setattr(ui.app, 'metadata', sample_metadata)
    response, _, provenance = ui.app.generate_answer("show david's salary", sample_metadata)
    assert provenance == "payroll_confidential.txt"

    ui.app.st = SessionStateMock({'user_role': 'David Kim (Engineer)'})
    monkeypatch.setattr(ui.app, 'metadata', sample_metadata)
    response, _, provenance = ui.app.generate_answer("show my salary", sample_metadata)
    assert provenance == "payroll_confidential.txt"

import pytest
import pandas as pd
from ui.app import generate_answer

# Expanded edge case test for unauthorized salary queries
@pytest.mark.parametrize("role,query", [
    ("David Kim (Engineer)", "show Nguyen salary"),
    ("David Kim (Engineer)", "show Carol Lee's salary"),
    ("David Kim (Engineer)", "show Emily Chen's salary"),
    ("David Kim (Engineer)", "show Grace Patel's salary"),
    ("David Kim (Engineer)", "show Isabella Brown's salary"),
    ("David Kim (Engineer)", "show Alice Johnson's salary"),
    ("David Kim (Engineer)", "show Bob Smith's salary"),
    ("David Kim (Engineer)", "show Olivia Zhang's salary"),
    ("David Kim (Engineer)", "show Jack Wilson's salary"),
    ("David Kim (Engineer)", "show HR salary"),
    ("David Kim (Engineer)", "show Technology salary"),
    ("David Kim (Engineer)", "show CTO salary"),
    ("David Kim (Engineer)", "show payroll salary"),
    ("David Kim (Engineer)", "show confidential salary"),
    ("David Kim (Engineer)", "show department salary"),
    ("David Kim (Engineer)", "show onboarding salary"),
])
def test_engineer_unauthorized_salary_queries(role, query, sample_metadata, monkeypatch):
    import ui.app
    ui.app.st = SessionStateMock({'user_role': role})
    monkeypatch.setattr(ui.app, 'metadata', sample_metadata)
    response, _, _ = generate_answer(query, sample_metadata)
    # Assert warning is present and table is NOT present
    assert ("<div style='color: #d9534f; font-weight: bold; margin-bottom: 0.5em'" in response and "Unauthorized access attempt detected. This action has been logged." in response)
    assert "<table" not in response
import pytest
import pandas as pd
from ui.app import generate_answer

# Mock Streamlit session state
class SessionStateMock:
    def __init__(self, initial=None):
        self.session_state = initial or {}
    def get(self, key, default=None):
        return self.session_state.get(key, default)

@pytest.fixture(autouse=True)
def patch_streamlit(monkeypatch):
    import ui.app
    monkeypatch.setattr(ui.app, 'st', SessionStateMock())

# Sample metadata DataFrame
@pytest.fixture
def sample_metadata():
    data = [
        {'text': 'Name: Alice Johnson | Department: HR | Title: HR | Salary: $112,000'},
        {'text': 'Name: Bob Smith | Department: HR | Salary: $98,500'},
        {'text': 'Name: David Kim | Department: Technology | Salary: $185,200'},
        {'text': 'Name: Olivia Zhang | Department: Technology | Title: CTO | Salary: $300,000'},
    ]
    return pd.DataFrame(data)

@pytest.mark.parametrize("role,query,expected", [
    ("Alice Johnson (HR)", "what are the HR salaries", "Alice Johnson"),
    ("Alice Johnson (HR)", "all salaries", "Alice Johnson"),
    ("Alice Johnson (HR)", "show my salary", "Alice Johnson"),
    ("Alice Johnson (HR)", "what's my salary", "Alice Johnson"),
    ("Alice Johnson (HR)", "show the cto's salary", "Olivia Zhang (CTO)"),
    ("Alice Johnson (HR)", "show Olivia Zhang's salary", "Olivia Zhang (CTO)"),
    ("David Kim (Engineer)", "all salaries", "You only have access to your own salary"),
    ("David Kim (Engineer)", "show my salary", "David Kim"),
    ("David Kim (Engineer)", "what's my salary", "David Kim"),
    ("Olivia Zhang (CTO)", "technology salaries", "Olivia Zhang"),
    ("Olivia Zhang (CTO)", "show my salary", "Olivia Zhang"),
    ("Olivia Zhang (CTO)", "what's my salary", "Olivia Zhang"),
    ("Olivia Zhang (CTO)", "HR salaries", "You do not have access to HR or other department salary information"),
    ("Olivia Zhang (CTO)", "show david's salary", "David Kim"),
])
def test_rbac_responses(role, query, expected, sample_metadata, monkeypatch):
    import ui.app
    ui.app.st = SessionStateMock({'user_role': role})
    # Patch metadata in app
    monkeypatch.setattr(ui.app, 'metadata', sample_metadata)
    response, _, _ = generate_answer(query, sample_metadata)
    if role == "Alice Johnson (HR)" and query in ["what are the HR salaries", "all salaries"]:
        # HR should see all employees for 'all salaries'
        for name in ["Alice Johnson", "Bob Smith", "David Kim", "Olivia Zhang"]:
            assert name in response
    else:
        # Accept both HTML-escaped and unescaped CTO/HR names
        if expected == "Olivia Zhang (CTO)":
            assert ("Olivia Zhang (CTO)" in response) or ("Olivia Zhang &#40;CTO&#41;" in response)
        elif expected == "Alice Johnson (HR)":
            assert ("Alice Johnson (HR)" in response) or ("Alice Johnson &#40;HR&#41;" in response)
        else:
            assert expected in response

@pytest.mark.parametrize("role,query,expected", [
    ("Alice Johnson (HR)", "HR salaries for Bob Smith", "Bob Smith"),
    ("Alice Johnson (HR)", "HR salaries for Alice Johnson", "Alice Johnson (HR)"),
    ("Olivia Zhang (CTO)", "Technology salaries for Olivia Zhang", "Olivia Zhang (CTO)"),
    ("Olivia Zhang (CTO)", "Technology salaries for David Kim", "David Kim"),
])
def test_rbac_name_department_search(role, query, expected, sample_metadata, monkeypatch):
    import ui.app
    ui.app.st = SessionStateMock({'user_role': role})
    monkeypatch.setattr(ui.app, 'metadata', sample_metadata)
    response, _, _ = generate_answer(query, sample_metadata)
    assert expected in response

@pytest.mark.parametrize("role,query,expected", [
    ("Alice Johnson (HR)", "HR salaries for Bob", "Bob Smith"),  # Partial name
    ("Alice Johnson (HR)", "Tech salaries", "David Kim"),        # Ambiguous department
    ("David Kim (Engineer)", "what's my salary", "David Kim"),   # Short ask after context
])
def test_rbac_partial_ambiguous_context(role, query, expected, sample_metadata, monkeypatch):
    import ui.app
    ui.app.st = SessionStateMock({'user_role': role, 'last_salary_query': 'what is my salary'})
    monkeypatch.setattr(ui.app, 'metadata', sample_metadata)
    response, _, _ = generate_answer(query, sample_metadata)
    assert expected in response

@pytest.mark.parametrize("role,query,expected_text,expected_source", [
    ("Alice Johnson (HR)", "what is my onboarding", "HR Department Onboarding", "mock_data/HR/hr_onboarding.md"),
    ("Alice Johnson (HR)", "show onboarding", "HR Department Onboarding", "mock_data/HR/hr_onboarding.md"),
    ("David Kim (Engineer)", "what is my onboarding", "Engineering Department Onboarding", "mock_data/Engineering/engineering_onboarding.md"),
    ("David Kim (Engineer)", "show onboarding", "Engineering Department Onboarding", "mock_data/Engineering/engineering_onboarding.md"),
    ("Olivia Zhang (CTO)", "what is my onboarding", "Technology Department Onboarding", "mock_data/Technology/technology_onboarding.md"),
    ("Olivia Zhang (CTO)", "show onboarding", "Technology Department Onboarding", "mock_data/Technology/technology_onboarding.md"),
])
def test_hr_onboarding_source(role, query, expected_text, expected_source, sample_metadata, monkeypatch):
    import ui.app
    ui.app.st = SessionStateMock({'user_role': role})
    monkeypatch.setattr(ui.app, 'metadata', sample_metadata)
    response, _, provenance = generate_answer(query, sample_metadata)
    assert expected_text in response
    assert provenance == expected_source

def test_hr_my_salary_only_returns_self(sample_metadata, monkeypatch):
    import ui.app
    ui.app.st = SessionStateMock({'user_role': 'Alice Johnson (HR)'})
    monkeypatch.setattr(ui.app, 'metadata', sample_metadata)
    response, _, _ = generate_answer("show my salary", sample_metadata)
    # Should only contain Alice Johnson (HR), not Bob Smith or others
    assert "Alice Johnson (HR)" in response
    assert "Bob Smith" not in response
    assert "David Kim" not in response
    assert "Olivia Zhang" not in response


def test_hr_subset_salary_returns_only_subset(sample_metadata, monkeypatch):
    import ui.app
    ui.app.st = SessionStateMock({'user_role': 'Alice Johnson (HR)'})
    monkeypatch.setattr(ui.app, 'metadata', sample_metadata)
    response, _, _ = generate_answer("show Bob Smith's salary", sample_metadata)
    # Should only contain Bob Smith
    assert "Bob Smith" in response
    assert "Alice Johnson" not in response
    assert "David Kim" not in response
    assert "Olivia Zhang" not in response


def test_cto_subset_salary_returns_only_subset(sample_metadata, monkeypatch):
    import ui.app
    ui.app.st = SessionStateMock({'user_role': 'Olivia Zhang (CTO)'})
    monkeypatch.setattr(ui.app, 'metadata', sample_metadata)
    response, _, _ = generate_answer("show David Kim's salary", sample_metadata)
    # Should only contain David Kim
    assert "David Kim" in response
    assert "Olivia Zhang" not in response
    assert "Alice Johnson" not in response
    assert "Bob Smith" not in response


def test_engineer_my_salary_only_returns_self(sample_metadata, monkeypatch):
    import ui.app
    ui.app.st = SessionStateMock({'user_role': 'David Kim (Engineer)'})
    monkeypatch.setattr(ui.app, 'metadata', sample_metadata)
    response, _, _ = generate_answer("show my salary", sample_metadata)
    # Should only contain David Kim
    assert "David Kim" in response
    assert "Alice Johnson" not in response
    assert "Bob Smith" not in response
    assert "Olivia Zhang" not in response


def test_hr_partial_name_salary_returns_only_jack(sample_metadata, monkeypatch):
    import ui.app
    import pandas as pd
    ui.app.st = SessionStateMock({'user_role': 'Alice Johnson (HR)'})
    # Add Jack Wilson to sample_metadata
    jack_row = pd.DataFrame([{'text': 'Name: Jack Wilson | Department: HR | Salary: $99,950'}])
    sample_metadata = pd.concat([sample_metadata, jack_row], ignore_index=True)
    monkeypatch.setattr(ui.app, 'metadata', sample_metadata)
    response, _, _ = generate_answer("show jack's salary", sample_metadata)
    # Should only contain Jack Wilson
    assert "Jack Wilson" in response
    assert "Alice Johnson" not in response
    assert "Bob Smith" not in response
    assert "David Kim" not in response
    assert "Olivia Zhang" not in response


def test_hr_department_salary_returns_only_technology(sample_metadata, monkeypatch):
    import ui.app
    import pandas as pd
    ui.app.st = SessionStateMock({'user_role': 'Alice Johnson (HR)'})
    # Add more Technology and HR rows to sample_metadata
    extra_rows = pd.DataFrame([
        {'text': 'Name: Emily Chen | Department: Technology | Salary: $217,300'},
        {'text': 'Name: Grace Patel | Department: Technology | Salary: $208,900'},
        {'text': 'Name: Isabella Brown | Department: Technology | Salary: $220,000'},
        {'text': 'Name: Carol Lee | Department: HR | Salary: $125,750'},
    ])
    sample_metadata = pd.concat([sample_metadata, extra_rows], ignore_index=True)
    monkeypatch.setattr(ui.app, 'metadata', sample_metadata)
    response, _, _ = generate_answer("list all technology salaries", sample_metadata)
    # Should only contain Technology department
    assert "Technology" in response
    assert "Emily Chen" in response
    assert "Grace Patel" in response
    assert "Isabella Brown" in response
    assert "David Kim" in response
    assert "Olivia Zhang" in response
    # Should not contain HR-only names
    assert "Alice Johnson" not in response
    assert "Bob Smith" not in response
    assert "Carol Lee" not in response
    assert "Jack Wilson" not in response

@pytest.mark.parametrize("role,query,expected_names,expected_departments", [
    ("Olivia Zhang (CTO)", "all salaries", ["Olivia Zhang (CTO)", "David Kim"], ["Technology"]),
])
def test_cto_all_salaries_only_technology(role, query, expected_names, expected_departments, sample_metadata, monkeypatch):
    import ui.app
    ui.app.st = SessionStateMock({'user_role': role})
    monkeypatch.setattr(ui.app, 'metadata', sample_metadata)
    response, _, _ = generate_answer(query, sample_metadata)
    # Check limitation message
    assert "You only have access to Technology department salaries." in response
    # Check only Technology department names are present
    for name in expected_names:
        assert name in response
    # Check no HR department names are present
    assert "Alice Johnson" not in response
    assert "Bob Smith" not in response
    # Optionally, check department column if present
    assert "Technology" in response
    assert "HR" not in response

@pytest.mark.parametrize("role,query,expected_names,not_expected_names", [
    ("Alice Johnson (HR)", "show cto salary", ["Olivia Zhang (CTO)"], ["Alice Johnson", "Bob Smith", "David Kim"]),
    ("Alice Johnson (HR)", "show Olivia Zhang's salary", ["Olivia Zhang (CTO)"], ["Alice Johnson", "Bob Smith", "David Kim"]),
])
def test_hr_show_cto_salary_only_cto(role, query, expected_names, not_expected_names, sample_metadata, monkeypatch):
    import ui.app
    ui.app.st = SessionStateMock({'user_role': role})
    monkeypatch.setattr(ui.app, 'metadata', sample_metadata)
    response, _, _ = generate_answer(query, sample_metadata)
    for name in expected_names:
        assert name in response
    for name in not_expected_names:
        assert name not in response
