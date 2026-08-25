"""
app.py
Aplicación Streamlit: CDO Analytics & Career Hub (UNLP).
Dashboard académico, mapa curricular interactivo y simulador de graduación.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from curriculum_data import AREAS, CURRICULUM, CURRICULUM_BY_CODE
from data_loader import load_academic_data
from analytics import (
    calculate_kpis,
    create_grades_bar_chart,
    create_year_progress_chart,
    create_radar_skills_chart
)
from simulator import (
    calculate_target_gpa,
    simulate_future_gpa,
    generate_graduation_roadmap
)

st.set_page_config(
    page_title="CDO Analytics & Career Hub",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS para diseño moderno
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
        padding: 24px;
        border-radius: 16px;
        color: white;
        margin-bottom: 24px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    }
    .metric-card {
        background: white;
        border-radius: 12px;
        padding: 18px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
        text-align: center;
    }
    .metric-card h3 {
        margin: 0;
        font-size: 28px;
        font-weight: 700;
        color: #1E293B;
    }
    .metric-card p {
        margin: 4px 0 0 0;
        font-size: 13px;
        color: #64748B;
        font-weight: 500;
    }
    .status-pill {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 12px;
        font-weight: 600;
    }
    .pill-aprobada { background-color: #DCFCE7; color: #15803D; }
    .pill-encurso { background-color: #FEF3C7; color: #B45309; }
    .pill-regular { background-color: #DBEAFE; color: #1D4ED8; }
    .pill-habilitada { background-color: #F3E8FF; color: #7E22CE; }
    .pill-bloqueada { background-color: #F1F5F9; color: #64748B; }
    
    .subject-card {
        background: #FFFFFF;
        border-radius: 10px;
        padding: 14px;
        margin-bottom: 10px;
        border-left: 4px solid #3B82F6;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
</style>
""", unsafe_allow_html=True)

# ----------------- SIDEBAR -----------------
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/data-configuration.png", width=64)
    st.title("CDO Tracker")
    st.caption("Lic. en Ciencia de Datos en Organizaciones - UNLP")
    
    st.markdown("---")
    
    # Selector de pestañas
    nav_option = st.radio(
        "Navegación",
        [
            "📊 Dashboard de Rendimiento",
            "🗺️ Malla Curricular & Correlativas",
            "🔮 Simulador What-If & GPA",
            "📅 Planificador de Graduación",
            "💼 Matriz de Habilidades (CV)",
            "📁 Importar Archivos Guaraní"
        ]
    )
    
    st.markdown("---")
    
    # Cargar datos
    if 'custom_plan' in st.session_state and 'custom_act' in st.session_state:
        student_info, df_subjects = load_academic_data(
            st.session_state['custom_plan'],
            st.session_state['custom_act']
        )
    elif 'custom_plan' in st.session_state:
        student_info, df_subjects = load_academic_data(
            st.session_state['custom_plan']
        )
    else:
        student_info, df_subjects = load_academic_data()
        
    st.markdown(f"""
    **Estudiante:** {student_info['name']}  
    **Plan:** {student_info['plan']}  
    """)
    
    st.markdown("---")
    st.caption("Hecho para estudiantes y graduados de CDO UNLP 🚀")

# Calcular KPIs
kpis = calculate_kpis(df_subjects)

