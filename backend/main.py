from fastapi import FastAPI, WebSocket
import cv2
import numpy as np
from ultralytics import YOLO
import supervision as sv
import asyncio
import json
import time

app = FastAPI()

# Define the zone polygon as a normalized array
ZONE_POLYGON = np.array([
    [0, 0],
    [0.5, 0],
    [0.5, 1],
    [0, 1]
])

# Load the YOLO model
model = YOLO("yolov8l.pt")

# Initialize the box annotator
box_annotator = sv.BoxAnnotator(
    thickness=2,
    text_thickness=2,
    text_scale=1
)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    # Initialize video capture
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    # Define the zone polygon in actual pixel values
    zone_polygon = (ZONE_POLYGON * np.array([1280, 720])).astype(int)
    zone = sv.PolygonZone(polygon=zone_polygon, frame_resolution_wh=(1280, 720))
    zone_annotator = sv.PolygonZoneAnnotator(
        zone=zone, 
        color=sv.Color.red(),
        thickness=2,
        text_thickness=4,
        text_scale=2
    )

    detection_start_time = None
    detection_threshold = 0.8  # 80% confidence threshold

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Perform object detection
            results = model(frame, agnostic_nms=True)[0]
            
            # Convert YOLO results to detections
            detections = sv.Detections.from_yolov8(results)
            
            # Generate labels and filter detections for 'person' with confidence >= 80%
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

            # Annotate frame with bounding boxes and zone polygon
            frame = box_annotator.annotate(scene=frame, detections=detections, labels=labels)
            zone.trigger(detections=detections)
            frame = zone_annotator.annotate(scene=frame)

            # Send the bounding box data over the WebSocket
            await websocket.send_text(json.dumps(bbox_data))

            # Control the frame rate
            await asyncio.sleep(0.03)

    except Exception as e:
        print(f"Error: {e}")
    finally:
        cap.release()
        await websocket.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
