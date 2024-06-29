import { createRouter, createWebHistory } from 'vue-router';
import StartScreen from '@/components/StartScreen.vue';
import Game from '@/components/Game.vue';

const routes = [
  {
    path: '/',
    name: 'StartScreen',
    component: StartScreen
  },
  {
    path: '/game',
    name: 'Game',
    component: Game
  }
];

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
});

export default router;