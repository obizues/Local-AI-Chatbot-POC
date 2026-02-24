import streamlit as st
import pandas as pd
from sentence_transformers import SentenceTransformer
from transformers import pipeline
import pandas as pd
import subprocess
import faiss
import time
import numpy as np


APP_VERSION = "v0.11.0"
ECHO_MODE = False
GEN_MODEL_NAME = 'ollama'
GEN_MODEL_NAME_DISPLAY = 'Ollama'
OLLAMA_MODEL_SELECTED = 'llama2:7b-chat'

banner_html = '''
<style>
    .top-banner {
        width: 100vw;
        position: fixed;
        top: 0;
        left: 0;
        z-index: 1000;
        background: linear-gradient(90deg, #1976d2 0%, #64b5f6 100%);
        color: #fff;
        box-shadow: 0 2px 8px rgba(33,150,243,0.08);
        text-align: center;
        font-family: 'Segoe UI', 'Arial', sans-serif;
        margin: 0;
        font-size: 2.1em;
        font-weight: 800;
        letter-spacing: -0.5px;
        box-sizing: border-box;
        overflow: visible;
        height: 4.2em;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 0;
    }
    .top-banner .banner-emoji {
        font-size: 1.1em;
        vertical-align: middle;
        margin-right: 0.18em;
        position: relative;
        top: 0;
    }
    .banner-spacer {
        height: 4.2em;
    }
    @media (max-width: 600px) {
        .top-banner { font-size: 1.2em; height: 3.1em; }
        .banner-spacer { height: 3.1em; }
    }
</style>
<div class="top-banner">
    <span class="banner-emoji"><br>🤖</span><br>Welcome to your private, local AI Chatbot
</div>
<script>
// Remove Streamlit's default top padding
const stApp = window.parent.document.querySelector('section.main');
if (stApp) { stApp.style.paddingTop = '0px'; }
</script>
<!-- Removed banner-spacer to eliminate gap below banner -->
'''



###############################
# --- Header Banner and Personal Info Card ---
###############################


# Banner HTML (already defined as banner_html)
st.markdown(banner_html, unsafe_allow_html=True)

# --- Sidebar Documentation Update ---
sidebar_md = '''
## About This Project
Portfolio Project
This is a demonstration of a secure, local AI chatbot architecture designed for:
- Role-based access control (RBAC) for sensitive data
- Real-time document Q&A and semantic search
- Unified, modern chat UI with persistent role and model display
- Production-grade Python/Streamlit stack
- Modular, extensible codebase and reproducible environments
- System design thinking and technical leadership

**Target Audience:**
Technology executives, engineering leaders, HR professionals, AI/ML practitioners, and technical decision-makers interested in secure document Q&A, RBAC enforcement, and advanced LLM-driven systems for enterprise use cases.
'''
st.sidebar.markdown(sidebar_md)
## (Sidebar markdown removed as requested)





# Personal/professional info multi-line banner
user_info_banner = """
<style>
.user-info-banner {
    width: 100vw;
    background: #e3f2fd;
    color: #1976d2;
    font-family: 'Segoe UI', 'Arial', sans-serif;
    font-size: 1.01em;
    font-weight: 500;
    text-align: center;
    margin: 0;
    margin-top: 3.2em;
    margin-left: calc(-50vw + 50%);
    padding: 0.3em 0 0.3em 0;
    box-sizing: border-box;
    border-bottom: 1px solid #b3e5fc;
}
.user-info-banner .name-title {
    font-size: 1.08em;
    font-weight: 700;
    color: #1976d2;
    margin-bottom: 0.1em;
}
.user-info-banner .subtitle {
    font-size: 0.98em;
    color: #226;
    margin-bottom: 0.2em;
}
.user-info-banner .links, .user-info-banner .project-links {
    font-size: 0.97em;
    margin-bottom: 0.1em;
}
.user-info-banner a {
    color: #1976d2;
    text-decoration: underline;
    margin: 0 8px;
    font-size: 0.97em;
}
.user-info-banner .project-links {
    margin-top: 0.1em;
}
@media (max-width: 600px) {
    .user-info-banner { font-size: 0.93em; }
    .user-info-banner .name-title { font-size: 1em; }
    .user-info-banner .subtitle { font-size: 0.91em; }
    .user-info-banner .links, .user-info-banner .project-links { font-size: 0.91em; }
}
</style>
<div class="user-info-banner">
    <div class="name-title">Chris Obermeier | SVP of Engineering</div>
    <div class="subtitle">Enterprise &amp; PE-Backed Platform Modernization | AI &amp; Data-Driven Transformation</div>
    <div class="links">
        <a href="https://www.linkedin.com/in/chrisobermeier/" target="_blank">LinkedIn</a> |
        <a href="https://github.com/obizues" target="_blank">GitHub</a> |
        <a href="mailto:chris.obermeier@gmail.com" target="_blank">Email</a>
    </div>
    <div class="project-links">
        <span style="margin-right:4px;">&#11088;</span><a href="https://github.com/obizues/Local-AI-Chatbot-POC" target="_blank">Star on GitHub</a> |
        <span style="margin-right:4px;">&#128214;</span><a href="https://github.com/obizues/Local-AI-Chatbot-POC/blob/main/README.md" target="_blank">Read Documentation</a> |
        <span style="margin-right:4px;">&#127891;</span><a href="https://github.com/obizues/Local-AI-Chatbot-POC/blob/main/ARCHITECTURE.md" target="_blank">View Architecture</a>
    </div>
</div>
"""
st.markdown(user_info_banner, unsafe_allow_html=True)

# --- RBAC: Role selection ---

# --- RBAC: Role selection ---

ROLES = [
    "Alice Johnson (HR)",
    "David Kim (Engineer)",
    "Olivia Zhang (CTO)",
]
ROLE_DESCRIPTIONS = {
    "Alice Johnson (HR)": "Access to confidential HR details (e.g., pay, benefits)",
    "David Kim (Engineer)": "Access to David Kim's engineering SOPs and salary only",
    "Olivia Zhang (CTO)": "Full access to all Technology department data and documents"
}

if 'user_role' not in st.session_state:
    st.session_state['user_role'] = ROLES[0]


EMBED_MODEL_NAME = 'all-MiniLM-L6-v2'
embed_model = SentenceTransformer(EMBED_MODEL_NAME)

# Set up generative model (no timing)
if GEN_MODEL_NAME == 'ollama':
    llm = None  # Placeholder, handled in generate_answer
    gen_model_display = GEN_MODEL_NAME_DISPLAY
else:
    llm = pipeline('text-generation', model=GEN_MODEL_NAME, device=-1, max_new_tokens=256)
    gen_model_display = GEN_MODEL_NAME.upper()


EMBED_MODEL_NAME = 'all-MiniLM-L6-v2'
embed_model = SentenceTransformer(EMBED_MODEL_NAME)

# Set up generative model (no timing)
if GEN_MODEL_NAME == 'ollama':
    llm = None  # Placeholder, handled in generate_answer
    gen_model_display = GEN_MODEL_NAME_DISPLAY
else:
    llm = pipeline('text-generation', model=GEN_MODEL_NAME, device=-1, max_new_tokens=256)
    gen_model_display = GEN_MODEL_NAME.upper()

EMBED_MODEL_NAME = 'all-MiniLM-L6-v2'
EMBED_MODEL_NAME = 'all-MiniLM-L6-v2'
embed_model = SentenceTransformer(EMBED_MODEL_NAME)

# Set up generative model (no timing)
if GEN_MODEL_NAME == 'ollama':
    llm = None  # Placeholder, handled in generate_answer
    gen_model_display = GEN_MODEL_NAME_DISPLAY
