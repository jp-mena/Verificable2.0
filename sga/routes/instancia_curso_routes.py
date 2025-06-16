# filepath: routes/instancia_curso_routes.py
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
    """Lista todas las instancias de curso"""
    try:
        instancias = InstanciaCurso.obtener_todos()
        return render_template('instancias_curso/listar.html', instancias=instancias)
    except Exception as e:
        flash('Error al cargar las instancias de curso', 'error')
        return render_template('instancias_curso/listar.html', instancias=[])

@instancia_curso_bp.route('/instancias-curso/crear', methods=['GET', 'POST'])
@ErrorHandler.handle_route_error
def crear_instancia():
    """Crea una nueva instancia de curso"""
    if request.method == 'POST':
        # Extraer datos del formulario de forma segura
        data = safe_form_data(request.form, ['semestre', 'anio', 'curso_id'])
        
        # Validar campos requeridos
        validate_required_fields(data, ['semestre', 'anio', 'curso_id'])
        
        # Validar formato de cada campo
        semestre = validate_semester(data['semestre'])
        anio = validate_year(data['anio'])
        curso_id = safe_int_conversion(data['curso_id'], 'Curso')
        
        # Verificar que el curso existe
        curso = Curso.get_by_id(curso_id)
        if not curso:
            raise ValidationError('El curso seleccionado no existe')
        
        # Crear la instancia
        InstanciaCurso.crear(semestre, anio, curso_id)
        flash('Instancia de curso creada exitosamente', 'success')
        return redirect(url_for('instancia_curso.listar_instancias'))
    
    # Obtener cursos para el formulario
    try:
        cursos = Curso.get_all()
        cursos_list = [{'id': c[0], 'codigo': c[1], 'nombre': c[2]} for c in cursos]
    except Exception:
        cursos_list = []
        flash('Error al cargar la lista de cursos', 'warning')
    
    return render_template('instancias_curso/crear.html', cursos=cursos_list)

@instancia_curso_bp.route('/instancias-curso/<int:id>/editar', methods=['GET', 'POST'])
@ErrorHandler.handle_route_error
def editar_instancia(id):
    """Edita una instancia de curso"""
    # Validar ID
    instancia_id = safe_int_conversion(id, 'ID de la instancia')
    
    # Obtener instancia
    instancia = InstanciaCurso.obtener_por_id(instancia_id)
    if not instancia:
        raise ValidationError('Instancia de curso no encontrada')
    
    # Verificar si la instancia está cerrada
    if instancia.esta_cerrado():
        raise ValidationError('No se puede editar una instancia de curso que ya ha sido cerrada')
    
    if request.method == 'POST':
        # Extraer datos del formulario de forma segura
        data = safe_form_data(request.form, ['semestre', 'anio', 'curso_id'])
        
        # Validar campos requeridos
        validate_required_fields(data, ['semestre', 'anio', 'curso_id'])
        
        # Validar formato de cada campo
        semestre = validate_semester(data['semestre'])
        anio = validate_year(data['anio'])
        curso_id = safe_int_conversion(data['curso_id'], 'Curso')
        
        # Verificar que el curso existe
        curso = Curso.get_by_id(curso_id)
        if not curso:
            raise ValidationError('El curso seleccionado no existe')
        
        # Actualizar la instancia
        instancia.semestre = semestre
        instancia.anio = anio
        instancia.curso_id = curso_id
        instancia.actualizar()
        
        flash('Instancia de curso actualizada exitosamente', 'success')
        return redirect(url_for('instancia_curso.listar_instancias'))
    
    # Obtener cursos para el formulario
    try:
        cursos = Curso.get_all()
        cursos_list = [{'id': c[0], 'codigo': c[1], 'nombre': c[2]} for c in cursos]
    except Exception:
        cursos_list = []
        flash('Error al cargar la lista de cursos', 'warning')
    
    return render_template('instancias_curso/editar.html', instancia=instancia, cursos=cursos_list)

