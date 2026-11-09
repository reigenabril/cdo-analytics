/* ============================================================
   CDO Analytics - aplicacion estatica
   Port de app.py / data_loader.py / analytics.py / simulator.py
   ============================================================ */
(function () {
  'use strict';

  var RAW = window.CDO_DATA || { areas: {}, curriculum: [], student: {}, history: {} };
  var AREAS = RAW.areas;
  var CURRICULUM = RAW.curriculum;
  var BY_CODE = {};
  CURRICULUM.forEach(function (s) { BY_CODE[s.code] = s; });

  var APPROVED_ORIGINS = ['Promoción', 'Examen', 'Actuación Provisoria', 'Equivalencia'];
  var STATUS_COLORS = {
    'Aprobada': '#10B981',
    'En Curso': '#D97706',
    'Regular': '#2563EB',
    'Habilitada': '#7C3AED',
    'Bloqueada': '#94A3B8'
  };
  var STATUS_CLASS = {
    'Aprobada': 'pill-aprobada',
    'En Curso': 'pill-encurso',
    'Regular': 'pill-regular',
    'Habilitada': 'pill-habilitada',
    'Bloqueada': 'pill-bloqueada'
  };
  var NAV = [
    ['dashboard', 'Dashboard de Rendimiento'],
    ['malla', 'Malla Curricular'],
    ['simulador', 'Simulador What-If'],
    ['planificador', 'Planificador de Graduacion'],
    ['competencias', 'Matriz de Competencias'],
    ['importar', 'Importar Archivos']
  ];

  var state = {
    page: 'dashboard',
    history: clone(RAW.history || {}),
    student: clone(RAW.student || {}),
    filters: { area: 'Todas', status: 'Todos', q: '' },
    simTab: 'meta',
    importLog: []
  };

  /* ---------- helpers ---------- */

  function clone(o) { return JSON.parse(JSON.stringify(o || {})); }

  function esc(v) {
    return String(v == null ? '' : v)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
  }

  function round(v, d) { var p = Math.pow(10, d); return Math.round(v * p + 1e-9) / p; }
  function fmt(v, d) { return (v === null || v === undefined || isNaN(v)) ? 'S/D' : Number(v).toFixed(d); }
  function pct(a, b) { return b ? (a / b) * 100 : 0; }

  function parseCode(name) {
    var m = String(name || '').match(/\(([A-Z]\d{3})\)/);
    return m ? m[1] : null;
  }

  function extractGrade(raw) {
    var m = String(raw == null ? '' : raw).trim().match(/^(\d+(\.\d+)?)/);
    return m ? parseFloat(m[1]) : null;
  }

  function cleanText(v) {
    return v === null || v === undefined ? '' : String(v).trim();
  }

  /* ---------- modelo ---------- */

  function computeSubjects(history) {
    var rec = {};
    Object.keys(history || {}).forEach(function (code) {
      var h = history[code] || {};
      var raw = h.raw_nota == null ? '' : String(h.raw_nota);
      var grade = (h.numeric_grade === null || h.numeric_grade === undefined || h.numeric_grade === '')
        ? extractGrade(raw)
        : Number(h.numeric_grade);
      rec[code] = {
        raw_nota: raw,
        origen: h.origen || '',
        numeric_grade: (grade === null || isNaN(grade)) ? null : grade
      };
    });

    var approved = {}, regular = {}, inCourse = {};
    CURRICULUM.forEach(function (item) {
      var r = rec[item.code];
      if (!r) return;
      if (APPROVED_ORIGINS.indexOf(r.origen) !== -1) approved[item.code] = true;
      else if (r.origen === 'Regularidad') regular[item.code] = true;
      else if (r.origen === 'En Curso') inCourse[item.code] = true;
    });

    var approvedCount = Object.keys(approved).length;

    return CURRICULUM.map(function (item) {
      var r = rec[item.code] || { raw_nota: '', origen: '', numeric_grade: null };
      var status;
      if (approved[item.code]) status = 'Aprobada';
      else if (regular[item.code]) status = 'Regular';
      else if (inCourse[item.code]) status = 'En Curso';
      else {
        var reqs = item.correlativas || [];
        var met = true;
        if (reqs.indexOf('REQ_13_MATERIAS') !== -1) {
          met = approvedCount >= 13;
        } else {
          for (var i = 0; i < reqs.length; i++) {
            if (!approved[reqs[i]] && !regular[reqs[i]]) { met = false; break; }
          }
        }
        status = met ? 'Habilitada' : 'Bloqueada';
      }
      return {
        code: item.code,
        name: item.name,
        year: item.year,
        semester: item.semester,
        area: item.area,
        hours: item.hours,
        skills: item.skills || [],
        correlativas: item.correlativas || [],
        status: status,
        origen: r.origen || 'Pendiente',
        raw_nota: r.raw_nota,
        numeric_grade: r.numeric_grade
      };
    });
  }

  function computeKpis(subjects) {
    var graded = subjects.filter(function (s) { return s.numeric_grade !== null; });
    var totalSubjects = subjects.length;
    var sum = graded.reduce(function (a, s) { return a + s.numeric_grade; }, 0);
    var gpa = graded.length ? sum / graded.length : 0;

    var counts = {};
    subjects.forEach(function (s) { counts[s.status] = (counts[s.status] || 0) + 1; });

    var totalHours = subjects.reduce(function (a, s) { return a + s.hours; }, 0);
    var doneHours = subjects.filter(function (s) { return s.status === 'Aprobada'; })
      .reduce(function (a, s) { return a + s.hours; }, 0);

    var areaStats = {};
    Object.keys(AREAS).forEach(function (area) {
      var inArea = subjects.filter(function (s) { return s.area === area; });
      var gradedArea = inArea.filter(function (s) { return s.numeric_grade !== null; });
      var approvedArea = inArea.filter(function (s) { return s.status === 'Aprobada'; });
      var mean = gradedArea.length
        ? gradedArea.reduce(function (a, s) { return a + s.numeric_grade; }, 0) / gradedArea.length
        : null;
      areaStats[area] = {
        mean_grade: mean,
        approved_count: approvedArea.length,
        total_count: inArea.length,
        pct_progress: pct(approvedArea.length, inArea.length)
      };
    });

    return {
      gpa: round(gpa, 2),
      total_subjects: totalSubjects,
      aprobadas: counts['Aprobada'] || 0,
      en_curso: counts['En Curso'] || 0,
      regulares: counts['Regular'] || 0,
      habilitadas: counts['Habilitada'] || 0,
      bloqueadas: counts['Bloqueada'] || 0,
      pct_aprobado: round(pct(counts['Aprobada'] || 0, totalSubjects), 1),
      pct_en_proceso: round(pct((counts['Aprobada'] || 0) + (counts['En Curso'] || 0) + (counts['Regular'] || 0), totalSubjects), 1),
      total_hours: totalHours,
      completed_hours: doneHours,
      pct_hours: round(pct(doneHours, totalHours), 1),
      area_stats: areaStats,
      graded_count: graded.length
    };
  }

  /* ---------- simulador ---------- */

  function targetGpa(subjects, target) {
    var graded = subjects.filter(function (s) { return s.numeric_grade !== null; });
    var pending = subjects.filter(function (s) { return s.numeric_grade === null; });
    var curCount = graded.length;
    var curSum = graded.reduce(function (a, s) { return a + s.numeric_grade; }, 0);
    var gpa = curCount ? curSum / curCount : 0;

    if (!pending.length) {
      return { possible: true, current_gpa: round(gpa, 2), required_avg: round(gpa, 2), pending_count: 0 };
    }
    var total = curCount + pending.length;
    var needed = (target * total - curSum) / pending.length;
    return {
      possible: needed >= 4 && needed <= 10,
      current_gpa: round(gpa, 2),
      target_gpa: round(target, 2),
      required_avg: round(needed, 2),
      current_count: curCount,
      pending_count: pending.length,
      total_count: total
    };
  }

  function simulateGpa(subjects, grades) {
    var graded = subjects.filter(function (s) { return s.numeric_grade !== null; });
    var real = graded.map(function (s) { return s.numeric_grade; });
    var sim = Object.keys(grades).map(function (k) { return grades[k]; })
      .filter(function (g) { return g !== null && g !== '' && !isNaN(g); })
      .map(Number);

    var all = real.concat(sim);
    var projected = all.length ? all.reduce(function (a, b) { return a + b; }, 0) / all.length : 0;
    var current = real.length ? real.reduce(function (a, b) { return a + b; }, 0) / real.length : 0;

    return {
      current_gpa: round(current, 2),
      projected_gpa: round(projected, 2),
      diff: round(projected - current, 2),
      simulated_count: sim.length,
      total_evaluated: all.length
    };
  }

  function maxAttainable(res) {
    if (!res.pending_count) return res.current_gpa;
    return round((res.current_gpa * res.current_count + 10 * res.pending_count) / res.total_count, 2);
  }

  /* ---------- planificador ---------- */

  function currentTermStart() {
    var now = new Date();
    var m = now.getMonth() + 1;
    var y = now.getFullYear();
    if (m >= 3 && m <= 7) return { year: y, term: 1 };
    if (m >= 8) return { year: y, term: 2 };
    return { year: y - 1, term: 2 };
  }

  function canTake(code, approvedSet) {
    var reqs = (BY_CODE[code] && BY_CODE[code].correlativas) || [];
    if (reqs.indexOf('REQ_13_MATERIAS') !== -1) return approvedSet.size >= 13;
    for (var i = 0; i < reqs.length; i++) {
      if (!approvedSet.has(reqs[i])) return false;
    }
    return true;
  }

  function graduationRoadmap(subjects, maxPerTerm) {
    var approved = new Set();
    var inProgress = [];
    subjects.forEach(function (s) {
      if (s.status === 'Aprobada') approved.add(s.code);
      else if (s.status === 'En Curso' || s.status === 'Regular') inProgress.push(s.code);
    });

    var pending = subjects.filter(function (s) { return s.status !== 'Aprobada'; })
      .map(function (s) { return s.code; });

    var roadmap = [];
    var start = currentTermStart();
    var year = start.year;
    var term = start.term;
    var simApproved = new Set(approved);

    function advance() {
      if (term === 1) { term = 2; } else { term = 1; year += 1; }
    }

    if (inProgress.length) {
      roadmap.push({
        term_name: year + ' - ' + term + '° Cuatrimestre (Actual)',
        year: year, term: term,
        subjects: inProgress.map(function (c) { return BY_CODE[c]; }).filter(Boolean),
        is_current: true
      });
      inProgress.forEach(function (c) {
        simApproved.add(c);
        var i = pending.indexOf(c);
        if (i !== -1) pending.splice(i, 1);
      });
      advance();
    }

    var guard = 0;
    while (pending.length && guard < 15) {
      guard += 1;
      var available = pending.filter(function (c) { return canTake(c, simApproved); });
      if (!available.length) break;

      available.sort(function (a, b) {
        return (BY_CODE[a].year - BY_CODE[b].year) || (BY_CODE[a].semester - BY_CODE[b].semester);
      });
      var chosen = available.slice(0, maxPerTerm);

      roadmap.push({
        term_name: year + ' - ' + term + '° Cuatrimestre',
        year: year, term: term,
        subjects: chosen.map(function (c) { return BY_CODE[c]; }),
        is_current: false
      });

      chosen.forEach(function (c) {
        simApproved.add(c);
        var i = pending.indexOf(c);
        if (i !== -1) pending.splice(i, 1);
      });
      advance();
    }

    return {
      roadmap: roadmap,
      estimated_graduation: roadmap.length ? roadmap[roadmap.length - 1].term_name : 'Graduado',
      remaining_terms: roadmap.filter(function (r) { return !r.is_current; }).length,
      leftover: pending.length
    };
  }

  /* ---------- graficos ---------- */

  var PLOT_FONT = { family: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif', size: 12, color: '#475569' };
  var PLOT_LAYOUT = {
    paper_bgcolor: 'rgba(0,0,0,0)',
    plot_bgcolor: 'rgba(0,0,0,0)',
    font: PLOT_FONT,
    margin: { l: 48, r: 16, t: 18, b: 44 },
    hoverlabel: { bgcolor: '#0F172A', font: { color: '#fff', size: 12 } }
  };
  var PLOT_CONFIG = { displayModeBar: false, responsive: true };

  function plot(el, traces, layout) {
    if (!el || !window.Plotly) return false;
    var merged = Object.assign({}, PLOT_LAYOUT, layout || {});
    window.Plotly.newPlot(el, traces, merged, PLOT_CONFIG);
    return true;
  }

  function gradesChart(subjects) {
    var graded = subjects.filter(function (s) { return s.numeric_grade !== null; })
      .sort(function (a, b) { return a.code.localeCompare(b.code); });
    var mean = graded.reduce(function (a, s) { return a + s.numeric_grade; }, 0) / (graded.length || 1);

    var traces = Object.keys(AREAS).map(function (area) {
      var pts = graded.filter(function (s) { return s.area === area; });
      return {
        type: 'bar',
        name: area,
        x: pts.map(function (s) { return s.code; }),
        y: pts.map(function (s) { return s.numeric_grade; }),
        marker: { color: AREAS[area].color, line: { width: 0 } },
        text: pts.map(function (s) { return fmt(s.numeric_grade, 0); }),
        textposition: 'outside',
        textfont: { size: 11, color: '#334155' },
        customdata: pts.map(function (s) { return [s.name, s.origen, s.raw_nota]; }),
        hovertemplate: '<b>%{x}</b> - %{customdata[0]}<br>Nota: %{y} · %{customdata[1]}<extra></extra>'
      };
    }).filter(function (t) { return t.x.length; });

    var narrow = window.innerWidth < 700;

    return {
      traces: traces,
      layout: {
        height: narrow ? 460 : 400,
        barmode: 'group',
        bargap: 0.45,
        showlegend: true,
        margin: narrow
          ? { l: 42, r: 12, t: 10, b: 104 }
          : { l: 48, r: 16, t: 18, b: 44 },
        legend: narrow
          ? { orientation: 'h', y: -0.42, x: 0, font: { size: 10 } }
          : { orientation: 'h', y: 1.12, x: 0, font: { size: 11 } },
        xaxis: { title: { text: 'Codigo de materia', font: { size: 11 } }, tickfont: { size: 10 }, gridcolor: '#F1F5F9' },
        yaxis: { title: { text: 'Nota', font: { size: 11 } }, range: [0, 11], dtick: 1, gridcolor: '#EEF2F7' },
        shapes: [{
          type: 'line', xref: 'paper', x0: 0, x1: 1,
          y0: mean, y1: mean,
          line: { color: '#E11D48', width: 1.5, dash: 'dash' }
        }],
        annotations: [{
          xref: 'paper', x: 1, y: mean, xanchor: 'right', yanchor: 'bottom',
          text: 'Promedio ' + mean.toFixed(2), showarrow: false,
          font: { size: 10, color: '#E11D48' }, bgcolor: 'rgba(255,255,255,.85)'
        }]
      }
    };
  }

  var AREA_SHORT = {
    'Computación': 'Computo',
    'Matemática': 'Matemática',
    'Gestión & Negocios': 'Negocios',
    'General / Profesional': 'General'
  };

  function radarChart(kpis) {
    var cats = Object.keys(AREAS);
    var progress = cats.map(function (a) { return round(kpis.area_stats[a].pct_progress, 1); });
    var performance = cats.map(function (a) {
      var m = kpis.area_stats[a].mean_grade;
      return m ? round(m * 10, 1) : 0;
    });

    var close = function (arr) { return arr.concat([arr[0]]); };
    var labels = cats.map(function (a) { return AREA_SHORT[a] || a; });
    var closedCats = close(labels);
    cats = labels;

    return {
      traces: [
        {
          type: 'scatterpolar', r: close(progress), theta: closedCats, fill: 'toself',
          name: '% Avance en creditos',
          line: { color: '#2563EB', width: 2 }, fillcolor: 'rgba(37,99,235,.18)'
        },
        {
          type: 'scatterpolar', r: close(performance), theta: closedCats, fill: 'toself',
          name: 'Rendimiento /100',
          line: { color: '#10B981', width: 2 }, fillcolor: 'rgba(16,185,129,.15)'
        }
      ],
      layout: {
        height: 400,
        polar: {
          domain: { x: [0.16, 0.84], y: [0.12, 0.92] },
          radialaxis: { visible: true, range: [0, 100], showticklabels: false, ticks: '', gridcolor: '#E9EEF5' },
          angularaxis: { tickfont: { size: 11 }, gridcolor: '#E9EEF5' },
          bgcolor: 'rgba(0,0,0,0)'
        },
        legend: { orientation: 'h', y: -0.1, x: 0.5, xanchor: 'center', font: { size: 11 } },
        margin: { l: 24, r: 24, t: 12, b: 44 }
      }
    };
  }

  function yearChart(subjects) {
    var years = [1, 2, 3, 4];
    var aprob = [], enCurso = [], pend = [];
    years.forEach(function (y) {
      var inYear = subjects.filter(function (s) { return s.year === y; });
      var a = inYear.filter(function (s) { return s.status === 'Aprobada'; }).length;
      var e = inYear.filter(function (s) { return s.status === 'En Curso' || s.status === 'Regular'; }).length;
      aprob.push(a); enCurso.push(e); pend.push(inYear.length - a - e);
    });
    var labels = years.map(function (y) { return y + '° Anio'; });

    return {
      traces: [
        { type: 'bar', name: 'Aprobadas', x: labels, y: aprob, marker: { color: '#10B981' }, hovertemplate: '%{x}: %{y}<extra>Aprobadas</extra>' },
        { type: 'bar', name: 'En curso / Regular', x: labels, y: enCurso, marker: { color: '#F59E0B' }, hovertemplate: '%{x}: %{y}<extra>En curso</extra>' },
        { type: 'bar', name: 'Pendientes', x: labels, y: pend, marker: { color: '#CBD5E1' }, hovertemplate: '%{x}: %{y}<extra>Pendientes</extra>' }
      ],
      layout: {
        height: 360,
        barmode: 'stack',
        bargap: 0.5,
        legend: { orientation: 'h', y: 1.14, x: 0, font: { size: 11 } },
        xaxis: { tickfont: { size: 11 }, gridcolor: '#F1F5F9' },
        yaxis: { title: { text: 'Materias', font: { size: 11 } }, dtick: 1, gridcolor: '#EEF2F7' }
      }
    };
  }

  /* ---------- vistas ---------- */

  function pageHead(title, subtitle, chip) {
    return '<div class="page-head"><div><h2>' + esc(title) + '</h2><p>' + subtitle + '</p></div>' +
      (chip ? '<span class="head-chip">' + esc(chip) + '</span>' : '') + '</div>';
  }

  function chartCard(id, title, sub, cls) {
    return '<div class="card"><h3>' + title + (sub ? '<small>' + sub + '</small>' : '') + '</h3>' +
      '<div class="chart ' + (cls || '') + '" id="' + id + '"></div>' +
      '<p class="skill-empty" id="' + id + '-fallback" hidden>Los graficos necesitan conexion para cargar Plotly.</p></div>';
  }

  function viewDashboard(subjects, k) {
    var h = pageHead('Dashboard academico',
      esc(state.student.name || '') + ' &middot; ' + esc(state.student.degree || ''),
      state.student.plan || 'Plan 2024');

    var kpis = [
      { v: fmt(k.gpa, 2), l: 'Promedio general', c: '#2563EB', s: k.graded_count + ' materias con nota' },
      { v: k.pct_aprobado + '<span>%</span>', l: 'Aprobadas', c: '#10B981', s: k.aprobadas + ' de ' + k.total_subjects },
      { v: k.en_curso, l: 'En curso', c: '#D97706', s: k.regulares + ' regulares' },
      { v: k.habilitadas, l: 'Habilitadas', c: '#7C3AED', s: k.bloqueadas + ' bloqueadas' },
      { v: k.completed_hours + '<span> h</span>', l: 'Horas completadas', c: '#0284C7', s: k.pct_hours + '% de ' + k.total_hours }
    ];

    var grid = kpis.map(function (x) {
      return '<div class="kpi" style="--kpi-color:' + x.c + '">' +
        '<div class="kpi-value">' + x.v + '</div>' +
        '<div class="kpi-label">' + x.l + '</div>' +
        '<div class="kpi-sub">' + x.s + '</div></div>';
    }).join('');

    var areaRows = Object.keys(AREAS).map(function (area) {
      var st = k.area_stats[area];
      var color = AREAS[area].color;
      return '<div class="area-row" style="--area-color:' + color + '">' +
        '<div class="area-main"><div class="area-name">' + esc(area) + '</div>' +
        '<div class="area-meta">' + st.approved_count + ' de ' + st.total_count + ' materias</div>' +
        '<div class="bar"><i style="width:' + round(st.pct_progress, 1) + '%"></i></div></div>' +
        '<div class="area-grade">' + (st.mean_grade === null ? 'S/D' : fmt(st.mean_grade, 2)) +
        '<small>promedio</small></div></div>';
    }).join('');

    return h +
      '<div class="kpi-grid">' + grid + '</div>' +
      '<div class="grid-2">' +
        chartCard('chart-grades', 'Calificaciones por asignatura', k.graded_count + ' notas registradas', 'tall') +
        chartCard('chart-radar', 'Balance por area tematica', 'avance vs. rendimiento') +
      '</div>' +
      '<div class="grid-2-even">' +
        chartCard('chart-years', 'Avance por anio', '') +
        '<div class="card"><h3>Resumen por area</h3>' + areaRows + '</div>' +
      '</div>';
  }

  function viewMalla(subjects) {
    var h = pageHead('Malla curricular', 'Plan de 4 anios, correlatividades y estado de cada materia.', '28 materias');
    var f = state.filters;

    var optionsArea = ['Todas'].concat(Object.keys(AREAS)).map(function (a) {
      return '<option' + (a === f.area ? ' selected' : '') + '>' + esc(a) + '</option>';
    }).join('');
    var statuses = ['Todos', 'Aprobada', 'En Curso', 'Regular', 'Habilitada', 'Bloqueada'];
    var optionsStatus = statuses.map(function (s) {
      return '<option' + (s === f.status ? ' selected' : '') + '>' + esc(s) + '</option>';
    }).join('');

    var filtered = subjects.filter(function (s) {
      if (f.area !== 'Todas' && s.area !== f.area) return false;
      if (f.status !== 'Todos' && s.status !== f.status) return false;
      if (f.q) {
        var q = f.q.toLowerCase();
        if (s.name.toLowerCase().indexOf(q) === -1 && s.code.toLowerCase().indexOf(q) === -1) return false;
      }
      return true;
    });

    var controls = '<div class="filters">' +
      '<div class="field"><label for="f-area">Area</label><select id="f-area">' + optionsArea + '</select></div>' +
      '<div class="field"><label for="f-status">Estado</label><select id="f-status">' + optionsStatus + '</select></div>' +
      '<div class="field"><label for="f-q">Buscar materia o codigo</label><input id="f-q" type="text" placeholder="Ej.: base de datos, I202" value="' + esc(f.q) + '"></div>' +
      '</div>';

    if (!filtered.length) {
      return h + controls + '<div class="note warn">Ninguna materia coincide con los filtros aplicados.</div>';
    }

    var blocks = [1, 2, 3, 4].map(function (year) {
      var inYear = filtered.filter(function (s) { return s.year === year; });
      if (!inYear.length) return '';
      var approvedYear = inYear.filter(function (s) { return s.status === 'Aprobada'; }).length;

      var sem = [1, 2].map(function (semN) {
        var list = inYear.filter(function (s) { return s.semester === semN; });
        var body = list.length
          ? list.map(subjectCard).join('')
          : '<p class="skill-empty">Sin materias.</p>';
        return '<div class="sem-col"><div class="sem-title"><span>' + semN + '° semestre</span><span>' + list.length + '</span></div>' + body + '</div>';
      }).join('');

      return '<div class="year-block"><div class="year-head"><h3>' + year + '° anio</h3>' +
        '<span>' + approvedYear + '/' + inYear.length + ' aprobadas</span></div>' +
        '<div class="semesters">' + sem + '</div></div>';
    }).join('');

    return h + controls + blocks;
  }

  function subjectCard(s) {
    var color = STATUS_COLORS[s.status] || '#94A3B8';
    var corr = s.correlativas.indexOf('REQ_13_MATERIAS') !== -1
      ? '13 materias aprobadas'
      : (s.correlativas.length ? s.correlativas.join(', ') : 'Ninguna');
    var tags = s.skills.map(function (t) { return '<span class="tag">' + esc(t) + '</span>'; }).join('');
    var grade = s.numeric_grade !== null ? fmt(s.numeric_grade, 0) : (s.raw_nota ? esc(s.raw_nota) : '');

    return '<details class="subject" style="--status-color:' + color + '">' +
      '<summary><span class="s-code">' + esc(s.code) + '</span>' +
      '<span class="s-name">' + esc(s.name) + '</span>' +
      (grade ? '<span class="s-grade">' + grade + '</span>' : '') +
      '<span class="pill ' + (STATUS_CLASS[s.status] || 'pill-bloqueada') + '">' + esc(s.status) + '</span>' +
      '</summary>' +
      '<div class="subject-body"><dl>' +
      '<dt>Area</dt><dd>' + esc(s.area) + '</dd>' +
      '<dt>Origen</dt><dd>' + esc(s.origen) + '</dd>' +
      '<dt>Carga horaria</dt><dd>' + s.hours + ' hs</dd>' +
      '<dt>Correlativas</dt><dd>' + esc(corr) + '</dd>' +
      '</dl><div class="tags">' + tags + '</div></div></details>';
  }

  function viewSimulador(subjects, k) {
    var h = pageHead('Simulador de promedio', 'Proyecciones de calificaciones y metas de rendimiento.', 'What-If');

    var tabs = '<div class="tabs" role="tablist">' +
      '<button role="tab" data-tab="meta" aria-selected="' + (state.simTab === 'meta') + '">Meta de promedio</button>' +
      '<button role="tab" data-tab="individual" aria-selected="' + (state.simTab === 'individual') + '">Simulacion individual</button>' +
      '</div>';

    if (state.simTab === 'meta') {
      var res = targetGpa(subjects, 8.5);
      var msg;
      if (res.pending_count === 0) {
        msg = '<div class="note ok">Ya no quedan materias sin nota: el promedio esta cerrado.</div>';
      } else if (res.possible) {
        msg = '<div class="note">Necesitas un promedio de <strong>' + res.required_avg.toFixed(2) +
          '</strong> en las ' + res.pending_count + ' materias pendientes para graduarte con ' + res.target_gpa.toFixed(2) + '.</div>';
      } else if (res.required_avg > 10) {
        msg = '<div class="note warn">La meta requiere un promedio mayor a 10 (' + res.required_avg.toFixed(2) +
          '). El maximo posible con las notas actuales es ' +
          fmt((res.current_gpa * res.current_count + 10 * res.pending_count) / res.total_count, 2) + '.</div>';
      } else {
        msg = '<div class="note ok">Tu promedio actual (' + res.current_gpa.toFixed(2) + ') ya supera la meta.</div>';
      }

      return h + tabs +
        '<div class="card"><h3>Promedio objetivo de graduacion<small>' + res.current_count + ' notas cargadas · ' + res.pending_count + ' pendientes</small></h3>' +
        '<div class="slider-row"><input type="range" id="target-range" min="6" max="10" step="0.1" value="8.5" aria-label="Promedio objetivo">' +
        '<output class="slider-value" id="target-out">8.5</output></div>' +
        '<div class="metric-row">' +
        '<div class="metric"><div class="m-label">Promedio actual</div><div class="m-value" id="t-cur">' + res.current_gpa.toFixed(2) + '</div></div>' +
        '<div class="metric"><div class="m-label">Meta</div><div class="m-value" id="t-target">8.50</div></div>' +
        '<div class="metric"><div class="m-label">Necesario en pendientes</div><div class="m-value" id="t-req">' + res.required_avg.toFixed(2) + '</div></div>' +
        '<div class="metric"><div class="m-label">Maximo posible</div><div class="m-value" id="t-max">' + maxAttainable(res).toFixed(2) + '</div></div>' +
        '</div><div id="t-msg">' + msg + '</div></div>';
    }

    var pending = subjects.filter(function (s) { return s.numeric_grade === null; });
    var inputs = pending.map(function (s) {
      return '<label class="num-field"><span class="nf-name">' + esc(s.name) +
        '<span class="nf-code">' + esc(s.code) + '</span></span>' +
        '<input type="number" min="4" max="10" step="1" value="8" data-sim-code="' + esc(s.code) + '"></label>';
    }).join('');

    var sim = simulateGpa(subjects, {});
    return h + tabs +
      '<div class="card"><h3>Notas tentativas en materias pendientes<small>' + pending.length + ' materias sin nota</small></h3>' +
      '<div class="num-grid">' + inputs + '</div>' +
      '<div class="metric-row">' +
      '<div class="metric"><div class="m-label">Promedio actual</div><div class="m-value" id="s-cur">' + sim.current_gpa.toFixed(2) + '</div></div>' +
      '<div class="metric"><div class="m-label">Promedio proyectado</div><div class="m-value" id="s-proj">' + sim.projected_gpa.toFixed(2) + '</div><div class="m-delta" id="s-delta"></div></div>' +
      '<div class="metric"><div class="m-label">Materias evaluadas</div><div class="m-value" id="s-count">' + sim.total_evaluated + '</div></div>' +
      '</div><div class="note" id="s-note">Ajusta las notas para ver el promedio proyectado al completar la carrera.</div></div>';
  }

  function viewPlanner(subjects) {
    var h = pageHead('Planificador de cursada', 'Secuencia sugerida de cuatrimestres segun correlatividades.', 'Roadmap');

    var plan = graduationRoadmap(subjects, 3);
    var chips = plan.roadmap.map(function (t) {
      var cards = t.subjects.map(function (s) {
        var color = AREAS[s.area] ? AREAS[s.area].color : '#2563EB';
        return '<div class="subject-card" style="--area-color:' + color + '">' +
          '<div class="sc-code">' + esc(s.code) + '</div>' +
          '<div class="sc-name">' + esc(s.name) + '</div>' +
          '<div class="sc-area">' + esc(s.area) + '</div></div>';
      }).join('');
      return '<div class="term' + (t.is_current ? ' is-current' : '') + '">' +
        '<div class="term-head">' + esc(t.term_name) +
        (t.is_current ? '<span class="term-badge">En curso</span>' : '') +
        '<span style="margin-left:auto;font-weight:500;font-size:11px;color:#64748B">' + t.subjects.length + ' materias</span>' +
        '</div><div class="term-body">' + cards + '</div></div>';
    }).join('');

    var leftover = plan.leftover
      ? '<div class="note warn">Quedan ' + plan.leftover + ' materias sin ubicar: revisa correlatividades o sube el ritmo.</div>'
      : '';

    return h +
      '<div class="card"><h3>Ritmo de cursada<small>materias por cuatrimestre</small></h3>' +
      '<div class="slider-row"><input type="range" id="pace-range" min="1" max="4" step="1" value="3" aria-label="Materias por cuatrimestre">' +
      '<output class="slider-value" id="pace-out">3</output></div>' +
      '<p class="skill-empty" style="margin-top:8px">Graduacion estimada: <strong id="grad-est">' + esc(plan.estimated_graduation) + '</strong> · ' +
      '<span id="grad-terms">' + plan.remaining_terms + '</span> cuatrimestres desde el actual.</p></div>' +
      '<div id="roadmap">' + chips + '</div>' + leftover;
  }

  function viewCompetencias(subjects) {
    var h = pageHead('Matriz de competencias', 'Habilidades tecnicas y metodologicas adquiridas segun materias aprobadas o en curso.', 'Skills');
    var active = subjects.filter(function (s) { return s.status === 'Aprobada' || s.status === 'En Curso'; });

    function collect(area) {
      var set = new Set();
      active.filter(function (s) { return s.area === area; })
        .forEach(function (s) { s.skills.forEach(function (t) { set.add(t); }); });
      return Array.from(set).sort(function (a, b) { return a.localeCompare(b); });
    }

    var groups = [
      ['Computación', 'Computacion y datos'],
      ['Gestión & Negocios', 'Negocios y gestion'],
      ['Matemática', 'Metodos cuantitativos']
    ];

    var cols = groups.map(function (g) {
      var skills = collect(g[0]);
      var body = skills.length
        ? '<div class="skill-list">' + skills.map(function (s) { return '<span class="skill-chip">' + esc(s) + '</span>'; }).join('') + '</div>'
        : '<p class="skill-empty">Sin materias aprobadas en esta area.</p>';
      return '<div class="card" style="--area-color:' + (AREAS[g[0]] ? AREAS[g[0]].color : '#2563EB') + '">' +
        '<h4>' + esc(g[1]) + '</h4><p class="skill-empty" style="margin:4px 0 10px">' + esc(AREAS[g[0]] ? AREAS[g[0]].desc : '') + '</p>' + body + '</div>';
    }).join('');

    var totalSkills = new Set();
    active.forEach(function (s) { s.skills.forEach(function (t) { totalSkills.add(t); }); });

    return h + '<div class="skills-grid">' + cols + '</div>' +
      '<p class="foot" style="border:0;margin-top:14px">' + totalSkills.size +
      ' competencias detectadas en ' + active.length + ' materias aprobadas o en curso.</p>';
  }

  function viewImportar(subjects, k) {
    var h = pageHead('Importar archivos', 'Carga el plan de estudios o la actuacion provisoria del SIU Guarani. Todo se procesa en tu navegador.', 'Local');

    var log = state.importLog.length
      ? '<div class="import-log">' + esc(state.importLog.join('\n')) + '</div>'
      : '';

    return h +
      '<div class="card"><h3>Subir archivos<small>.xlsx / .xls / .json</small></h3>' +
      '<div class="dropzone" id="dropzone">' +
      '<p style="margin:0 0 10px;font-weight:600;color:#0F172A">Arrastra los archivos aca</p>' +
      '<button class="btn" id="pick-btn" type="button">Elegir archivos</button>' +
      '<p>Uno o dos Excel del SIU (plan + actuacion) o un academic_data.json.</p>' +
      '<input type="file" id="file-input" accept=".xlsx,.xls,.json" multiple>' +
      '</div>' + log +
      '<div class="metric-row" style="margin-top:16px">' +
      '<div class="metric"><div class="m-label">Registros cargados</div><div class="m-value">' + Object.keys(state.history).length + '</div></div>' +
      '<div class="metric"><div class="m-label">Aprobadas</div><div class="m-value">' + k.aprobadas + ' / ' + k.total_subjects + '</div></div>' +
      '<div class="metric"><div class="m-label">Promedio</div><div class="m-value">' + fmt(k.gpa, 2) + '</div></div>' +
      '</div>' +
      '<button class="btn ghost" id="reset-btn" type="button">Restablecer datos originales</button>' +
      '</div>' +
      '<div class="card" style="margin-top:16px"><h3>Formatos aceptados<small>los archivos no salen de tu equipo</small></h3>' +
      '<div class="format-grid">' +
      '<div><h5>plan_estudios.xls</h5><p>Reporte del SIU con la tabla <em>Actividad</em>. Se leen codigo, nota y origen (Promocion, Examen, Equivalencia, Regularidad).</p></div>' +
      '<div><h5>actuacion_provisoria.xls</h5><p>Opcional. Columnas Actividad, Nota y Resultado; se cruza por nombre con la malla.</p></div>' +
      '<div><h5>academic_data.json</h5><p>Formato del repositorio: <code>{ student_info, academic_history }</code>. Es el que usa el sitio por defecto.</p></div>' +
      '</div><p class="skill-empty" style="margin-top:12px">Los Excel se procesan con SheetJS desde CDN, por lo que la primera carga necesita conexion.</p></div>';
  }

  var VIEWS = {
    dashboard: viewDashboard,
    malla: viewMalla,
    simulador: viewSimulador,
    planificador: viewPlanner,
    competencias: viewCompetencias,
    importar: viewImportar
  };

  /* ---------- montaje / eventos ---------- */

  function render() {
    var subjects = computeSubjects(state.history);
    var k = computeKpis(subjects);
    var view = document.getElementById('view');
    view.innerHTML = VIEWS[state.page](subjects, k);

    if (state.page === 'dashboard') {
      var g = gradesChart(subjects);
      plot(document.getElementById('chart-grades'), g.traces, g.layout);
      var r = radarChart(k);
      plot(document.getElementById('chart-radar'), r.traces, r.layout);
      var y = yearChart(subjects);
      plot(document.getElementById('chart-years'), y.traces, y.layout);
    }

    if (state.page === 'malla') {
      document.getElementById('f-area').addEventListener('change', function (e) {
        state.filters.area = e.target.value; render();
      });
      document.getElementById('f-status').addEventListener('change', function (e) {
        state.filters.status = e.target.value; render();
      });
      var q = document.getElementById('f-q');
      q.addEventListener('input', debounce(function (e) {
        state.filters.q = e.target.value;
        var pos = e.target.selectionStart;
        render();
        var nq = document.getElementById('f-q');
        if (nq) { nq.focus(); nq.setSelectionRange(pos, pos); }
      }, 220));
    }

    if (state.page === 'simulador') {
      document.querySelectorAll('.tabs button').forEach(function (b) {
        b.addEventListener('click', function () {
          state.simTab = b.getAttribute('data-tab'); render();
        });
      });

      if (state.simTab === 'meta') {
        var range = document.getElementById('target-range');
        range.addEventListener('input', function () {
          var target = parseFloat(range.value);
          var res = targetGpa(subjects, target);
          document.getElementById('target-out').textContent = target.toFixed(1);
          document.getElementById('t-cur').textContent = res.current_gpa.toFixed(2);
          document.getElementById('t-target').textContent = target.toFixed(2);
          document.getElementById('t-req').textContent = res.required_avg.toFixed(2);
          document.getElementById('t-max').textContent = maxAttainable(res).toFixed(2);

          var msg;
          if (res.pending_count === 0) {
            msg = '<div class="note ok">Ya no quedan materias sin nota.</div>';
          } else if (res.possible) {
            msg = '<div class="note">Necesitas <strong>' + res.required_avg.toFixed(2) + '</strong> en las ' + res.pending_count +
              ' pendientes para graduarte con ' + target.toFixed(2) + '.</div>';
          } else if (res.required_avg > 10) {
            var maxGpa = (res.current_gpa * res.current_count + 10 * res.pending_count) / res.total_count;
            msg = '<div class="note warn">Imposible: requeriria ' + res.required_avg.toFixed(2) + '. Maximo alcanzable: ' + maxGpa.toFixed(2) + '.</div>';
          } else {
            msg = '<div class="note ok">Tu promedio actual (' + res.current_gpa.toFixed(2) + ') ya supera la meta.</div>';
          }
          document.getElementById('t-msg').innerHTML = msg;
        });
      }

      if (state.simTab === 'individual') {
        var inputs = document.querySelectorAll('input[data-sim-code]');
        var recalc = function () {
          var grades = {};
          inputs.forEach(function (i) {
            var v = parseFloat(i.value);
            if (!isNaN(v)) grades[i.getAttribute('data-sim-code')] = Math.min(10, Math.max(4, v));
          });
          var sim = simulateGpa(subjects, grades);
          document.getElementById('s-cur').textContent = sim.current_gpa.toFixed(2);
          document.getElementById('s-proj').textContent = sim.projected_gpa.toFixed(2);
          var delta = document.getElementById('s-delta');
          delta.textContent = (sim.diff >= 0 ? '+' : '') + sim.diff.toFixed(2);
          delta.className = 'm-delta ' + (sim.diff >= 0 ? 'delta-up' : 'delta-down');
          document.getElementById('s-count').textContent = sim.total_evaluated;
          document.getElementById('s-note').textContent =
            'Promedio proyectado con ' + sim.total_evaluated + ' materias (' + sim.simulated_count + ' simuladas).';
        };
        inputs.forEach(function (i) { i.addEventListener('input', recalc); });
        recalc();
      }
    }

    if (state.page === 'planificador') {
      var pace = document.getElementById('pace-range');
      var update = function () {
        var n = parseInt(pace.value, 10);
        document.getElementById('pace-out').textContent = n;
        var plan = graduationRoadmap(subjects, n);
        document.getElementById('grad-est').textContent = plan.estimated_graduation;
        document.getElementById('grad-terms').textContent = plan.remaining_terms;

        var html = plan.roadmap.map(function (t) {
          var cards = t.subjects.map(function (s) {
            var color = AREAS[s.area] ? AREAS[s.area].color : '#2563EB';
            return '<div class="subject-card" style="--area-color:' + color + '">' +
              '<div class="sc-code">' + esc(s.code) + '</div>' +
              '<div class="sc-name">' + esc(s.name) + '</div>' +
              '<div class="sc-area">' + esc(s.area) + '</div></div>';
          }).join('');
          return '<div class="term' + (t.is_current ? ' is-current' : '') + '">' +
            '<div class="term-head">' + esc(t.term_name) +
            (t.is_current ? '<span class="term-badge">En curso</span>' : '') +
            '<span style="margin-left:auto;font-weight:500;font-size:11px;color:#64748B">' + t.subjects.length + ' materias</span>' +
            '</div><div class="term-body">' + cards + '</div></div>';
        }).join('');

        if (plan.leftover) {
          html += '<div class="note warn">Quedan ' + plan.leftover + ' materias sin ubicar.</div>';
        }
        document.getElementById('roadmap').innerHTML = html;
      };
      pace.addEventListener('input', update);
    }

    if (state.page === 'importar') {
      wireImport(subjects);
    }

    renderStudentBox(subjects, k);
  }

  function renderStudentBox(subjects, k) {
    var box = document.getElementById('student-box');
    box.innerHTML = '<strong>' + esc(state.student.name || 'Estudiante') + '</strong>' +
      '<span>' + esc(state.student.plan || '') + '</span>' +
      '<div style="margin-top:8px">' + k.aprobadas + '/' + k.total_subjects + ' materias · ' + fmt(k.gpa, 2) + ' promedio</div>';
  }

  function updateNav() {
    document.querySelectorAll('#nav button').forEach(function (b) {
      if (b.getAttribute('data-page') === state.page) b.setAttribute('aria-current', 'page');
      else b.removeAttribute('aria-current');
    });
  }

  function debounce(fn, ms) {
    var t;
    return function () {
      var args = arguments, ctx = this;
      clearTimeout(t);
      t = setTimeout(function () { fn.apply(ctx, args); }, ms);
    };
  }

  /* ---------- importacion ---------- */

  function loadScript(src) {
    return new Promise(function (resolve, reject) {
      var s = document.createElement('script');
      s.src = src;
      s.onload = resolve;
      s.onerror = function () { reject(new Error('No se pudo cargar ' + src)); };
      document.head.appendChild(s);
    });
  }

  function ensureXLSX() {
    if (window.XLSX) return Promise.resolve();
    return loadScript('https://cdn.sheetjs.com/xlsx-0.20.3/package/dist/xlsx.full.min.js');
  }

  function readSheet(file) {
    return file.arrayBuffer().then(function (buf) {
      var wb = window.XLSX.read(new Uint8Array(buf), { type: 'array' });
      var ws = wb.Sheets[wb.SheetNames[0]];
      return window.XLSX.utils.sheet_to_json(ws, { header: 1, raw: true, defval: '' });
    });
  }

  function parsePlanRows(rows) {
    var out = {};
    var headerIdx = -1;
    for (var i = 0; i < rows.length; i++) {
      if (cleanText(rows[i][0]) === 'Actividad') { headerIdx = i; break; }
    }
    if (headerIdx === -1) throw new Error('No se encontro la tabla "Actividad" en el plan.');

    for (var j = headerIdx + 1; j < rows.length; j++) {
      var row = rows[j] || [];
      var act = cleanText(row[0]);
      if (!act) continue;
      if (act.indexOf('(*)') === 0 || act.indexOf('(-)') === 0 || act.indexOf('(!)') === 0) continue;

      var code = parseCode(act);
      if (!code || !BY_CODE[code]) continue;

      var raw = cleanText(row[4]);
      var origen = cleanText(row[5]);
      out[code] = { raw_nota: raw, origen: origen, numeric_grade: extractGrade(raw) };
    }
    return out;
  }

  function parseActRows(rows) {
    var out = {};
    var headerIdx = -1;
    for (var i = 0; i < rows.length; i++) {
      var joined = (rows[i] || []).map(cleanText).join('|').toLowerCase();
      if (joined.indexOf('actividad') !== -1 && joined.indexOf('nota') !== -1) { headerIdx = i; break; }
    }
    if (headerIdx === -1) throw new Error('No se encontro la tabla de actuacion.');

    var head = (rows[headerIdx] || []).map(function (c) { return cleanText(c).toLowerCase(); });
    var iAct = head.findIndex(function (h) { return h.indexOf('actividad') !== -1; });
    var iNota = head.findIndex(function (h) { return h === 'nota' || h.indexOf('nota') === 0; });
    var iRes = head.findIndex(function (h) { return h.indexOf('resultado') !== -1; });

    for (var j = headerIdx + 1; j < rows.length; j++) {
      var row = rows[j] || [];
      var name = cleanText(row[iAct]);
      var nota = row[iNota];
      if (!name || nota === '' || nota === null || nota === undefined) continue;

      for (var c = 0; c < CURRICULUM.length; c++) {
        var item = CURRICULUM[c];
        var a = item.name.toLowerCase(), b = name.toLowerCase();
        if (a.indexOf(b) !== -1 || b.indexOf(a) !== -1) {
          var num = parseFloat(nota);
          if (isNaN(num)) continue;
          var res = cleanText(iRes >= 0 ? row[iRes] : '');
          out[item.code] = {
            raw_nota: (num === Math.trunc(num) ? String(num) : String(num)) + (res ? ' (' + res + ')' : ''),
            origen: 'Actuación Provisoria',
            numeric_grade: num
          };
          break;
        }
      }
    }
    return out;
  }

  function wireImport() {
    var input = document.getElementById('file-input');
    var zone = document.getElementById('dropzone');
    var pick = document.getElementById('pick-btn');
    var reset = document.getElementById('reset-btn');

    pick.addEventListener('click', function (e) { e.preventDefault(); input.click(); });
    zone.addEventListener('click', function (e) {
      if (e.target === zone) input.click();
    });

    ['dragenter', 'dragover'].forEach(function (ev) {
      zone.addEventListener(ev, function (e) { e.preventDefault(); zone.classList.add('drag'); });
    });
    ['dragleave', 'drop'].forEach(function (ev) {
      zone.addEventListener(ev, function (e) { e.preventDefault(); zone.classList.remove('drag'); });
    });
    zone.addEventListener('drop', function (e) {
      if (e.dataTransfer.files.length) handleFiles(e.dataTransfer.files);
    });
    input.addEventListener('change', function () {
      if (input.files.length) handleFiles(input.files);
    });

    reset.addEventListener('click', function () {
      state.history = clone(RAW.history || {});
      state.student = clone(RAW.student || {});
      state.importLog = ['Datos restablecidos a academic_data.json.'];
      render();
    });
  }

  function handleFiles(fileList) {
    var files = Array.prototype.slice.call(fileList);
    var log = [];
    var chain = Promise.resolve();

    var historyPatch = {};

    files.forEach(function (file) {
      chain = chain.then(function () {
        if (/\.json$/i.test(file.name)) {
          return file.text().then(function (txt) {
            var data = JSON.parse(txt);
            if (data.academic_history) {
              Object.assign(historyPatch, data.academic_history);
              if (data.student_info) Object.assign(state.student, data.student_info);
              log.push('OK  ' + file.name + ': ' + Object.keys(data.academic_history).length + ' registros');
            } else if (data.curriculum || data.areas) {
              throw new Error('Ese JSON es un dataset de curriculum, no de historial.');
            } else {
              throw new Error('El JSON no tiene "academic_history".');
            }
          });
        }
        return ensureXLSX().then(function () {
          return readSheet(file);
        }).then(function (rows) {
          var isAct = rows.some(function (r) {
            var t = (r || []).map(cleanText).join('|').toLowerCase();
            return t.indexOf('actividad') !== -1 && t.indexOf('nota') !== -1 && t.indexOf('resultado') !== -1;
          });
          var parsed = isAct ? parseActRows(rows) : parsePlanRows(rows);
          Object.assign(historyPatch, parsed);
          log.push('OK  ' + file.name + ': ' + Object.keys(parsed).length + ' materias (' + (isAct ? 'actuacion' : 'plan') + ')');
        });
      }).catch(function (err) {
        log.push('ERR ' + file.name + ': ' + err.message);
      });
    });

    chain.then(function () {
      state.history = Object.assign({}, state.history, historyPatch);
      state.importLog = log;
      render();
    });
  }

  /* ---------- init ---------- */

  function setPage(page) {
    if (!VIEWS[page]) page = 'dashboard';
    state.page = page;
    if (location.hash !== '#' + page) {
      try { history.replaceState(null, '', '#' + page); } catch (err) { location.hash = page; }
    }
    updateNav();
    render();
  }

  function initNav() {
    var nav = document.getElementById('nav');
    nav.innerHTML = NAV.map(function (item) {
      return '<button type="button" data-page="' + item[0] + '"><span class="dot"></span>' + esc(item[1]) + '</button>';
    }).join('');
    nav.addEventListener('click', function (e) {
      var btn = e.target.closest('button[data-page]');
      if (!btn) return;
      setPage(btn.getAttribute('data-page'));
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });

    window.addEventListener('hashchange', function () {
      var page = location.hash.replace('#', '');
      if (page && page !== state.page && VIEWS[page]) setPage(page);
    });
  }

  function init() {
    if (!CURRICULUM.length) {
      document.getElementById('view').innerHTML =
        '<div class="note warn">No se encontraron datos. Ejecuta <code>python3 tools/build_static_data.py</code> para generar <code>docs/data.js</code>.</div>';
      return;
    }
    initNav();
    document.getElementById('btn-print').addEventListener('click', function () { window.print(); });
    setPage(location.hash.replace('#', '') || 'dashboard');
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
