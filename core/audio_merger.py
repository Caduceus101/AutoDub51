import os
import subprocess
from utils.logger import log


def extract_audio_track(mkv_path, track_index, output_wav):
    """MKV içindeki belirli bir ses kanalını WAV olarak dışarı aktarır."""
    log.info(f"Ses dışarı aktarılıyor: Track {track_index}")
    cmd = [
        "ffmpeg", "-y", "-i", mkv_path,
        "-map", f"0:{track_index}",
        "-c:a", "pcm_s24le",  # 24-bit kayıpsız stüdyo formatı
        output_wav
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    return output_wav


def split_51_audio(input_51_wav, output_dir):
    """5.1 surround WAV dosyasını 6 ayrı mono WAV dosyasına böler."""
    log.info("5.1 ses kanalları bileşenlerine ayrılıyor...")
    os.makedirs(output_dir, exist_ok=True)

    channels = {
        "FL.wav": "FL", "FR.wav": "FR", "FC.wav": "FC",
        "LFE.wav": "LFE", "BL.wav": "BL", "BR.wav": "BR"
    }

    output_files = {}
    for filename, channel in channels.items():
        out_path = os.path.join(output_dir, filename)
        # Sadece belirli bir kanalı (örneğin FC - Front Center) filtreleyip çıkarır
        cmd = [
            "ffmpeg", "-y", "-i", input_51_wav,
            "-filter_complex", f"channelsplit=channel_layout=5.1[FL][FR][FC][LFE][BL][BR]",
            "-map", f"[{channel}]",
            "-c:a", "pcm_s24le", out_path
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        output_files[channel] = out_path

    return output_files


def mix_new_center(turkish_vocals_wav, english_effects_wav, output_center_wav):
    """AI'dan gelen Türkçe Vokaller ile İngilizce Merkez efektlerini birleştirir ve Mono yapar."""
    log.info("Yeni mükemmel Merkez (Center) kanalı oluşturuluyor (Türkçe Ses + Orijinal Efektler)...")
    cmd = [
        "ffmpeg", "-y",
        "-i", turkish_vocals_wav,
        "-i", english_effects_wav,
        "-filter_complex", "amix=inputs=2:duration=longest:weights=1 1",
        "-ac", "1",  # EKLENEN KRİTİK KOD: Çıktıyı kesinlikle Mono (Tek Kanal) yap!
        output_center_wav
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    return output_center_wav


def build_final_51_and_mux(original_mkv, fl, fr, new_fc, lfe, bl, br, output_mkv):
    """6 mono kanalı birleştirip 5.1 yapar ve orijinal videoyla kayıpsız birleştirir."""
    log.info("Yeni 5.1 ses paketi oluşturuluyor ve videoya entegre ediliyor...")

    # 6 ayrı ses dosyasını tek bir 5.1 akışında birleştiren karmaşık FFmpeg filtresi
    cmd = [
        "ffmpeg", "-y",
        "-i", original_mkv,
        "-i", fl, "-i", fr, "-i", new_fc, "-i", lfe, "-i", bl, "-i", br,
        "-filter_complex",
        "[1:a][2:a][3:a][4:a][5:a][6:a]join=inputs=6:channel_layout=5.1:map=0.0-FL|1.0-FR|2.0-FC|3.0-LFE|4.0-BL|5.0-BR[a]",
        "-map", "0:v",  # Orijinal videoyu kopyala
        "-map", "[a]",  # Yeni oluşturulan 5.1 sesi al
        "-c:v", "copy",  # Görüntü kalitesini BOZMA (Render süresini sıfırlar)
        "-c:a", "flac",  # Sesi kayıpsız ve yüksek kaliteli FLAC formatında sıkıştır
        output_mkv
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    log.info(f"İşlem Tamamlandı! Yeni film dosyanız hazır: {output_mkv}")
    return output_mkv