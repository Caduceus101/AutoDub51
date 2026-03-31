import subprocess
import json
import os
from utils.logger import log


def parse_mkv(file_path):
    if not os.path.exists(file_path):
        log.error(f"Dosya bulunamadı: {file_path}")
        return []

    cmd = [
        "ffprobe", "-v", "quiet", "-print_format", "json",
        "-show_streams", "-select_streams", "a", file_path
    ]

    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        data = json.loads(result.stdout)

        audio_tracks = []
        for stream in data.get('streams', []):
            tags = stream.get('tags', {})
            language = tags.get('language', 'Bilinmiyor').upper()
            channels = stream.get('channels', 2)
            codec = stream.get('codec_name', 'Bilinmiyor').upper()

            display_name = f"Track {stream['index']}: {language} | {channels} Kanal | {codec}"

            audio_tracks.append({
                "index": stream['index'],
                "language": language,
                "channels": channels,
                "codec": codec,
                "display_name": display_name
            })

        log.info(f"MKV Analizi Başarılı: {len(audio_tracks)} ses kanalı bulundu.")
        return audio_tracks

    except Exception as e:
        log.error(f"FFprobe analiz hatası: {e}")
        return []