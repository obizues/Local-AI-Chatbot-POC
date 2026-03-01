"""
CTO HR salary access logic for the chatbot.
Extracted from ui/app.py for testability and maintainability.
"""
def check_cto_hr_salary_access(user_role, query):
    """
    Returns a dict:
      - denied: True/False
      - message: denial message if denied
    """
    query_lc = query.strip().lower()
    if user_role != 'Olivia Zhang (CTO)':
        return {"denied": False}
    hr_salary_keywords = [
        "hr's salaries", "hr salaries", "hr salary", "human resources salaries", "human resources salary", "hr's salary", "hr department salary", "hr department salaries"
    ]
    for kw in hr_salary_keywords:
        if kw in query_lc:
            return {"denied": True, "message": "<div style='color: #d9534f; font-weight: bold; margin-bottom: 0.5em'>Unauthorized access attempt detected. This action has been logged.</div>"}
    return {"denied": False}
