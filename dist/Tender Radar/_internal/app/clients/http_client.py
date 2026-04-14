import requests


class HttpClient:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0"
        }
        self.timeout = 10

    def fetch_page(self, url: str):
        try:
            response = requests.get(
                url,
                headers=self.headers,
                timeout=self.timeout
            )
            response.raise_for_status()

            return {
                "success": True,
                "html": response.text,
                "final_url": response.url,
                "status_code": response.status_code,
                "error": None
            }

        except requests.exceptions.HTTPError as e:
            response = e.response
            return {
                "success": False,
                "html": None,
                "final_url": response.url if response else url,
                "status_code": response.status_code if response else None,
                "error": str(e)
            }

        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "html": None,
                "final_url": url,
                "status_code": None,
                "error": str(e)
            }