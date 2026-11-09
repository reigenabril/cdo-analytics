"""
app.py
CDO Analytics & Career Hub (UNLP).
Dashboard academico, malla curricular y simulador de graduacion.
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
    page_title="CDO Analytics",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        background: #0F172A;
        padding: 20px 24px;
        border-radius: 12px;
        color: white;
        margin-bottom: 20px;
    }
    .metric-card {
        background: white;
        border-radius: 10px;
        padding: 16px;
        border: 1px solid #E2E8F0;
        text-align: center;
    }
    .metric-card h3 {
        margin: 0;
        font-size: 26px;
        font-weight: 700;
        color: #0F172A;
    }
    .metric-card p {
        margin: 4px 0 0 0;
        font-size: 13px;
        color: #64748B;
        font-weight: 500;
    }
    .status-pill {
        display: inline-block;
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 11px;
        font-weight: 600;
    }
    .pill-aprobada { background-color: #DCFCE7; color: #15803D; }
    .pill-encurso { background-color: #FEF3C7; color: #B45309; }
    .pill-regular { background-color: #DBEAFE; color: #1D4ED8; }
    .pill-habilitada { background-color: #F3E8FF; color: #7E22CE; }
    .pill-bloqueada { background-color: #F1F5F9; color: #64748B; }
    
    .subject-card {
        background: #FFFFFF;
        border-radius: 8px;
        padding: 12px;
        margin-bottom: 8px;
        border-left: 3px solid #3B82F6;
        border-top: 1px solid #F1F5F9;
        border-right: 1px solid #F1F5F9;
        border-bottom: 1px solid #F1F5F9;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.title("CDO Analytics")
    st.caption("Lic. en Ciencia de Datos en Organizaciones - UNLP")
    st.markdown("---")
    
    nav_option = st.radio(
        "Menu",
        [
            "Dashboard de Rendimiento",
            "Malla Curricular",
            "Simulador What-If",
            "Planificador de Graduacion",
            "Matriz de Competencias",
            "Importar Archivos"
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

kpis = calculate_kpis(df_subjects)

# 1. DASHBOARD
if nav_option == "Dashboard de Rendimiento":
    st.markdown(f"""
    <div class='main-header'>
        <h2 style='margin:0; font-size:22px;'>Dashboard Academico</h2>
        <p style='margin:4px 0 0 0; opacity:0.8; font-size:14px;'>
            {student_info['name']} &bull; {student_info['degree']}
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.markdown(f"""
        <div class='metric-card'>
            <h3 style='color: #2563EB;'>{kpis['gpa']}</h3>
            <p>Promedio General</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class='metric-card'>
            <h3 style='color: #10B981;'>{kpis['pct_aprobado']}%</h3>
            <p>Aprobadas ({kpis['aprobadas']}/{kpis['total_subjects']})</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class='metric-card'>
            <h3 style='color: #D97706;'>{kpis['en_curso']}</h3>
            <p>En Curso</p>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class='metric-card'>
            <h3 style='color: #7C3AED;'>{kpis['habilitadas']}</h3>
            <p>Habilitadas</p>
        </div>
        """, unsafe_allow_html=True)
    with col5:
        st.markdown(f"""
        <div class='metric-card'>
            <h3 style='color: #0284C7;'>{kpis['completed_hours']} h</h3>
            <p>Horas ({kpis['pct_hours']}%)</p>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    col_g1, col_g2 = st.columns([3, 2])
    with col_g1:
        st.subheader("Calificaciones por Asignatura")
        grades_chart = create_grades_bar_chart(df_subjects)
        if grades_chart:
            st.plotly_chart(grades_chart, use_container_width=True)
        else:
            st.info("Sin calificaciones numericas registradas.")
            
    with col_g2:
        st.subheader("Balance por Area Tematica")
        radar_chart = create_radar_skills_chart(kpis)
        st.plotly_chart(radar_chart, use_container_width=True)

    st.markdown("---")
    
    col_a1, col_a2 = st.columns([1, 1])
    with col_a1:
        st.subheader("Avance por Anio")
        year_chart = create_year_progress_chart(df_subjects)
        st.plotly_chart(year_chart, use_container_width=True)
        
    with col_a2:
        st.subheader("Resumen por Area")
        for area, data in kpis['area_stats'].items():
            color = AREAS[area]['color']
            mean_str = f"{data['mean_grade']:.2f}" if data['mean_grade'] is not None else "S/D"
            st.markdown(f"""
            <div style='padding: 10px 14px; background: #F8FAFC; border-radius: 6px; margin-bottom: 6px; border-left: 3px solid {color};'>
                <div style='display: flex; justify-content: space-between;'>
                    <strong>{area}</strong>
                    <span>Promedio: {mean_str}</span>
                </div>
                <div style='font-size: 12px; color: #64748B; margin-top: 2px;'>
                    {data['approved_count']} de {data['total_count']} materias ({data['pct_progress']:.0f}%)
                </div>
            </div>
            """, unsafe_allow_html=True)

# 2. MALLA CURRICULAR
elif nav_option == "Malla Curricular":
    st.markdown(f"""
    <div class='main-header'>
        <h2 style='margin:0; font-size:22px;'>Malla Curricular</h2>
        <p style='margin:4px 0 0 0; opacity:0.8; font-size:14px;'>
            Plan de 4 anios y correlatividades.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    fcol1, fcol2, fcol3 = st.columns([2, 2, 3])
    with fcol1:
        filter_area = st.selectbox("Area", ["Todas"] + list(AREAS.keys()))
    with fcol2:
        filter_status = st.selectbox("Estado", ["Todos", "Aprobada", "Regular", "En Curso", "Habilitada", "Bloqueada"])
    with fcol3:
        search_query = st.text_input("Buscar materia o codigo", "")
        
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
            
        st.markdown(f"### {year} Anio")
        sem1_df = year_subjects[year_subjects['semester'] == 1]
        sem2_df = year_subjects[year_subjects['semester'] == 2]
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"**1 Semestre** ({len(sem1_df)} materias)")
            for _, subj in sem1_df.iterrows():
                pclass = status_classes.get(subj['status'], 'pill-bloqueada')
                nota_display = f" &bull; <strong>Nota: {subj['raw_nota']}</strong>" if subj['raw_nota'] else ""
                correlativas_str = ", ".join(subj['correlativas']) if subj['correlativas'] else "Ninguna"
                if 'REQ_13_MATERIAS' in subj['correlativas']:
                    correlativas_str = "13 materias aprobadas"
                    
                with st.expander(f"{subj['code']} - {subj['name']} | {subj['status']}"):
                    st.markdown(f"""
                    * **Area:** {subj['area']}
                    * **Estado:** <span class='status-pill {pclass}'>{subj['status']}</span>{nota_display}
                    * **Origen:** {subj['origen']}
                    * **Horas:** {subj['hours']} hs
                    * **Correlativas:** `{correlativas_str}`
                    * **Temas:** {', '.join(subj['skills'])}
                    """, unsafe_allow_html=True)
                    
        with c2:
            st.markdown(f"**2 Semestre** ({len(sem2_df)} materias)")
            for _, subj in sem2_df.iterrows():
                pclass = status_classes.get(subj['status'], 'pill-bloqueada')
                nota_display = f" &bull; <strong>Nota: {subj['raw_nota']}</strong>" if subj['raw_nota'] else ""
                correlativas_str = ", ".join(subj['correlativas']) if subj['correlativas'] else "Ninguna"
                if 'REQ_13_MATERIAS' in subj['correlativas']:
                    correlativas_str = "13 materias aprobadas"
                    
                with st.expander(f"{subj['code']} - {subj['name']} | {subj['status']}"):
                    st.markdown(f"""
                    * **Area:** {subj['area']}
                    * **Estado:** <span class='status-pill {pclass}'>{subj['status']}</span>{nota_display}
                    * **Origen:** {subj['origen']}
                    * **Horas:** {subj['hours']} hs
                    * **Correlativas:** `{correlativas_str}`
                    * **Temas:** {', '.join(subj['skills'])}
                    """, unsafe_allow_html=True)

