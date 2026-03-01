"""
HR/CTO salary and provenance logic for the chatbot.
Extracted from ui/app.py for testability and maintainability.
"""
import re
import pandas as pd
import difflib

def get_salary_and_provenance(user_role, query, salaries, fuzzy_any):
    """
    Returns a dict:
      - html_table: HTML table string or None
      - provenance: source file string or None
      - message: error or info message (optional)
    """
    query_lc = query.strip().lower()
    start_time = 0.0  # UI should set this
    # HR logic
    if user_role == 'Alice Johnson (HR)':
        # HR can see all salaries for 'all salaries' and similar queries
        all_salaries_patterns = [
            'all salaries', 'all salares', 'all salarioes', 'all salerys', 'all salarie', 'all salarrys', 'all sallaries', 'all sallares',
            'show all salaries', 'show all salares', 'show all salarioes', 'show all salerys', 'show all salarie', 'show all salarrys', 'show all sallaries', 'show all sallares',
            'show salaries', "everyone's salary", "everyone's salaries", 'list all salaries'
        ]
        if (
            re.search(r"all salaries", query_lc)
            or re.search(r"show all salaries", query_lc)
            or re.search(r"what are the hr salaries", query_lc)
            or fuzzy_any(all_salaries_patterns, query_lc, cutoff=0.7)
        ):
            if salaries:
                filtered_df = pd.DataFrame(salaries, columns=["Name", "Title", "Department", "Salary"])
                html_table = filtered_df.to_html(index=False, escape=False, border=0, classes="salary-table")
                html_table = html_table.replace('Olivia Zhang &#40;CTO&#41;', 'Olivia Zhang (CTO)').replace('Alice Johnson &#40;HR&#41;', 'Alice Johnson (HR)')
                return {"html_table": html_table, "provenance": 'payroll_confidential.txt'}
            else:
                return {"message": "No salary information found.", "provenance": 'payroll_confidential.txt'}
        # HR can see CTO salary for fuzzy/variant CTO queries
        if any(alias in query_lc for alias in ["cto", "chief technology officer", "olivia zhang"]):
            cto_candidates = []
            for s in salaries:
                name_lc = s[0].strip().lower()
                title_lc = (s[1] or '').strip().lower()
                if 'olivia zhang' in name_lc or 'cto' in name_lc or 'cto' in title_lc:
                    cto_candidates.append(s)
            cto_row = None
            for s in cto_candidates:
                if 'olivia zhang' in s[0].strip().lower() and 'cto' in (s[1] or '').strip().lower():
                    cto_row = s
                    break
            if not cto_row and cto_candidates:
                cto_row = cto_candidates[0]
            if cto_row:
                filtered_df = pd.DataFrame([cto_row], columns=["Name", "Title", "Department", "Salary"])
                html_table = filtered_df.to_html(index=False, escape=False, border=0, classes="salary-table")
                html_table = html_table.replace('Olivia Zhang &#40;CTO&#41;', 'Olivia Zhang (CTO)').replace('Alice Johnson &#40;HR&#41;', 'Alice Johnson (HR)')
                return {"html_table": html_table, "provenance": 'payroll_confidential.txt'}
            else:
                return {"message": "No salary information found.", "provenance": 'payroll_confidential.txt'}
        # HR can only see their own salary for self-queries
        self_query_patterns = [r"show my salary", r"my salary", r"what's my salary", r"what is my salary", r"alice johnson salary", r"show alice johnson salary", r"show alice johnson's salary", r"alice johnson's salary"]
        if any(re.search(pat, query_lc) for pat in self_query_patterns) or query_lc.strip() in ["show my salary", "my salary", "what's my salary", "what is my salary"]:
            filtered_df = pd.DataFrame([
                s for s in salaries if s[0].lower() == 'alice johnson (hr)'
            ], columns=["Name", "Title", "Department", "Salary"])
            if not filtered_df.empty:
                html_table = filtered_df.to_html(index=False, escape=False, border=0, classes="salary-table")
                html_table = html_table.replace('Olivia Zhang &#40;CTO&#41;', 'Olivia Zhang (CTO)').replace('Alice Johnson &#40;HR&#41;', 'Alice Johnson (HR)')
                return {"html_table": html_table, "provenance": 'payroll_confidential.txt'}
            else:
                return {"message": "No salary information found.", "provenance": 'payroll_confidential.txt'}
        # HR can see all HR salaries for department queries
        if re.search(r"hr salaries", query_lc) or re.search(r"list all hr salaries", query_lc):
            hr_salaries = [s for s in salaries if s[2] and s[2].strip().lower() == 'hr']
            filtered_df = pd.DataFrame(hr_salaries, columns=["Name", "Title", "Department", "Salary"])
            if not filtered_df.empty:
                html_table = filtered_df.to_html(index=False, escape=False, border=0, classes="salary-table")
                html_table = html_table.replace('Olivia Zhang &#40;CTO&#41;', 'Olivia Zhang (CTO)').replace('Alice Johnson &#40;HR&#41;', 'Alice Johnson (HR)')
                return {"html_table": html_table, "provenance": 'payroll_confidential.txt'}
            else:
                return {"message": "No salary information found.", "provenance": 'payroll_confidential.txt'}
    # CTO logic can be added here if needed
    return {"message": "No salary information found.", "provenance": None}
