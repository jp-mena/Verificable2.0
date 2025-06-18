from flask import Blueprint, request, render_template, redirect, url_for, flash, jsonify
from sga.models.instancia_curso import InstanciaCurso
from sga.models.curso import Curso
from sga.models.inscripcion import Inscripcion
from sga.models.alumno import Alumno
from sga.utils.validators import ValidationError, safe_int_conversion, validate_semester, validate_year
from sga.utils.error_handlers import ErrorHandler, safe_form_data, validate_required_fields

instancia_curso_bp = Blueprint('instancia_curso', __name__)

@instancia_curso_bp.route('/instancias-curso')
def listar_instancias():
    try:
        instancias = InstanciaCurso.obtener_todos()
        return render_template('instancias_curso/listar.html', instancias=instancias)
    except Exception as e:
        flash('Error al cargar las instancias de curso', 'error')
        return render_template('instancias_curso/listar.html', instancias=[])

@instancia_curso_bp.route('/instancias-curso/crear', methods=['GET', 'POST'])
@ErrorHandler.handle_route_error
def crear_instancia():
    if request.method == 'POST':
        data = safe_form_data(request.form, ['semestre', 'anio', 'curso_id'])
        
        validate_required_fields(data, ['semestre', 'anio', 'curso_id'])
        
        semestre = validate_semester(data['semestre'])
        anio = validate_year(data['anio'])
        curso_id = safe_int_conversion(data['curso_id'], 'Curso')
        
        curso = Curso.get_by_id(curso_id)
        if not curso:
            raise ValidationError('El curso seleccionado no existe')
        
        InstanciaCurso.crear(semestre, anio, curso_id)
        flash('Instancia de curso creada exitosamente', 'success')
        return redirect(url_for('instancia_curso.listar_instancias'))
    try:
        cursos = Curso.get_all()
    except Exception:
        cursos = []
        flash('Error al cargar la lista de cursos', 'warning')
    
    return render_template('instancias_curso/crear.html', cursos=cursos)

@instancia_curso_bp.route('/instancias-curso/<int:id>/editar', methods=['GET', 'POST'])
@ErrorHandler.handle_route_error
def editar_instancia(id):
    instancia_id = safe_int_conversion(id, 'ID de la instancia')
    
    instancia = InstanciaCurso.obtener_por_id(instancia_id)
    if not instancia:
        raise ValidationError('Instancia de curso no encontrada')
    
    if instancia.esta_cerrado():
        raise ValidationError('No se puede editar una instancia de curso que ya ha sido cerrada')
    
    if request.method == 'POST':
        data = safe_form_data(request.form, ['semestre', 'anio', 'curso_id'])
        
        validate_required_fields(data, ['semestre', 'anio', 'curso_id'])
        
        semestre = validate_semester(data['semestre'])
        anio = validate_year(data['anio'])
        curso_id = safe_int_conversion(data['curso_id'], 'Curso')
        
        curso = Curso.get_by_id(curso_id)
        if not curso:
            raise ValidationError('El curso seleccionado no existe')
        
        instancia.semestre = semestre
        instancia.anio = anio
        instancia.curso_id = curso_id
        instancia.actualizar()
        
        flash('Instancia de curso actualizada exitosamente', 'success')
        return redirect(url_for('instancia_curso.listar_instancias'))
    try:
        cursos = Curso.get_all()
    except Exception:
        cursos = []
        flash('Error al cargar la lista de cursos', 'warning')
    
    return render_template('instancias_curso/editar.html', instancia=instancia, cursos=cursos)

@instancia_curso_bp.route('/instancias-curso/<int:id>/eliminar', methods=['POST'])
@ErrorHandler.handle_route_error
def eliminar_instancia(id):
    instancia_id = safe_int_conversion(id, 'ID de la instancia')
    
    instancia = InstanciaCurso.obtener_por_id(instancia_id)
    if not instancia:
        raise ValidationError('Instancia de curso no encontrada')
    
    if instancia.esta_cerrado():
        raise ValidationError('No se puede eliminar una instancia de curso que ya ha sido cerrada')
    
    InstanciaCurso.eliminar(instancia_id)
    flash('Instancia de curso eliminada exitosamente', 'success')
    return redirect(url_for('instancia_curso.listar_instancias'))

@instancia_curso_bp.route('/instancias-curso/<int:id>/detalle')
@ErrorHandler.handle_route_error
def detalle_curso(id):
    instancia_id = safe_int_conversion(id, 'ID de la instancia')
    
    resumen = InstanciaCurso.obtener_resumen_curso(instancia_id)
    if not resumen:
        raise ValidationError('Instancia de curso no encontrada')
    
    alumnos_disponibles = []
    if not resumen['instancia']['cerrado']:
        try:
            alumnos_disponibles = Inscripcion.obtener_alumnos_no_inscritos(instancia_id)
        except Exception:
            flash('Error al cargar alumnos disponibles', 'warning')
    
    return render_template('instancias_curso/detalle.html', 
                         resumen=resumen, 
                         alumnos_disponibles=alumnos_disponibles)

