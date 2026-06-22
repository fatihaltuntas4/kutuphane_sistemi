# 📚 Modern Kütüphane Yönetim Sistemi

Bu proje, öğrencilerin ve kütüphanecilerin kitap ödünç alma, iade etme, rezerve etme ve raporlama gibi kütüphane işlemlerini dijital ortamda yönetebilmeleri için geliştirilmiş kapsamlı bir **Kütüphane Yönetim Sistemi**dir.

## 🚀 Proje Mimarisi (Teknolojiler)

Sistem modern web standartlarına ve mikroservis (container) mimarisine uygun olarak **3 katmanlı (3-tier)** yapı ile tasarlanmıştır:

1. **Frontend (Kullanıcı Arayüzü):** HTML5, Vanilla CSS (Glassmorphism & Dark Mode) ve JavaScript. Nginx web sunucusu üzerinden yayınlanır.
2. **Backend (API):** Python tabanlı **FastAPI** kullanılarak geliştirilmiştir. Hızlı ve asenkron bir API sunar.
3. **Veritabanı (Database):** **PostgreSQL 15** kullanılmıştır. ORM olarak SQLAlchemy tercih edilmiştir.

Tüm bu sistem **Docker** ve **Docker Compose** kullanılarak konteynerleştirilmiştir.

## ✨ Temel Özellikler

- **Yetkilendirme (Auth):** JWT (JSON Web Tokens) tabanlı güvenli giriş ve kayıt sistemi. Şifreler `bcrypt` ile şifrelenir.
- **Kullanıcı Rolleri:** Öğrenci, Kütüphaneci ve Yönetici olmak üzere 3 farklı rol.
- **Öğrenci İşlemleri:** 
  - Kitap kataloğunda arama yapma.
  - Müsait kitapları ödünç alma.
  - Ödünç alınmış (müsait olmayan) kitapları rezerve etme.
  - Kendi işlem geçmişini (ödünçler ve rezervasyonlar) görüntüleme ve yönetme (İade/İptal).
- **Yönetici/Kütüphaneci İşlemleri:**
  - Yeni kitap ekleme ve silme.
  - Sistemdeki tüm işlemleri anlık takip etme.
  - **Kapsamlı Raporlar:** En çok okunan kitaplar, en aktif kullanıcılar, gecikmiş iadeler, şu an ödünçte olan kitaplar ve aylık istatistikler.

## 📦 Kurulum ve Çalıştırma (Docker)

Projeyi bilgisayarınızda çalıştırmak için sadece **Docker Desktop**'ın yüklü ve çalışır durumda olması yeterlidir. Sistemin kurulumu ve verilerin içeri aktarılması **tamamen otomatikleştirilmiştir**.

### ⚡ Tek Tıkla Kurulum (Windows İçin Önerilen)
Sistemi değerlendirecek hocalarımızın ve kullanıcıların rahatlığı için otomatik bir başlatıcı hazırlanmıştır:
1. Proje klasörü içerisindeki **`baslat.bat`** dosyasına çift tıklayın.
2. Komut satırı (CMD) ekranı açılacak ve sırasıyla; Docker sunucularını indirecek, veritabanını hazırlayacak ve 2000 adet Kaggle kitabını sisteme otomatik olarak aktaracaktır.
3. İşlem tamamlandığında sistem varsayılan tarayıcınızda otomatik olarak açılacaktır (👉 **http://localhost**).

### 🛠️ Manuel Kurulum (Mac/Linux veya Alternatif)
Eğer sistemi manuel komutlarla çalıştırmak isterseniz proje dizininde (Terminal/CMD) aşağıdaki komutları sırasıyla girebilirsiniz:
1. Docker Compose ile sunucuları ayağa kaldırın:
   ```bash
   docker-compose up -d --build
   ```
2. Kaggle verisetini veritabanına aktarın:
   ```bash
   docker exec kutuphane_backend python import_kaggle_data.py
   ```
3. Tarayıcınızdan sisteme giriş yapın: 👉 **http://localhost**

## 📂 Dosya Yapısı
- `/frontend`: Kullanıcı arayüzü dosyaları (HTML, CSS, JS) ve Nginx Dockerfile.
- `/backend`: FastAPI kodları, veritabanı modelleri (SQLAlchemy) ve Python Dockerfile.
- `docker-compose.yml`: Tüm servisleri birbirine bağlayan orkestrasyon dosyası.
- `books_data`: Kaggle üzerinden alınan örnek kütüphane verileri (CSV).
