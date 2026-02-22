
import streamlit as st
from sentence_transformers import SentenceTransformer
import faiss
import time

# Define app version at the top
APP_VERSION = "v0.9.0"
ECHO_MODE = False
GEN_MODEL_NAME = 'ollama'
GEN_MODEL_NAME_DISPLAY = 'Ollama'
header_html = """
<style>
.main-title-banner { display: flex; align-items: center; justify-content: flex-start; border-radius: 14px; padding: 12px 24px 10px 18px; margin-bottom: 0; box-shadow: 0 2px 12px rgba(33,150,243,0.08); font-family: 'Segoe UI', 'Arial', sans-serif; }
.main-title-banner .header-icon { font-size: 2.2rem; margin-right: 18px; filter: drop-shadow(0 1px 2px #90caf9); }
.main-title-banner .header-text { font-size: 2.1rem; font-weight: 700; color: #1976d2; letter-spacing: 0.5px; text-shadow: 0 1px 0 #fff, 0 2px 6px #90caf9; }
</style>
<div class="main-title-banner"><span class="header-icon">&#127979;&#65039;</span><span class="header-text">Internal Chat AI (POC)</span></div>
"""

import streamlit as st
import os
import pandas as pd
from sentence_transformers import SentenceTransformer
from transformers import pipeline

# Use fixed embedding model
EMBED_MODEL_NAME = 'all-MiniLM-L6-v2'
embed_model = SentenceTransformer(EMBED_MODEL_NAME)


# Always show the header, regardless of model


from numpy import dot
from numpy.linalg import norm

# Model options (must be defined before use)
OLLAMA_MODEL = "llama2"  # Default model name (set to your preferred default)
OLLAMA_MODEL_SELECTED = OLLAMA_MODEL  # Default selected model
OLLAMA_MODEL = "llama2:7b-chat"
OLLAMA_MODEL_MISTRAL = "mistral"
GEN_MODEL_OPTIONS = [
    'distilgpt2',
    'gpt2',
    'deepset/roberta-base-squad2',
    f'Ollama ({OLLAMA_MODEL})',
    f'Ollama ({OLLAMA_MODEL_MISTRAL})'
]

st.set_page_config(page_title="Internal Chat AI", layout="wide")

# Always show the header, regardless of model


st.markdown(header_html, unsafe_allow_html=True)

