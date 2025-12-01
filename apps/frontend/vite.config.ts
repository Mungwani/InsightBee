import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react-swc'
import tailwindcss from '@tailwindcss/vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  
  preview: {
    host: true,      
    port: 8080,      
    allowedHosts: [
      'insightbee-frontend-950949202751.europe-west1.run.app',
      // 나중에 커스텀 도메인 쓰면 여기 추가
    ],
  },

  server: {
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        secure: false,
      },
    },
  },
})
