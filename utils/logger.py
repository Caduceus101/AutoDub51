import logging
import os


def setup_logger():
    os.makedirs("logs", exist_ok=True)
    logger = logging.getLogger("AutoDub51")
    logger.setLevel(logging.DEBUG)

    # Dosyaya yazdırılacaklar
    fh = logging.FileHandler("logs/autodub.log", encoding="utf-8")
    fh.setLevel(logging.DEBUG)

    # Konsola (Terminale) yazdırılacaklar
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%H:%M:%S')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger


log = setup_logger()