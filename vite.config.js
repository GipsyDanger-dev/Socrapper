import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
    plugins: [react()],
    resolve: {
        alias: {
            '@': path.resolve(__dirname, './resources/js'),
        },
    },
    build: {
        outDir: 'public/build',
        emptyOutDir: true,
        manifest: true,
    },
    server: {
        proxy: {
            '/api': {
                target: 'http://localhost:8000',
                changeOrigin: true,
            },
            '/exports': {
                target: 'http://localhost:8000',
                changeOrigin: true,
            },
        },
    },
});
