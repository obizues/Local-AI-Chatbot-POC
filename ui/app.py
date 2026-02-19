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

st.set_page_config(page_title="Internal Chat AI POC", layout="wide")
st.title("Internal Chat AI (POC)")

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


# Show current models
st.write(f"**Embedding Model:** {EMBED_MODEL_NAME}")
st.write(f"**Generative Model:** {gen_model_display}")

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

if 'history' not in st.session_state:
    st.session_state['history'] = []

if 'loading' not in st.session_state:
    st.session_state['loading'] = False
if 'current_question' not in st.session_state:
    st.session_state['current_question'] = ''
if 'cancel' not in st.session_state:
    st.session_state['cancel'] = False

with st.form(key='chat_form', clear_on_submit=True):
    user_query = st.text_input("Ask a question:", "")
    submit = st.form_submit_button("Send", disabled=st.session_state['loading'])

if submit and not st.session_state['loading']:
    st.session_state['loading'] = True
    st.session_state['current_question'] = user_query
    st.session_state['cancel'] = False

if st.session_state['loading']:
    with st.spinner(f"Loading response for: '{st.session_state['current_question']}' ..."):
        # Only log if user_query is a real question (not blank, not None, starts with a question word)
        question_words = ("what", "how", "do", "when", "where", "why", "who", "is", "are", "can", "should", "does", "did", "will", "could", "would", "may", "might")
        total_start = time.time()
        if isinstance(st.session_state['current_question'], str) and st.session_state['current_question'].strip() and st.session_state['current_question'].strip().lower().startswith(question_words):
            retrieval_start = time.time()
            retrieved = retrieve(st.session_state['current_question'])
            # Only measure total elapsed time for both retrieval and answer
            answer_start = time.time()
            answer, _ = generate_answer(st.session_state['current_question'], retrieved)
            elapsed_time = time.time() - total_start
            # Semantic similarity metric
            retrieved_texts = retrieved['text'].tolist()
            similarity = compute_max_similarity(answer, retrieved_texts, embed_model)
            user_rating = 'neutral'  # Default is neutral unless voted
            st.session_state['history'].append((st.session_state['current_question'], answer, retrieved[['file', 'text']], elapsed_time, similarity))
            # Log to CSV
            log_path = os.path.join(os.path.dirname(__file__), '..', 'demo_results.csv')
            file_exists = os.path.isfile(log_path)
            import csv
            with open(log_path, 'a', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile, quoting=csv.QUOTE_ALL)
                if not file_exists:
                    writer.writerow(['question', 'answer', 'generative_model', 'embedding_model', 'elapsed_time', 'similarity', 'user_rating', 'notes'])
                writer.writerow([st.session_state['current_question'], answer, MODEL_TYPE, EMBED_MODEL_NAME, f"{elapsed_time:.2f}", f"{similarity:.3f}", user_rating, ''])
        else:
            # Still answer and show in UI, but do not log
            retrieval_start = time.time()
            retrieved = retrieve(st.session_state['current_question'])
            answer_start = time.time()
            answer, _ = generate_answer(st.session_state['current_question'], retrieved)
            elapsed_time = time.time() - total_start
            similarity = compute_max_similarity(answer, retrieved['text'].tolist(), embed_model)
            st.session_state['history'].append((st.session_state['current_question'], answer, retrieved[['file', 'text']], elapsed_time, similarity))
        st.session_state['loading'] = False
        st.session_state['current_question'] = ''
        st.rerun()

if 'feedback' not in st.session_state:
    st.session_state['feedback'] = {}

