import re
import unicodedata
from datetime import date, datetime

from app.services.scoring_config import (
    STRONG_POSITIVE_GROUPS,
    MEDIUM_POSITIVE_GROUPS,
    STRONG_NEGATIVE_GROUPS,
    MEDIUM_NEGATIVE_GROUPS,
    HARD_EXCLUDE_STATUS,
    NON_ACTIONABLE_STATUS,
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
                normalized_variant = normalize_text(variant)

                # "web app" must not also count as a mobile app merely because
                # it contains the generic token "app".
                if group_name == "mobile_app" and normalized_variant == "app":
                    text_without_web_apps = re.sub(r"\bweb\s+app\b", " ", search_text)
                    if not contains_variant(text_without_web_apps, "app"):
                        continue

                # Short AR/VR acronyms occur in building project codes. Require
                # them to be free of an obvious construction context unless an
                # explicit extended-reality term is also present.
                if group_name == "ar_vr_xr" and normalized_variant in {"ar", "vr"}:
                    construction_context = any(
                        contains_variant(search_text, marker)
                        for marker in [
                            "bau",
                            "neubau",
                            "umbau",
                            "glt",
                            "gebaeudeautomation",
                            "facility management",
                            "cafm",
                            "elektrotechnik",
                            "schwachstrom",
                        ]
                    )
                    explicit_xr_context = any(
                        contains_variant(search_text, marker)
                        for marker in [
                            "virtual reality",
                            "augmented reality",
                            "mixed reality",
                            "extended reality",
                            "immersive",
                        ]
                    )
                    if construction_context and not explicit_xr_context:
                        continue

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

    match = re.search(r"(\d{2}\.\d{2}\.\d{4})", raw_date)
    if not match:
        return None

    try:
        return datetime.strptime(match.group(1), "%d.%m.%Y")
    except ValueError:
        return None


def calculate_deadline_score(
    tender: dict,
    today: date | None = None,
) -> tuple[int, list[str]]:
    reasons = []
    score = 0

    deadline = parse_deadline(
        tender.get("abgabefrist_detail")
        or tender.get("angebots_teilnahmefrist")
        or tender.get("frist")
    )

    if not deadline:
        return score, reasons

    today_date = today or date.today()
    days_left = (deadline.date() - today_date).days
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


def has_any_variant(search_text: str, variants: list[str]) -> tuple[bool, str | None]:
    for variant in variants:
        if contains_variant(search_text, variant):
            return True, variant
    return False, None


def apply_context_rules(tender: dict, search_text: str) -> tuple[int, list[str]]:
    score_delta = 0
    reasons = []

    title_text = normalize_text(tender.get("titel", ""))

    # -----------------------------------------
    # POSITIVE BOOSTS
    # -----------------------------------------

    app_hit, _ = has_any_variant(search_text, ["app", "mobile app", "android app", "ios app"])
    app_context_hit, app_context_word = has_any_variant(
        search_text,
        [
            "zoo", "museum", "guide", "audio guide", "visitor", "besucher",
            "tourismus", "tourism", "interaktiv", "interactive", "multimedia",
            "learning", "lernen", "edutainment", "gamification", "erlebnis",
            "besucherinformation", "visitor information"
        ]
    )
    if app_hit and app_context_hit:
        score_delta += 8
        reasons.append(f"+8 context_boost_app ({app_context_word})")

    web_hit, _ = has_any_variant(search_text, ["website", "webseite", "web app", "web application", "portal", "homepage"])
    web_context_hit, web_context_word = has_any_variant(
        search_text,
        [
            "redesign", "relaunch", "ux", "ui", "usability", "frontend",
            "interface design", "webauftritt", "digital experience",
            "informationsarchitektur", "nutzeroberflaeche", "anwenderoberflaeche"
        ]
    )
    if web_hit and web_context_hit:
        score_delta += 10
        reasons.append(f"+10 context_boost_web_ux ({web_context_word})")

    xr_hit, xr_word = has_any_variant(
        search_text,
        ["augmented reality", "virtual reality", "xr", "mixed reality", "immersive", "ar", "vr"]
    )
    xr_bad_context_hit, xr_bad_context_word = has_any_variant(
        search_text,
        [
            "bau", "neubau", "umbau", "glt", "aufschaltung",
            "gebaeudeautomation", "liegenschaft",
            "facility management", "cafm", "schliesssystem",
            "schliessanlage", "elektrotechnik", "schwachstrom"
        ]
    )

    if xr_hit and not xr_bad_context_hit:
        score_delta += 6
        reasons.append(f"+6 context_boost_xr ({xr_word})")
    elif xr_hit and xr_bad_context_hit:
        score_delta -= 10
        reasons.append(f"-10 xr_false_context ({xr_bad_context_word})")

    learning_hit, learning_word = has_any_variant(
        search_text,
        [
            "lernsoftware", "learning app", "interactive learning", "edutainment",
            "gamification", "training software", "training system", "simulation",
            "trainingsanwendung", "digitale lernumgebung", "interaktive lernplattform"
        ]
    )
    if learning_hit:
        score_delta += 6
        reasons.append(f"+6 context_boost_learning ({learning_word})")

    # -----------------------------------------
    # NEGATIVE CONTEXT PENALTIES
    # -----------------------------------------

    operations_hit, operations_word = has_any_variant(
        search_text,
        [
            "betrieb", "wartung", "support", "managed service", "managed services",
            "sicherstellung des betriebs", "plattformbetrieb", "servicebetrieb",
            "renewal", "refresh", "lizenz", "lizenzverlaengerung",
            "hosting"
        ]
    )
    if operations_hit:
        delivery_action_hit, _ = has_any_variant(
            search_text,
            [
                "entwicklung",
                "implementierung",
                "erstellung",
                "neuentwicklung",
                "relaunch",
                "redesign",
            ],
        )
        digital_product_hit, _ = has_any_variant(
            search_text,
            [
                "app",
                "website",
                "webseite",
                "web app",
                "web application",
                "internetangebot",
                "portal",
                "software",
            ],
        )

        if delivery_action_hit and digital_product_hit:
            score_delta -= 6
            reasons.append(f"-6 context_penalty_mixed_operations ({operations_word})")
        else:
            score_delta -= 16
            reasons.append(f"-16 context_penalty_operations ({operations_word})")

    enterprise_hit, enterprise_word = has_any_variant(
        search_text,
        [
            "projektportfoliomanagement", "portfoliomanagement", "ppm",
            "hr software", "personalsoftware", "verwaltungssoftware",
            "geschaeftsprozesse", "workflow management", "managementsoftware",
            "workflow", "fachverfahren", "prozessmodellierung", "business process"
        ]
    )
    if enterprise_hit:
        score_delta -= 16
        reasons.append(f"-16 context_penalty_enterprise ({enterprise_word})")

    consulting_hit, consulting_word = has_any_variant(
        search_text,
        [
            "beratung", "consulting", "projektbegleitung",
            "beratungs und unterstuetzungsleistungen",
            "etablierung", "kompetenzcenter"
        ]
    )
    if consulting_hit:
        score_delta -= 12
        reasons.append(f"-12 context_penalty_consulting ({consulting_word})")

    infra_hit, infra_word = has_any_variant(
        search_text,
        [
            "netzwerk", "wan", "layer 2", "server", "rechenzentrum",
            "virenschutz", "authentifizierung", "it sicherheit", "isms", "bcms"
        ]
    )
    if infra_hit:
        score_delta -= 18
        reasons.append(f"-18 context_penalty_infra_security ({infra_word})")

    archive_hit, archive_word = has_any_variant(
        search_text,
        [
            "papierakten", "aktenarchiv", "bauaktenarchiv", "archiv",
            "scan service", "aktendigitalisierung", "fallakten",
            "aktenverwaltung", "dokumentenlagerung"
        ]
    )
    if archive_hit:
        score_delta -= 14
        reasons.append(f"-14 context_penalty_archive ({archive_word})")

    # -----------------------------------------
    # GENERISCHE ENTWICKLUNG
    # -----------------------------------------

    generic_dev_hit, _ = has_any_variant(search_text, ["entwicklung"])
    dev_bad_context_hit, dev_bad_context_word = has_any_variant(
        search_text,
        ["strategische entwicklung", "projektbegleitung", "smart city", "messnetz", "beratung"]
    )

    if generic_dev_hit and dev_bad_context_hit:
        score_delta -= 10
        reasons.append(f"-10 context_penalty_generic_entwicklung ({dev_bad_context_word})")

    # -----------------------------------------
    # TITLE BOOSTS
    # -----------------------------------------

    title_positive_hit, title_positive_word = has_any_variant(
        title_text,
        [
            "zoo app",
            "museum app",
            "augmented reality",
            "virtual reality",
            "serious game",
            "gamification",
        ]
    )
    if title_positive_hit:
        score_delta += 8
        reasons.append(f"+8 title_boost ({title_positive_word})")

    title_web_hit, title_web_word = has_any_variant(title_text, ["redesign", "relaunch"])
    title_web_context_hit, title_web_context_word = has_any_variant(
        title_text,
        ["website", "webseite", "homepage", "webauftritt", "portal", "ux", "ui"]
    )
    if title_web_hit and title_web_context_hit:
        score_delta += 5
        reasons.append(f"+5 title_web_boost ({title_web_word} + {title_web_context_word})")

    return score_delta, reasons


def get_status_text(tender: dict) -> str:
    return normalize_text(
        " ".join([
            str(tender.get("status_detail", "")),
            str(tender.get("vergabeart_detail", "")),
            str(tender.get("vergabeart", "")),
        ])
    )


def check_hard_exclusions(tender: dict, search_text: str) -> str | None:
    status_text = get_status_text(tender)

    for marker in HARD_EXCLUDE_STATUS:
        if contains_variant(status_text, marker):
            return f"Harter Ausschluss wegen Status/Vergabeart: {marker}"

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
        "wan",
        "layer 2",
        "virenschutz",
        "zwei faktor authentifizierung",
    ]

    for marker in hard_negative_title_markers:
        if contains_variant(title_text, marker):
            return f"Harter Ausschluss wegen Titel: {marker}"

    return None


