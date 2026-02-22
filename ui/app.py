
# --- Define ECHO_MODE ---
ECHO_MODE = False

# --- Define model name variables ---
GEN_MODEL_NAME = 'ollama'  # or your default model name
GEN_MODEL_NAME_DISPLAY = 'Ollama'
import os
import time
import faiss
import pandas as pd
from sentence_transformers import SentenceTransformer

import streamlit as st

# Use fixed embedding model
EMBED_MODEL_NAME = 'all-MiniLM-L6-v2'
embed_model = SentenceTransformer(EMBED_MODEL_NAME)

# Set up generative model (no timing)
if GEN_MODEL_NAME == 'ollama':
    llm = None  # Placeholder, handled in generate_answer
    gen_model_display = GEN_MODEL_NAME_DISPLAY
else:
    llm = pipeline('text-generation', model=GEN_MODEL_NAME, device=-1, max_new_tokens=256)
    gen_model_display = GEN_MODEL_NAME.upper()
    # ...existing code...

import os
import time
import faiss
import pandas as pd
from sentence_transformers import SentenceTransformer

import streamlit as st


# --- Modern header banner ---

import subprocess
def get_app_version():
        try:
                return subprocess.check_output(["git", "describe", "--tags", "--abbrev=0"], encoding="utf-8").strip()
        except Exception:
                return "v1.0.0"
APP_VERSION = get_app_version()
header_html = f"""
<style>
.main-title-banner {{
    background: linear-gradient(90deg, #2196f3 0%, #00bfae 100%);
    color: #fff;
    padding: 6px 6px 4px 6px;
    border-radius: 8px;
    margin-bottom: 2px;
    text-align: center;
    font-size: 1.25em;
    font-weight: 600;
}}
.user-info-card {{
    background: #f7f7f7;
    color: #222;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    padding: 4px 8px 4px 8px;
    margin-bottom: 2px;
    max-width: 500px;
    margin-left: auto;
    margin-right: auto;
}}
.user-info-links {{
    margin-top: 4px;
    font-size: 0.95em;
}}
</style>
<div class="main-title-banner">
    Internal Chat AI (POC)
</div>
<div class="user-info-card" style="text-align:center;">
    <div style="font-size:1.15em;font-weight:600;color:#1976d2;text-align:center;">Chris Obermeier | SVP of Engineering</div>
    <div style="margin-bottom:6px;text-align:center;">Enterprise & PE-Backed Platform Modernization | AI & Data-Driven Transformation</div>
    <div class="user-info-links" style="text-align:center;margin-top:8px;">
            <span>
                <a href="https://www.linkedin.com/in/chris-obermeier" target="_blank" style="color:#1976d2;text-decoration:underline;">LinkedIn</a> |
                <a href="https://github.com/obizues/Local-AI-Chatbot-POC" target="_blank" style="color:#1976d2;text-decoration:underline;">GitHub</a> |
                <a href="mailto:chris.obermeier@gmail.com" style="color:#1976d2;text-decoration:underline;">Email</a>
            </span>
            <br>
            <span>
                ⭐ <a href="https://github.com/obizues/Local-AI-Chatbot-POC" target="_blank" style="color:#1976d2;text-decoration:underline;">Star on GitHub</a> |
                📖 <a href="https://github.com/obizues/Local-AI-Chatbot-POC#readme" target="_blank" style="color:#1976d2;text-decoration:underline;">Read Documentation</a> |
                🎓 <a href="https://github.com/obizues/Local-AI-Chatbot-POC/blob/main/ARCHITECTURE.md" target="_blank" style="color:#1976d2;text-decoration:underline;">View Architecture</a>
            </span>
        </div>
</div>
"""
st.markdown(header_html, unsafe_allow_html=True)


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
def retrieve(query, top_k=3):
    query_emb = embed_model.encode([query]).astype('float32')
    top_k = 5  # Retrieve more chunks for richer answers
    D, I = index.search(query_emb, top_k)
    results = metadata.iloc[I[0]]
    return results

def generate_answer(query, retrieved_chunks):
    # Echo mode for testing chat scroll
    if 'ECHO_MODE' in globals() and ECHO_MODE:
        return f'[echo] {query}', 0
    import time
    response_time = None
    unrelated_keywords = ["onboarding", "welcome", "paperwork"]
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
        response = llm(prompt)[0]['generated_text']
        response_time = time.time() - start
        return response, response_time

