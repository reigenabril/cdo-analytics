"""
curriculum_data.py
Información oficial del Plan de Estudios de la Licenciatura en Ciencia de Datos en Organizaciones (CDO - UNLP).
Plan 2024 - Co-dictada por Facultad de Informática y Facultad de Ciencias Económicas.
"""

AREAS = {
    "Computación": {
        "color": "#3B82F6",
        "icon": "",
        "desc": "Algoritmos, software, bases de datos, big data e inteligencia artificial."
    },
    "Matemática": {
        "color": "#8B5CF6",
        "icon": "",
        "desc": "Cálculo, álgebra lineal, probabilidades, estadística y optimización."
    },
    "Gestión & Negocios": {
        "color": "#10B981",
        "icon": "",
        "desc": "Organizaciones, economía, finanzas, costos, personas y estrategia."
    },
    "General / Profesional": {
        "color": "#F59E0B",
        "icon": "",
        "desc": "Idiomas y Práctica Profesional Supervisada (PPS)."
    }
}

CURRICULUM = [
    # --- AÑO 1 - SEMESTRE 1 ---
    {
        "code": "I101",
        "name": "Algoritmos y Programación I",
        "year": 1,
        "semester": 1,
        "area": "Computación",
        "correlativas": [],
        "skills": ["Python / C", "Estructuras de Control", "Modularización", "Algoritmos Básicos"],
        "hours": 96
    },
    {
        "code": "X102",
        "name": "Matemática A",
        "year": 1,
        "semester": 1,
        "area": "Matemática",
        "correlativas": [],
        "skills": ["Cálculo Diferencial", "Límites", "Derivadas", "Funciones"],
        "hours": 96
    },
    {
        "code": "E103",
        "name": "Gestión de las Organizaciones",
        "year": 1,
        "semester": 1,
        "area": "Gestión & Negocios",
        "correlativas": [],
        "skills": ["Estructura Organizacional", "Procesos Administrativos", "Toma de Decisiones", "Modelos de Gestión"],
        "hours": 64
    },

    # --- AÑO 1 - SEMESTRE 2 ---
    {
        "code": "I104",
        "name": "Algoritmos y Programación II",
        "year": 1,
        "semester": 2,
        "area": "Computación",
        "correlativas": ["I101"],
        "skills": ["POO", "Estructuras de Datos Dinámicas", "Recursión", "Complejidad Algorítmica"],
        "hours": 96
    },
    {
        "code": "X105",
        "name": "Matemática B",
        "year": 1,
        "semester": 2,
        "area": "Matemática",
        "correlativas": ["X102"],
        "skills": ["Álgebra Lineal", "Matrices", "Vectores", "Espacios Vectoriales", "Transformaciones"],
        "hours": 96
    },
    {
        "code": "E106",
        "name": "Economía y Medición Económica",
        "year": 1,
        "semester": 2,
        "area": "Gestión & Negocios",
        "correlativas": ["X102", "E103"],
        "skills": ["Microeconomía", "Macroeconomía", "Indicadores Económicos", "Cuentas Nacionales"],
        "hours": 64
    },

    # --- AÑO 2 - SEMESTRE 1 ---
    {
        "code": "I201",
        "name": "Taller de Lenguajes",
        "year": 2,
        "semester": 1,
        "area": "Computación",
        "correlativas": ["I104"],
        "skills": ["Python Avanzado", "Git / GitHub", "APIs", "Entornos de Desarrollo"],
        "hours": 96
    },
    {
        "code": "I202",
        "name": "Introducción a Base de Datos",
        "year": 2,
        "semester": 1,
        "area": "Computación",
        "correlativas": ["I104"],
        "skills": ["Modelo Entidad-Relación", "SQL Básico", "Diseño Relacional", "Normalización"],
        "hours": 64
    },
    {
        "code": "E203",
        "name": "Contabilidad e Interpretación de Estados Contables",
        "year": 2,
        "semester": 1,
        "area": "Gestión & Negocios",
        "correlativas": ["E106"],
        "skills": ["Balances", "Estados de Resultados", "Ratios Financieros", "Auditoría Contable"],
        "hours": 64
    },
    {
        "code": "X204",
        "name": "Matemática C",
        "year": 2,
        "semester": 1,
        "area": "Matemática",
        "correlativas": ["X105"],
        "skills": ["Cálculo Multivariable", "Integrales Múltiples", "Series y Sucesiones", "Optimización"],
        "hours": 96
    },

    # --- AÑO 2 - SEMESTRE 2 ---
    {
        "code": "I205",
        "name": "Base de Datos",
        "year": 2,
        "semester": 2,
        "area": "Computación",
        "correlativas": ["I202"],
        "skills": ["SQL Avanzado", "NoSQL", "Indexación", "Transacciones y Concurrencia", "Data Warehousing"],
        "hours": 96
    },
    {
        "code": "E206",
        "name": "Procesos de Negocio",
        "year": 2,
        "semester": 2,
        "area": "Gestión & Negocios",
        "correlativas": ["E203"],
        "skills": ["BPMN", "Optimización de Procesos", "Flujos de Trabajo", "ERP / CRM"],
        "hours": 64
    },
    {
        "code": "X207",
        "name": "Matemática D",
        "year": 2,
        "semester": 2,
        "area": "Matemática",
        "correlativas": ["X204"],
        "skills": ["Probabilidad", "Estadística Inferencial", "Variables Aleatorias", "Modelado Estocástico"],
        "hours": 96
    },
    {
        "code": "O208",
        "name": "Inglés (Prueba Lecto-Comprensión y Traducción)",
        "year": 2,
        "semester": 2,
        "area": "General / Profesional",
        "correlativas": [],
        "skills": ["Comprensión Lectora Técnica", "Papers Científicos", "Documentación en Inglés"],
        "hours": 32
    },

    # --- AÑO 3 - SEMESTRE 1 ---
    {
        "code": "I301",
        "name": "Fundamentos de Arquitectura de Computadoras, SO y Redes",
        "year": 3,
        "semester": 1,
        "area": "Computación",
        "correlativas": ["I104", "O208"],
        "skills": ["Linux / Shell Scripting", "Procesos y Memoria", "Redes TCP/IP", "Cloud Computing Basics"],
        "hours": 96
    },
    {
        "code": "I302",
        "name": "Ingeniería de Software",
        "year": 3,
        "semester": 1,
        "area": "Computación",
        "correlativas": ["I201", "O208"],
        "skills": ["Metodologías Ágiles (Scrum/Kanban)", "Testing", "Arquitectura de Software", "CI/CD"],
        "hours": 96
    },
    {
        "code": "E303",
        "name": "Costos e Información Para la Gestión",
        "year": 3,
        "semester": 1,
        "area": "Gestión & Negocios",
        "correlativas": ["X105", "E203", "O208"],
        "skills": ["Costeo por Procesos", "Punto de Equilibrio", "Presupuestación", "Control de Gestión"],
        "hours": 64
    },
    {
        "code": "E304",
        "name": "Gestión de Personas y Equipos",
        "year": 3,
        "semester": 1,
        "area": "Gestión & Negocios",
        "correlativas": ["X105", "E203", "O208"],
        "skills": ["Liderazgo", "Gestión del Talento", "Dinámica de Equipos Ágiles", "Comunicación"],
        "hours": 64
    },

    # --- AÑO 3 - SEMESTRE 2 ---
    {
        "code": "I305",
        "name": "Visualización de Grandes Volúmenes de Datos",
        "year": 3,
        "semester": 2,
        "area": "Computación",
        "correlativas": ["X207", "O208"],
        "skills": ["PowerBI / Tableau", "D3.js / Plotly / Seaborn", "Storytelling con Datos", "Dashboards Ejecutivos"],
        "hours": 96
    },
    {
        "code": "I306",
        "name": "Minería de Datos y Aprendizaje Automático",
        "year": 3,
        "semester": 2,
        "area": "Computación",
        "correlativas": ["I201", "X207", "O208"],
        "skills": ["Scikit-Learn", "Modelos Supervisados/No Supervisados", "Clustering", "Evaluación de Modelos"],
        "hours": 96
    },
    {
        "code": "E307",
        "name": "Tecnologías Para la Gestión",
        "year": 3,
        "semester": 2,
        "area": "Gestión & Negocios",
        "correlativas": ["X204", "E206", "O208"],
        "skills": ["Sistemas de Información Empresarial", "Business Intelligence", "Automatización de Negocios"],
        "hours": 64
    },

    # --- AÑO 4 - SEMESTRE 1 ---
    {
        "code": "I401",
        "name": "Conceptos y Aplicaciones en Big Data",
        "year": 4,
        "semester": 1,
        "area": "Computación",
        "correlativas": ["I201", "X207", "O208"],
        "skills": ["Apache Spark", "Hadoop Ecosystem", "Pipelines de Datos Escalables", "Data Lakes"],
        "hours": 96
    },
    {
        "code": "E402",
        "name": "Finanzas de Empresas",
        "year": 4,
        "semester": 1,
        "area": "Gestión & Negocios",
        "correlativas": ["X207", "E303"],
        "skills": ["Valuación de Proyectos (VAN/TIR)", "Riesgo y Retorno", "Estructura de Capital", "Mercados Financieros"],
        "hours": 64
    },
    {
        "code": "E403",
        "name": "Estrategia de Tecnología y Gestión de Proyectos",
        "year": 4,
        "semester": 1,
        "area": "Gestión & Negocios",
        "correlativas": ["X207", "E307", "O208"],
        "skills": ["Gestión de Proyectos Tech", "Transformación Digital", "Roadmapping", "Gestión de Portafolios"],
        "hours": 64
    },
    {
        "code": "E404",
        "name": "Marketing Estratégico y Operativo",
        "year": 4,
        "semester": 1,
        "area": "Gestión & Negocios",
        "correlativas": ["E206", "X207", "O208", "E304"],
        "skills": ["Marketing Analytics", "Customer Lifetime Value", "Segmentación de Clientes", "Growth & Growth Hacking"],
        "hours": 64
    },

    # --- AÑO 4 - SEMESTRE 2 ---
    {
        "code": "I405",
        "name": "Aplicaciones de Inteligencia de Datos en Organizaciones",
        "year": 4,
        "semester": 2,
        "area": "Computación",
        "correlativas": ["I306"],
        "skills": ["Deep Learning", "Procesamiento de Lenguaje Natural (NLP)", "MLOps", "Modelos de Decisión en Negocios"],
        "hours": 96
    },
    {
        "code": "E406",
        "name": "Dirección General",
        "year": 4,
        "semester": 2,
        "area": "Gestión & Negocios",
        "correlativas": ["X207", "E303", "E304", "E307"],
        "skills": ["Estrategia Corporativa", "Gobierno Corporativo", "Modelos de Negocio", "Toma de Decisiones de Alta Dirección"],
        "hours": 64
    },
    {
        "code": "O408",
        "name": "Práctica Profesional Supervisada (PPS)",
        "year": 4,
        "semester": 2,
        "area": "General / Profesional",
        "correlativas": ["REQ_13_MATERIAS"],
        "skills": ["Experiencia Práctica", "Resolución de Problemas Reales", "Data Science Aplicado", "Informe Profesional"],
        "hours": 200
    }
]

CURRICULUM_BY_CODE = {subject["code"]: subject for subject in CURRICULUM}
