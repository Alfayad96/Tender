import io
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


# =========================================
# LOGIN-DATEN
# =========================================
APP_USERNAME = "qm"
APP_PASSWORD = "1234"


st.set_page_config(
    page_title="Tender Radar",
    page_icon="📡",
    layout="wide"
)


def check_login():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        st.title("🔐 Login erforderlich")
        st.caption("Bitte mit den Zugangsdaten anmelden, um Tender Radar zu öffnen.")

        username = st.text_input("Benutzername")
        password = st.text_input("Passwort", type="password")

        if st.button("Login", use_container_width=True):
            if username == APP_USERNAME and password == APP_PASSWORD:
                st.session_state.logged_in = True
                st.success("Login erfolgreich.")
                st.rerun()
            else:
                st.error("Falscher Benutzername oder falsches Passwort.")

        st.stop()


def safe_value(value, fallback="—"):
    return fallback if value in (None, "") else value


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
        # Beispiel: FORTSCHRITT: Seite 3 von 12 wird geladen ...
        parts = line.split()
        try:
            current = int(parts[2])
            total = int(parts[4])
            if total > 0:
                return int((current / total) * 100)
        except Exception:
            return None

    if "[" in line and "/" in line and "]" in line:
        # Beispiel: FORTSCHRITT: [8/143] Verarbeite: ...
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
    def __init__(self, status_box, progress_bar, log_box):
        self.status_box = status_box
        self.progress_bar = progress_bar
        self.log_box = log_box
        self.buffer = ""
        self.lines = []
        self.last_progress = 0

    def write(self, text):
        if not text:
            return 0

        self.buffer += text

        while "\n" in self.buffer:
            line, self.buffer = self.buffer.split("\n", 1)
            clean_line = line.rstrip()

            if clean_line:
                self.lines.append(clean_line)

                parsed = parse_status_line(clean_line)
                if parsed:
                    self.status_box.info(parsed["message"])

                progress = extract_progress_percent(clean_line)
                if progress is not None:
                    self.last_progress = progress
                    self.progress_bar.progress(progress)

                self.log_box.code("\n".join(self.lines[-12:]), language="bash")

        return len(text)

    def flush(self):
        if self.buffer.strip():
            clean_line = self.buffer.rstrip()
            self.lines.append(clean_line)

            parsed = parse_status_line(clean_line)
            if parsed:
                self.status_box.info(parsed["message"])

            progress = extract_progress_percent(clean_line)
            if progress is not None:
                self.last_progress = progress
                self.progress_bar.progress(progress)

            self.log_box.code("\n".join(self.lines[-12:]), language="bash")

        self.buffer = ""


def run_with_live_output(fn, title: str):
    st.subheader(title)

    status_box = st.empty()
    progress_bar = st.progress(0)
    log_box = st.empty()

    writer = StreamlitLogWriter(status_box, progress_bar, log_box)

    try:
        status_box.info(f"{title} läuft ...")
        with redirect_stdout(writer), redirect_stderr(writer):
            fn()

        writer.flush()
        progress_bar.progress(100)
        status_box.success(f"{title} erfolgreich abgeschlossen.")
        return True
    except Exception as e:
        writer.flush()
        status_box.error(f"{title} wurde mit Fehler beendet: {e}")
        return False


def run_marktscan_live():
    try:
        success = run_with_live_output(run_marktscan, "Marktscan")
        return success
    finally:
        st.session_state.scan_running = False


def run_relevanzanalyse_live():
    try:
        success = run_with_live_output(run_relevanzanalyse, "Relevanzanalyse")
        return success
    finally:
        st.session_state.analyse_running = False


def render_links(tender: dict):
    detail_url = tender.get("final_detail_url") or tender.get("detail_url")
    verfahrens_url = tender.get("final_verfahrensangaben_url") or tender.get("verfahrensangaben_url")
    externe_url = tender.get("externe_info_url")

    col1, col2, col3 = st.columns(3)

    with col1:
        if detail_url:
            st.link_button("Zur Ausschreibung", detail_url, use_container_width=True)

    with col2:
        if verfahrens_url:
            st.link_button("Verfahrensangaben", verfahrens_url, use_container_width=True)

    with col3:
        if externe_url:
            st.link_button("Externe Infos", externe_url, use_container_width=True)


