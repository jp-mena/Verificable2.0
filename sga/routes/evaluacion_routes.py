from flask import Blueprint, request, render_template, redirect, url_for, flash, jsonify
from sga.models.evaluacion import Evaluacion
from sga.models.seccion import Seccion
from sga.db.database import execute_query
from sga.utils.validators import ValidationError, validate_text_field, validate_percentage, parse_integer_field
from sga.utils.error_handlers import ErrorHandler, safe_form_data, validate_required_fields

evaluacion_bp = Blueprint('evaluacion', __name__)

def _verificar_seccion_cerrada(seccion_id):
    try:
        seccion_id = parse_integer_field(seccion_id, 'ID de sección')
        query = """
        SELECT ic.cerrado
        FROM secciones s
        JOIN instancias_curso ic ON s.instancia_id = ic.id
        WHERE s.id = %s
        """
        resultado = execute_query(query, (seccion_id,))
        if resultado:
            return bool(resultado[0][0])
        return False
    except Exception:
        return True

def _verificar_instancia_curso_cerrada(instancia_id):
    try:
        instancia_id = parse_integer_field(instancia_id, 'ID de instancia')
        query = "SELECT cerrado FROM instancias_curso WHERE id = %s"
        resultado = execute_query(query, (instancia_id,))
        if resultado:
            return bool(resultado[0][0])
        return False
    except Exception:
        return True

def _obtener_evaluaciones_para_listado():
    return Evaluacion.obtener_todos()

def _renderizar_listado_evaluaciones(evaluaciones):
    return render_template('evaluaciones/listar.html', evaluaciones=evaluaciones)

def _renderizar_listado_evaluaciones_con_error():
    flash('Error al cargar las evaluaciones', 'error')
    return render_template('evaluaciones/listar.html', evaluaciones=[])

@evaluacion_bp.route('/evaluaciones')
def listar_evaluaciones():
    try:
        evaluaciones = _obtener_evaluaciones_para_listado()
        return _renderizar_listado_evaluaciones(evaluaciones)
    except Exception as e:
        return _renderizar_listado_evaluaciones_con_error()

@evaluacion_bp.route('/evaluaciones/crear', methods=['GET', 'POST'])
@ErrorHandler.handle_route_error
def crear_evaluacion():
    if request.method == 'POST':
        data = safe_form_data(request.form, ['nombre', 'porcentaje', 'seccion_id'])
        
        validate_required_fields(data, ['nombre', 'porcentaje', 'seccion_id'])
        
        nombre = validate_text_field(data['nombre'], 'Nombre', min_length=2, max_length=100)
        porcentaje = validate_percentage(data['porcentaje'])
        seccion_id = parse_integer_field(data['seccion_id'], 'Sección')
        
        seccion = Seccion.obtener_por_id(seccion_id)
        if not seccion:
            raise ValidationError('La sección seleccionada no existe')
        
        if _verificar_seccion_cerrada(seccion_id):
            raise ValidationError('No se pueden crear evaluaciones en un curso que ya ha sido cerrado')
        
        Evaluacion.crear(nombre, porcentaje, seccion_id)
        flash('Evaluación creada exitosamente', 'success')
        return redirect(url_for('evaluacion.listar_evaluaciones'))
    
    try:
        todas_secciones = Seccion.obtener_todos()
        secciones = []
        for seccion in todas_secciones:
            if not _verificar_instancia_curso_cerrada(seccion['instancia_id']):
                secciones.append(seccion)
    except Exception:
        secciones = []
        flash('Error al cargar las secciones disponibles', 'warning')
    
    return render_template('evaluaciones/crear.html', secciones=secciones)

@evaluacion_bp.route('/evaluaciones/<int:id>/editar', methods=['GET', 'POST'])
@ErrorHandler.handle_route_error
def editar_evaluacion(id):
    evaluacion_id = parse_integer_field(id, 'ID de la evaluación')
    
    evaluacion = Evaluacion.obtener_por_id(evaluacion_id)
    if not evaluacion:
        raise ValidationError('Evaluación no encontrada')
    
    if _verificar_seccion_cerrada(evaluacion.seccion_id):
        raise ValidationError('No se pueden editar evaluaciones de un curso que ya ha sido cerrado')
    
    if request.method == 'POST':
        data = safe_form_data(request.form, ['nombre', 'porcentaje', 'seccion_id'])
        
        validate_required_fields(data, ['nombre', 'porcentaje', 'seccion_id'])
        
        nombre = validate_text_field(data['nombre'], 'Nombre', min_length=2, max_length=100)
        porcentaje = validate_percentage(data['porcentaje'])
        nueva_seccion_id = parse_integer_field(data['seccion_id'], 'Sección')
        
        seccion = Seccion.obtener_por_id(nueva_seccion_id)
        if not seccion:
            raise ValidationError('La sección seleccionada no existe')
        
        if _verificar_seccion_cerrada(nueva_seccion_id):
            raise ValidationError('No se puede mover la evaluación a un curso que ya ha sido cerrado')
        
        evaluacion.nombre = nombre
        evaluacion.porcentaje = porcentaje
        evaluacion.seccion_id = nueva_seccion_id
        evaluacion.actualizar()
        
        flash('Evaluación actualizada exitosamente', 'success')
        return redirect(url_for('evaluacion.listar_evaluaciones'))
    
    try:
        todas_secciones = Seccion.obtener_todos()
        secciones = []
        for seccion in todas_secciones:
            if not _verificar_instancia_curso_cerrada(seccion['instancia_id']):
                secciones.append(seccion)
    except Exception:
        secciones = []
        flash('Error al cargar las secciones disponibles', 'warning')
    
    return render_template('evaluaciones/editar.html', evaluacion=evaluacion, secciones=secciones)

@evaluacion_bp.route('/evaluaciones/<int:id>/eliminar', methods=['POST'])
@ErrorHandler.handle_route_error
def eliminar_evaluacion(id):
    evaluacion_id = parse_integer_field(id, 'ID de la evaluación')
    
    evaluacion = Evaluacion.obtener_por_id(evaluacion_id)
    if not evaluacion:
        raise ValidationError('Evaluación no encontrada')
    
    if _verificar_seccion_cerrada(evaluacion.seccion_id):
        raise ValidationError('No se pueden eliminar evaluaciones de un curso que ya ha sido cerrado')
    
    Evaluacion.eliminar(evaluacion_id)
    flash('Evaluación eliminada exitosamente', 'success')
    
    return redirect(url_for('evaluacion.listar_evaluaciones'))
