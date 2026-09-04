import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// نکته: پورت (5174) عمداً متفاوت از User App (5173) است تا هر دو بتوانند
// هم‌زمان و بدون تداخل در توسعه‌ی محلی اجرا شوند.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5174,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
