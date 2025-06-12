# filepath: routes/instancia_curso_routes.py
from flask import Blueprint, request, render_template, redirect, url_for, flash, jsonify
from models.instancia_curso import InstanciaCurso
from models.curso import Curso
from models.inscripcion import Inscripcion
from models.alumno import Alumno

instancia_curso_bp = Blueprint('instancia_curso', __name__)

@instancia_curso_bp.route('/instancias-curso')
def listar_instancias():
    """Lista todas las instancias de curso"""
    instancias = InstanciaCurso.obtener_todos()
    return render_template('instancias_curso/listar.html', instancias=instancias)

@instancia_curso_bp.route('/instancias-curso/crear', methods=['GET', 'POST'])
def crear_instancia():
    """Crea una nueva instancia de curso"""
    if request.method == 'POST':
        try:
            semestre = int(request.form['semestre'])
            anio = int(request.form['anio'])
            curso_id = int(request.form['curso_id'])
            
            # Validaciones básicas
            if semestre not in [1, 2]:
                flash('El semestre debe ser 1 o 2', 'error')
                return redirect(url_for('instancia_curso.crear_instancia'))
            
            if anio < 2000 or anio > 2030:
                flash('El año debe estar entre 2000 y 2030', 'error')
                return redirect(url_for('instancia_curso.crear_instancia'))
            InstanciaCurso.crear(semestre, anio, curso_id)
            flash('Instancia de curso creada exitosamente', 'success')
            return redirect(url_for('instancia_curso.listar_instancias'))
            
        except ValueError:
            flash('Error en los datos ingresados', 'error')
        except Exception as e:
            flash(f'Error al crear la instancia: {str(e)}', 'error')
    
    cursos = Curso.get_all()
    return render_template('instancias_curso/crear.html', cursos=cursos)

@instancia_curso_bp.route('/instancias-curso/<int:id>/editar', methods=['GET', 'POST'])
def editar_instancia(id):
    """Edita una instancia de curso"""
    instancia = InstanciaCurso.obtener_por_id(id)
    if not instancia:
        flash('Instancia de curso no encontrada', 'error')
        return redirect(url_for('instancia_curso.listar_instancias'))
    
    # Verificar si la instancia está cerrada
    if instancia.esta_cerrado():
        flash('No se puede editar una instancia de curso que ya ha sido cerrada', 'error')
        return redirect(url_for('instancia_curso.listar_instancias'))
    
    if request.method == 'POST':
        try:
            instancia.semestre = int(request.form['semestre'])
            instancia.anio = int(request.form['anio'])
            instancia.curso_id = int(request.form['curso_id'])
            
            # Validaciones básicas
            if instancia.semestre not in [1, 2]:
                flash('El semestre debe ser 1 o 2', 'error')
                return redirect(url_for('instancia_curso.editar_instancia', id=id))
            
            if instancia.anio < 2000 or instancia.anio > 2030:
                flash('El año debe estar entre 2000 y 2030', 'error')
                return redirect(url_for('instancia_curso.editar_instancia', id=id))
            
            instancia.actualizar()
            flash('Instancia de curso actualizada exitosamente', 'success')
            return redirect(url_for('instancia_curso.listar_instancias'))
        except ValueError:
            flash('Error en los datos ingresados', 'error')
        except Exception as e:
            flash(f'Error al actualizar la instancia: {str(e)}', 'error')
    
    cursos = Curso.get_all()
    return render_template('instancias_curso/editar.html', instancia=instancia, cursos=cursos)

@instancia_curso_bp.route('/instancias-curso/<int:id>/eliminar', methods=['POST'])
def eliminar_instancia(id):
    """Elimina una instancia de curso"""
    try:
        # Verificar si la instancia está cerrada antes de eliminar
        instancia = InstanciaCurso.obtener_por_id(id)
        if instancia and instancia.esta_cerrado():
            flash('No se puede eliminar una instancia de curso que ya ha sido cerrada', 'error')
            return redirect(url_for('instancia_curso.listar_instancias'))
        
        InstanciaCurso.eliminar(id)
        flash('Instancia de curso eliminada exitosamente', 'success')
    except Exception as e:
        flash(f'Error al eliminar la instancia: {str(e)}', 'error')
    
    return redirect(url_for('instancia_curso.listar_instancias'))

@instancia_curso_bp.route('/instancias-curso/<int:id>/cerrar', methods=['GET', 'POST'])
def cerrar_instancia(id):
    """Cierra una instancia de curso y calcula notas finales"""
    instancia = InstanciaCurso.obtener_por_id(id)
    if not instancia:
        flash('Instancia de curso no encontrada', 'error')
        return redirect(url_for('instancia_curso.listar_instancias'))
    
    if instancia.esta_cerrado():
        flash('Esta instancia de curso ya está cerrada', 'warning')
        return redirect(url_for('instancia_curso.listar_instancias'))
    
    if request.method == 'POST':
        try:
            instancia.cerrar_curso()
            flash(f'Instancia de curso "{instancia.curso_nombre}" {instancia.semestre}-{instancia.anio} cerrada exitosamente. Las notas finales han sido calculadas.', 'success')
            return redirect(url_for('instancia_curso.listar_instancias'))
        except Exception as e:
            flash(f'Error al cerrar la instancia: {str(e)}', 'error')
    
    return render_template('instancias_curso/cerrar.html', instancia=instancia)