def check_non_actionable_status(tender: dict) -> str | None:
    status_text = get_status_text(tender)

    for marker in NON_ACTIONABLE_STATUS:
        if contains_variant(status_text, marker):
            return marker

    return None


def has_soft_warning(tender: dict, search_text: str) -> tuple[bool, str | None]:
    status_text = get_status_text(tender)

    for marker in SOFT_WARNING_STATUS:
        if contains_variant(status_text, marker):
            return True, marker

    return False, None


def classify_tender(
    score: int,
    positive_hits: list[str],
    negative_hits: list[str],
    hard_exclusion: str | None,
    non_actionable_marker: str | None,
) -> str:
    if hard_exclusion:
        return "NICHT_PASSEND"

    if non_actionable_marker:
        return "NICHT_AKTIV_BEREITS_VERGEBEN"

    strong_core_groups = {
        "game_development",
        "ar_vr_xr",
        "simulation_training",
        "mobile_app",
        "web_app",
        "web_redesign_ux_ui",
        "interactive_systems",
        "visitor_experience_apps",
        "gamification",
    }

    heavy_negative_groups = {
        "sap_erp_enterprise",
        "infrastructure_operations",
        "hardware_procurement",
        "construction_facility",
        "security_networking",
        "enterprise_admin_software",
    }

    has_strong_core = any(hit in strong_core_groups for hit in positive_hits)
    has_heavy_negative = any(hit in heavy_negative_groups for hit in negative_hits)

    # Spezialregel: workflow-app eher manuell prüfen
    title_like_workflow_app = (
        "mobile_app" in positive_hits and
        "enterprise_admin_software" in negative_hits
    )
    if title_like_workflow_app and score >= 0:
        return "MANUELL_PRUEFEN"

    if has_strong_core and not has_heavy_negative and score >= 24:
        return "PASSEND"

    if has_strong_core and has_heavy_negative and score >= 14:
        return "MANUELL_PRUEFEN"

    if score >= 14:
        return "MANUELL_PRUEFEN"

    return "NICHT_PASSEND"


