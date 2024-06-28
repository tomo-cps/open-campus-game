<template>
  <v-container fluid>
    <v-row class="text-center">
      <v-col cols="12" class="video-container">
        <video ref="video" class="video-stream" autoplay></video>
        <div 
          v-for="(bbox, index) in bboxes" 
          :key="index" 
          :style="getBoundingBoxStyle(bbox)" 
          class="bounding-box"
        >
          {{ bbox.label }}: {{ bbox.confidence.toFixed(2) }}
        </div>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
export default {
  name: 'HelloWorld',
  data() {
    return {
      bboxes: [],
      websocket: null,
      videoWidth: 1280,  // 初期のビデオの幅
      videoHeight: 720  // 初期のビデオの高さ
    };
  },
  mounted() {
    this.connectWebSocket();
    this.startVideoStream();
  },
  methods: {
    connectWebSocket() {
      this.websocket = new WebSocket("ws://localhost:8000/ws");
      this.websocket.onopen = () => {
        console.log("WebSocket connection established");
      };
      this.websocket.onmessage = this.handleWebSocketMessage;
      this.websocket.onerror = (error) => {
        console.error("WebSocket error:", error);
      };
      this.websocket.onclose = () => {
        console.log("WebSocket connection closed");
      };
    },
    handleWebSocketMessage(event) {
      const data = JSON.parse(event.data);
      console.log("Data received from WebSocket:", data);  // Log received data
      this.bboxes = data;
    },
    getBoundingBoxStyle(bbox) {
      const [x1, y1, x2, y2] = bbox.bbox;
      const videoElement = this.$refs.video;
      const containerWidth = videoElement.clientWidth;
      const containerHeight = videoElement.clientHeight;

      const scaleX = containerWidth;
      const scaleY = containerHeight;

      const style = {
        position: "absolute",
        left: `${x1 * scaleX}px`,
        top: `${y1 * scaleY}px`,
        width: `${(x2 - x1) * scaleX}px`,
        height: `${(y2 - y1) * scaleY}px`,
        color: "red",
        backgroundColor: "rgba(255, 0, 0, 0.3)",
        border: "2px solid red",
        boxShadow: "0 0 10px red",
        animation: "pulse 1s infinite"
      };
      return style;
    },
    async startVideoStream() {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true });
        const videoElement = this.$refs.video;
        videoElement.srcObject = stream;
        videoElement.onloadedmetadata = () => {
          videoElement.play();
          this.videoWidth = videoElement.videoWidth;
          this.videoHeight = videoElement.videoHeight;
        };
      } catch (error) {
        console.error("Error accessing the camera: ", error);
      }
    }
  },
};
</script>

<style>
html, body, #app {
  width: 100%;
  height: 100%;
  margin: 0;
  padding: 0;
  overflow: hidden;
}

.video-container {
  position: relative;
  width: 100vw; /* Full viewport width */
  height: 100vh; /* Full viewport height */
}

.video-stream {
  width: 100%;
  height: 100%;
  object-fit: cover; /* Maintain aspect ratio and cover the area */
}

.bounding-box {
  position: absolute;
  color: red;
  background-color: rgba(255, 0, 0, 0.3);
  border: 2px solid red;
  box-shadow: 0 0 10px red;
  animation: pulse 1s infinite;
  pointer-events: none; /* Allow clicks to pass through */
}

@keyframes pulse {
  0% {
    transform: scale(1);
    box-shadow: 0 0 10px red;
  }
  50% {
    transform: scale(1.1);
    box-shadow: 0 0 20px red;
  }
  100% {
    transform: scale(1);
    box-shadow: 0 0 10px red;
  }
}
</style>
