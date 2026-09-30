# Gesture Sticker

Overlay stiker ke webcam secara real-time berdasarkan **gestur tangan**.
Deteksi tangan memakai MediaPipe, hasilnya dikirim ke **kamera virtual** (pyvirtualcam)
sehingga bisa dipakai di Zoom, Google Meet, OBS, Discord, atau aplikasi live streaming apa pun.

```
Webcam  ->  MediaPipe (deteksi tangan)  ->  OpenCV (gambar stiker)  ->  Kamera Virtual  ->  Zoom / OBS
```

## Fitur

Dukung **1 tangan** dan **2 tangan** (maks. 2 tangan terdeteksi).

| Gestur | Kondisi | Stiker |
| --- | --- | --- |
| Love (2 tangan) | Ujung telunjuk & jempol dari 2 tangan saling berdekatan | `cantik.jpg` |
| Finger Heart (1 tangan) | Jempol & telunjuk dekat, jari tengah/ring/pinky ditekuk | `cantik.jpg` |
| Thumbs Up / Like | Jempol di atas pergelangan, jari lain ditekuk | `like.jpg` |
| Peace | Telunjuk + tengah teracah, ring & pinky ditekuk | `peace.jpg` |
| Stop / Open Palm | 5 jari terbuka | `stop.jpg` |

Gambar stiker bisa berupa **PNG transparan** (channel alpha) atau **JPG**.
Stiker otomatis disembunyikan kalau posisinya keluar dari frame.

## Kebutuhan

- Windows (kamera virtual pyvirtualcam hanya ergonomic di Windows; Linux perlu install
  `v4l2loopback` dulu, macOS belum didukung pyvirtualcam)
- Python 3.9+
- Webcam
- Untuk Windows: pasang [OBS Virtual Camera](https://obsproject.com/kb/virtual-camera-guide)
  atau driver kamera virtual lain (Zoom/OBS Virtual Camera).

## Instalasi

```bash
git clone <url-repo-kamu>
cd gesture-sticker
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Menjalankan

```bash
python gesture_sticker.py
```

> **Penting:** tutup Zoom / OBS / aplikasi yang sedang memakai kamera virtual
> sebelum menjalankan, karena OBS Virtual Camera hanya bisa dipakai satu proses pada
> satu waktu. Kalau gagal, restart `obs64.exe --startvirtualcam` atau jalankan ulang script.

Kamera virtual akan muncul sebagai perangkat baru di aplikasi conferencing.
Cukup pilih "OBS Virtual Camera" (atau device virtual yang muncul) sebagai input.

## Struktur Project

```
.
├── gesture_sticker.py   # script utama
├── requirements.txt
├── README.md
└── stickers/
    ├── cantik.jpg       # love / finger heart
    ├── like.jpg         # thumbs up
    ├── peace.jpg        # peace sign
    └── stop.jpg         # open palm
```

## Cara Kerja Singkat

1. `pyvirtualcam` membuat perangkat kamera virtual dengan ukuran & FPS yang sama
   dengan webcam asli.
2. Setiap frame dari webcam di-*flip* (mode cermin) dan dikirim ke MediaPipe Hands
   dengan `max_num_hands=2`.
3. openness tiap jari ditentukan dari perbandingan posisi ujung jari dengan
   sendi MCP-nya (`tip.y < mcp.y`).
4. Gestur dicek berurutan dari yang paling spesifik, lalu stiker di-*alpha blend*
   ke frame pada posisi ujung telunjuk.
5. Frame hasil dikirim ke kamera virtual memakai `cam.send()` +
   `cam.sleep_until_next_frame()` supaya tidakewa buffer penuh.

## Menyesuaikan

- Ganti file stiker di `stickers/` dengan nama yang sama, atau ubah baris
  `cv2.imread(...)` di `gesture_sticker.py`.
- Ubah `size=(160, 160)` di `overlay_image()` untuk ukuran stiker.
- Ubah offset penempatan stiker di `sticker_x` / `sticker_y` (default `-80` dan `-180`).
- Ubah ambang sensitivitas gestur: `0.08` (finger heart), `0.15` (love 2 tangan).

## Lisensi

MIT
