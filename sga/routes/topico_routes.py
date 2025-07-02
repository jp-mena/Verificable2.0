from flask import Blueprint, request, render_template, redirect, url_for, flash, jsonify
from sga.models.topico import Topico
from sga.utils.validators import ValidationError, validate_text_field, validate_choice, parse_integer_field
from sga.utils.error_handlers import ErrorHandler, safe_form_data, validate_required_fields

topico_bp = Blueprint('topico', __name__)

TIPOS_TOPICO = ['teorico', 'practico', 'taller', 'laboratorio']

def _obtener_topicos_para_listado():
    return Topico.obtener_todos()

def _renderizar_listado_topicos(topicos):
    return render_template('topicos/listar.html', topicos=topicos)

def _renderizar_listado_topicos_con_error():
    flash('Error al cargar los tópicos', 'error')
    return render_template('topicos/listar.html', topicos=[])

@topico_bp.route('/topicos')
def listar_topicos():
    try:
        topicos = _obtener_topicos_para_listado()
        return _renderizar_listado_topicos(topicos)
    except Exception as e:
        return _renderizar_listado_topicos_con_error()

@topico_bp.route('/topicos/crear', methods=['GET', 'POST'])
@ErrorHandler.handle_route_error
def crear_topico():
    if request.method == 'POST':
        data = safe_form_data(request.form, ['nombre', 'tipo'])
        
        validate_required_fields(data, ['nombre', 'tipo'])
        
        nombre = validate_text_field(data['nombre'], 'Nombre', min_length=2, max_length=100)
        tipo = validate_text_field(data['tipo'], 'Tipo', min_length=2, max_length=50)
        
        Topico.crear(nombre, tipo)
        flash('Tópico creado exitosamente', 'success')
        return redirect(url_for('topico.listar_topicos'))
    
    return render_template('topicos/crear.html', tipos_permitidos=TIPOS_TOPICO)

@topico_bp.route('/topicos/<int:id>/editar', methods=['GET', 'POST'])
@ErrorHandler.handle_route_error
def editar_topico(id):
    topico_id = parse_integer_field(id, 'ID del tópico')
    
    topico = Topico.obtener_por_id(topico_id)
    if not topico:
        raise ValidationError('Tópico no encontrado')
    
    if request.method == 'POST':
        data = safe_form_data(request.form, ['nombre', 'tipo'])
        
        validate_required_fields(data, ['nombre', 'tipo'])
        
        nombre = validate_text_field(data['nombre'], 'Nombre', min_length=2, max_length=100)
        tipo = validate_text_field(data['tipo'], 'Tipo', min_length=2, max_length=50)
        
        
        topico.nombre = nombre
        topico.tipo = tipo
        topico.actualizar()
        
        flash('Tópico actualizado exitosamente', 'success')
        return redirect(url_for('topico.listar_topicos'))
    
    return render_template('topicos/editar.html', topico=topico, tipos_permitidos=TIPOS_TOPICO)

@topico_bp.route('/topicos/<int:id>/eliminar', methods=['POST'])
@ErrorHandler.handle_route_error
def eliminar_topico(id):
    topico_id = parse_integer_field(id, 'ID del tópico')
    
    topico = Topico.obtener_por_id(topico_id)
    if not topico:
        raise ValidationError('Tópico no encontrado')
    
    Topico.eliminar(topico_id)
    flash('Tópico eliminado exitosamente', 'success')
    
    return redirect(url_for('topico.listar_topicos'))
