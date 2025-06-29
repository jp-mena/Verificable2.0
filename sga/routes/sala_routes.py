from flask import Blueprint, render_template, request, redirect, url_for, flash
from sga.models.sala import Sala

sala_bp = Blueprint("sala", __name__, url_prefix="/salas")

def _obtener_salas_para_listado():
    """Query: Obtiene todas las salas formateadas"""
    filas = Sala.obtener_todas()
    return [{"id": f[0], "nombre": f[1], "capacidad": f[2]} for f in filas]

def _renderizar_listado_salas(salas):
    """Command: Renderiza la vista de listado de salas"""
    return render_template("salas/listar.html", salas=salas)

@sala_bp.route("/")
def listar_salas():
    salas = _obtener_salas_para_listado()
    return _renderizar_listado_salas(salas)

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

def _obtener_sala_por_id(id):
    """Query: Obtiene una sala por ID y la formatea"""
    fila = Sala.obtener_por_id(id)
    if not fila:
        return None
    return {"id": fila[0], "nombre": fila[1], "capacidad": fila[2]}

def _actualizar_sala_validada(id, nombre, capacidad):
    """Command: Actualiza una sala después de validar"""
    if not nombre or capacidad < 1:
        raise ValueError("Datos inválidos")
    Sala.actualizar(id, nombre, capacidad)

def _renderizar_formulario_editar_sala(sala):
    """Command: Renderiza el formulario de edición de sala"""
    return render_template("salas/editar.html", sala=sala)

def _procesar_sala_no_encontrada():
    """Command: Procesa cuando no se encuentra la sala"""
    flash("Sala no encontrada", "danger")
    return redirect(url_for("sala.listar_salas"))

def _procesar_actualizacion_exitosa_sala():
    """Command: Procesa una actualización exitosa"""
    flash("Sala actualizada", "success")
    return redirect(url_for("sala.listar_salas"))

def _procesar_error_validacion_sala(id):
    """Command: Procesa errores de validación"""
    flash("Datos inválidos", "danger")
    return redirect(url_for("sala.editar_sala", id=id))

@sala_bp.route("/<int:id>/editar", methods=["GET", "POST"])
def editar_sala(id):
    sala = _obtener_sala_por_id(id)
    if not sala:
        return _procesar_sala_no_encontrada()

    if request.method == "POST":
        nombre = request.form["nombre"].strip()
        capacidad = int(request.form["capacidad"])
        try:
            _actualizar_sala_validada(id, nombre, capacidad)
            return _procesar_actualizacion_exitosa_sala()
        except ValueError:
            return _procesar_error_validacion_sala(id)

    return _renderizar_formulario_editar_sala(sala)

@sala_bp.route("/<int:id>/eliminar", methods=["POST"])
def eliminar_sala(id):
    Sala.eliminar(id)
    flash("Sala eliminada", "success")
    return redirect(url_for("sala.listar_salas"))
