from PySide6.QtWidgets import QWidget, QVBoxLayout, QComboBox, QGroupBox

class TrackSelector(QWidget):
    """Kullanıcının Türkçe ve İngilizce ses kanallarını seçtiği arayüz bileşeni."""
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # 1. Grup: Türkçe Ses Seçimi
        self.group_tr = QGroupBox("1. Merkez (Diyalog) Yapılacak Türkçe Ses Kanalı:")
        tr_layout = QVBoxLayout()
        self.cb_tr_track = QComboBox()
        tr_layout.addWidget(self.cb_tr_track)
        self.group_tr.setLayout(tr_layout)

        # 2. Grup: İngilizce 5.1 Ses Seçimi
        self.group_en = QGroupBox("2. Efekt (Surround) Alınacak Orijinal Kanal (5.1):")
        en_layout = QVBoxLayout()
        self.cb_en_track = QComboBox()
        en_layout.addWidget(self.cb_en_track)
        self.group_en.setLayout(en_layout)

        layout.addWidget(self.group_tr)
        layout.addWidget(self.group_en)

    def load_tracks(self, tracks):
        """MKV'den okunan ses listesini menülere doldurur."""
        self.cb_tr_track.clear()
        self.cb_en_track.clear()
        for track in tracks:
            self.cb_tr_track.addItem(track["display_name"], track["index"])
            self.cb_en_track.addItem(track["display_name"], track["index"])

    def get_selections(self):
        """Seçilen kanalların index numaralarını döndürür."""
        return {
            "tr_idx": self.cb_tr_track.currentData(),
            "en_idx": self.cb_en_track.currentData()
        }

    def set_active(self, state):
        """İşlem sırasında menüleri dondurmak için kullanılır."""
        self.cb_tr_track.setEnabled(state)
        self.cb_en_track.setEnabled(state)