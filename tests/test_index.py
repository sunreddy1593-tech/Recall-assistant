import pytest
from recall.index import apply_filters

def test_apply_filters():
    index = {
        "photos": {
            "p1": {"id": "p1", "taken_at": "2019-02-14", "place": "A", "people": ["Ananya"]},
            "p2": {"id": "p2", "taken_at": "2020-02-14", "place": "B", "people": ["Kabir"]},
        },
        "events": [
            {"id": "e1", "photo_ids": ["p1"], "event_label": "Dinner"},
            {"id": "e2", "photo_ids": ["p2"], "event_label": "Party"},
        ],
        "chapters": []
    }
    
    evs, phs = apply_filters(index, {"who": ["Ananya"]})
    assert len(phs) == 1
    assert "p1" in phs
    assert len(evs) == 1
    assert evs[0]["id"] == "e1"
