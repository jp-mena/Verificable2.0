# filepath: routes/instancia_curso_routes.py
from flask import Blueprint, request, render_template, redirect, url_for, flash, jsonify
from models.instancia_curso import InstanciaCurso
from models.curso import Curso

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
        InstanciaCurso.eliminar(id)
        flash('Instancia de curso eliminada exitosamente', 'success')
    except Exception as e:
        flash(f'Error al eliminar la instancia: {str(e)}', 'error')
    
    return redirect(url_for('instancia_curso.listar_instancias'))
