import cv2
import mediapipe as mp
import numpy as np
import pygame
import threading
import math

# MediaPipe BlazePoseのセットアップ
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(static_image_mode=False, model_complexity=1, smooth_landmarks=True, enable_segmentation=False, min_detection_confidence=0.5, min_tracking_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils

# カメラのセットアップ
cap = cv2.VideoCapture(0)

# サウンドファイルのパス
sound_file = 'jump_sound.mp3'

# Pygameの初期化
pygame.mixer.init()

def play_sound():
    pygame.mixer.music.load(sound_file)
    pygame.mixer.music.play()

def calculate_angle(a, b, c):
    a = np.array([a.x, a.y])
    b = np.array([b.x, b.y])
    c = np.array([c.x, c.y])
    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180.0 / np.pi)
    if angle > 180.0:
        angle = 360 - angle
    return angle

def is_matching_pose(landmarks):
    # 必要なランドマークのインデックス
    LEFT_HIP = mp_pose.PoseLandmark.LEFT_HIP
    RIGHT_HIP = mp_pose.PoseLandmark.RIGHT_HIP
    LEFT_KNEE = mp_pose.PoseLandmark.LEFT_KNEE
    RIGHT_KNEE = mp_pose.PoseLandmark.RIGHT_KNEE
    LEFT_ANKLE = mp_pose.PoseLandmark.LEFT_ANKLE
    RIGHT_ANKLE = mp_pose.PoseLandmark.RIGHT_ANKLE
    LEFT_ELBOW = mp_pose.PoseLandmark.LEFT_ELBOW
    RIGHT_ELBOW = mp_pose.PoseLandmark.RIGHT_ELBOW
    LEFT_SHOULDER = mp_pose.PoseLandmark.LEFT_SHOULDER
    RIGHT_SHOULDER = mp_pose.PoseLandmark.RIGHT_SHOULDER

    # 角度の計算
    left_leg_angle = calculate_angle(landmarks[LEFT_HIP], landmarks[LEFT_KNEE], landmarks[LEFT_ANKLE])
    right_leg_angle = calculate_angle(landmarks[RIGHT_HIP], landmarks[RIGHT_KNEE], landmarks[RIGHT_ANKLE])
    left_arm_angle = calculate_angle(landmarks[LEFT_SHOULDER], landmarks[LEFT_ELBOW], landmarks[LEFT_HIP])
    right_arm_angle = calculate_angle(landmarks[RIGHT_SHOULDER], landmarks[RIGHT_ELBOW], landmarks[RIGHT_HIP])

    # 反対向きのポーズも考慮して、角度の条件を調整
    if (left_leg_angle > 150 and right_leg_angle < 70 and left_arm_angle < 90 and right_arm_angle > 90) or \
       (right_leg_angle > 150 and left_leg_angle < 70 and right_arm_angle < 90 and left_arm_angle > 90):
        return True

    return False

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # 画像をRGBに変換
    image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(image)

    # 骨格が検出された場合
    if results.pose_landmarks:
        landmarks = results.pose_landmarks.landmark

        # ポーズが一致する場合
        if is_matching_pose(landmarks):
            cv2.putText(frame, 'Pose Detected', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
            threading.Thread(target=play_sound).start()  # ポーズが検出されたら音を鳴らす

        # 骨格を描画
        mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

    # 画像を表示
    cv2.imshow('Pose Detection', frame)
    if cv2.waitKey(10) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
pygame.quit()
