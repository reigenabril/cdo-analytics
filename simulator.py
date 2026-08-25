"""
simulator.py
Motor de simulación académica, proyección de graduación y análisis 'What-If'.
"""

import math
import pandas as pd
from curriculum_data import CURRICULUM, CURRICULUM_BY_CODE

def calculate_target_gpa(df_subjects, target_gpa):
    """
    Calcula qué nota promedio necesita el estudiante en las materias pendientes 
    para alcanzar un promedio objetivo al graduarse.
    """
    graded_df = df_subjects[df_subjects['numeric_grade'].notna()]
    current_count = len(graded_df)
    current_sum = graded_df['numeric_grade'].sum()
    current_gpa = current_sum / current_count if current_count > 0 else 0.0
    
    pending_df = df_subjects[df_subjects['numeric_grade'].isna()]
    pending_count = len(pending_df)
    
    if pending_count == 0:
        return {
            'possible': True,
            'current_gpa': current_gpa,
            'required_avg': current_gpa,
            'pending_count': 0,
            'message': 'Ya completaste todas las materias con calificación numérica.'
        }
        
    total_count = current_count + pending_count
    needed_sum = (target_gpa * total_count) - current_sum
    required_avg = needed_sum / pending_count
    
    possible = (4.0 <= required_avg <= 10.0)
    
    return {
        'possible': possible,
        'current_gpa': round(current_gpa, 2),
        'target_gpa': round(target_gpa, 2),
        'required_avg': round(required_avg, 2),
        'current_count': current_count,
        'pending_count': pending_count,
        'total_count': total_count
    }

def simulate_future_gpa(df_subjects, simulated_grades_dict):
    """
    Calcula el GPA proyectado asignando notas simuladas a materias pendientes.
    simulated_grades_dict: {'I305': 8.0, 'I306': 9.0, ...}
    """
    graded_df = df_subjects[df_subjects['numeric_grade'].notna()]
    real_grades = list(graded_df['numeric_grade'].values)
    
    sim_grades = []
    for code, grade in simulated_grades_dict.items():
        if grade is not None and not math.isnan(grade):
            sim_grades.append(float(grade))
            
    total_grades = real_grades + sim_grades
    projected_gpa = sum(total_grades) / len(total_grades) if total_grades else 0.0
    current_gpa = sum(real_grades) / len(real_grades) if real_grades else 0.0
    
    return {
        'current_gpa': round(current_gpa, 2),
        'projected_gpa': round(projected_gpa, 2),
        'diff': round(projected_gpa - current_gpa, 2),
        'simulated_count': len(sim_grades),
        'total_evaluated': len(total_grades)
    }

def generate_graduation_roadmap(df_subjects, max_subjects_per_term=3, start_year=2026, start_term=2):
    """
    Genera un plan cronológico optimizado de cursada cuatrimestre a cuatrimestre
    respetando las correlatividades hasta la graduación.
    """
    approved_set = set(df_subjects[df_subjects['status'] == 'Aprobada']['code'].values)
    in_progress_set = set(df_subjects[df_subjects['status'].isin(['En Curso', 'Regular'])]['code'].values)
    
    # Asumimos que las que están 'En Curso' se aprueban al terminar el cuatrimestre actual
    pending_subjects = [row['code'] for _, row in df_subjects.iterrows() if row['status'] not in ['Aprobada']]
    
    roadmap = []
    current_year = start_year
    current_term = start_term
    
    sim_approved = set(approved_set)
    # Agregar las que están en curso al cuatrimestre actual si corresponde
    if in_progress_set:
        current_term_subjects = list(in_progress_set)
        roadmap.append({
            'term_name': f'{current_year} - {current_term}° Cuatrimestre (Actual)',
            'year': current_year,
            'term': current_term,
            'subjects': [CURRICULUM_BY_CODE[c] for c in current_term_subjects if c in CURRICULUM_BY_CODE],
            'is_current': True
        })
        sim_approved.update(in_progress_set)
        for c in in_progress_set:
            if c in pending_subjects:
                pending_subjects.remove(c)
                
        # Avanzar al siguiente término
        if current_term == 1:
            current_term = 2
        else:
            current_term = 1
            current_year += 1

    # Planificar los siguientes cuatrimestres
    max_iterations = 15 # Salvaguarda contra bucles
    iter_count = 0
    
    while pending_subjects and iter_count < max_iterations:
        iter_count += 1
        available_this_term = []
        
        for code in list(pending_subjects):
            subj = CURRICULUM_BY_CODE[code]
            reqs = subj['correlativas']
            can_take = True
            
            if 'REQ_13_MATERIAS' in reqs:
                if len(sim_approved) < 13:
                    can_take = False
            else:
                for r in reqs:
                    if r not in sim_approved:
                        can_take = False
                        break
                        
            if can_take:
                available_this_term.append(code)
                
        if not available_this_term:
            # No hay materias habilitadas directamente (caso anómalo de correlativas)
            break
            
        # Seleccionar hasta max_subjects_per_term priorizando año/semestre curricular
        available_this_term.sort(key=lambda c: (CURRICULUM_BY_CODE[c]['year'], CURRICULUM_BY_CODE[c]['semester']))
        chosen = available_this_term[:max_subjects_per_term]
        
        roadmap.append({
            'term_name': f'{current_year} - {current_term}° Cuatrimestre',
            'year': current_year,
            'term': current_term,
            'subjects': [CURRICULUM_BY_CODE[c] for c in chosen],
            'is_current': False
        })
        
        sim_approved.update(chosen)
        for c in chosen:
            pending_subjects.remove(c)
            
        # Avanzar cuatrimestre
        if current_term == 1:
            current_term = 2
        else:
            current_term = 1
            current_year += 1

    grad_term = roadmap[-1]['term_name'] if roadmap else 'Graduado'
    return {
        'roadmap': roadmap,
        'estimated_graduation': grad_term,
        'remaining_terms': len([r for r in roadmap if not r.get('is_current', False)])
    }
