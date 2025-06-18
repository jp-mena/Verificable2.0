from flask import Blueprint, render_template, request, redirect, url_for, flash
from sga.models.sala import Sala

sala_bp = Blueprint("sala", __name__, url_prefix="/salas")

@sala_bp.route("/")
def listar_salas():
    filas = Sala.obtener_todas()
    salas = [{"id": f[0], "nombre": f[1], "capacidad": f[2]} for f in filas]
    return render_template("salas/listar.html", salas=salas)

@sala_bp.route("/crear", methods=["GET", "POST"])
def crear_sala():
    if request.method == "POST":
        nombre = request.form["nombre"].strip()
        capacidad = int(request.form["capacidad"])
        if not nombre or capacidad < 1:
            flash("Datos inválidos", "danger")
            return redirect(url_for("sala.crear_sala"))
        Sala.crear(nombre, capacidad)
        flash("Sala creada correctamente", "success")
        return redirect(url_for("sala.listar_salas"))
    return render_template("salas/crear.html")

@sala_bp.route("/<int:id>/editar", methods=["GET", "POST"])
def editar_sala(id):
    fila = Sala.obtener_por_id(id)
    if not fila:
        flash("Sala no encontrada", "danger")
        return redirect(url_for("sala.listar_salas"))

    sala = {"id": fila[0], "nombre": fila[1], "capacidad": fila[2]}

    if request.method == "POST":
        nombre = request.form["nombre"].strip()
        capacidad = int(request.form["capacidad"])
        if not nombre or capacidad < 1:
            flash("Datos inválidos", "danger")
            return redirect(url_for("sala.editar_sala", id=id))
        Sala.actualizar(id, nombre, capacidad)
        flash("Sala actualizada", "success")
        return redirect(url_for("sala.listar_salas"))

    return render_template("salas/editar.html", sala=sala)

@sala_bp.route("/<int:id>/eliminar", methods=["POST"])
def eliminar_sala(id):
    Sala.eliminar(id)
    flash("Sala eliminada", "success")
    return redirect(url_for("sala.listar_salas"))
