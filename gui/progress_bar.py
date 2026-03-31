from PySide6.QtWidgets import QWidget, QVBoxLayout, QProgressBar, QTextEdit


class ProgressConsole(QWidget):
    """İşlem yüzdesini ve terminal loglarını gösteren arayüz bileşeni."""

    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Gerçek bir ilerleme çubuğu
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)

        # Terminal görünümlü log ekranı
        self.text_log = QTextEdit()
        self.text_log.setReadOnly(True)
        # Koyu arka plan ve yeşil konsol yazısı
        self.text_log.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e; 
                color: #00ff00; 
                font-family: Consolas, Courier, monospace;
                font-size: 12px;
            }
        """)

        layout.addWidget(self.progress_bar)
        layout.addWidget(self.text_log)

    def append_log(self, text):
        """Yeni bir log satırı ekler."""
        self.text_log.append(text)

    def set_progress(self, value):
        """İlerleme çubuğunun yüzdesini günceller."""
        self.progress_bar.setValue(value)

    def reset_console(self):
        """Yeni bir işleme başlarken ekranı temizler."""
        self.text_log.clear()
        self.progress_bar.setValue(0)