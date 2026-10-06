import pytest
from recall.ai import parse_era
import streamlit as st

def test_era_fallback():
    # Override st.secrets to ensure fallback path is taken
    st.secrets = {}
    
    chapters = [
        {"name": "College", "start": "2018-08-01", "end": "2022-05-31", "aliases": "college first year;manipal"},
        {"name": "Scotland Masters", "start": "2023-09-01", "end": "2024-09-01", "aliases": "scotland;edinburgh"}
    ]
    
    res1 = parse_era("before COVID", chapters)
    assert res1["end"] == "2020-03-15"
    
    res2 = parse_era("2019", chapters)
    assert res2["start"] == "2019-01-01"
    assert res2["end"] == "2019-12-31"
    
    res3 = parse_era("summer 2019", chapters)
    assert res3["start"] == "2019-01-01"
    
    res4 = parse_era("college first year", chapters)
    assert res4["matched_chapter"] == "College"
    
    res5 = parse_era("when I was in Scotland", chapters)
    assert res5["matched_chapter"] == "Scotland Masters"