user_info_html = """
<style>
.user-info-card {
    background: #e9ecef;
    border-radius: 10px;
    padding: 14px 20px 10px 20px;
    margin-top: 0;
    margin-bottom: 14px;
    box-shadow: 0 1px 6px rgba(33,150,243,0.06);
    text-align: center;
    font-family: 'Segoe UI', 'Arial', sans-serif;
}
.user-info-card .user-title {
    font-size: 1.05rem;
    font-weight: 600;
    color: #1976d2;
    margin-bottom: 2px;
}
.user-info-card .user-subtitle {
    font-size: 0.84rem;
    color: #2196f3;
    margin-bottom: 5px;
}
.user-info-links {
    margin-top: 3px;
    font-size: 0.89em;
}
.user-info-links a {
    color: #1976d2;
    text-decoration: underline;
    margin: 0 2px;
}
.user-info-links .link-block {
    display: block;
    margin-top: 1px;
    font-size: 0.83em;
}
</style>
<div class="user-info-card">
    <div class="user-title">Chris Obermeier | SVP of Engineering</div>
    <div class="user-subtitle">Enterprise &amp; PE-Backed Platform Modernization | AI &amp; Data-Driven Transformation</div>
    <div class="user-info-links">
        <span>
            <a href="https://www.linkedin.com/in/chris-obermeier" target="_blank">LinkedIn</a> |
            <a href="https://github.com/obizues/Local-AI-Chatbot-POC" target="_blank">GitHub</a> |
            <a href="mailto:chris.obermeier@gmail.com">Email</a>
        </span>
        <span class="link-block">
            &#11088; <a href="https://github.com/obizues/Local-AI-Chatbot-POC" target="_blank">Star on GitHub</a> |
            &#128214; <a href="https://github.com/obizues/Local-AI-Chatbot-POC#readme" target="_blank">Read Documentation</a> |
            &#127891; <a href="https://github.com/obizues/Local-AI-Chatbot-POC/blob/main/ARCHITECTURE.md" target="_blank">View Architecture</a>
        </span>
    </div>
</div>
"""
st.markdown(user_info_html, unsafe_allow_html=True)


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
    unrelated_keywords = ["vacation", "paid vacation", "HR portal", "onboarding", "welcome", "paperwork"]
    filtered_texts = []
    for x in retrieved_chunks['text'].tolist():
        if isinstance(x, str) and x.strip():
            lowered = x.lower()
            if not any(kw in lowered for kw in unrelated_keywords):
                filtered_texts.append(x)
    context = "\n".join(filtered_texts)
    context = "\n".join(
        line for line in context.splitlines() if not line.strip().startswith("#")
    )
    prompt = (
        "You are an expert assistant. Only use the information from the context that is directly relevant to the question. "
        "If some context is unrelated, ignore it. Do not mention or add any notes, disclaimers, or statements about what is or isn't included or omitted. Do not mention onboarding or vacation policies unless the question is about those topics. Do not repeat or restate the steps in your answer. Just answer the question directly.\n"
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
            result = subprocess.run([
                ollama_path, "run", OLLAMA_MODEL_SELECTED
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



    
with st.container():
    st.markdown('<div class="model-select-row"><span class="model-select-label">LLM Model:</span></div>', unsafe_allow_html=True)
    selected_model = st.selectbox(
        "LLM Model",
        GEN_MODEL_OPTIONS,
        index=GEN_MODEL_OPTIONS.index('Ollama (llama2:7b-chat)'),
        key="llm_model_select",
        label_visibility="collapsed"
    )

# Update model selection in session state (if needed)
if 'selected_model' not in st.session_state or st.session_state['selected_model'] != selected_model:
    st.session_state['selected_model'] = selected_model

def retrieve(query, top_k=3):
    query_emb = embed_model.encode([query]).astype('float32')
    top_k = 5  # Retrieve more chunks for richer answers
    D, I = index.search(query_emb, top_k)
    results = metadata.iloc[I[0]]
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
    height: 180px;
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
    padding: 10px 16px;
    border-radius: 18px 18px 4px 18px;
    margin-bottom: 4px;
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
    padding: 10px 16px;
    border-radius: 18px 18px 18px 4px;
    margin-bottom: 16px;
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
    padding: 0;
}
</style>
''', unsafe_allow_html=True)


# Scrollable chat window with fixed height, messages start at bottom
 # Scrollable chat window with fixed height, messages start at bottom

# Render messages in normal order (newest at bottom) with feedback



import uuid
    # ...existing code...
chat_html = '<div class="scrollable-chat-window">'
for idx, entry in enumerate(reversed(st.session_state.get('history', []))):
    # Unpack entry
    if len(entry) == 4:
        user, bot, response_time, extra = entry
    elif len(entry) == 3:
        user, bot, response_time = entry
        extra = ''
    else:
        user, bot = entry
        response_time = None
        extra = ''

    # Always show response time and LLM model at the bottom of the bot message
    # If extra is empty or 'neutral', use the current LLM name
    if extra and extra not in ['neutral', '']:
        llm_display = f' | {extra}'
    else:
        # Use the current LLM for display
        llm_display = f' | Ollama ({OLLAMA_MODEL_SELECTED})' if GEN_MODEL_NAME == 'ollama' else f' | {GEN_MODEL_NAME} (generative)'
    if response_time is not None:
        time_llm_html = f'<span style="font-size:0.85em;color:#888;">({response_time:.2f}s{llm_display})</span>'
    else:
        time_llm_html = ''
    chat_html += f'<div>'
    chat_html += f'<div class="chat-bubble-user">🧑 <b>You:</b> {user}</div>'
    chat_html += f'<div class="chat-bubble-bot">🤖 <b>Bot:</b> {bot}'
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
        if 'ECHO_MODE' in globals() and ECHO_MODE:
            bot_response = f'[echo] {user_input}'
            llm_used = f"Ollama ({OLLAMA_MODEL_SELECTED})" if GEN_MODEL_NAME == 'ollama' else f"{GEN_MODEL_NAME} (generative)"
            st.session_state.setdefault('history', []).append((user_input, bot_response, 0.0, llm_used))
            st.rerun()
        else:
            # Use actual retrieval and model logic
            retrieved = retrieve(user_input)
            bot_response, response_time = generate_answer(user_input, retrieved)
            llm_used = f"Ollama ({OLLAMA_MODEL_SELECTED})" if GEN_MODEL_NAME == 'ollama' else f"{GEN_MODEL_NAME} (generative)"
            st.session_state.setdefault('history', []).append((user_input, bot_response, response_time, llm_used))
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
        try:
            log_path = os.path.join(os.path.dirname(__file__), '..', 'ollama_debug.log')
            with open(log_path, 'a', encoding='utf-8') as logf:
                logf.write(f"[CHAT] Response time: {response_time:.2f}s\n")
        except Exception:
            pass

        # --- Auto-append to demo_results.csv ---
        try:
            demo_log_path = os.path.join(os.path.dirname(__file__), '..', 'demo_results.csv')
            expected_columns = ['question', 'answer', 'generative_model', 'embedding_model', 'elapsed_time', 'similarity', 'user_rating', 'notes']
            import csv
            import os
            import pandas as pd
            # Compute similarity if possible
            similarity = None
            try:
                retrieved_texts = retrieved['text'].tolist() if hasattr(retrieved, 'text') else []
                similarity = compute_max_similarity(bot_response, retrieved_texts, embed_model)
            except Exception:
                similarity = ''
            # Write header if file does not exist
            write_header = not os.path.isfile(demo_log_path)
            with open(demo_log_path, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f, quoting=csv.QUOTE_ALL)
                if write_header:
                    writer.writerow(expected_columns)
                writer.writerow([
                    user_input,
                    bot_response,
                    f"Ollama ({OLLAMA_MODEL_SELECTED})" if GEN_MODEL_NAME == 'ollama' else f"{GEN_MODEL_NAME} (generative)",
                    EMBED_MODEL_NAME,
                    f"{response_time:.2f}",
                    f"{similarity:.3f}" if similarity is not None and similarity != '' else '',
                    'neutral',
                    ''
                ])
        except Exception as e:
            # Optionally log or print error
            pass

        llm_used = f"Ollama ({OLLAMA_MODEL_SELECTED})" if GEN_MODEL_NAME == 'ollama' else f"{GEN_MODEL_NAME} (generative)"
        st.session_state.setdefault('history', []).append((user_input, bot_response, response_time, llm_used))
        st.rerun()
    # ...existing code...
st.markdown('</div>', unsafe_allow_html=True)

def retrieve(query, top_k=3):
    query_emb = embed_model.encode([query]).astype('float32')
    top_k = 5  # Retrieve more chunks for richer answers
    D, I = index.search(query_emb, top_k)
    results = metadata.iloc[I[0]]
    return results

def generate_answer(query, retrieved_chunks):
    import time
    response_time = None
    unrelated_keywords = ["vacation", "paid vacation", "HR portal", "onboarding", "welcome", "paperwork"]
    filtered_texts = []
    for x in retrieved_chunks['text'].tolist():
        if isinstance(x, str) and x.strip():
            lowered = x.lower()
            if not any(kw in lowered for kw in unrelated_keywords):
                filtered_texts.append(x)
    context = "\n".join(filtered_texts)
    context = "\n".join(
        line for line in context.splitlines() if not line.strip().startswith("#")
    )
    prompt = (
        "You are an expert assistant. Only use the information from the context that is directly relevant to the question. "
        "If some context is unrelated, ignore it. Do not mention or add any notes, disclaimers, or statements about what is or isn't included or omitted. Do not mention onboarding or vacation policies unless the question is about those topics. Do not repeat or restate the steps in your answer. Just answer the question directly.\n"
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
            result = subprocess.run([
                ollama_path, "run", "llama2:7b-chat"
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
        response = llm(prompt)[0]['generated_text']
        response_time = time.time() - start
        return response, response_time


if not ECHO_MODE:
    # Streamlit UI

    # Track model type for logging (dynamic)



# Collapsible sidebar sections (default collapsed)

    st.markdown("""
    <b>Portfolio Project</b><br><br>
    This is a demonstration of agentic AI architecture built to showcase:
    <ul style='margin-top: 6px; margin-bottom: 0;'>
        <li>Multi-agent LLM orchestration</li>
        <li>Multi-round debate system with consensus building</li>
        <li>Historical learning with outcome validation</li>
        <li>Real-time UI with streaming updates</li>
        <li>Production-grade patterns</li>
        <li>System design thinking</li>
    </ul>
    """, unsafe_allow_html=True)


st.sidebar.markdown(f"""
<div class='sidebar-card' style='font-size:0.97em;padding:8px 12px 6px 12px;'>
    <span style='font-size:1.05em;'>&#128241;</span> <b style='font-size:1em;'>App version:</b><br>
    <span style='font-size:0.95em;'>{APP_VERSION} - Demo UI Polishing</span>
</div>
<div class='sidebar-card' style='background:#eaf6ff;font-size:0.93em;margin-bottom:16px;border:1.5px solid #b3e5fc;padding:8px 8px 6px 8px;'>
    <div style='font-weight:700;font-size:1em;line-height:1.2;margin-bottom:2px;text-align:center;'>
        <span style=\"font-size:1.05em;vertical-align:middle;\">&#129302;</span> AI Search & Knowledge System
    </div>
    <div style='margin:0 0 0 0;font-size:0.91em;line-height:1.35;text-align:center;'>
        <div style='display:flex;align-items:center;justify-content:center;gap:6px;margin-bottom:2px;'>
            <span style=\"font-size:1em;\">&#128269;</span> <span>Semantic Search</span>
        </div>
        <div style='display:flex;align-items:center;justify-content:center;gap:6px;margin-bottom:2px;'>
            <span style=\"font-size:1em;\">&#128196;</span> <span>Document Q&amp;A</span>
        </div>
        <div style='display:flex;align-items:center;justify-content:center;gap:6px;margin-bottom:2px;'>
            <span style=\"font-size:1em;\">&#128737;</span> <span>Private, Local LLM</span>
        </div>
        <div style='display:flex;align-items:center;justify-content:center;gap:6px;margin-bottom:2px;'>
            <span style=\"font-size:1em;\">&#9889;</span> <span>Fast, Modern UI</span>
        </div>
        <div style='display:flex;align-items:center;justify-content:center;gap:6px;'>
            <span style=\"font-size:1em;\">&#128202;</span> <span>Feedback Logging</span>
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
                <b>GitHub Repository</b> 🔗 <a href='https://github.com/obizues/Local-AI-Chatbot-POC' target='_blank'>github.com/obizues/Local-AI-Chatbot-POC</a>
            </span>
        </div>
        <div style='margin-bottom:8px;'><b>Documentation</b></div>
        <ul style='margin-bottom:0; padding-left: 18px;'>
            <li>📖 <a href='https://github.com/obizues/Local-AI-Chatbot-POC/blob/main/README.md' target='_blank'>README.md</a> - Project overview, quick start, features</li>
            <li>🏗️ <a href='https://github.com/obizues/Local-AI-Chatbot-POC/blob/main/ARCHITECTURE.md' target='_blank'>ARCHITECTURE.md</a> - Deep technical documentation</li>
            <li>📊 System Diagrams - 5 Mermaid diagrams</li>
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
        st.markdown("""
        <div style='font-size:1.12em;font-weight:700;margin-bottom:8px;'>📋 System Design Notes</div>
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
        """, unsafe_allow_html=True)
