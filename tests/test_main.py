from streamlit.testing.v1 import AppTest
import pytest


@pytest.fixture
def mock_openai(monkeypatch):
    def mockcall(*args, **kwargs):
        return (r for r in ["This ", "is ", "your ", "response."])
    
    monkeypatch.setattr("streamlit.secrets", {"OPENAI_API_KEY": "dummy"})
    monkeypatch.setattr(
        "openai.resources.chat.completions.Completions.create", mockcall
    )


def test_inputdisplay(mock_openai):
    # Enter "hello"
    at = AppTest.from_file("app.py").run()
    at.chat_input[0].set_value("hello").run()
    # Check user input is displayed
    assert at.chat_message[0].children[0].value == "hello"
    # Check response is displayed
    assert at.chat_message[1].children[0].value.startswith("This")
    # Enter "goodbye"
    at.chat_input[0].set_value("goodbye").run()
    # Check new user input is displayed in correct position
    assert at.chat_message[2].children[0].value == "goodbye"
    # Check new response is displayed in correct position
    assert at.chat_message[3].children[0].value.startswith("This")
