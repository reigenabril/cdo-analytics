# CDO Analytics & Career Hub

Dashboard academico, malla curricular interactiva y planificador de graduacion para la
Licenciatura en Ciencia de Datos en Organizaciones (UNLP).

**Version web:** https://reigenabril.github.io/cdo-analytics/

Sitio estatico (HTML, CSS y JavaScript): sin backend, sin build, se publica tal cual en
GitHub Pages.

## Caracteristicas

- **Dashboard de Rendimiento:** promedio general, avance de la carrera, horas completadas y balance por area.
- **Malla Curricular:** 29 materias (plan oficial 2024, 2692 h) por anio y semestre, con correlatividades y estado de cada una.
- **Simulador What-If:** promedio necesario para una meta de graduacion y proyeccion con notas tentativas.
- **Planificador de Cursada:** cronograma por cuatrimestre con validacion de correlatividades; las materias se mueven a mano y el plan queda guardado en el navegador.
- **Matriz de Competencias:** habilidades tecnicas, de negocio y cuantitativas segun materias aprobadas.
- **Importador de Datos:** reportes del SIU Guarani (.xls/.xlsx) o `academic_data.json`, procesados en el navegador.

## Datos

- `curriculum_data.py`: plan oficial y correlatividades. Es la fuente de verdad.
- `academic_data.json`: historial academico (`student_info` + `academic_history`).
- `data.js`: datos que consume el sitio. Es generado, no editar a mano.

Despues de cambiar notas o el plan de estudios:

```bash
python3 tools/build_static_data.py
```

Solo necesita Python 3, sin dependencias.

## Desarrollo local

```bash
python3 -m http.server 8000
# abrir http://localhost:8000/
```

## Publicacion

GitHub Pages sirve el repositorio desde `main` / `(root)`; `.nojekyll` desactiva Jekyll.
Cada push a `main` republica el sitio.

## Estructura

- `index.html`, `styles.css`, `app.js`: la aplicacion.
- `data.js`: datos para el navegador (generado por `tools/build_static_data.py`).
- `curriculum_data.py`: plan de estudios oficial y correlatividades.
- `academic_data.json`: historial academico.
- `.nojekyll`: evita el procesamiento de Jekyll.

Los graficos usan Plotly y la importacion de Excel usa SheetJS, ambos desde CDN: la primera
carga necesita conexion. Sin CDN la app sigue funcionando, solo quedan los graficos vacios.
