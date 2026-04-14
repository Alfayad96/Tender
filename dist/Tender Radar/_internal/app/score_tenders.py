import os
import json

from app.services.scoring_service import score_tender


def load_json(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: str, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def main():
    print("\n" + "=" * 60)
    print("SCORING WIRD GESTARTET")
    print("=" * 60)

    os.makedirs("data/scored", exist_ok=True)

    datei_mit_verfahrensangaben = "data/processed/erfolgreiche_tender.json"
    datei_ohne_verfahrensangaben = "data/processed/teilweise_brauchbare_tender.json"

    print("Lade verarbeitete Ausschreibungen ...")
    print(f"Datei mit Verfahrensangaben: {datei_mit_verfahrensangaben}")
    print(f"Datei ohne Verfahrensangaben: {datei_ohne_verfahrensangaben}")

    mit_verfahrensangaben = load_json(datei_mit_verfahrensangaben)
    ohne_verfahrensangaben = load_json(datei_ohne_verfahrensangaben)

    print(f"-> Mit Verfahrensangaben geladen: {len(mit_verfahrensangaben)}")
    print(f"-> Ohne Verfahrensangaben geladen: {len(ohne_verfahrensangaben)}")

    alle_bewertbaren = []

    print("\n" + "-" * 60)
    print("BEWERTUNG: AUSSCHREIBUNGEN MIT VERFAHRENSANGABEN")
    print("-" * 60)

    for index, tender in enumerate(mit_verfahrensangaben, start=1):
        titel = tender.get("titel", "Ohne Titel")
        print(f"[MIT {index}/{len(mit_verfahrensangaben)}] Bewerte: {titel}")

        tender["datenquelle_typ"] = "mit_verfahrensangaben"
        scored = score_tender(tender)
        alle_bewertbaren.append(scored)

        print(
            f"   -> Score: {scored.get('score')} | "
            f"Bewertung: {scored.get('bewertung')}"
        )

    print("\n" + "-" * 60)
    print("BEWERTUNG: AUSSCHREIBUNGEN OHNE VERFAHRENSANGABEN")
    print("-" * 60)

    for index, tender in enumerate(ohne_verfahrensangaben, start=1):
        titel = tender.get("titel", "Ohne Titel")
        print(f"[OHNE {index}/{len(ohne_verfahrensangaben)}] Bewerte: {titel}")

        tender["datenquelle_typ"] = "ohne_verfahrensangaben"
        scored = score_tender(tender)
        alle_bewertbaren.append(scored)

        print(
            f"   -> Score: {scored.get('score')} | "
            f"Bewertung: {scored.get('bewertung')}"
        )

    print("\nAlle bewertbaren Ausschreibungen wurden analysiert.")
    print(f"Gesamtzahl bewertbar: {len(alle_bewertbaren)}")

    passende = [t for t in alle_bewertbaren if t.get("bewertung") == "PASSEND"]
    manuell_pruefen = [t for t in alle_bewertbaren if t.get("bewertung") == "MANUELL_PRUEFEN"]
    nicht_passend = [t for t in alle_bewertbaren if t.get("bewertung") == "NICHT_PASSEND"]
    nicht_aktiv_bereits_vergeben = [
        t for t in alle_bewertbaren
        if t.get("bewertung") == "NICHT_AKTIV_BEREITS_VERGEBEN"
    ]

    print("\nSortiere Ergebnisse ...")
    passende.sort(key=lambda x: x.get("score", 0), reverse=True)
    manuell_pruefen.sort(key=lambda x: x.get("score", 0), reverse=True)
    nicht_passend.sort(key=lambda x: x.get("score", 0), reverse=True)
    nicht_aktiv_bereits_vergeben.sort(key=lambda x: x.get("score", 0), reverse=True)
    alle_bewertbaren.sort(key=lambda x: x.get("score", 0), reverse=True)

    print("Speichere JSON-Dateien ...")
    save_json("data/scored/ausschreibungen_mit_score.json", alle_bewertbaren)
    save_json("data/scored/passende_ausschreibungen.json", passende)
    save_json("data/scored/manuell_pruefen.json", manuell_pruefen)
    save_json("data/scored/nicht_passend.json", nicht_passend)
    save_json("data/scored/nicht_aktiv_bereits_vergeben.json", nicht_aktiv_bereits_vergeben)

    print("-> Gespeichert: data/scored/ausschreibungen_mit_score.json")
    print("-> Gespeichert: data/scored/passende_ausschreibungen.json")
    print("-> Gespeichert: data/scored/manuell_pruefen.json")
    print("-> Gespeichert: data/scored/nicht_passend.json")
    print("-> Gespeichert: data/scored/nicht_aktiv_bereits_vergeben.json")

    print("\n" + "=" * 60)
    print("SCORING ZUSAMMENFASSUNG")
    print("=" * 60)
    print(f"Gesamt bewertbar: {len(alle_bewertbaren)}")
    print(f"PASSEND: {len(passende)}")
    print(f"MANUELL_PRUEFEN: {len(manuell_pruefen)}")
    print(f"NICHT_AKTIV_BEREITS_VERGEBEN: {len(nicht_aktiv_bereits_vergeben)}")
    print(f"NICHT_PASSEND: {len(nicht_passend)}")

    print("\nTop 10 PASSENDE Ausschreibungen:")
    if passende:
        for tender in passende[:10]:
            print("-" * 50)
            print(f"Titel: {tender.get('titel')}")
            print(f"Score: {tender.get('score')}")
            print(f"Bewertung: {tender.get('bewertung')}")
            print(f"Quelle: {tender.get('datenquelle_typ')}")
            print(f"Gründe: {', '.join(tender.get('score_reasons', []))}")
    else:
        print("Keine passenden Ausschreibungen gefunden.")

    print("\nTop 10 MANUELL_PRUEFEN:")
    if manuell_pruefen:
        for tender in manuell_pruefen[:10]:
            print("-" * 50)
            print(f"Titel: {tender.get('titel')}")
            print(f"Score: {tender.get('score')}")
            print(f"Bewertung: {tender.get('bewertung')}")
            print(f"Quelle: {tender.get('datenquelle_typ')}")
            print(f"Gründe: {', '.join(tender.get('score_reasons', []))}")
    else:
        print("Keine manuellen Prüffälle gefunden.")

    print("\nTop 10 NICHT_AKTIV_BEREITS_VERGEBEN:")
    if nicht_aktiv_bereits_vergeben:
        for tender in nicht_aktiv_bereits_vergeben[:10]:
            print("-" * 50)
            print(f"Titel: {tender.get('titel')}")
            print(f"Score: {tender.get('score')}")
            print(f"Bewertung: {tender.get('bewertung')}")
            print(f"Quelle: {tender.get('datenquelle_typ')}")
            print(f"Gründe: {', '.join(tender.get('score_reasons', []))}")
    else:
        print("Keine nicht aktiven Ausschreibungen gefunden.")

    print("\nScoring erfolgreich abgeschlossen.")


if __name__ == "__main__":
    main()