import os
import faiss
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
from transformers import pipeline
import streamlit as st

@st.cache_resource(show_spinner=True)
def load_embed_model():
    return SentenceTransformer('all-MiniLM-L6-v2')

@st.cache_resource(show_spinner=True)
def load_llm_pipeline(gen_model_name):
    if gen_model_name == 'ollama':
        return None, 'Ollama'
    else:
        llm = pipeline('text-generation', model=gen_model_name, device=-1, max_new_tokens=256)
        return llm, gen_model_name.upper()

# Data loading helpers
@st.cache_resource(show_spinner=True)
def load_faiss_index(index_path):
    return faiss.read_index(index_path)

@st.cache_resource(show_spinner=True)
def load_metadata(metadata_path):
    return pd.read_csv(metadata_path)