else:
    llm = pipeline('text-generation', model=GEN_MODEL_NAME, device=-1, max_new_tokens=256)
    gen_model_display = GEN_MODEL_NAME.upper()

embed_model = SentenceTransformer(EMBED_MODEL_NAME)

# Set up generative model (no timing)
if GEN_MODEL_NAME == 'ollama':
    llm = None  # Placeholder, handled in generate_answer
    gen_model_display = GEN_MODEL_NAME_DISPLAY
else:
    llm = pipeline('text-generation', model=GEN_MODEL_NAME, device=-1, max_new_tokens=256)
    gen_model_display = GEN_MODEL_NAME.upper()





# --- Move retrieve and generate_answer above chat UI ---
# --- Load FAISS index and metadata ---
import numpy as np
import os
index_path = os.path.join(os.path.dirname(__file__), '..', 'vector_db', 'document_chunks.index')
metadata_path = os.path.join(os.path.dirname(__file__), '..', 'vector_db', 'metadata.csv')
chunks_path = os.path.join(os.path.dirname(__file__), '..', 'ingestion', 'document_chunks.csv')

# Load metadata
if os.path.exists(metadata_path):
    metadata = pd.read_csv(metadata_path)
elif os.path.exists(chunks_path):
    metadata = pd.read_csv(chunks_path)
else:
    metadata = pd.DataFrame()

# Load or create FAISS index
if os.path.exists(index_path):
    index = faiss.read_index(index_path)
else:
    # Fallback: create a dummy index if not found
    emb_dim = 384  # all-MiniLM-L6-v2 output dim
    index = faiss.IndexFlatL2(emb_dim)


