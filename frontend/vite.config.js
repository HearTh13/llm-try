import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0', // Memungkinkan akses dari luar kontainer
    port: 5173,      // Port standar Vite
    watch: {
      usePolling: true, // WAJIB untuk mendeteksi perubahan file di Windows/Docker
    },
    hmr: {
      clientPort: 5173, // Menghubungkan client browser ke websocket Docker
    }
  }
})
