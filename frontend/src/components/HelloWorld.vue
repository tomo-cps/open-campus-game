<template>
  <v-container fluid>
    <v-row class="text-center">
      <v-col cols="12" class="video-container">
        <video ref="video" class="video-stream" autoplay></video>
        <audio ref="audio" :src="gameMusic" loop></audio>
        <audio ref="gameOverAudio" :src="gameOverSound"></audio> <!-- 追加 -->
        <div 
          v-for="(bbox, index) in bboxes" 
          :key="index" 
          :style="getBoundingBoxStyle(bbox)" 
          class="bounding-box"
        >
          {{ bbox.label }}: {{ bbox.confidence.toFixed(2) }}
        </div>
        <div v-if="countdown > 0 && !gameOver" class="countdown">
          <img :src="getCountdownImage()" alt="Countdown">
        </div>
        <div v-if="gameOver" class="game-over">
          <img :src="gameOverImage" alt="Game Over">
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
      videoHeight: 720,  // 初期のビデオの高さ
      gameOver: false,    // ゲームオーバーフラグ
      gameOverImage: require('@/assets/game_over.gif'), // ゲームオーバー画像のインポート
      countdown: 0,       // カウントダウンの秒数
      countdownImages: [
        require('@/assets/3.png'), // カウントダウン画像のインポート
        require('@/assets/2.png'),
        require('@/assets/1.png')
      ],
      gameMusic: require('@/assets/sounds/mario_1.mp3'), // ゲーム音楽のインポート
      gameOverSound: require('@/assets/sounds/game_over.mp3') // ゲームオーバー音のインポート
    };
  },
  mounted() {
    this.connectWebSocket();
    this.startVideoStream();
    this.playMusic();
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
      if (data.game_over) {
        this.gameOver = true;
        this.stopMusic();
        this.playGameOverSound(); // ゲームオーバー音を再生
      } else if (data.countdown !== undefined) {
        this.countdown = data.countdown;
      } else {
        this.bboxes = data;
      }
    },
    getCountdownImage() {
      return this.countdownImages[3 - this.countdown]; // 修正: カウントダウン画像の順序
    },
    getBoundingBoxStyle(bbox) {
      if (!bbox || !bbox.bbox) {
        return {};
      }
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
    playMusic() {
      const audioElement = this.$refs.audio;
      audioElement.play();
    },
    stopMusic() {
      const audioElement = this.$refs.audio;
      audioElement.pause();
      audioElement.currentTime = 0;
    },
    playGameOverSound() { // ゲームオーバー音を再生するメソッド
      const gameOverAudioElement = this.$refs.gameOverAudio;
      gameOverAudioElement.play();
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

.countdown {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  z-index: 1000;
}

.countdown img {
  width: 300px;
  height: 300px;
}

.game-over {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  z-index: 1000;
}

.game-over img {
  max-width: 100%; /* 最大幅を100%に設定 */
  max-height: 100%; /* 最大高さを100%に設定 */
  width: 300px; /* 固定幅 */
  height: 300px; /* 固定高さ */
  border-radius: 10px;
}
</style>