def score_tender(tender: dict) -> dict:
    search_text = build_search_text(tender)

    positive_score_1, positive_hits_1, positive_reasons_1 = evaluate_groups(
        search_text, STRONG_POSITIVE_GROUPS
    )
    positive_score_2, positive_hits_2, positive_reasons_2 = evaluate_groups(
        search_text, MEDIUM_POSITIVE_GROUPS
    )

    negative_score_1, negative_hits_1, negative_reasons_1 = evaluate_groups(
        search_text, STRONG_NEGATIVE_GROUPS
    )
    negative_score_2, negative_hits_2, negative_reasons_2 = evaluate_groups(
        search_text, MEDIUM_NEGATIVE_GROUPS
    )

    context_score, context_reasons = apply_context_rules(tender, search_text)
    hard_exclusion = check_hard_exclusions(tender, search_text)
    non_actionable_marker = check_non_actionable_status(tender)

    # Frist nur bei aktiven Verfahren werten
    if not hard_exclusion and not non_actionable_marker:
        deadline_score, deadline_reasons = calculate_deadline_score(tender)

        deadline_value = parse_deadline(
            tender.get("abgabefrist_detail")
            or tender.get("angebots_teilnahmefrist")
            or tender.get("frist")
        )
        if (
            deadline_value
            and tender.get("tage_bis_frist") is not None
            and tender["tage_bis_frist"] < 0
        ):
            non_actionable_marker = "frist abgelaufen"
    else:
        deadline_score, deadline_reasons = 0, []

    score = (
        positive_score_1
        + positive_score_2
        + negative_score_1
        + negative_score_2
        + context_score
        + deadline_score
    )

    positive_hits = positive_hits_1 + positive_hits_2
    negative_hits = negative_hits_1 + negative_hits_2

    reasons = (
        positive_reasons_1
        + positive_reasons_2
        + negative_reasons_1
        + negative_reasons_2
        + context_reasons
        + deadline_reasons
    )

    soft_warning, soft_warning_marker = has_soft_warning(tender, search_text)
    if soft_warning:
        reasons.insert(0, f"SOFT_WARNING: {soft_warning_marker}")

    if non_actionable_marker:
        reasons.insert(0, f"NICHT_AKTIV: {non_actionable_marker}")

    if hard_exclusion:
        reasons.insert(0, f"HARTER_AUSSCHLUSS: {hard_exclusion}")

    classification = classify_tender(
        score,
        positive_hits,
        negative_hits,
        hard_exclusion,
        non_actionable_marker,
    )

    tender["scoring_text"] = search_text
    tender["score"] = score
    tender["positive_hits"] = positive_hits
    tender["negative_hits"] = negative_hits
    tender["score_reasons"] = reasons
    tender["hard_exclusion_reason"] = hard_exclusion
    tender["non_actionable_reason"] = non_actionable_marker
    tender["bewertung"] = classification

    return tender
