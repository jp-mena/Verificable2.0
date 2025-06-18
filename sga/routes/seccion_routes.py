from flask import Blueprint, request, render_template, redirect, url_for, flash, jsonify
from sga.models.seccion import Seccion
from sga.models.instancia_curso import InstanciaCurso
from sga.models.profesor import Profesor
from sga.models.sala import Sala
from sga.db.database import execute_query

seccion_bp = Blueprint('seccion', __name__)

def _verificar_instancia_curso_cerrada(instancia_id):
    query = "SELECT cerrado FROM instancias_curso WHERE id = ?"
    res = execute_query(query, (instancia_id,))
    return bool(res[0][0]) if res else False

@seccion_bp.route('/secciones')
def listar_secciones():
    secciones = Seccion.obtener_todos()
    return render_template('secciones/listar.html', secciones=secciones)

@seccion_bp.route('/secciones/crear', methods=['GET', 'POST'])
def crear_seccion():
    if request.method == 'POST':
        try:
            numero = int(request.form['numero'])
            instancia_id = int(request.form['instancia_id'])
            profesor_id = request.form.get('profesor_id')
            sala_id = request.form.get('sala_id')
            profesor_id = int(profesor_id) if profesor_id else None
            sala_id = int(sala_id) if sala_id else None
            if _verificar_instancia_curso_cerrada(instancia_id):
                flash('La instancia está cerrada', 'error')
                return redirect(url_for('seccion.crear_seccion'))
            if numero <= 0:
                flash('Número inválido', 'error')
                return redirect(url_for('seccion.crear_seccion'))
            for s in Seccion.obtener_todos():
                if s['instancia_id'] == instancia_id and s['numero'] == numero:
                    flash('Número repetido', 'error')
                    return redirect(url_for('seccion.crear_seccion'))
            Seccion.crear(numero, instancia_id, profesor_id, sala_id)
            flash('Sección creada', 'success')
            return redirect(url_for('seccion.listar_secciones'))
        except Exception:
            flash('Error al crear', 'error')
            return redirect(url_for('seccion.crear_seccion'))
    instancias = [i for i in InstanciaCurso.obtener_todos() if not i['cerrado']]
    profesores = [{'id': p[0], 'nombre': p[1], 'correo': p[2]} for p in Profesor.get_all()]
    salas = Sala.obtener_todas()
    return render_template('secciones/crear.html', instancias=instancias, profesores=profesores, salas=salas)

@seccion_bp.route('/secciones/<int:id>/editar', methods=['GET', 'POST'])
def editar_seccion(id):
    seccion = Seccion.obtener_por_id(id)
    if not seccion:
        flash('No encontrada', 'error')
        return redirect(url_for('seccion.listar_secciones'))
    if _verificar_instancia_curso_cerrada(seccion.instancia_id):
        flash('Instancia cerrada', 'error')
        return redirect(url_for('seccion.listar_secciones'))
    if request.method == 'POST':
        try:
            seccion.numero = int(request.form['numero'])
            nuevo_inst = int(request.form['instancia_id'])
            profesor_id = request.form.get('profesor_id')
            sala_id = request.form.get('sala_id')
            seccion.profesor_id = int(profesor_id) if profesor_id else None
            seccion.sala_id = int(sala_id) if sala_id else None
            if _verificar_instancia_curso_cerrada(nuevo_inst):
                flash('Instancia destino cerrada', 'error')
                return redirect(url_for('seccion.editar_seccion', id=id))
            seccion.instancia_id = nuevo_inst
            if seccion.numero <= 0:
                flash('Número inválido', 'error')
                return redirect(url_for('seccion.editar_seccion', id=id))
            seccion.actualizar()
            flash('Sección actualizada', 'success')
            return redirect(url_for('seccion.listar_secciones'))
        except Exception:
            flash('Error al actualizar', 'error')
            return redirect(url_for('seccion.editar_seccion', id=id))
    instancias = [i for i in InstanciaCurso.obtener_todos() if not i['cerrado']]
    profesores = [{'id': p[0], 'nombre': p[1], 'correo': p[2]} for p in Profesor.get_all()]
    salas = Sala.obtener_todas()
    return render_template('secciones/editar.html', seccion=seccion, instancias=instancias, profesores=profesores, salas=salas)

@seccion_bp.route('/secciones/<int:id>/eliminar', methods=['POST'])
def eliminar_seccion(id):
    seccion = Seccion.obtener_por_id(id)
    if not seccion:
        flash('No encontrada', 'error')
        return redirect(url_for('seccion.listar_secciones'))
    if _verificar_instancia_curso_cerrada(seccion.instancia_id):
        flash('Instancia cerrada', 'error')
        return redirect(url_for('seccion.listar_secciones'))
    Seccion.eliminar(id)
    flash('Sección eliminada', 'success')
    return redirect(url_for('seccion.listar_secciones'))

@seccion_bp.route('/api/secciones/profesores-disponibles/<int:instancia_id>')
def obtener_profesores_disponibles(instancia_id):
    try:
        return jsonify({'profesores': Seccion.obtener_profesores_disponibles(instancia_id)}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
