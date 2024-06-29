<template>
    <v-container fluid>
      <v-row class="text-center">
        <v-col cols="12" class="start-screen-container">
          <img :src="startScreenImage" alt="Start Screen" class="start-screen-image">
          <img :src="startButtonImage" alt="Start Button" @click="startGame" class="start-button">
        </v-col>
      </v-row>
    </v-container>
  </template>
  
  <script>
  export default {
    name: 'StartScreen',
    data() {
      return {
        startScreenImage: require('@/assets/home.png'),
        startButtonImage: require('@/assets/start_button.png')
      };
    },
    methods: {
      startGame() {
        this.$router.push('/game');
      }
    }
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
  
  .start-screen-container {
    position: relative;
    width: 100vw;
    height: 100vh;
    display: flex;
    justify-content: center;
    align-items: center;
    flex-direction: column;
    background-color: #000;
  }
  
  .start-screen-image {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }
  
  .start-button {
    position: absolute;
    bottom: 350px; /* 位置を調整 */
    width: 300px; /* 画像の幅を調整 */
    cursor: pointer;
  }
  </style>
  