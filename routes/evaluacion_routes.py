# filepath: routes/evaluacion_routes.py
from flask import Blueprint, request, render_template, redirect, url_for, flash, jsonify
from models.evaluacion import Evaluacion
from models.seccion import Seccion

evaluacion_bp = Blueprint('evaluacion', __name__)

@evaluacion_bp.route('/evaluaciones')
def listar_evaluaciones():
    """Lista todas las evaluaciones"""
    evaluaciones = Evaluacion.obtener_todos()
    return render_template('evaluaciones/listar.html', evaluaciones=evaluaciones)

@evaluacion_bp.route('/evaluaciones/crear', methods=['GET', 'POST'])
def crear_evaluacion():
    """Crea una nueva evaluación"""
    if request.method == 'POST':
        try:
            nombre = request.form['nombre'].strip()
            porcentaje = float(request.form['porcentaje'])
            seccion_id = int(request.form['seccion_id'])
            
            # Validaciones básicas
            if not nombre:
                flash('El nombre de la evaluación es requerido', 'error')
                return redirect(url_for('evaluacion.crear_evaluacion'))
            
            if porcentaje <= 0 or porcentaje > 100:
                flash('El porcentaje debe estar entre 0 y 100', 'error')
                return redirect(url_for('evaluacion.crear_evaluacion'))
            
            Evaluacion.crear(nombre, porcentaje, seccion_id)
            flash('Evaluación creada exitosamente', 'success')
            return redirect(url_for('evaluacion.listar_evaluaciones'))
            
        except ValueError:
            flash('Error en los datos ingresados', 'error')
        except Exception as e:
            flash(f'Error al crear la evaluación: {str(e)}', 'error')
    
    secciones = Seccion.obtener_todos()
    return render_template('evaluaciones/crear.html', secciones=secciones)

@evaluacion_bp.route('/evaluaciones/<int:id>/editar', methods=['GET', 'POST'])
def editar_evaluacion(id):
    """Edita una evaluación"""
    evaluacion = Evaluacion.obtener_por_id(id)
    if not evaluacion:
        flash('Evaluación no encontrada', 'error')
        return redirect(url_for('evaluacion.listar_evaluaciones'))
    
    if request.method == 'POST':
        try:
            evaluacion.nombre = request.form['nombre'].strip()
            evaluacion.porcentaje = float(request.form['porcentaje'])
            evaluacion.seccion_id = int(request.form['seccion_id'])
            
            # Validaciones básicas
            if not evaluacion.nombre:
                flash('El nombre de la evaluación es requerido', 'error')
                return redirect(url_for('evaluacion.editar_evaluacion', id=id))
            
            if evaluacion.porcentaje <= 0 or evaluacion.porcentaje > 100:
                flash('El porcentaje debe estar entre 0 y 100', 'error')
                return redirect(url_for('evaluacion.editar_evaluacion', id=id))
            
            evaluacion.actualizar()
            flash('Evaluación actualizada exitosamente', 'success')
            return redirect(url_for('evaluacion.listar_evaluaciones'))
            
        except ValueError:
            flash('Error en los datos ingresados', 'error')
        except Exception as e:
            flash(f'Error al actualizar la evaluación: {str(e)}', 'error')
    
    secciones = Seccion.obtener_todos()
    return render_template('evaluaciones/editar.html', evaluacion=evaluacion, secciones=secciones)

@evaluacion_bp.route('/evaluaciones/<int:id>/eliminar', methods=['POST'])
def eliminar_evaluacion(id):
    """Elimina una evaluación"""
    try:
        Evaluacion.eliminar(id)
        flash('Evaluación eliminada exitosamente', 'success')
    except Exception as e:
        flash(f'Error al eliminar la evaluación: {str(e)}', 'error')
    
    return redirect(url_for('evaluacion.listar_evaluaciones'))
