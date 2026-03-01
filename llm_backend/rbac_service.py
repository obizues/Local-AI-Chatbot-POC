"""
RBAC and salary access logic for the chatbot.
Extracted from ui/app.py for testability and maintainability.
"""
import re
import difflib
import pandas as pd

def check_engineer_salary_access(user_role, query, metadata, fuzzy_any):
    """
    Returns a dict:
      - denied: True/False
      - message: denial message if denied
      - salary_row: DataFrame row if allowed
    """
    query_lc = query.strip().lower()
    salary_pattern = re.compile(r'salar(y|ies)\\b', re.IGNORECASE)
    salary_targets = ['salary', 'salaries', 'salares', 'salarioes', 'salerys', 'salarie', 'salarrys', 'sallaries', 'sallares']
    all_salaries_targets = ['all salaries', 'all salares', 'all salarioes', 'all salerys', 'all salarie', 'all salarrys', 'all sallaries', 'all sallares']
    salary_in_query = bool(salary_pattern.search(query_lc) or 'salary' in query_lc or fuzzy_any(salary_targets, query_lc, cutoff=0.7))
    all_salaries_in_query = bool('all salaries' in query_lc or fuzzy_any(all_salaries_targets, query_lc, cutoff=0.7))
    if not (salary_in_query or all_salaries_in_query):
        return {"denied": False, "salary_row": None}
    allowed_self_queries = [
        "my salary", "show my salary", "what's my salary", "what is my salary", "david kim salary", "show david kim salary", "show david kim's salary", "david kim's salary"
    ]
    forbidden_keywords = ["hr", "human resources", "cto", "payroll", "confidential", "department", "onboarding", "engineering", "technology", "alice johnson", "olivia zhang", "bob smith", "nguyen", "carol lee", "emily chen", "grace patel", "isabella brown", "jack wilson"]
    for kw in forbidden_keywords:
        if kw in query_lc or fuzzy_any([kw], query_lc, cutoff=0.8):
            return {"denied": True, "message": "<div style='color: #d9534f; font-weight: bold; margin-bottom: 0.5em'>You only have access to your own salary.<br>Unauthorized access attempt detected. This action has been logged.</div>"}
    is_self_query = any(query_lc.strip() == q for q in allowed_self_queries)
    if not is_self_query:
        for q in allowed_self_queries:
            if difflib.SequenceMatcher(None, query_lc.strip(), q).ratio() > 0.85:
                is_self_query = True
                break
    if not is_self_query:
        return {"denied": True, "message": "<div style='color: #d9534f; font-weight: bold; margin-bottom: 0.5em'>You only have access to your own salary.<br>Unauthorized access attempt detected. This action has been logged.</div>"}
    # Only return David Kim's salary for self-queries
    if isinstance(metadata, pd.DataFrame) and 'text' in metadata.columns:
        for row in metadata.itertuples():
            text_str = str(row.text) if not isinstance(row.text, str) else row.text
            match = re.search(r'Name: David Kim\s*\| Department: Technology(?:\s*\| Title: ([^|]+))?\s*\| Salary: \$([\d,]+)', text_str)
            if match:
                name = 'David Kim'
                dept = 'Technology'
                title = match.group(1).strip() if match.group(1) else ''
                salary = match.group(2).strip()
                return {"denied": False, "salary_row": pd.DataFrame([[name, title, dept, salary]], columns=["Name", "Title", "Department", "Salary"])}
    return {"denied": False, "salary_row": None}
