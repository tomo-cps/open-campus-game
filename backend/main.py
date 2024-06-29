import cv2
import numpy as np
from fastapi import FastAPI, WebSocket
from ultralytics import YOLO
import supervision as sv
import asyncio
import json
import time

app = FastAPI()

# ZONE_POLYGONを正規化された配列として定義
ZONE_POLYGON = np.array([
    [0, 0],
    [0.5, 0],
    [0.5, 1],
    [0, 1]
])

# YOLOモデルを読み込む
model = YOLO("yolov8l.pt")

# ボックスアノテーターを初期化
box_annotator = sv.BoxAnnotator(
    thickness=2,
    text_thickness=2,
    text_scale=1
)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    # ビデオキャプチャを初期化
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

    # 実際のピクセル値でゾーンポリゴンを定義
    zone_polygon = (ZONE_POLYGON * np.array([1920, 1080])).astype(int)
    zone = sv.PolygonZone(polygon=zone_polygon, frame_resolution_wh=(1920, 1080))
    zone_annotator = sv.PolygonZoneAnnotator(
        zone=zone, 
        color=sv.Color.red(),
        thickness=2,
        text_thickness=4,
        text_scale=2
    )

    detection_start_time = None
    detection_threshold = 0.8  # 80%の信頼度閾値

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # FOVを広げるためのソフトウェア調整を適用
            h, w = frame.shape[:2]
            new_w = int(w * 1.5)  # この係数を調整してFOVを広げる
            new_h = int(h * 1.5)
            frame = cv2.resize(frame, (new_w, new_h))
            frame = frame[int(new_h/2-h/2):int(new_h/2+h/2), int(new_w/2-w/2):int(new_w/2+w/2)]
            frame = np.ascontiguousarray(frame)  # フレームを連続配列に変換

            # オブジェクト検出を実行
            results = model(frame, agnostic_nms=True)[0]
            
            # YOLOの結果を検出結果に変換
            detections = sv.Detections.from_yolov8(results)
            
            # ラベルを生成し、信頼度が80%以上の「person」をフィルタリング
            labels = [
                f"{model.model.names[class_id]} {confidence:0.2f}"
                for _, confidence, class_id, _ in detections
            ]
            bbox_data = [
                {
                    "label": model.model.names[class_id],
                    "confidence": float(confidence),
                    "bbox": [
                        bbox[0] / frame.shape[1], 
                        bbox[1] / frame.shape[0], 
                        bbox[2] / frame.shape[1], 
                        bbox[3] / frame.shape[0]
                    ]
                }
                for bbox, confidence, class_id, _ in detections
                if model.model.names[class_id] == 'person' and confidence >= detection_threshold
            ]

            person_detected = len(bbox_data) > 0

            if person_detected:
                if detection_start_time is None:
                    detection_start_time = time.time()
                elapsed_time = time.time() - detection_start_time
                if elapsed_time >= 3:
                    await websocket.send_text(json.dumps({"countdown": 0, "game_over": True}))
                    print("Game Over")
                    break
                elif elapsed_time >= 2:
                    await websocket.send_text(json.dumps({"countdown": 1}))
                    print("Countdown: 1")
                elif elapsed_time >= 1:
                    await websocket.send_text(json.dumps({"countdown": 2}))
                    print("Countdown: 2")
                else:
                    await websocket.send_text(json.dumps({"countdown": 3}))
                    print("Countdown: 3")
            else:
                detection_start_time = None
                await websocket.send_text(json.dumps({"countdown": 0}))
                print("Countdown reset")

            # フレームにバウンディングボックスとゾーンポリゴンを注釈
            frame = np.ascontiguousarray(frame)  # フレームを連続配列に変換
            print(f"Frame is contiguous: {frame.flags['C_CONTIGUOUS']}")  # デバッグステートメント
            frame = box_annotator.annotate(scene=frame, detections=detections, labels=labels)
            zone.trigger(detections=detections)
            frame = zone_annotator.annotate(scene=frame)

            # バウンディングボックスデータをWebSocket経由で送信
            await websocket.send_text(json.dumps(bbox_data))

            # フレームレートを制御
            await asyncio.sleep(0.03)

    except Exception as e:
        print(f"Error: {e}")
    finally:
        cap.release()
        await websocket.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