@instancia_curso_bp.route('/instancias-curso/<int:id>/cerrar', methods=['GET', 'POST'])
@ErrorHandler.handle_route_error
def cerrar_instancia(id):
    instancia_id = safe_int_conversion(id, 'ID de la instancia')
    
    instancia = InstanciaCurso.obtener_por_id(instancia_id)
    if not instancia:
        raise ValidationError('Instancia de curso no encontrada')
    
    if instancia.esta_cerrado():
        flash('Esta instancia de curso ya está cerrada', 'warning')
        return redirect(url_for('instancia_curso.listar_instancias'))
    
    if request.method == 'POST':
        if InstanciaCurso.cerrar_curso(instancia_id):
            flash(f'Instancia de curso "{instancia.curso_nombre}" {instancia.semestre}-{instancia.anio} cerrada exitosamente. Las notas finales han sido calculadas.', 'success')
        else:
            raise ValidationError('Error al cerrar la instancia de curso')
        return redirect(url_for('instancia_curso.listar_instancias'))
    
    return render_template('instancias_curso/cerrar.html', instancia=instancia)

@instancia_curso_bp.route('/instancias-curso/<int:id>/inscribir', methods=['POST'])
@ErrorHandler.handle_route_error
def inscribir_alumno(id):
    instancia_id = safe_int_conversion(id, 'ID de la instancia')
    
    instancia = InstanciaCurso.obtener_por_id(instancia_id)
    if not instancia:
        raise ValidationError('Instancia de curso no encontrada')
    
    if instancia.esta_cerrado():
        raise ValidationError('No se pueden inscribir alumnos en un curso cerrado')
    
    data = safe_form_data(request.form, ['alumno_id'])
    validate_required_fields(data, ['alumno_id'])
    
    alumno_id = safe_int_conversion(data['alumno_id'], 'Alumno')
    
    alumno = Alumno.get_by_id(alumno_id)
    if not alumno:
        raise ValidationError('El alumno seleccionado no existe')
    
    if Inscripcion.esta_inscrito(alumno_id, instancia_id):
        flash('El alumno ya está inscrito en este curso', 'warning')
        return redirect(url_for('instancia_curso.detalle_curso', id=instancia_id))
    
    Inscripcion.crear(alumno_id, instancia_id)
    flash('Alumno inscrito exitosamente', 'success')
    
    return redirect(url_for('instancia_curso.detalle_curso', id=instancia_id))

@instancia_curso_bp.route('/instancias-curso/<int:instancia_id>/desinscribir/<int:alumno_id>', methods=['POST'])
@ErrorHandler.handle_route_error
def desinscribir_alumno(instancia_id, alumno_id):
    instancia_id = safe_int_conversion(instancia_id, 'ID de la instancia')
    alumno_id = safe_int_conversion(alumno_id, 'ID del alumno')
    
    instancia = InstanciaCurso.obtener_por_id(instancia_id)
    if not instancia:
        raise ValidationError('Instancia de curso no encontrada')
    
    if instancia.esta_cerrado():
        raise ValidationError('No se pueden desinscribir alumnos de un curso cerrado')
    
    try:
        inscripciones = Inscripcion.obtener_por_curso(instancia_id)
        inscripcion_id = None
        for insc in inscripciones:
            if insc['alumno_id'] == alumno_id:
                inscripcion_id = insc['id']
                break
        
        if inscripcion_id:
            Inscripcion.eliminar(inscripcion_id)
            flash('Alumno desinscrito exitosamente', 'success')
        else:
            flash('El alumno no está inscrito en este curso', 'warning')
    except Exception:
        raise ValidationError('Error al procesar la desinscripción')
    
    return redirect(url_for('instancia_curso.detalle_curso', id=instancia_id))

@instancia_curso_bp.route('/api/instancias-curso/<int:id>/cerrar', methods=['POST'])
@ErrorHandler.handle_api_error
def api_cerrar_instancia(id):
    """API para cerrar una instancia de curso"""
    instancia_id = safe_int_conversion(id, 'ID de la instancia')
    
    instancia = InstanciaCurso.obtener_por_id(instancia_id)
    if not instancia:
        return jsonify({'error': 'Instancia de curso no encontrada'}), 404
    
    if instancia.esta_cerrado():
        return jsonify({'error': 'Esta instancia ya está cerrada'}), 400
    
    if InstanciaCurso.cerrar_curso(instancia_id):
        return jsonify({
            'mensaje': f'Instancia cerrada exitosamente',
            'instancia_id': instancia_id
        }), 200
    else:
        return jsonify({'error': 'Error al cerrar la instancia'}), 500

@instancia_curso_bp.route('/api/instancias-curso/<int:id>/estado')
@ErrorHandler.handle_api_error
def api_estado_instancia(id):
    """API para obtener el estado de una instancia"""
    instancia_id = safe_int_conversion(id, 'ID de la instancia')
    
    instancia = InstanciaCurso.obtener_por_id(instancia_id)
    if not instancia:
        return jsonify({'error': 'Instancia no encontrada'}), 404
    
    return jsonify({
        'id': instancia.id,
        'semestre': instancia.semestre,
        'anio': instancia.anio,
        'curso_nombre': getattr(instancia, 'curso_nombre', ''),
        'cerrado': instancia.esta_cerrado(),
        'fecha_cierre': getattr(instancia, 'fecha_cierre', None)
    }), 200