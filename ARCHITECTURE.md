# Architecture: Local AI Chatbot POC

## Overview
This document describes the architecture, components, and deployment strategies for the Local AI Chatbot POC. The design is inspired by the structure and best practices of the agentic-mortgage-research project.

## System Components
- **UI:** Streamlit-based chat interface (`ui/app.py`) with modern, right-aligned, bottom-aligned chat bubbles
- **LLM Integration:** Supports HuggingFace models and local Ollama (if available)
- **Retrieval:** FAISS vector search with SentenceTransformers embeddings
- **Data:** CSV and local file-based document storage
- **Feedback:** Thumbs up/down voting, semantic similarity metrics, and CSV logging

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
