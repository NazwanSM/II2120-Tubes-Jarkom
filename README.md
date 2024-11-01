# Chat Room Application

Aplikasi chat room sederhana menggunakan Python dengan komunikasi UDP dan antarmuka grafis menggunakan CustomTkinter.

## Fitur

- Antarmuka grafis modern dengan tema gelap
- Komunikasi real-time menggunakan UDP
- Sistem autentikasi dengan password untuk akses chat room
- Sistem registrasi dan login pengguna
- Penyimpanan riwayat chat
- Tampilan timestamp untuk setiap pesan
- Dukungan untuk multiple client
- Auto-scroll chat
- Notifikasi broadcast untuk user baru

## Persyaratan

- Python 3.x
- Modul yang diperlukan:
  - customtkinter
  - tkinter
  - socket
  - threading
  - queue

## Instalasi

1. Install Python 3.x
2. Install modul yang diperlukan:
```bash
pip install customtkinter
```

## Cara Penggunaan

### Menjalankan Server

1. Jalankan server.py:
```bash
python server.py
```
2. Server akan otomatis menggunakan IP lokal dan port 9999
3. Riwayat chat akan disimpan di `chat_history.txt`

### Menjalankan Client

1. Jalankan client.py:
```bash
python client.py
```
2. Masukkan informasi yang diminta:
   - Server IP address
   - Client IP address
   - Password chat room (default: jarkom100)
   - Username dan password personal

## Fitur Keamanan

- Password chat room untuk akses awal
- Sistem registrasi username unik
- Penyimpanan kredensial pengguna
- Maksimal 3 kali percobaan password

## Struktur File

- `server.py`: Implementasi server UDP
- `client.py`: Aplikasi client dengan GUI
- `chat_history.txt`: File penyimpanan riwayat chat

## Catatan Penting

- Password default chat room: "jarkom100"
- Server harus dijalankan sebelum client
- Pastikan firewall mengizinkan komunikasi UDP pada port 9999
- Aplikasi menggunakan encoding UTF-8 untuk mendukung karakter khusus

## Error Handling

- Penanganan error untuk koneksi gagal
- Notifikasi untuk username yang sudah digunakan
- Penanganan disconnect dan reconnect
- Validasi input pengguna

## Kontribusi

Silakan berkontribusi dengan membuat pull request atau melaporkan issues.

## Lisensi

[MIT License](https://opensource.org/licenses/MIT)

