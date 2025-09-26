# Game Translator - Panduan Pengguna

Terima kasih telah menggunakan Game Translator! Aplikasi ini dirancang untuk menerjemahkan teks game secara real-time langsung di layar Anda.

## Fitur Utama

-   **Terjemahan Real-time**: Tangkap area mana pun di layar Anda untuk mendapatkan terjemahan instan dari Bahasa Inggris ke Bahasa Indonesia.
-   **Dua Jendela**: Sebuah overlay transparan untuk memilih area dan sebuah jendela terpisah untuk menampilkan hasil terjemahan.
-   **Dapat Dikonfigurasi**: Atur area tangkapan, ukuran font, dan lainnya sesuai kebutuhan Anda.

## Cara Menggunakan

1.  **Jalankan Aplikasi**: Luncurkan file `GameTranslator.exe`. Dua jendela akan muncul: overlay (awalnya mungkin tidak terlihat) dan jendela terjemahan.
2.  **Pilih Area Tangkapan**:
    -   Tekan `Ctrl+Shift+3`. Layar akan menjadi sedikit gelap.
    -   Klik dan seret mouse Anda di atas teks game yang ingin Anda terjemahkan untuk membuat kotak.
    -   Lepaskan tombol mouse. Kotak merah sekarang akan menandai area tangkapan Anda.
3.  **Mulai/Jeda Terjemahan**:
    -   Tekan `Ctrl+Shift+2` untuk memulai atau menjeda proses penerjemahan.
    -   Saat aktif, teks apa pun yang muncul di dalam kotak merah akan secara otomatis diterjemahkan di jendela terjemahan.

## Daftar Hotkey

| Hotkey                | Aksi                                      |
| --------------------- | ----------------------------------------- |
| `Ctrl+Shift+1`        | Menampilkan/Menyembunyikan overlay merah. |
| `Ctrl+Shift+2`        | Memulai/Menjeda terjemahan.               |
| `Ctrl+Shift+3`        | Masuk ke mode pemilihan area.             |
| `Ctrl+Shift+C`        | Menyalin teks terakhir dari jendela terjemahan. |
| `Ctrl+Shift+Up Arrow` | Memperbesar ukuran font di jendela terjemahan. |
| `Ctrl+Shift+Down Arrow`| Memperkecil ukuran font di jendela terjemahan. |

## Tips Mengatasi Masalah (Anti-Lag)

-   **Perkecil Area Tangkapan**: Semakin kecil area yang ditangkap, semakin cepat prosesnya. Coba fokus hanya pada kotak dialog atau area teks yang relevan.
-   **Gunakan Mode "Speed"**: Di file `config.json` (terletak di `%APPDATA%\\GameTranslator`), Anda dapat mengatur `"ocr_quality": "speed"` untuk latensi yang lebih rendah dengan mengorbankan sedikit akurasi OCR.
-   **Gunakan Backend Lokal**: Backend `"local"` (default) jauh lebih cepat daripada backend `"api"`. Pastikan ini diatur di `config.json`.

## Catatan

Aplikasi ini berjalan sepenuhnya secara lokal (kecuali jika Anda mengonfigurasi backend API) dan tidak mengumpulkan data pribadi apa pun. Untuk detail lebih lanjut, silakan lihat file `PRIVACY.md`.

Selamat bermain!