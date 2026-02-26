# IDA Yer Kontrol İstasyonu (GCS) Arayüzü

Bu proje, İnsansız Deniz Araçları (İDA) için tasarlanmış bir Yer Kontrol İstasyonu (Ground Control Station - GCS) arayüzüdür. Python ve PyQt5 kullanılarak geliştirilmiştir.

## Özellikler

- Telemetri verilerini (Hız, Yön, Konum, Batarya vb.) canlı görüntüleme
- Harita üzerinden konum takibi
- Görev (Mission) planlama ve yönetimi
- Veri kaydetme (Data Logging)
- Video akışı görüntüleme arayüzü
- Açık/Koyu tema desteği

## Gereksinimler

Projenin çalıştırılabilmesi için sisteminizde **Python 3.8+** yüklü olmalıdır.

## Kurulum ve Çalıştırma

Projenin kurulumu ve çalıştırılması için aşağıdaki adımları sırasıyla uygulayabilirsiniz:

### 1. Projeyi Klonlayın veya İndirin

```bash
git clone <github_repo_url>
cd IDA_Arayuz
```

### 2. Sanal Ortam (Virtual Environment) Oluşturun (Önerilen)

Projeyi izole bir ortamda çalıştırmak için:

```bash
# Windows (PowerShell/CMD):
python -m venv .venv
.venv\Scripts\activate

# macOS/Linux:
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Gerekli Kütüphaneleri Yükleyin

Projenin çalışması için gereken Python kütüphanelerini (PyQt5 ve diğer araçlar) ortamınıza kurun:

```bash
pip install -r requirements.txt
```

### 4. Uygulamayı Başlatın

Tüm gereksinimler yüklendikten sonra arayüzü başlatabilirsiniz:

```bash
python main.py
```

## Arayüz Geliştirme (UI Güncellemesi)

Arayüzün temel yapısı Qt Designer kullanılarak (`gcs_mainwindow.ui` dosyası) tasarlanmıştır. Tasarım üzerinde değişiklik yaptıktan sonra, `.ui` dosyasını Python koduna dönüştürmek için aşağıdaki komutu kullanmanız gerekmektedir:

```bash
pyuic5 -o ui_mainwindow.py gcs_mainwindow.ui
```

Bu işlem `ui_mainwindow.py` dosyasını `gcs_mainwindow.ui` dosyasına göre güncelleyerek arayüzün yeni haline göre çalışmasını sağlar.

## Lisans ve Atıf

MIT