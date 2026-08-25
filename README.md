# 🎓 CDO Analytics & Career Hub (UNLP)

> **Plataforma Integral de Inteligencia Académica, Malla Curricular Interactiva y Simulador de Graduación** para la carrera **Licenciatura en Ciencia de Datos en Organizaciones** (Facultad de Informática & Facultad de Ciencias Económicas - Universidad Nacional de La Plata).

---

## 🌟 Características Principales

1. **📊 Dashboard de Rendimiento & Analytics:**
   - Cálculo automático de **GPA / Promedio histórico**, porcentaje de avance de la carrera y horas cátedra acumuladas.
   - Historial interactivo de calificaciones por materia con línea de corte de promedio.
   - **Radar / Spider Chart** con el balance de formación entre Computación, Matemática, Negocios y Práctica Profesional.
   - Desglose de materias aprobadas vs en curso vs pendientes año por año.

2. **🗺️ Malla Curricular & Grafo de Correlatividades:**
   - Mapa interactivo de los 4 años y 8 semestres de la carrera.
   - Detección automática del estado de cada materia: `Aprobada`, `En Curso`, `Regular`, `Habilitada para Cursar` y `Bloqueada por Correlativas`.
   - Filtros dinámicos por área temática, estado o búsqueda por nombre/código.
   - Fichas detalladas con correlatividades requeridas, origen de la nota y habilidades técnicas asociadas.

3. **🔮 Simulador "What-If" & GPA Objetivo:**
   - **Calculadora de Meta:** Ingresa tu promedio deseado de graduación (ej. 8.5 o 9.0) y calcula la nota promedio exacta requerida en las materias pendientes.
   - **Matriz de Simulación:** Asigna notas tentativas a materias futuras y observa el impacto en tiempo real en tu promedio proyectado.

4. **📅 Planificador Inteligente de Graduación:**
   - Motor de optimización de cursada cuatrimestre a cuatrimestre basado en el árbol de dependencias y correlatividades.
   - Selector de ritmo de cursada (1 a 4 materias por cuatrimestre).
   - Proyección estimada del cuatrimestre y año de graduación.

5. **💼 Matriz de Competencias & Portafolio (LinkedIn/CV):**
   - Agrupación automática de todas las tecnologías y conocimientos adquiridos (Python, SQL, Linux, Machine Learning, Big Data, Finanzas, BPMN, PowerBI, etc.) según tus materias aprobadas.

6. **📁 Importador Dinámico de SIU Guaraní:**
   - Soporte para arrastrar nuevos archivos `.xls` o `.xlsx` descargados de Guaraní para actualizar todo en segundos.

---

## 🚀 Cómo Ejecutar la Aplicación

1. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Iniciar la aplicación:**
   ```bash
   streamlit run app.py
   ```

3. La aplicación se abrirá automáticamente en tu navegador en `http://localhost:8501`.

---

## 📁 Estructura del Proyecto

* [`app.py`](app.py): Interfaz web moderna con Streamlit, tabs de navegación y componentes interactivos.
* [`data_loader.py`](data_loader.py): Parser inteligente para archivos de SIU Guaraní (`plan_estudios.xls` y `actuacion_provisoria_cursada.xls`).
* [`curriculum_data.py`](curriculum_data.py): Base de conocimiento oficial del Plan 2024 de CDO UNLP (materias, códigos, correlatividades, horas y skills).
* [`analytics.py`](analytics.py): Métricas académicas y visualizaciones con Plotly.
* [`simulator.py`](simulator.py): Algoritmos de simulación What-If y generador de roadmap cronológico de graduación.
* [`requirements.txt`](requirements.txt): Dependencias necesarias.
