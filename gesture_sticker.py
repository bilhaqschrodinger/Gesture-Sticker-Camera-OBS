import cv2
import mediapipe as mp
import pyvirtualcam
import numpy as np
import os
import math

# --- FUNGSI OVERLAY GAMBAR (JPG / PNG) ---
def overlay_image(background, overlay, x, y, size=(160, 160)):
    if overlay is None:
        return background
    
    overlay = cv2.resize(overlay, size)
    h, w, c = overlay.shape

    # Batasi agar gambar tidak keluar dari frame layar
    if y + h > background.shape[0] or x + w > background.shape[1] or x < 0 or y < 0:
        return background

    if c == 4: # PNG Transparan
        b, g, r, a = cv2.split(overlay)
        overlay_rgb = cv2.merge((b, g, r))
        mask = a / 255.0
        for ch in range(3):
            background[y:y+h, x:x+w, ch] = (
                mask * overlay_rgb[:, :, ch] + (1 - mask) * background[y:y+h, x:x+w, ch]
            )
    else: # JPG / Tanpa transparansi
        background[y:y+h, x:x+w] = overlay

    return background


# --- LOAD SEMUA STIKER ---
img_like   = cv2.imread('stickers/like.jpg')
img_peace  = cv2.imread('stickers/peace.jpg')
img_stop   = cv2.imread('stickers/stop.jpg')
img_cantik = cv2.imread('stickers/cantik.jpg')  # Stiker Love / Cantik


# --- INISIALISASI MEDIAPIPE (Mendukung hingga 2 tangan) ---
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    max_num_hands=2, 
    min_detection_confidence=0.7, 
    min_tracking_confidence=0.7
)

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
cap.set(cv2.CAP_PROP_FPS, 30)

if not cap.isOpened():
    print("❌ ERROR: Webcam tidak bisa dibuka! Pastikan Zoom/OBS sudah ditutup lalu jalankan ulang.")
    exit()

width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = 30

with pyvirtualcam.Camera(width=width, height=height, fps=fps, fmt=pyvirtualcam.PixelFormat.BGR) as cam:
    print(f"✅ Kamera Virtual Aktif: {cam.device}")

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb_frame)

        if results.multi_hand_landmarks:
            num_hands = len(results.multi_hand_landmarks)

            # -----------------------------------------------------------------
            # OPS 1: GESTUR LOVE 2 TANGAN (Membentuk Heart dengan 2 Tangan)
            # -----------------------------------------------------------------
            if num_hands == 2:
                hand1 = results.multi_hand_landmarks[0].landmark
                hand2 = results.multi_hand_landmarks[1].landmark

                # Ambil posisi ujung telunjuk dan jempol kedua tangan
                h1_index = hand1[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                h2_index = hand2[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                h1_thumb = hand1[mp_hands.HandLandmark.THUMB_TIP]
                h2_thumb = hand2[mp_hands.HandLandmark.THUMB_TIP]

                # Hitung jarak antara ujung jari tangan kiri & kanan
                dist_index = math.hypot(h1_index.x - h2_index.x, h1_index.y - h2_index.y)
                dist_thumb = math.hypot(h1_thumb.x - h2_thumb.x, h1_thumb.y - h2_thumb.y)

                # Jika telunjuk dan jempol kedua tangan saling berdekatan (membentuk love)
                if dist_index < 0.15 and dist_thumb < 0.15:
                    center_x = int(((h1_index.x + h2_index.x) / 2) * width) - 80
                    center_y = int(((h1_index.y + h2_index.y) / 2) * height) - 180
                    frame = overlay_image(frame, img_cantik, center_x, center_y)

            # -----------------------------------------------------------------
            # OPS 2: GESTUR 1 TANGAN (Finger Heart, Like, Peace, Stop)
            # -----------------------------------------------------------------
            for hand_landmarks in results.multi_hand_landmarks:
                lm = hand_landmarks.landmark

                thumb_tip  = lm[mp_hands.HandLandmark.THUMB_TIP]
                index_tip  = lm[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                middle_tip = lm[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
                ring_tip   = lm[mp_hands.HandLandmark.RING_FINGER_TIP]
                pinky_tip  = lm[mp_hands.HandLandmark.PINKY_TIP]

                index_mcp  = lm[mp_hands.HandLandmark.INDEX_FINGER_MCP]
                middle_mcp = lm[mp_hands.HandLandmark.MIDDLE_FINGER_MCP]
                ring_mcp   = lm[mp_hands.HandLandmark.RING_FINGER_MCP]
                pinky_mcp  = lm[mp_hands.HandLandmark.PINKY_MCP]
                wrist      = lm[mp_hands.HandLandmark.WRIST]

                sticker_x = int(index_tip.x * width) - 80
                sticker_y = int(index_tip.y * height) - 180

                index_open  = index_tip.y < index_mcp.y
                middle_open = middle_tip.y < middle_mcp.y
                ring_open   = ring_tip.y < ring_mcp.y
                pinky_open  = pinky_tip.y < pinky_mcp.y

                # Hitung jarak antara ujung Jempol dan Telunjuk (Finger Heart 1 Tangan)
                dist_thumb_index = math.hypot(thumb_tip.x - index_tip.x, thumb_tip.y - index_tip.y)

                # A. Finger Heart (1 tangan: Jempol & Telunjuk dekat, jari lain ditekuk)
                if dist_thumb_index < 0.08 and not middle_open and not ring_open and not pinky_open:
                    frame = overlay_image(frame, img_cantik, sticker_x, sticker_y)

                # B. Thumbs Up (Like)
                elif thumb_tip.y < wrist.y and not index_open and not middle_open and not ring_open and not pinky_open:
                    frame = overlay_image(frame, img_like, sticker_x, sticker_y)

                # C. Peace Sign (2 Jari)
                elif index_open and middle_open and not ring_open and not pinky_open:
                    frame = overlay_image(frame, img_peace, sticker_x, sticker_y)

                # D. Stop / Open Palm (5 Jari)
                elif index_open and middle_open and ring_open and pinky_open:
                    frame = overlay_image(frame, img_stop, sticker_x, sticker_y)

        cam.send(frame)
        cam.sleep_until_next_frame()

cap.release()