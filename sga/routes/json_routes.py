from flask import Blueprint, request, render_template, redirect, url_for, flash, jsonify
import json
import os
from sga.models.curso import Curso
from sga.models.profesor import Profesor
from sga.models.alumno import Alumno
from sga.models.instancia_curso import InstanciaCurso
from sga.models.seccion import Seccion
from sga.models.evaluacion import Evaluacion
from sga.models.topico import Topico
from sga.models.instancia_topico import InstanciaTopico
from sga.models.nota import Nota
from sga.models.inscripcion import Inscripcion

json_bp = Blueprint('json_load', __name__)

EJEMPLOS_JSON = {
    'cursos': [
        {
            "codigo": "ICC5130",
            "nombre": "Programación Orientada a Objetos",
            "requisitos": "Programación I"
        },
        {
            "codigo": "MAT1001", 
            "nombre": "Matemáticas I",
            "requisitos": ""
        }
    ],
    'profesores': [
        {
            "nombre": "Dr. Juan Pérez",
            "correo": "juan.perez@universidad.cl"
        },
        {
            "nombre": "Dra. María González",
            "correo": "maria.gonzalez@universidad.cl"
        }
    ],
    'alumnos': [
        {
            "nombre": "Ana Silva",
            "correo": "ana.silva@student.cl",
            "fecha_ingreso": "2024-03-01"
        },
        {
            "nombre": "Carlos Rojas",
            "correo": "carlos.rojas@student.cl",
            "fecha_ingreso": "2024-03-01"
        }
    ],
    'instancias_curso': [
        {
            "semestre": 1,
            "anio": 2025,
            "curso_codigo": "ICC5130"
        },
        {
            "semestre": 2,
            "anio": 2025,
            "curso_codigo": "MAT1001"
        }
    ],
    'secciones': [
        {
            "numero": 1,
            "curso_codigo": "ICC5130",
            "semestre": 1,
            "anio": 2025,
            "profesor_correo": "juan.perez@universidad.cl"
        }
    ],
    'topicos': [
        {
            "nombre": "Control",
            "tipo": "control"
        },
        {
            "nombre": "Tarea",
            "tipo": "tarea"
        }
    ],
    'evaluaciones': [
        {
            "nombre": "Controles",
            "porcentaje": 40,
            "curso_codigo": "ICC5130",
            "semestre": 1,
            "anio": 2025,
            "seccion_numero": 1
        }
    ],
    'instancias_topico': [
        {
            "nombre": "Control 1",
            "peso": 50,
            "topico_nombre": "Control",
            "evaluacion_nombre": "Controles",
            "curso_codigo": "ICC5130",
            "semestre": 1,
            "anio": 2025
        }
    ],
    'inscripciones': [
        {
            "alumno_correo": "ana.silva@student.cl",
            "curso_codigo": "ICC5130",
            "semestre": 1,
            "anio": 2025,
            "fecha_inscripcion": "2024-12-01"
        }
    ],
    'notas': [
        {
            "alumno_correo": "ana.silva@student.cl",
            "instancia_topico_nombre": "Control 1",
            "evaluacion_nombre": "Controles",
            "curso_codigo": "ICC5130",
            "semestre": 1,
            "anio": 2025,
            "nota": 6.5
        }
    ]
}

@json_bp.route('/cargar-json')
def mostrar_carga():
    return render_template('json/index.html')

@json_bp.route('/cargar-json/<entidad>')
def mostrar_carga_entidad(entidad):
    entidades_validas = list(EJEMPLOS_JSON.keys())
    
    if entidad not in entidades_validas:
        flash('Entidad no válida', 'error')
        return redirect(url_for('json_load.mostrar_carga'))
    
    ejemplo_json = EJEMPLOS_JSON[entidad]
    return render_template('json/cargar_entidad.html', 
                         entidad=entidad, 
                         ejemplo_json=json.dumps(ejemplo_json, indent=2, ensure_ascii=False),
                         entidades_validas=entidades_validas)


