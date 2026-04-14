import json
import os
from typing import List, Dict


BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SCORED_DIR = os.path.join(BASE_DIR, "data", "scored")


def _load_json(filename: str) -> List[Dict]:
    path = os.path.join(SCORED_DIR, filename)

    if not os.path.exists(path):
        return []

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_all_tenders() -> List[Dict]:
    return _load_json("ausschreibungen_mit_score.json")


def load_passende_tender() -> List[Dict]:
    return _load_json("passende_ausschreibungen.json")


def load_manuell_pruefen_tender() -> List[Dict]:
    return _load_json("manuell_pruefen.json")


def load_nicht_passende_tender() -> List[Dict]:
    return _load_json("nicht_passend.json")


def load_nicht_aktive_tender() -> List[Dict]:
    return _load_json("nicht_aktiv_bereits_vergeben.json")


def filter_tenders_by_search(tenders: List[Dict], search_term: str) -> List[Dict]:
    if not search_term:
        return tenders

    search_term = search_term.lower().strip()

    result = []
    for tender in tenders:
        searchable_text = " ".join([
            str(tender.get("titel", "")),
            str(tender.get("auftraggeber", "")),
            str(tender.get("auftraggeber_name", "")),
            str(tender.get("ausschreibungs_id", "")),
            str(tender.get("vergabe_nr", "")),
            str(tender.get("vergabeart", "")),
            str(tender.get("vergabeart_detail", "")),
            str(tender.get("beschreibung_leistung", "")),
            str(tender.get("auftragsgegenstand_detail", "")),
            str(tender.get("auftragsgegenstand_text", "")),
            str(tender.get("ort", "")),
            str(tender.get("postleitzahl", "")),
        ]).lower()

        if search_term in searchable_text:
            result.append(tender)

    return result


def sort_tenders(tenders: List[Dict], sort_by: str) -> List[Dict]:
    if sort_by == "Score absteigend":
        return sorted(tenders, key=lambda x: x.get("score", 0), reverse=True)

    if sort_by == "Score aufsteigend":
        return sorted(tenders, key=lambda x: x.get("score", 0))

    if sort_by == "Frist":
        def deadline_key(item):
            days = item.get("tage_bis_frist")
            if days is None:
                return 999999
            return days
        return sorted(tenders, key=deadline_key)

    if sort_by == "Titel A-Z":
        return sorted(tenders, key=lambda x: str(x.get("titel", "")).lower())

    return tenders