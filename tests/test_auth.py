import os
import unittest
from unittest.mock import patch

from app.gui.streamlit_app import credentials_match, login_credentials


class AuthenticationConfigurationTest(unittest.TestCase):
    def test_credentials_are_loaded_from_server_environment(self):
        configured = {
            "TENDER_RADAR_USERNAME": "configured-user",
            "TENDER_RADAR_PASSWORD": "configured-password",
        }

        with patch.dict(os.environ, configured, clear=False):
            self.assertEqual(login_credentials(), tuple(configured.values()))
            self.assertTrue(credentials_match(*configured.values()))
            self.assertFalse(credentials_match("configured-user", "wrong-password"))
            self.assertFalse(credentials_match("wrong-user", "configured-password"))

    def test_missing_server_configuration_never_authenticates(self):
        with patch.dict(os.environ, {}, clear=True):
            self.assertEqual(login_credentials(), ("", ""))
            self.assertFalse(credentials_match("any-user", "any-password"))


if __name__ == "__main__":
    unittest.main()
