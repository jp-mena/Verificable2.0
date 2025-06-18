from flask import Blueprint, request, render_template, redirect, url_for, flash, jsonify, make_response
from sga.models.reporte import Reporte
from sga.models.alumno import Alumno
from datetime import datetime
import csv
import io

reporte_bp = Blueprint('reporte', __name__)

@reporte_bp.route('/reportes')
def index_reportes():
    return render_template('reportes/index.html')

@reporte_bp.route('/reportes/instancia-topico', methods=['GET', 'POST'])
def reporte_instancia_topico():
    if request.method == 'POST':
        try:
            if 'instancia_topico_id' not in request.form or not request.form['instancia_topico_id'].strip():
                flash('Debe seleccionar una instancia de tópico', 'error')
                return redirect(url_for('reporte.reporte_instancia_topico'))
            
            try:
                instancia_topico_id = int(request.form['instancia_topico_id'])
                if instancia_topico_id <= 0:
                    raise ValueError("ID debe ser positivo")
            except (ValueError, TypeError):
                flash('ID de instancia de tópico inválido', 'error')
                return redirect(url_for('reporte.reporte_instancia_topico'))
            
            formato = request.form.get('formato', 'html')
            if formato not in ['html', 'csv']:
                formato = 'html'
            
            notas = Reporte.obtener_notas_instancia_topico(instancia_topico_id)
            
            if not notas:
                flash('No se encontraron notas para la instancia de tópico seleccionada', 'warning')
                return redirect(url_for('reporte.reporte_instancia_topico'))
            
            contexto = notas[0] if notas else {}
            
            if formato == 'csv':
                return _generar_csv_instancia_topico(notas, contexto)
            
            return render_template('reportes/instancia_topico_resultado.html', 
                                 notas=notas, 
                                 contexto=contexto)
                                 
        except ValueError as ve:
            flash(f'Error de validación: {str(ve)}', 'error')
        except Exception as e:
            flash(f'Error inesperado al generar el reporte: {str(e)}', 'error')
    
    instancias_disponibles = Reporte.obtener_instancias_topico_disponibles()
    return render_template('reportes/instancia_topico.html', 
                         instancias_disponibles=instancias_disponibles)

@reporte_bp.route('/reportes/notas-finales-seccion', methods=['GET', 'POST'])
def reporte_notas_finales_seccion():
    """Reporte de notas finales de una sección de curso cerrado"""
    if request.method == 'POST':
        try:
            if 'instancia_curso_id' not in request.form or not request.form['instancia_curso_id'].strip():
                flash('Debe seleccionar un curso', 'error')
                return redirect(url_for('reporte.reporte_notas_finales_seccion'))
            
            if 'seccion_numero' not in request.form or not request.form['seccion_numero'].strip():
                flash('Debe seleccionar una sección', 'error')
                return redirect(url_for('reporte.reporte_notas_finales_seccion'))
            
            try:
                instancia_curso_id = int(request.form['instancia_curso_id'])
                seccion_numero = int(request.form['seccion_numero'])
                if instancia_curso_id <= 0 or seccion_numero <= 0:
                    raise ValueError("Los IDs deben ser positivos")
            except (ValueError, TypeError):
                flash('Los datos del curso y sección deben ser números válidos', 'error')
                return redirect(url_for('reporte.reporte_notas_finales_seccion'))
            
            formato = request.form.get('formato', 'html')
            if formato not in ['html', 'csv']:
                formato = 'html'
            
            notas = Reporte.obtener_notas_finales_seccion(instancia_curso_id, seccion_numero)
            if not notas:
                flash('No se encontraron notas finales para la sección seleccionada', 'warning')
                return redirect(url_for('reporte.reporte_notas_finales_seccion'))
            
            seccion_info = notas[0] if notas else {}
            estadisticas = Reporte.calcular_estadisticas_seccion(notas)
            
            if formato == 'csv':
                return _generar_csv_notas_finales(notas, seccion_info)
            
            return render_template('reportes/notas_finales_resultado.html', 
                                 notas=notas, 
                                 seccion_info=seccion_info,
                                 estadisticas=estadisticas)
        except ValueError:
            flash('Error en los datos seleccionados', 'error')
        except Exception as e:
            flash(f'Error al generar el reporte: {str(e)}', 'error')
    
    cursos_cerrados = Reporte.obtener_cursos_cerrados()
    return render_template('reportes/notas_finales_seccion.html', 
                         cursos_cerrados=cursos_cerrados)