# --- Injected Modern Chat UI ---
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
    max-width: 700px;
    margin: 0 auto 2px auto;
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
    max-width: 700px;
    margin: 0 auto 0 auto;
    background: #fff;
    padding: 0px 0 0 0;
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
    if GEN_MODEL_NAME == 'ollama':
        MODEL_TYPE = f'Ollama ({OLLAMA_MODEL})'
    else:
        MODEL_TYPE = f'{GEN_MODEL_NAME} (generative)'


    # --- Custom Sidebar Layout ---
    # Sidebar info cards
    st.sidebar.markdown(f"""
    <div style='background:#eaf6ff;padding:10px 12px;border-radius:8px;margin-bottom:8px;font-size:1.1em;'>
        <b>Local AI Chatbot POC</b><br>
        Modern, production-ready chat UI with semantic search, LLM integration, and feedback logging.<br>
        <span style='font-size:0.95em;'>Inspired by <a href='https://github.com/obizues/agentic-mortgage-research' target='_blank'>agentic-mortgage-research</a>.</span><br>
        <b>App Version:</b> {APP_VERSION}
    </div>
    """, unsafe_allow_html=True)

    # Collapsible sidebar sections (default collapsed)
    with st.sidebar.expander("ℹ️ About This Project", expanded=False):
        st.markdown(f"""
        <span style='font-size:1em;'>
        <b>Local AI Chatbot POC</b> — Modern, production-ready chat UI with semantic search, LLM integration, and feedback logging.<br>
        Inspired by <a href='https://github.com/obizues/agentic-mortgage-research' target='_blank'>agentic-mortgage-research</a>.<br>
        <b>Version:</b> {APP_VERSION} — February 21, 2026
        </span>
        """, unsafe_allow_html=True)
    with st.sidebar.expander("📁 Project Documentation", expanded=False):
        st.markdown("""
        <span style='font-size:1em;'>
        <ul style='margin-bottom:0;'>
          <li><a href='https://github.com/obizues/Local-AI-Chatbot-POC/blob/main/README.md' target='_blank'>README</a></li>
          <li><a href='https://github.com/obizues/Local-AI-Chatbot-POC/blob/main/CHANGELOG.md' target='_blank'>Changelog</a></li>
          <li><a href='https://github.com/obizues/Local-AI-Chatbot-POC/blob/main/ARCHITECTURE.md' target='_blank'>Architecture</a></li>
          <li><a href='https://github.com/obizues/Local-AI-Chatbot-POC/blob/main/ARCHITECTURE.md#system-components' target='_blank'>System Design Notes</a></li>
        </ul>
        </span>
        """, unsafe_allow_html=True)
    with st.sidebar.expander("🛠️ Tech Stack", expanded=False):
        st.markdown("""
        <span style='font-size:1em;'>
        <ul style='margin-bottom:0;'>
          <li>Python 3.10+</li>
          <li>Streamlit</li>
          <li>FAISS, pandas, sentence-transformers</li>
          <li>Ollama (optional)</li>
          <li>HuggingFace Transformers</li>
          <li>Flask (API integration)</li>
        </ul>
        </span>
        """, unsafe_allow_html=True)
    with st.sidebar.expander("📝 System Design Notes", expanded=False):
        st.markdown("""
        <span style='font-size:1em;'>
        <ul style='margin-bottom:0;'>
          <li>Modern, compact chat UI with colored header and sidebar sections</li>
          <li>Sidebar: About, Documentation, Tech Stack, System Design Notes, App Version</li>
          <li>Unified chat logic in <code>ui/app.py</code> (no more <code>basic_chat.py</code>)</li>
          <li>Robust FAISS index and metadata loading</li>
          <li>Bugfixes for NameError and UI rendering</li>
          <li>All chat UI and logic now in <code>ui/app.py</code></li>
          <li>See <a href='https://github.com/obizues/Local-AI-Chatbot-POC/blob/main/ARCHITECTURE.md' target='_blank'>ARCHITECTURE.md</a></li>
        </ul>
        </span>
        """, unsafe_allow_html=True)
