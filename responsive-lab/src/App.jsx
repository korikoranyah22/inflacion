import { useCallback, useEffect, useMemo, useRef, useState } from 'react'

const DEVICES = [
  { id: 'phone-360', label: 'Móvil S', width: 360, height: 800, icon: '📱' },
  { id: 'phone-390', label: 'Móvil M', width: 390, height: 844, icon: '📱' },
  { id: 'phone-430', label: 'Móvil L', width: 430, height: 932, icon: '📱' },
  { id: 'tablet-768', label: 'Tablet', width: 768, height: 1024, icon: '▯' },
  { id: 'desktop-1440', label: 'Escritorio', width: 1440, height: 900, icon: '🖥️' },
]

const DEFAULT_DEVICE = DEVICES[1]

function clamp(value, min, max) {
  return Math.min(max, Math.max(min, Number(value) || min))
}

function initialViewport() {
  const params = new URLSearchParams(window.location.search)
  return {
    width: clamp(params.get('width') || DEFAULT_DEVICE.width, 320, 1920),
    height: clamp(params.get('height') || DEFAULT_DEVICE.height, 480, 1400),
  }
}

function describeElement(element) {
  if (!element) return 'elemento desconocido'
  const id = element.id ? `#${element.id}` : ''
  const classes = [...element.classList].slice(0, 2).map((name) => `.${name}`).join('')
  return `${element.tagName.toLowerCase()}${id}${classes}`
}

