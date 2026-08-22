import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

const here = path.dirname(fileURLToPath(import.meta.url))
const dashboardRoot = path.resolve(here, '..')

const MIME = {
  '.html': 'text/html; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.mjs': 'text/javascript; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.csv': 'text/csv; charset=utf-8',
  '.md': 'text/markdown; charset=utf-8',
  '.txt': 'text/plain; charset=utf-8',
  '.svg': 'image/svg+xml',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.webp': 'image/webp',
  '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
}

function safeDashboardPath(requestUrl) {
  const pathname = decodeURIComponent(new URL(requestUrl, 'http://localhost').pathname)
  const relativePath = pathname.replace(/^\/+/, '') || 'index.html'
  const resolved = path.resolve(dashboardRoot, relativePath)
  const relative = path.relative(dashboardRoot, resolved)
  if (relative.startsWith('..') || path.isAbsolute(relative)) return null
  return resolved
}

function dashboardMiddleware() {
  const serveDashboard = (server) => {
    server.middlewares.use('/dashboard', (request, response, next) => {
      const target = safeDashboardPath(request.url || '/')
      if (!target) {
        response.statusCode = 403
        response.end('Ruta no permitida')
        return
      }

      fs.stat(target, (statError, stat) => {
        const file = !statError && stat.isDirectory() ? path.join(target, 'index.html') : target
        fs.readFile(file, (readError, content) => {
          if (readError) {
            next()
            return
          }
          response.statusCode = 200
          response.setHeader('Content-Type', MIME[path.extname(file).toLowerCase()] || 'application/octet-stream')
          response.setHeader('Content-Length', content.length)
          response.setHeader('Cache-Control', 'no-store')
          if (request.method === 'HEAD') response.end()
          else response.end(content)
        })
      })
    })
  }

  return {
    name: 'serve-real-dashboard',
    configureServer: serveDashboard,
    configurePreviewServer: serveDashboard,
  }
}

export default defineConfig({
  plugins: [react(), dashboardMiddleware()],
  server: {
    host: '127.0.0.1',
    port: 5173,
  },
  preview: {
    host: '127.0.0.1',
    port: 4173,
  },
})
