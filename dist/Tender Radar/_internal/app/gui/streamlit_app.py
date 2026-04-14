import os
import sys
import subprocess
import streamlit as st

from app.services.tender_service import (
    load_passende_tender,
    load_manuell_pruefen_tender,
    load_nicht_passende_tender,
    load_nicht_aktive_tender,
    filter_tenders_by_search,
    sort_tenders,
)

st.set_page_config(
    page_title="Tender Radar",
    page_icon="📡",
    layout="wide"
)

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
PYTHON_EXE = sys.executable


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


def parse_status_line(line: str):
    if not line.startswith("STATUS|"):
        return None

    data = {}
    parts = line.strip().split("|")[1:]

    for part in parts:
        if "=" in part:
            key, value = part.split("=", 1)
            data[key.strip()] = value.strip()

    return data


def format_status(data: dict) -> str:
    phase = data.get("phase", "")
    message = data.get("message", "")
    current = data.get("current")
    total = data.get("total")
    count = data.get("count")
    total_pages = data.get("total_pages")

    if message:
        return message

    if phase == "start":
        return "Prozess wurde gestartet ..."
    if phase == "search":
        return "Ausschreibungen werden gesucht ..."
    if phase == "pages_found":
        return f"{total_pages} Seiten wurden gefunden."
    if phase == "page_progress":
        return f"Seite {current} von {total} wird geladen ..."
    if phase == "tenders_found":
        return f"{count} Ausschreibungen wurden gefunden."
    if phase == "collecting":
        return "Ausschreibungen werden jetzt geholt und verarbeitet ..."
    if phase == "detail_loading":
        return "Detailseiten werden geladen ..."
    if phase == "verfahrens_loading":
        return "Verfahrensangaben werden geladen ..."
    if phase == "item_progress":
        return f"Ausschreibung {current} von {total} wird verarbeitet ..."
    if phase == "scoring_start":
        return "Analyse wurde gestartet ..."
    if phase == "scoring_loading":
        return "Bewertbare Daten werden geladen ..."
    if phase == "scoring_mit":
        return "Ausschreibungen mit Verfahrensangaben werden bewertet ..."
    if phase == "scoring_ohne":
        return "Ausschreibungen ohne Verfahrensangaben werden bewertet ..."
    if phase == "sorting":
        return "Ergebnisse werden sortiert ..."
    if phase == "saving":
        return "Dateien werden gespeichert ..."
    if phase == "done":
        return "Prozess abgeschlossen."
    if phase == "error":
        return "Ein Fehler ist aufgetreten."

    return "Prozess läuft ..."


def get_progress(data: dict):
    phase = data.get("phase", "")
    current = data.get("current")
    total = data.get("total")

    if phase in {"page_progress", "item_progress"} and current and total:
        try:
            current_int = int(current)
            total_int = int(total)
            if total_int > 0:
                return int((current_int / total_int) * 100)
        except ValueError:
            return None

    return None


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


def run_script_live(script_name: str, title: str):
    script_path = os.path.join(BASE_DIR, script_name)

    if not os.path.exists(script_path):
        st.error(f"Datei nicht gefunden: {script_path}")
        return False

    st.subheader(title)

    status_box = st.empty()
    progress_bar = st.progress(0)
    log_box = st.empty()

    output_lines = []
    last_progress = 0

    try:
        process = subprocess.Popen(
            [PYTHON_EXE, "-u", script_path],
            cwd=BASE_DIR,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )

        for line in iter(process.stdout.readline, ""):
            if not line:
                break

            clean_line = line.rstrip()
            output_lines.append(clean_line)

            status_data = parse_status_line(clean_line)

            if status_data:
                status_box.info(format_status(status_data))

                progress = get_progress(status_data)
                if progress is not None:
                    progress_bar.progress(progress)
                    last_progress = progress

            log_box.code("\n".join(output_lines[-6:]), language="bash")

        process.wait()

        if process.returncode == 0:
            if last_progress < 100:
                progress_bar.progress(100)

            status_box.success(f"{title} erfolgreich abgeschlossen.")
            return True

        status_box.error(f"{title} wurde mit Fehler beendet.")
        return False

    except Exception as e:
        st.error(f"Fehler beim Starten: {e}")
        return False


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
    init_session_state()

    st.title("📡 Tender Radar")
    st.caption("Suche, Analyse und Bewertung von Ausschreibungen für QM Interactive")

    with st.sidebar:
        st.header("Filter")

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

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("📡 Marktscan", use_container_width=True):
            clear_session_results()
            success = run_script_live("run.py", "Marktscan")
            if success:
                st.info("Marktscan abgeschlossen. Bitte jetzt Relevanz analysieren ausführen.")

    with col2:
        if st.button("🎯 Relevanz analysieren", use_container_width=True):
            success = run_script_live("run_scoring.py", "Analyse")
            if success:
                load_results_into_session()
                st.session_state.has_current_run_results = True

    with col3:
        if st.button("🔄 Neu laden", use_container_width=True):
            if st.session_state.has_current_run_results:
                load_results_into_session()
                st.success("Ergebnisse dieser aktuellen Sitzung wurden neu geladen.")
            else:
                st.warning("In dieser Sitzung wurden noch keine neuen Ergebnisse erzeugt. Bitte zuerst Marktscan und Relevanz analysieren ausführen.")

    st.divider()

    if not st.session_state.daten_geladen:
        st.info("Noch keine neuen Ergebnisse geladen. Bitte zuerst Marktscan und danach Relevanz analysieren ausführen.")
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