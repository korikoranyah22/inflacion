import { createReadStream } from 'node:fs'
import { stat } from 'node:fs/promises'
import { createServer } from 'node:http'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const root = path.dirname(fileURLToPath(import.meta.url))
const port = Number(process.env.PORT) || 3000

const mime = new Map([
  ['.html', 'text/html; charset=utf-8'],
  ['.js', 'text/javascript; charset=utf-8'],
  ['.mjs', 'text/javascript; charset=utf-8'],
  ['.css', 'text/css; charset=utf-8'],
  ['.csv', 'text/csv; charset=utf-8'],
  ['.json', 'application/json; charset=utf-8'],
  ['.md', 'text/markdown; charset=utf-8'],
  ['.txt', 'text/plain; charset=utf-8'],
  ['.svg', 'image/svg+xml'],
  ['.png', 'image/png'],
  ['.jpg', 'image/jpeg'],
  ['.jpeg', 'image/jpeg'],
  ['.webp', 'image/webp'],
])

function resolveRequestPath(requestUrl) {
  const pathname = decodeURIComponent(new URL(requestUrl, 'http://localhost').pathname)
  const withoutDashboardPrefix = pathname.replace(/^\/dashboard(?=\/|$)/, '')
  const relative = withoutDashboardPrefix.replace(/^\/+/, '') || 'index.html'
  const resolved = path.resolve(root, relative)
  const relation = path.relative(root, resolved)
  if (relation.startsWith('..') || path.isAbsolute(relation)) return null
  return resolved
}

const server = createServer(async (request, response) => {
  if (request.url === '/health') {
    response.writeHead(200, { 'Content-Type': 'text/plain; charset=utf-8' })
    response.end('ok')
    return
  }

  const candidate = resolveRequestPath(request.url || '/')
  if (!candidate) {
    response.writeHead(403, { 'Content-Type': 'text/plain; charset=utf-8' })
    response.end('Ruta no permitida')
    return
  }

  try {
    const info = await stat(candidate)
    const file = info.isDirectory() ? path.join(candidate, 'index.html') : candidate
    const fileInfo = info.isDirectory() ? await stat(file) : info
    const extension = path.extname(file).toLowerCase()
    response.writeHead(200, {
      'Content-Type': mime.get(extension) || 'application/octet-stream',
      'Content-Length': fileInfo.size,
      'Cache-Control': extension === '.html' ? 'no-cache' : 'public, max-age=300',
      'X-Content-Type-Options': 'nosniff',
    })
    if (request.method === 'HEAD') response.end()
    else createReadStream(file).pipe(response)
  } catch {
    response.writeHead(404, { 'Content-Type': 'text/plain; charset=utf-8' })
    response.end('No encontrado')
  }
})

server.listen(port, '0.0.0.0', () => {
  console.log(`Dashboard escuchando en el puerto ${port}`)
})
