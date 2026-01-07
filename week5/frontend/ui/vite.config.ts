import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  build: {
    outDir: path.resolve(__dirname, '../dist'),
    emptyOutDir: true,
  },
  server: {
    port: 3000,
    proxy: {
      '/notes': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
      '/action-items': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },
})
