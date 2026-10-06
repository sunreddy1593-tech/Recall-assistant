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