@instancia_curso_bp.route('/instancias-curso/<int:id>/notas-finales')
def ver_notas_finales(id):
    """Muestra las notas finales de una instancia cerrada"""
    instancia = InstanciaCurso.obtener_por_id(id)
    if not instancia:
        flash('Instancia de curso no encontrada', 'error')
        return redirect(url_for('instancia_curso.listar_instancias'))
    
    if not instancia.esta_cerrado():
        flash('Esta instancia de curso no está cerrada', 'warning')
        return redirect(url_for('instancia_curso.listar_instancias'))
    
    # Obtener notas finales
    query = """
    SELECT a.id, a.nombre, a.correo, nf.nota_final, nf.fecha_calculo
    FROM notas_finales nf
    JOIN alumnos a ON nf.alumno_id = a.id
    WHERE nf.instancia_curso_id = ?
    ORDER BY a.nombre
    """
    from db.database import execute_query
    notas_finales = execute_query(query, (id,))
    
    alumnos_notas = [
        {
            'alumno_id': fila[0],
            'nombre': fila[1],
            'correo': fila[2],
            'nota_final': fila[3],
            'fecha_calculo': fila[4]
        }
        for fila in notas_finales
    ]
    
    return render_template('instancias_curso/notas_finales.html', 
                         instancia=instancia, 
                         alumnos_notas=alumnos_notas)

@instancia_curso_bp.route('/instancias-curso/<int:id>/detalle')
def detalle_curso(id):
    """Muestra el detalle completo del curso con alumnos y notas"""
    try:
        resumen = InstanciaCurso.obtener_resumen_curso(id)
        if not resumen:
            flash('Instancia de curso no encontrada', 'error')
            return redirect(url_for('instancia_curso.listar_instancias'))
        
        # Obtener alumnos disponibles para inscribir (solo si no está cerrado)
        alumnos_disponibles = []
        if not resumen['instancia']['cerrado']:
            alumnos_disponibles = Inscripcion.obtener_alumnos_no_inscritos(id)
        
        return render_template('instancias_curso/detalle.html', 
                             resumen=resumen, 
                             alumnos_disponibles=alumnos_disponibles)
                             
    except Exception as e:
        flash(f'Error al obtener el detalle del curso: {str(e)}', 'error')
        return redirect(url_for('instancia_curso.listar_instancias'))

# API endpoints para funcionalidad de cierre
@instancia_curso_bp.route('/api/instancias-curso/<int:id>/cerrar', methods=['POST'])
def api_cerrar_instancia(id):
    """API para cerrar una instancia de curso"""
    try:
        instancia = InstanciaCurso.obtener_por_id(id)
        if not instancia:
            return jsonify({'error': 'Instancia de curso no encontrada'}), 404
        
        if instancia.esta_cerrado():
            return jsonify({'error': 'Esta instancia ya está cerrada'}), 400
        
        instancia.cerrar_curso()
        return jsonify({
            'mensaje': f'Instancia cerrada exitosamente',
            'instancia_id': id,
            'fecha_cierre': instancia.fecha_cierre
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@instancia_curso_bp.route('/api/instancias-curso/<int:id>/estado')
def api_estado_instancia(id):
    """API para obtener el estado de una instancia"""
    try:
        instancia = InstanciaCurso.obtener_por_id(id)        if not instancia:
            return jsonify({'error': 'Instancia no encontrada'}), 404
        
        return jsonify({
            'id': instancia.id,
            'semestre': instancia.semestre,
            'anio': instancia.anio,
            'curso_nombre': instancia.curso_nombre,
            'cerrado': instancia.esta_cerrado(),
            'fecha_cierre': getattr(instancia, 'fecha_cierre', None)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@instancia_curso_bp.route('/instancias-curso/<int:id>/inscribir', methods=['POST'])
def inscribir_alumno(id):
    """Inscribe un alumno en una instancia de curso"""
    try:
        # Verificar que la instancia existe
        instancia = InstanciaCurso.obtener_por_id(id)
        if not instancia:
            flash('Instancia de curso no encontrada', 'error')
            return redirect(url_for('instancia_curso.listar_instancias'))
        
        # Verificar que la instancia no esté cerrada
        if instancia.esta_cerrado():
            flash('No se pueden inscribir alumnos en un curso cerrado', 'error')
            return redirect(url_for('instancia_curso.detalle_curso', id=id))
        
        alumno_id = int(request.form['alumno_id'])
        
        # Verificar que el alumno no esté ya inscrito
        if Inscripcion.esta_inscrito(alumno_id, id):
            flash('El alumno ya está inscrito en este curso', 'warning')
            return redirect(url_for('instancia_curso.detalle_curso', id=id))
        
        # Crear la inscripción
        Inscripcion.crear(alumno_id, id)
        flash('Alumno inscrito exitosamente', 'success')
        
    except ValueError:
        flash('Error en los datos ingresados', 'error')
    except Exception as e:
        flash(f'Error al inscribir alumno: {str(e)}', 'error')
    
    return redirect(url_for('instancia_curso.detalle_curso', id=id))

@instancia_curso_bp.route('/instancias-curso/<int:instancia_id>/desinscribir/<int:alumno_id>', methods=['POST'])
def desinscribir_alumno(instancia_id, alumno_id):
    """Desinscribe un alumno de una instancia de curso"""
    try:
        # Verificar que la instancia existe
        instancia = InstanciaCurso.obtener_por_id(instancia_id)
        if not instancia:
            flash('Instancia de curso no encontrada', 'error')
            return redirect(url_for('instancia_curso.listar_instancias'))
        
        # Verificar que la instancia no esté cerrada
        if instancia.esta_cerrado():
            flash('No se pueden desinscribir alumnos de un curso cerrado', 'error')
            return redirect(url_for('instancia_curso.detalle_curso', id=instancia_id))
        
        # Buscar la inscripción
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
        
    except Exception as e:
        flash(f'Error al desinscribir alumno: {str(e)}', 'error')
    
    return redirect(url_for('instancia_curso.detalle_curso', id=instancia_id))