# 3. SIMULADOR WHAT-IF
elif nav_option == "Simulador What-If":
    st.markdown(f"""
    <div class='main-header'>
        <h2 style='margin:0; font-size:22px;'>Simulador de Promedio</h2>
        <p style='margin:4px 0 0 0; opacity:0.8; font-size:14px;'>
            Proyecciones de calificaciones y metas de rendimiento.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    sim_tab1, sim_tab2 = st.tabs(["Meta de Promedio", "Simulacion Individual"])
    
    with sim_tab1:
        st.subheader("Calculo de Promedio Requerido")
        target = st.slider("Promedio objetivo de graduacion:", min_value=6.0, max_value=10.0, value=8.5, step=0.1)
        res = calculate_target_gpa(df_subjects, target)
        
        col_t1, col_t2, col_t3 = st.columns(3)
        with col_t1:
            st.metric("Promedio Actual", f"{res['current_gpa']:.2f}")
        with col_t2:
            st.metric("Meta", f"{target:.2f}")
        with col_t3:
            st.metric("Promedio Necesario en Pendientes", f"{res['required_avg']:.2f}")
            
        if res['possible']:
            st.info(f"Se requiere un promedio de {res['required_avg']:.2f} en las {res['pending_count']} materias restantes para alcanzar {target:.2f}.")
        else:
            if res['required_avg'] > 10.0:
                st.warning(f"La meta de {target:.2f} requeriria un promedio superior a 10 ({res['required_avg']:.2f}).")
            else:
                st.info(f"El promedio actual ({res['current_gpa']:.2f}) ya supera el objetivo fijado.")
                
    with sim_tab2:
        st.subheader("Notas Tentativas en Materias Restantes")
        pending_subjects = df_subjects[df_subjects['status'] != 'Aprobada']
        
        sim_grades = {}
        cols = st.columns(3)
        for idx, (_, subj) in enumerate(pending_subjects.iterrows()):
            c_idx = idx % 3
            with cols[c_idx]:
                sim_grades[subj['code']] = st.number_input(
                    f"{subj['code']} - {subj['name'][:22]}",
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
            st.metric("Promedio Proyectado", f"{sim_res['projected_gpa']:.2f}", delta=f"{sim_res['diff']:+.2f}")
        with sc3:
            st.metric("Materias Evaluadas", f"{sim_res['total_evaluated']} / {len(df_subjects)}")

# 4. PLANIFICADOR
elif nav_option == "Planificador de Graduacion":
    st.markdown(f"""
    <div class='main-header'>
        <h2 style='margin:0; font-size:22px;'>Planificador de Cursada</h2>
        <p style='margin:4px 0 0 0; opacity:0.8; font-size:14px;'>
            Secuencia sugerida de cuatrimestres segun correlativas.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col_p1, col_p2 = st.columns([1, 2])
    with col_p1:
        pace = st.slider("Materias por cuatrimestre:", min_value=1, max_value=4, value=3)
        
    roadmap_data = generate_graduation_roadmap(df_subjects, max_subjects_per_term=pace)
    st.info(f"Fecha estimada de graduacion: {roadmap_data['estimated_graduation']} ({roadmap_data['remaining_terms']} cuatrimestres restantes)")
    
    st.subheader("Cronograma Sugerido")
    for term in roadmap_data['roadmap']:
        badge_style = "background:#F8FAFC; border-left:3px solid #3B82F6;" if not term.get('is_current') else "background:#FEF3C7; border-left:3px solid #D97706;"
        st.markdown(f"""
        <div style='padding: 10px 14px; {badge_style} border-radius: 6px; margin-bottom: 8px;'>
            <strong>{term['term_name']}</strong>
        </div>
        """, unsafe_allow_html=True)
        
        term_cols = st.columns(len(term['subjects'])) if term['subjects'] else [st]
        for idx, subj in enumerate(term['subjects']):
            with term_cols[idx]:
                st.markdown(f"""
                <div class='subject-card'>
                    <strong>{subj['code']}</strong><br>
                    <span style='font-size: 13px;'>{subj['name']}</span><br>
                    <span style='font-size: 11px; color: #64748B;'>{subj['area']}</span>
                </div>
                """, unsafe_allow_html=True)

# 5. MATRIZ DE COMPETENCIAS
elif nav_option == "Matriz de Competencias":
    st.markdown(f"""
    <div class='main-header'>
        <h2 style='margin:0; font-size:22px;'>Matriz de Competencias</h2>
        <p style='margin:4px 0 0 0; opacity:0.8; font-size:14px;'>
            Habilidades tecnicas y metodologicas adquiridas.
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
        st.subheader("Computacion & Datos")
        for sk in sorted(tech_skills):
            st.markdown(f"- {sk}")
            
    with c_sk2:
        st.subheader("Negocios & Gestion")
        for sk in sorted(business_skills):
            st.markdown(f"- {sk}")
            
    with c_sk3:
        st.subheader("Metodos Cuantitativos")
        for sk in sorted(math_skills):
            st.markdown(f"- {sk}")

# 6. IMPORTAR ARCHIVOS
elif nav_option == "Importar Archivos":
    st.markdown(f"""
    <div class='main-header'>
        <h2 style='margin:0; font-size:22px;'>Importar Archivos</h2>
        <p style='margin:4px 0 0 0; opacity:0.8; font-size:14px;'>
            Actualizar datos cargando reportes del SIU Guarani.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    u_col1, u_col2 = st.columns(2)
    with u_col1:
        up_plan = st.file_uploader("Subir plan_estudios.xls (.xls o .xlsx)", type=["xls", "xlsx"])
    with u_col2:
        up_act = st.file_uploader("Subir actuacion_provisoria_cursada.xls (opcional)", type=["xls", "xlsx"])
        
    if up_plan:
        st.session_state['custom_plan'] = up_plan
        if up_act:
            st.session_state['custom_act'] = up_act
        st.success("Archivos cargados con exito.")
        if st.button("Actualizar Dashboard"):
            st.rerun()
