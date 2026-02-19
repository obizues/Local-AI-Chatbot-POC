import streamlit as st
import os
import faiss
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
from transformers import pipeline
import csv
import io
import time

from numpy import dot
from numpy.linalg import norm

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

# Embedding and generative model options
EMBED_MODEL_OPTIONS = [
    'all-MiniLM-L6-v2',
    # Add more embedding models here if needed
]
OLLAMA_MODEL = "llama2:7b-chat"
GEN_MODEL_OPTIONS = [
    'distilgpt2',
    'gpt2',
    'deepset/roberta-base-squad2',
    f'Ollama ({OLLAMA_MODEL})',  # Show model name in dropdown
    # Add more generative/extractive models here if needed
]

# Model selection UI
st.sidebar.header('Model Selection')
EMBED_MODEL_NAME = st.sidebar.selectbox('Embedding Model', EMBED_MODEL_OPTIONS, index=EMBED_MODEL_OPTIONS.index('all-MiniLM-L6-v2'))
GEN_MODEL_NAME_DISPLAY = st.sidebar.selectbox('Generative Model', GEN_MODEL_OPTIONS, index=GEN_MODEL_OPTIONS.index(f'Ollama ({OLLAMA_MODEL})'))
if GEN_MODEL_NAME_DISPLAY.startswith('Ollama'):
    GEN_MODEL_NAME = 'ollama'
else:
    GEN_MODEL_NAME = GEN_MODEL_NAME_DISPLAY

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



# Load embedding model (no timing)
embed_model = SentenceTransformer(EMBED_MODEL_NAME)





# Set up generative model (no timing)
OLLAMA_MODEL = "llama2:7b-chat"
if GEN_MODEL_NAME == 'ollama':
    llm = None  # Placeholder, handled in generate_answer
    gen_model_display = f"Ollama ({OLLAMA_MODEL})"
else:
    llm = pipeline('text-generation', model=GEN_MODEL_NAME, device=-1, max_new_tokens=256)
    gen_model_display = GEN_MODEL_NAME.upper()




# Show current models side by side
col1, col2 = st.columns(2)
with col1:
    st.write(f"**Embedding Model:** {EMBED_MODEL_NAME}")
with col2:
    st.write(f"**Generative Model:** {gen_model_display}")

# --- Move retrieve and generate_answer above chat UI ---
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

# --- Injected Modern Chat UI ---
if 'history' not in st.session_state:
    st.session_state['history'] = []

# CSS for scrollable chat box and chat bubbles
st.markdown('''
<style>
.scrollable-chat-window {
    max-width: 700px;
    margin: 0 auto 16px auto;
    height: 300px;
    overflow-y: scroll;
    padding: 0 8px 0 8px;
    background: #fafbfc;
    border: 1px solid #eee;
    border-radius: 8px;
    display: flex;
    flex-direction: column;
    justify-content: flex-end;
    scrollbar-color: #bbb #fafbfc;
    scrollbar-width: thin;
    align-items: flex-end;
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
    background: #fff;
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
    padding: 16px 0 0 0;
}
</style>
''', unsafe_allow_html=True)

# Scrollable chat window with fixed height, messages start at bottom
chat_html = '<div class="scrollable-chat-window">'
for user, bot in st.session_state.get('history', []):
    chat_html += f'<div class="chat-bubble-user">🧑 <b>You:</b> {user}</div>'
    chat_html += f'<div class="chat-bubble-bot">🤖 <b>Bot:</b> {bot}</div>'
chat_html += '</div>'
st.markdown(chat_html, unsafe_allow_html=True)

# Input bar just below chat window
st.markdown('<div class="input-bar">', unsafe_allow_html=True)
with st.form(key='chat_input_form', clear_on_submit=True):
    user_input = st.text_input("Message", "", key="user_input")
    submitted = st.form_submit_button("Send")
    if submitted and user_input.strip():
        # Use actual retrieval and model logic
        retrieved = retrieve(user_input)
        bot_response, _ = generate_answer(user_input, retrieved)
        st.session_state.setdefault('history', []).append((user_input, bot_response))
        st.rerun()
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
    # Remove markdown headings from context for LLM
    # Light filtering: exclude chunks with keywords that are clearly unrelated to deployment
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
    # Prompt refinement: instruct model to use only relevant info
    prompt = (
        "You are an expert assistant. Only use the information from the context that is directly relevant to the question. "
        "If some context is unrelated, ignore it. Do not mention or add any notes, disclaimers, or statements about what is or isn't included or omitted. Do not mention onboarding or vacation policies unless the question is about those topics. Do not repeat or restate the steps in your answer. Just answer the question directly.\n"
        f"Context:\n{context}\n\nQuestion: {query}\nAnswer:"
    )
    if GEN_MODEL_NAME == 'ollama':
        # Call Ollama via subprocess and time the response
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
            # If no output, show stderr and return code for debugging
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
