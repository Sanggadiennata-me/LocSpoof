# LocSpoof Web v2.0 - Universal GPS Spoofer

> **Universal Location Spoofer Web Application & Mobile Controller (Flat Design).**  
> Mengontrol dan memanipulasi koordinat geolokasi GPS secara instan melalui Web GUI interaktif berbasis React + Tailwind CSS dengan gaya autentik **Flat Design**, terintegrasi langsung dengan Google Maps & OpenStreetMap, serta sistem lisensi kriptografis serverless (tanpa database).

[![Frontend](https://img.shields.io/badge/Frontend-React%20%2B%20Tailwind%20CSS-blue.svg)](https://react.dev)
[![Design](https://img.shields.io/badge/Style-Flat%20Design-brightgreen.svg)]()
[![Platform](https://img.shields.io/badge/Target-Universal%20(iOS%2C%20Android%2C%20PC%2C%20Mac)-orange.svg)]()
[![Security](https://img.shields.io/badge/License-Serverless%20HMAC--SHA256-success.svg)]()
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 1. Ringkasan Analisis Arsitektur Lama vs Baru

### 📌 Bagaimana Cara Kerja Versi Lama (CLI)?
Pada versi awal, `locspoof` adalah aplikasi terminal (CLI) berbasis Python dengan modul-modul berikut:
1. **Coordinate Parser (`locspoof/core/coordinate_parser.py`)**: Mem-parsing string koordinat desimal (`-6.2088 106.8456`) maupun format DMS (`55°33'15.3"N 55°45'56.2"E`) menggunakan regular expressions dan formula trigonometri.
2. **Android ADB Provider (`locspoof/providers/android/`)**: Berinteraksi dengan Android Debug Bridge:
   - *Android Emulator (QEMU)*: Mengirim perintah console `geo fix <lon> <lat> [alt]` yang langsung ditangkap oleh HAL `gps.goldfish.so`.
   - *HP Fisik Android*: Menggunakan Android 12+ Test Provider API (`cmd location set-test-provider-location`) atau Mock Location App di Developer Options.
3. **Browser CDP Provider (`locspoof/providers/browser/`)**: Meluncurkan Chrome/Chromium dengan port debugging jarak jauh (CDP port 9222) dan meng-override API `navigator.geolocation` melalui `Emulation.setGeolocationOverride`.
4. **Network GeoIP Provider (`locspoof/providers/network/`)**: Memeriksa IP publik dan GeoIP resolver.
5. **Keterbatasan Versi Lama**: Hanya berupa CLI, mengharuskan input koordinat manual satu per satu via terminal, dan membutuhkan kabel data USB yang tercolok ke laptop untuk HP fisik.

---

### 🚀 Apa Saja Pembaruan di Versi 2.0 (Murni Web GUI)?
1. **CLI Telah Dihapus Total**: Digantikan dengan **Web GUI Modern Murni** berbasis **React JS + Tailwind CSS**.
2. **Gaya Visual "Flat Design" Otentik**: Mengadopsi palet warna 2D tegas & ikonik (Flat UI Colors: Turquoise, Peter River, Emerald, Sunflower, Alizarin), tombol datar kontras tinggi dengan feedback hover flat yang jelas, tanpa drop-shadow 3D lebay.
3. **Akses Peta Interaktif & Google Maps**:
   - Peta interaktif dengan dukungan layer **Google Maps Jalan**, **Google Maps Satelit**, **Google Maps Hybrid**, dan **OpenStreetMap**.
   - **Tanpa Perlu Ketik Koordinat**: Cukup klik di mana saja pada peta atau seret pin merah untuk memilih lokasi baru.
   - **Search Bar Cerdas**: Cari tempat langsung berdasarkan nama (contoh: *"Monas"*, *"Pantai Kuta"*, *"Shibuya Tokyo"*, *"Eiffel Tower Paris"*).
   - **Shortcut Preset Populer**: Tombol 1-klik untuk berpindah ke berbagai kota dan landmark dunia.
4. **Universal Multi-Device (Bisa Dipakai di Semua Device Tanpa Colok Kabel ke Laptop)**:
   - **Mode 1: Universal Browser Injection (iOS iPhone, Android, iPad, PC, Mac)**: 
     Menyediakan *1-Click Bookmarklet / Script Injector* yang meng-override `navigator.geolocation` langsung di browser HP tanpa perlu menghubungkan kabel ke laptop atau mengatur developer options!
   - **Mode 2: Wireless ADB (Android Tanpa Kabel)**:
     Dukungan koneksi nirkabel melalui Wi-Fi Debugging Android 11+ (`IP:Port`), sehingga spoofing level sistem dapat dikirim langsung lewat jaringan lokal tanpa kabel USB.
   - **Mode 3: Export Mock Route (GPX File)**: Download file GPX sekali klik untuk di-load ke GPS simulator mobile.
5. **Sistem Lisensi Serverless Kriptografis (Tanpa Database)**:
   - Menggunakan tanda tangan digital **HMAC-SHA256**.
   - Tidak memerlukan database (MySQL/PostgreSQL/MongoDB) atau server backend untuk verifikasi.
   - Anti-tamper & anti-pemalsuan: perubahan sekecil apa pun pada data token akan membatalkan tanda tangan.
   - **Key Generator Bawaan untuk Pemilik**: Pemilik dapat membuat lisensi baru untuk teman/klien dengan menentukan nama, masa aktif (7 hari, 30 hari, 1 tahun, selamanya), dan hak akses.

---

## 2. Master Key Pemilik (Owner Key)

Khusus untuk Anda sebagai pembuat aplikasi (`r3x`), berikut adalah Master License Key berkriptografi tinggi tanpa batas kedaluwarsa (**LIFETIME OWNER**):

```text
LOCSPOOF-OWNER-eyJzdWIiOiJyM3gtZm91bmRlci1tYXN0ZXIiLCJyb2xlIjoiT1dORVIiLCJpYXQiOjE3OTMyNjUyODAsImV4cCI6MCwiZmVhdCI6WyIqIl19-bb998ab22ac851fcaffff8deacff9918
```

> **Catatan Pemilik:**  
> Key di atas membuka seluruh fitur administratif, termasuk tombol **"Key Gen"** di navigasi atas untuk menghasilkan license key baru bagi pengguna lain.

---

## 3. Cara Menjalankan & Membuka GUI

### Opsi A: Menggunakan Node / Vite (Development Mode)
```bash
cd web
npm install
npm run dev
```
Buka browser di `http://localhost:3000` (atau URL yang ditampilkan terminal).

### Opsi B: Menggunakan Python Web Launcher (Desktop Ready)
```bash
# Build frontend sekali
cd web && npm run build && cd ..

# Jalankan server GUI
python3 -m locspoof
# atau
python3 locspoof/gui/server.py
```
Aplikasi akan otomatis menyala di `http://localhost:3000` dan membuka web browser Anda.

### Opsi C: Deploy Serverless (Vercel / Netlify / GitHub Pages)
Folder `web/dist` adalah aplikasi web statis murni tanpa ketergantungan server database. Anda dapat mendeploy folder `web/` ke Vercel atau Netlify hanya dengan menghubungkan repository GitHub!

---

## 4. Cara Penggunaan di Perangkat HP (Semua Device)

### Cara 1: Mengubah Lokasi Browser di HP Tanpa Colok Kabel (iPhone & Android)
1. Buka Web LocSpoof di HP Anda (atau buka di laptop lalu pilih lokasi yang Anda inginkan di peta).
2. Di panel **"Mode Integrasi Device"**, pilih tab **"Universal Browser"** lalu klik **"Salin Script"**.
3. Buka tab baru di browser HP (contoh: buka Google Maps Web atau web target).
4. Tempelkan script yang sudah disalin ke bilah alamat (address bar) browser, pastikan diawali dengan `javascript:`, lalu tekan Enter.
5. Lokasi browser HP Anda seketika berpindah ke koordinat yang dipilih!

### Cara 2: Mengubah Lokasi Level Sistem di Android Secara Nirkabel (Wireless ADB)
1. Di HP Android Anda: Masuk ke **Pengaturan &rarr; Opsi Pengembang &rarr; Wireless Debugging** lalu aktifkan.
2. Pastikan HP dan laptop berada dalam satu jaringan Wi-Fi yang sama.
3. Catat alamat IP dan Port yang muncul di layar HP (contoh: `192.168.1.15:5555`).
4. Masukkan ke tab **"Wireless ADB"** di web GUI LocSpoof, lalu klik **Hubungkan Wi-Fi**.
5. Klik **"TELEPORT SEKARANG"** di peta, dan seluruh aplikasi di HP Anda (Gojek, Grab, Google Maps App, WhatsApp) akan langsung mengikuti koordinat tersebut!

---

## 5. Lisensi & Hak Cipta
Dilisensikan di bawah **MIT License**. Dibuat untuk pengujian keamanan dan simulasi lokasi.
