# filepath: routes/seccion_routes.py
from flask import Blueprint, request, render_template, redirect, url_for, flash, jsonify
from models.seccion import Seccion
from models.instancia_curso import InstanciaCurso
from db.database import execute_query

seccion_bp = Blueprint('seccion', __name__)

def _verificar_instancia_curso_cerrada(instancia_id):
    """Verifica si una instancia de curso está cerrada"""
    query = "SELECT cerrado FROM instancias_curso WHERE id = ?"
    resultado = execute_query(query, (instancia_id,))
    if resultado:
        return bool(resultado[0][0])
    return False

@seccion_bp.route('/secciones')
def listar_secciones():
    """Lista todas las secciones"""
    secciones = Seccion.obtener_todos()
    return render_template('secciones/listar.html', secciones=secciones)

@seccion_bp.route('/secciones/crear', methods=['GET', 'POST'])
def crear_seccion():
    """Crea una nueva sección"""
    if request.method == 'POST':
        try:
            numero = int(request.form['numero'])
            instancia_id = int(request.form['instancia_id'])
            
            # Verificar que la instancia de curso no esté cerrada
            if _verificar_instancia_curso_cerrada(instancia_id):
                flash('No se pueden crear secciones en un curso que ya ha sido cerrado', 'error')
                return redirect(url_for('seccion.crear_seccion'))
            
            # Validaciones básicas
            if numero <= 0:
                flash('El número de sección debe ser mayor a 0', 'error')
                return redirect(url_for('seccion.crear_seccion'))
            
            Seccion.crear(numero, instancia_id)
            flash('Sección creada exitosamente', 'success')
            return redirect(url_for('seccion.listar_secciones'))
            
        except ValueError:
            flash('Error en los datos ingresados', 'error')
        except Exception as e:
            flash(f'Error al crear la sección: {str(e)}', 'error')
      # Filtrar instancias de curso que estén abiertas
    todas_instancias = InstanciaCurso.obtener_todos()
    instancias = [inst for inst in todas_instancias if not inst['cerrado']]
    return render_template('secciones/crear.html', instancias=instancias)

@seccion_bp.route('/secciones/<int:id>/editar', methods=['GET', 'POST'])
def editar_seccion(id):
    """Edita una sección"""
    seccion = Seccion.obtener_por_id(id)
    if not seccion:
        flash('Sección no encontrada', 'error')
        return redirect(url_for('seccion.listar_secciones'))
    
    # Verificar si la instancia de curso actual está cerrada
    if _verificar_instancia_curso_cerrada(seccion.instancia_id):
        flash('No se pueden editar secciones de un curso que ya ha sido cerrado', 'error')
        return redirect(url_for('seccion.listar_secciones'))
    
    if request.method == 'POST':
        try:
            seccion.numero = int(request.form['numero'])
            nueva_instancia_id = int(request.form['instancia_id'])
            
            # Verificar que la nueva instancia de curso no esté cerrada
            if _verificar_instancia_curso_cerrada(nueva_instancia_id):
                flash('No se puede mover la sección a un curso que ya ha sido cerrado', 'error')
                return redirect(url_for('seccion.editar_seccion', id=id))
            
            seccion.instancia_id = nueva_instancia_id
            
            # Validaciones básicas
            if seccion.numero <= 0:
                flash('El número de sección debe ser mayor a 0', 'error')
                return redirect(url_for('seccion.editar_seccion', id=id))
            
            seccion.actualizar()
            flash('Sección actualizada exitosamente', 'success')
            return redirect(url_for('seccion.listar_secciones'))
            
        except ValueError:
            flash('Error en los datos ingresados', 'error')
        except Exception as e:
            flash(f'Error al actualizar la sección: {str(e)}', 'error')
      # Filtrar instancias de curso que estén abiertas (todas para poder mover a abierta)
    todas_instancias = InstanciaCurso.obtener_todos()
    instancias = [inst for inst in todas_instancias if not inst['cerrado']]
    return render_template('secciones/editar.html', seccion=seccion, instancias=instancias)

@seccion_bp.route('/secciones/<int:id>/eliminar', methods=['POST'])
def eliminar_seccion(id):
    """Elimina una sección"""
    try:
        # Obtener la sección antes de eliminarla para verificar si está cerrada
        seccion = Seccion.obtener_por_id(id)
        if not seccion:
            flash('Sección no encontrada', 'error')
            return redirect(url_for('seccion.listar_secciones'))
        
        # Verificar si la instancia de curso está cerrada
        if _verificar_instancia_curso_cerrada(seccion.instancia_id):
            flash('No se pueden eliminar secciones de un curso que ya ha sido cerrado', 'error')
            return redirect(url_for('seccion.listar_secciones'))
        
        Seccion.eliminar(id)
        flash('Sección eliminada exitosamente', 'success')
    except Exception as e:
        flash(f'Error al eliminar la sección: {str(e)}', 'error')
    
    return redirect(url_for('seccion.listar_secciones'))