@json_bp.route('/api/validar-json', methods=['POST'])
def api_validar_json():
    try:
        if not request.is_json:
            return jsonify({'error': 'Content-Type debe ser application/json'}), 400
        
        datos = request.get_json()
        if not datos:
            return jsonify({'error': 'No se recibieron datos JSON'}), 400
        
        entidades_validas = ['cursos', 'profesores', 'alumnos', 'instancias_curso', 
                           'secciones', 'topicos', 'evaluaciones', 'instancias_topico', 'notas']
        
        entidades_encontradas = []
        errores = []
        
        for key in datos.keys():
            if key in entidades_validas:
                entidades_encontradas.append(key)
                if not isinstance(datos[key], list):
                    errores.append(f"'{key}' debe ser una lista")
            else:
                errores.append(f"Entidad desconocida: '{key}'")
        
        conteos = {}
        for entidad in entidades_encontradas:
            conteos[entidad] = len(datos[entidad])
        
        return jsonify({
            'valido': len(errores) == 0,
            'entidades_encontradas': entidades_encontradas,
            'conteos': conteos,
            'errores': errores
        }), 200
        
    except json.JSONDecodeError:
        return jsonify({'error': 'JSON inválido'}), 400
    except Exception as e:
        return jsonify({'error': f'Error validando JSON: {str(e)}'}), 500

@json_bp.route('/cargar-json/<entidad>/procesar', methods=['POST'])
def procesar_carga_entidad(entidad):
    entidades_validas = list(EJEMPLOS_JSON.keys())
    
    if entidad not in entidades_validas:
        flash('Entidad no válida', 'error')
        return redirect(url_for('json_load.mostrar_carga'))
    
    try:
        if 'archivo_json' in request.files:
            archivo = request.files['archivo_json']
            if archivo.filename != '':
                contenido = archivo.read().decode('utf-8')
                datos = json.loads(contenido)
            else:
                flash('No se seleccionó ningún archivo', 'error')
                return redirect(url_for('json_load.mostrar_carga_entidad', entidad=entidad))
        else:
            contenido_texto = request.form.get('datos_json', '').strip()
            if not contenido_texto:
                flash('No se proporcionaron datos JSON', 'error')
                return redirect(url_for('json_load.mostrar_carga_entidad', entidad=entidad))
            datos = json.loads(contenido_texto)
        
        if not isinstance(datos, list):
            flash('El JSON debe contener una lista de objetos', 'error')
            return redirect(url_for('json_load.mostrar_carga_entidad', entidad=entidad))
        
        resultado = procesar_entidad_especifica(entidad, datos)
        
        flash(f'Carga de {entidad} completada: {resultado}', 'success')
        return redirect(url_for('json_load.mostrar_carga'))
        
    except json.JSONDecodeError as e:
        flash(f'Error: El JSON no es válido - {str(e)}', 'error')
    except Exception as e:
        flash(f'Error al procesar los datos: {str(e)}', 'error')
    
    return redirect(url_for('json_load.mostrar_carga_entidad', entidad=entidad))

def procesar_entidad_especifica(entidad, datos):

    procesadores = {
        'cursos': _procesar_cursos,
        'profesores': _procesar_profesores,
        'alumnos': _procesar_alumnos,
        'instancias_curso': _procesar_instancias_curso,
        'secciones': _procesar_secciones,
        'topicos': _procesar_topicos,
        'evaluaciones': _procesar_evaluaciones,
        'instancias_topico': _procesar_instancias_topico,
        'inscripciones': _procesar_inscripciones,
        'notas': _procesar_notas
    }
    
    if entidad not in procesadores:
        return f"Error: Entidad '{entidad}' no soportada"
    
    try:
        return procesadores[entidad](datos)
    except Exception as e:
        return f"Error general procesando {entidad}: {str(e)}"


def _procesar_cursos(datos):
    total_procesados = 0
    errores = 0
    
    for item in datos:
        try:
            curso = Curso(
                item['codigo'], 
                item['nombre'], 
                item.get('creditos', 4), 
                item.get('requisitos', '')
            )
            curso.save()
            total_procesados += 1
        except Exception as e:
            if "Duplicate entry" not in str(e):
                print(f"Error creando curso: {e}")
                errores += 1
    
    return f"{total_procesados} cursos creados, {errores} errores"


def _procesar_profesores(datos):
    total_procesados = 0
    errores = 0
    
    for item in datos:
        try:
            Profesor.crear(item['nombre'], item['correo'])
            total_procesados += 1
        except Exception as e:
            if "Duplicate entry" not in str(e):
                print(f"Error creando profesor: {e}")
                errores += 1
    
    return f"{total_procesados} profesores creados, {errores} errores"


