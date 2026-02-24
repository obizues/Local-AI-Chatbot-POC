

# [0.11.0] - 2026-02-23
### Changed
- Strict RBAC for salary and sensitive data (HR: all, CTO: Technology only, David Kim: self only)
- All salary responses are formatted as HTML tables
- CTO/HR queries for specific roles (e.g., CTO salary) return only that individual's salary

# [0.10.0] - 2026-02-23
### Added
- Strict RBAC for salary and sensitive data (HR: all, CTO: Technology only, David Kim: self only)
- All salary responses are formatted as HTML tables
- CTO/HR queries for specific roles (e.g., CTO salary) return only that individual's salary
- Role-preserved chat history (each message stores the role at time of sending)
- Chat bubbles always display the role at the time of message
- UI/UX improvements and bug fixes

# [0.9.0] - 2026-02-22
### Added
- Unified, modern chat UI with colored header, sidebar, and persistent model display
- Sidebar: About, Project Documentation, Tech Stack, System Design Notes, App Version
- Conversational Q&A over internal documents (PDF, DOCX, TXT)
- Semantic search and retrieval with FAISS and SentenceTransformers
- LLM support: Ollama (local) and HuggingFace Transformers (cloud/local)
- Feedback logging, semantic similarity, and response time metrics
- CSV logging of all interactions for evaluation
- Modular, extensible Python codebase


# Changelog

## [0.6.0] - 2026-02-19
### Added
- Unified chat UI in `ui/app.py` (basic_chat.py deprecated)
- Always display LLM/model name after each response
- Improved retrieval accuracy and logging
- Feedback and improvements tracker in sidebar
- Removal of unused `my_chat_component` folder

## [0.2.0] - 2026-02-19
### Changed
- Replaced old chat UI with new modern, right-aligned, bottom-aligned chat bubbles in ui/app.py
- Removed basic_chat.py; all chat functionality is now in app.py
- Updated documentation and project structure to reflect new UI

## [0.1.0] - 2026-02-18
### Added
- Initial public release of the Internal Chat AI POC
- Streamlit UI for chat with LLM (Ollama and HuggingFace support)
- Semantic search and retrieval with FAISS and SentenceTransformers
- Thumbs up/down feedback with logging
- Semantic similarity and elapsed time metrics
- CSV logging of all interactions
- GitHub integration and project scaffolding
