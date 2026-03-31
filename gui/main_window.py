import os
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QLabel,
                               QPushButton, QMessageBox)
from PySide6.QtCore import Qt, QThread, Signal
import shutil

# Çekirdek modüllerimizi içe aktarıyoruz
from core.mkv_parser import parse_mkv
from core.audio_merger import extract_audio_track, split_51_audio, mix_new_center, build_final_51_and_mux
from core.ai_separator import run_demucs
from utils.hardware_check import get_optimal_device
from utils.logger import log

# YENİ: Arayüz modüllerimiz (Kendi yazdığımız özel bileşenler)
from gui.track_selector import TrackSelector
from gui.progress_bar import ProgressConsole


class DubbingWorker(QThread):
    """Arka planda AI ve FFmpeg işlemlerini yürüten işçi (Thread)"""
    log_signal = Signal(str)
    progress_signal = Signal(int)  # İlerleme çubuğunu dolduracak sinyal
    finished_signal = Signal(bool, str)

    def __init__(self, mkv_path, tr_track_idx, en_track_idx):
        super().__init__()
        self.mkv_path = mkv_path
        self.tr_track_idx = tr_track_idx
        self.en_track_idx = en_track_idx
        self.device = get_optimal_device()

    def run(self):
        try:
            self.progress_signal.emit(5)
            self.log_signal.emit("İşlem Başlıyor... Geçici çalışma klasörü oluşturuluyor.")
            temp_dir = os.path.join(os.path.dirname(self.mkv_path), "AutoDub_Temp")
            os.makedirs(temp_dir, exist_ok=True)

            # ADIM 1: Sesleri Dışarı Aktar
            tr_wav = os.path.join(temp_dir, "TR_Source.wav")
            en_wav = os.path.join(temp_dir, "EN_Source_51.wav")

            self.log_signal.emit(f"[1/6] Türkçe Ses (Track {self.tr_track_idx}) dışarı aktarılıyor...")
            extract_audio_track(self.mkv_path, self.tr_track_idx, tr_wav)
            self.progress_signal.emit(15)

            self.log_signal.emit(f"[2/6] Orijinal 5.1 Ses (Track {self.en_track_idx}) dışarı aktarılıyor...")
            extract_audio_track(self.mkv_path, self.en_track_idx, en_wav)
            self.progress_signal.emit(25)

            # ADIM 2: 5.1 Sesi Parçala
            self.log_signal.emit("[3/6] Orijinal 5.1 Ses 6 mono kanala bölünüyor...")
            split_files = split_51_audio(en_wav, temp_dir)
            en_center_wav = split_files["FC"]  # Orijinal İngilizce Merkez Kanalı
            self.progress_signal.emit(35)

            # ADIM 3: Yapay Zeka (Demucs) İşlemleri
            self.log_signal.emit(
                f"[4/6] AI Motoru Türkçe Vokalleri temizliyor (Donanım: {self.device.upper()})... Bu aşama biraz sürebilir.")
            tr_vocals_clean = run_demucs(tr_wav, temp_dir, target="vocals", device=self.device)
            if not tr_vocals_clean:
                raise Exception("Türkçe vokal temizleme başarısız oldu!")
            self.progress_signal.emit(60)

            self.log_signal.emit(
                f"[5/6] AI Motoru İngilizce Merkez Kanalından efektleri süzüyor... Bu aşama biraz sürebilir.")
            en_effects_clean = run_demucs(en_center_wav, temp_dir, target="effects", device=self.device)
            if not en_effects_clean:
                raise Exception("İngilizce efekt süzme başarısız oldu!")
            self.progress_signal.emit(85)

            # ADIM 4: Yeni Merkezi Oluştur ve Paketle
            self.log_signal.emit("[6/6] Yeni Mükemmel Merkez (Center) kanalı oluşturuluyor ve MKV paketleniyor...")
            new_center_wav = os.path.join(temp_dir, "NEW_Center.wav")
            mix_new_center(tr_vocals_clean, en_effects_clean, new_center_wav)

            output_mkv = os.path.join(os.path.dirname(self.mkv_path), f"AutoDub_{os.path.basename(self.mkv_path)}")

            build_final_51_and_mux(
                self.mkv_path,
                split_files["FL"], split_files["FR"], new_center_wav,
                split_files["LFE"], split_files["BL"], split_files["BR"],
                output_mkv
            )
            self.progress_signal.emit(95)

            # Temizlik
            self.log_signal.emit("Geçici dosyalar temizleniyor...")
            shutil.rmtree(temp_dir, ignore_errors=True)

            self.progress_signal.emit(100)
            self.finished_signal.emit(True, f"İşlem Başarıyla Tamamlandı!\nDosya: {output_mkv}")

        except Exception as e:
            self.progress_signal.emit(0)
            self.finished_signal.emit(False, str(e))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AutoDub51 - Stüdyo Kalitesinde Senkron Motoru")
        self.resize(750, 550)  # Modüller sığsın diye arayüzü biraz daha genişlettik
        self.setAcceptDrops(True)
        self.mkv_path = None
        self.audio_tracks = []
        self.setup_ui()

    def setup_ui(self):
        widget = QWidget()
        layout = QVBoxLayout()

        # 1. Sürükle Bırak Alanı
        self.lbl_drop = QLabel("MKV Dosyasını Buraya Sürükleyin")
        self.lbl_drop.setAlignment(Qt.AlignCenter)
        self.lbl_drop.setStyleSheet("border: 2px dashed #aaa; border-radius: 10px; padding: 30px; font-size: 16px;")
        layout.addWidget(self.lbl_drop)

        # 2. TrackSelector Modülü (Sesleri seçtiğimiz menüler)
        self.selector = TrackSelector()
        layout.addWidget(self.selector)

        # 3. Başlat Butonu
        self.btn_start = QPushButton("Dublajı Başlat ve 5.1 Paketi Oluştur")
        self.btn_start.setFixedHeight(45)
        self.btn_start.setEnabled(False)
        self.btn_start.clicked.connect(self.start_processing)
        self.btn_start.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(self.btn_start)

        # 4. ProgressConsole Modülü (İlerleme çubuğu ve Hacker ekranı)
        self.console = ProgressConsole()
        layout.addWidget(self.console)

        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls() and event.mimeData().urls()[0].toLocalFile().endswith('.mkv'):
            event.acceptProposedAction()

    def dropEvent(self, event):
        file_path = event.mimeData().urls()[0].toLocalFile()
        self.mkv_path = file_path
        self.lbl_drop.setText(f"Seçilen Dosya:\n{os.path.basename(file_path)}")
        self.load_tracks(file_path)

    def load_tracks(self, file_path):
        self.console.reset_console()
        self.console.append_log("Dosya analiz ediliyor...")

        self.audio_tracks = parse_mkv(file_path)
        if not self.audio_tracks:
            self.console.append_log("Hata: Dosyada ses kanalı bulunamadı veya FFprobe çalışmadı.")
            return

        # Dışarıdaki modüle verileri gönderiyoruz
        self.selector.load_tracks(self.audio_tracks)

        self.btn_start.setEnabled(True)
        self.console.append_log(f"{len(self.audio_tracks)} ses kanalı bulundu. Lütfen eşleştirmeleri yapın.")

    def start_processing(self):
        # Dışarıdaki modülden seçimleri alıyoruz
        selections = self.selector.get_selections()
        tr_idx = selections["tr_idx"]
        en_idx = selections["en_idx"]

        if tr_idx is None or en_idx is None:
            QMessageBox.warning(self, "Hata", "Lütfen her iki kanal için de seçim yapın!")
            return

        if tr_idx == en_idx:
            QMessageBox.warning(self, "Hata", "Aynı ses kanalını iki farklı görev için seçemezsiniz!")
            return

        # Arayüzü kilitle ve konsolu sıfırla
        self.btn_start.setEnabled(False)
        self.selector.set_active(False)
        self.console.reset_console()

        # İş parçacığını (Thread) başlat
        self.worker = DubbingWorker(self.mkv_path, tr_idx, en_idx)

        # Sinyalleri yeni ProgressConsole modülümüze bağlıyoruz
        self.worker.log_signal.connect(self.console.append_log)
        self.worker.progress_signal.connect(self.console.set_progress)
        self.worker.finished_signal.connect(self.process_finished)

        self.worker.start()

    def process_finished(self, success, message):
        self.console.append_log("\n" + message)
        self.btn_start.setEnabled(True)
        self.selector.set_active(True)  # Menülerin kilidini aç

        if success:
            QMessageBox.information(self, "Başarılı", "Yeni 5.1 dublajlı MKV dosyanız oluşturuldu!")
        else:
            QMessageBox.critical(self, "Hata", f"İşlem sırasında bir hata oluştu:\n{message}")