# Paquete mínimo para Railway

Esta carpeta es el único directorio que Railway necesita descargar para publicar el dashboard. No contiene los PDFs, microdatos, checkpoints ni copias completas de investigación del repositorio principal.

## Configuración del servicio en Railway

- **Root Directory:** `/railway-dashboard`
- **Watch Paths:** `/railway-dashboard/**`
- **Build Command:** dejar vacío
- **Start Command:** `npm start` (normalmente se detecta solo)
- **Healthcheck Path:** `/health`

La ruta `/` y la ruta histórica `/dashboard/` sirven el mismo dashboard.

## Actualizar el paquete

Después de modificar el dashboard o uno de sus CSV descargables, ejecutar desde la raíz:

```powershell
python scripts/sync_railway_dashboard.py
python scripts/validate_railway_bundle.py
```

El sincronizador sólo copia los archivos públicos requeridos y genera `.bundle-manifest.json` con tamaño y SHA-256.
