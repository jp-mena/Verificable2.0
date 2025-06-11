# filepath: routes/topico_routes.py
from flask import Blueprint, request, render_template, redirect, url_for, flash, jsonify
from models.topico import Topico

topico_bp = Blueprint('topico', __name__)

@topico_bp.route('/topicos')
def listar_topicos():
    """Lista todos los tópicos"""
    topicos = Topico.obtener_todos()
    return render_template('topicos/listar.html', topicos=topicos)

@topico_bp.route('/topicos/crear', methods=['GET', 'POST'])
def crear_topico():
    """Crea un nuevo tópico"""
    if request.method == 'POST':
        try:
            nombre = request.form['nombre'].strip()
            tipo = request.form['tipo'].strip()
            
            # Validaciones básicas
            if not nombre:
                flash('El nombre del tópico es requerido', 'error')
                return redirect(url_for('topico.crear_topico'))
            
            if not tipo:
                flash('El tipo del tópico es requerido', 'error')
                return redirect(url_for('topico.crear_topico'))
            
            Topico.crear(nombre, tipo)
            flash('Tópico creado exitosamente', 'success')
            return redirect(url_for('topico.listar_topicos'))
            
        except Exception as e:
            flash(f'Error al crear el tópico: {str(e)}', 'error')
    
    return render_template('topicos/crear.html')

@topico_bp.route('/topicos/<int:id>/editar', methods=['GET', 'POST'])
def editar_topico(id):
    """Edita un tópico"""
    topico = Topico.obtener_por_id(id)
    if not topico:
        flash('Tópico no encontrado', 'error')
        return redirect(url_for('topico.listar_topicos'))
    
    if request.method == 'POST':
        try:
            topico.nombre = request.form['nombre'].strip()
            topico.tipo = request.form['tipo'].strip()
            
            # Validaciones básicas
            if not topico.nombre:
                flash('El nombre del tópico es requerido', 'error')
                return redirect(url_for('topico.editar_topico', id=id))
            
            if not topico.tipo:
                flash('El tipo del tópico es requerido', 'error')
                return redirect(url_for('topico.editar_topico', id=id))
            
            topico.actualizar()
            flash('Tópico actualizado exitosamente', 'success')
            return redirect(url_for('topico.listar_topicos'))
            
        except Exception as e:
            flash(f'Error al actualizar el tópico: {str(e)}', 'error')
    
    return render_template('topicos/editar.html', topico=topico)

@topico_bp.route('/topicos/<int:id>/eliminar', methods=['POST'])
def eliminar_topico(id):
    """Elimina un tópico"""
    try:
        Topico.eliminar(id)
        flash('Tópico eliminado exitosamente', 'success')
    except Exception as e:
        flash(f'Error al eliminar el tópico: {str(e)}', 'error')
    
    return redirect(url_for('topico.listar_topicos'))
