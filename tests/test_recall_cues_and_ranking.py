import pytest
import streamlit as st
from unittest.mock import patch, MagicMock
from streamlit.testing.v1 import AppTest
from recall.ai import detail_rerank

# Mock candidate photos for offline ranking test
MOCK_PHOTOS = [
    {
        "id": "2026-10-05_NoLocation/IMG_20261005_001.jpg",
        "caption": "A screenshot of an electricity bill payment confirmation.",
        "objects": ["screenshot", "text", "bill"],
        "clothing_colours": [],
        "text_in_image": "Electricity Bill Payment Successful Amount Paid 2000 INR ID 12345"
    },
    {
        "id": "2026-09-01_NoLocation/IMG_prescription.jpg",
        "caption": "A screenshot of a doctor's prescription.",
        "objects": ["screenshot", "document", "prescription"],
        "clothing_colours": [],
        "text_in_image": "Patient: John Doe, Rx Paracetamol 500mg, Take twice daily"
    },
    {
        "id": "2026-08-15_NoLocation/IMG_boarding_pass.jpg",
        "caption": "A screenshot of a flight boarding pass.",
        "objects": ["screenshot", "boarding pass", "barcode"],
        "clothing_colours": [],
        "text_in_image": "Flight 8A443, Gate 12, Boarding 08:30"
    },
    {
        "id": "2026-07-22_NoLocation/IMG_cab.jpg",
        "caption": "A screenshot of a cab booking.",
        "objects": ["screenshot", "map", "car"],
        "clothing_colours": [],
        "text_in_image": "Your ride is on the way. Driver: Ramesh, Vehicle: MH12AB3456"
    },
    {
        "id": "2026-06-10_NoLocation/IMG_generic_payment.jpg",
        "caption": "A screenshot of a generic payment receipt.",
        "objects": ["screenshot", "payment", "receipt"],
        "clothing_colours": [],
        "text_in_image": "Payment Successful. Amount Paid: 500 INR"
    }
]

@pytest.fixture(autouse=True)
def clear_caches():
    detail_rerank.clear()
    from recall.ai import parse_description
    parse_description.clear()

@patch('recall.ai.st.secrets')
def test_ranking_fallback_electricity_sentence(mock_secrets):
    mock_secrets.get.return_value = None # Force fallback
    detail = "The screenshot of the electricity bill I paid."
    ranked = detail_rerank(MOCK_PHOTOS, detail)
    assert ranked[0] == "2026-10-05_NoLocation/IMG_20261005_001.jpg"

@patch('recall.ai.st.secrets')
def test_ranking_fallback_electricity_word(mock_secrets):
    mock_secrets.get.return_value = None # Force fallback
    detail = "electricity"
    ranked = detail_rerank(MOCK_PHOTOS, detail)
    assert ranked[0] == "2026-10-05_NoLocation/IMG_20261005_001.jpg"

@patch('recall.ai.requests.post')
@patch('recall.ai.st.secrets')
def test_ranking_valid_gemini_response(mock_secrets, mock_post):
    mock_secrets.get.return_value = "fake_key"
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "candidates": [{
            "content": {
                "parts": [{
                    "text": '[{"id": "2026-10-05_NoLocation/IMG_20261005_001.jpg", "score": 0.99}, {"id": "2026-06-10_NoLocation/IMG_generic_payment.jpg", "score": 0.5}]'
                }]
            }
        }]
    }
    mock_post.return_value = mock_response
    ranked = detail_rerank(MOCK_PHOTOS, "electricity")
    assert ranked[0] == "2026-10-05_NoLocation/IMG_20261005_001.jpg"
    assert "2026-06-10_NoLocation/IMG_generic_payment.jpg" in ranked
    assert len(ranked) == 2

@patch('recall.ai.requests.post')
@patch('recall.ai.st.secrets')
def test_ranking_malformed_response(mock_secrets, mock_post):
    mock_secrets.get.return_value = "fake_key"
    mock_response = MagicMock()
    mock_response.status_code = 200
    # Malformed JSON (not a list, duplicate ids, missing score)
    mock_response.json.return_value = {
        "candidates": [{
            "content": {
                "parts": [{
                    "text": '{"id": "unknown_id"}'
                }]
            }
        }]
    }
    mock_post.return_value = mock_response
    ranked = detail_rerank(MOCK_PHOTOS, "electricity")
    # Should fallback cleanly if malformed, or return nothing if it parses but has no valid scores
    # Wait, if it parses as dict, the code says "if isinstance(res, list):", so it falls through to fallback!
    assert ranked[0] == "2026-10-05_NoLocation/IMG_20261005_001.jpg"

