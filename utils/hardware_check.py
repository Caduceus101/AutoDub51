import torch
import platform
import subprocess
from utils.logger import log

def get_optimal_device():
    if torch.cuda.is_available():
        device = "cuda"
        name = torch.cuda.get_device_name(0)
        log.info(f"Donanım: CUDA (Nvidia) Aktif - {name}")
        return device
    elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        log.info("Donanım: MPS (Apple Silicon) Aktif")
        return "mps"
    else:
        log.info(f"Donanım: CPU ({platform.system()})")
        return "cpu"

def check_ffmpeg():
    try:
        subprocess.run(["ffmpeg", "-version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        log.info("Sistem: FFmpeg hazır.")
        return True
    except FileNotFoundError:
        log.error("Kritik Hata: FFmpeg bulunamadı! Lütfen sisteme kurun.")
        return False