def _procesar_alumnos(datos):
    total_procesados = 0
    errores = 0
    
    for item in datos:
        try:
            Alumno.crear(item['nombre'], item['correo'], item.get('fecha_ingreso', None))
            total_procesados += 1
        except Exception as e:
            if "Duplicate entry" not in str(e):
                print(f"Error creando alumno: {e}")
                errores += 1
    
    return f"{total_procesados} alumnos creados, {errores} errores"


def _procesar_instancias_curso(datos):
    total_procesados = 0
    errores = 0
    
    for item in datos:
        try:
            curso = Curso.get_by_codigo(item['curso_codigo'])
            if curso:
                InstanciaCurso.crear(item['semestre'], item['anio'], curso.id)
                total_procesados += 1
            else:
                print(f"Curso no encontrado: {item['curso_codigo']}")
                errores += 1
        except Exception as e:
            print(f"Error creando instancia de curso: {e}")
            errores += 1
    
    return f"{total_procesados} instancias de curso creadas, {errores} errores"


def _procesar_secciones(datos):
    total_procesados = 0
    errores = 0
    
    for item in datos:
        try:
            instancia = _buscar_instancia_curso(item['curso_codigo'], item['semestre'], item['anio'])
            profesor = Profesor.obtener_por_correo(item['profesor_correo'])
            
            if instancia and profesor:
                Seccion.crear(item['numero'], instancia.id, profesor.id)
                total_procesados += 1
            else:
                print(f"Instancia o profesor no encontrado para sección {item['numero']}")
                errores += 1
        except Exception as e:
            print(f"Error creando sección: {e}")
            errores += 1
    
    return f"{total_procesados} secciones creadas, {errores} errores"


def _procesar_topicos(datos):
    total_procesados = 0
    errores = 0
    
    for item in datos:
        try:
            Topico.crear(item['nombre'], item.get('tipo', 'control'))
            total_procesados += 1
        except Exception as e:
            if "Duplicate entry" not in str(e):
                print(f"Error creando tópico: {e}")
                errores += 1
    
    return f"{total_procesados} tópicos creados, {errores} errores"


def _procesar_evaluaciones(datos):
    total_procesados = 0
    errores = 0
    
    for item in datos:
        try:
            seccion = _buscar_seccion(
                item['curso_codigo'], 
                item['semestre'], 
                item['anio'], 
                item['seccion_numero']
            )
            
            if seccion:
                Evaluacion.crear(item['nombre'], item['porcentaje'], seccion.id)
                total_procesados += 1
            else:
                print(f"Sección no encontrada para evaluación {item['nombre']}")
                errores += 1
        except Exception as e:
            print(f"Error creando evaluación: {e}")
            errores += 1
    
    return f"{total_procesados} evaluaciones creadas, {errores} errores"


def _procesar_instancias_topico(datos):
    total_procesados = 0
    errores = 0
    
    for item in datos:
        try:
            topico = Topico.obtener_por_nombre(item['topico_nombre'])
            if not topico:
                print(f"Tópico no encontrado: {item['topico_nombre']}")
                errores += 1
                continue
                
            evaluacion = _buscar_evaluacion(
                item['evaluacion_nombre'], 
                item['curso_codigo'], 
                item['semestre'], 
                item['anio']
            )
            if not evaluacion:
                print(f"Evaluación no encontrada: {item['evaluacion_nombre']} para curso {item['curso_codigo']}")
                errores += 1
                continue
            
            InstanciaTopico.crear(item['nombre'], item['peso'], topico.id, evaluacion.id)
            total_procesados += 1
        except Exception as e:
            print(f"Error creando instancia de tópico: {e}")
            errores += 1
    
    return f"{total_procesados} instancias de tópico creadas, {errores} errores"


def _procesar_inscripciones(datos):
    total_procesados = 0
    errores = 0
    
    for item in datos:
        try:
            alumno = Alumno.obtener_por_correo(item['alumno_correo'])
            instancia = _buscar_instancia_curso(item['curso_codigo'], item['semestre'], item['anio'])
            
            if alumno and instancia:
                Inscripcion.crear(alumno.id, instancia.id, item.get('fecha_inscripcion', None))
                total_procesados += 1
            else:
                print(f"Alumno o instancia no encontrado para inscripción")
                errores += 1
        except Exception as e:
            print(f"Error creando inscripción: {e}")
            errores += 1
    
    return f"{total_procesados} inscripciones creadas, {errores} errores"


