import { createRouter, createWebHistory } from 'vue-router';
import type { RouteRecordRaw } from 'vue-router';
import LandingPage from '@/views/LandingPage.vue';
import LoginPage from '@/views/LoginPage.vue';
import SingupPage from './views/SingupPage.vue';
import DashboardPage from './views/DashboardPage.vue';

const routes: Array<RouteRecordRaw> = [
  // Add your routes here, for example:
  // { path: '/', component: () => import('./views/Home.vue') }
  {
    path: '/',
    name: 'Home',
    component: LandingPage
  },
  {
    path: '/login',
    name: 'Login',
    component: LoginPage
  },
  {
    path: '/singup',
    name: 'Singup',
    component: SingupPage
  }
  ,
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: DashboardPage
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
