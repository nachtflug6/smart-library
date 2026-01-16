#!/usr/bin/env node
/**
 * Simple server for Smart Library UI with API proxy
 * Serves static files from dist/ and proxies API requests to the backend
 */

import express from 'express';
import { createProxyMiddleware } from 'express-http-proxy';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const app = express();
const PORT = process.env.PORT || 5173;

// Get API URL from environment, defaults to smartlib_api:8000 on Docker network
const API_URL = process.env.VITE_API_URL || 'http://smartlib_api:8000';

console.log(`Starting UI server on port ${PORT}`);
console.log(`API backend: ${API_URL}`);

// Proxy API requests to the backend
app.use('/api', createProxyMiddleware({
  target: API_URL,
  changeOrigin: true,
  pathRewrite: {
    '^/api': '/api', // Keep the /api prefix
  },
  onError: (err, req, res) => {
    console.error('Proxy error:', err);
    res.status(503).json({ error: 'Backend service unavailable' });
  },
}));

// Serve static files
const distDir = path.join(__dirname, 'dist');
app.use(express.static(distDir));

// SPA fallback - serve index.html for all routes not matching files
app.get('*', (req, res) => {
  res.sendFile(path.join(distDir, 'index.html'));
});

app.listen(PORT, '0.0.0.0', () => {
  console.log(`✓ UI server running on http://0.0.0.0:${PORT}`);
});