for idx, (q, a, docs, elapsed_time, similarity) in enumerate(reversed(st.session_state['history'])):
    st.markdown(f"**You:** {q}")
    # Show model name in parenthesis next to AI if Ollama is used
    if GEN_MODEL_NAME == 'ollama':
        st.markdown(f"**AI ({OLLAMA_MODEL}):** {a}")
    else:
        st.markdown(f"**AI:** {a}")
    # Show elapsed time and semantic similarity on the same line
    st.markdown(f"_Elapsed time: {elapsed_time:.2f} s | Semantic similarity to source: {similarity:.3f}_")
    # Voting UI: clear label and buttons side by side
    st.markdown("<span style='font-weight:600;'>Vote on this answer:</span>", unsafe_allow_html=True)
    feedback_key = f"feedback_{idx}"
    feedback_val = st.session_state['feedback'].get(feedback_key, 'neutral')
    # Place buttons inline using columns with minimal spacing
    col_up, col_down, col_reset = st.columns([1,1,1], gap="small")
    up_style = "background-color: #d4edda; border-radius: 8px; font-size: 1.2em;" if feedback_val == 'up' else "font-size: 1.2em;"
    down_style = "background-color: #f8d7da; border-radius: 8px; font-size: 1.2em;" if feedback_val == 'down' else "font-size: 1.2em;"
    reset_style = "background-color: #e2e3e5; border-radius: 8px; font-size: 1.1em;" if feedback_val == 'neutral' else "font-size: 1.1em;"
    with col_up:
        if st.button("👍", key=f"up_{idx}"):
            if feedback_val == 'up':
                st.session_state['feedback'][feedback_key] = 'neutral'
                feedback_val = 'neutral'
            else:
                st.session_state['feedback'][feedback_key] = 'up'
                feedback_val = 'up'
            # Log feedback immediately to CSV
            log_path = os.path.join(os.path.dirname(__file__), '..', 'demo_results.csv')
            if os.path.isfile(log_path):
                import pandas as pd
                df = pd.read_csv(log_path, quoting=csv.QUOTE_ALL, quotechar='"', engine='python')
                mask = (df['question'] == q) & (df['answer'] == a)
                idxs = df[mask].index.tolist()
                if idxs:
                    df.at[idxs[-1], 'user_rating'] = feedback_val
                    df.to_csv(log_path, index=False, quoting=csv.QUOTE_ALL)
    with col_down:
        if st.button("👎", key=f"down_{idx}"):
            if feedback_val == 'down':
                st.session_state['feedback'][feedback_key] = 'neutral'
                feedback_val = 'neutral'
            else:
                st.session_state['feedback'][feedback_key] = 'down'
                feedback_val = 'down'
            # Log feedback immediately to CSV
            log_path = os.path.join(os.path.dirname(__file__), '..', 'demo_results.csv')
            if os.path.isfile(log_path):
                import pandas as pd
                df = pd.read_csv(log_path, quoting=csv.QUOTE_ALL, quotechar='"', engine='python')
                mask = (df['question'] == q) & (df['answer'] == a)
                idxs = df[mask].index.tolist()
                if idxs:
                    df.at[idxs[-1], 'user_rating'] = feedback_val
                    df.to_csv(log_path, index=False, quoting=csv.QUOTE_ALL)
    with col_reset:
        if st.button("Reset", key=f"reset_{idx}"):
            st.session_state['feedback'][feedback_key] = 'neutral'
            feedback_val = 'neutral'
            # Log feedback immediately to CSV
            log_path = os.path.join(os.path.dirname(__file__), '..', 'demo_results.csv')
            if os.path.isfile(log_path):
                import pandas as pd
                df = pd.read_csv(log_path, quoting=csv.QUOTE_ALL, quotechar='"', engine='python')
                mask = (df['question'] == q) & (df['answer'] == a)
                idxs = df[mask].index.tolist()
                if idxs:
                    df.at[idxs[-1], 'user_rating'] = feedback_val
                    df.to_csv(log_path, index=False, quoting=csv.QUOTE_ALL)
    # Show feedback status with highlight
    feedback_display = ''
    if feedback_val == 'up':
        feedback_display = ':green[👍 You liked this answer]'
    elif feedback_val == 'down':
        feedback_display = ':red[👎 You disliked this answer]'
    else:
        feedback_display = ':gray[No feedback given]'
    st.markdown(feedback_display)
    with st.expander("Show retrieved document chunks"):
        st.dataframe(docs)

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
