# CDO Analytics & Career Hub

Dashboard academico, malla curricular interactiva y planificador de graduacion para la Licenciatura en Ciencia de Datos en Organizaciones (UNLP).

## Caracteristicas

- **Dashboard de Rendimiento:** Metricas de promedio general, porcentaje de avance de la carrera y horas completadas.
- **Malla Curricular:** Mapa de materias por anio y semestre con deteccion de correlatividades y estados.
- **Simulador What-If:** Proyeccion de promedio final y calculo de calificaciones requeridas para alcanzar metas de GPA.
- **Planificador de Cursada:** Cronograma de materias por cuatrimestre optimizado por correlativas.
- **Matriz de Competencias:** Resumen de habilidades tecnicas y de negocio segun asignaturas cursadas.
- **Importador de Datos:** Carga dinamica de reportes exportados de SIU Guarani.

## Instalacion y Uso

1. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```

2. Ejecutar la aplicacion:
   ```bash
   streamlit run app.py
   ```

3. Abrir en el navegador: `http://localhost:8501`.

## Estructura

- `app.py`: Aplicacion principal en Streamlit.
- `data_loader.py`: Procesamiento y carga de datos academicos.
- `curriculum_data.py`: Plan de estudios oficial y correlatividades.
- `analytics.py`: Calculo de metricas y graficos.
- `simulator.py`: Motor de proyecciones y roadmap de graduacion.
