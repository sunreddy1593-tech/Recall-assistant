import json
import pytest
from recall.index import apply_filters, get_facet_counts

@pytest.fixture
def index_data():
    with open("data/index.json", "r") as f:
        return json.load(f)

def test_no_placeholders(index_data):
    photos = index_data["photos"]
    placeholders = sum(1 for p in photos.values() if p.get("caption", "").startswith("Placeholder"))
    assert placeholders == 0, f"Expected 0 placeholders, found {placeholders}"

def test_other_ratio(index_data):
    events = index_data["events"]
    total = len(events)
    others = sum(1 for e in events if e.get("event_type") == "other")
    assert others / total <= 0.1, f"Expected <=10% 'other' events, found {others}/{total} ({others/total:.1%})"

def test_screenshots_exist(index_data):
    events = index_data["events"]
    screenshots = sum(1 for e in events if e.get("type") == "screenshot" or e.get("event_type") == "screenshot")
    assert screenshots >= 1, "Expected at least 1 screenshot event"

def test_nolocation_types(index_data):
    photos = index_data["photos"]
    nolocation_photos = {pid: p for pid, p in photos.items() if "nolocation" in pid.lower()}
    for pid, p in nolocation_photos.items():
        assert p.get("type") in ["screenshot", "document"], f"NoLocation item {pid} has invalid type {p.get('type')}"

def test_facet_counts(index_data):
    facets = get_facet_counts(index_data, {})
    for t, expected_count in facets["type"].items():
        # Apply the filter to see actual matches
        events, matched_photos = apply_filters(index_data, {"type": [t]})
        assert len(matched_photos) == expected_count, f"Facet count for {t} is {expected_count}, but filtering gives {len(matched_photos)}"
