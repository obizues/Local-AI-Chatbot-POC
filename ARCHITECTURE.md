



# Local AI Chatbot POC - Architecture (v1.0.2)

## Overview
This document describes the architecture, components, and deployment strategies for the Local AI Chatbot POC. The design is inspired by the structure and best practices of the agentic-mortgage-research project.



**Version:** v1.0.2 (March 2026)
## Key Components
- **ui/app.py**: Main Streamlit app, chat UI, sidebar/documentation, RBAC logic, onboarding, and salary extraction.
- **llm_backend/**: Business logic, LLM service, RAG pipeline, RBAC service, and data utilities.
- **ingestion/**: Scripts for document ingestion, chunking, and embedding.
- **vector_db/**: Stores metadata and vector index for document retrieval.
- **mock_data/**: Sample HR, Engineering, and Training documents.
- **tests/**: Unit and integration tests for chatbot logic and RBAC.

## Data Flow
1. User interacts with Streamlit UI (ui/app.py).
2. Query is processed, RBAC checked, and routed to LLM backend.
3. Relevant documents are retrieved from vector_db and mock_data.
4. LLM backend generates answer, possibly using RAG pipeline.
5. Results (e.g., salary tables, onboarding steps) are rendered in the UI.

## Known Issues
- Some business logic remains in the UI layer (to be refactored).
- App performance is slow for large queries.

**Major Features:**
- Enterprise-grade, typo-tolerant RBAC for all salary and sensitive queries
- Unified, modern Streamlit chat UI with persistent role/model display
- Role-preserved chat history (each message stores the role at time of sending)
- Advanced semantic search and retrieval (FAISS + SentenceTransformers)
- Robust audit logging and feedback metrics

## System Components
- **UI:** Streamlit-based chat interface (`ui/app.py`) with modern, right-aligned, bottom-aligned chat bubbles, persistent LLM/model display, and feedback controls
- **Sidebar:** About, Project Documentation, Tech Stack, System Design Notes, App Version (all styled and mobile-friendly)
- **LLM Integration:** Supports HuggingFace models and local Ollama (llama2:7b-chat, mistral, etc.), switchable via UI
- **Retrieval:** FAISS vector search with SentenceTransformers embeddings
- **Data:** CSV and local file-based document storage
- **Feedback & Logging:** Thumbs up/down voting, semantic similarity metrics, response time, LLM name display, and CSV logging (demo_results.csv)


**RBAC Logic:**
- HR: Sees all salaries
- CTO: Sees only Technology department salaries
- David Kim (Engineer): Sees only David Kim's salary (strict, typo-tolerant, all other salary queries blocked)

**Chat History:**
- Each chat bubble displays the role as it was when the message was sent, regardless of later role changes

## Key Design Principles
- Modular, extensible codebase
- Reproducible environments (requirements.txt, devcontainer)
- Secure secrets/configuration management (.env, .streamlit/secrets.toml)
- GitHub Actions for uptime and CI/CD
- Documentation-first: README, CHANGELOG, and architecture docs

## Deployment
- **Streamlit Cloud:** HuggingFace models only
- **Self-hosted/VM:** Full feature set with Ollama support
- **Dev Container:** VS Code + Docker for reproducible local development


## New in v0.11.0
- Strict, typo-tolerant RBAC for all salary and sensitive queries (HR: all, CTO: Technology only, David Kim: self only)
- Unified, modern chat UI with persistent role/model display and mobile-friendly sidebar
- Role-preserved chat history (each message stores the role at time of sending)
- Robust audit logging for all unauthorized access attempts
- All denials and fallbacks use a unified, branded HTML message
- Fully tested with pytest (RBAC, fallback, audit, typo-tolerance)
- Advanced semantic search and retrieval (FAISS + SentenceTransformers)
- Modular, extensible Python/Streamlit codebase



## Recent Updates (v0.11.0)
- Enterprise-grade, typo-tolerant RBAC for all salary and sensitive queries
- Unified, modern Streamlit chat UI with persistent role/model display
- Role-preserved chat history (each message stores the role at time of sending)
- Robust audit logging for all unauthorized access attempts
- All denials and fallbacks use a unified, branded HTML message
- Fully tested with pytest (RBAC, fallback, audit, typo-tolerance)
- Advanced semantic search and retrieval (FAISS + SentenceTransformers)
- Modular, extensible Python/Streamlit codebase

## Diagrams
### Chat UI and Data Flow (Mermaid)

```mermaid
graph TD
    UserInput[User Input] --> ChatWindow[Chat Window]
    ChatWindow --> LLMBackend[LLM Backend]
    LLMBackend --> Retrieval[Retrieval]
    Retrieval --> DataStore[Document/Data Store]
    LLMBackend --> ChatWindow
```


## Further Reading
- See README.md for quick start and usage
- See CHANGELOG.md for release history
- See ui/app.py for modern chat UI and RBAC logic

---