def render_tender_card(tender: dict):
    titel = safe_value(tender.get("titel"))
    score = safe_value(tender.get("score"))
    bewertung = safe_value(tender.get("bewertung"))
    auftraggeber = safe_value(tender.get("auftraggeber"))
    frist = safe_value(
        tender.get("abgabefrist_detail")
        or tender.get("angebots_teilnahmefrist")
        or tender.get("frist")
    )
    ausschreibungs_id = safe_value(tender.get("ausschreibungs_id"))
    vergabe_nr = safe_value(tender.get("vergabe_nr"))
    ort = safe_value(tender.get("ort"))
    beschreibung = safe_value(tender.get("beschreibung_leistung"))
    positive_hits = tender.get("positive_hits", [])
    negative_hits = tender.get("negative_hits", [])
    score_reasons = tender.get("score_reasons", [])

    with st.container(border=True):
        col1, col2 = st.columns([4, 1])

        with col1:
            st.subheader(titel)
            st.write(f"**Bewertung:** {bewertung}")
            st.write(f"**Auftraggeber:** {auftraggeber}")

        with col2:
            st.metric("Score", score)

        info1, info2 = st.columns(2)

        with info1:
            st.write(f"**Frist:** {frist}")
            st.write(f"**Ausschreibungs-ID:** {ausschreibungs_id}")

        with info2:
            st.write(f"**Vergabe-Nr.:** {vergabe_nr}")
            st.write(f"**Ort:** {ort}")

        with st.expander("Details"):
            st.write(f"**Beschreibung:** {beschreibung}")

            st.write("**Positive Hits:**")
            st.write(", ".join(positive_hits) if positive_hits else "—")

            st.write("**Negative Hits:**")
            st.write(", ".join(negative_hits) if negative_hits else "—")

            st.write("**Score-Gründe:**")
            if score_reasons:
                for reason in score_reasons:
                    st.write(f"- {reason}")
            else:
                st.write("—")

            render_links(tender)


def render_section(title: str, tenders: list[dict]):
    st.subheader(f"{title} ({len(tenders)})")

    if not tenders:
        st.info("Keine Einträge vorhanden.")
        return

    for tender in tenders:
        render_tender_card(tender)


def main():
    check_login()
    init_session_state()

    st.title("📡 Tender Radar")
    st.caption("Suche, Analyse und Bewertung von Ausschreibungen für QM Interactive")

    if st.session_state.scan_done_message:
        st.success(st.session_state.scan_done_message)
        st.session_state.scan_done_message = ""

    if st.session_state.analyse_done_message:
        st.success(st.session_state.analyse_done_message)
        st.session_state.analyse_done_message = ""

    with st.sidebar:
        st.header("Filter")

        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()

        search_term = st.text_input("Suche")
        sort_option = st.selectbox(
            "Sortierung",
            ["Score absteigend", "Score aufsteigend", "Frist", "Titel A-Z"]
        )

        st.divider()
        st.write(f"**Passend:** {len(st.session_state.passende)}")
        st.write(f"**Manuell prüfen:** {len(st.session_state.manuell)}")
        st.write(f"**Nicht aktiv:** {len(st.session_state.nicht_aktiv)}")
        st.write(f"**Nicht passend:** {len(st.session_state.nicht_passend)}")

    irgendwas_laeuft = st.session_state.scan_running or st.session_state.analyse_running

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button(
            "📡 Marktscan",
            use_container_width=True,
            disabled=irgendwas_laeuft
        ):
            st.session_state.scan_running = True
            st.rerun()

    with col2:
        if st.button(
            "🎯 Relevanz analysieren",
            use_container_width=True,
            disabled=irgendwas_laeuft
        ):
            st.session_state.analyse_running = True
            st.rerun()

    with col3:
        if st.button(
            "🔄 Neu laden",
            use_container_width=True,
            disabled=irgendwas_laeuft
        ):
            load_results_into_session()
            st.session_state.has_current_run_results = True
            st.success("Ergebnisse wurden neu geladen.")

    if st.session_state.scan_running:
        clear_session_results()
        success = run_marktscan_live()
        if success:
            st.session_state.scan_done_message = "Marktscan ist fertig."
        st.rerun()

    if st.session_state.analyse_running:
        success = run_relevanzanalyse_live()
        if success:
            load_results_into_session()
            st.session_state.has_current_run_results = True
            st.session_state.analyse_done_message = "Relevanzanalyse ist fertig."
        st.rerun()

    st.divider()

    if not st.session_state.daten_geladen:
        st.info("Noch keine Ergebnisse geladen. Bitte zuerst Marktscan und danach Relevanz analysieren ausführen.")
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
        "✅ PASSEND",
        "⚠️ MANUELL",
        "📦 NICHT AKTIV",
        "❌ NICHT PASSEND",
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
