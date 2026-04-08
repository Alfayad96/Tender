from bs4 import BeautifulSoup
from urllib.parse import urljoin


def _clean_text(text: str | None) -> str | None:
    if not text:
        return None
    cleaned = " ".join(text.split())
    return cleaned if cleaned else None


def _extract_label_value_pairs(soup: BeautifulSoup) -> dict:
    data = {}

    rows = soup.find_all("tr")
    for row in rows:
        cells = row.find_all(["td", "th"])
        if len(cells) >= 2:
            key = _clean_text(cells[0].get_text(" ", strip=True))
            value = _clean_text(cells[1].get_text(" ", strip=True))
            if key and value:
                data[key] = value

    # Fallback für Seiten mit div-/span-Struktur
    texts = [_clean_text(x.get_text(" ", strip=True)) for x in soup.find_all(["div", "span", "p", "td", "th"])]
    texts = [t for t in texts if t]

    for i in range(len(texts) - 1):
        key = texts[i]
        value = texts[i + 1]
        if key.endswith(":") and value:
            data[key.rstrip(":")] = value

    return data


def parse_detail_page(html: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    page_text = soup.get_text("\n", strip=True)
    pairs = _extract_label_value_pairs(soup)

    result = {
        # bisherige Felder
        "ausschreibungs_id": None,
        "auftraggeber_detail": None,
        "abgabefrist_detail": None,
        "auftragsgegenstand_detail": None,

        # neue Felder
        "vergabe_nr": None,
        "stelle_bezeichnung": None,
        "nationale_identifikationsnummer": None,
        "postanschrift": None,
        "ort": None,
        "postleitzahl": None,
        "land": None,
        "leistung_bezeichnung": None,
        "art_der_leistung": None,
        "beschreibung_leistung": None,
        "hauptleistungsort_postleitzahl": None,
        "angebots_teilnahmefrist": None,
        "auftragsgegenstand_code": None,
        "auftragsgegenstand_text": None,
        "bekanntmachungs_id": None,
        "veroeffentlicher": None,
        "externe_info_url": None,
        "sonstige_angaben": None,
    }

    # Kopfbereich
    if "Vergabe-Nr.:" in page_text:
        idx = page_text.find("Vergabe-Nr.:")
        snippet = page_text[idx:idx + 200].split("\n")
        for line in snippet:
            if "Vergabe-Nr.:" in line:
                parts = line.split("Vergabe-Nr.:")
                if len(parts) > 1:
                    result["vergabe_nr"] = _clean_text(parts[1])
                    break

    # Bestehende Felder
    if "Ausschreibungs-ID" in page_text:
        idx = page_text.find("Ausschreibungs-ID")
        snippet = page_text[idx:idx + 300].split("\n")
        if len(snippet) > 1:
            result["ausschreibungs_id"] = _clean_text(snippet[1])

    result["auftraggeber_detail"] = (
        pairs.get("Bezeichnung")
        or pairs.get("Auftraggeber / Ausschreibende Stelle")
        or result["auftraggeber_detail"]
    )

    result["abgabefrist_detail"] = (
        pairs.get("Abgabefrist")
        or pairs.get("Angebots- / Teilnahmefrist")
        or pairs.get("Angebots-/ Teilnahmefrist")
        or pairs.get("Angebots-/Teilnahmefrist")
    )

    # Neue Felder direkt aus Label-Value-Struktur
    result["stelle_bezeichnung"] = pairs.get("Bezeichnung")
    result["nationale_identifikationsnummer"] = pairs.get("Nationale Identifikationsnummer")
    result["postanschrift"] = pairs.get("Postanschrift")
    result["ort"] = pairs.get("Ort")
    result["postleitzahl"] = pairs.get("Postleitzahl")
    result["land"] = pairs.get("Land")

    result["leistung_bezeichnung"] = pairs.get("Bezeichnung")
    result["art_der_leistung"] = pairs.get("Art der Leistung")
    result["beschreibung_leistung"] = pairs.get("Beschreibung")

    result["hauptleistungsort_postleitzahl"] = pairs.get("Postleitzahl")
    result["angebots_teilnahmefrist"] = (
        pairs.get("Angebots- / Teilnahmefrist")
        or pairs.get("Angebots-/ Teilnahmefrist")
        or pairs.get("Angebots-/Teilnahmefrist")
    )

    result["bekanntmachungs_id"] = pairs.get("Bekanntmachungs-ID")
    result["veroeffentlicher"] = pairs.get("Vergabeplattform / Veröffentlichter")
    result["sonstige_angaben"] = pairs.get("Sonstige Angaben")

    # Link zu weiteren Informationen
    link = soup.find("a", string=lambda text: text and "Adresse im neuen Fenster öffnen" in text)
    if link and link.has_attr("href"):
        result["externe_info_url"] = link["href"]

    # Auftragsgegenstand robuster lesen
    if "Auftragsgegenstand" in page_text:
        idx = page_text.find("Auftragsgegenstand")
        snippet = page_text[idx:idx + 500].split("\n")
        lines = [_clean_text(line) for line in snippet[1:] if _clean_text(line)]
        if lines:
            result["auftragsgegenstand_detail"] = lines[0]

            first_line = lines[0]
            if " " in first_line:
                first_part, rest = first_line.split(" ", 1)
                result["auftragsgegenstand_code"] = _clean_text(first_part)
                result["auftragsgegenstand_text"] = _clean_text(rest)
            else:
                result["auftragsgegenstand_code"] = first_line

    return result


def find_verfahrensangaben_url(detail_html: str, current_url: str) -> str | None:
    soup = BeautifulSoup(detail_html, "html.parser")

    link = soup.find("a", string=lambda text: text and "Verfahrensangaben" in text)

    if not link or not link.has_attr("href"):
        return None

    return urljoin(current_url, link["href"])