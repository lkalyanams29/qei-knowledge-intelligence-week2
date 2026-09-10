"""Streamlit's simulated application tests; not browser/screenshot QA."""
import unittest
from pathlib import Path
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]


class StreamlitTests(unittest.TestCase):
    def test_answer_and_rerun_preserve_results(self):
        app = AppTest.from_file(str(ROOT/"ui.py"), default_timeout=60).run()
        self.assertFalse(app.exception)
        example = "Which execution outcome is linked to SYN-BSP-REQ-001?"
        app.selectbox(key="example").set_value(example).run()
        next(b for b in app.button if b.label == "Use example").click().run()
        self.assertEqual(app.text_area(key="question").value, example)
        submit = next(b for b in app.button if b.label == "Ask QE")
        submit.click().run()
        self.assertFalse(app.exception)
        result = app.session_state["results"]["graph"]
        self.assertTrue(result["evidence"])
        highlight = next(c for c in app.checkbox if c.label == "Highlight last retrieved evidence")
        highlight.set_value(False).run()
        self.assertFalse(app.exception)
        self.assertEqual(app.session_state["results"]["graph"]["question"], result["question"])

    def test_project_filter_does_not_grant_access(self):
        app = AppTest.from_file(str(ROOT/"ui.py"), default_timeout=60).run()
        app.selectbox(key="project").set_value("Salesforce").run()
        app.text_area(key="question").set_value("Show SYN-BSP-REQ-001")
        next(b for b in app.button if b.label == "Ask QE").click().run()
        self.assertEqual(app.session_state["results"]["graph"]["status"], "INSUFFICIENT_EVIDENCE")
        self.assertFalse(app.exception)


if __name__ == "__main__":
    unittest.main()
