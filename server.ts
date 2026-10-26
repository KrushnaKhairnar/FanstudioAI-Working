import dotenv from 'dotenv';
dotenv.config();

import express from 'express';
import path from 'path';
import fs from 'fs';
import http from 'http';
import { spawn } from 'child_process';
import { fileURLToPath } from 'url';
import { createServer as createViteServer } from 'vite';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const PORT = process.env.PORT ? parseInt(process.env.PORT, 10) : 3000;

app.use(express.json({ limit: '50mb' }));
app.use(express.urlencoded({ extended: true, limit: '50mb' }));

// Static asset folders
const dataDir = path.resolve(__dirname, 'data');
const roomsDir = path.resolve(dataDir, 'rooms');
const visDir = path.resolve(dataDir, 'visualizations');
const productsDir = path.resolve(dataDir, 'products');
const uploadsDir = path.resolve(__dirname, 'uploads');

fs.mkdirSync(roomsDir, { recursive: true });
fs.mkdirSync(visDir, { recursive: true });
fs.mkdirSync(productsDir, { recursive: true });
fs.mkdirSync(uploadsDir, { recursive: true });

app.use('/api/static/rooms', express.static(roomsDir));
app.use('/api/static/visualizations', express.static(visDir));
app.use('/api/static/products', express.static(productsDir));
app.use('/uploads', express.static(uploadsDir));
app.use('/uploads', express.static(path.resolve(dataDir, 'uploads')));

// Spawn Python FastAPI backend process on port 8001
const PYTHON_PORT = 8001;
let pythonReady = false;
let pythonProcess: any = null;

function startPythonBackend() {
  console.log('🐍 Starting Python FastAPI Backend on port 8001...');
  try {
    pythonProcess = spawn('python3', ['-m', 'uvicorn', 'backend.app.main:app', '--host', '127.0.0.1', '--port', `${PYTHON_PORT}`], {
      cwd: __dirname,
      env: { ...process.env, PYTHONUNBUFFERED: '1' },
      stdio: ['ignore', 'pipe', 'pipe'],
    });

    pythonProcess.stdout?.on('data', (d: Buffer) => {
      console.log(`[Python] ${d.toString().trim()}`);
    });

    pythonProcess.stderr?.on('data', (d: Buffer) => {
      console.error(`[Python Err] ${d.toString().trim()}`);
    });

    pythonProcess.on('error', (err: any) => {
      console.error('Python FastAPI backend process error:', err);
    });

    pythonProcess.on('exit', (code: number) => {
      console.log(`Python FastAPI backend exited (code ${code}). Auto-restarting in 3s...`);
      pythonReady = false;
      setTimeout(startPythonBackend, 3000);
    });

    const checkHealth = () => {
      const req = http.get(`http://127.0.0.1:${PYTHON_PORT}/api/health`, (res) => {
        if (res.statusCode === 200) {
          pythonReady = true;
          console.log('✅ Python FastAPI backend is LIVE on port 8001 and serving requests!');
        } else {
          setTimeout(checkHealth, 600);
        }
      });
      req.on('error', () => {
        setTimeout(checkHealth, 600);
      });
    };
    setTimeout(checkHealth, 800);
  } catch (err) {
    console.error('Failed to spawn Python process:', err);
  }
}

startPythonBackend();

// Reverse-proxy all /api/* requests to FastAPI backend (or return 503 if not ready)
app.use((req, res, next) => {
  const isApi = req.url.startsWith('/api/') || req.url === '/docs' || req.url === '/openapi.json';
  if (!isApi) {
    return next();
  }

  if (!pythonReady) {
    return res.status(503).json({ error: 'Backend starting' });
  }

  const options: http.RequestOptions = {
    hostname: '127.0.0.1',
    port: PYTHON_PORT,
    path: req.originalUrl || req.url,
    method: req.method,
    headers: {
      ...req.headers,
      host: `127.0.0.1:${PYTHON_PORT}`,
    },
  };

  const proxyReq = http.request(options, (proxyRes) => {
    res.writeHead(proxyRes.statusCode || 200, proxyRes.headers);
    proxyRes.pipe(res);
  });

  proxyReq.on('error', (err) => {
    console.warn(`[Proxy Fallback] Python request ${req.url} error:`, err.message);
    if (!res.headersSent) {
      res.status(502).json({ error: 'Backend proxy error', details: err.message });
    }
  });

  if (req.body && Object.keys(req.body).length > 0 && req.method !== 'GET' && req.method !== 'HEAD') {
    const bodyStr = typeof req.body === 'string' ? req.body : JSON.stringify(req.body);
    proxyReq.setHeader('content-type', req.headers['content-type'] || 'application/json');
    proxyReq.setHeader('content-length', Buffer.byteLength(bodyStr));
    proxyReq.write(bodyStr);
    proxyReq.end();
  } else if (!['GET', 'HEAD'].includes(req.method || '')) {
    req.pipe(proxyReq);
  } else {
    proxyReq.end();
  }
});

// Vite Integration (Dev Mode & Production)
async function startServer() {
  if (process.env.NODE_ENV !== 'production') {
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: 'spa',
    });
    app.use(vite.middlewares);
  } else {
    app.use(express.static(path.resolve(__dirname, 'dist')));
    app.get('*', (req, res) => {
      res.sendFile(path.resolve(__dirname, 'dist', 'index.html'));
    });
  }

  app.listen(PORT, '0.0.0.0', () => {
    console.log(`🚀 FanstudioAI server running on http://0.0.0.0:${PORT}`);
  });
}

startServer();
