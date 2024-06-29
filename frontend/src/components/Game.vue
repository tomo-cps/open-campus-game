<template>
  <v-container fluid>
    <v-row class="text-center">
      <v-col cols="12" class="video-container">
        <audio ref="audio" :src="backgroundMusic" loop></audio>
        <video ref="video" class="video-stream" autoplay @click="toggleMusic"></video>
        <audio ref="gameOverAudio" :src="gameOverSound"></audio>
        <audio ref="gameClearAudio" :src="gameClearSound"></audio>
        <div 
          v-for="(bbox, index) in bboxes" 
          :key="index" 
          :style="getBoundingBoxStyle(bbox)" 
          class="bounding-box"
        >
          {{ bbox.label }}: {{ bbox.confidence.toFixed(2) }}
        </div>
        <div v-if="countdown > 0 && !gameOver && !gameClear" class="countdown">
          <img :src="getCountdownImage()" alt="Countdown">
        </div>
        <div v-if="gameOver && !gameClear" class="game-over">
          <img :src="gameOverImage" alt="Game Over">
        </div>
        <div v-if="gameClear" class="game-clear">
          <img :src="gameClearImage" alt="Game Clear">
        </div>
        <div v-if="showContinue" class="continue" @click="reloadPage">
          <img :src="continueImage" alt="Continue">
        </div>
        <div v-if="showReady" class="ready">
          <img :src="readyImage" alt="Ready">
        </div>
        <div v-if="showGo" class="go">
          <img :src="goImage" alt="Go">
        </div>
        <div class="blocks-container">
          <img v-for="n in numberOfBlocks" :key="n" :src="blockImage" class="block" />
        </div>
        <!-- Add the music icon here -->
        <div class="music-icon" @click="toggleMusic">
          <svg-icon type="mdi" :path="musicIconPath"></svg-icon>
        </div>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import SvgIcon from '@jamescoyle/vue-icon';
import { mdiVolumeHigh, mdiVolumeOff } from '@mdi/js';

