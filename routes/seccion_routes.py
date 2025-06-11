# filepath: routes/seccion_routes.py
from flask import Blueprint, request, render_template, redirect, url_for, flash, jsonify
from models.seccion import Seccion
from models.instancia_curso import InstanciaCurso

seccion_bp = Blueprint('seccion', __name__)

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
    
    instancias = InstanciaCurso.obtener_todos()
    return render_template('secciones/crear.html', instancias=instancias)

@seccion_bp.route('/secciones/<int:id>/editar', methods=['GET', 'POST'])
def editar_seccion(id):
    """Edita una sección"""
    seccion = Seccion.obtener_por_id(id)
    if not seccion:
        flash('Sección no encontrada', 'error')
        return redirect(url_for('seccion.listar_secciones'))
    
    if request.method == 'POST':
        try:
            seccion.numero = int(request.form['numero'])
            seccion.instancia_id = int(request.form['instancia_id'])
            
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
    
    instancias = InstanciaCurso.obtener_todos()
    return render_template('secciones/editar.html', seccion=seccion, instancias=instancias)

@seccion_bp.route('/secciones/<int:id>/eliminar', methods=['POST'])
def eliminar_seccion(id):
    """Elimina una sección"""
    try:
        Seccion.eliminar(id)
        flash('Sección eliminada exitosamente', 'success')
    except Exception as e:
        flash(f'Error al eliminar la sección: {str(e)}', 'error')
    
    return redirect(url_for('seccion.listar_secciones'))
