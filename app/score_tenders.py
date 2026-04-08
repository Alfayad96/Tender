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
    os.makedirs("data/scored", exist_ok=True)

    datei_mit_verfahrensangaben = "data/processed/erfolgreiche_tender.json"
    datei_ohne_verfahrensangaben = "data/processed/teilweise_brauchbare_tender.json"

    mit_verfahrensangaben = load_json(datei_mit_verfahrensangaben)
    ohne_verfahrensangaben = load_json(datei_ohne_verfahrensangaben)

    alle_bewertbaren = []

    for tender in mit_verfahrensangaben:
        tender["datenquelle_typ"] = "mit_verfahrensangaben"
        alle_bewertbaren.append(score_tender(tender))

    for tender in ohne_verfahrensangaben:
        tender["datenquelle_typ"] = "ohne_verfahrensangaben"
        alle_bewertbaren.append(score_tender(tender))

    passende = [t for t in alle_bewertbaren if t.get("bewertung") == "PASSEND"]
    manuell_pruefen = [t for t in alle_bewertbaren if t.get("bewertung") == "MANUELL_PRUEFEN"]
    nicht_passend = [t for t in alle_bewertbaren if t.get("bewertung") == "NICHT_PASSEND"]

    # nach Score sortieren
    passende.sort(key=lambda x: x.get("score", 0), reverse=True)
    manuell_pruefen.sort(key=lambda x: x.get("score", 0), reverse=True)
    nicht_passend.sort(key=lambda x: x.get("score", 0), reverse=True)
    alle_bewertbaren.sort(key=lambda x: x.get("score", 0), reverse=True)

    save_json("data/scored/ausschreibungen_mit_score.json", alle_bewertbaren)
    save_json("data/scored/passende_ausschreibungen.json", passende)
    save_json("data/scored/manuell_pruefen.json", manuell_pruefen)
    save_json("data/scored/nicht_passend.json", nicht_passend)

    print("\n" + "=" * 60)
    print("SCORING ZUSAMMENFASSUNG")
    print("=" * 60)
    print(f"Gesamt bewertbar: {len(alle_bewertbaren)}")
    print(f"PASSEND: {len(passende)}")
    print(f"MANUELL_PRUEFEN: {len(manuell_pruefen)}")
    print(f"NICHT_PASSEND: {len(nicht_passend)}")

    print("\nTop 10 PASSENDE Ausschreibungen:")
    for tender in passende[:10]:
        print("-" * 50)
        print(f"Titel: {tender.get('titel')}")
        print(f"Score: {tender.get('score')}")
        print(f"Bewertung: {tender.get('bewertung')}")
        print(f"Quelle: {tender.get('datenquelle_typ')}")
        print(f"Gründe: {', '.join(tender.get('score_reasons', []))}")


if __name__ == "__main__":
    main()