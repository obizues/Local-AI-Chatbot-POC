import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest
import streamlit
from ui.app import generate_answer
import pandas as pd

# Mock CTO role and onboarding query
def test_cto_onboarding_returns_technology_chunk():
    # Simulate CTO role and onboarding query
    streamlit.session_state['user_role'] = 'Olivia Zhang (CTO)'
    query = "What's the onboarding process?"
    # Simulate empty DataFrame to trigger fallback
    retrieved_chunks = pd.DataFrame(columns=['file', 'text'])
    answer, _, provenance = generate_answer(query, retrieved_chunks)
    assert 'Technology Department Onboarding' in answer
    assert provenance == 'mock_data/Technology/technology_onboarding.md'
    assert '<ul>' in answer

# Mock DataFrame with technology onboarding chunk
def test_cto_onboarding_returns_chunk_from_dataframe():
    streamlit.session_state['user_role'] = 'Olivia Zhang (CTO)'
    query = "What's the onboarding process?"
    retrieved_chunks = pd.DataFrame([
        {'file': 'mock_data/Technology/technology_onboarding.md', 'text': '1. Complete your technical setup.'}
    ])
    answer, _, provenance = generate_answer(query, retrieved_chunks)
    assert 'Complete your technical setup' in answer
    assert provenance == 'mock_data/Technology/technology_onboarding.md'

# Ensure fallback returns error if file missing
def test_cto_onboarding_fallback_file_missing(monkeypatch):
    streamlit.session_state['user_role'] = 'Olivia Zhang (CTO)'
    query = "What's the onboarding process?"
    retrieved_chunks = pd.DataFrame(columns=['file', 'text'])
    monkeypatch.setattr('builtins.open', lambda *args, **kwargs: (_ for _ in ()).throw(FileNotFoundError()))
    answer, _, provenance = generate_answer(query, retrieved_chunks)
    assert 'Technology onboarding file not found.' in answer
    assert provenance is None