@instancia_curso_bp.route('/instancias-curso/<int:id>/eliminar', methods=['POST'])
@ErrorHandler.handle_route_error
def eliminar_instancia(id):
    """Elimina una instancia de curso"""
    # Validar ID
    instancia_id = safe_int_conversion(id, 'ID de la instancia')
    
    # Verificar que la instancia existe
    instancia = InstanciaCurso.obtener_por_id(instancia_id)
    if not instancia:
        raise ValidationError('Instancia de curso no encontrada')
    
    # Verificar si la instancia está cerrada
    if instancia.esta_cerrado():
        raise ValidationError('No se puede eliminar una instancia de curso que ya ha sido cerrada')
    
    # Eliminar la instancia
    InstanciaCurso.eliminar(instancia_id)
    flash('Instancia de curso eliminada exitosamente', 'success')
    return redirect(url_for('instancia_curso.listar_instancias'))

@instancia_curso_bp.route('/instancias-curso/<int:id>/detalle')
@ErrorHandler.handle_route_error
def detalle_curso(id):
    """Muestra el detalle completo del curso con alumnos y notas"""
    # Validar ID
    instancia_id = safe_int_conversion(id, 'ID de la instancia')
    
    # Obtener resumen del curso
    resumen = InstanciaCurso.obtener_resumen_curso(instancia_id)
    if not resumen:
        raise ValidationError('Instancia de curso no encontrada')
    
    # Obtener alumnos disponibles para inscribir (solo si no está cerrado)
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
    """Cierra una instancia de curso y calcula notas finales"""
    # Validar ID
    instancia_id = safe_int_conversion(id, 'ID de la instancia')
    
    # Obtener instancia
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
    """Inscribe un alumno en una instancia de curso"""
    # Validar ID de instancia
    instancia_id = safe_int_conversion(id, 'ID de la instancia')
    
    # Verificar que la instancia existe
    instancia = InstanciaCurso.obtener_por_id(instancia_id)
    if not instancia:
        raise ValidationError('Instancia de curso no encontrada')
    
    # Verificar que la instancia no esté cerrada
    if instancia.esta_cerrado():
        raise ValidationError('No se pueden inscribir alumnos en un curso cerrado')
    
    # Extraer y validar datos del formulario
    data = safe_form_data(request.form, ['alumno_id'])
    validate_required_fields(data, ['alumno_id'])
    
    alumno_id = safe_int_conversion(data['alumno_id'], 'Alumno')
    
    # Verificar que el alumno existe
    alumno = Alumno.get_by_id(alumno_id)
    if not alumno:
        raise ValidationError('El alumno seleccionado no existe')
    
    # Verificar que el alumno no esté ya inscrito
    if Inscripcion.esta_inscrito(alumno_id, instancia_id):
        flash('El alumno ya está inscrito en este curso', 'warning')
        return redirect(url_for('instancia_curso.detalle_curso', id=instancia_id))
    
    # Crear la inscripción
    Inscripcion.crear(alumno_id, instancia_id)
    flash('Alumno inscrito exitosamente', 'success')
    
    return redirect(url_for('instancia_curso.detalle_curso', id=instancia_id))

@instancia_curso_bp.route('/instancias-curso/<int:instancia_id>/desinscribir/<int:alumno_id>', methods=['POST'])
@ErrorHandler.handle_route_error
def desinscribir_alumno(instancia_id, alumno_id):
    """Desinscribe un alumno de una instancia de curso"""
    # Validar IDs
    instancia_id = safe_int_conversion(instancia_id, 'ID de la instancia')
    alumno_id = safe_int_conversion(alumno_id, 'ID del alumno')
    
    # Verificar que la instancia existe
    instancia = InstanciaCurso.obtener_por_id(instancia_id)
    if not instancia:
        raise ValidationError('Instancia de curso no encontrada')
    
    # Verificar que la instancia no esté cerrada
    if instancia.esta_cerrado():
        raise ValidationError('No se pueden desinscribir alumnos de un curso cerrado')
    
    # Buscar la inscripción
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

# API endpoints
@instancia_curso_bp.route('/api/instancias-curso/<int:id>/cerrar', methods=['POST'])
@ErrorHandler.handle_api_error
def api_cerrar_instancia(id):
    """API para cerrar una instancia de curso"""
    # Validar ID
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
    # Validar ID
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