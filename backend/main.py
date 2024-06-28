from fastapi import FastAPI, WebSocket
import cv2
import numpy as np
from ultralytics import YOLO
import supervision as sv
import asyncio
import json

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

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Perform object detection
            results = model(frame, agnostic_nms=True)[0]
            
            # Convert YOLO results to detections
            detections = sv.Detections.from_yolov8(results)
            
            # Generate labels and filter detections for 'person'
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
            ]
            bbox_data = [item for item in bbox_data if item['label'] == 'person']

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
