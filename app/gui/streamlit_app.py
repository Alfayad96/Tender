import base64
import hmac
import io
import os
from html import escape
from pathlib import Path

import streamlit as st
from contextlib import redirect_stdout, redirect_stderr

from app.services.tender_service import (
    load_passende_tender,
    load_manuell_pruefen_tender,
    load_nicht_passende_tender,
    load_nicht_aktive_tender,
    filter_tenders_by_search,
    sort_tenders,
)

from run import main as run_marktscan
from run_scoring import main as run_relevanzanalyse
from app.gui.presentation import (
    display_deadline,
    display_items,
    first_display_value,
    has_display_value,
)


ASSET_DIR = Path(__file__).resolve().parent / "assets"
BRAND_MARK = ASSET_DIR / "tender-radar-mark.svg"
USERNAME_ENV = "TENDER_RADAR_USERNAME"
PASSWORD_ENV = "TENDER_RADAR_PASSWORD"


st.set_page_config(
    page_title="Tender Radar",
    page_icon=str(BRAND_MARK),
    layout="wide"
)


def inject_styles():
    st.markdown(
        """
        <style>
        .block-container {
            max-width: 1180px;
            padding-top: 2.25rem;
            padding-bottom: 4rem;
        }

        [data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
            gap: 0.9rem;
        }

        [data-testid="stVerticalBlockBorderWrapper"] {
            border-color: rgba(128, 128, 128, 0.22);
            border-radius: 1rem;
            box-shadow: 0 8px 28px rgba(0, 0, 0, 0.08);
        }

        .stButton > button,
        .stFormSubmitButton > button,
        .stLinkButton > a {
            min-height: 2.7rem;
            border-radius: 0.65rem;
            font-weight: 600;
        }

        [data-testid="stIconMaterial"] {
            font-size: 1.15rem;
        }

        .stButton > button[kind="primary"],
        .stFormSubmitButton > button[kind="primaryFormSubmit"] {
            border-color: #2f80ed;
            background: #2f80ed;
            color: #ffffff;
        }

        .stButton > button[kind="primary"]:hover,
        .stFormSubmitButton > button[kind="primaryFormSubmit"]:hover {
            border-color: #1f6fd8;
            background: #1f6fd8;
            color: #ffffff;
        }

        .stButton > button:focus-visible,
        .stFormSubmitButton > button:focus-visible,
        .stLinkButton > a:focus-visible {
            outline: 3px solid rgba(64, 153, 255, 0.38);
            outline-offset: 2px;
        }

        .stTabs [data-baseweb="tab-list"] {
            gap: 0.4rem;
        }

        .stTabs [data-baseweb="tab"] {
            border-radius: 0.6rem 0.6rem 0 0;
            padding-left: 1rem;
            padding-right: 1rem;
        }

        [data-testid="stMetric"] {
            padding: 0.8rem 0.9rem;
            border: 1px solid rgba(128, 128, 128, 0.2);
            border-radius: 0.75rem;
        }

        .tender-status {
            display: inline-flex;
            align-items: center;
            width: fit-content;
            margin: 0.1rem 0 0.65rem;
            padding: 0.25rem 0.65rem;
            border: 1px solid rgba(128, 128, 128, 0.28);
            border-radius: 999px;
            background: rgba(128, 128, 128, 0.1);
            font-size: 0.78rem;
            font-weight: 700;
            letter-spacing: 0.02em;
        }

        .brand-header,
        .empty-state {
            display: flex;
            align-items: center;
            gap: 1rem;
        }

        .brand-header {
            margin: 0.15rem 0 1.4rem;
        }

        .brand-header img {
            width: 64px;
            height: 64px;
            flex: 0 0 64px;
        }

        .login-brand-mark {
            display: block;
            width: 60px;
            height: 60px;
            margin-bottom: 0.35rem;
        }

        .brand-header h1,
        .empty-state h3 {
            margin: 0;
            padding: 0;
        }

        .brand-header p,
        .empty-state p {
            margin: 0.3rem 0 0;
            color: rgba(128, 128, 128, 0.95);
        }

        .empty-state {
            padding: 0.45rem 0.2rem;
        }

        .empty-state img {
            width: 54px;
            height: 54px;
            flex: 0 0 54px;
        }

        .tender-meta {
            margin: 0.15rem 0 0.7rem;
            line-height: 1.45;
        }

        .tender-meta-label {
            display: block;
            margin-bottom: 0.12rem;
            color: rgba(128, 128, 128, 0.95);
            font-size: 0.75rem;
            font-weight: 700;
            letter-spacing: 0.035em;
            text-transform: uppercase;
        }

        .tender-meta-value {
            overflow-wrap: anywhere;
            font-weight: 550;
        }

        .tender-reasons {
            margin-top: 0.25rem;
            margin-bottom: 1rem;
            padding-left: 1.25rem;
        }

        .tender-reasons li {
            margin: 0.25rem 0;
        }

        hr {
            margin-top: 1.7rem !important;
            margin-bottom: 1.7rem !important;
        }

        @media (max-width: 640px) {
            .block-container {
                padding-top: 3.75rem;
                padding-left: 1rem;
                padding-right: 1rem;
            }

            .stTabs [data-baseweb="tab"] {
                padding-left: 0.65rem;
                padding-right: 0.65rem;
            }

            .brand-header {
                align-items: flex-start;
            }

            .brand-header img {
                width: 52px;
                height: 52px;
                flex-basis: 52px;
            }

            .brand-header h1 {
                font-size: 2rem;
                line-height: 1.1;
            }

            .empty-state {
                align-items: flex-start;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def login_credentials() -> tuple[str, str]:
    """Read credentials on the Streamlit server without exposing them to the UI."""
    return os.getenv(USERNAME_ENV, "").strip(), os.getenv(PASSWORD_ENV, "")


def credentials_match(username: str, password: str) -> bool:
    expected_username, expected_password = login_credentials()
    if not expected_username or not expected_password:
        return False

    return hmac.compare_digest(username, expected_username) and hmac.compare_digest(
        password,
        expected_password,
    )


def check_login():
    # TEMPORÄR: Login komplett deaktiviert — die Session wird als eingeloggt markiert.
    # Nur lokal verwenden. Nicht in Produktion oder ins Repo pushen.
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = True
    else:
        st.session_state.logged_in = True
    return


def brand_mark_data_uri() -> str:
    encoded = base64.b64encode(BRAND_MARK.read_bytes()).decode("ascii")
    return f"data:image/svg+xml;base64,{encoded}"


def render_brand_header():
    st.markdown(
        f"""
        <div class="brand-header">
            <img src="{brand_mark_data_uri()}" alt="Tender Radar Logo">
            <div>
                <h1>Tender Radar</h1>
                <p>Suche, Analyse und Bewertung von Ausschreibungen für QM Interactive</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_initial_empty_state():
    with st.container(border=True):
        st.markdown(
            f"""
            <div class="empty-state">
                <img src="{brand_mark_data_uri()}" alt="">
                <div>
                    <h3>Bereit für den nächsten Marktscan</h3>
                    <p>Starte die Suche, um aktuelle Ausschreibungen zu sammeln und nach Relevanz zu bewerten.</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def init_session_state():
    if "daten_geladen" not in st.session_state:
        st.session_state.daten_geladen = False

    if "has_current_run_results" not in st.session_state:
        st.session_state.has_current_run_results = False

    if "passende" not in st.session_state:
        st.session_state.passende = []

    if "manuell" not in st.session_state:
        st.session_state.manuell = []

    if "nicht_aktiv" not in st.session_state:
        st.session_state.nicht_aktiv = []

    if "nicht_passend" not in st.session_state:
        st.session_state.nicht_passend = []

    if "scan_running" not in st.session_state:
        st.session_state.scan_running = False

    if "analyse_running" not in st.session_state:
        st.session_state.analyse_running = False

    if "scan_done_message" not in st.session_state:
        st.session_state.scan_done_message = ""

    if "analyse_done_message" not in st.session_state:
        st.session_state.analyse_done_message = ""


def clear_session_results():
    st.session_state.passende = []
    st.session_state.manuell = []
    st.session_state.nicht_aktiv = []
    st.session_state.nicht_passend = []
    st.session_state.daten_geladen = False
    st.session_state.has_current_run_results = False


def load_results_into_session():
    passende = load_passende_tender()
    manuell = load_manuell_pruefen_tender()
    nicht_aktiv = load_nicht_aktive_tender()
    nicht_passend = load_nicht_passende_tender()

    st.session_state.passende = passende
    st.session_state.manuell = manuell
    st.session_state.nicht_aktiv = nicht_aktiv
    st.session_state.nicht_passend = nicht_passend
    st.session_state.daten_geladen = True


def parse_status_line(line: str):
    line = line.strip()

    if line.startswith("STATUS:"):
        return {"type": "status", "message": line.replace("STATUS:", "", 1).strip()}

    if line.startswith("FORTSCHRITT:"):
        return {"type": "progress_text", "message": line.replace("FORTSCHRITT:", "", 1).strip()}

    return None


def extract_progress_percent(line: str):
    line = line.strip()

    if "Seite" in line and "von" in line and "wird geladen" in line:
        parts = line.split()
        try:
            current = int(parts[2])
            total = int(parts[4])
            if total > 0:
                return int((current / total) * 100)
        except Exception:
            return None

    if "[" in line and "/" in line and "]" in line:
        try:
            start = line.index("[") + 1
            end = line.index("]")
            current_str, total_str = line[start:end].split("/")
            current = int(current_str)
            total = int(total_str)
            if total > 0:
                return int((current / total) * 100)
        except Exception:
            return None

    return None


class StreamlitLogWriter(io.TextIOBase):
    def __init__(self, status_box, progress_bar):
        self.status_box = status_box
        self.progress_bar = progress_bar
        self.buffer = ""
        self.last_progress = 0

    def show_current_line(self, line: str):
        parsed = parse_status_line(line)

        if parsed:
            self.status_box.info(parsed["message"], icon=":material/sync:")
        else:
            self.status_box.info(line, icon=":material/sync:")

        progress = extract_progress_percent(line)
        if progress is not None:
            self.last_progress = progress
            self.progress_bar.progress(progress)

    def write(self, text):
        if not text:
            return 0

        self.buffer += text

        while "\n" in self.buffer:
            line, self.buffer = self.buffer.split("\n", 1)
            clean_line = line.strip()

            if clean_line:
                self.show_current_line(clean_line)

        return len(text)

    def flush(self):
        if self.buffer.strip():
            clean_line = self.buffer.strip()
            self.show_current_line(clean_line)

        self.buffer = ""


def run_with_live_output(fn, title: str):
    st.subheader(title)

    status_box = st.empty()
    progress_bar = st.progress(0)

    writer = StreamlitLogWriter(status_box, progress_bar)

    try:
        status_box.info(f"{title} läuft ...", icon=":material/sync:")

        with redirect_stdout(writer), redirect_stderr(writer):
            fn()

        writer.flush()
        progress_bar.progress(100)
        status_box.success(
            f"{title} erfolgreich abgeschlossen.",
            icon=":material/check_circle:",
        )
        return True

    except Exception as e:
        writer.flush()
        status_box.error(
            f"{title} wurde mit Fehler beendet: {e}",
            icon=":material/error:",
        )
        return False


def run_full_search():
    clear_session_results()

    success_scan = run_with_live_output(run_marktscan, "Marktscan")

    if not success_scan:
        return False

    st.info(
        "Marktscan ist fertig. Ausschreibungen werden analysiert ...",
        icon=":material/analytics:",
    )

    success_analyse = run_with_live_output(run_relevanzanalyse, "Relevanzanalyse")

    if not success_analyse:
        return False

    load_results_into_session()
    st.session_state.has_current_run_results = True
    st.session_state.scan_done_message = "Ausschreibungen wurden gefunden und analysiert."
    return True


def available_links(tender: dict) -> list[tuple[str, str, str]]:
    links = [
        (
            "Zur Ausschreibung",
            first_display_value(tender.get("final_detail_url"), tender.get("detail_url")),
            ":material/open_in_new:",
        ),
        (
            "Verfahrensangaben",
            first_display_value(
                tender.get("final_verfahrensangaben_url"),
                tender.get("verfahrensangaben_url"),
            ),
            ":material/description:",
        ),
        ("Externe Infos", tender.get("externe_info_url"), ":material/language:"),
    ]
    return [(label, url, icon) for label, url, icon in links if has_display_value(url)]


def render_links(links: list[tuple[str, str, str]]):
    if not links:
        return

    columns = st.columns(len(links))
    for column, (label, url, icon) in zip(columns, links):
        with column:
            st.link_button(label, url, icon=icon, use_container_width=True)


def render_metadata(items: list[tuple[str, object]]):
    visible_items = [(label, value) for label, value in items if has_display_value(value)]

    for index in range(0, len(visible_items), 2):
        row = visible_items[index : index + 2]
        columns = st.columns(len(row))
        for column, (label, value) in zip(columns, row):
            with column:
                st.markdown(
                    (
                        '<div class="tender-meta">'
                        f'<span class="tender-meta-label">{escape(label)}</span>'
                        f'<span class="tender-meta-value">{escape(str(value).strip())}</span>'
                        "</div>"
                    ),
                    unsafe_allow_html=True,
                )


def readable_tag(value: object) -> str:
    return str(value).replace("_", " ").strip()


def readable_status(value: object) -> str:
    labels = {
        "PASSEND": "Passend",
        "MANUELL_PRUEFEN": "Manuell prüfen",
        "NICHT_AKTIV_BEREITS_VERGEBEN": "Nicht aktiv",
        "NICHT_PASSEND": "Nicht passend",
    }
    raw_value = str(value).strip()
    return labels.get(raw_value, readable_tag(raw_value).title())


def render_tender_card(tender: dict):
    titel = tender.get("titel")
    score = tender.get("score")
    bewertung = tender.get("bewertung")
    auftraggeber = first_display_value(
        tender.get("auftraggeber"),
        tender.get("auftraggeber_name"),
        tender.get("stelle_bezeichnung"),
    )
    frist = display_deadline(
        tender.get("abgabefrist_detail"),
        tender.get("angebots_teilnahmefrist"),
        tender.get("teilnahmefrist"),
        tender.get("frist"),
    )
    ort = first_display_value(tender.get("ort"), tender.get("postleitzahl"))
    beschreibung = first_display_value(
        tender.get("beschreibung_leistung"),
        tender.get("auftragsgegenstand_text"),
    )
    cpv = first_display_value(
        tender.get("auftragsgegenstand_detail"),
        tender.get("auftragsgegenstand_code"),
    )
    positive_hits = display_items(tender.get("positive_hits"))
    negative_hits = display_items(tender.get("negative_hits"))
    score_reasons = display_items(tender.get("score_reasons"))
    links = available_links(tender)

    metadata = [
        ("Frist", frist),
        ("Veröffentlicht", tender.get("veroeffentlichung")),
        ("Ausschreibungs-ID", tender.get("ausschreibungs_id")),
        ("Vergabe-Nr.", tender.get("vergabe_nr")),
        (
            "Vergabeart",
            first_display_value(tender.get("vergabeart_detail"), tender.get("vergabeart")),
        ),
        ("Status", tender.get("status_detail")),
        ("Ort", ort),
        ("CPV / Leistungsbereich", cpv),
    ]

    with st.container(border=True):
        if has_display_value(score):
            content_column, score_column = st.columns([5, 1])
        else:
            content_column = st.container()
            score_column = None

        with content_column:
            if has_display_value(titel):
                st.subheader(str(titel).strip())

            if has_display_value(bewertung):
                status = readable_status(bewertung)
                st.markdown(
                    f'<span class="tender-status">{escape(status)}</span>',
                    unsafe_allow_html=True,
                )

            if has_display_value(auftraggeber):
                st.caption(f"Auftraggeber · {str(auftraggeber).strip()}")

        if score_column is not None:
            with score_column:
                st.metric("Score", score)

        render_metadata(metadata)

        has_details = (
            has_display_value(beschreibung)
            or bool(positive_hits)
            or bool(negative_hits)
            or bool(score_reasons)
            or bool(links)
        )
        if has_details:
            with st.expander("Details & Links", icon=":material/info:"):
                if has_display_value(beschreibung):
                    st.markdown("**Beschreibung**")
                    st.write(str(beschreibung).strip())

                if positive_hits:
                    st.markdown("**Positive Signale**")
                    st.write(", ".join(readable_tag(item) for item in positive_hits))

                if negative_hits:
                    st.markdown("**Negative Signale**")
                    st.write(", ".join(readable_tag(item) for item in negative_hits))

                if score_reasons:
                    st.markdown("**Bewertungsgründe**")
                    reasons = "".join(
                        f"<li>{escape(str(reason).strip())}</li>" for reason in score_reasons
                    )
                    st.markdown(
                        f'<ul class="tender-reasons">{reasons}</ul>',
                        unsafe_allow_html=True,
                    )

                render_links(links)


def render_section(title: str, tenders: list[dict]):
    st.subheader(f"{title} ({len(tenders)})")

    if not tenders:
        st.info("Keine Einträge vorhanden.", icon=":material/inbox:")
        return

    for tender in tenders:
        render_tender_card(tender)


def main():
    inject_styles()
    check_login()
    init_session_state()

    render_brand_header()

    if st.session_state.scan_done_message:
        st.success(st.session_state.scan_done_message)
        st.session_state.scan_done_message = ""

    if st.session_state.analyse_done_message:
        st.success(st.session_state.analyse_done_message)
        st.session_state.analyse_done_message = ""

    with st.sidebar:
        st.header(":material/filter_alt: Filter", anchor=False)

        if st.button(
            "Abmelden",
            icon=":material/logout:",
            use_container_width=True,
        ):
            st.session_state.logged_in = False
            st.rerun()

        search_term = st.text_input(
            "Suche",
            placeholder="Titel, Auftraggeber oder ID",
        )
        sort_option = st.selectbox(
            "Sortierung",
            ["Score absteigend", "Score aufsteigend", "Frist", "Titel A-Z"]
        )

        st.divider()
        st.caption("ERGEBNISÜBERSICHT")
        stats_left, stats_right = st.columns(2)
        with stats_left:
            st.metric("Passend", len(st.session_state.passende))
            st.metric("Nicht aktiv", len(st.session_state.nicht_aktiv))
        with stats_right:
            st.metric("Manuell", len(st.session_state.manuell))
            st.metric("Nicht passend", len(st.session_state.nicht_passend))

    irgendwas_laeuft = st.session_state.scan_running or st.session_state.analyse_running

    if st.button(
        "Ausschreibungen finden",
        icon=":material/search:",
        use_container_width=True,
        disabled=irgendwas_laeuft,
        type="primary",
    ):
        st.session_state.scan_running = True
        st.rerun()

    if st.session_state.scan_running:
        run_full_search()
        st.session_state.scan_running = False
        st.session_state.analyse_running = False
        st.rerun()

    st.divider()

    if not st.session_state.daten_geladen:
        render_initial_empty_state()
        return

    passende = sort_tenders(
        filter_tenders_by_search(st.session_state.passende, search_term),
        sort_option
    )
    manuell = sort_tenders(
        filter_tenders_by_search(st.session_state.manuell, search_term),
        sort_option
    )
    nicht_aktiv = sort_tenders(
        filter_tenders_by_search(st.session_state.nicht_aktiv, search_term),
        sort_option
    )
    nicht_passend = sort_tenders(
        filter_tenders_by_search(st.session_state.nicht_passend, search_term),
        sort_option
    )

    tab1, tab2, tab3, tab4 = st.tabs([
        ":material/check_circle: PASSEND",
        ":material/rule: MANUELL",
        ":material/inventory_2: NICHT AKTIV",
        ":material/cancel: NICHT PASSEND",
    ])

    with tab1:
        render_section("Passende Ausschreibungen", passende)

    with tab2:
        render_section("Manuell prüfen", manuell)

    with tab3:
        render_section("Nicht aktiv", nicht_aktiv)

    with tab4:
        render_section("Nicht passend", nicht_passend)


if __name__ == "__main__":
    main()
