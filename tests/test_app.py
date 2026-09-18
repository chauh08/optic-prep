from streamlit.testing.v1 import AppTest


def test_streamlit_setup_smoke():
    app = AppTest.from_file("app.py").run(timeout=15)
    assert not app.exception
    assert app.title[0].value == "Set the focus. Test the fundamentals."
    assert app.button[0].label == "Start practice →"


def test_curated_quiz_can_start_and_answer():
    app = AppTest.from_file("app.py").run(timeout=15)
    app.button[0].click().run(timeout=15)
    assert not app.exception
    assert any("Question 1 of" in markdown.value for markdown in app.markdown)
    app.radio[0].set_value(0).run(timeout=15)
    submit = next(button for button in app.button if button.label == "Submit answer")
    submit.click().run(timeout=15)
    assert not app.exception
    assert app.success or app.error
