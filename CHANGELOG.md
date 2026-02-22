# [0.8.0] - 2026-02-21
### Added
- Modern, compact chat UI with colored header and sidebar sections
- Sidebar: About, Documentation, Tech Stack, System Design Notes, App Version
- Unified chat logic in `ui/app.py` (no more `basic_chat.py`)
- Robust FAISS index and metadata loading
- Bugfixes for NameError and UI rendering
- All chat UI and logic now in `ui/app.py`


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
