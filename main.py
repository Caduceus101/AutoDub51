import sys
from PySide6.QtWidgets import QApplication
from gui.main_window import MainWindow
from utils.logger import log


def main():
    log.info("AutoDub51 Başlatılıyor...")
    app = QApplication(sys.argv)

    # Modern koyu tema dokunuşu (Opsiyonel)
    app.setStyle("Fusion")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()