@patch('recall.ai.requests.post')
@patch('recall.ai.st.secrets')
def test_ranking_invalid_ids_and_duplicates(mock_secrets, mock_post):
    mock_secrets.get.return_value = "fake_key"
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "candidates": [{
            "content": {
                "parts": [{
                    "text": '[{"id": "2026-10-05_NoLocation/IMG_20261005_001.jpg", "score": 0.9}, {"id": "unknown_id", "score": 0.8}, {"id": "2026-10-05_NoLocation/IMG_20261005_001.jpg", "score": 0.7}]'
                }]
            }
        }]
    }
    mock_post.return_value = mock_response
    ranked = detail_rerank(MOCK_PHOTOS, "electricity")
    assert "unknown_id" not in ranked
    assert ranked.count("2026-10-05_NoLocation/IMG_20261005_001.jpg") == 1

# Regression test for describe it date preservation
@patch('recall.ai.requests.post')
@patch('recall.ai.st.secrets')
def test_describe_it_preserves_date_filter(mock_secrets, mock_post):
    mock_secrets.get.return_value = "fake_key"
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "candidates": [{
            "content": {
                "parts": [{
                    "text": '{"chapters": [], "who": ["Brother"], "where": [], "what": [], "type": [], "anything_else": "medal"}'
                }]
            }
        }]
    }
    mock_post.return_value = mock_response
    
    at = AppTest.from_file("../app.py").run()
    
    # 1. Start fresh task
    at.selectbox(key="sb_participant").select("Guest").run()
    at.selectbox(key="sb_task").select("Task 2").run()
    for b in at.button:
        if b.label == "▶ Start task":
            b.click().run()
            break
    
    # 2. Open Help me remember
    at.button(key="btn_help_remember_main").click().run()
    
    # 3. Enter 'before COVID' in Era
    at.text_input(key="era_box").input("before COVID").run()
    at.button(key="btn_parse_era").click().run()
    
    # Verify date range was set
    assert at.session_state['filters'].get('date_range') == ("1990-01-01", "2020-03-15")
    
    # 4. Describe it
    at.text_area(key="desc_input_box").input("My little brother with his school medal, sometime before COVID.").run()
    for b in at.button:
        if b.label == "Parse cues & auto-fill":
            b.click().run()
            break
    
    # 5. Verify date range survived
    assert at.session_state['filters'].get('date_range') == ("1990-01-01", "2020-03-15")
    assert at.session_state['filters'].get('era_chip') is not None

from recall.index import load_index

@patch('recall.ai.st.secrets')
def test_real_index_electricity_bill_fallback(mock_secrets):
    mock_secrets.get.return_value = None
    real_index = load_index()
    real_photos = list(real_index['photos'].values())
    
    # Verify metadata is correct in real index
    target_photo = next((p for p in real_photos if p['id'] == '2026-10-05_NoLocation/IMG_20261005_001.jpg'), None)
    assert target_photo is not None
    assert "payment" in target_photo.get('text_in_image', '').lower()
    
    unrelated_photo = next((p for p in real_photos if p['id'] == '2026-10-05_NoLocation/IMG_20261005_002.jpg'), None)
    assert unrelated_photo is not None
    assert "electricity" not in unrelated_photo.get('text_in_image', '').lower()
    
    # 1. "The screenshot of the electricity bill I paid."
    ranked1 = detail_rerank(real_photos, "The screenshot of the electricity bill I paid.")
    assert ranked1[0] == "2026-10-05_NoLocation/IMG_20261005_001.jpg"
    
    # 2. "electricity" places genuine records ahead
    ranked2 = detail_rerank(real_photos, "electricity")
    # Could be either bill_screenshot.jpg or IMG_20261005_001.jpg in top positions
    top_ids = ranked2[:2]
    assert "2026-10-05_NoLocation/IMG_20261005_001.jpg" in top_ids
    assert "bill_screenshot.jpg" in top_ids

def test_generator_preserves_curated_labels():
    import os, subprocess
    os.makedirs('scratch/test_gen/library', exist_ok=True)
    with open('scratch/test_gen/library/manifest.csv', 'w') as f:
        f.write('filename\n')
        f.write('2026-10-05_NoLocation/IMG_20261005_001.jpg\n')
        f.write('2026-10-05_NoLocation/IMG_20261005_002.jpg\n')
        f.write('2026-06-14_NoLocation/unknown_screenshot.jpg\n')
    
    with open('scratch/test_gen/library/photo_labels.csv', 'w') as f:
        f.write('filename,caption,objects,clothing,text_in_image\n')
        f.write('2026-10-05_NoLocation/IMG_20261005_001.jpg,Curated Caption,obj,cloth,Curated Text\n')
    
    with open('scripts/generate_labels.py', 'r') as src:
        script = src.read()
    
    with open('scratch/test_gen/gen.py', 'w') as dst:
        dst.write(script)
    
    subprocess.run(['python', 'gen.py'], cwd='scratch/test_gen', check=True)
    
    with open('scratch/test_gen/library/photo_labels.csv', 'r') as f:
        content = f.read()
    
    assert 'Curated Caption' in content
    assert 'Curated Text' in content
    assert 'Screenshot of a meme or chat,,,' in content # Unknown screenshot has neutral description and no OCR

