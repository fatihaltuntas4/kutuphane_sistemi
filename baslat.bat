@echo off
echo ===================================================
echo Kutuphane Yonetim Sistemi Otomatik Baslatici
echo ===================================================
echo.
echo [1/3] Docker uzerinden sunucular ve veritabani ayaga kaldiriliyor...
docker-compose up -d --build

echo.
echo [2/3] Veritabaninin hazir olmasi icin kisa bir sure bekleniyor...
timeout /t 10 /nobreak > NUL

echo.
echo [3/3] Kaggle kitaplari ve kullanici verileri sisteme aktariliyor...
docker exec kutuphane_backend python import_kaggle_data.py

echo.
echo ===================================================
echo SISTEM BASARIYLA KURULDU VE YAYINDA!
echo ===================================================
echo Tarayiciniz otomatik olarak aciliyor...
start http://localhost:8080
pause
