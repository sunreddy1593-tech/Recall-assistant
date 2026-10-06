from streamlit.testing.v1 import AppTest
from unittest.mock import patch
import pytest

@patch('recall.logging_utils.requests.post')
def test_task_instruction_visible(mock_post):
    at = AppTest.from_file("../app.py").run()
    assert "Task preview \u2014 press Start task to begin." in at.markdown[2].value
    
    # Start task S1
    at.sidebar.selectbox("sb_participant").set_value("P1")
    at.sidebar.selectbox("sb_task").set_value("Task 1")
    at.sidebar.button[0].click().run()
    
    assert "Current task." in at.markdown[2].value
    assert "When you lived in Scotland, there is a photo of you crouched on the floor at home wearing a face mask. Find it." in at.markdown[2].value

@patch('recall.logging_utils.requests.post')
def test_facet_replacing_and_skipping(mock_post):
    at = AppTest.from_file("../app.py").run()
    at.sidebar.selectbox("sb_task").set_value("Task 1")
    at.sidebar.button[0].click().run()
    
    at.button("btn_help_remember_main").click().run()
    
    # Select a chapter
    at.pills("pills_q1_chaps").set_value(["College (42)"]).run()
    at.button("btn_q1_next").click().run()
    
    # Now in step 2. Go back.
    at.button("back_to_1").click().run()
    
    # Deselect the chapter, select a year instead
    at.pills("pills_q1_chaps").set_value([]).run()
    years_opts = at.pills("pills_q1_years").options
    at.pills("pills_q1_years").set_value([years_opts[0]]).run()
    at.button("btn_q1_next").click().run()
    
    # Verify filters
    assert 'chapters' not in at.session_state['filters']
    assert 'years' in at.session_state['filters']
    assert len(at.session_state['filters']['years']) > 0

@patch('recall.logging_utils.requests.post')
def test_pending_reset_boundaries(mock_post):
    at = AppTest.from_file("../app.py").run()
    at.sidebar.button[0].click().run()
    
    # Set some query
    at.text_input("photoSearchInput").input("test query").run()
    assert at.session_state['search_retries'] == 1
    
    # Rerun should not increment search_retries if query is unchanged
    at.run()
    assert at.session_state['search_retries'] == 1
    
    # Start task resets widgets
    at.sidebar.button[0].click().run()
    
    # Search input should be cleared
    assert 'photoSearchInput' not in at.session_state or at.session_state['photoSearchInput'] == ''

@patch('recall.logging_utils.requests.post')
def test_reject_all_suggestions(mock_post):
    at = AppTest.from_file("../app.py").run()
    at.sidebar.button[0].click().run()
    at.button("btn_help_remember_main").click().run()
    
    # Skip to end
    at.button("btn_q1_next").click().run()
    at.button("btn_q2_next").click().run()
    at.button("btn_q3_next").click().run()
    at.button("btn_q4_show_results").click().run()
    
    # Click None of these photos
    at.button("btn_reject_all_results").click().run()
    
    assert at.session_state['help_step'] == 1
    assert "Let's try different clues" in at.info[0].value

from recall.ui import render_moment_card
from unittest.mock import MagicMock

def test_moment_card_rendering():
    event_empty_people = {
        "id": "e1",
        "start": "2024-10-14T10:00:00Z",
        "people": [],
        "place": "Dublin & Co",
        "event_label": "Test <Event>",
        "photo_ids": ["p1", "p2"]
    }
    event_named_people = {
        "id": "e2",
        "start": "2024-10-14T10:00:00Z",
        "people": ["Tom <Smith>", "Alice & Bob"],
        "place": "Dublin",
        "event_label": "Test",
        "photo_ids": ["p1", "p2"]
    }
    
    with patch('recall.ui.st') as mock_st:
        mock_st.columns.side_effect = lambda x: [MagicMock() for _ in range(x)] if isinstance(x, int) else [MagicMock() for _ in x]
        
        render_moment_card(event_empty_people, 0)
        calls = mock_st.markdown.call_args_list
        html_content = calls[0][0][0]
        
        assert "Just me" in html_content
        assert "&lt;Event&gt;" in html_content
        assert "Dublin &amp; Co" in html_content
        assert "\n    " not in html_content
        
        mock_st.markdown.reset_mock()
        render_moment_card(event_named_people, 1)
        calls = mock_st.markdown.call_args_list
        html_content = calls[0][0][0]
        
        assert "Tom &lt;Smith&gt;" in html_content
        assert 'title="Tom &lt;Smith&gt;"' in html_content

