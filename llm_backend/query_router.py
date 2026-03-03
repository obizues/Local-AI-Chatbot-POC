# All imports at the top
import os
import re
import pandas as pd
from llm_backend.benefits_service import get_benefits_text
from llm_backend.salary_access import get_salary_rows

def detect_salary_intent(user_input):
    """Return 'my' if user asks for their own salary, 'all' if for all, else None."""
    q = user_input.lower()
    if 'my salary' in q or 'show my salary' in q or 'what is my salary' in q:
        return 'my'
    if 'all salaries' in q or 'everyone' in q or 'show all salaries' in q:
        return 'all'
    return None

def get_department_from_role(user_role):
    """Map user_role to department string."""
    # Add more mappings as needed
    if 'HR' in user_role or 'CPO' in user_role or user_role.strip() == 'Alice Johnson':
        return 'HR'
    if 'Technology' in user_role or 'CTO' in user_role or 'Engineer' in user_role or user_role.strip() == 'David Kim':
        return 'Technology'
    return None

def route_query(user_input, user_role, metadata):
    import time
    start_time = time.time()
    # Deploy software SOP logic
    step1 = time.time()
    if re.search(r'deploy software|deploy.*sop|how to deploy', user_input, re.IGNORECASE):
        # Only allow users with 'Engineer' in their title/role
        if 'engineer' in user_role.lower():
            sop_path = os.path.join(os.path.dirname(__file__), '../mock_data/Technology/deploy_software_sop.md')
            try:
                with open(sop_path, 'r', encoding='utf-8') as f:
                    return f.read(), 'mock_data/Technology/deploy_software_sop.md'
            except Exception as e:
                return '<div style="color:#b71c1c;font-weight:bold;font-size:1.1em;">SOP not found.</div>', None
        else:
            # Log denied SOP access
            import datetime
            log_path = os.environ.get('ACCESS_AUDIT_LOG')
            if not log_path:
                log_path = os.path.join(os.path.dirname(__file__), '../access_audit.log')
            # Ensure the audit log file exists before writing
            try:
                os.makedirs(os.path.dirname(log_path), exist_ok=True)
                if not os.path.exists(log_path):
                    with open(log_path, 'w', encoding='utf-8') as _:
                        pass
            except Exception as e:
                print(f"[AccessAudit] Failed to create audit log file: {e}", flush=True)
            now = datetime.datetime.now().isoformat()
            attempted = f"user_input='{user_input}'"
            log_line = f"{now}\t{user_role}\t{attempted}\n"
            try:
                with open(log_path, 'a', encoding='utf-8') as logf:
                    logf.write(log_line)
            except Exception as e:
                print(f"[AccessAudit] Failed to log SOP access denial: {e}", flush=True)
            return '<div style="color:#b71c1c;font-weight:bold;font-size:1.1em;">You do not have a need to access this.</div>', None
    # Onboarding guide logic
    if re.search(r'onboarding', user_input, re.IGNORECASE):
        step2 = time.time()
        dept = get_department_from_role(user_role)
        if dept == 'HR':
            onboarding_path = os.path.join(os.path.dirname(__file__), '../mock_data/HR/hr_onboarding.md')
            with open(onboarding_path, 'r', encoding='utf-8') as f:
                return f.read(), 'mock_data/HR/hr_onboarding.md'
        elif dept == 'Technology':
            onboarding_path = os.path.join(os.path.dirname(__file__), '../mock_data/Technology/technology_onboarding.md')
            with open(onboarding_path, 'r', encoding='utf-8') as f:
                return f.read(), 'mock_data/Technology/technology_onboarding.md'
        else:
            return 'Onboarding guide is only available to HR or Technology department members.', None

    """
    Route the user query to the appropriate service (salary or benefits).
    Returns (response_text, provenance)
    """
    # Debug: print user_input and branch
    print(f"DEBUG: route_query received user_input='{user_input}' user_role='{user_role}'", flush=True)
    if re.search(r'benefit', user_input, re.IGNORECASE):
        print("DEBUG: Detected benefits query", flush=True)
        return get_benefits_text(), 'mock_data/HR/benefits_overview.txt'
    print("DEBUG: Detected salary query", flush=True)
    step3 = time.time()
    # Otherwise, treat as salary query
    # Extract salaries from metadata
    salaries = []
    if isinstance(metadata, pd.DataFrame) and 'text' in metadata.columns:
        for row in metadata.itertuples():
            text_str = str(row.text) if not isinstance(row.text, str) else row.text
            match = re.search(r'Name:\s*([^|]+)\s*\|\s*Department:\s*([^|]+)(?:\s*\|\s*Title:\s*([^|]+))?\s*\|\s*Salary:\s*\$([\d,]+)', text_str)
            if match:
                name = match.group(1).strip()
                dept = match.group(2).strip()
                title = match.group(3).strip() if match.group(3) else ''
                salary = match.group(4).strip()
                salaries.append((name, title, dept, salary))
    step4 = time.time()
    # Defensive: if salaries is empty and metadata has columns Name, Title, Department, Salary, extract directly
    if not salaries and isinstance(metadata, pd.DataFrame):
        cols = [c.lower() for c in metadata.columns]
        if all(x in cols for x in ['name', 'department', 'salary']):
            title_col = 'Title' if 'Title' in metadata.columns else None
            for row in metadata.itertuples(index=False):
                name = getattr(row, 'Name', '')
                dept = getattr(row, 'Department', '')
                title = getattr(row, 'Title', '') if title_col else ''
                salary = getattr(row, 'Salary', '')
                salaries.append((name, title, dept, salary))
    step5 = time.time()
    # Salary intent logic
    intent = detect_salary_intent(user_input)
    dept = get_department_from_role(user_role)
    if intent == 'my':
        # Only show user's own salary, regardless of department or role
        name = user_role.split(' (')[0].strip().lower()
        visible_rows = [row for row in salaries if row[0].strip().lower() == name]
    elif intent == 'all' and dept == 'HR':
        # HR can see all salaries
        visible_rows = salaries
    elif intent == 'all' and dept == 'Technology' and ('CTO' in user_role or 'Chief Technology Officer' in user_role):
        # CTO can see all Technology salaries
        visible_rows = [row for row in salaries if row[2].strip().lower() == 'technology']
    elif intent == 'all':
        # All others denied
        visible_rows = []
    else:
        # Check if user is asking for another person's salary
        # Try to extract a name from the user_input
        name_match = re.search(r'salary for ([A-Za-z ]+)', user_input, re.IGNORECASE)
        if name_match:
            requested_name = name_match.group(1).strip().lower()
            user_name = user_role.split(' (')[0].strip().lower()
            if requested_name != user_name:
                visible_rows = []  # Deny access to others' salaries
            else:
                visible_rows = [row for row in salaries if row[0].strip().lower() == user_name]
        else:
            # Default RBAC logic
            visible_rows = get_salary_rows(user_role, salaries)
    if visible_rows:
        df = pd.DataFrame(visible_rows, columns=["Name", "Title", "Department", "Salary"])
        df = df.astype(str)  # Convert all columns to string to avoid Arrow LargeUtf8 errors
        response = df.to_html(index=False, escape=False, border=0, classes="salary-table")
        provenance = 'mock_data/HR/payroll_confidential.txt'
        end_time = time.time()
        # Defensive: ensure all timing variables exist before printing
        timing_vars = locals()
        for var in ["step1", "step2", "step3", "step4", "step5"]:
            if var not in timing_vars:
                timing_vars[var] = start_time
        print(f"TIMING: route_query total={end_time-start_time:.3f}s, step1={timing_vars['step1']-start_time:.3f}s, step2={timing_vars['step2']-timing_vars['step1']:.3f}s, step3={timing_vars['step3']-timing_vars['step2']:.3f}s, step4={timing_vars['step4']-timing_vars['step3']:.3f}s, step5={timing_vars['step5']-timing_vars['step4']:.3f}s, df_html={end_time-timing_vars['step5']:.3f}s", flush=True)
    else:
        # Access denied: log and show bold red message
        import datetime
        log_path = os.environ.get('ACCESS_AUDIT_LOG')
        if not log_path:
            log_path = os.path.join(os.path.dirname(__file__), '../access_audit.log')
        # Ensure the audit log file exists before writing
        try:
            os.makedirs(os.path.dirname(log_path), exist_ok=True)
            if not os.path.exists(log_path):
                with open(log_path, 'w', encoding='utf-8') as _:
                    pass
        except Exception as e:
            print(f"[AccessAudit] Failed to create audit log file: {e}", flush=True)
        now = datetime.datetime.now().isoformat()
        attempted = f"user_input='{user_input}'"
        log_line = f"{now}\t{user_role}\t{attempted}\n"
        try:
            with open(log_path, 'a', encoding='utf-8') as logf:
                logf.write(log_line)
        except Exception as e:
            print(f"[AccessAudit] Failed to log access denial: {e}", flush=True)
        response = '<div style="color:#b71c1c;font-weight:bold;font-size:1.1em;">You do not have access to the requested salary information.</div>'
        provenance = 'mock_data/HR/payroll_confidential.txt'
    return response, provenance