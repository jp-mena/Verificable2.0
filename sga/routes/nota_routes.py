from flask import Blueprint, request, render_template, redirect, url_for, flash, jsonify
from sga.models.nota import Nota
from sga.models.alumno import Alumno
from sga.models.instancia_topico import InstanciaTopico
from sga.models.instancia_curso import InstanciaCurso
from sga.db.database import execute_query

nota_bp = Blueprint('nota', __name__)

def _verificar_instancia_cerrada(instancia_topico_id):
    """Verifica si la instancia de tópico pertenece a un curso cerrado"""
    try:
        if not isinstance(instancia_topico_id, int) or instancia_topico_id <= 0:
            return True
        
        query = """
        SELECT ic.cerrado
        FROM instancias_topico it
        JOIN evaluaciones e ON it.evaluacion_id = e.id
        JOIN secciones s ON e.seccion_id = s.id
        JOIN instancias_curso ic ON s.instancia_id = ic.id
        WHERE it.id = %s
        """
        resultado = execute_query(query, (instancia_topico_id,))
        if resultado:
            return bool(resultado[0][0])
        return True
    except Exception as e:
        print(f"Error verificando instancia cerrada: {e}")
        return True

def _obtener_notas_para_listado():
    """Query: Obtiene todas las notas"""
    return Nota.obtener_todos()

def _renderizar_listado_notas(notas):
    """Command: Renderiza la vista de listado de notas"""
    return render_template('notas/listar.html', notas=notas or [])

def _renderizar_listado_notas_con_error(error_msg):
    """Command: Renderiza la vista de listado con error"""
    flash(f'Error al cargar las notas: {error_msg}', 'error')
    return render_template('notas/listar.html', notas=[])

@nota_bp.route('/notas')
def listar_notas():
    try:
        notas = _obtener_notas_para_listado()
        return _renderizar_listado_notas(notas)
    except Exception as e:
        return _renderizar_listado_notas_con_error(str(e))

@nota_bp.route('/notas/crear', methods=['GET', 'POST'])
def crear_nota():
    return redirect(url_for('nota.crear_nota_simple'))

@nota_bp.route('/notas/crear/paso2/<int:instancia_curso_id>', methods=['GET', 'POST'])
def crear_nota_paso2(instancia_curso_id):
    return redirect(url_for('nota.crear_nota_simple'))

@nota_bp.route('/notas/crear-simple', methods=['GET', 'POST'])
def crear_nota_simple():
    """Crea una nota simple para un alumno en una instancia de tópico"""
    if request.method == 'POST':
        try:
            datos_validados = _validar_datos_nota_simple(request.form)
            _verificar_prerequisitos_nota(datos_validados)
            
            Nota.crear(
                datos_validados['alumno_id'], 
                datos_validados['instancia_topico_id'], 
                datos_validados['nota_valor']
            )
            
            flash('Nota creada exitosamente', 'success')
            return redirect(url_for('nota.listar_notas'))
            
        except ValueError as e:
            return _manejar_error_creacion_nota(str(e))
        except Exception as e:
            return _manejar_error_creacion_nota(f'Error al crear la nota: {str(e)}')
    
    return _renderizar_formulario_nota_simple()

def _validar_datos_nota_simple(form_data):
    """Valida y extrae los datos del formulario de nota simple"""
    try:
        datos = {
            'instancia_curso_id': int(form_data['instancia_curso_id']),
            'alumno_id': int(form_data['alumno_id']),
            'instancia_topico_id': int(form_data['instancia_topico_id']),
            'nota_valor': float(form_data['nota'])
        }
        
        if not (1.0 <= datos['nota_valor'] <= 7.0):
            raise ValueError('La nota debe estar entre 1.0 y 7.0')
            
        return datos
    except (KeyError, ValueError, TypeError) as e:
        raise ValueError('Error en los datos ingresados') from e