def _procesar_notas(datos):
    total_procesados = 0
    errores = 0
    
    for item in datos:
        try:
            alumno = Alumno.obtener_por_correo(item['alumno_correo'])
            instancia_topico = _buscar_instancia_topico(
                item['instancia_topico_nombre'], 
                item['evaluacion_nombre'],
                item['curso_codigo'], 
                item['semestre'], 
                item['anio']
            )
            
            if alumno and instancia_topico:
                Nota.crear(alumno.id, instancia_topico.id, item['nota'])
                total_procesados += 1
            else:
                print(f"Alumno o instancia de tópico no encontrado para nota")
                errores += 1
        except Exception as e:
            print(f"Error creando nota: {e}")
            errores += 1
    
    return f"{total_procesados} notas creadas, {errores} errores"

def _buscar_instancia_curso(curso_codigo, semestre, anio):
    try:
        from sga.db.database import execute_query
        query = """
        SELECT ic.id, ic.semestre, ic.anio, ic.curso_id
        FROM instancias_curso ic
        JOIN cursos c ON ic.curso_id = c.id
        WHERE c.codigo = %s AND ic.semestre = %s AND ic.anio = %s
        """
        resultado = execute_query(query, (curso_codigo, semestre, anio))
        if resultado:
            from collections import namedtuple
            InstanciaCurso = namedtuple('InstanciaCurso', ['id', 'semestre', 'anio', 'curso_id'])
            return InstanciaCurso(*resultado[0])
        return None
    except Exception as e:
        print(f"Error buscando instancia de curso: {e}")
        return None

def _buscar_seccion(curso_codigo, semestre, anio, numero):
    try:
        from sga.db.database import execute_query
        query = """
        SELECT s.id, s.numero, s.instancia_id, s.profesor_id
        FROM secciones s
        JOIN instancias_curso ic ON s.instancia_id = ic.id
        JOIN cursos c ON ic.curso_id = c.id
        WHERE c.codigo = %s AND ic.semestre = %s AND ic.anio = %s AND s.numero = %s
        """
        resultado = execute_query(query, (curso_codigo, semestre, anio, numero))
        if resultado:
            from collections import namedtuple
            Seccion = namedtuple('Seccion', ['id', 'numero', 'instancia_id', 'profesor_id'])
            return Seccion(*resultado[0])
        return None
    except Exception as e:
        print(f"Error buscando sección: {e}")
        return None

def _buscar_evaluacion(nombre, curso_codigo, semestre, anio):
    try:
        from sga.db.database import execute_query
        query = """
        SELECT e.id, e.nombre, e.porcentaje, e.seccion_id
        FROM evaluaciones e
        JOIN secciones s ON e.seccion_id = s.id
        JOIN instancias_curso ic ON s.instancia_id = ic.id
        JOIN cursos c ON ic.curso_id = c.id
        WHERE e.nombre = %s AND c.codigo = %s AND ic.semestre = %s AND ic.anio = %s
        """
        resultado = execute_query(query, (nombre, curso_codigo, semestre, anio))
        if resultado:
            from collections import namedtuple
            Evaluacion = namedtuple('Evaluacion', ['id', 'nombre', 'porcentaje', 'seccion_id'])
            return Evaluacion(*resultado[0])
        return None
    except Exception as e:
        print(f"Error buscando evaluación: {e}")
        return None

def _buscar_instancia_topico(nombre, evaluacion_nombre, curso_codigo, semestre, anio):
    try:
        from sga.db.database import execute_query
        query = """
        SELECT it.id, it.nombre, it.peso, it.topico_id, it.evaluacion_id
        FROM instancias_topico it
        JOIN evaluaciones e ON it.evaluacion_id = e.id
        JOIN secciones s ON e.seccion_id = s.id
        JOIN instancias_curso ic ON s.instancia_id = ic.id
        JOIN cursos c ON ic.curso_id = c.id
        WHERE it.nombre = %s AND e.nombre = %s AND c.codigo = %s AND ic.semestre = %s AND ic.anio = %s
        """
        resultado = execute_query(query, (nombre, evaluacion_nombre, curso_codigo, semestre, anio))
        if resultado:
            from collections import namedtuple
            InstanciaTopico = namedtuple('InstanciaTopico', ['id', 'nombre', 'peso', 'topico_id', 'evaluacion_id'])
            return InstanciaTopico(*resultado[0])
        return None
    except Exception as e:
        print(f"Error buscando instancia de tópico: {e}")
        return None