export default function App() {
  const initial = useMemo(initialViewport, [])
  const [width, setWidth] = useState(initial.width)
  const [height, setHeight] = useState(initial.height)
  const [zoom, setZoom] = useState(100)
  const [frameKey, setFrameKey] = useState(0)
  const [loaded, setLoaded] = useState(false)
  const [copied, setCopied] = useState(false)
  const [metrics, setMetrics] = useState({
    viewportWidth: initial.width,
    documentWidth: null,
    overflow: null,
    activeTab: 'cargando…',
    suspects: [],
  })
  const iframeRef = useRef(null)

  const activeDevice = DEVICES.find((device) => device.width === width && device.height === height)

  const measure = useCallback(() => {
    const frame = iframeRef.current
    if (!frame?.contentDocument) return
    try {
      const doc = frame.contentDocument
      const root = doc.documentElement
      const viewportWidth = frame.contentWindow.innerWidth
      const suspects = [...doc.body.querySelectorAll('*')]
        .filter((element) => {
          const style = frame.contentWindow.getComputedStyle(element)
          if (style.position === 'fixed') return false
          const rect = element.getBoundingClientRect()
          return rect.right > viewportWidth + 2 || rect.left < -2
        })
        .slice(0, 8)
        .map(describeElement)

      setMetrics({
        viewportWidth,
        documentWidth: root.scrollWidth,
        overflow: root.scrollWidth > root.clientWidth + 1,
        activeTab: doc.querySelector('.tab-btn.active')?.textContent?.trim() || 'sin tab activo',
        suspects,
      })
    } catch {
      setMetrics((current) => ({ ...current, activeTab: 'sin acceso al iframe' }))
    }
  }, [])

  useEffect(() => {
    const params = new URLSearchParams(window.location.search)
    params.set('width', String(width))
    params.set('height', String(height))
    window.history.replaceState(null, '', `${window.location.pathname}?${params}`)
    const timers = [50, 350, 1000].map((delay) => window.setTimeout(measure, delay))
    return () => timers.forEach(window.clearTimeout)
  }, [width, height, measure])

  useEffect(() => {
    const interval = window.setInterval(measure, 1500)
    return () => window.clearInterval(interval)
  }, [measure])

  function selectDevice(device) {
    setWidth(device.width)
    setHeight(device.height)
  }

  function rotate() {
    setWidth(height)
    setHeight(width)
  }

  function reload() {
    setLoaded(false)
    setFrameKey((key) => key + 1)
  }

  async function copyUrl() {
    await navigator.clipboard.writeText(window.location.href)
    setCopied(true)
    window.setTimeout(() => setCopied(false), 1200)
  }

  function handleLoad() {
    setLoaded(true)
    window.setTimeout(measure, 100)
    window.setTimeout(measure, 900)
  }

  return (
    <main className="lab-shell">
      <header className="lab-header">
        <div>
          <span className="eyebrow">Laboratorio local ♡</span>
          <h1>Responsive del dashboard</h1>
          <p>El marco sirve el <code>index.html</code> real. Podés navegar todos sus tabs sin mantener una copia.</p>
        </div>
        <div className="header-actions">
          <button type="button" onClick={reload}>↻ Recargar</button>
          <button type="button" onClick={copyUrl}>{copied ? '✓ Copiado' : 'Copiar vista'}</button>
          <a href="/dashboard/" target="_blank" rel="noreferrer">Abrir limpio ↗</a>
        </div>
      </header>

      <section className="control-panel" aria-label="Controles responsive">
        <div className="device-presets">
          {DEVICES.map((device) => (
            <button
              type="button"
              key={device.id}
              className={activeDevice?.id === device.id ? 'active' : ''}
              onClick={() => selectDevice(device)}
            >
              <span>{device.icon}</span>
              <b>{device.label}</b>
              <small>{device.width} × {device.height}</small>
            </button>
          ))}
        </div>

        <div className="manual-controls">
          <label>
            Ancho
            <input value={width} type="number" min="320" max="1920" onChange={(event) => setWidth(clamp(event.target.value, 320, 1920))} />
          </label>
          <span>×</span>
          <label>
            Alto
            <input value={height} type="number" min="480" max="1400" onChange={(event) => setHeight(clamp(event.target.value, 480, 1400))} />
          </label>
          <button type="button" className="rotate" onClick={rotate} title="Rotar orientación">↻ Rotar</button>
          <label className="zoom-control">
            Escala visual <b>{zoom}%</b>
            <input type="range" min="40" max="100" step="5" value={zoom} onChange={(event) => setZoom(Number(event.target.value))} />
          </label>
        </div>
      </section>

      <section className="status-row" aria-live="polite">
        <span className={loaded ? 'status good' : 'status waiting'}>{loaded ? '● Dashboard cargado' : '○ Cargando dashboard'}</span>
        <span className="status">Viewport real: <b>{metrics.viewportWidth}px</b></span>
        <span className="status">Documento: <b>{metrics.documentWidth ?? '—'}px</b></span>
        <span className={`status ${metrics.overflow ? 'bad' : metrics.overflow === false ? 'good' : ''}`}>
          {metrics.overflow ? '⚠ Overflow global' : metrics.overflow === false ? '✓ Sin overflow global' : 'Revisando overflow'}
        </span>
        <span className="status">Tab: <b>{metrics.activeTab}</b></span>
        <button type="button" className="measure" onClick={measure}>Medir ahora</button>
      </section>

      {metrics.overflow && metrics.suspects.length > 0 && (
        <aside className="overflow-warning">
          <b>Elementos para inspeccionar:</b> {metrics.suspects.join(' · ')}
          <small>La lista orienta: un gráfico dentro de un contenedor con scroll puede aparecer aunque el overflow sea intencional.</small>
        </aside>
      )}

      <section className="workbench">
        <div className="ruler ruler-top" aria-hidden="true"><span>0</span><span>{Math.round(width / 2)}</span><span>{width}px</span></div>
        <div
          className="device-frame"
          style={{
            width: width + 20,
            height: height + 54,
            transform: `scale(${zoom / 100})`,
            marginBottom: (height + 54) * (zoom / 100 - 1),
          }}
        >
          <div className="device-bar">
            <i /><i /><i />
            <span>localhost:5173/dashboard/</span>
            <b>{width} × {height}</b>
          </div>
          <iframe
            key={frameKey}
            ref={iframeRef}
            src="/dashboard/"
            title="Dashboard argentino en prueba responsive"
            onLoad={handleLoad}
          />
        </div>
      </section>

      <footer>
        <b>Tip:</b> usá 100% para revisar tamaño táctil real; bajá la escala sólo para ver un viewport grande completo. La escala no modifica las media queries.
      </footer>
    </main>
  )
}
