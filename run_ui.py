from __future__ import annotations

import os
import time
import threading
import webbrowser

import uvicorn

from paths import ensure_user_data_initialized, packaged_root


def main():
    # Initiera användardata
    p = ensure_user_data_initialized()

    # Peka appen mot templates i paketet och data i användarmappen
    os.environ["TEMPLATES_DIR"] = str(packaged_root() / "templates")
    os.environ["DATA_DIR"] = str(p["data"])

    host = "127.0.0.1"
    port = 8000
    url = f"http://{host}:{port}/"

    def open_browser():
        time.sleep(1.0)
        webbrowser.open(url)

    threading.Thread(target=open_browser, daemon=True).start()

    uvicorn.run("app:app", host=host, port=port, log_level="info")


if __name__ == "__main__":
    main()
