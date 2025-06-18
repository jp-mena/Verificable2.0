# filepath: routes/nota_routes.py
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
            return True  # Si hay error, asumir cerrado por seguridad
        
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
        return True  # Si no se encuentra, asumir cerrado
    except Exception as e:
        print(f"Error verificando instancia cerrada: {e}")
        return True  # En caso de error, asumir cerrado

@nota_bp.route('/notas')
def listar_notas():
    """Lista todas las notas"""
    try:
        notas = Nota.obtener_todos()
        return render_template('notas/listar.html', notas=notas or [])
    except Exception as e:
        flash(f'Error al cargar las notas: {str(e)}', 'error')
        return render_template('notas/listar.html', notas=[])

@nota_bp.route('/notas/crear', methods=['GET', 'POST'])
def crear_nota():
    """Redirige al formulario simple (el wizard fue eliminado)"""
    return redirect(url_for('nota.crear_nota_simple'))

@nota_bp.route('/notas/crear/paso2/<int:instancia_curso_id>', methods=['GET', 'POST'])
def crear_nota_paso2(instancia_curso_id):
    """Redirige al formulario simple (el wizard fue eliminado)"""
    return redirect(url_for('nota.crear_nota_simple'))

@nota_bp.route('/notas/crear-simple', methods=['GET', 'POST'])
def crear_nota_simple():
    """Crear nota en una sola pantalla con dropdowns dinámicos"""
    if request.method == 'POST':
        try:
            print(f"DEBUG: Datos del formulario: {request.form}")
            instancia_curso_id = int(request.form['instancia_curso_id'])
            alumno_id = int(request.form['alumno_id'])
            instancia_topico_id = int(request.form['instancia_topico_id'])
            nota_valor = float(request.form['nota'])
            
            print(f"DEBUG: Valores extraídos - instancia_curso_id: {instancia_curso_id}, alumno_id: {alumno_id}, instancia_topico_id: {instancia_topico_id}, nota_valor: {nota_valor}")
            
            # Validaciones
            if nota_valor < 1.0 or nota_valor > 7.0:
                flash('La nota debe estar entre 1.0 y 7.0', 'error')
                return redirect(url_for('nota.crear_nota_simple'))
              
            # Validar que la instancia no esté cerrada
            print(f"DEBUG: Obteniendo instancia curso {instancia_curso_id}")
            instancia = InstanciaCurso.obtener_por_id(instancia_curso_id)
            if not instancia:
                flash('Instancia de curso no encontrada', 'error')
                return redirect(url_for('nota.crear_nota_simple'))
            
            print(f"DEBUG: Instancia obtenida: {instancia}")
            if getattr(instancia, 'cerrado', False):
                flash('No se pueden agregar notas a un curso cerrado', 'error')
                return redirect(url_for('nota.crear_nota_simple'))
            
            # Validar que el alumno esté inscrito
            print(f"DEBUG: Verificando inscripción del alumno {alumno_id} en instancia {instancia_curso_id}")
            from sga.models.inscripcion import Inscripcion
            if not Inscripcion.esta_inscrito(alumno_id, instancia_curso_id):
                flash('El alumno no está inscrito en esta instancia', 'error')
                return redirect(url_for('nota.crear_nota_simple'))
            
            # Crear la nota
            print(f"DEBUG: Creando nota - alumno_id: {alumno_id}, instancia_topico_id: {instancia_topico_id}, nota_valor: {nota_valor}")
            Nota.crear(alumno_id, instancia_topico_id, nota_valor)
            print(f"DEBUG: Nota creada exitosamente")
            flash('Nota creada exitosamente', 'success')
            return redirect(url_for('nota.listar_notas'))
            
        except ValueError as e:
            if "Ya existe una nota" in str(e):
                flash('Ya existe una nota para este alumno en esta evaluación', 'error')
            else:
                flash('Error en los datos ingresados', 'error')
        except Exception as e:
            flash(f'Error al crear la nota: {str(e)}', 'error')
    
    # Obtener instancias de curso abiertas
    instancias_curso = InstanciaCurso.obtener_todos()
    instancias_abiertas = [inst for inst in instancias_curso if not inst.get('cerrado', False)]
    
    return render_template('notas/crear_simple.html', instancias_curso=instancias_abiertas)

