# filepath: routes/nota_routes.py
from flask import Blueprint, request, render_template, redirect, url_for, flash, jsonify
from models.nota import Nota
from models.alumno import Alumno
from models.instancia_topico import InstanciaTopico

nota_bp = Blueprint('nota', __name__)

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
            
            # Validaciones básicas
            if nota < 0 or nota > 7:
                flash('La nota debe estar entre 0 y 7', 'error')
                return redirect(url_for('nota.crear_nota'))
            
            Nota.crear(alumno_id, instancia_topico_id, nota)
            flash('Nota creada exitosamente', 'success')
            return redirect(url_for('nota.listar_notas'))
            
        except ValueError:
            flash('Error en los datos ingresados', 'error')
        except Exception as e:
            flash(f'Error al crear la nota: {str(e)}', 'error')
    
    alumnos = Alumno.obtener_todos()
    instancias_topico = InstanciaTopico.obtener_todos()
    return render_template('notas/crear.html', alumnos=alumnos, instancias_topico=instancias_topico)

@nota_bp.route('/notas/<int:id>/editar', methods=['GET', 'POST'])
def editar_nota(id):
    """Edita una nota"""
    nota = Nota.obtener_por_id(id)
    if not nota:
        flash('Nota no encontrada', 'error')
        return redirect(url_for('nota.listar_notas'))
    
    if request.method == 'POST':
        try:
            nota.alumno_id = int(request.form['alumno_id'])
            nota.instancia_topico_id = int(request.form['instancia_topico_id'])
            nota.nota = float(request.form['nota'])
            
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
    instancias_topico = InstanciaTopico.obtener_todos()
    return render_template('notas/editar.html', nota=nota, alumnos=alumnos, instancias_topico=instancias_topico)

@nota_bp.route('/notas/<int:id>/eliminar', methods=['POST'])
def eliminar_nota(id):
    """Elimina una nota"""
    try:
        Nota.eliminar(id)
        flash('Nota eliminada exitosamente', 'success')
    except Exception as e:
        flash(f'Error al eliminar la nota: {str(e)}', 'error')
    
    return redirect(url_for('nota.listar_notas'))
