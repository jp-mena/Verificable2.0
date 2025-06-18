from flask import Blueprint, render_template, request, redirect, url_for, flash
from sga.models.sala import Sala

sala_bp = Blueprint("sala", __name__, url_prefix="/salas")

@sala_bp.route("/")
def listar():
    salas = Sala.obtener_todas()
    return render_template("salas/listar.html", salas=salas)

@sala_bp.route("/crear", methods=["POST"])
def crear():
    nombre = request.form["nombre"]
    capacidad = int(request.form["capacidad"])
    Sala.crear(nombre, capacidad)
    return redirect(url_for("sala.listar"))

@sala_bp.route("/<int:id>/eliminar", methods=["POST"])
def eliminar(id):
    Sala.eliminar(id)
    return redirect(url_for("sala.listar"))
