import unittest

from app.gui.presentation import (
    display_deadline,
    display_items,
    first_display_value,
    has_display_value,
)


class PresentationHelpersTest(unittest.TestCase):
    def test_missing_values_are_hidden(self):
        missing_values = [
            None,
            "",
            "   ",
            "-",
            "—",
            "/",
            "N/A",
            "n/a",
            "nv",
            "N.V.",
            "nicht vorhanden",
            "Nicht verfügbar",
            "null",
            "undefined",
            [],
            {},
        ]

        for value in missing_values:
            with self.subTest(value=value):
                self.assertFalse(has_display_value(value))

    def test_zero_and_false_remain_visible(self):
        self.assertTrue(has_display_value(0))
        self.assertTrue(has_display_value(0.0))
        self.assertTrue(has_display_value(False))

    def test_first_display_value_skips_placeholders(self):
        self.assertEqual(first_display_value(None, "—", "05.09.2026"), "05.09.2026")
        self.assertIsNone(first_display_value(None, " ", "N/A"))

    def test_display_items_removes_empty_entries(self):
        self.assertEqual(display_items(["mobile_app", " ", None, "N/A"]), ["mobile_app"])
        self.assertEqual(display_items(None), [])

    def test_notice_type_labels_are_not_rendered_as_deadlines(self):
        self.assertIsNone(display_deadline("Ergebnis"))
        self.assertIsNone(display_deadline("Frühere Bekanntmachung zu diesem Verfahren"))
        self.assertEqual(display_deadline("05.09.2026"), "05.09.2026")
        self.assertEqual(display_deadline("Ergebnis", "05.09.2026"), "05.09.2026")


if __name__ == "__main__":
    unittest.main()
