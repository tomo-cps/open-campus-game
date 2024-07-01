<template>
    <v-container fluid>
      <v-row class="text-center">
        <v-col cols="12" class="start-screen-container">
          <img :src="startScreenImage" alt="Start Screen" class="start-screen-image">
          <img :src="startButtonImage" alt="Start Button" @click="startGame" class="start-button animated-button">
        </v-col>
      </v-row>
    </v-container>
  </template>
  
  <script>
  export default {
    name: 'StartScreen',
    data() {
      return {
        startScreenImage: require('@/assets/home.gif'),
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
    bottom: 350px; /* Final position */
    width: 300px; /* Image width */
    cursor: pointer;
    opacity: 0; /* Initially hidden */
  }
  
  .animated-button {
    animation: slide-up 1s ease-out 1s forwards; /* 1s delay added with 'forwards' to keep the final state */
  }
  
  @keyframes slide-up {
    from {
      bottom: 300px; /* Starting position (adjust as needed) */
      opacity: 0;
    }
    to {
      bottom: 330px; /* Final position */
      opacity: 1;
    }
  }
  </style>
  