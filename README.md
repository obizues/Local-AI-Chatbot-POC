# Local Internal Chat AI POC

This project demonstrates a fully local, privacy-preserving internal chat AI with document ingestion, semantic search, RAG pipeline, and simulated RBAC security. Includes mock HR, Engineering, and Training documents in various formats.

## Features
- Local document ingestion (PDF, DOCX, MD, TXT)
- Embedding & vector search (FAISS)
- Retrieval-Augmented Generation (RAG) with open-source LLM
- Streamlit UI
- Simulated RBAC security

## Quick Start
1. Install requirements: `pip install -r requirements.txt`
2. Run Streamlit UI: `streamlit run ui/app.py`

## Folder Structure
- mock_data/ — Sample documents (HR, Engineering, Training)
- ingestion/ — Scripts for loading, chunking, embedding
- vector_db/ — FAISS index files
- llm_backend/ — RAG pipeline code
- ui/ — Streamlit/Gradio app
- security/ — RBAC logic
