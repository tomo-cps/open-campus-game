<template>
  <v-container fluid>
    <v-row class="text-center">
      <v-col cols="12" class="video-container">
        <audio ref="audio" :src="backgroundMusic" loop></audio>
        <video ref="video" class="video-stream" autoplay @click="playMusic"></video>
        <audio ref="gameOverAudio" :src="gameOverSound"></audio>
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
        <div v-if="showContinue" class="continue" @click="reloadPage">
          <img :src="continueImage" alt="Continue">
        </div>
        <div class="blocks-container">
          <img v-for="n in numberOfBlocks" :key="n" :src="blockImage" class="block" />
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
      videoWidth: 1280,
      videoHeight: 720,
      gameOver: false,
      gameOverImage: require('@/assets/game_over.gif'),
      continueImage: require('@/assets/continue.png'),
      countdown: 0,
      showContinue: false,
      countdownImages: [
        require('@/assets/3.png'),
        require('@/assets/2.png'),
        require('@/assets/1.png')
      ],
      backgroundMusic: require('@/assets/sounds/mario_1.mp3'),
      gameOverSound: require('@/assets/sounds/game_over.mp3'),
      blockImage: require('@/assets/block.png'),
      numberOfBlocks: 50 // Adjust the number of blocks you want to display
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
      if (data.game_over) {
        this.gameOver = true;
        this.stopMusic();
        this.playGameOverSound();
        this.showContinueWithDelay();
      } else if (data.countdown !== undefined) {
        this.countdown = data.countdown;
      } else {
        this.bboxes = data;
      }
    },
    getCountdownImage() {
      return this.countdownImages[3 - this.countdown];
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
      if (audioElement) {
        audioElement.volume = 1.0;
        audioElement.play().catch(error => {
          console.error("Error playing audio:", error);
        });
      }
    },
    stopMusic() {
      const audioElement = this.$refs.audio;
      if (audioElement) {
        audioElement.pause();
        audioElement.currentTime = 0;
      }
    },
    playGameOverSound() {
      const gameOverAudioElement = this.$refs.gameOverAudio;
      if (gameOverAudioElement) {
        gameOverAudioElement.volume = 1.0;
        gameOverAudioElement.play().catch(error => {
          console.error("Error playing game over sound:", error);
        });
      }
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
    },
    async showContinueWithDelay() {
      await this.sleep(3000);
      this.showContinue = true;
    },
    sleep(ms) {
      return new Promise(resolve => setTimeout(resolve, ms));
    },
    reloadPage() {
      window.location.reload();
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
  width: 100vw;
  height: 100vh;
}

.video-stream {
  width: 100%;
  height: 100%;
  object-fit: cover;
  cursor: pointer;
}

.bounding-box {
  position: absolute;
  color: red;
  background-color: rgba(255, 0, 0, 0.3);
  border: 2px solid red;
  box-shadow: 0 0 10px red;
  animation: pulse 1s infinite;
  pointer-events: none;
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
  max-width: 100%;
  max-height: 100%;
  width: 800px;
  height: 800px;
  border-radius: 10px;
}

.continue {
  position: absolute;
  bottom: 30px;
  right: 10px;
  z-index: 1000;
  cursor: pointer;
}

.continue img {
  max-width: 100%;
  height: auto;  
  width: 300px; 
}

.blocks-container {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: transparent;
}

.block {
  width: 35px; /* Adjust the size of the blocks */
  height: auto;
}
</style>