# API endpoints para obtener datos dinámicamente
@nota_bp.route('/api/notas/alumnos-inscritos/<int:instancia_curso_id>')
def obtener_alumnos_inscritos(instancia_curso_id):
    """API para obtener alumnos inscritos en una instancia de curso"""
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
    """API para obtener instancias de tópico de una instancia de curso"""
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

@nota_bp.route('/notas/<int:id>/editar', methods=['GET', 'POST'])
def editar_nota(id):
    """Edita una nota"""
    nota = Nota.obtener_por_id(id)
    if not nota:
        flash('Nota no encontrada', 'error')
        return redirect(url_for('nota.listar_notas'))
    
    # Verificar si la instancia de curso está cerrada
    if _verificar_instancia_cerrada(nota.instancia_topico_id):
        flash('No se pueden editar notas de un curso que ya ha sido cerrado', 'error')
        return redirect(url_for('nota.listar_notas'))
    
    if request.method == 'POST':
        try:
            nota.alumno_id = int(request.form['alumno_id'])
            nota.instancia_topico_id = int(request.form['instancia_topico_id'])
            nota.nota = float(request.form['nota'])
            
            # Verificar nuevamente que la nueva instancia de tópico no esté cerrada
            if _verificar_instancia_cerrada(nota.instancia_topico_id):
                flash('No se pueden editar notas a un curso que ya ha sido cerrado', 'error')
                return redirect(url_for('nota.editar_nota', id=id))
              
            # Validaciones básicas
            if nota.nota < 1.0 or nota.nota > 7.0:
                flash('La nota debe estar entre 1.0 y 7.0', 'error')
                return redirect(url_for('nota.editar_nota', id=id))
            
            nota.actualizar()
            flash('Nota actualizada exitosamente', 'success')
            return redirect(url_for('nota.listar_notas'))
        except ValueError:
            flash('Error en los datos ingresados', 'error')
        except Exception as e:
            flash(f'Error al actualizar la nota: {str(e)}', 'error')
    
    # Obtener la instancia de curso para esta nota
    query_instancia = """
    SELECT ic.id as instancia_curso_id
    FROM instancias_topico it
    JOIN evaluaciones e ON it.evaluacion_id = e.id
    JOIN secciones s ON e.seccion_id = s.id
    JOIN instancias_curso ic ON s.instancia_id = ic.id
    WHERE it.id = %s
    """
    resultado_instancia = execute_query(query_instancia, (nota.instancia_topico_id,))
    
    if not resultado_instancia:
        flash('No se pudo determinar la instancia de curso para esta nota', 'error')
        return redirect(url_for('nota.listar_notas'))
    
    instancia_curso_id = resultado_instancia[0][0]
    
    # Obtener alumnos inscritos en la instancia de curso específica
    from sga.models.inscripcion import Inscripcion
    alumnos = Inscripcion.obtener_por_curso(instancia_curso_id)
    
    # Obtener instancias de tópico con información completa de cursos abiertos
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
    resultados = execute_query(query)
    instancias_topico = [
        {
            'id': fila[0],
            'nombre': fila[1],
            'peso': fila[2],
            'evaluacion_nombre': fila[3],
            'curso_codigo': fila[4]
        }
        for fila in resultados
    ]
    
    return render_template('notas/editar.html', nota=nota, alumnos=alumnos, instancias_topico=instancias_topico)

@nota_bp.route('/notas/<int:id>/eliminar', methods=['POST'])
def eliminar_nota(id):
    """Elimina una nota"""
    try:
        # Obtener la nota antes de eliminarla para verificar si está cerrada
        nota = Nota.obtener_por_id(id)
        if not nota:
            flash('Nota no encontrada', 'error')
            return redirect(url_for('nota.listar_notas'))
          
        # Verificar si la instancia de curso está cerrada
        if _verificar_instancia_cerrada(nota.instancia_topico_id):
            flash('No se pueden eliminar notas de un curso que ya ha sido cerrado', 'error')
            return redirect(url_for('nota.listar_notas'))
        
        Nota.eliminar(id)
        flash('Nota eliminada exitosamente', 'success')
    except Exception as e:
        flash(f'Error al eliminar la nota: {str(e)}', 'error')
    
    return redirect(url_for('nota.listar_notas'))
