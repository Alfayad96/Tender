import os
import sys
import time
import socket
import threading
import webbrowser
import traceback

HOST = "127.0.0.1"
PORT = 8502


def get_base_dir():
    if getattr(sys, "frozen", False):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))


def get_log_dir():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def log_message(message: str):
    log_path = os.path.join(get_log_dir(), "tender_radar_debug.log")
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(message + "\n")


def is_port_open(host=HOST, port=PORT):
    try:
        with socket.create_connection((host, port), timeout=1):
            return True
    except OSError:
        return False


def get_streamlit_app_path():
    base_dir = get_base_dir()
    return os.path.join(base_dir, "app", "gui", "streamlit_app.py")


def open_browser_once():
    url = f"http://{HOST}:{PORT}"
    for _ in range(60):
        if is_port_open():
            log_message(f"Browser wird geöffnet: {url}")
            webbrowser.open_new_tab(url)
            return
        time.sleep(0.5)
    log_message("Server wurde nicht rechtzeitig erreichbar.")


def main():
    log_message("=" * 60)
    log_message("Programmstart")
    log_message(f"sys.executable = {sys.executable}")
    log_message(f"base_dir = {get_base_dir()}")

    app_file = get_streamlit_app_path()
    log_message(f"Erwartete Streamlit-Datei: {app_file}")

    if not os.path.exists(app_file):
        raise FileNotFoundError(f"Streamlit-Datei nicht gefunden: {app_file}")

    if is_port_open():
        log_message("Port ist bereits offen. Öffne Browser direkt.")
        webbrowser.open_new_tab(f"http://{HOST}:{PORT}")
        return

    browser_thread = threading.Thread(target=open_browser_once, daemon=True)
    browser_thread.start()

    log_message("Importiere streamlit.web.bootstrap ...")
    from streamlit.web import bootstrap

    log_message("Starte Streamlit ...")
    bootstrap.run(
        app_file,
        False,
        [],
        {
            "server.headless": True,
            "browser.gatherUsageStats": False,
            "server.port": PORT,
            "server.address": HOST,
        },
    )


if __name__ == "__main__":
    try:
        main()
    except Exception:
        error_text = traceback.format_exc()
        log_message("FEHLER:")
        log_message(error_text)
        raise