@reporte_bp.route('/reportes/certificado-notas', methods=['GET', 'POST'])
def reporte_certificado_notas():
    """Certificado de notas de un alumno - todos los cursos cerrados"""
    if request.method == 'POST':
        try:
            if 'alumno_id' not in request.form or not request.form['alumno_id'].strip():
                flash('Debe seleccionar un alumno', 'error')
                return redirect(url_for('reporte.reporte_certificado_notas'))
            
            try:
                alumno_id = int(request.form['alumno_id'])
                if alumno_id <= 0:
                    raise ValueError("ID debe ser positivo")
            except (ValueError, TypeError):
                flash('ID de alumno inválido', 'error')
                return redirect(url_for('reporte.reporte_certificado_notas'))
            
            formato = request.form.get('formato', 'html')
            if formato not in ['html', 'csv']:
                formato = 'html'
            
            alumno = Alumno.obtener_por_id(alumno_id)
            if not alumno:
                flash('Alumno no encontrado', 'error')
                return redirect(url_for('reporte.reporte_certificado_notas'))
            
            certificado = Reporte.obtener_certificado_notas_alumno(alumno_id)
            
            if not certificado:
                flash('El alumno seleccionado no tiene cursos cerrados', 'warning')
                return redirect(url_for('reporte.reporte_certificado_notas'))
            
            estadisticas = Reporte.calcular_estadisticas_alumno(certificado)
            
            if formato == 'csv':
                return _generar_csv_certificado(certificado, alumno)
            
            return render_template('reportes/certificado_resultado.html', 
                                 notas=certificado, 
                                 alumno_info=alumno,
                                 estadisticas=estadisticas,
                                 fecha_generacion=datetime.now().strftime('%d/%m/%Y %H:%M'))
                                 
        except ValueError:
            flash('Error en los datos seleccionados', 'error')
        except Exception as e:
            flash(f'Error al generar el reporte: {str(e)}', 'error')
    alumnos = Alumno.obtener_todos()
    return render_template('reportes/certificado_notas.html', 
                         alumnos_disponibles=alumnos)

