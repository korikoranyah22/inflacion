# Laboratorio responsive

Mini proyecto React + Vite para navegar el dashboard real desde localhost y probarlo en anchos conocidos.

## Ejecutar

```powershell
cd C:\Github\inflacion\responsive-lab
npm install
npm run dev
```

Abrir: <http://127.0.0.1:5173/>

## Qué hace

- sirve el `index.html` ubicado un nivel arriba en `/dashboard/`;
- no duplica el dashboard ni sus datos;
- ofrece presets de 360×800, 390×844, 430×932, 768×1024 y 1440×900;
- permite ingresar cualquier ancho/alto y rotar la orientación;
- mantiene la navegación y las interacciones reales dentro del iframe;
- informa si el documento tiene overflow horizontal global;
- conserva ancho y alto en la URL para compartir una vista concreta.

La escala visual sólo achica el marco en pantalla: no altera el viewport ni las media queries del dashboard.
