# CDO Analytics & Career Hub

Dashboard academico, malla curricular interactiva y planificador de graduacion para la
Licenciatura en Ciencia de Datos en Organizaciones (UNLP).

**Version web:** https://reigenabril.github.io/cdo-analytics/ — sitio estatico, sin servidor.

## Caracteristicas

- **Dashboard de Rendimiento:** promedio general, avance de la carrera, horas completadas y balance por area.
- **Malla Curricular:** 29 materias (plan oficial 2024, 2692 h) por anio y semestre, con correlatividades y estado de cada una.
- **Simulador What-If:** promedio necesario para una meta de graduacion y proyeccion con notas tentativas.
- **Planificador de Cursada:** cronograma por cuatrimestre respetando correlatividades, editable a mano.
- **Matriz de Competencias:** habilidades tecnicas, de negocio y cuantitativas segun materias aprobadas.
- **Importador de Datos:** carga de reportes del SIU Guarani (.xls/.xlsx) o `academic_data.json`, procesados en el navegador.

## Version web (GitHub Pages)

El sitio vive en la raiz del repo: HTML, CSS y JavaScript sin backend. La logica de `analytics.py` y
`simulator.py` esta portada a `docs/app.js`, y los datos se generan desde las fuentes Python.

```
index.html
styles.css
app.js
data.js               # generado, no editar a mano
.nojekyll
```

Regenerar los datos cuando cambie el plan de estudios o el historial academico:

```bash
python3 tools/build_static_data.py
```

Probar localmente:

```bash
python3 -m http.server 8000
# abrir http://localhost:8000/
```

### Publicar en GitHub Pages

1. Push a `main`.
2. Settings → Pages → **Source: Deploy from a branch** → Branch `main`, carpeta `/ (root)` → Save.
3. En un minuto queda online en `https://<usuario>.github.io/cdo-analytics/`.

Los graficos usan Plotly desde CDN y la importacion de Excel usa SheetJS desde CDN, asi que
la primera carga necesita conexion. Si el CDN no esta disponible la app sigue funcionando,
solo se muestran los graficos vacios.

## Version Streamlit (local)

Se mantiene la app original en Python, util para trabajar con los Excel del SIU sin navegador.

```bash
pip install -r requirements.txt
streamlit run app.py
```

Abrir `http://localhost:8501`.

## Estructura

- `app.py`: aplicacion Streamlit.
- `data_loader.py`: lectura de plan de estudios y actuaciones provisorias.
- `curriculum_data.py`: plan oficial y correlatividades (fuente de verdad).
- `analytics.py`: metricas y graficos.
- `simulator.py`: proyecciones y roadmap de graduacion.
- `academic_data.json`: historial academico sanitizado que usa el sitio.
- `tools/build_static_data.py`: genera `data.js` para la version web.
- `index.html`, `styles.css`, `app.js`: version estatica publicada en GitHub Pages.
