import unittest
from pathlib import Path

from streamlit.testing.v1 import AppTest


class StreamlitFrontendTest(unittest.TestCase):
    def test_card_hides_missing_fields_and_preserves_zero_score(self):
        app_path = Path(__file__).parents[1] / "app" / "gui" / "streamlit_app.py"
        app = AppTest.from_file(str(app_path), default_timeout=20)
        app.session_state["logged_in"] = True
        app.session_state["daten_geladen"] = True
        app.session_state["has_current_run_results"] = True
        app.session_state["scan_running"] = False
        app.session_state["analyse_running"] = False
        app.session_state["scan_done_message"] = ""
        app.session_state["analyse_done_message"] = ""
        app.session_state["passende"] = [
            {
                "titel": "Testausschreibung mit langem Titel für responsive Prüfungen",
                "score": 0,
                "bewertung": "PASSEND",
                "auftraggeber": "Beispielstadt",
                "frist": "N/A",
                "ausschreibungs_id": "—",
                "vergabe_nr": None,
                "ort": "/",
                "veroeffentlichung": "24.08.2026",
                "vergabeart": "Offenes Verfahren",
                "auftragsgegenstand_detail": "72000000-5",
                "positive_hits": [],
                "negative_hits": ["N/A"],
                "score_reasons": ["0 neutraler Testwert"],
                "final_detail_url": "https://example.com/tender",
            }
        ]
        app.session_state["manuell"] = []
        app.session_state["nicht_aktiv"] = []
        app.session_state["nicht_passend"] = []

        app.run()

        self.assertFalse(app.exception)
        rendered_text = " ".join(element.value for element in app.markdown)
        for hidden_text in ["Frist", "Ausschreibungs-ID", "Vergabe-Nr.", "Ort", "N/A", "—"]:
            with self.subTest(hidden_text=hidden_text):
                self.assertNotIn(hidden_text, rendered_text)
        self.assertTrue(any(metric.value == "0" for metric in app.metric))


if __name__ == "__main__":
    unittest.main()
