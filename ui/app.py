import sys
import os
# Ensure project root is in sys.path for imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import streamlit as st
from llm_backend.model_service import load_llm_pipeline
import os
import pandas as pd
import re
import time
import difflib

# --- Persistent Query Log Utilities ---
LOG_CSV_PATH = os.path.join(os.path.dirname(__file__), '..', 'query_logs.csv')

def load_query_logs():
    if os.path.exists(LOG_CSV_PATH):
        import csv
        with open(LOG_CSV_PATH, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            return list(reader)
    else:
        return []

def append_query_log(log_entry):
    import csv
    file_exists = os.path.exists(LOG_CSV_PATH)
    with open(LOG_CSV_PATH, 'a', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['timestamp', 'user', 'query', 'response', 'denial'])
        if not file_exists:
            writer.writeheader()
        entry = log_entry.copy()
        entry['denial'] = str(entry['denial'])
        writer.writerow(entry)

# --- Retroactively flag denial logs in query_logs.csv ---
import csv
csv_path = LOG_CSV_PATH
if os.path.exists(csv_path):
    denial_keywords = [
        'unauthorized', 'denied', 'forbidden', 'not allowed', 'access denied',
        'you do not have access', "you don't have access", 'permission denied', 'insufficient permissions', 'color:red'
    ]
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = list(csv.DictReader(f))
    for log in reader:
        resp = str(log.get('response', '')).lower()
        log['denial'] = str(any(kw in resp for kw in denial_keywords))
    with open(csv_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['timestamp', 'user', 'query', 'response', 'denial'])
        writer.writeheader()
        writer.writerows(reader)


# --- Initialize persistent query logs in session state ---
if 'query_logs' not in st.session_state:
    logs = load_query_logs()
    st.session_state['query_logs'] = logs if logs is not None else []
# --- Initialize denial filter state in session state ---
if 'show_only_denials' not in st.session_state:
    st.session_state['show_only_denials'] = False
import pandas as pd
import faiss
import re
import time
 # print("DEBUG: Starting import of sentence_transformers and transformers", flush=True)

import streamlit as st

# Use Streamlit cache for expensive imports
@st.cache_resource(show_spinner=False)
def get_sentence_transformer():
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer('all-MiniLM-L6-v2')

@st.cache_resource(show_spinner=False)
def get_transformers_pipeline(model_name):
    from transformers import pipeline
    return pipeline('text-generation', model=model_name)
print("DEBUG: Finished import of sentence_transformers and transformers", flush=True)


# Placeholder variable definitions (replace with actual logic as needed)
GEN_MODEL_NAME = 'gpt2'
GEN_MODEL_NAME_DISPLAY = 'GPT-2'
ECHO_MODE = False
salary_pattern = re.compile(r"\$[0-9,]+")





# Global fuzzy_any function for fuzzy matching
def fuzzy_any(targets, query_lc, cutoff=0.7):
    for t in targets:
        if difflib.SequenceMatcher(None, t, query_lc).ratio() >= cutoff:
            return True
        words = query_lc.split()
        for w in words:
            if difflib.SequenceMatcher(None, t, w).ratio() >= cutoff:
                return True
    return False

def write_audit_log(message):
    with open('access_audit.log', 'a', encoding='utf-8') as audit_log:
        audit_log.write(message)


# --- Top blue app title bar (centered, above personal info) ---
st.markdown(
    """
    <style>
        .main-title-banner {
            background: #1976d2;
            color: #fff;
            font-size: 1.45em;
            font-weight: 700;
            text-align: center;
            margin: 0 auto 0 auto;
            padding: 0.7em 0 0.7em 0;
            box-sizing: border-box;
            border-radius: 0 0 18px 18px;
            box-shadow: 0 2px 8px rgba(25, 118, 210, 0.10);
            letter-spacing: 0.01em;
            max-width: 1100px;
        }
        .main-title-banner .emoji {
            font-size: 1.3em;
            vertical-align: middle;
            margin-right: 0.18em;
            filter: none;
        }
    </style>
    <div class="main-title-banner">
        <span class="emoji">🤖</span> Local AI Governance Platform
    </div>
    """
    , unsafe_allow_html=True
)

app_title_banner = """
<style>
.app-title-banner {
    background: #f5f5f5;
    color: #222;
    font-family: 'Segoe UI', 'Arial', sans-serif;
    font-size: 1.08em;
    font-weight: 500;
    text-align: center;
    margin: 0.5em auto 0 auto;
    padding: 0.5em 0 0.5em 0;
    box-sizing: border-box;
    border-radius: 0 0 12px 12px;
    box-shadow: 0 2px 8px rgba(25, 118, 210, 0.08);
    max-width: 1100px;
}
.app-title-banner .name-title {
    font-size: 1.18em;
    font-weight: 700;
    color: #1976d2;
    margin-bottom: 0.1em;
}
.app-title-banner .subtitle {
    font-size: 0.98em;
    color: #1976d2;
    margin-bottom: 0.2em;
}
.app-title-banner .links, .app-title-banner .project-links {
    font-size: 0.97em;
    margin-bottom: 0.1em;
}
.app-title-banner a {
    color: #1976d2;
    text-decoration: underline;
    margin: 0 8px;
    font-size: 0.97em;
}
.app-title-banner .project-links {
    margin-top: 0.1em;
}
    @media (max-width: 1100px) {
        .app-title-banner { font-size: 0.93em; }
        .app-title-banner .name-title { font-size: 1em; }
        .app-title-banner .subtitle { font-size: 0.91em; }
        .app-title-banner .links, .app-title-banner .project-links { font-size: 0.91em; }
    }
</style>

<div class="app-title-banner">
    <div class="name-title" style="font-size:0.95em; font-weight:400; margin-bottom:0.08em; text-align:center; color:#1976d2;"><b>Chris Obermeier</b> | SVP of Engineering</div>
    <div class="subtitle" style="background:transparent;border-radius:0;padding:2px 8px;font-size:0.83em;text-align:center;margin-bottom:0.08em;color:#64b5f6;font-weight:400;">Enterprise Platform & AI Transformation | Led 100+ Engineer Orgs | PE & Revenue-Scale Modernization</div>
    <div class="links" style="font-size:0.92em; font-weight:400; margin-bottom:0em; text-align:center;">
        <a href="https://www.linkedin.com/in/chris-obermeier/" target="_blank">LinkedIn</a> |
        <a href="https://github.com/obizues" target="_blank">GitHub</a> |
        <a href="mailto:chris.obermeier@gmail.com" target="_blank">Email</a>
    </div>
    <div class="project-links" style="font-size:0.92em; font-weight:400; margin-top:0em; text-align:center;">
        <span style="margin-right:4px;">&#11088;</span><a href="https://github.com/obizues/Local-AI-Chatbot-POC" target="_blank">Star on GitHub</a> |
        <span style="margin-right:4px;">&#128214;</span><a href="https://github.com/obizues/Local-AI-Chatbot-POC/blob/main/README.md" target="_blank">Read Documentation</a> |
        <span style="margin-right:4px;">&#127891;</span><a href="https://github.com/obizues/Local-AI-Chatbot-POC/blob/main/ARCHITECTURE.md" target="_blank">View Architecture</a>
    </div>
</div>
"""
st.markdown(app_title_banner, unsafe_allow_html=True)

##Additional spacing after title banner
st.markdown("<br>", unsafe_allow_html=True)

# --- RBAC: Role selection ---
ROLES = [
    "Alice Johnson (CPO)",
    "David Kim (Engineer)",
    "Olivia Zhang (CTO)",
]
ROLE_DESCRIPTIONS = {
    "Alice Johnson (CPO)": "Access to confidential HR details (e.g., pay, benefits)",
    "David Kim (Engineer)": "Access to David Kim's engineering SOPs and salary only",
    "Olivia Zhang (CTO)": "Full access to all Technology department data and documents"
}

if 'user_role' not in st.session_state:
    st.session_state['user_role'] = ROLES[0]

# --- Model caching using Streamlit's cache_resource ---
# Preload metadata and warm up cache at app startup
from llm_backend.model_service import load_metadata

# ...existing code...

EMBED_MODEL_NAME = 'all-MiniLM-L6-v2'


# Only load metadata once per session
def load_metadata_once(metadata_path, chunks_path):
    import pandas as pd
    import os
    if os.path.exists(metadata_path):
        abs_path = os.path.abspath(metadata_path)
        print(f"DEBUG: ABSOLUTE metadata_path: {abs_path}", flush=True)
        temp_df = pd.read_csv(abs_path)
        # Clean up: drop fully empty rows and duplicates
        temp_df = temp_df.dropna(how='all')
        temp_df = temp_df.drop_duplicates()
        print(f"DEBUG: metadata.csv shape after clean: {temp_df.shape}", flush=True)
        print(f"DEBUG: metadata.csv head after clean:\n{temp_df.head(10)}", flush=True)
        return temp_df
    elif os.path.exists(chunks_path):
        print(f"DEBUG: metadata_path missing, loading chunks_path: {chunks_path}", flush=True)
        temp_df = pd.read_csv(chunks_path)
        temp_df = temp_df.dropna(how='all')
        temp_df = temp_df.drop_duplicates()
        print(f"DEBUG: chunks_path shape after clean: {temp_df.shape}", flush=True)
        print(f"DEBUG: chunks_path head after clean:\n{temp_df.head(10)}", flush=True)
        return temp_df
    else:
        print(f"DEBUG: neither metadata_path nor chunks_path found, using empty DataFrame", flush=True)
        return pd.DataFrame()

index_path = os.path.join(os.path.dirname(__file__), '..', 'vector_db', 'document_chunks.index')
metadata_path = os.path.join(os.path.dirname(__file__), '..', 'vector_db', 'metadata.csv')
chunks_path = os.path.join(os.path.dirname(__file__), '..', 'ingestion', 'document_chunks.csv')

if 'metadata' not in st.session_state:
    st.session_state['metadata'] = load_metadata_once(metadata_path, chunks_path)
metadata = st.session_state['metadata']

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

col1, col2 = st.columns([1,1], gap="large")
with col1:
    st.markdown('<span class="dropdown-label-align">LLM Model:</span>', unsafe_allow_html=True)
    selected_model = st.selectbox(
        "LLM Model",
        GEN_MODEL_OPTIONS,
        index=GEN_MODEL_OPTIONS.index('Ollama (llama2:7b-chat)'),
        key="llm_model_select",
        label_visibility="collapsed"
    )
with col2:
    st.markdown('<span class="dropdown-label-align">Role:</span>', unsafe_allow_html=True)
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


# Map dropdown display names to valid HuggingFace model names
MODEL_NAME_MAP = {
    'Ollama (llama2:7b-chat)': 'ollama',
    'Ollama (mistral:7b-instruct)': 'ollama',
    'Ollama (phi3:mini)': 'ollama',
    'gpt2': 'gpt2',
    'distilgpt2': 'distilgpt2',
}

# When the user changes the model in the dropdown, reload the pipeline and update session state
model_name = MODEL_NAME_MAP.get(selected_model, 'gpt2')
if 'selected_model' not in st.session_state or st.session_state['selected_model'] != selected_model or st.session_state.get('last_model_name') != model_name:
    st.session_state['selected_model'] = selected_model
    st.session_state['llm'], st.session_state['gen_model_display'] = load_llm_pipeline(model_name)
    st.session_state['last_model_name'] = model_name


if 'history' not in st.session_state:
    st.session_state['history'] = []

# Patch old chat history in memory to always include LLM name if missing or set to 'neutral'


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
@media (max-width: 1300px) {
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
            # Ensure provenance is always set for all salary queries, including fallback and direct lookups
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
    chat_html += f'<div class="chat-bubble-bot">&#129302; <b>Chatbot:</b> {bot}'
    # Show source file for onboarding answers
    # Only show sources if not None, not empty, and not a denial/warning message
    if sources and sources not in [None, '', [], 'None'] and not (isinstance(bot, str) and 'Unauthorized access attempt' in bot):
        def file_to_link(file):
            try:
                rel_path = os.path.relpath(str(file), os.path.dirname(__file__))
                rel_path_url = rel_path.replace('\\', '/').replace(' ', '%20')
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

st.markdown('<div class="input-bar">', unsafe_allow_html=True)
chat_html = '<div class="scrollable-chat-window">'
message_sent = False  # Ensure variable is always defined
with st.form(key='chat_input_form', clear_on_submit=True):
    user_input = st.text_input("Message", "", key="user_input")
    submitted = st.form_submit_button("Send")
    if submitted and user_input.strip():
        user_role = st.session_state.get('user_role', 'You')
        metadata = st.session_state.get('metadata', pd.DataFrame())
        bot_response = ''
        provenance = None
        model_used = st.session_state.get('selected_model', GEN_MODEL_NAME)
        response_time = None
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        from llm_backend.query_router import route_query
        bot_response, provenance = route_query(user_input, user_role, metadata)
        # Improved denial detection
        denial_keywords = [
            'unauthorized', 'denied', 'forbidden', 'not allowed', 'access denied',
            'you do not have access', "you don't have access", 'permission denied', 'insufficient permissions', 'color:red'
        ]
        is_denial = False
        if isinstance(bot_response, str):
            bot_response_lc = bot_response.lower()
            is_denial = any(kw in bot_response_lc for kw in denial_keywords)
        log_entry = {
            'timestamp': timestamp,
            'user': user_role,
            'query': user_input,
            'response': bot_response,
            'denial': is_denial
        }
        if 'query_logs' not in st.session_state:
            st.session_state['query_logs'] = []
        st.session_state['query_logs'].append(log_entry)
        append_query_log(log_entry)
        st.session_state.setdefault('history', []).append((user_input, bot_response, response_time, model_used, provenance, model_used, user_role))
        message_sent = True
if message_sent:
    st.experimental_rerun()

# Audit log dropdown below message input
with st.expander('Query Log Viewer', expanded=False):
    st.markdown('**Audit Trail:** All queries and responses are logged below. Use the filter to show only denial logs.')
    show_only_denials = st.checkbox('Show only denial logs', value=st.session_state['show_only_denials'], key='show_only_denials')
    logs_to_display = st.session_state['query_logs']
    if st.session_state['show_only_denials']:
        logs_to_display = [log for log in logs_to_display if log.get('denial', False) is True or str(log.get('denial', '')).strip().lower() == 'true']
    if logs_to_display:
        import pandas as pd
        df = pd.DataFrame(logs_to_display)
        def highlight_denials(row):
            color = 'background-color: #ffcccc; color: #b71c1c;' if str(row['denial']).lower() == 'true' else ''
            return [color] * len(row)
        st.dataframe(df.style.apply(highlight_denials, axis=1))
    else:
        st.info('No logs to display for the selected filter.')

# Always render sidebar (do not gate on ECHO_MODE)
# Collapsible sidebar sections (default collapsed)
st.sidebar.markdown("""
<div style='background:#eaf6ff;border:1.5px solid #b3e5fc;padding:10px 12px 8px 12px;margin-bottom:12px;text-align:center;border-radius:8px;'>
    <span style='font-size:1.08em;font-weight:600;color:#1976d2;'>&#128241; App version:</span><br>
    <span style='font-size:1.05em;color:#222;'>v2.1.2 - Enterprise RBAC, RAG, Audit Logging, Modern UI</span>
</div>
<div class='sidebar-card' style='background:#eaf6ff;font-size:0.93em;margin-bottom:16px;border:1.5px solid #b3e5fc;padding:8px 8px 6px 8px;'>
    <div style='font-weight:700;font-size:1em;line-height:1.2;margin-bottom:2px;text-align:center;'>
        <span style=\"font-size:1.05em;vertical-align:middle;\">&#129302;</span>  Local AI Governance Platform
    </div>
    <div style='margin:0 0 0 0;font-size:0.91em;line-height:1.35;text-align:center;'>
        <div style='display:flex;align-items:center;justify-content:center;gap:6px;margin-bottom:2px;'>
            <span style=\"font-size:1em;\">&#128269;</span> <span>Semantic Search (FAISS + SentenceTransformers)</span>
        </div>
        <div style='display:flex;align-items:center;justify-content:center;gap:6px;margin-bottom:2px;'>
            <span style=\"font-size:1em;\">&#128196;</span> <span>Document Q&amp;A (PDF, DOCX, TXT)</span>
        </div>
        <div style='display:flex;align-items:center;justify-content:center;gap:6px;margin-bottom:2px;'>
            <span style=\"font-size:1em;\">&#128273;</span> <span>Enterprise-Grade RBAC & Audit Logging</span>
        </div>
        <div style='display:flex;align-items:center;justify-content:center;gap:6px;margin-bottom:2px;'>
            <span style=\"font-size:1em;\">&#128640;</span> <span>Retrieval-Augmented Generation (RAG)</span>
        </div>
        <div style='display:flex;align-items:center;justify-content:center;gap:6px;margin-bottom:2px;'>
            <span style=\"font-size:1em;\">&#128187;</span> <span>Modern, Unified Chat UI</span>
        </div>
        <div style='display:flex;align-items:center;justify-content:center;gap:6px;margin-bottom:2px;'>
            <span style=\"font-size:1em;\">&#128221;</span> <span>Role-Preserved Chat History</span>
        </div>
        <div style='display:flex;align-items:center;justify-content:center;gap:6px;margin-bottom:2px;'>
            <span style=\"font-size:1em;\">&#128202;</span> <span>Feedback, Metrics, and Logging</span>
        </div>
        <div style='display:flex;align-items:center;justify-content:center;gap:6px;margin-bottom:2px;'>
            <span style=\"font-size:1em;\">&#128640;</span> <span>LLM: Ollama & HuggingFace</span>
        </div>
        <div style='display:flex;align-items:center;justify-content:center;gap:6px;margin-bottom:2px;'>
            <span style=\"font-size:1em;\">&#128736;</span> <span>Fully Tested (pytest)</span>
        </div>
        <div style='display:flex;align-items:center;justify-content:center;gap:6px;margin-bottom:2px;'>
            <span style=\"font-size:1em;\">&#128737;</span> <span>Private, Local LLM</span>
        </div>
        <div style='display:flex;align-items:center;justify-content:center;gap:6px;margin-bottom:2px;'>
            <span style=\"font-size:1em;\">&#9889;</span> <span>Fast, Modern UI</span>
        </div>
        <div style='display:flex;align-items:center;justify-content:center;gap:6px;margin-bottom:2px;'>
            <span style=\"font-size:1em;\">&#128274;</span> <span>Strict Role-Based Access Control (RBAC)</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)



    # Restore About This Project expander at the top
with st.sidebar.expander("ℹ️ About This Project", expanded=False):
    st.markdown("""
Portfolio Project
- Secure, local AI chatbot for enterprise document Q&A
- Strict, typo-tolerant RBAC for salary, onboarding, and SOP
- Retrieval-Augmented Generation (RAG) with semantic search
- Unified, modern chat UI with persistent role/model display
- Modular, extensible Python/Streamlit codebase
- Robust audit logging and feedback evaluation
- Production-grade deployment and reproducible environments
- **Persistent query logging and audit trail (CSV-based)**
- **Collapsible log viewer with denial log filtering and selection**
- **Denial detection logic for audit logs, with retroactive flagging and red highlighting**

**Target Audience:**
Technology executives, engineering leaders, HR professionals, AI/ML practitioners, and technical decision-makers interested in secure document Q&A, RBAC enforcement, and advanced LLM-driven systems for enterprise use cases.

**What This Demonstrates:**
- Deep LLM integration (Ollama, HuggingFace Transformers)
- Strict, typo-tolerant RBAC and audit logging
- Retrieval-Augmented Generation (RAG) pipeline
- Modern, role-preserved chat UI and feedback logging
- Clean architecture, modular code, and documentation
- Technical leadership and system design for enterprise AI
- **Persistent, filterable audit logs for all queries and denials**
- **Denial logs visually highlighted in red for clarity**
""", unsafe_allow_html=True)
with st.sidebar.expander("📄 Project Documentation", expanded=False):
    st.markdown("**Project Documentation**")
    st.markdown("[GitHub Repository](https://github.com/obizues/Local-AI-Chatbot-POC)")
    st.markdown("**Documentation**")
    st.markdown("- [README.md](https://github.com/obizues/Local-AI-Chatbot-POC/blob/main/README.md): Project overview, quick start, features")
    st.markdown("- [ARCHITECTURE.md](https://github.com/obizues/Local-AI-Chatbot-POC/blob/main/ARCHITECTURE.md): Deep technical documentation and diagrams")
    st.markdown("- System Diagrams: Mermaid diagrams for flow, components, and RAG")
    st.markdown("**Key Sections:**\n- RBAC & Audit Logging\n- RAG & Semantic Search\n- LLM integration strategy\n- Production deployment guide\n- Architectural decision records\n- Denial detection and audit log filtering logic\n- Red highlighting for denial logs in audit viewer")
with st.sidebar.expander("🧰 Tech Stack", expanded=False):
    st.markdown("""
<span style='font-size:1em;'>
<ul style='margin-bottom:0; padding-left: 18px;'>
<li>Python 3.10+</li>
<li>Streamlit (UI, audit log filtering, denial highlighting)</li>
<li>FAISS (vector search)</li>
<li>sentence-transformers (embeddings)</li>
<li>HuggingFace Transformers (LLM pipeline)</li>
<li>Ollama (local LLM, optional)</li>
<li>Flask (API integration)</li>
<li>pandas (data handling, audit log styling)</li>
<li>NumPy (vector math)</li>
<li>PyMuPDF (PDF ingestion)</li>
<li>python-docx (DOCX ingestion)</li>
<li>langchain, llama-index (optional, advanced retrieval)</li>
<li>pytest (testing, audit validation)</li>
</ul>
</span>
""", unsafe_allow_html=True)
with st.sidebar.expander("🧩 System Design Notes", expanded=False):
    st.markdown("""
<span style='font-size:1em;'>
<ul style='margin-bottom:0; padding-left: 18px;'>
<li><b>Retrieval-Augmented Chat:</b> User questions are embedded and matched to relevant document chunks using FAISS, providing context for LLM answers.</li>
<li><b>Unified Chat Interface:</b> Streamlit UI displays chat history, model selection, and sidebar documentation in a single, modern layout.</li>
<li><b>Session State Management:</b> All chat history, selected model, and user context are stored in Streamlit session state for seamless multi-turn conversations.</li>
<li><b>Flexible LLM Backend:</b> Supports both local (Ollama) and HuggingFace LLMs, switchable via UI, with fallback and error handling for robustness.</li>
<li><b>Document Ingestion Pipeline:</b> Batch scripts process PDFs, DOCX, and text files, chunking and embedding them for fast semantic search.</li>
<li><b>Feedback Logging:</b> User queries, responses, and feedback are logged to CSV for evaluation and improvement.</li>
<li><b>Customizable Sidebar:</b> Sidebar provides About, Documentation, Tech Stack, and System Design Notes, all styled for clarity and mobile compatibility.</li>
<li><b>Real-Time UI Updates:</b> Chat and sidebar update instantly on user input, with scroll-to-bottom and feedback features for usability.</li>
<li><b>Extensible Architecture:</b> Modular codebase allows easy addition of new models, data sources, or UI features.</li>
<li><b>Observability:</b> Debug logs and error messages are written to local files for troubleshooting and transparency.</li>
<li><b>Resilience:</b> Graceful error handling ensures the app remains usable even if some components fail or are unavailable.</li>
<li><b>Infrastructure:</b> Designed for local use, but can be containerized or deployed on private servers as needed.</li>
<li><b>Audit Log Filtering & Denial Highlighting:</b> Denial detection logic flags and highlights denial events in the audit log viewer for compliance and review.</li>
</ul>
</span>
""", unsafe_allow_html=True)
st.markdown("**Security & Privacy:** All processing is local; no data leaves the user's environment. API keys and secrets are managed via environment variables and never committed to source control.", unsafe_allow_html=True)