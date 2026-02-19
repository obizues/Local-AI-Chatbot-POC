import os
import faiss
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
from transformers import pipeline

# Load FAISS index and metadata
data_dir = os.path.join(os.path.dirname(__file__), '../vector_db')
index = faiss.read_index(os.path.join(data_dir, 'faiss_index.bin'))
metadata = pd.read_csv(os.path.join(data_dir, 'metadata.csv'))

# Load embedding model
embed_model = SentenceTransformer('all-MiniLM-L6-v2')

# Load LLM (local, small for demo)
llm = pipeline('text-generation', model='distilgpt2', device='cpu', max_new_tokens=128)

def retrieve(query, top_k=3):
    query_emb = embed_model.encode([query]).astype('float32')
    D, I = index.search(query_emb, top_k)
    results = metadata.iloc[I[0]]
    return results

def generate_answer(query, retrieved_chunks):
    context = "\n".join(retrieved_chunks['text'].tolist())
    prompt = f"Context:\n{context}\n\nQuestion: {query}\nAnswer:"
    response = llm(prompt)[0]['generated_text']
    return response

if __name__ == "__main__":
    user_query = input("Ask a question: ")
    retrieved = retrieve(user_query)
    answer = generate_answer(user_query, retrieved)
    print("\n--- Retrieved Chunks ---")
    print(retrieved[['file', 'text']])
    print("\n--- AI Answer ---")
    print(answer)
