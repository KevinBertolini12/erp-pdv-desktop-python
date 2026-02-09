import threading
import time
import logging

import uvicorn
from PySide6.QtWidgets import QApplication

from app.api.server import create_app
from app.core.config import settings
from app.core.logging import setup_logging
from app.ui.main_window import MainWindow


def run_api():
    app = create_app()
    uvicorn.run(app, host=settings.api_host, port=settings.api_port, log_level="info")


def main():
    setup_logging(logging.INFO)

    t = threading.Thread(target=run_api, daemon=True)
    t.start()
    time.sleep(0.5)

    qt = QApplication([])
    w = MainWindow(settings.api_base_url)
    w.show()
    qt.exec()


if __name__ == "__main__":
    main()
