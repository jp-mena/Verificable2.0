# filepath: routes/instancia_topico_routes.py
from flask import Blueprint, request, render_template, redirect, url_for, flash, jsonify
from sga.models.instancia_topico import InstanciaTopico
from sga.models.evaluacion import Evaluacion
from sga.models.seccion import Seccion
from sga.models.topico import Topico
from sga.db.database import execute_query

instancia_topico_bp = Blueprint('instancia_topico', __name__)

def _verificar_evaluacion_cerrada(evaluacion_id):
    """Verifica si la evaluación pertenece a un curso cerrado"""
    query = """
    SELECT ic.cerrado
    FROM evaluaciones e
    JOIN secciones s ON e.seccion_id = s.id
    JOIN instancias_curso ic ON s.instancia_id = ic.id
    WHERE e.id = ?
    """
    resultado = execute_query(query, (evaluacion_id,))
    if resultado:
        return bool(resultado[0][0])
    return False

def _verificar_instancia_curso_cerrada(instancia_id):
    """Verifica si una instancia de curso está cerrada"""
    query = "SELECT cerrado FROM instancias_curso WHERE id = ?"
    resultado = execute_query(query, (instancia_id,))
    if resultado:
        return bool(resultado[0][0])
    return False

@instancia_topico_bp.route('/instancias-topico')
def listar_instancias():
    """Lista todas las instancias de tópico"""
    instancias = InstanciaTopico.obtener_todos()
    return render_template('instancias_topico/listar.html', instancias=instancias)

@instancia_topico_bp.route('/instancias-topico/crear', methods=['GET', 'POST'])
def crear_instancia():
    """Crea una nueva instancia de tópico"""
    if request.method == 'POST':
        try:
            nombre = request.form['nombre'].strip()
            peso = float(request.form['peso'])
            opcional = 'opcional' in request.form
            evaluacion_id = int(request.form['evaluacion_id'])
            topico_id = int(request.form['topico_id'])
            
            # Verificar que la evaluación no pertenezca a un curso cerrado
            if _verificar_evaluacion_cerrada(evaluacion_id):
                flash('No se pueden crear instancias de tópico en un curso que ya ha sido cerrado', 'error')
                return redirect(url_for('instancia_topico.crear_instancia'))
              # Validaciones básicas
            if not nombre:
                flash('El nombre de la instancia es requerido', 'error')
                return redirect(url_for('instancia_topico.crear_instancia'))
            
            if peso <= 0 or peso > 100:
                flash('El peso debe estar entre 0 y 100', 'error')
                return redirect(url_for('instancia_topico.crear_instancia'))
            
            InstanciaTopico.crear(nombre, peso, opcional, evaluacion_id, topico_id)
            flash('Instancia de tópico creada exitosamente', 'success')
            return redirect(url_for('instancia_topico.listar_instancias'))
            
        except ValueError:
            flash('Error en los datos ingresados', 'error')
        except Exception as e:
            flash(f'Error al crear la instancia: {str(e)}', 'error')
    
    # Filtrar evaluaciones que pertenezcan solo a cursos abiertos
    todas_evaluaciones = Evaluacion.obtener_todos()
    evaluaciones = []
    for evaluacion in todas_evaluaciones:
        if not _verificar_evaluacion_cerrada(evaluacion['id']):
            evaluaciones.append(evaluacion)
    
    topicos = Topico.obtener_todos()
    return render_template('instancias_topico/crear.html', evaluaciones=evaluaciones, topicos=topicos)

@instancia_topico_bp.route('/instancias-topico/<int:id>/editar', methods=['GET', 'POST'])
def editar_instancia(id):
    """Edita una instancia de tópico"""
    instancia = InstanciaTopico.obtener_por_id(id)
    if not instancia:
        flash('Instancia de tópico no encontrada', 'error')
        return redirect(url_for('instancia_topico.listar_instancias'))
    
    # Verificar si la evaluación actual pertenece a un curso cerrado
    if _verificar_evaluacion_cerrada(instancia.evaluacion_id):
        flash('No se pueden editar instancias de tópico de un curso que ya ha sido cerrado', 'error')
        return redirect(url_for('instancia_topico.listar_instancias'))
    
    if request.method == 'POST':
        try:
            instancia.nombre = request.form['nombre'].strip()
            instancia.peso = float(request.form['peso'])
            instancia.opcional = 'opcional' in request.form
            nueva_evaluacion_id = int(request.form['evaluacion_id'])
            instancia.topico_id = int(request.form['topico_id'])
            
            # Verificar que la nueva evaluación no pertenezca a un curso cerrado
            if _verificar_evaluacion_cerrada(nueva_evaluacion_id):
                flash('No se puede mover la instancia a un curso que ya ha sido cerrado', 'error')
                return redirect(url_for('instancia_topico.editar_instancia', id=id))
            
            instancia.evaluacion_id = nueva_evaluacion_id
              # Validaciones básicas
            if not instancia.nombre:
                flash('El nombre de la instancia es requerido', 'error')
                return redirect(url_for('instancia_topico.editar_instancia', id=id))
            
            if instancia.peso <= 0 or instancia.peso > 100:
                flash('El peso debe estar entre 0 y 100', 'error')
                return redirect(url_for('instancia_topico.editar_instancia', id=id))
            
            instancia.actualizar()
            flash('Instancia de tópico actualizada exitosamente', 'success')
            return redirect(url_for('instancia_topico.listar_instancias'))
            
        except ValueError:
            flash('Error en los datos ingresados', 'error')
        except Exception as e:
            flash(f'Error al actualizar la instancia: {str(e)}', 'error')
    
    # Filtrar evaluaciones que pertenezcan solo a cursos abiertos
    todas_evaluaciones = Evaluacion.obtener_todos()
    evaluaciones = []
    for evaluacion in todas_evaluaciones:
        if not _verificar_evaluacion_cerrada(evaluacion['id']):
            evaluaciones.append(evaluacion)
    
    topicos = Topico.obtener_todos()
    return render_template('instancias_topico/editar.html', instancia=instancia, evaluaciones=evaluaciones, topicos=topicos)

@instancia_topico_bp.route('/instancias-topico/<int:id>/eliminar', methods=['POST'])
def eliminar_instancia(id):
    """Elimina una instancia de tópico"""
    try:
        # Obtener la instancia antes de eliminarla para verificar si está cerrada
        instancia = InstanciaTopico.obtener_por_id(id)
        if not instancia:
            flash('Instancia de tópico no encontrada', 'error')
            return redirect(url_for('instancia_topico.listar_instancias'))
        
        # Verificar si la evaluación pertenece a un curso cerrado
        if _verificar_evaluacion_cerrada(instancia.evaluacion_id):
            flash('No se pueden eliminar instancias de tópico de un curso que ya ha sido cerrado', 'error')
            return redirect(url_for('instancia_topico.listar_instancias'))
        
        InstanciaTopico.eliminar(id)
        flash('Instancia de tópico eliminada exitosamente', 'success')
    except Exception as e:
        flash(f'Error al eliminar la instancia: {str(e)}', 'error')
    
    return redirect(url_for('instancia_topico.listar_instancias'))
