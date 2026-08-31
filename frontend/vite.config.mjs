import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    proxy: {
      // Proxy API calls to the Flask backend
      '/api': {
        target: 'http://127.0.0.1:5001',
        // Do not change the Origin header — let the backend see the browser's
        // origin (e.g. http://localhost:5173). Changing it to the target
        // (127.0.0.1) caused inconsistent CORS behavior and cookies.
        changeOrigin: false,
        secure: false
      },
      // Proxy page routes used in iframes
      '/dashboard': {
        target: 'http://127.0.0.1:5001',
        changeOrigin: false,
        secure: false
      },
      '/users': {
        target: 'http://127.0.0.1:5001',
        changeOrigin: false,
        secure: false
      },
      '/roles': {
        target: 'http://127.0.0.1:5001',
        changeOrigin: false,
        secure: false
      },
      '/profile': {
        target: 'http://127.0.0.1:5001',
        changeOrigin: false,
        secure: false
      }
    }
  }
})
