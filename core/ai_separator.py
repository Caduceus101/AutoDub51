import os
import subprocess
from utils.logger import log


def run_demucs(input_audio_path, output_base_dir, target="vocals", device="cuda"):
    if not os.path.exists(input_audio_path):
        log.error(f"AI Girdi dosyası yok: {input_audio_path}")
        return None

    model_name = "htdemucs"
    os.makedirs(output_base_dir, exist_ok=True)

    cmd = [
        "demucs", "--two-stems", "vocals", "-n", model_name,
        "--int24", "--device", device, "--out", output_base_dir,
        input_audio_path
    ]

    log.info(f"AI Motoru Çalışıyor... Hedef: {target.upper()} | Cihaz: {device.upper()}")

    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)

        base_name = os.path.splitext(os.path.basename(input_audio_path))[0]
        demucs_output_folder = os.path.join(output_base_dir, model_name, base_name)

        vocals_path = os.path.join(demucs_output_folder, "vocals.wav")
        effects_path = os.path.join(demucs_output_folder, "no_vocals.wav")

        if target == "vocals" and os.path.exists(vocals_path):
            log.info("Vokal izolasyonu başarıyla tamamlandı.")
            return vocals_path
        elif target == "effects" and os.path.exists(effects_path):
            log.info("Efekt izolasyonu başarıyla tamamlandı.")
            return effects_path

        log.error("Demucs çıktı dosyaları oluşturulamadı.")
        return None

    except subprocess.CalledProcessError as e:
        log.error(f"Demucs AI Çöktü: {e}")
        return None