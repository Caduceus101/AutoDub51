#  AutoDub51: AI-Powered 5.1 Surround Dubbing Engine

AutoDub51, MKV dosyalarındaki orijinal 5.1 ses kanallarını bozmadan, yapay zeka desteğiyle yüksek kalitede Türkçe dublaj entegrasyonu sağlayan bir masaüstü uygulamasıdır.

##  Öne Çıkan Özellikler
- **AI Destekli Ayrıştırma:** Facebook'un `Demucs` modelini kullanarak Türkçe vokal temizleme ve İngilizce merkez kanal efekt süzme.
- **5.1 Surround Koruma:** Orijinal sesin çevresel (surround) ve düşük frekans (LFE) etkilerini koruyarak sadece merkez (center) kanalı yeniden inşa eder.
- **Donanım Hızlandırma:** Apple Silicon (MPS) ve NVIDIA (CUDA) otomatik algılama ve GPU kullanımı.
- **Modern Arayüz:** PySide6 ile geliştirilmiş kullanıcı dostu sürükle-bırak destekli GUI.

##  Teknik Mimari
Proje modüler bir yapı üzerine inşa edilmiştir:
- **`core/`**: MKV analizi, FFmpeg ile ses işleme ve Demucs AI entegrasyonu.
- **`gui/`**: Özel tasarlanmış kanal seçici ve terminal görünümlü işlem konsolu.
- **`utils/`**: Donanım kontrolü ve gelişmiş loglama sistemi.

##  Kurulum ve Gereksinimler
Bu projenin çalışması için sisteminizde aşağıdaki araçların kurulu olması gerekir:
- Python 3.10+
- **FFmpeg** & **FFprobe** (Sistem yoluna eklenmiş olmalı).
- **Demucs** (AI motoru için).

