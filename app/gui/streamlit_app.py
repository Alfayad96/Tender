import streamlit as st

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


st.set_page_config(
    page_title="Tender Radar",
    page_icon="📡",
    layout="wide"
)


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


def run_marktscan_live():
    st.subheader("Marktscan")
    info_box = st.empty()

    try:
        info_box.info("Marktscan läuft ... Das kann einige Minuten dauern.")
        run_marktscan()
        info_box.success("Marktscan erfolgreich abgeschlossen.")
        return True
    except Exception as e:
        info_box.error(f"Fehler beim Marktscan: {e}")
        return False
    finally:
        st.session_state.scan_running = False


def run_relevanzanalyse_live():
    st.subheader("Analyse")
    info_box = st.empty()

    try:
        info_box.info("Relevanzanalyse läuft ...")
        run_relevanzanalyse()
        info_box.success("Analyse erfolgreich abgeschlossen.")
        return True
    except Exception as e:
        info_box.error(f"Fehler bei der Analyse: {e}")
        return False
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
            st.info("Marktscan abgeschlossen. Bitte jetzt Relevanz analysieren ausführen.")
        st.rerun()

    if st.session_state.analyse_running:
        success = run_relevanzanalyse_live()
        if success:
            load_results_into_session()
            st.session_state.has_current_run_results = True
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