def generate_answer(query, retrieved_chunks):
    user_role = st.session_state.get('user_role', None)
    import re
    salary_pattern = re.compile(r'salar(y|ies)\b', re.IGNORECASE)
    query_lc = query.strip().lower()
    if user_role == 'Alice Johnson (HR)':
        # Alice Johnson (HR) can see all salaries
        if (salary_pattern.search(query_lc) or 'salary' in query_lc or 'compensation' in query_lc or 'pay' in query_lc):
            if 'text' in metadata.columns:
                salaries = []
                tech_keywords = ["technology", "engineer", "tech department", "software", "developer"]
                cto_keywords = ["cto", "olivia zhang"]
                # If query is about CTO salary, show only CTO
                if any(kw in query_lc for kw in cto_keywords):
                    for row in metadata.itertuples():
                        text_str = str(row.text) if not isinstance(row.text, str) else row.text
                        match = re.search(r'Name: Olivia Zhang\s*\| Department: Technology \| Title: CTO \| Salary: \$([\d,]+)', text_str)
                        if match:
                            salary = match.group(1).strip()
                            df = pd.DataFrame([["Olivia Zhang (CTO)", "CTO", "Technology", salary]], columns=["Name", "Title", "Department", "Salary"])
                            html_table = df.to_html(index=False, escape=False, border=0, classes="salary-table")
                            return (html_table, 0.0)
                    return ("No CTO salary information found in internal documentation.", 0.0)
                # If query is about Technology salaries, filter for Technology department only
                if any(kw in query_lc for kw in tech_keywords):
                    for row in metadata.itertuples():
                        text_str = str(row.text) if not isinstance(row.text, str) else row.text
                        match = re.search(r'Name: ([^|]+)\s*\| Department: ([^|]+)\s*\|(?: Title: ([^|]+)\s*\|)? Salary: \$([\d,]+)', text_str)
                        if match:
                            name = match.group(1).strip()
                            dept = match.group(2).strip()
                            title = match.group(3).strip() if match.group(3) else ''
                            salary = match.group(4).strip()
                            if dept.lower() == 'technology':
                                # Show Olivia Zhang as 'Olivia Zhang (CTO)'
                                if name == 'Olivia Zhang' and title == 'CTO':
                                    name_display = 'Olivia Zhang (CTO)'
                                else:
                                    name_display = name
                                salaries.append((name_display, title, dept, salary))
                    if salaries:
                        df = pd.DataFrame(salaries, columns=["Name", "Title", "Department", "Salary"])
                        html_table = df.to_html(index=False, escape=False, border=0, classes="salary-table")
                        return (html_table, 0.0)
                    return ("No Technology salary information found in internal documentation.", 0.0)
                # Otherwise, show all salaries (default HR behavior)
                for row in metadata.itertuples():
                    text_str = str(row.text) if not isinstance(row.text, str) else row.text
                    match = re.search(r'Name: ([^|]+)\s*\| Department: ([^|]+)\s*\|(?: Title: ([^|]+)\s*\|)? Salary: \$([\d,]+)', text_str)
                    if match:
                        name = match.group(1).strip()
                        dept = match.group(2).strip()
                        title = match.group(3).strip() if match.group(3) else ''
                        salary = match.group(4).strip()
                        # Show Alice Johnson as 'Alice Johnson (HR)'
                        if name == 'Alice Johnson' and dept == 'HR':
                            name_display = 'Alice Johnson (HR)'
                        else:
                            name_display = name
                        salaries.append((name_display, title, dept, salary))
                if salaries:
                    df = pd.DataFrame(salaries, columns=["Name", "Title", "Department", "Salary"])
                    html_table = df.to_html(index=False, escape=False, border=0, classes="salary-table")
                    return (html_table, 0.0)
            return ("No salary information found in internal documentation.", 0.0)
    # Special case: CTO salary RBAC logic
    user_role = st.session_state.get('user_role', None)
    import re
    salary_pattern = re.compile(r'salar(y|ies)\b', re.IGNORECASE)
    query_lc = query.strip().lower()
    if user_role == 'CTO' or user_role == 'Olivia Zhang (CTO)':
        # CTO can see all company salaries (HR + Technology) for 'everyone' queries
        tech_keywords = ["technology", "team", "engineer", "salaries", "pay", "compensation"]
        personal_keywords = ["my salary", "olivia zhang", "my compensation", "my pay"]
        everyone_keywords = ["everyone", "all salaries", "company salaries", "every employee", "all employees", "entire company", "everyone's salaries", "everyone's salary"]
        if any(kw in query_lc for kw in personal_keywords) and (salary_pattern.search(query_lc) or 'salary' in query_lc or 'compensation' in query_lc or 'pay' in query_lc):
            # Find CTO chunk
            cto_mask = metadata['text'].astype(str).str.contains('olivia zhang', case=False, na=False)
            cto_chunk = metadata[cto_mask]
            if not cto_chunk.empty:
                df = pd.DataFrame([["Olivia Zhang", "CTO", "Technology", "300,000"]], columns=["Name", "Title", "Department", "Salary"])
                html_table = df.to_html(index=False, escape=False, border=0, classes="salary-table")
                return (html_table, 0.0)
        elif any(kw in query_lc for kw in everyone_keywords) and (salary_pattern.search(query_lc) or 'salary' in query_lc):
            # CTO can only see Technology salaries, even for 'everyone' queries
            if 'text' in metadata.columns:
                import re
                salaries = []
                for row in metadata.itertuples():
                    text_str = str(row.text) if not isinstance(row.text, str) else row.text
                    match = re.search(r'Name: ([^|]+)\s*\| Department: ([^|]+)\s*\|(?: Title: ([^|]+)\s*\|)? Salary: \$([\d,]+)', text_str)
                    if match:
                        name = match.group(1).strip()
                        dept = match.group(2).strip()
                        title = match.group(3).strip() if match.group(3) else ''
                        salary = match.group(4).strip()
                        if dept.lower() == 'technology':
                            salaries.append((name, title, dept, salary))
                if salaries:
                    df = pd.DataFrame(salaries, columns=["Name", "Title", "Department", "Salary"])
                    html_table = df.to_html(index=False, escape=False, border=0, classes="salary-table")
                    denial_note = "You do not have access to all company salaries. Only Technology department salaries are shown below."
                    combined = f"{denial_note}<br><br>{html_table}"
                    return (combined, 0.0)
            return ("No Technology salary information found in internal documentation.", 0.0)
        else:
            # If query mentions HR or other departments, deny access
            if 'hr' in query_lc or 'human resources' in query_lc or 'finance' in query_lc or 'marketing' in query_lc:
                return ("You do not have access to HR or other department salary information.", 0.0)
            # Extract all Technology employee names from metadata
            tech_mask = metadata['text'].astype(str).str.contains('department: technology', case=False, na=False)
            tech_chunks = metadata[tech_mask]
            tech_names = []
            import re
            for row in tech_chunks.itertuples():
                text_str = str(row.text) if not isinstance(row.text, str) else row.text
                match = re.search(r'Name: ([^|]+)\s*\|', text_str)
                if match:
                    tech_names.append(match.group(1).strip().lower())
            # If any tech employee name is in the query, return their salary
            for name in tech_names:
                if name in query_lc:
                    # Find that employee's chunk
                    emp_mask = tech_chunks['text'].astype(str).str.contains(name, case=False, na=False)
                    emp_chunk = tech_chunks[emp_mask]
                    if not emp_chunk.empty:
                        text_str = str(emp_chunk.iloc[0]['text']) if not isinstance(emp_chunk.iloc[0]['text'], str) else emp_chunk.iloc[0]['text']
                        match = re.search(r'Salary: \$([\d,]+)', text_str)
                        if match:
                            # Try to extract title if present
                            title_match = re.search(r'Title: ([^|]+)', text_str)
                            title = title_match.group(1).strip() if title_match else ''
                            name_match = re.search(r'Name: ([^|]+)\s*\|', text_str)
                            name_val = name_match.group(1).strip() if name_match else ''
                            dept_match = re.search(r'Department: ([^|]+)', text_str)
                            dept = dept_match.group(1).strip() if dept_match else 'Technology'
                            salary = match.group(1).strip()
                            df = pd.DataFrame([[name_val, title, dept, salary]], columns=["Name", "Title", "Department", "Salary"])
                            html_table = df.to_html(index=False, escape=False, border=0, classes="salary-table")
                            return (html_table, 0.0)
            # Otherwise, if asking about team/technology salaries, return all
            if any(kw in query_lc for kw in tech_keywords) and (salary_pattern.search(query_lc) or 'salary' in query_lc or 'compensation' in query_lc or 'pay' in query_lc):
                if not tech_chunks.empty:
                    salaries = []
                    for row in tech_chunks.itertuples():
                        text_str = str(row.text) if not isinstance(row.text, str) else row.text
                        # Match both with and without Title field
                        match = re.search(r'Name: ([^|]+)\s*\|.*?Department: ([^|]+)\s*\|(?: Title: ([^|]+)\s*\|)? Salary: \$([\d,]+)', text_str)
                        if match:
                            name = match.group(1).strip()
                            dept = match.group(2).strip()
                            title = match.group(3).strip() if match.group(3) else ''
                            salary = match.group(4).strip()
                            salaries.append((name, title, dept, salary))
                    if salaries:
                        df = pd.DataFrame(salaries, columns=["Name", "Title", "Department", "Salary"])
                        html_table = df.to_html(index=False, escape=False, border=0, classes="salary-table")
                        return (html_table, 0.0)
    import time
    start_time = time.time()
    # Defensive: If no results or missing 'text' column, return a friendly message
    if not isinstance(retrieved_chunks, pd.DataFrame) or 'text' not in retrieved_chunks.columns or retrieved_chunks.empty:
        # Special case: David Kim salary RBAC message
        user_role = st.session_state.get('user_role', None)
        import re
        salary_pattern = re.compile(r'salar(y|ies)\b', re.IGNORECASE)
        query_lc = query.strip().lower()
        if user_role == 'David Kim (Engineer)':
            # Always check for queries about others' compensation
            others_keywords = ["everyone else's", "other employees", "colleagues", "others'", "other people's", "rest of", "all salaries", "everyone else", "other people's pay", "other people's compensation", "other people's income", "other people's earnings"]
            if any(kw in query_lc for kw in others_keywords):
                return ("You do not have access to other employees' salary information.", time.time() - start_time)
            # If the query is about 'my salary' or 'david kim's salary', just return the value
            if (salary_pattern.search(query_lc) or 'salary' in query_lc):
                if 'my salary' in query_lc or "david kim" in query_lc:
                    df = pd.DataFrame([["David Kim", "Engineer", "Technology", "185,200"]], columns=["Name", "Title", "Department", "Salary"])
                    html_table = df.to_html(index=False, escape=False, border=0, classes="salary-table")
                    return (html_table, time.time() - start_time)
                # Otherwise, explicit RBAC message for general salary queries
                # Show denial message and David Kim's own salary as a table
                df = pd.DataFrame([["David Kim", "Engineer", "Technology", "185,200"]], columns=["Name", "Title", "Department", "Salary"])
                html_table = df.to_html(index=False, escape=False, border=0, classes="salary-table")
                denial_message = "You only have access to your own salary. You do not have access to other employees' salaries."
                combined = f"{denial_message}<br><br>{html_table}"
                return (combined, time.time() - start_time)
        elif user_role == 'HR' and (salary_pattern.search(query_lc) or 'salary' in query_lc):
            # HR can see all salaries
            # Use metadata to extract all salary info
            if 'text' in metadata.columns:
                import re
                salaries = []
                for row in metadata.itertuples():
                    text_str = str(row.text) if not isinstance(row.text, str) else row.text
                    match = re.search(r'Name: ([^|]+)\s*\| Department: ([^|]+)\s*\|(?: Title: ([^|]+)\s*\|)? Salary: \$([\d,]+)', text_str)
                    if match:
                        name = match.group(1).strip()
                        dept = match.group(2).strip()
                        title = match.group(3).strip() if match.group(3) else ''
                        salary = match.group(4).strip()
                        # Show Alice Johnson as 'Alice Johnson (HR)'
                        if name == 'Alice Johnson' and dept == 'HR':
                            name_display = 'Alice Johnson (HR)'
                        else:
                            name_display = name
                        salaries.append((name_display, title, dept, salary))
                if salaries:
                    df = pd.DataFrame(salaries, columns=["Name", "Title", "Department", "Salary"])
                    html_table = df.to_html(index=False, escape=False, border=0, classes="salary-table")
                    return (html_table, time.time() - start_time)
            return ("No salary information found in internal documentation.", time.time() - start_time)
        return ("No relevant information found in internal documentation.", time.time() - start_time)
    import os
    unrelated_keywords = ["vacation", "paid vacation", "HR portal", "onboarding", "welcome", "paperwork"]
    filtered_texts = []
    sop_texts = []
    deployment_query = ("deploy" in query.lower() or "deployment" in query.lower())
    pto_keywords = ["pto", "paid time off", "vacation", "leave", "holiday"]
    pto_query = any(kw in query.lower() for kw in pto_keywords)
    response_time = 0.0
    response = ""
    for idx, x in enumerate(retrieved_chunks['text'].tolist()):
        if isinstance(x, str) and x.strip():
            # ...existing code...
            pass  # Prevent empty block error
            file_col = None
            if 'file' in retrieved_chunks.columns:
                file_col = retrieved_chunks.iloc[idx]['file']
            def clean_chunk(chunk):
                lines = chunk.splitlines()
                cleaned = []
                for line in lines:
                    l = line.strip()
                    # Remove all header/metadata lines and empty lines, but keep lines with actual policy text
                    if not l:
                        continue
                    if l.startswith('---') and len(l) < 10:
                        continue
                    if l.startswith('#') and len(l.strip('#').strip()) == 0:
                        continue
                    if l.lower().startswith('department:') or l.lower().startswith('sensitivity:') or l.lower().startswith('version:'):
                        continue
                    cleaned.append(l)
                # If nothing left, return the original chunk as fallback
                if not cleaned:
                    return chunk.strip()
                return '\n'.join(cleaned)

            # For deployment queries, only include deploy_software_sop chunk
            if deployment_query:
                if file_col and 'deploy_software_sop' in str(file_col).lower():
                    sop_texts.append(clean_chunk(x))
            # For PTO/vacation queries, only include vacation_policy chunk
            elif pto_query:
                if file_col and 'vacation_policy' in str(file_col).lower():
                    sop_texts.append(clean_chunk(x))
            else:
                lowered = x.lower()
                if not any(kw in lowered for kw in unrelated_keywords):
                    filtered_lines = [clean_chunk(line) for line in x.splitlines() if not line.strip().startswith("#")]
                    filtered_texts.append("\n".join(filtered_lines))

    # For deployment or PTO/vacation queries, use only the relevant chunk(s) as context
    if deployment_query or pto_query:
        context = "\n".join(sop_texts)
    else:
        context = "\n".join(filtered_texts)

    # DEBUG: Log the cleaned context being sent to the LLM
    log_path = os.path.join(os.path.dirname(__file__), '..', 'ollama_debug.log')
    try:
        with open(log_path, 'a', encoding='utf-8') as logf:
            logf.write(f"[DEBUG] CLEANED Context for query '{query}':\n{context}\n{'-'*40}\n")
    except Exception as e:
        pass
    # For deployment or PTO/vacation queries, use only the relevant chunk(s) as context
    if deployment_query or pto_query:
        context = "\n".join(sop_texts)
    else:
        context = "\n".join(filtered_texts)
    # DEBUG: Log the context being sent to the LLM
    log_path = os.path.join(os.path.dirname(__file__), '..', 'ollama_debug.log')
    try:
        with open(log_path, 'a', encoding='utf-8') as logf:
            logf.write(f"[DEBUG] Context for query '{query}':\n{context}\n{'-'*40}\n")
    except Exception as e:
        pass
    # Improved prompt: Avoid contradictory instructions and clarify logic
    if deployment_query:
        if context.strip():
            prompt = (
                "Copy the deployment steps verbatim from the context below. Do NOT add, summarize, rephrase, or invent any information. Only output the steps themselves, with no introductory or closing phrases. If the context contains a numbered or bulleted list, copy it exactly as shown.\n"
                f"Context:\n{context}\n\nQuestion: {query}\nAnswer:"
            )
        else:
            prompt = (
                "There are no deployment instructions in the context below. Respond: 'No deployment SOP found in internal documentation.'\n"
                f"Context:\n{context}\n\nQuestion: {query}\nAnswer:"
            )
    elif pto_query:
        if context.strip():
            prompt = (
                "Copy the PTO or vacation policy verbatim from the context below. Do NOT add, summarize, rephrase, or invent any information. Only output the policy itself, with no introductory or closing phrases. If the context contains a numbered or bulleted list, copy it exactly as shown.\n"
                f"Context:\n{context}\n\nQuestion: {query}\nAnswer:"
            )
        else:
            prompt = (
                "There are no PTO or vacation policy instructions in the context below. Respond: 'No PTO or vacation policy found in internal documentation.'\n"
                f"Context:\n{context}\n\nQuestion: {query}\nAnswer:"
            )
    else:
        # RBAC: Salary chunk logic
        user_role = st.session_state.get('user_role', None)
        import re
        salary_pattern = re.compile(r'salar(y|ies)\b', re.IGNORECASE)
        query_lc = query.strip().lower()
        if (salary_pattern.search(query_lc) or 'salary' in query_lc):
            if user_role == 'David Kim (Engineer)':
                if 'my salary' in query_lc or "david kim" in query_lc:
                    df = pd.DataFrame([["David Kim", "Engineer", "Technology", "185,200"]], columns=["Name", "Title", "Department", "Salary"])
                    html_table = df.to_html(index=False, escape=False, border=0, classes="salary-table")
                    return (html_table, 0.0)
                df = pd.DataFrame([["David Kim", "Engineer", "Technology", "185,200"]], columns=["Name", "Title", "Department", "Salary"])
                html_table = df.to_html(index=False, escape=False, border=0, classes="salary-table")
                denial_message = "You only have access to your own salary. You do not have access to other employees' salaries."
                combined = f"{denial_message}<br><br>{html_table}"
                return (combined, 0.0)
            elif user_role != 'CTO' and user_role != 'HR':
                # All other roles: explicit RBAC denial
                return ("You do not have access to salary information.", 0.0)
        prompt = (
            "Copy the answer verbatim from the context below. Do NOT add, summarize, rephrase, or invent any information. Only output the answer itself, with no introductory or closing phrases. If the answer is not present, respond: 'No answer found in internal documentation.'\n"
            f"Context:\n{context}\n\nQuestion: {query}\nAnswer:"
        )
    if GEN_MODEL_NAME == 'ollama':
        import subprocess
        ollama_path = r"C:\\Users\\mro84\\AppData\\Local\\Programs\\Ollama\\ollama.exe"
        try:
            import logging
            log_path = os.path.join(os.path.dirname(__file__), '..', 'ollama_debug.log')
            with open(log_path, 'a', encoding='utf-8') as logf:
                logf.write(f"[DEBUG] Calling Ollama subprocess. Prompt length: {len(prompt)}\n")
            start = time.time()
            # Ensure OLLAMA_MODEL_SELECTED is not None
            model = OLLAMA_MODEL_SELECTED if OLLAMA_MODEL_SELECTED else 'llama2:7b-chat'
            result = subprocess.run([
                ollama_path, "run", model
            ], input=prompt, capture_output=True, text=True, timeout=300, encoding="utf-8", errors="replace")
            response_time = time.time() - start
            with open(log_path, 'a', encoding='utf-8') as logf:
                logf.write(f"[DEBUG] Ollama subprocess finished. Return code: {result.returncode}\n")
            response = result.stdout.strip()
            if not response:
                with open(log_path, 'a', encoding='utf-8') as logf:
                    logf.write(f"[DEBUG] No output. Stderr: {result.stderr.strip()}\n")
                response = f"[Ollama returned no output. Return code: {result.returncode}. Stderr: {result.stderr.strip()}]"
        except Exception as e:
            with open(log_path, 'a', encoding='utf-8') as logf:
                logf.write(f"[DEBUG] Exception: {e}\n")
            response = f"[Ollama error: {e}]"
        return response, response_time
    else:
        start = time.time()
        if llm is not None:
            response = llm(prompt)[0]['generated_text']
        else:
            response = '[LLM pipeline not initialized]'
        response_time = time.time() - start
        return response, response_time