export default {
  name: 'HelloWorld',
  components: {
    SvgIcon
  },
  data() {
    return {
      bboxes: [],
      websocket: null,
      videoWidth: 1920,
      videoHeight: 1080,
      gameOver: false,
      gameClear: false,
      gameOverImage: require('@/assets/game_over.gif'),
      gameClearImage: require('@/assets/game_clear_v3.gif'),
      continueImage: require('@/assets/continue.png'),
      readyImage: require('@/assets/ready.png'),
      goImage: require('@/assets/go.png'),
      countdown: 0,
      showContinue: false,
      showReady: true,
      showGo: false,
      countdownImages: [
        require('@/assets/3.png'),
        require('@/assets/2.png'),
        require('@/assets/1.png')
      ],
      backgroundMusic: '',
      gameOverSound: require('@/assets/sounds/game_over.mp3'),
      gameClearSound: require('@/assets/sounds/game_clear.mp3'),
      blockImage: require('@/assets/block.png'),
      numberOfBlocks: 50,
      musicIconPath: mdiVolumeHigh, // Ensure the icon is set to volume high initially
      isMusicPlaying: true // Ensure music is playing initially
    };
  },
  mounted() {
    this.selectRandomMusic();
    this.startVideoStream();
    window.addEventListener('keydown', this.handleKeyDown);
    this.showReadyGoSequence();
  },
  beforeUnmount() {
    window.removeEventListener('keydown', this.handleKeyDown);
  },
  methods: {
    selectRandomMusic() {
      const musicFiles = [
        require('@/assets/sounds/01_mario_bgm.mp3'),
        require('@/assets/sounds/02_mario_bgm.mp3'),
        require('@/assets/sounds/01_mario_bgm.mp3'),
        require('@/assets/sounds/03_mario_bgm.mp3'),
        require('@/assets/sounds/01_mario_bgm.mp3'),
        require('@/assets/sounds/04_mario_bgm.mp3'),
        require('@/assets/sounds/01_mario_bgm.mp3'),
        require('@/assets/sounds/05_mario_bgm.mp3'),
        require('@/assets/sounds/01_mario_bgm.mp3')
      ];
      this.backgroundMusic = musicFiles[Math.floor(Math.random() * musicFiles.length)];
      this.$nextTick(() => {
        const audioElement = this.$refs.audio;
        audioElement.load();
        this.playMusic(); // Ensure music starts playing after loading
      });
    },
    showReadyGoSequence() {
      setTimeout(() => {
        this.showReady = false;
        this.showGo = true;
        setTimeout(() => {
          this.showGo = false;
          this.connectWebSocket();
          this.$refs.video.style.transform = 'none';
        }, 1000);
      }, 2000);
    },
    connectWebSocket() {
      this.websocket = new WebSocket("ws://localhost:8000/ws");
      this.websocket.onopen = () => {
        console.log("WebSocket connection established");
      };
      this.websocket.onmessage = this.handleWebSocketMessage.bind(this);
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
        if (!this.gameClear) {
          this.gameOver = true;
          this.stopMusic();
          this.playGameOverSound();
          this.pauseVideoForDuration(10000);
          this.showContinueWithDelay();
        }
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
    toggleMusic() {
      this.isMusicPlaying ? this.stopMusic() : this.playMusic();
    },
    playMusic() {
      const audioElement = this.$refs.audio;
      if (audioElement) {
        audioElement.volume = 1.0;
        audioElement.play().then(() => {
          this.isMusicPlaying = true;
          this.musicIconPath = mdiVolumeHigh;
        }).catch(error => {
          console.error("Error playing audio:", error);
        });
      }
    },
    stopMusic() {
      const audioElement = this.$refs.audio;
      if (audioElement) {
        audioElement.pause();
        audioElement.currentTime = 0;
        this.isMusicPlaying = false;
        this.musicIconPath = mdiVolumeOff;
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
    playGameClearSound() {
      const gameClearAudioElement = this.$refs.gameClearAudio;
      if (gameClearAudioElement) {
        gameClearAudioElement.volume = 1.0;
        gameClearAudioElement.play().catch(error => {
          console.error("Error playing game clear sound:", error);
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
          videoElement.style.transform = 'none';
        };
      } catch (error) {
        console.error("Error accessing the camera: ", error);
      }
    },
    pauseVideoForDuration(duration) {
      const videoElement = this.$refs.video;
      if (videoElement) {
        videoElement.pause();
        setTimeout(() => {
          videoElement.play();
        }, duration);
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
    },
    handleKeyDown(event) {
      if (event.code === 'Space' || event.code === 'Enter') { // Add check for 'Enter' key
        if (!this.gameOver) {
          this.gameClear = true;
          this.stopMusic();
          this.playGameClearSound();
          this.pauseVideoForDuration(10000);
          this.showContinueWithDelay();
        } else if (this.showContinue) { // If the game is over and "Continue" is shown, reload the page
          this.reloadPage();
        }
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
  width: 100vw;
  height: 100vh;
}

.video-stream {
  width: 100%;
  height: 100%;
  object-fit: cover;
  cursor: pointer;
  transform: none !important; /* Ensure no transformation is applied */
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
  width: 1500px;
  border-radius: 10px;
}

.game-clear {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  z-index: 1000;
}

.game-clear img {
  max-width: 100%;
  max-height: 100%;
  width: 3000px;
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
  width: 35px;
  height: auto;
}

.music-icon {
  position: absolute;
  top: 20px;
  right: 20px;
  z-index: 1000;
  cursor: pointer;
}

.music-icon svg {
  width: 50px;
  height: 50px;
}

.ready, .go {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  z-index: 1000;
}

.ready img, .go img {
  max-width: 100%;
  max-height: 100%;
  /* width: 300px; */
  height: 250px;
}
</style>
