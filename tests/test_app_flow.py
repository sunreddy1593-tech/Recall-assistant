import pytest
from streamlit.testing.v1 import AppTest

def test_app_flow():
    at = AppTest.from_file("../app.py", default_timeout=30)
    at.run()
    assert not at.exception
    
    # Check sidebar is available and set task
    at.sidebar.selectbox[1].set_value("Task 1").run()
    assert not at.exception
    
    # Start task
    at.sidebar.button[0].click().run()
    assert not at.exception
    
    # Click Help me remember to enter Guided mode
    help_btns = [b for b in at.button if "Help me remember" in b.label]
    assert len(help_btns) > 0, "Help me remember button not found"
    help_btns[0].click().run()
    assert not at.exception
    
    # Ensure Describe It is available
    assert len(at.text_area) > 0, "Describe It text area not found"
    
    at.text_area[0].set_value("college chai break outside campus").run()
    assert not at.exception
    
    # Click "Parse cues & auto-fill" button
    parse_buttons = [btn for btn in at.button if btn.label == "Parse cues & auto-fill"]
    assert len(parse_buttons) > 0, "Parse cues button not found"
    parse_buttons[0].click().run()
    
    assert not at.exception
    
    # Verify that the success text or matching moments are shown
    assert any("MATCHING MOMENTS" in str(md.value) for md in at.markdown) or any("RECALL RESULTS" in str(md.value) for md in at.markdown), "Recall results not shown"