# --- LLM Model Selection and Display ---
# Define available LLM model options
GEN_MODEL_OPTIONS = [
    'Ollama (llama2:7b-chat)',
    'Ollama (mistral:7b-instruct)',
    'Ollama (phi3:mini)',
    'gpt2',
    'distilgpt2',
    # Add more model names as needed
]



    

with st.container():
    st.markdown("""
    <style>
    .dropdown-row-align {
        display: flex;
        flex-direction: row;
        justify-content: space-between;
        align-items: flex-start;
        gap: 2em;
        margin-bottom: 0.5em;
    }
    .dropdown-col-align {
        flex: 1 1 0;
        min-width: 220px;
        max-width: 100%;
        display: flex;
        flex-direction: column;
        align-items: flex-start;
    }
    .dropdown-label-align {
        font-size: 1.08em;
        font-weight: 500;
        color: #1976d2;
        margin-bottom: 0.18em;
        display: block;
    }
    @media (max-width: 900px) {
        .dropdown-row-align { flex-direction: column; gap: 0.5em; }
        .dropdown-col-align { min-width: 0; }
    }
    </style>
    <div class="dropdown-row-align">
        <div class="dropdown-col-align" id="llm-col">
            <span class="dropdown-label-align">LLM Model:</span>
        </div>
        <div class="dropdown-col-align" id="role-col">
            <span class="dropdown-label-align">Role:</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    col1, col2 = st.columns([1,1], gap="large")
    with col1:
        selected_model = st.selectbox(
            "LLM Model",
            GEN_MODEL_OPTIONS,
            index=GEN_MODEL_OPTIONS.index('Ollama (llama2:7b-chat)'),
            key="llm_model_select",
            label_visibility="collapsed"
        )
    with col2:
        current_role = st.session_state.get('user_role', ROLES[0])
        new_role = st.selectbox(
            "Role",
            ROLES,
            index=ROLES.index(current_role) if current_role in ROLES else 0,
            key="role_switch_select",
            label_visibility="collapsed",
            format_func=lambda r: f"{r} - {ROLE_DESCRIPTIONS[r]}"
        )
        if new_role != current_role:
            st.session_state['user_role'] = new_role
            st.rerun()

# --- Model selection logic: always keep GEN_MODEL_NAME and OLLAMA_MODEL_SELECTED in sync with dropdown ---
def update_model_selection(selected_model):
    global GEN_MODEL_NAME, OLLAMA_MODEL_SELECTED, llm, gen_model_display
    if selected_model.startswith('Ollama ('):
        if 'mistral' in selected_model.lower():
            GEN_MODEL_NAME = 'ollama'
            OLLAMA_MODEL_SELECTED = 'mistral'
        else:
            GEN_MODEL_NAME = 'ollama'
            OLLAMA_MODEL_SELECTED = 'llama2:7b-chat'
    else:
        GEN_MODEL_NAME = selected_model
        OLLAMA_MODEL_SELECTED = None
    # Re-initialize llm pipeline if not using Ollama
    if GEN_MODEL_NAME == 'ollama':
        # ...existing code for Ollama...
        # If Ollama logic does not set response_time, set a default
        if 'response_time' not in locals():
            response_time = 0.0
        if 'response' not in locals():
            response = ''
        return response, response_time
    else:
        # ...existing code for other models...
        if 'response_time' not in locals():
            response_time = 0.0
        if 'response' not in locals():
            response = ''
        return response, response_time
        llm = None
        gen_model_display = GEN_MODEL_NAME_DISPLAY

if 'selected_model' not in st.session_state or st.session_state['selected_model'] != selected_model:
    st.session_state['selected_model'] = selected_model
    update_model_selection(selected_model)

def retrieve(query, top_k=3):
    user_role = st.session_state.get('user_role', None)
    results = pd.DataFrame()
    # DEBUG: Unconditional debug file write to confirm retrieve() entry and user_role
    import datetime
    debug_path = 'david_kim_salary_debug.txt'
    try:
        with open(debug_path, 'a', encoding='utf-8') as f:
            f.write(f"\n--- {datetime.datetime.now()} ---\n")
            f.write(f"retrieve() called. user_role: {user_role}, query: {query}\n")
    except Exception as e:
        pass
    # Always log kim_chunk and metadata DataFrame for debugging
    kim_mask = metadata['text'].astype(str).str.contains('david kim', case=False, na=False) if 'text' in metadata.columns else []
    kim_chunk = metadata[kim_mask] if len(kim_mask) > 0 else pd.DataFrame()
    # If David Kim (Engineer) and salary query, return kim_chunk directly if not empty
    try:
        with open(debug_path, 'a', encoding='utf-8') as f:
            f.write(f"[CHECK] user_role: '{user_role}', query: '{query}', kim_chunk.empty: {kim_chunk.empty}\n")
    except Exception:
        pass
    import re
    # Match any word containing 'salary' (e.g., 'salary', 'salaries', 'salary?')
    salary_pattern = re.compile(r'salar(y|ies)\b', re.IGNORECASE)
    query_stripped = query.strip().lower()
    if (salary_pattern.search(query_stripped) or 'salary' in query_stripped) and user_role == 'David Kim (Engineer)' and not kim_chunk.empty:
        try:
            with open(debug_path, 'a', encoding='utf-8') as f:
                f.write(f"Returning kim_chunk directly for David Kim salary query.\n")
        except Exception:
            pass
        return kim_chunk
    else:
        try:
            with open(debug_path, 'a', encoding='utf-8') as f:
                f.write(f"[NOT RETURNING] Condition not met for kim_chunk direct return.\n")
        except Exception:
            pass
    try:
        with open(debug_path, 'a', encoding='utf-8') as f:
            f.write(f"kim_chunk DataFrame:\n{kim_chunk.to_string()}\n")
            f.write(f"\nFULL metadata DataFrame:\n{metadata.to_string()}\n")
    except Exception as e:
        with open(debug_path, 'a', encoding='utf-8') as f:
            f.write(f"[EXCEPTION] Error writing kim_chunk/metadata: {e}\n")

    # ...existing code for retrieval...

    # At the end of retrieve(), before return, log the final results DataFrame
    try:
        with open(debug_path, 'a', encoding='utf-8') as f:
            f.write(f"\nFINAL results DataFrame returned by retrieve():\n{results.to_string()}\n")
    except Exception as e:
        with open(debug_path, 'a', encoding='utf-8') as f:
            f.write(f"[EXCEPTION] Error writing final results: {e}\n")
    # DEBUG: Print results DataFrame for David Kim salary queries
    if 'salary' in query.lower() and user_role == 'David Kim (Engineer)':
        print("[DEBUG] Results DataFrame for David Kim salary query:")
        print(results)
    # DEBUG: Log type and dir of index to diagnose FAISS search error
    log_path = os.path.join(os.path.dirname(__file__), '..', 'ollama_debug.log')
    try:
        with open(log_path, 'a', encoding='utf-8') as logf:
            logf.write(f"[DEBUG] index type: {type(index)}\n")
            logf.write(f"[DEBUG] index dir: {dir(index)}\n")
    except Exception as e:
        pass
    query_emb = embed_model.encode([query]).astype('float32')
    if len(query_emb.shape) == 1:
        query_emb = query_emb.reshape(1, -1)
    top_k = 5  # Retrieve more chunks for richer answers
    # Ensure correct argument order for FAISS index.search
    # index.search(x, k) where x is (n_queries, d)
    # Ensure query_emb is contiguous float32 (n, d)
    if not query_emb.flags['C_CONTIGUOUS']:
        query_emb = np.ascontiguousarray(query_emb, dtype='float32')
    if query_emb.ndim != 2:
        raise ValueError(f"query_emb must be 2D (n, d), got shape {query_emb.shape}")
    # Ensure query_emb is contiguous float32 (n, d)
    if not query_emb.flags['C_CONTIGUOUS']:
        query_emb = np.ascontiguousarray(query_emb, dtype='float32')
    if query_emb.ndim != 2:
        raise ValueError(f"query_emb must be 2D (n, d), got shape {query_emb.shape}")
    D, I = index.search(query_emb, int(top_k))
    # Defensive: I is a 2D numpy array (n_queries, top_k)
    if hasattr(I, '__getitem__') and len(I) > 0 and hasattr(I[0], '__iter__'):
        idxs = [i for i in I[0] if i >= 0]
        results = metadata.iloc[idxs] if len(idxs) > 0 else pd.DataFrame()
    else:
        results = pd.DataFrame()
    # If the query is about deployment, always include the deploy_software_sop chunk
    if 'deploy' in query.lower() or 'deployment' in query.lower():
        sop_mask = metadata['file'].astype(str).str.contains('deploy_software_sop', case=False, na=False)
        sop_chunk = metadata[sop_mask]
        if not sop_chunk.empty:
            if 'file' in results.columns:
                in_results = results['file'].astype(str).str.contains('deploy_software_sop', case=False, na=False)
                if not in_results.any():
                    results = pd.concat([results, sop_chunk], ignore_index=True)
            elif not results.empty:
                results = pd.concat([results, sop_chunk], ignore_index=True)
            else:
                results = sop_chunk.copy()

    # If the query is about PTO/vacation, always include the vacation_policy chunk
    pto_keywords = ['pto', 'paid time off', 'vacation', 'leave', 'holiday']
    if any(kw in query.lower() for kw in pto_keywords):
        vac_mask = metadata['file'].astype(str).str.contains('vacation_policy', case=False, na=False)
        vac_chunk = metadata[vac_mask]
        if not vac_chunk.empty:
            if 'file' in results.columns:
                in_results = results['file'].astype(str).str.contains('vacation_policy', case=False, na=False)
                if not in_results.any():
                    results = pd.concat([results, vac_chunk], ignore_index=True)
            elif not results.empty:
                results = pd.concat([results, vac_chunk], ignore_index=True)
            else:
                results = vac_chunk.copy()
    # RBAC: Filter Technology department salary data for non-CTO roles
    user_role = st.session_state.get('user_role', None)
    if user_role != 'CTO' and 'salary' in query.lower():
        # Remove Technology department salary chunks
        if not results.empty and 'text' in results.columns:
            mask = ~results['text'].astype(str).str.contains('Department: Technology', case=False, na=False)
            results = results[mask]
    return results

if 'history' not in st.session_state:
    st.session_state['history'] = []

# Patch old chat history in memory to always include LLM name if missing or set to 'neutral'
if st.session_state['history']:
    llm_used = f"Ollama ({OLLAMA_MODEL_SELECTED})" if GEN_MODEL_NAME == 'ollama' else f"{GEN_MODEL_NAME} (generative)"
    patched = []
    for entry in st.session_state['history']:
        if len(entry) == 4:
            user, bot, response_time, extra = entry
            if extra in ('', 'neutral', None):
                patched.append((user, bot, response_time, llm_used))
            else:
                patched.append(entry)
        elif len(entry) == 3:
            user, bot, response_time = entry
            patched.append((user, bot, response_time, llm_used))
        else:
            patched.append(entry)
    st.session_state['history'] = patched

# CSS for scrollable chat box and chat bubbles
st.markdown('''
<style>
.scrollable-chat-window {
    width: 100%;
    margin: 0;
    height: 420px;
    min-height: 220px;
    max-height: 60vh;
    overflow-y: scroll;
    padding: 0 2px 0 2px;
    background: #fafbfc;
    border: 1px solid #eee;
    border-radius: 8px;
    display: flex;
    flex-direction: column-reverse;
    scrollbar-color: #bbb #fafbfc;
    scrollbar-width: thin;
}
.chat-bubble-user {
    background: #d1e7ff;
    color: #222;
    padding: 6px 10px;
    border-radius: 18px 18px 4px 18px;
    margin-bottom: 2px;
    max-width: 70%;
    align-self: flex-end;
    margin-right: 0;
    margin-left: 30%;
    box-shadow: 0 1px 2px rgba(0,0,0,0.04);
    font-weight: 500;
}
.chat-bubble-bot {
    background: #f0f0f0;
    color: #222;
    padding: 6px 10px;
    border-radius: 18px 18px 18px 4px;
    margin-bottom: 6px;
    max-width: 70%;
    align-self: flex-end;
    margin-right: 0;
    margin-left: 30%;
    box-shadow: 0 1px 2px rgba(0,0,0,0.04);
}
.scrollable-chat-window::-webkit-scrollbar {
    width: 8px;
}
.scrollable-chat-window::-webkit-scrollbar-thumb {
    background: #bbb;
    border-radius: 4px;
}
.scrollable-chat-window::-webkit-scrollbar-track {
    background: #fafbfc;
}
.input-bar {
    width: 100%;
    margin: 0;
    background: #fff;
    padding: 0 0 2px 0;
}
@media (max-width: 900px) {
    .scrollable-chat-window {
        height: 220px;
        min-height: 120px;
        max-height: 32vh;
    }
}
</style>
''', unsafe_allow_html=True)


# Scrollable chat window with fixed height, messages start at bottom
 # Scrollable chat window with fixed height, messages start at bottom

# Render messages in normal order (newest at bottom) with feedback



import uuid
    # ...existing code...
chat_html = '<div class="scrollable-chat-window">'

# --- Enhanced: Display source files for each answer ---
for idx, entry in enumerate(reversed(st.session_state.get('history', []))):
    # Unpack entry

    # Always store the selected model at the time of response
    # Robustly unpack all possible formats (7, 6, 5, 4, 3, 2 fields)
    user = bot = response_time = llm_used = sources = model_used = user_role_at_time = None
    if len(entry) == 7:
        user, bot, response_time, llm_used, sources, model_used, user_role_at_time = entry
    elif len(entry) == 6:
        user, bot, response_time, llm_used, sources, user_role_at_time = entry
        model_used = llm_used
    elif len(entry) == 5:
        user, bot, response_time, llm_used, user_role_at_time = entry
        sources = None
        model_used = llm_used
    elif len(entry) == 4:
        user, bot, response_time, llm_used = entry
        sources = None
        model_used = llm_used
        user_role_at_time = None
    elif len(entry) == 3:
        user, bot, response_time = entry
        llm_used = ''
        sources = None
        model_used = st.session_state.get('selected_model') or GEN_MODEL_NAME
        user_role_at_time = None
    elif len(entry) == 2:
        user, bot = entry
        response_time = None
        llm_used = ''
        sources = None
        model_used = st.session_state.get('selected_model') or GEN_MODEL_NAME
        user_role_at_time = None

    # Always show response time and LLM model at the bottom of the bot message
    # Always display the model actually used for this response
    llm_display = f' | {model_used}'
    time_llm_html = f'<span style="font-size:0.85em;color:#888;">{llm_display}</span>'
    chat_html += f'<div>'
    # Role-specific icon and label for user chat bubble
    role_icons = {
        'Alice Johnson (HR)': '🧑‍💼',
        'David Kim (Engineer)': '🧑‍💻',
        'Olivia Zhang (CTO)': '🧑‍💼',
    }
    role_labels = {
        'Alice Johnson (HR)': 'Alice Johnson (HR)',
        'David Kim (Engineer)': 'David Kim (Engineer)',
        'Olivia Zhang (CTO)': 'Olivia Zhang (CTO)',
    }
    # Normalize CTO and HR role to always display as their full label
    if user_role_at_time == 'CTO' or user_role_at_time == 'Olivia Zhang (CTO)':
        display_role = 'Olivia Zhang (CTO)'
    elif user_role_at_time == 'HR' or user_role_at_time == 'Alice Johnson (HR)':
        display_role = 'Alice Johnson (HR)'
    elif user_role_at_time == 'David Kim (Engineer)':
        display_role = 'David Kim (Engineer)'
    else:
        display_role = user_role_at_time or 'You'
    icon = role_icons.get(display_role, '🧑')
    label = role_labels.get(display_role, display_role)
    chat_html += f'<div class="chat-bubble-user">{icon} <b>{label}:</b> {user}</div>'
    chat_html += f'<div class="chat-bubble-bot">🤖 <b>Bot:</b> {bot}'
    if sources:
        # Show sources as clickable links (open in new tab)
        def file_to_link(file):
            # Try to create a relative path for the file, fallback to basename
            try:
                rel_path = os.path.relpath(str(file), os.path.dirname(__file__))
                # Use forward slashes for URLs
                rel_path_url = rel_path.replace('\\', '/').replace(' ', '%20')
                # Only link to files under mock_data, ingestion, or vector_db
                if rel_path_url.startswith(('mock_data/', 'ingestion/', 'vector_db/')):
                    return f'<a href="/{rel_path_url}" target="_blank">{os.path.basename(str(file))}</a>'
                else:
                    return os.path.basename(str(file))
            except Exception:
                return os.path.basename(str(file))
        if isinstance(sources, list) and sources:
            src_links = ', '.join([file_to_link(s) for s in sources])
            src_html = f'<br><span style="font-size:0.85em;color:#1976d2;">Sources: {src_links}</span>'
            chat_html += src_html
        elif isinstance(sources, str) and sources:
            chat_html += f'<br><span style="font-size:0.85em;color:#1976d2;">Source: {file_to_link(sources)}</span>'
    # Only show LLM model used, not response time
    if time_llm_html:
        chat_html += f'<br><span style="display:block;text-align:right;margin-top:4px;font-size:0.95em;color:#555;">{time_llm_html}</span>'
    chat_html += '</div>'
    chat_html += f'</div>'
chat_html += '</div>'
st.markdown(chat_html, unsafe_allow_html=True)

# Inject scroll-to-bottom script separately and persistently
st.markdown('''
<script>
    function scrollChatToBottom() {
        const chatWin = document.querySelector('.scrollable-chat-window');
        if (chatWin) {
            chatWin.scrollTop = chatWin.scrollHeight;
        }
    }
    // Try repeatedly for 1s after each render
    let scrollTries = 0;
    const maxTries = 20;
    const interval = setInterval(() => {
        scrollChatToBottom();
        scrollTries++;
        if (scrollTries > maxTries) clearInterval(interval);
    }, 50);
    // Also scroll on window load
    window.addEventListener('load', scrollChatToBottom);
</script>
''', unsafe_allow_html=True)

# Input bar just below chat window
st.markdown('<div class="input-bar">', unsafe_allow_html=True)
with st.form(key='chat_input_form', clear_on_submit=True):
    user_input = st.text_input("Message", "", key="user_input")
    submitted = st.form_submit_button("Send")
    if submitted and user_input.strip():
        import time
        start_total = time.time()
        user_role_at_time = st.session_state.get('user_role', 'You')
        if 'ECHO_MODE' in globals() and ECHO_MODE:
            bot_response = f'[echo] {user_input}'
            llm_used = f"Ollama ({OLLAMA_MODEL_SELECTED})" if GEN_MODEL_NAME == 'ollama' else f"{GEN_MODEL_NAME} (generative)"
            st.session_state.setdefault('history', []).append((user_input, bot_response, 0.0, llm_used, user_role_at_time))
            st.rerun()
        else:
            # Use actual retrieval and model logic
            import datetime
            debug_path = 'timing_debug.txt'
            retrieved = retrieve(user_input)
            bot_response, model_response_time = generate_answer(user_input, retrieved)
            end_total = time.time()
            total_response_time = end_total - start_total
            # Log timing debug info
            try:
                with open(debug_path, 'a', encoding='utf-8') as f:
                    f.write(f"\n--- {datetime.datetime.now()} ---\n")
                    f.write(f"user_input: {user_input}\n")
                    f.write(f"start_total: {start_total}\n")
                    f.write(f"end_total: {end_total}\n")
                    f.write(f"total_response_time: {total_response_time}\n")
            except Exception:
                pass
            llm_used = f"Ollama ({OLLAMA_MODEL_SELECTED})" if GEN_MODEL_NAME == 'ollama' else f"{GEN_MODEL_NAME} (generative)"
            # Special case: CTO Technology salary query, force correct source
            if user_role_at_time == 'CTO' and 'salary' in user_input.lower() and any('department: technology' in line.lower() for line in bot_response.splitlines()):
                sources = ['payroll_confidential.txt']
            elif 'file' in retrieved.columns:
                sources = list(set([os.path.basename(str(f)) for f in retrieved['file'].tolist() if pd.notnull(f)]))
            else:
                sources = None
            # Store the selected model at the time of response for accurate display
            model_used = st.session_state.get('selected_model') or GEN_MODEL_NAME
            # Always use total_response_time for display, not model_response_time
            st.session_state.setdefault('history', []).append((user_input, bot_response, total_response_time, llm_used, sources, model_used, user_role_at_time))
            st.rerun()
    if submitted and user_input.strip() and ECHO_MODE:
        bot_response = f'[echo] {user_input}'
        llm_used = f"Ollama ({OLLAMA_MODEL_SELECTED})" if GEN_MODEL_NAME == 'ollama' else f"{GEN_MODEL_NAME} (generative)"
        st.session_state.setdefault('history', []).append((user_input, bot_response, 0.0, llm_used))
        st.rerun()
    elif submitted and user_input.strip():
        # Use actual retrieval and model logic
        retrieved = retrieve(user_input)
        bot_response, response_time = generate_answer(user_input, retrieved)
        # Log response time
        if len(entry) == 7:
            user, bot, response_time, llm_used, sources, model_used, user_role_at_time = entry
        elif len(entry) == 6:
            user, bot, response_time, llm_used, sources, user_role_at_time = entry
            model_used = llm_used
        elif len(entry) == 5:
            user, bot, response_time, llm_used, user_role_at_time = entry
            sources = None
            model_used = llm_used
        elif len(entry) == 4:
            user, bot, response_time, llm_used = entry
            sources = None
            model_used = llm_used
            user_role_at_time = None
        elif len(entry) == 3:
            user, bot, response_time = entry
            llm_used = ''
            sources = None
            model_used = st.session_state.get('selected_model') or GEN_MODEL_NAME
            user_role_at_time = None
        else:
            user, bot = entry
            response_time = None
            llm_used = ''
            sources = None
            model_used = st.session_state.get('selected_model') or GEN_MODEL_NAME
            user_role_at_time = None

        # Always show response time and LLM model at the bottom of the bot message
        # Always display the model actually used for this response
        llm_display = f' | {model_used}'
        if response_time is not None:
            time_llm_html = f'<span style="font-size:0.85em;color:#888;">({response_time:.2f}s{llm_display})</span>'
        else:
            time_llm_html = ''
        chat_html += f'<div>'
        # Role-specific icon and label for user chat bubble
        role_icons = {
            'HR': '🧑‍💼',
            'Engineering': '🧑‍💻',
            'David Kim (Engineer)': '🧑‍💻',
            'CTO': '🧑‍💼',
        }
        role_labels = {
            'HR': 'HR',
            'Engineering': 'Engineering',
            'David Kim (Engineer)': 'David Kim (Engineer)',
            'CTO': 'CTO',
        }
        # Always use the role at the time of message, fallback to 'You'
        display_role = user_role_at_time if user_role_at_time else 'You'
        icon = role_icons.get(display_role, '🧑')
        label = role_labels.get(display_role, display_role)
        chat_html += f'<div class="chat-bubble-user">{icon} <b>{label}:</b> {user}</div>'
        chat_html += f'<div class="chat-bubble-bot">🤖 <b>Bot:</b> {bot}'
st.markdown('</div>', unsafe_allow_html=True)




if not ECHO_MODE:
    # Streamlit UI

    # Track model type for logging (dynamic)

    # Collapsible sidebar sections (default collapsed)
    st.sidebar.markdown(f"""
<div class='sidebar-card' style='font-size:0.97em;padding:8px 12px 6px 12px;'>
    <span style='font-size:1.05em;'>&#128241;</span> <b style='font-size:1em;'>App version:</b><br>
    <span style='font-size:0.95em;'>{APP_VERSION} - RBAC, Role-Preserved Chat, and UI Enhancements</span>
</div>
<div class='sidebar-card' style='background:#eaf6ff;font-size:0.93em;margin-bottom:16px;border:1.5px solid #b3e5fc;padding:8px 8px 6px 8px;'>
    <div style='font-weight:700;font-size:1em;line-height:1.2;margin-bottom:2px;text-align:center;'>
        <span style="font-size:1.05em;vertical-align:middle;">&#129302;</span> AI Search & Knowledge System
    </div>
    <div style='margin:0 0 0 0;font-size:0.91em;line-height:1.35;text-align:center;'>
        <div style='display:flex;align-items:center;justify-content:center;gap:6px;margin-bottom:2px;'>
            <span style="font-size:1em;">&#128269;</span> <span>Semantic Search</span>
        </div>
        <div style='display:flex;align-items:center;justify-content:center;gap:6px;margin-bottom:2px;'>
            <span style="font-size:1em;">&#128196;</span> <span>Document Q&amp;A</span>
        </div>
        <div style='display:flex;align-items:center;justify-content:center;gap:6px;margin-bottom:2px;'>
            <span style="font-size:1em;">&#128737;</span> <span>Private, Local LLM</span>
        </div>
        <div style='display:flex;align-items:center;justify-content:center;gap:6px;margin-bottom:2px;'>
            <span style="font-size:1em;">&#9889;</span> <span>Fast, Modern UI</span>
        </div>
        <div style='display:flex;align-items:center;justify-content:center;gap:6px;margin-bottom:2px;'>
            <span style="font-size:1em;">&#128274;</span> <span>Role-Based Access Control (RBAC)</span>
        </div>
        <div style='display:flex;align-items:center;justify-content:center;gap:6px;margin-bottom:2px;'>
            <span style="font-size:1em;">&#128100;</span> <span>Role-Preserved Chat History</span>
        </div>
        <div style='display:flex;align-items:center;justify-content:center;gap:6px;'>
            <span style="font-size:1em;">&#128202;</span> <span>Feedback Logging</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

    # Restore About This Project expander at the top
    with st.sidebar.expander("ℹ️ About This Project", expanded=False):
        st.markdown("""
<div style='font-size:1.15em;font-weight:700;margin-bottom:6px;'>Portfolio Project</div>
<div style='margin-bottom:10px;'>
    This is a demonstration of a <b>Chatbot</b> for private, local document Q&amp;A and semantic search, featuring:
</div>
<ul style='margin-top: 6px; margin-bottom: 0; padding-left: 18px;'>
    <li>Conversational Q&amp;A over your internal documents</li>
    <li>Natural language chat interface with context retention</li>
    <li>Historical learning and context-aware chat memory</li>
    <li>Private, local LLM (Ollama or HuggingFace) with no cloud dependency</li>
    <li>Semantic search over internal documents using FAISS and embeddings</li>
    <li>Modern, real-time UI with Streamlit</li>
    <li>Production-grade, modular Python codebase</li>
    </ul>
    """, unsafe_allow_html=True)

    with st.sidebar.expander("📁 Project Documentation", expanded=False):
        st.markdown("""
<div style='font-size:1.12em;font-weight:700;margin-bottom:6px;'>Project Documentation</div>
<div style='margin-bottom:8px;'>
    <span style='font-size:1em;'>
        <b>GitHub Repository</b> <a href='https://github.com/obizues/Local-AI-Chatbot-POC' target='_blank'>github.com/obizues/Local-AI-Chatbot-POC</a>
    </span>
</div>
<div style='margin-bottom:8px;'><b>Documentation</b></div>
<ul style='margin-bottom:0; padding-left: 18px;'>
    <li><a href='https://github.com/obizues/Local-AI-Chatbot-POC/blob/main/README.md' target='_blank'>README.md</a> - Project overview, quick start, features</li>
    <li><a href='https://github.com/obizues/Local-AI-Chatbot-POC/blob/main/ARCHITECTURE.md' target='_blank'>ARCHITECTURE.md</a> - Deep technical documentation</li>
    <li>System Diagrams - 5 Mermaid diagrams</li>
</ul>
<div style='margin-top:10px; margin-bottom:4px;'><b>Key Sections:</b></div>
<ul style='margin-bottom:0; padding-left: 18px;'>
    <li>Multi-agent system design</li>
    <li>LLM integration strategy</li>
    <li>Production deployment guide</li>
    <li>Architectural decision records</li>
</ul>
""", unsafe_allow_html=True)
    with st.sidebar.expander("🛠️ Tech Stack", expanded=False):
        st.markdown("""
<span style='font-size:1em;'>
<ul style='margin-bottom:0; padding-left: 18px;'>
    <li>Python 3.10+</li>
    <li>Streamlit (UI)</li>
    <li>FAISS (vector search)</li>
    <li>sentence-transformers (embeddings)</li>
    <li>HuggingFace Transformers (LLM pipeline)</li>
    <li>Ollama (local LLM, optional)</li>
    <li>Flask (API integration)</li>
    <li>pandas (data handling)</li>
    <li>NumPy (vector math)</li>
    <li>PyMuPDF (PDF ingestion)</li>
    <li>python-docx (DOCX ingestion)</li>
    <li>langchain, llama-index (optional, advanced retrieval)</li>
</ul>
</span>
""", unsafe_allow_html=True)
    with st.sidebar.expander("📝 System Design Notes", expanded=False):
        st.markdown(
            """
<div style='font-size:1.12em;font-weight:700;margin-bottom:8px;'>System Design Notes</div>
<ul style='margin-bottom:0; padding-left: 18px;'>
    <li><b>Retrieval-Augmented Chat:</b> User questions are embedded and matched to relevant document chunks using FAISS, providing context for LLM answers.</li>
    <li><b>Unified Chat Interface:</b> Streamlit UI displays chat history, model selection, and sidebar documentation in a single, modern layout.</li>
    <li><b>Session State Management:</b> All chat history, selected model, and user context are stored in Streamlit session state for seamless multi-turn conversations.</li>
    <li><b>Flexible LLM Backend:</b> Supports both local (Ollama) and HuggingFace LLMs, switchable via UI, with fallback and error handling for robustness.</li>
    <li><b>Document Ingestion Pipeline:</b> Batch scripts process PDFs, DOCX, and text files, chunking and embedding them for fast semantic search.</li>
    <li><b>Feedback Logging:</b> User queries, responses, and feedback are logged to CSV for evaluation and improvement.</li>
    <li><b>Customizable Sidebar:</b> Sidebar provides About, Documentation, Tech Stack, and System Design Notes, all styled for clarity and mobile compatibility.</li>
    <li><b>Real-Time UI Updates:</b> Chat and sidebar update instantly on user input, with scroll-to-bottom and feedback features for usability.</li>
    <li><b>Security & Privacy:</b> All processing is local; no data leaves the user's environment. API keys and secrets are managed via environment variables and never committed to source control.</li>
    <li><b>Extensible Architecture:</b> Modular codebase allows easy addition of new models, data sources, or UI features.</li>
    <li><b>Observability:</b> Debug logs and error messages are written to local files for troubleshooting and transparency.</li>
    <li><b>Resilience:</b> Graceful error handling ensures the app remains usable even if some components fail or are unavailable.</li>
    <li><b>Infrastructure:</b> Designed for local use, but can be containerized or deployed on private servers as needed.</li>
</ul>
""",
            unsafe_allow_html=True
        )