@patch('recall.logging_utils.requests.post')
def test_when_step_skip_clears_time(mock_post):
    at = AppTest.from_file("../app.py").run()
    at.sidebar.button[0].click().run()
    at.button("btn_help_remember_main").click().run()
    
    years_opts = at.pills("pills_q1_years").options
    at.pills("pills_q1_years").set_value([years_opts[0]]).run()
    at.button("btn_q1_next").click().run()
    
    assert 'years' in at.session_state['filters']
    
    at.button("back_to_1").click().run()
    assert 'years' in at.session_state['filters']
    
    at.button("btn_q1_next").click().run()
    assert 'years' in at.session_state['filters']
    
    at.button("back_to_1").click().run()
    at.button("btn_skip_1").click().run()
    
    assert 'years' not in at.session_state['filters']
    assert 'chapters' not in at.session_state['filters']
    
    at.button("back_to_1").click().run()
    assert 'pills_q1_years' not in at.session_state or not at.session_state['pills_q1_years']

@patch('recall.logging_utils.requests.post')
def test_when_step_not_sure_clears_time(mock_post):
    at = AppTest.from_file("../app.py").run()
    at.sidebar.button[0].click().run()
    at.button("btn_help_remember_main").click().run()
    
    at.text_input("era_box").input("college").run()
    at.session_state['filters']['date_range'] = ("2019", "2020")
    at.session_state['filters']['era_chip'] = "Parsed"
    
    at.button("btn_q1_next").click().run()
    at.button("back_to_1").click().run()
    
    at.button("btn_not_sure_1").click().run()
    
    assert 'date_range' not in at.session_state['filters']
    assert 'era_chip' not in at.session_state['filters']
    
    at.button("back_to_1").click().run()
    assert 'era_box' not in at.session_state or not at.session_state['era_box']

@patch('recall.logging_utils.requests.post')
def test_bug1_search_rejection_exclusion_and_state(mock_post):
    at = AppTest.from_file("../app.py").run()
    at.sidebar.button[0].click().run()
    
    at.text_input("photoSearchInput").input("scotland").run()
    
    matched_keys = [k for k in at.button if k.key and k.key.startswith("srch_view_")]
    if not matched_keys: return # skip if no data
    first_pid = matched_keys[0].key.replace("srch_view_", "")
    
    matched_keys[0].click().run()
    at.button(f"reject_focus_{first_pid}").click().run()
    
    if at.session_state['viewing_event']:
        at.button("btn_back_to_results").click().run()
        
    assert at.text_input("photoSearchInput").value == "scotland"
    
    new_matched_keys = [k for k in at.button if k.key and k.key.startswith("srch_view_")]
    assert first_pid not in [k.key.replace("srch_view_", "") for k in new_matched_keys]
    
    at.text_input("photoSearchInput").input("").run()
    assert len([k for k in at.button if k.key and k.key.startswith("srch_view_")]) == 0


@patch('recall.logging_utils.requests.post')
def test_bug2_pagination(mock_post):
    at = AppTest.from_file("../app.py").run()
    at.sidebar.button[0].click().run()
    
    at.text_input("photoSearchInput").input("e").run()
    
    buttons = [k for k in at.button if k.key and k.key.startswith("srch_view_")]
    assert len(buttons) <= 4
    
    show_more = [b for b in at.button if b.label == "Show more"]
    if show_more:
        show_more[0].click().run()
        buttons_page_2 = [k for k in at.button if k.key and k.key.startswith("srch_view_")]
        assert len(buttons_page_2) > len(buttons)
        assert len(buttons_page_2) <= 8


@patch('recall.logging_utils.requests.post')
def test_bug3_raw_html_zero_results(mock_post):
    at = AppTest.from_file("../app.py").run()
    at.sidebar.button[0].click().run()
    
    at.text_input("photoSearchInput").input("zzzznomatchtest").run()
    
    rendered_md = [m.value for m in at.markdown]
    has_zero_results = any("0 photos found" in m for m in rendered_md)
    assert has_zero_results
    
    for m in rendered_md:
        if "0 photos found" in m:
            assert "\n" not in m
            assert "    </div>" not in m