@reporte_bp.route('/api/reportes/secciones/<int:instancia_curso_id>')
def api_obtener_secciones(instancia_curso_id):
    try:
        secciones = Reporte.obtener_secciones_curso_cerrado(instancia_curso_id)
        return jsonify(secciones)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def _generar_csv_instancia_topico(notas, contexto):
    """Genera archivo CSV para reporte de instancia de tópico"""
    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow([f"Reporte de Notas - {contexto.get('instancia_topico_nombre', '')}"])
    writer.writerow([f"Curso: {contexto.get('curso_codigo', '')} - {contexto.get('curso_nombre', '')}"])
    writer.writerow([f"Período: {contexto.get('anio', '')}{contexto.get('semestre', ''):02d} - Sección {contexto.get('seccion_numero', '')}"])
    writer.writerow([f"Evaluación: {contexto.get('evaluacion_nombre', '')} ({contexto.get('porcentaje_evaluacion', '')}%)"])
    writer.writerow([f"Tópico: {contexto.get('topico_nombre', '')} - Peso: {contexto.get('peso_topico', '')}%"])
    writer.writerow([f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}"])
    writer.writerow([])  # Línea vacía
    
    writer.writerow(['Alumno', 'Correo', 'Nota'])
    
    for nota in notas:
        writer.writerow([
            nota['alumno_nombre'],
            nota['alumno_correo'],
            nota['nota']
        ])
    
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = f'attachment; filename=reporte_instancia_topico_{datetime.now().strftime("%Y%m%d_%H%M")}.csv'
    return response

def _generar_csv_notas_finales(notas_finales, contexto):
    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow([f"Reporte de Notas Finales"])
    writer.writerow([f"Curso: {contexto.get('curso_codigo', '')} - {contexto.get('curso_nombre', '')}"])
    writer.writerow([f"Período: {contexto.get('anio', '')}{contexto.get('semestre', ''):02d} - Sección {contexto.get('seccion_numero', '')}"])
    writer.writerow([f"Fecha de cierre: {contexto.get('fecha_cierre', '')}"])
    writer.writerow([f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}"])
    writer.writerow([])
    
    writer.writerow(['Alumno', 'Correo', 'Nota Final', 'Fecha Cálculo'])
    
    for nota in notas_finales:
        writer.writerow([
            nota['alumno_nombre'],
            nota['alumno_correo'],
            nota['nota_final'],
            nota['fecha_calculo']
        ])
    
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = f'attachment; filename=notas_finales_{datetime.now().strftime("%Y%m%d_%H%M")}.csv'
    return response

def _generar_csv_certificado(certificado, alumno):
    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow([f"Certificado de Notas"])
    writer.writerow([f"Alumno: {alumno['nombre']}"])
    writer.writerow([f"Correo: {alumno['correo']}"])
    writer.writerow([f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}"])
    writer.writerow([])
    
    writer.writerow(['Curso', 'Nombre del Curso', 'Período', 'Sección', 'Nota Final', 'Estado', 'Fecha Cierre'])

    for curso in certificado:
        writer.writerow([
            curso['curso_codigo'],
            curso['curso_nombre'],
            f"{curso['anio']}{curso['semestre']:02d}",
            curso['seccion_numero'],
            curso['nota_final'],
            curso['estado'],
            curso['fecha_cierre']
        ])
    
    output.seek(0)
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = f'attachment; filename=certificado_notas_{alumno["nombre"].replace(" ", "_")}_{datetime.now().strftime("%Y%m%d_%H%M")}.csv'
    return response

@reporte_bp.route('/reportes/exportar/instancia-topico/<int:instancia_topico_id>')
def exportar_instancia_topico_csv(instancia_topico_id):
    try:
        notas = Reporte.obtener_notas_instancia_topico(instancia_topico_id)
        if not notas:
            flash('No se encontraron datos para exportar', 'warning')
            return redirect(url_for('reporte.reporte_instancia_topico'))
        
        contexto = notas[0]
        return _generar_csv_instancia_topico(notas, contexto)
    except Exception as e:
        flash(f'Error al exportar: {str(e)}', 'error')
        return redirect(url_for('reporte.reporte_instancia_topico'))

@reporte_bp.route('/reportes/exportar/notas-finales/<int:seccion_id>')
def exportar_notas_finales_csv(seccion_id):
    try:
        from sga.models.seccion import Seccion
        seccion = Seccion.obtener_por_id(seccion_id)
        if not seccion:
            flash('Sección no encontrada', 'error')
            return redirect(url_for('reporte.notas_finales_seccion'))
        
        notas = Reporte.obtener_notas_finales_seccion(seccion.instancia_id, seccion.numero)
        if not notas:
            flash('No se encontraron datos para exportar', 'warning')
            return redirect(url_for('reporte.notas_finales_seccion'))
        
        seccion_info = notas[0]
        return _generar_csv_notas_finales(notas, seccion_info)
    except Exception as e:
        flash(f'Error al exportar: {str(e)}', 'error')
        return redirect(url_for('reporte.notas_finales_seccion'))

@reporte_bp.route('/reportes/exportar/certificado/<int:alumno_id>')
def exportar_certificado_csv(alumno_id):
    try:
        alumno = Alumno.obtener_por_id(alumno_id)
        if not alumno:
            flash('Alumno no encontrado', 'error')
            return redirect(url_for('reporte.certificado_notas'))
        
        certificado = Reporte.obtener_certificado_notas_alumno(alumno_id)
        if not certificado:
            flash('No se encontraron datos para exportar', 'warning')
            return redirect(url_for('reporte.certificado_notas'))
        
        return _generar_csv_certificado(certificado, alumno)
    except Exception as e:
        flash(f'Error al exportar: {str(e)}', 'error')
        return redirect(url_for('reporte.certificado_notas'))
