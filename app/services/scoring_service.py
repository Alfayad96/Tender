import re
import unicodedata
from datetime import datetime

from app.services.scoring_config import (
    STRONG_POSITIVE_GROUPS,
    MEDIUM_POSITIVE_GROUPS,
    STRONG_NEGATIVE_GROUPS,
    MEDIUM_NEGATIVE_GROUPS,
    HARD_EXCLUDE_STATUS,
    SOFT_WARNING_STATUS,
    MIN_GOOD_DAYS,
    MIN_ACCEPTABLE_DAYS,
    MIN_BAD_DAYS,
)


def normalize_text(text: str) -> str:
    if not text:
        return ""

    text = text.lower()

    replacements = {
        "ä": "ae",
        "ö": "oe",
        "ü": "ue",
        "ß": "ss",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)

    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))

    text = text.replace("/", " ")
    text = text.replace("-", " ")
    text = text.replace("_", " ")

    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

    return text


def build_search_text(tender: dict) -> str:
    fields = [
        tender.get("titel", ""),
        tender.get("vergabeart", ""),
        tender.get("vergabeart_detail", ""),
        tender.get("vergabeordnung", ""),
        tender.get("auftraggeber", ""),
        tender.get("auftraggeber_detail", ""),
        tender.get("stelle_bezeichnung", ""),
        tender.get("leistung_bezeichnung", ""),
        tender.get("beschreibung_leistung", ""),
        tender.get("auftragsgegenstand_detail", ""),
        tender.get("auftragsgegenstand_text", ""),
        tender.get("sonstige_angaben", ""),
        tender.get("art_der_leistung", ""),
        tender.get("veroeffentlicher", ""),
    ]

    joined = " ".join(str(x) for x in fields if x)
    return normalize_text(joined)


def contains_variant(search_text: str, variant: str) -> bool:
    normalized_variant = normalize_text(variant)
    if not normalized_variant:
        return False

    padded_text = f" {search_text} "
    padded_variant = f" {normalized_variant} "

    return padded_variant in padded_text


def evaluate_groups(search_text: str, groups: list[dict]) -> tuple[int, list[str], list[str]]:
    total_score = 0
    hits = []
    reasons = []

    for group in groups:
        group_name = group["name"]
        group_weight = group["weight"]
        variants = group["variants"]

        matched_variant = None
        for variant in variants:
            if contains_variant(search_text, variant):
                matched_variant = variant
                break

        if matched_variant:
            total_score += group_weight
            hits.append(group_name)

            sign = "+" if group_weight >= 0 else ""
            reasons.append(f"{sign}{group_weight} {group_name} ({matched_variant})")

    return total_score, hits, reasons


def parse_deadline(raw_date: str | None):
    if not raw_date or raw_date == "nv":
        return None

    raw_date = raw_date.strip()

    # Nur Datumsteil nehmen, falls Uhrzeit dabei ist
    match = re.search(r"(\d{2}\.\d{2}\.\d{4})", raw_date)
    if not match:
        return None

    try:
        return datetime.strptime(match.group(1), "%d.%m.%Y")
    except ValueError:
        return None


def calculate_deadline_score(tender: dict) -> tuple[int, list[str]]:
    reasons = []
    score = 0

    deadline = parse_deadline(
        tender.get("abgabefrist_detail")
        or tender.get("angebots_teilnahmefrist")
        or tender.get("frist")
    )

    if not deadline:
        return score, reasons

    today = datetime.now()
    days_left = (deadline - today).days

    tender["tage_bis_frist"] = days_left

    if days_left >= MIN_GOOD_DAYS:
        score += 12
        reasons.append(f"+12 gute Frist ({days_left} Tage)")
    elif MIN_ACCEPTABLE_DAYS <= days_left < MIN_GOOD_DAYS:
        score += 5
        reasons.append(f"+5 akzeptable Frist ({days_left} Tage)")
    elif days_left < MIN_BAD_DAYS:
        score -= 25
        reasons.append(f"-25 zu kurze Frist ({days_left} Tage)")

    return score, reasons


def check_hard_exclusions(tender: dict, search_text: str) -> str | None:
    status_text = normalize_text(
        " ".join([
            str(tender.get("status_detail", "")),
            str(tender.get("vergabeart_detail", "")),
            str(tender.get("vergabeart", "")),
        ])
    )

    for marker in HARD_EXCLUDE_STATUS:
        if contains_variant(status_text, marker):
            return f"Harter Ausschluss wegen Status/Vergabeart: {marker}"

    # klare fachliche Ausschlüsse über dominante Negativsignale
    title_text = normalize_text(tender.get("titel", ""))

    hard_negative_title_markers = [
        "schliessanlage",
        "schliesssystem",
        "strassenzustand",
        "fahrgastzaehlsystem",
        "postdienstleistung",
        "telefonanlage",
        "busse",
        "fahrzeug",
    ]

    for marker in hard_negative_title_markers:
        if contains_variant(title_text, marker):
            return f"Harter Ausschluss wegen Titel: {marker}"

    return None


def classify_tender(score: int, positive_hits: list[str], negative_hits: list[str], hard_exclusion: str | None) -> str:
    if hard_exclusion:
        return "NICHT_PASSEND"

    # wenn mindestens ein starker positiver Themen-Treffer da ist und Score hoch genug
    strong_thematic_groups = {
        "mobile_app",
        "web_app",
        "software_development",
        "game_development",
        "unity",
        "godot",
        "ar_vr_xr",
        "gamification"
    }

    has_strong_positive_theme = any(hit in strong_thematic_groups for hit in positive_hits)

    if has_strong_positive_theme and score >= 28:
        return "PASSEND"

    if score >= 12:
        return "MANUELL_PRUEFEN"

    return "NICHT_PASSEND"


def score_tender(tender: dict) -> dict:
    search_text = build_search_text(tender)

    positive_score_1, positive_hits_1, positive_reasons_1 = evaluate_groups(search_text, STRONG_POSITIVE_GROUPS)
    positive_score_2, positive_hits_2, positive_reasons_2 = evaluate_groups(search_text, MEDIUM_POSITIVE_GROUPS)

    negative_score_1, negative_hits_1, negative_reasons_1 = evaluate_groups(search_text, STRONG_NEGATIVE_GROUPS)
    negative_score_2, negative_hits_2, negative_reasons_2 = evaluate_groups(search_text, MEDIUM_NEGATIVE_GROUPS)

    hard_exclusion = check_hard_exclusions(tender, search_text)

    deadline_score, deadline_reasons = calculate_deadline_score(tender)

    score = (
        positive_score_1
        + positive_score_2
        + negative_score_1
        + negative_score_2
        + deadline_score
    )

    positive_hits = positive_hits_1 + positive_hits_2
    negative_hits = negative_hits_1 + negative_hits_2

    reasons = (
        positive_reasons_1
        + positive_reasons_2
        + negative_reasons_1
        + negative_reasons_2
        + deadline_reasons
    )

    if hard_exclusion:
        reasons.insert(0, f"HARTER_AUSSCHLUSS: {hard_exclusion}")

    classification = classify_tender(score, positive_hits, negative_hits, hard_exclusion)

    tender["scoring_text"] = search_text
    tender["score"] = score
    tender["positive_hits"] = positive_hits
    tender["negative_hits"] = negative_hits
    tender["score_reasons"] = reasons
    tender["hard_exclusion_reason"] = hard_exclusion
    tender["bewertung"] = classification

    return tender