# ----------------- PESTAÑA 1: DASHBOARD -----------------
if nav_option == "📊 Dashboard de Rendimiento":
    st.markdown(f"""
    <div class='main-header'>
        <h1 style='margin:0; font-size:26px;'>🎓 Dashboard Académico & Rendimiento</h1>
        <p style='margin:6px 0 0 0; opacity:0.85;'>
            {student_info['name']} • {student_info['degree']} ({student_info['plan']})
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Top KPI Cards
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown(f"""
        <div class='metric-card'>
            <h3 style='color: #2563EB;'>{kpis['gpa']}</h3>
            <p>Promedio General (GPA)</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown(f"""
        <div class='metric-card'>
            <h3 style='color: #10B981;'>{kpis['pct_aprobado']}%</h3>
            <p>Carrera Aprobada ({kpis['aprobadas']}/{kpis['total_subjects']})</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown(f"""
        <div class='metric-card'>
            <h3 style='color: #F59E0B;'>{kpis['en_curso']}</h3>
            <p>Materias En Curso</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col4:
        st.markdown(f"""
        <div class='metric-card'>
            <h3 style='color: #8B5CF6;'>{kpis['habilitadas']}</h3>
            <p>Habilitadas para Cursar</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col5:
        st.markdown(f"""
        <div class='metric-card'>
            <h3 style='color: #0EA5E9;'>{kpis['completed_hours']} h</h3>
            <p>Horas Cátedra ({kpis['pct_hours']}%)</p>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Gráficos Principales
    col_g1, col_g2 = st.columns([3, 2])
    
    with col_g1:
        st.subheader("📈 Historial de Calificaciones por Asignatura")
        grades_chart = create_grades_bar_chart(df_subjects)
        if grades_chart:
            st.plotly_chart(grades_chart, use_container_width=True)
        else:
            st.info("No hay calificaciones numéricas registradas todavía.")
            
    with col_g2:
        st.subheader("🎯 Perfil y Balance por Área Temática")
        radar_chart = create_radar_skills_chart(kpis)
        st.plotly_chart(radar_chart, use_container_width=True)

    st.markdown("---")
    
    # Desglose por Área y Avance por Año
    col_a1, col_a2 = st.columns([1, 1])
    
    with col_a1:
        st.subheader("🏛️ Avance por Año Curricular")
        year_chart = create_year_progress_chart(df_subjects)
        st.plotly_chart(year_chart, use_container_width=True)
        
    with col_a2:
        st.subheader("📚 Estadísticas Detalladas por Área")
        for area, data in kpis['area_stats'].items():
            color = AREAS[area]['color']
            icon = AREAS[area]['icon']
            mean_str = f"{data['mean_grade']:.2f}" if data['mean_grade'] is not None else "S/D"
            st.markdown(f"""
            <div style='padding: 12px; background: #F8FAFC; border-radius: 8px; margin-bottom: 8px; border-left: 4px solid {color};'>
                <div style='display: flex; justify-content: space-between; align-items: center;'>
                    <strong>{icon} {area}</strong>
                    <span style='font-size: 14px; font-weight: 600;'>Promedio: {mean_str}</span>
                </div>
                <div style='display: flex; justify-content: space-between; font-size: 12px; color: #64748B; margin-top: 4px;'>
                    <span>{data['approved_count']} de {data['total_count']} materias ({data['pct_progress']:.0f}%)</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

# ----------------- PESTAÑA 2: MALLA CURRICULAR -----------------
elif nav_option == "🗺️ Malla Curricular & Correlativas":
    st.markdown(f"""
    <div class='main-header'>
        <h1 style='margin:0; font-size:26px;'>🗺️ Malla Curricular Interactiva</h1>
        <p style='margin:6px 0 0 0; opacity:0.85;'>
            Plan de 4 años y 8 semestres con estado en tiempo real y detección automática de correlativas.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Filtros
    fcol1, fcol2, fcol3 = st.columns([2, 2, 3])
    with fcol1:
        filter_area = st.selectbox("Filtrar por Área", ["Todas"] + list(AREAS.keys()))
    with fcol2:
        filter_status = st.selectbox("Filtrar por Estado", ["Todos", "Aprobada", "Regular", "En Curso", "Habilitada", "Bloqueada"])
    with fcol3:
        search_query = st.text_input("🔍 Buscar por nombre o código", "")
        
    filtered_df = df_subjects.copy()
    if filter_area != "Todas":
        filtered_df = filtered_df[filtered_df['area'] == filter_area]
    if filter_status != "Todos":
        filtered_df = filtered_df[filtered_df['status'] == filter_status]
    if search_query:
        filtered_df = filtered_df[
            filtered_df['name'].str.contains(search_query, case=False, na=False) |
            filtered_df['code'].str.contains(search_query, case=False, na=False)
        ]
        
    # Mostrar Malla por Años
    status_classes = {
        'Aprobada': 'pill-aprobada',
        'En Curso': 'pill-encurso',
        'Regular': 'pill-regular',
        'Habilitada': 'pill-habilitada',
        'Bloqueada': 'pill-bloqueada'
    }
    
    for year in range(1, 5):
        year_subjects = filtered_df[filtered_df['year'] == year]
        if year_subjects.empty:
            continue
            
        st.markdown(f"### 🗓️ {year}° Año")
        
        sem1_df = year_subjects[year_subjects['semester'] == 1]
        sem2_df = year_subjects[year_subjects['semester'] == 2]
        
        c1, c2 = st.columns(2)
        
        with c1:
            st.markdown(f"**1° Semestre** ({len(sem1_df)} materias)")
            for _, subj in sem1_df.iterrows():
                pclass = status_classes.get(subj['status'], 'pill-bloqueada')
                border_color = AREAS[subj['area']]['color']
                nota_display = f" • <strong>Nota: {subj['raw_nota']}</strong>" if subj['raw_nota'] else ""
                
                correlativas_str = ", ".join(subj['correlativas']) if subj['correlativas'] else "Ninguna"
                if 'REQ_13_MATERIAS' in subj['correlativas']:
                    correlativas_str = "13 materias aprobadas"
                    
                with st.expander(f"{subj['code']} - {subj['name']} | {subj['status']}"):
                    st.markdown(f"""
                    * **Área:** {AREAS[subj['area']]['icon']} {subj['area']}
                    * **Estado:** <span class='status-pill {pclass}'>{subj['status']}</span>{nota_display}
                    * **Origen:** {subj['origen']}
                    * **Carga horaria:** {subj['hours']} hs
                    * **Correlativas necesarias:** `{correlativas_str}`
                    * **Habilidades clave:** {', '.join(subj['skills'])}
                    """, unsafe_allow_html=True)
                    
        with c2:
            st.markdown(f"**2° Semestre** ({len(sem2_df)} materias)")
            for _, subj in sem2_df.iterrows():
                pclass = status_classes.get(subj['status'], 'pill-bloqueada')
                border_color = AREAS[subj['area']]['color']
                nota_display = f" • <strong>Nota: {subj['raw_nota']}</strong>" if subj['raw_nota'] else ""
                
                correlativas_str = ", ".join(subj['correlativas']) if subj['correlativas'] else "Ninguna"
                if 'REQ_13_MATERIAS' in subj['correlativas']:
                    correlativas_str = "13 materias aprobadas"
                    
                with st.expander(f"{subj['code']} - {subj['name']} | {subj['status']}"):
                    st.markdown(f"""
                    * **Área:** {AREAS[subj['area']]['icon']} {subj['area']}
                    * **Estado:** <span class='status-pill {pclass}'>{subj['status']}</span>{nota_display}
                    * **Origen:** {subj['origen']}
                    * **Carga horaria:** {subj['hours']} hs
                    * **Correlativas necesarias:** `{correlativas_str}`
                    * **Habilidades clave:** {', '.join(subj['skills'])}
                    """, unsafe_allow_html=True)
                    
        st.markdown("<br>", unsafe_allow_html=True)

# ----------------- PESTAÑA 3: SIMULADOR WHAT-IF -----------------
elif nav_option == "🔮 Simulador What-If & GPA":
    st.markdown(f"""
    <div class='main-header'>
        <h1 style='margin:0; font-size:26px;'>🔮 Simulador de Promedio & Análisis What-If</h1>
        <p style='margin:6px 0 0 0; opacity:0.85;'>
            Proyecta tu promedio final asignando notas simuladas o calculando el rendimiento necesario para alcanzar una meta.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    sim_tab1, sim_tab2 = st.tabs(["🎯 Calculadora de GPA Objetivo", "🎛️ Matriz de Simulación Nota por Nota"])
    
    with sim_tab1:
        st.subheader("¿Qué promedio necesitas para graduarte con una meta específica?")
        
        target = st.slider("Selecciona tu promedio deseado de graduación:", min_value=6.0, max_value=10.0, value=8.5, step=0.1)
        
        res = calculate_target_gpa(df_subjects, target)
        
        col_t1, col_t2, col_t3 = st.columns(3)
        with col_t1:
            st.metric("Promedio Actual", f"{res['current_gpa']:.2f}")
        with col_t2:
            st.metric("Meta de Graduación", f"{target:.2f}")
        with col_t3:
            req_color = "normal" if res['possible'] else "off"
            st.metric("Promedio Requerido en Pendientes", f"{res['required_avg']:.2f}")
            
        if res['possible']:
            if res['required_avg'] <= res['current_gpa']:
                st.success(f"🎉 ¡Meta muy alcanzable! Necesitas un promedio de **{res['required_avg']:.2f}** en tus {res['pending_count']} materias restantes para alcanzar {target:.2f}.")
            else:
                st.warning(f"⚡ Meta exigente: Necesitas un promedio de **{res['required_avg']:.2f}** en las {res['pending_count']} materias restantes para alcanzar {target:.2f}.")
        else:
            if res['required_avg'] > 10.0:
                st.error(f"Matemáticamente no es posible alcanzar {target:.2f} (requeriría un promedio de {res['required_avg']:.2f} superior a 10).")
            else:
                st.info(f"Ya tienes un promedio superior al objetivo fijado ({res['current_gpa']:.2f}).")
                
    with sim_tab2:
        st.subheader("Simula notas tentativas en las materias restantes:")
        pending_subjects = df_subjects[df_subjects['status'] != 'Aprobada']
        
        sim_grades = {}
        cols = st.columns(3)
        
        for idx, (_, subj) in enumerate(pending_subjects.iterrows()):
            c_idx = idx % 3
            with cols[c_idx]:
                sim_grades[subj['code']] = st.number_input(
                    f"{subj['code']} - {subj['name'][:22]}...",
                    min_value=4.0,
                    max_value=10.0,
                    value=8.0,
                    step=1.0,
                    key=f"sim_{subj['code']}"
                )
                
        sim_res = simulate_future_gpa(df_subjects, sim_grades)
        
        st.markdown("---")
        sc1, sc2, sc3 = st.columns(3)
        with sc1:
            st.metric("Promedio Actual", f"{sim_res['current_gpa']:.2f}")
        with sc2:
            st.metric("Promedio Proyectado con Simulación", f"{sim_res['projected_gpa']:.2f}", delta=f"{sim_res['diff']:+.2f}")
        with sc3:
            st.metric("Total Materias Evaluadas", f"{sim_res['total_evaluated']} / 28")

# ----------------- PESTAÑA 4: PLANIFICADOR -----------------
elif nav_option == "📅 Planificador de Graduación":
    st.markdown(f"""
    <div class='main-header'>
        <h1 style='margin:0; font-size:26px;'>📅 Planificador de Graduación & Roadmap</h1>
        <p style='margin:6px 0 0 0; opacity:0.85;'>
            Generación de hoja de ruta cuatrimestre a cuatrimestre optimizada por correlatividades.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col_p1, col_p2 = st.columns([1, 2])
    with col_p1:
        pace = st.slider("Materias por cuatrimestre que planeas cursar:", min_value=1, max_value=4, value=3)
        
    roadmap_data = generate_graduation_roadmap(df_subjects, max_subjects_per_term=pace)
    
    st.info(f"🎓 **Fecha estimada de graduación:** **{roadmap_data['estimated_graduation']}** ({roadmap_data['remaining_terms']} cuatrimestres restantes)")
    
    st.markdown("### 🗺️ Cronograma Sugerido de Cursada:")
    for term in roadmap_data['roadmap']:
        badge_style = "background:#EEF2FF; border-left:4px solid #6366F1;" if not term.get('is_current') else "background:#FEF3C7; border-left:4px solid #F59E0B;"
        st.markdown(f"""
        <div style='padding: 14px; {badge_style} border-radius: 8px; margin-bottom: 12px;'>
            <h4 style='margin:0 0 8px 0;'>📌 {term['term_name']}</h4>
        </div>
        """, unsafe_allow_html=True)
        
        term_cols = st.columns(len(term['subjects'])) if term['subjects'] else [st]
        for idx, subj in enumerate(term['subjects']):
            with term_cols[idx]:
                st.markdown(f"""
                <div class='subject-card'>
                    <strong>{subj['code']}</strong><br>
                    <span style='font-size: 13px;'>{subj['name']}</span><br>
                    <span style='font-size: 11px; color: #64748B;'>{AREAS[subj['area']]['icon']} {subj['area']}</span>
                </div>
                """, unsafe_allow_html=True)

# ----------------- PESTAÑA 5: SKILLS MATRIX -----------------
elif nav_option == "💼 Matriz de Habilidades (CV)":
    st.markdown(f"""
    <div class='main-header'>
        <h1 style='margin:0; font-size:26px;'>💼 Matriz de Competencias & Portafolio</h1>
        <p style='margin:6px 0 0 0; opacity:0.85;'>
            Stack tecnológico y habilidades adquiridas en base a tus materias aprobadas y en curso.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    approved_subjects = df_subjects[df_subjects['status'].isin(['Aprobada', 'En Curso'])]
    
    tech_skills = set()
    business_skills = set()
    math_skills = set()
    
    for _, s in approved_subjects.iterrows():
        if s['area'] == 'Computación':
            tech_skills.update(s['skills'])
        elif s['area'] == 'Gestión & Negocios':
            business_skills.update(s['skills'])
        elif s['area'] == 'Matemática':
            math_skills.update(s['skills'])
            
    c_sk1, c_sk2, c_sk3 = st.columns(3)
    
    with c_sk1:
        st.subheader("💻 Computación & Datos")
        for sk in sorted(tech_skills):
            st.markdown(f"* ✅ **{sk}**")
            
    with c_sk2:
        st.subheader("📈 Negocios & Gestión")
        for sk in sorted(business_skills):
            st.markdown(f"* 📊 **{sk}**")
            
    with c_sk3:
        st.subheader("📐 Métodos Cuantitativos")
        for sk in sorted(math_skills):
            st.markdown(f"* 🔢 **{sk}**")

# ----------------- PESTAÑA 6: IMPORTAR -----------------
elif nav_option == "📁 Importar Archivos Guaraní":
    st.markdown(f"""
    <div class='main-header'>
        <h1 style='margin:0; font-size:26px;'>📁 Actualizar Datos del SIU Guaraní</h1>
        <p style='margin:6px 0 0 0; opacity:0.85;'>
            Sube nuevos archivos exportados del SIU Guaraní para actualizar el dashboard en tiempo real.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    u_col1, u_col2 = st.columns(2)
    with u_col1:
        up_plan = st.file_uploader("Subir nuevo 'plan_estudios.xls' (.xls o .xlsx)", type=["xls", "xlsx"])
    with u_col2:
        up_act = st.file_uploader("Subir 'actuacion_provisoria_cursada.xls' (opcional)", type=["xls", "xlsx"])
        
    if up_plan:
        st.session_state['custom_plan'] = up_plan
        if up_act:
            st.session_state['custom_act'] = up_act
        st.success("✅ ¡Archivos cargados con éxito! Los datos del dashboard se han actualizado.")
        if st.button("Recargar Dashboard"):
            st.rerun()
