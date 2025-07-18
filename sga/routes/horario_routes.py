from flask import Blueprint, render_template, request, redirect, url_for, flash
from sga.services.scheduler import SchedulerService
from sga.db.database import execute_query
from datetime import timedelta, time

horario_bp = Blueprint("horario", __name__, url_prefix="/horarios")

def _to_str(hora):
    if isinstance(hora, timedelta):
        minutos = hora.total_seconds() // 60
        h, m = divmod(int(minutos), 60)
        return f"{h:02d}:{m:02d}"
    if isinstance(hora, time):
        return hora.strftime("%H:%M")
    return str(hora)[:5]  

def _grid_horario(semestre, anio):
    rows = execute_query(
        """
        SELECT c.codigo,
               s.numero,
               sal.nombre,
               b.dia,
               b.inicio,
               b.fin
        FROM horarios h
        JOIN secciones s          ON s.id  = h.seccion_id
        JOIN instancias_curso ic  ON ic.id = s.instancia_id
        JOIN cursos c             ON c.id  = ic.curso_id
        JOIN bloques b            ON b.id  = h.bloque_id
        JOIN salas sal            ON sal.id= h.sala_id
        WHERE ic.semestre=%s AND ic.anio=%s
        ORDER BY b.inicio,b.dia
        """,
        (semestre, anio),
    )
    horas = ["09:00","10:00","11:00","12:00","14:00","15:00","16:00","17:00"]
    grid = {h:{d:[] for d in range(1,6)} for h in horas}
    for cod, sec, sala, dia, ini, _ in rows:
        key = ini.strftime("%H:%M") if hasattr(ini, "strftime") else f"{int(ini.total_seconds()//3600):02d}:00"
        grid[key][dia].append(f"{cod}-{sec}<br><small>{sala}</small>")
    return horas, grid


@horario_bp.route("/")
def ver_horario():
    semestre = int(request.args.get("semestre", 1))
    anio = int(request.args.get("anio", 2025))
    horas, grid = _grid_horario(semestre, anio)
    return render_template(
        "horarios/listar.html", horas=horas, grid=grid, semestre=semestre, anio=anio
    )


@horario_bp.route("/generar", methods=["POST"])
def generar_horario():
    semestre = int(request.form["semestre"])
    anio = int(request.form["anio"])
    ok, msg = SchedulerService(semestre, anio).solve_and_persist()
    flash(msg, "success" if ok else "danger")
    return redirect(url_for("horario.ver_horario", semestre=semestre, anio=anio))