def _verificar_prerequisitos_nota(datos):
    """Verifica que se cumplan los prerequisitos para crear la nota"""
    # Verificar que la instancia existe y está abierta
    instancia = InstanciaCurso.obtener_por_id(datos['instancia_curso_id'])
    if not instancia:
        raise ValueError('Instancia de curso no encontrada')
    
    if getattr(instancia, 'cerrado', False):
        raise ValueError('No se pueden agregar notas a un curso cerrado')
    
    # Verificar que el alumno está inscrito
    from sga.models.inscripcion import Inscripcion
    if not Inscripcion.esta_inscrito(datos['alumno_id'], datos['instancia_curso_id']):
        raise ValueError('El alumno no está inscrito en esta instancia')

def _manejar_error_creacion_nota(mensaje_error):
    """Maneja errores en la creación de notas"""
    if "Ya existe una nota" in mensaje_error:
        flash('Ya existe una nota para este alumno en esta evaluación', 'error')
    else:
        flash(mensaje_error, 'error')
    return redirect(url_for('nota.crear_nota_simple'))

def _renderizar_formulario_nota_simple():
    """Renderiza el formulario de creación de nota simple"""
    instancias_curso = InstanciaCurso.obtener_todos()
    instancias_abiertas = [inst for inst in instancias_curso if not inst.get('cerrado', False)]
    return render_template('notas/crear_simple.html', instancias_curso=instancias_abiertas)

@nota_bp.route('/api/notas/alumnos-inscritos/<int:instancia_curso_id>')
def obtener_alumnos_inscritos(instancia_curso_id):
    try:
        from sga.models.inscripcion import Inscripcion
        alumnos = Inscripcion.obtener_por_curso(instancia_curso_id)
        print(f"DEBUG: Instancia {instancia_curso_id} tiene {len(alumnos)} alumnos inscritos")
        return jsonify({
            'alumnos': alumnos,
            'count': len(alumnos),
            'instancia_curso_id': instancia_curso_id
        }), 200
    except Exception as e:
        print(f"ERROR en obtener_alumnos_inscritos: {str(e)}")
        return jsonify({'error': str(e)}), 500

@nota_bp.route('/api/notas/instancias-topico/<int:instancia_curso_id>')
def obtener_instancias_topico_por_curso(instancia_curso_id):
    try:
        query = """
        SELECT it.id, it.nombre, it.peso, e.nombre as evaluacion_nombre
        FROM instancias_topico it
        JOIN evaluaciones e ON it.evaluacion_id = e.id
        JOIN secciones s ON e.seccion_id = s.id
        WHERE s.instancia_id = %s
        ORDER BY e.nombre, it.nombre
        """
        resultados = execute_query(query, (instancia_curso_id,))
        instancias_topico = [
            {
                'id': fila[0],
                'nombre': fila[1],
                'peso': fila[2],
                'evaluacion_nombre': fila[3]
            }
            for fila in resultados
        ]
        print(f"DEBUG: Instancia {instancia_curso_id} tiene {len(instancias_topico)} evaluaciones disponibles")
        return jsonify({'instancias_topico': instancias_topico}), 200
    except Exception as e:
        print(f"ERROR en obtener_instancias_topico_por_curso: {str(e)}")
        return jsonify({'error': str(e)}), 500

def _obtener_instancia_curso_id_por_topico(instancia_topico_id):
    """Query: Obtiene el ID de instancia de curso por tópico"""
    query = """
    SELECT ic.id as instancia_curso_id
    FROM instancias_topico it
    JOIN evaluaciones e ON it.evaluacion_id = e.id
    JOIN secciones s ON e.seccion_id = s.id
    JOIN instancias_curso ic ON s.instancia_id = ic.id
    WHERE it.id = %s
    """
    resultado = execute_query(query, (instancia_topico_id,))
    return resultado[0][0] if resultado else None

def _obtener_datos_brutos_instancias_topico_abiertas():
    """Query: Obtiene datos brutos de instancias de tópico de cursos abiertos"""
    query = """
    SELECT it.id, it.nombre, it.peso, e.nombre as evaluacion_nombre, c.codigo as curso_codigo
    FROM instancias_topico it
    JOIN evaluaciones e ON it.evaluacion_id = e.id
    JOIN secciones s ON e.seccion_id = s.id
    JOIN instancias_curso ic ON s.instancia_id = ic.id
    JOIN cursos c ON ic.curso_id = c.id
    WHERE ic.cerrado = 0 OR ic.cerrado IS NULL
    ORDER BY c.codigo, e.nombre, it.nombre
    """
    return execute_query(query)

