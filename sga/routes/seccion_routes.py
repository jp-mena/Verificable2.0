from flask import Blueprint, request, render_template, redirect, url_for, flash, jsonify
from sga.models.seccion import Seccion
from sga.models.instancia_curso import InstanciaCurso
from sga.models.profesor import Profesor
from sga.db.database import execute_query

seccion_bp = Blueprint('seccion', __name__)

def _verificar_instancia_curso_cerrada(instancia_id):
    query = "SELECT cerrado FROM instancias_curso WHERE id = %s"
    res = execute_query(query, (instancia_id,))
    return bool(res[0][0]) if res else False

def _obtener_secciones_para_listado():
    return Seccion.obtener_todos()

def _renderizar_listado_secciones(secciones):
    return render_template('secciones/listar.html', secciones=secciones)

@seccion_bp.route('/secciones')
def listar_secciones():
    secciones = _obtener_secciones_para_listado()
    return _renderizar_listado_secciones(secciones)

@seccion_bp.route('/secciones/crear', methods=['GET', 'POST'])
def crear_seccion():
    if request.method == 'POST':
        return _procesar_creacion_seccion()
    
    return _mostrar_formulario_crear_seccion()

def _procesar_creacion_seccion():
    try:
        datos_validados = _validar_datos_nueva_seccion()
        _verificar_reglas_negocio_seccion(datos_validados)
        
        Seccion.crear(datos_validados['numero'], datos_validados['instancia_id'], datos_validados['profesor_id'])
        flash('Sección creada', 'success')
        return redirect(url_for('seccion.listar_secciones'))
        
    except Exception as e:
        flash(f'Error al crear: {str(e)}', 'error')
        return redirect(url_for('seccion.crear_seccion'))

def _validar_datos_nueva_seccion():
    numero = int(request.form['numero'])
    instancia_id = int(request.form['instancia_id'])
    profesor_id = request.form.get('profesor_id')
    profesor_id = int(profesor_id) if profesor_id else None
    
    return {
        'numero': numero,
        'instancia_id': instancia_id,
        'profesor_id': profesor_id
    }

def _verificar_reglas_negocio_seccion(datos):
    if _verificar_instancia_curso_cerrada(datos['instancia_id']):
        raise ValueError('La instancia está cerrada')
    
    if datos['numero'] <= 0:
        raise ValueError('Número inválido')
    
    if _verificar_numero_seccion_duplicado(datos['instancia_id'], datos['numero']):
        raise ValueError('Número repetido')

def _verificar_numero_seccion_duplicado(instancia_id, numero):
    secciones_existentes = Seccion.obtener_todos()
    return any(s['instancia_id'] == instancia_id and s['numero'] == numero 
              for s in secciones_existentes)

def _mostrar_formulario_crear_seccion():
    instancias = _obtener_instancias_abiertas()
    profesores = _obtener_profesores_disponibles()
    return render_template('secciones/crear.html', instancias=instancias, profesores=profesores)

def _obtener_instancias_abiertas():
    return [i for i in InstanciaCurso.obtener_todos() if not i['cerrado']]

def _obtener_profesores_disponibles():
    return [{'id': p[0], 'nombre': p[1], 'correo': p[2]} for p in Profesor.get_all()]

@seccion_bp.route('/secciones/<int:id>/editar', methods=['GET', 'POST'])
def editar_seccion(id):
    seccion = _validar_seccion_editable(id)
    
    if request.method == 'POST':
        return _procesar_edicion_seccion(seccion, id)
    
    return _mostrar_formulario_editar_seccion(seccion)

def _validar_seccion_editable(id):
    seccion = Seccion.obtener_por_id(id)
    if not seccion:
        flash('No encontrada', 'error')
        raise Exception('Sección no encontrada')
    
    if _verificar_instancia_curso_cerrada(seccion.instancia_id):
        flash('Instancia cerrada', 'error')
        raise Exception('Instancia cerrada')
    
    return seccion

def _procesar_edicion_seccion(seccion, id):
    try:
        datos_validados = _validar_datos_edicion_seccion()
        _actualizar_seccion_con_datos(seccion, datos_validados)
        
        flash('Sección actualizada', 'success')
        return redirect(url_for('seccion.listar_secciones'))
        
    except Exception as e:
        flash(f'Error al actualizar: {str(e)}', 'error')
        return redirect(url_for('seccion.editar_seccion', id=id))

def _validar_datos_edicion_seccion():
    numero = int(request.form['numero'])
    nuevo_inst = int(request.form['instancia_id'])
    profesor_id = request.form.get('profesor_id')
    profesor_id = int(profesor_id) if profesor_id else None
    
    _verificar_reglas_edicion_seccion(numero, nuevo_inst)
    
    return {
        'numero': numero,
        'instancia_id': nuevo_inst,
        'profesor_id': profesor_id
    }

def _verificar_reglas_edicion_seccion(numero, instancia_id):
    if _verificar_instancia_curso_cerrada(instancia_id):
        raise ValueError('Instancia destino cerrada')
    
    if numero <= 0:
        raise ValueError('Número inválido')

def _actualizar_seccion_con_datos(seccion, datos_validados):
    seccion.numero = datos_validados['numero']
    seccion.instancia_id = datos_validados['instancia_id']
    seccion.profesor_id = datos_validados['profesor_id']
    seccion.actualizar()

def _mostrar_formulario_editar_seccion(seccion):
    instancias = _obtener_instancias_abiertas()
    profesores = _obtener_profesores_disponibles()
    return render_template('secciones/editar.html', 
                         seccion=seccion, 
                         instancias=instancias, 
                         profesores=profesores)

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
