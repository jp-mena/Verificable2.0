# filepath: routes/nota_routes.py
from flask import Blueprint, request, render_template, redirect, url_for, flash, jsonify
from models.nota import Nota
from models.alumno import Alumno
from models.instancia_topico import InstanciaTopico
from models.instancia_curso import InstanciaCurso
from db.database import execute_query

nota_bp = Blueprint('nota', __name__)

def _verificar_instancia_cerrada(instancia_topico_id):
    """Verifica si la instancia de tópico pertenece a un curso cerrado"""
    query = """
    SELECT ic.cerrado
    FROM instancias_topico it
    JOIN evaluaciones e ON it.evaluacion_id = e.id
    JOIN secciones s ON e.seccion_id = s.id
    JOIN instancias_curso ic ON s.instancia_id = ic.id
    WHERE it.id = ?
    """
    resultado = execute_query(query, (instancia_topico_id,))
    if resultado:
        return bool(resultado[0][0])
    return False

@nota_bp.route('/notas')
def listar_notas():
    """Lista todas las notas"""
    notas = Nota.obtener_todos()
    return render_template('notas/listar.html', notas=notas)

@nota_bp.route('/notas/crear', methods=['GET', 'POST'])
def crear_nota():
    """Crea una nueva nota"""
    if request.method == 'POST':
        try:
            alumno_id = int(request.form['alumno_id'])
            instancia_topico_id = int(request.form['instancia_topico_id'])
            nota = float(request.form['nota'])
            
            # Validar que la instancia de curso no esté cerrada
            if _verificar_instancia_cerrada(instancia_topico_id):
                flash('No se pueden agregar notas a un curso que ya ha sido cerrado', 'error')
                return redirect(url_for('nota.crear_nota'))
            
            # Validaciones básicas            if nota < 0 or nota > 7:
                flash('La nota debe estar entre 0 y 7', 'error')
                return redirect(url_for('nota.crear_nota'))
            
            Nota.crear(alumno_id, instancia_topico_id, nota)
            flash('Nota creada exitosamente', 'success')
            return redirect(url_for('nota.listar_notas'))
        except ValueError:
            flash('Error en los datos ingresados', 'error')
        except Exception as e:
            flash(f'Error al crear la nota: {str(e)}', 'error')
    
    # Obtener solo alumnos inscritos en cursos abiertos
    query_alumnos = """
    SELECT DISTINCT a.id, a.nombre, a.correo
    FROM alumnos a
    JOIN inscripciones i ON a.id = i.alumno_id
    JOIN instancias_curso ic ON i.instancia_curso_id = ic.id
    WHERE ic.cerrado = 0 OR ic.cerrado IS NULL
    ORDER BY a.nombre
    """
    resultados_alumnos = execute_query(query_alumnos)
    alumnos = [
        {
            'id': fila[0],
            'nombre': fila[1],
            'correo': fila[2]
        }
        for fila in resultados_alumnos
    ]
    
    # Filtrar instancias de tópico que pertenezcan solo a cursos abiertos
    todas_instancias = InstanciaTopico.obtener_todos()
    instancias_topico = []
    for instancia in todas_instancias:
        # Verificar si la evaluación pertenece a un curso abierto
        query = """
        SELECT ic.cerrado
        FROM evaluaciones e
        JOIN secciones s ON e.seccion_id = s.id
        JOIN instancias_curso ic ON s.instancia_id = ic.id
        WHERE e.id = ?
        """
        resultado = execute_query(query, (instancia['evaluacion_id'],))
        if resultado and not bool(resultado[0][0]):  # Si no está cerrado
            instancias_topico.append(instancia)
    
    return render_template('notas/crear.html', alumnos=alumnos, instancias_topico=instancias_topico)

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
            if nota.nota < 0 or nota.nota > 7:
                flash('La nota debe estar entre 0 y 7', 'error')
                return redirect(url_for('nota.editar_nota', id=id))
            
            nota.actualizar()
            flash('Nota actualizada exitosamente', 'success')
            return redirect(url_for('nota.listar_notas'))
        except ValueError:
            flash('Error en los datos ingresados', 'error')
        except Exception as e:
            flash(f'Error al actualizar la nota: {str(e)}', 'error')
    
    alumnos = Alumno.obtener_todos()
    # Filtrar instancias de tópico que pertenezcan solo a cursos abiertos
    todas_instancias = InstanciaTopico.obtener_todos()
    instancias_topico = []
    for instancia in todas_instancias:
        # Verificar si la evaluación pertenece a un curso abierto
        query = """
        SELECT ic.cerrado
        FROM evaluaciones e
        JOIN secciones s ON e.seccion_id = s.id
        JOIN instancias_curso ic ON s.instancia_id = ic.id
        WHERE e.id = ?
        """
        resultado = execute_query(query, (instancia['evaluacion_id'],))
        if resultado and not bool(resultado[0][0]):  # Si no está cerrado
            instancias_topico.append(instancia)
    
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