def _mapear_instancia_topico_para_form(fila):
    """Mapper: Mapea una fila de instancia de tópico para formulario"""
    return {
        'id': fila[0],
        'nombre': fila[1],
        'peso': fila[2],
        'evaluacion_nombre': fila[3],
        'curso_codigo': fila[4]
    }

def _mapear_instancias_topico_para_form(resultados):
    """Mapper: Mapea lista de instancias de tópico para formulario"""
    return [_mapear_instancia_topico_para_form(fila) for fila in resultados]

def _validar_y_actualizar_nota(nota, form_data):
    """Business Logic: Valida y actualiza una nota"""
    nota.alumno_id = int(form_data['alumno_id'])
    nota.instancia_topico_id = int(form_data['instancia_topico_id'])
    nota.nota = float(form_data['nota'])
    
    if _verificar_instancia_cerrada(nota.instancia_topico_id):
        raise ValueError('No se pueden editar notas a un curso que ya ha sido cerrado')
      
    if nota.nota < 1.0 or nota.nota > 7.0:
        raise ValueError('La nota debe estar entre 1.0 y 7.0')
    
    nota.actualizar()

def _renderizar_formulario_editar_nota(nota, alumnos, instancias_topico):
    """Renderer: Renderiza el formulario de edición de nota"""
    return render_template('notas/editar.html', nota=nota, alumnos=alumnos, instancias_topico=instancias_topico)

@nota_bp.route('/notas/<int:id>/editar', methods=['GET', 'POST'])
def editar_nota(id):
    nota = Nota.obtener_por_id(id)
    if not nota:
        flash('Nota no encontrada', 'error')
        return redirect(url_for('nota.listar_notas'))
    
    if _verificar_instancia_cerrada(nota.instancia_topico_id):
        flash('No se pueden editar notas de un curso que ya ha sido cerrado', 'error')
        return redirect(url_for('nota.listar_notas'))
    
    if request.method == 'POST':
        try:
            _validar_y_actualizar_nota(nota, request.form)
            flash('Nota actualizada exitosamente', 'success')
            return redirect(url_for('nota.listar_notas'))
        except ValueError as e:
            flash(str(e), 'error')
            return redirect(url_for('nota.editar_nota', id=id))
        except Exception as e:
            flash(f'Error al actualizar la nota: {str(e)}', 'error')
    
    # Obtener datos para el formulario
    instancia_curso_id = _obtener_instancia_curso_id_por_topico(nota.instancia_topico_id)
    if not instancia_curso_id:
        flash('No se pudo determinar la instancia de curso para esta nota', 'error')
        return redirect(url_for('nota.listar_notas'))
    
    from sga.models.inscripcion import Inscripcion
    alumnos = Inscripcion.obtener_por_curso(instancia_curso_id)
    
    resultados_topicos = _obtener_datos_brutos_instancias_topico_abiertas()
    instancias_topico = _mapear_instancias_topico_para_form(resultados_topicos)
    
    return _renderizar_formulario_editar_nota(nota, alumnos, instancias_topico)

@nota_bp.route('/notas/<int:id>/eliminar', methods=['POST'])
def eliminar_nota(id):
    try:
        nota = Nota.obtener_por_id(id)
        if not nota:
            flash('Nota no encontrada', 'error')
            return redirect(url_for('nota.listar_notas'))
          
        if _verificar_instancia_cerrada(nota.instancia_topico_id):
            flash('No se pueden eliminar notas de un curso que ya ha sido cerrado', 'error')
            return redirect(url_for('nota.listar_notas'))
        
        Nota.eliminar(id)
        flash('Nota eliminada exitosamente', 'success')
    except Exception as e:
        flash(f'Error al eliminar la nota: {str(e)}', 'error')
    
    return redirect(url_for('nota.listar_notas'))
