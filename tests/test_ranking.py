import pytest
from recall.ranking import rank_moments, get_narrowing_question

def test_rank_moments():
    events = [
        {"id": "e1", "matched_photo_ids": ["p1", "p2", "p3", "p4"], "start": "2020"},
        {"id": "e2", "matched_photo_ids": ["p5"], "start": "2019"},
        {"id": "e3", "matched_photo_ids": ["p6"], "start": "2021"}
    ]
    
    ranked = rank_moments(events)
    # fewer photos first -> e2 and e3 have 1 photo. e3 is more recent -> e3, e2, e1
    assert ranked[0]["id"] == "e3"
    assert ranked[1]["id"] == "e2"
    assert ranked[2]["id"] == "e1"

def test_get_narrowing_question():
    events = [
        {"id": "e1", "event_type": "celebration", "place": "A"},
        {"id": "e2", "event_type": "school", "place": "B"},
        {"id": "e3", "event_type": "work", "place": "A"},
        {"id": "e4", "event_type": "food", "place": "B"},
        {"id": "e5", "event_type": "document", "place": "A"},
        {"id": "e6", "event_type": "other", "place": "B"}
    ]
    
    q = get_narrowing_question(events, {})
    assert q is not None
    assert q["facet"] == "type"
