from bs4 import BeautifulSoup


def parse_verfahrensangaben_page(html: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    page_text = soup.get_text("\n", strip=True)

    result = {
        "vergabeordnung": None,
        "vergabeart_detail": None,
        "status_detail": None,
        "frist_aufklaerungsfragen": None,
        "teilnahmefrist": None,
        "auftraggeber_name": None,
    }

    lines = [line.strip() for line in page_text.split("\n") if line.strip()]

    for i, line in enumerate(lines):
        if line == "VO:" and i + 1 < len(lines):
            result["vergabeordnung"] = lines[i + 1]

        elif line == "Vergabeart:" and i + 1 < len(lines):
            result["vergabeart_detail"] = lines[i + 1]

        elif line == "Status:" and i + 1 < len(lines):
            result["status_detail"] = lines[i + 1]

        elif "Frist zur Einreichung von Aufklärungsfragen" in line and i + 1 < len(lines):
            result["frist_aufklaerungsfragen"] = lines[i + 1]

        elif "Teilnahmefrist" in line and i + 1 < len(lines):
            result["teilnahmefrist"] = lines[i + 1]

        elif "Offizielle Bezeichnung" in line and i + 1 < len(lines):
            result["auftraggeber_name"] = lines[i + 1]

    return result