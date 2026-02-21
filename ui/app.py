
import streamlit as st
# --- Echo mode toggle for testing chat scroll ---



import os
from sentence_transformers import SentenceTransformer
import pandas as pd
import faiss
import csv
import io
import time


from numpy import dot
from numpy.linalg import norm

# Model options (must be defined before use)
OLLAMA_MODEL = "llama2:7b-chat"
OLLAMA_MODEL_MISTRAL = "mistral"
GEN_MODEL_OPTIONS = [
    'distilgpt2',
    'gpt2',
    'deepset/roberta-base-squad2',
    f'Ollama ({OLLAMA_MODEL})',
    f'Ollama ({OLLAMA_MODEL_MISTRAL})'
]

def compute_max_similarity(answer, retrieved_texts, embed_model):
    answer_emb = embed_model.encode([answer])[0]
    chunk_embs = embed_model.encode([str(x) for x in retrieved_texts])
    sims = [dot(answer_emb, c) / (norm(answer_emb) * norm(c)) for c in chunk_embs]
    return max(sims) if sims else 0.0

st.set_page_config(page_title="Internal Chat AI", layout="wide")

# Reduce whitespace above the title
st.markdown('''
<style>
.block-container {
    padding-top: 1.5rem !important;
}
h1, .stMarkdown h1 {
    margin-top: 0.2em !important;
    }
    </style>
''', unsafe_allow_html=True)
st.markdown('<h1 style="margin-bottom: 0.2em;">Internal Chat AI (POC)</h1>', unsafe_allow_html=True)





# --- Echo mode toggle for testing chat scroll ---
st.sidebar.header('Test/Echo Mode')
ECHO_MODE = st.sidebar.checkbox('Enable test echo (bot repeats you)', key='echo_mode_checkbox')

# Model selection UI (generative model only) - now on main page
if ECHO_MODE:
    st.info('Test Echo Mode is enabled. The bot will simply repeat your input for testing purposes. No models are used.')
    GEN_MODEL_NAME_DISPLAY = f'Ollama ({OLLAMA_MODEL})'
    GEN_MODEL_NAME = 'ollama'
    OLLAMA_MODEL_SELECTED = OLLAMA_MODEL
else:

    GEN_MODEL_NAME_DISPLAY = st.selectbox('Active LLM', GEN_MODEL_OPTIONS, index=GEN_MODEL_OPTIONS.index(f'Ollama ({OLLAMA_MODEL})'))
    if GEN_MODEL_NAME_DISPLAY.startswith('Ollama'):
        GEN_MODEL_NAME = 'ollama'
        # Set the correct Ollama model string for use in subprocess
        if 'mistral' in GEN_MODEL_NAME_DISPLAY.lower():
            OLLAMA_MODEL_SELECTED = OLLAMA_MODEL_MISTRAL
        else:
            OLLAMA_MODEL_SELECTED = OLLAMA_MODEL
    else:
        GEN_MODEL_NAME = GEN_MODEL_NAME_DISPLAY
        OLLAMA_MODEL_SELECTED = OLLAMA_MODEL

    # Model loading timers
    load_times = {}
    # ...existing code...

    # Load FAISS index and metadata
    data_dir = os.path.join(os.path.dirname(__file__), '../vector_db')
    retrieval_start = time.time()
    index = faiss.read_index(os.path.join(data_dir, 'faiss_index.bin'))
    metadata = pd.read_csv(os.path.join(data_dir, 'metadata.csv'))
    retrieval_time = time.time() - retrieval_start

    # Model loading timers
    load_times = {}

    # Model loading timers
    load_times = {}

    # Load FAISS index and metadata
    data_dir = os.path.join(os.path.dirname(__file__), '../vector_db')
    retrieval_start = time.time()
    index = faiss.read_index(os.path.join(data_dir, 'faiss_index.bin'))
    metadata = pd.read_csv(os.path.join(data_dir, 'metadata.csv'))
    retrieval_time = time.time() - retrieval_start


    # Use fixed embedding model
    EMBED_MODEL_NAME = 'all-MiniLM-L6-v2'
    embed_model = SentenceTransformer(EMBED_MODEL_NAME)

    # Set up generative model (no timing)
    OLLAMA_MODEL = "llama2:7b-chat"
    if GEN_MODEL_NAME == 'ollama':
        llm = None  # Placeholder, handled in generate_answer
        gen_model_display = f"Ollama ({OLLAMA_MODEL})"
    else:
        llm = pipeline('text-generation', model=GEN_MODEL_NAME, device=-1, max_new_tokens=256)
        gen_model_display = GEN_MODEL_NAME.upper()





    # Show only generative model
    st.write(f"**Generative Model:** {gen_model_display}")
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

# --- Move retrieve and generate_answer above chat UI ---
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
    margin: 0 auto 4px auto;
    height: 300px;
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
    margin: 0 auto;
    background: #fff;
    padding: 2px 0 0 0;
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

    # Section to view demo results log
    st.sidebar.header('Demo Results Log')
    if st.sidebar.button('Refresh Log'):
        st.rerun()
    log_path = os.path.join(os.path.dirname(__file__), '..', 'demo_results.csv')
    expected_columns = ['question', 'answer', 'generative_model', 'embedding_model', 'elapsed_time', 'similarity', 'user_rating', 'notes']
    import csv
    import pandas as pd
    def rewrite_csv_with_header(path, header):
        with open(path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f, quoting=csv.QUOTE_ALL)
            writer.writerow(header)


# --- Collapsible Demo Results Log ---
with st.sidebar.expander('Demo Results Log', expanded=False):
    if st.button('Refresh Log', key='refresh_demo_log'):
        st.rerun()
    log_path = os.path.join(os.path.dirname(__file__), '..', 'demo_results.csv')
    expected_columns = ['question', 'answer', 'generative_model', 'embedding_model', 'elapsed_time', 'similarity', 'user_rating', 'notes']
    import csv
    import pandas as pd
    def rewrite_csv_with_header(path, header):
        with open(path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f, quoting=csv.QUOTE_ALL)
            writer.writerow(header)

    # ...existing code...
    if os.path.isfile(log_path):
        try:
            log_df = pd.read_csv(log_path, quoting=csv.QUOTE_ALL, quotechar='"', engine='python')
            # If columns don't match, rewrite file with new header
            if list(log_df.columns) != expected_columns:
                rewrite_csv_with_header(log_path, expected_columns)
                st.sidebar.warning('Log file format changed. The log was reset to match the new format.')
            else:
                st.sidebar.dataframe(log_df)
        except Exception as e:
            # If error, rewrite file with new header and show message
            rewrite_csv_with_header(log_path, expected_columns)
            st.sidebar.error(f'Log file was malformed and has been reset. Error: {e}')
    else:
        st.sidebar.info('No demo results logged yet.')


# --- Collapsible Improvements Tracker (Retrieval/Indexing/LLM/Settings only) ---
with st.sidebar.expander('Retrieval & Indexing Improvements', expanded=False):
    st.markdown('**Improvements to Embedding, Ingestion, LLM, Query, and Retrieval Accuracy/Settings:**')
    improvements = [
        "Updated retrieval filter to include vacation policy content for PTO/vacation questions.",
        "Verified both LLMs (llama2:7b, mistral) now use correct policy for PTO queries.",
        "Demo results log now auto-updates after each query for better evaluation.",
        "Similarity between answer and retrieved context is now logged for each query.",
        # Add more retrieval/indexing/accuracy/LLM/query/embedding/ingestion improvements here as you make them
    ]
    for i, item in enumerate(improvements, 1):
        st.markdown(f"**{i}.** {item}")
