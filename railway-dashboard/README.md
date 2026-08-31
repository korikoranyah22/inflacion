# Paquete mínimo para Railway o Netlify

Esta carpeta es el único directorio que Railway necesita descargar para publicar el dashboard. No contiene los PDFs, microdatos, checkpoints ni copias completas de investigación del repositorio principal.

## Configuración del servicio en Railway

- **Root Directory:** `/railway-dashboard`
- **Watch Paths:** `/railway-dashboard/**`
- **Build Command:** dejar vacío
- **Start Command:** `npm start` (normalmente se detecta solo)
- **Healthcheck Path:** `/health`

La ruta `/` y la ruta histórica `/dashboard/` sirven el mismo dashboard.

## Configuración en Netlify

- **Base directory:** `railway-dashboard` (sin barra inicial)
- **Package directory:** dejar vacío
- **Build command:** dejar vacío
- **Publish directory:** `.`
- **Functions directory:** dejar vacío
- **Runtime:** no requiere selección manual

`netlify.toml` conserva la carpeta de publicación y hace que `/dashboard/` siga funcionando. Netlify sólo publica el contenido de esta carpeta, aunque el proveedor puede clonar el repositorio completo antes de iniciar el build.

## Actualizar el paquete

Después de modificar el dashboard o uno de sus CSV descargables, ejecutar desde la raíz:

```powershell
python scripts/sync_railway_dashboard.py
python scripts/validate_railway_bundle.py
```

El sincronizador sólo copia los archivos públicos requeridos y genera `.bundle-manifest.json` con tamaño y SHA-256.
