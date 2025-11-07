import { createRouter, createWebHistory } from 'vue-router';

const routes = [
  { path: '/messages', name: 'messages', component: () => import('../views/MessageView.vue') },
  { path: '/history', name: 'history', component: () => import('../views/HistoryView.vue') },
  { path: '/invite', name: 'invite', component: () => import('../views/InviteView.vue') },
  { path: '/logout', name: 'logout', component: () => import('../views/LogoutView.vue') }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;
