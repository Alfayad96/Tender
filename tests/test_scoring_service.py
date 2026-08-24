import unittest
from datetime import date, timedelta

from app.services.scoring_service import calculate_deadline_score, score_tender


class ScoringRegressionTest(unittest.TestCase):
    def score(self, title, **fields):
        return score_tender({"titel": title, **fields})

    def test_clear_visitor_app_remains_a_match(self):
        result = self.score("Zoo-App mit interaktivem Besucher-Guide")

        self.assertEqual(result["bewertung"], "PASSEND")
        self.assertIn("mobile_app", result["positive_hits"])
        self.assertIn("visitor_experience_apps", result["positive_hits"])

    def test_clear_xr_learning_project_remains_a_match(self):
        result = self.score("Virtual-Reality-Trainingssimulation für interaktives Lernen")

        self.assertEqual(result["bewertung"], "PASSEND")
        self.assertIn("ar_vr_xr", result["positive_hits"])
        self.assertIn("simulation_training", result["positive_hits"])

    def test_web_app_does_not_imply_mobile_app(self):
        result = self.score("Entwicklung einer Web-App für ein Kundenportal")

        self.assertIn("web_app", result["positive_hits"])
        self.assertNotIn("mobile_app", result["positive_hits"])

    def test_relaunch_with_secondary_operations_scope_is_a_match(self):
        result = self.score(
            "Relaunch, Support und Hosting einer Kultur-Website",
            beschreibung_leistung="UX-Redesign und Implementierung des neuen Webauftritts",
        )

        self.assertEqual(result["bewertung"], "PASSEND")
        self.assertNotIn("infrastructure_operations", result["negative_hits"])
        self.assertTrue(
            any("context_penalty_mixed_operations" in reason for reason in result["score_reasons"])
        )

    def test_operations_only_website_is_not_a_match(self):
        result = self.score("Support und Wartung einer bestehenden Website")

        self.assertEqual(result["bewertung"], "NICHT_PASSEND")
        self.assertLess(result["score"], 14)

    def test_negative_enterprise_conflict_needs_minimum_score_for_manual_review(self):
        result = self.score("SAP S/4HANA Portal und ERP-Datenmigration")

        self.assertEqual(result["bewertung"], "NICHT_PASSEND")
        self.assertIn("sap_erp_enterprise", result["negative_hits"])

    def test_vr_building_code_is_not_treated_as_virtual_reality(self):
        result = self.score("MS FHS VR Campus Neubau mit GLT-Aufschaltung")

        self.assertEqual(result["bewertung"], "NICHT_PASSEND")
        self.assertNotIn("ar_vr_xr", result["positive_hits"])
        self.assertIn("construction_facility", result["negative_hits"])

    def test_procurement_word_alone_does_not_imply_hardware(self):
        result = self.score("Beschaffung und Entwicklung einer mobilen App")

        self.assertNotIn("hardware_procurement", result["negative_hits"])
        self.assertIn("mobile_app", result["positive_hits"])

    def test_actual_hardware_procurement_stays_negative(self):
        result = self.score("Lieferung von 500 Laptops und Monitoren")

        self.assertEqual(result["bewertung"], "NICHT_PASSEND")
        self.assertIn("hardware_procurement", result["negative_hits"])

    def test_software_introduction_is_not_consulting_by_itself(self):
        result = self.score("Einführung einer interaktiven Lernsoftware")

        self.assertEqual(result["bewertung"], "PASSEND")
        self.assertNotIn("consulting_only", result["negative_hits"])

    def test_explicit_consulting_stays_negative(self):
        result = self.score("Strategieberatung und Consulting zur Einführung von SAP")

        self.assertEqual(result["bewertung"], "NICHT_PASSEND")
        self.assertIn("consulting_only", result["negative_hits"])
        self.assertIn("sap_erp_enterprise", result["negative_hits"])

    def test_non_actionable_and_hard_statuses_keep_precedence(self):
        awarded = self.score("Entwicklung einer Museum-App", status_detail="Vergebener Auftrag")
        cancelled = self.score("Entwicklung einer Museum-App", status_detail="Aufgehoben")

        self.assertEqual(awarded["bewertung"], "NICHT_AKTIV_BEREITS_VERGEBEN")
        self.assertEqual(cancelled["bewertung"], "NICHT_PASSEND")

    def test_expired_deadline_is_non_actionable(self):
        yesterday = (date.today() - timedelta(days=1)).strftime("%d.%m.%Y")
        today = date.today().strftime("%d.%m.%Y")

        expired = self.score("Entwicklung einer Museum-App", frist=yesterday)
        due_today = self.score("Entwicklung einer Museum-App", frist=today)

        self.assertEqual(expired["bewertung"], "NICHT_AKTIV_BEREITS_VERGEBEN")
        self.assertEqual(expired["non_actionable_reason"], "frist abgelaufen")
        self.assertNotEqual(due_today["bewertung"], "NICHT_AKTIV_BEREITS_VERGEBEN")

    def test_missing_information_is_not_promoted(self):
        result = score_tender({})

        self.assertEqual(result["score"], 0)
        self.assertEqual(result["bewertung"], "NICHT_PASSEND")

    def test_deadline_boundaries_use_calendar_days(self):
        today = date(2026, 8, 24)

        good = {"frist": (today + timedelta(days=21)).strftime("%d.%m.%Y")}
        acceptable = {"frist": (today + timedelta(days=10)).strftime("%d.%m.%Y")}
        neutral = {"frist": (today + timedelta(days=5)).strftime("%d.%m.%Y")}
        bad = {"frist": (today + timedelta(days=4)).strftime("%d.%m.%Y")}

        self.assertEqual(calculate_deadline_score(good, today=today)[0], 12)
        self.assertEqual(calculate_deadline_score(acceptable, today=today)[0], 5)
        self.assertEqual(calculate_deadline_score(neutral, today=today)[0], 0)
        self.assertEqual(calculate_deadline_score(bad, today=today)[0], -25)
        self.assertEqual(good["tage_bis_frist"], 21)


if __name__ == "__main__":
    unittest.main()
