"""
data_loader.py
Módulo de ingesta y procesamiento de datos académicos de SIU Guaraní para CDO UNLP.
"""

import re
import pandas as pd
from curriculum_data import CURRICULUM, CURRICULUM_BY_CODE

def clean_text(val):
    if pd.isna(val):
        return ''
    return str(val).strip()

def parse_code_from_name(name_str):
    match = re.search(r'\(([A-Z]\d{3})\)', name_str)
    if match:
        return match.group(1)
    return None

def extract_numeric_grade(raw_nota):
    if not raw_nota:
        return None
    # Check for digit at start
    match = re.search(r'^(\d+(\.\d+)?)', str(raw_nota).strip())
    if match:
        try:
            return float(match.group(1))
        except ValueError:
            return None
    return None

import os
import json

def load_academic_data(plan_file_path_or_bytes=None, 
                       actuacion_file_path_or_bytes=None):
    """
    Carga y procesa el plan de estudios y actuaciones provisorias o el JSON sanitizado.
    Retorna (student_info, subjects_df).
    """
    student_info = {
        'name': 'Abril Reigenborn',
        'degree': 'Licenciatura en Ciencia de Datos en Organizaciones (UNLP)',
        'plan': 'Plan 2024'
    }
    
    subjects_records = {}

    # 0. Cargar desde academic_data.json si existe (Modo Portfolio seguro para GitHub)
    for json_candidate in ['academic_data.json', '/Users/abril/Desktop/notas/academic_data.json']:
        if os.path.exists(json_candidate):
            try:
                with open(json_candidate, 'r', encoding='utf-8') as jf:
                    data = json.load(jf)
                    if 'student_info' in data:
                        student_info.update(data['student_info'])
                    if 'academic_history' in data:
                        subjects_records.update(data['academic_history'])
                break
            except Exception as e:
                print(f'Error al leer academic_data.json: {e}')

    # Determinar rutas por defecto para archivos XLS si se especificaron
    # 1. Leer Plan de Estudios (si se subió o pasó un archivo nuevo)
    if plan_file_path_or_bytes is not None:
        try:
            df_plan = pd.read_excel(plan_file_path_or_bytes, engine='calamine')
            
            # Extraer metadatos del estudiante
            for idx, row in df_plan.iterrows():
                val = clean_text(row.iloc[0])
                if 'Alumno:' in val:
                    student_info['name'] = val.replace('Alumno:', '').strip()
                elif 'Propuesta:' in val:
                    student_info['degree'] = val.replace('Propuesta:', '').strip()
                elif 'Plan:' in val:
                    student_info['plan'] = val.replace('Plan:', '').strip()

            # Localizar tabla de actividades
            header_idx = None
            for idx, row in df_plan.iterrows():
                if clean_text(row.iloc[0]) == 'Actividad':
                    header_idx = idx
                    break

            if header_idx is not None:
                for idx in range(header_idx + 1, len(df_plan)):
                    row = df_plan.iloc[idx]
                    actividad = clean_text(row.iloc[0])
                    if not actividad or actividad.startswith('(*)') or actividad.startswith('(-)') or actividad.startswith('(!)'):
                        continue
                    code = parse_code_from_name(actividad)
                    if not code:
                        continue
                    
                    raw_nota = clean_text(row.iloc[4])
                    origen = clean_text(row.iloc[5])
                    
                    subjects_records[code] = {
                        'raw_nota': raw_nota,
                        'origen': origen,
                        'numeric_grade': extract_numeric_grade(raw_nota)
                    }
        except Exception as e:
            print(f'Error al leer plan de estudios: {e}')

    # 2. Leer Actuación Provisoria (si existe)
    if actuacion_file_path_or_bytes is not None:
        try:
            df_act = pd.read_excel(actuacion_file_path_or_bytes, engine='calamine')
            for idx, row in df_act.iterrows():
                act_name = clean_text(row.get('Actividad', ''))
                nota = row.get('Nota', None)
                res = clean_text(row.get('Resultado', ''))
                if not act_name or pd.isna(nota):
                    continue
                
                # Buscar código correspondiente
                for c, data in CURRICULUM_BY_CODE.items():
                    if data['name'].lower() in act_name.lower() or act_name.lower() in data['name'].lower():
                        # Si no estaba aprobada con final en el plan principal, actualizar
                        current_orig = subjects_records.get(c, {}).get('origen', '')
                        if current_orig not in ['Examen', 'Promoción']:
                            num_g = float(nota) if pd.notna(nota) else None
                            disp_nota = f"{int(num_g) if num_g == int(num_g) else num_g} ({res})" if num_g else res
                            subjects_records[c] = {
                                'raw_nota': disp_nota,
                                'origen': 'Actuación Provisoria',
                                'numeric_grade': num_g
                            }
                        break
        except Exception as e:
            print(f'Error al leer actuación provisoria: {e}')

    # 3. Consolidar con el Curriculum oficial y determinar estados
    records = []
    
    # Primero identificar aprobadas para cálculo de correlativas
    approved_codes = set()
    regular_codes = set()
    en_curso_codes = set()

    for item in CURRICULUM:
        code = item['code']
        rec = subjects_records.get(code, {'raw_nota': '', 'origen': '', 'numeric_grade': None})
        origen = rec['origen']
        raw_nota = rec['raw_nota']

        if origen in ['Promoción', 'Examen', 'Actuación Provisoria', 'Equivalencia']:
            approved_codes.add(code)
        elif origen == 'Regularidad':
            regular_codes.add(code)
        elif origen == 'En Curso':
            en_curso_codes.add(code)

    for item in CURRICULUM:
        code = item['code']
        rec = subjects_records.get(code, {'raw_nota': '', 'origen': '', 'numeric_grade': None})
        origen = rec['origen']
        raw_nota = rec['raw_nota']
        num_grade = rec['numeric_grade']

        # Determinar estado
        if code in approved_codes:
            status = 'Aprobada'
        elif code in regular_codes:
            status = 'Regular'
        elif code in en_curso_codes:
            status = 'En Curso'
        else:
            # Evaluar correlatividades
            reqs = item['correlativas']
            all_reqs_met = True
            
            if 'REQ_13_MATERIAS' in reqs:
                if len(approved_codes) < 13:
                    all_reqs_met = False
            else:
                for r in reqs:
                    if r not in approved_codes and r not in regular_codes:
                        all_reqs_met = False
                        break
            
            if all_reqs_met:
                status = 'Habilitada'
            else:
                status = 'Bloqueada'

        records.append({
            'code': code,
            'name': item['name'],
            'year': item['year'],
            'semester': item['semester'],
            'area': item['area'],
            'hours': item['hours'],
            'skills': item['skills'],
            'correlativas': item['correlativas'],
            'status': status,
            'origen': origen if origen else 'Pendiente',
            'raw_nota': raw_nota,
            'numeric_grade': num_grade
        })

    df_subjects = pd.DataFrame(records)
    return student_info, df_subjects
