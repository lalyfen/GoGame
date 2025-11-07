import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    host: true
  },
  build: {
    rollupOptions: {
      input: {
        auth: 'auth.html',
        boardgame: 'boardgame.html'
      }
    }
  }
})
