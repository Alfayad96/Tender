import re
import os
import json

from app.clients.http_client import HttpClient
from app.parser.list_parser import parse_list_page
from app.parser.detail_parser import parse_detail_page, find_verfahrensangaben_url
from app.parser.verfahrens_parser import parse_verfahrensangaben_page


def detailseite_hat_mindestdaten(detail_daten: dict) -> bool:
    return any([
        detail_daten.get("ausschreibungs_id"),
        detail_daten.get("auftraggeber_detail"),
        detail_daten.get("abgabefrist_detail"),
        detail_daten.get("auftragsgegenstand_detail"),
    ])


def main():
    base_url = "https://www.evergabe.nrw.de/VMPCenter/company/announcements/categoryOverview.do?method=showTable&cpvCode=72000000-5&fromSearch=1&selectedTablePagePROJECT_RESULT={}"

    client = HttpClient()
    os.makedirs("data/processed", exist_ok=True)

    first_page_result = client.fetch_page(base_url.format(1))

    if not first_page_result["success"]:
        print("Fehler beim Laden der ersten Seite")
        print(first_page_result["error"])
        return

    first_page_html = first_page_result["html"]

    match = re.search(r"Seite:\s*\d+\s*von\s*(\d+)", first_page_html)
    if not match:
        print("Gesamtseitenzahl konnte nicht gefunden werden")
        return

    letzte_seite = int(match.group(1))
    print(f"Gesamtseiten: {letzte_seite}")

    alle_ausschreibungen = []

    for page in range(1, letzte_seite + 1):
        print(f"Lade und parse Seite {page}...")

        result = client.fetch_page(base_url.format(page))

        if not result["success"]:
            print(f"  -> Seite {page} konnte nicht geladen werden.")
            continue

        html = result["html"]
        eintraege = parse_list_page(html)
        print(f"  -> {len(eintraege)} Einträge gefunden")
        alle_ausschreibungen.extend(eintraege)

    print(f"\nGesamtzahl aller geladenen Ausschreibungen aus der Liste: {len(alle_ausschreibungen)}")

    erfolgreiche = []
    teilweise_brauchbar = []
    ausgeschlossene = []

    for index, ausschreibung in enumerate(alle_ausschreibungen, start=1):
        print(f"\n[{index}/{len(alle_ausschreibungen)}] Verarbeite Ausschreibung:")
        print(f"Titel: {ausschreibung.get('titel')}")

        detail_url = ausschreibung.get("detail_url")

        if not detail_url:
            ausgeschlossene.append({
                "titel": ausschreibung.get("titel"),
                "detail_url": None,
                "final_detail_url": None,
                "verfahrensangaben_url": None,
                "status_code": None,
                "grund": "Kein Detail-Link vorhanden",
                "error": None
            })
            print("  -> Kein Detail-Link vorhanden.")
            continue

        # Detailseite laden
        detail_result = client.fetch_page(detail_url)

        if not detail_result["success"]:
            ausgeschlossene.append({
                "titel": ausschreibung.get("titel"),
                "detail_url": detail_url,
                "final_detail_url": detail_result["final_url"],
                "verfahrensangaben_url": None,
                "status_code": detail_result["status_code"],
                "grund": "Detailseite nicht ladbar",
                "error": detail_result["error"]
            })
            print(f"  -> Detailseite Fehler: {detail_result['status_code']} | {detail_result['error']}")
            continue

        detail_html = detail_result["html"]
        final_detail_url = detail_result["final_url"]
        detail_daten = parse_detail_page(detail_html)

        verfahrensangaben_url = find_verfahrensangaben_url(detail_html, final_detail_url)

        # Fall: Verfahrensangaben-Link fehlt
        if not verfahrensangaben_url:
            if detailseite_hat_mindestdaten(detail_daten):
                datensatz = {
                    **ausschreibung,
                    **detail_daten,
                    "final_detail_url": final_detail_url,
                    "verfahrensangaben_url": None,
                    "final_verfahrensangaben_url": None,
                    "verarbeitung_status": "teilweise_brauchbar",
                    "hinweis": "Verfahrensangaben-Link fehlt, aber Detailseite enthält Mindestdaten"
                }
                teilweise_brauchbar.append(datensatz)
                print("  -> Verfahrensangaben-Link fehlt, aber Detailseite ist brauchbar.")
            else:
                ausgeschlossene.append({
                    "titel": ausschreibung.get("titel"),
                    "detail_url": detail_url,
                    "final_detail_url": final_detail_url,
                    "verfahrensangaben_url": None,
                    "status_code": None,
                    "grund": "Verfahrensangaben-Link fehlt und Detailseite hat zu wenige Daten",
                    "error": None
                })
                print("  -> Verfahrensangaben-Link fehlt und Detailseite reicht nicht aus.")
            continue

        # Verfahrensangaben laden
        verfahrens_result = client.fetch_page(verfahrensangaben_url)

        if not verfahrens_result["success"]:
            if detailseite_hat_mindestdaten(detail_daten):
                datensatz = {
                    **ausschreibung,
                    **detail_daten,
                    "final_detail_url": final_detail_url,
                    "verfahrensangaben_url": verfahrensangaben_url,
                    "final_verfahrensangaben_url": verfahrens_result["final_url"],
                    "verarbeitung_status": "teilweise_brauchbar",
                    "hinweis": "Verfahrensangaben nicht ladbar, aber Detailseite enthält Mindestdaten",
                    "verfahrens_status_code": verfahrens_result["status_code"],
                    "verfahrens_error": verfahrens_result["error"]
                }
                teilweise_brauchbar.append(datensatz)
                print(f"  -> Verfahrensangaben Fehler: {verfahrens_result['status_code']} | trotzdem brauchbar.")
            else:
                ausgeschlossene.append({
                    "titel": ausschreibung.get("titel"),
                    "detail_url": detail_url,
                    "final_detail_url": final_detail_url,
                    "verfahrensangaben_url": verfahrensangaben_url,
                    "status_code": verfahrens_result["status_code"],
                    "grund": "Verfahrensangaben nicht ladbar und Detailseite reicht nicht aus",
                    "error": verfahrens_result["error"]
                })
                print(f"  -> Verfahrensangaben Fehler: {verfahrens_result['status_code']} | ausgeschlossen.")
            continue

        verfahrens_html = verfahrens_result["html"]
        final_verfahrens_url = verfahrens_result["final_url"]
        verfahrens_daten = parse_verfahrensangaben_page(verfahrens_html)

        kompletter_datensatz = {
            **ausschreibung,
            **detail_daten,
            **verfahrens_daten,
            "final_detail_url": final_detail_url,
            "verfahrensangaben_url": verfahrensangaben_url,
            "final_verfahrensangaben_url": final_verfahrens_url,
            "verarbeitung_status": "vollständig"
        }

        erfolgreiche.append(kompletter_datensatz)
        print("  -> Ausschreibung erfolgreich vollständig verarbeitet.")

    # Speichern
    with open("data/processed/erfolgreiche_tender.json", "w", encoding="utf-8") as f:
        json.dump(erfolgreiche, f, ensure_ascii=False, indent=2)

    with open("data/processed/teilweise_brauchbare_tender.json", "w", encoding="utf-8") as f:
        json.dump(teilweise_brauchbar, f, ensure_ascii=False, indent=2)

    with open("data/processed/ausgeschlossene_tender.json", "w", encoding="utf-8") as f:
        json.dump(ausgeschlossene, f, ensure_ascii=False, indent=2)

    print("\n" + "=" * 60)
    print("ZUSAMMENFASSUNG")
    print("=" * 60)
    print(f"Gesamt aus Liste: {len(alle_ausschreibungen)}")
    print(f"Erfolgreich vollständig: {len(erfolgreiche)}")
    print(f"Teilweise brauchbar: {len(teilweise_brauchbar)}")
    print(f"Wirklich ausgeschlossen: {len(ausgeschlossene)}")

    print("\nDateien gespeichert:")
    print("✔ data/processed/erfolgreiche_tender.json")
    print("✔ data/processed/teilweise_brauchbare_tender.json")
    print("✔ data/processed/ausgeschlossene_tender.json")


if __name__ == "__main__":
    main()