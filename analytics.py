"""
analytics.py
Módulo de cálculo de métricas, estadísticas académicas y generación de visualizaciones Plotly.
"""

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from curriculum_data import AREAS, CURRICULUM

def calculate_kpis(df_subjects):
    """Calcula los KPIs principales del estudiante."""
    total_subjects = len(df_subjects)
    
    # Materias con nota numérica
    num_grades_df = df_subjects[df_subjects['numeric_grade'].notna()]
    gpa = num_grades_df['numeric_grade'].mean() if len(num_grades_df) > 0 else 0.0
    
    # Contadores de estado
    status_counts = df_subjects['status'].value_counts().to_dict()
    aprobadas = status_counts.get('Aprobada', 0)
    en_curso = status_counts.get('En Curso', 0)
    regulares = status_counts.get('Regular', 0)
    habilitadas = status_counts.get('Habilitada', 0)
    bloqueadas = status_counts.get('Bloqueada', 0)
    
    pct_aprobado = (aprobadas / total_subjects) * 100
    pct_en_proceso = ((aprobadas + en_curso + regulares) / total_subjects) * 100
    
    # Horas completadas
    total_hours = df_subjects['hours'].sum()
    completed_hours = df_subjects[df_subjects['status'] == 'Aprobada']['hours'].sum()
    pct_hours = (completed_hours / total_hours) * 100 if total_hours > 0 else 0
    
    # Promedio por área
    area_stats = {}
    for area_name in AREAS.keys():
        area_df = num_grades_df[num_grades_df['area'] == area_name]
        area_total = len(df_subjects[df_subjects['area'] == area_name])
        area_approved = len(df_subjects[(df_subjects['area'] == area_name) & (df_subjects['status'] == 'Aprobada')])
        area_mean = area_df['numeric_grade'].mean() if len(area_df) > 0 else None
        
        area_stats[area_name] = {
            'mean_grade': area_mean,
            'approved_count': area_approved,
            'total_count': area_total,
            'pct_progress': (area_approved / area_total * 100) if area_total > 0 else 0
        }
        
    return {
        'gpa': round(gpa, 2),
        'total_subjects': total_subjects,
        'aprobadas': aprobadas,
        'en_curso': en_curso,
        'regulares': regulares,
        'habilitadas': habilitadas,
        'bloqueadas': bloqueadas,
        'pct_aprobado': round(pct_aprobado, 1),
        'pct_en_proceso': round(pct_en_proceso, 1),
        'total_hours': total_hours,
        'completed_hours': completed_hours,
        'pct_hours': round(pct_hours, 1),
        'area_stats': area_stats,
        'graded_count': len(num_grades_df)
    }

def create_grades_bar_chart(df_subjects):
    """Gráfico de barras interactivo con todas las notas obtenidas por materia."""
    df_graded = df_subjects[df_subjects['numeric_grade'].notna()].copy()
    if df_graded.empty:
        return None
    
    color_map = {k: v['color'] for k, v in AREAS.items()}
    
    fig = px.bar(
        df_graded,
        x='code',
        y='numeric_grade',
        color='area',
        color_discrete_map=color_map,
        hover_data=['name', 'origen', 'raw_nota'],
        text='numeric_grade',
        labels={'code': 'Materia', 'numeric_grade': 'Nota Obtenida', 'area': 'Área Temática'}
    )
    
    mean_val = df_graded['numeric_grade'].mean()
    fig.add_hline(
        y=mean_val,
        line_dash="dash",
        line_color="#E11D48",
        annotation_text=f"Promedio: {mean_val:.2f}",
        annotation_position="top right"
    )
    
    fig.update_traces(textposition='outside')
    fig.update_layout(
        yaxis=dict(range=[0, 11], tickmode='linear', tick0=0, dtick=1),
        xaxis_title="Código de Materia",
        yaxis_title="Nota (Escala 1 - 10)",
        legend_title="Área",
        template="plotly_white",
        height=420,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    return fig

def create_year_progress_chart(df_subjects):
    """Gráfico de avance por año de la carrera (1° a 4° año)."""
    years_data = []
    for year in range(1, 5):
        year_df = df_subjects[df_subjects['year'] == year]
        tot = len(year_df)
        aprob = len(year_df[year_df['status'] == 'Aprobada'])
        encurso = len(year_df[year_df['status'].isin(['En Curso', 'Regular'])])
        pend = tot - aprob - encurso
        
        years_data.append({
            'Año': f'{year}° Año',
            'Aprobadas': aprob,
            'En Curso / Regular': encurso,
            'Pendientes': pend,
            'Total': tot
        })
    
    df_years = pd.DataFrame(years_data)
    
    fig = go.Figure()
    fig.add_trace(go.Bar(name='Aprobadas', x=df_years['Año'], y=df_years['Aprobadas'], marker_color='#10B981'))
    fig.add_trace(go.Bar(name='En Curso / Regular', x=df_years['Año'], y=df_years['En Curso / Regular'], marker_color='#F59E0B'))
    fig.add_trace(go.Bar(name='Pendientes', x=df_years['Año'], y=df_years['Pendientes'], marker_color='#94A3B8'))
    
    fig.update_layout(
        barmode='stack',
        template='plotly_white',
        yaxis_title='Cantidad de Materias',
        height=380,
        margin=dict(l=20, r=20, t=30, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    return fig

def create_radar_skills_chart(kpis):
    """Gráfico de radar (Spider Chart) con el perfil de formación."""
    categories = []
    values_progress = []
    values_mean = []
    
    for area, stats in kpis['area_stats'].items():
        categories.append(area)
        values_progress.append(stats['pct_progress'])
        # Normalizar promedio de 0-10 a 0-100%
        mean_scaled = (stats['mean_grade'] * 10) if stats['mean_grade'] else 0
        values_mean.append(mean_scaled)
        
    categories.append(categories[0])
    values_progress.append(values_progress[0])
    values_mean.append(values_mean[0])
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=values_progress,
        theta=categories,
        fill='toself',
        name='% Avance de Créditos',
        line_color='#3B82F6',
        fillcolor='rgba(59, 130, 246, 0.25)'
    ))
    
    fig.add_trace(go.Scatterpolar(
        r=values_mean,
        theta=categories,
        fill='toself',
        name='Rendimiento Promedio (/100)',
        line_color='#10B981',
        fillcolor='rgba(16, 185, 129, 0.2)'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                ticksuffix='%'
            )
        ),
        showlegend=True,
        template='plotly_white',
        height=380,
        margin=dict(l=40, r=40, t=30, b=30),
        legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5)
    )
    return fig
