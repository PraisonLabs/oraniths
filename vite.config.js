
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  root: './src/frontend',
  build: { outDir: '../../dist', emptyOutDir: true },
  server: { proxy: { '/api': { target: 'http://localhost:3001', changeOrigin: true } } }
});