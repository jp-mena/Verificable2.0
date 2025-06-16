# filepath: routes/json_routes.py
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

json_bp = Blueprint('json_load', __name__)

@json_bp.route('/cargar-json')
def mostrar_carga():
    """Muestra la página de carga de JSON"""
    return render_template('json/cargar.html')

@json_bp.route('/cargar-json/procesar', methods=['POST'])
def procesar_json():
    """Procesa la carga masiva desde JSON"""
    try:
        # Verificar si se subió un archivo
        if 'archivo_json' in request.files:
            archivo = request.files['archivo_json']
            if archivo.filename != '':
                contenido = archivo.read().decode('utf-8')
                datos = json.loads(contenido)
            else:
                flash('No se seleccionó ningún archivo', 'error')
                return redirect(url_for('json_load.mostrar_carga'))
        else:
            # Usar datos de ejemplo
            datos = cargar_datos_ejemplo()
        
        # Procesar los datos
        resultado = procesar_datos_json(datos)
        
        flash(f'Carga completada: {resultado}', 'success')
        return redirect(url_for('index'))
        
    except json.JSONDecodeError:
        flash('Error: El archivo no es un JSON válido', 'error')
    except Exception as e:
        flash(f'Error al procesar los datos: {str(e)}', 'error')
    
    return redirect(url_for('json_load.mostrar_carga'))

def cargar_datos_ejemplo():
    """Carga datos de ejemplo desde archivo local"""
    try:
        ruta_ejemplo = 'data/json_examples/datos_ejemplo.json'
        if os.path.exists(ruta_ejemplo):
            with open(ruta_ejemplo, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:            # Datos de ejemplo integrados
            return {
                "cursos": [
                    {"codigo": "ICS1113", "nombre": "Programación", "requisitos": ""},
                    {"codigo": "ICS2122", "nombre": "Algoritmos y Estructuras de Datos", "requisitos": "ICS1113"},
                    {"codigo": "MAT1610", "nombre": "Matemáticas I", "requisitos": ""},
                    {"codigo": "MAT1620", "nombre": "Matemáticas II", "requisitos": "MAT1610"},
                    {"codigo": "ICS2523", "nombre": "Ingeniería de Software", "requisitos": "ICS2122"},
                    {"codigo": "FIS1500", "nombre": "Física I", "requisitos": "MAT1610"},
                    {"codigo": "QUI1100", "nombre": "Química General", "requisitos": ""},
                    {"codigo": "IEE2153", "nombre": "Circuitos Eléctricos", "requisitos": "FIS1500, MAT1620"},
                    {"codigo": "ICS3413", "nombre": "Base de Datos", "requisitos": "ICS2122"},
                    {"codigo": "MAT2630", "nombre": "Matemáticas III", "requisitos": "MAT1620"}
                ],
                "profesores": [
                    {"nombre": "Dr. Juan Pérez", "correo": "juan.perez@universidad.cl"},
                    {"nombre": "Dra. María González", "correo": "maria.gonzalez@universidad.cl"},
                    {"nombre": "Mg. Carlos López", "correo": "carlos.lopez@universidad.cl"},
                    {"nombre": "Dr. Ana Martínez", "correo": "ana.martinez@universidad.cl"},
                    {"nombre": "Ing. Pedro Silva", "correo": "pedro.silva@universidad.cl"},
                    {"nombre": "Dra. Laura Fernández", "correo": "laura.fernandez@universidad.cl"},
                    {"nombre": "Dr. Roberto Morales", "correo": "roberto.morales@universidad.cl"},
                    {"nombre": "Mg. Sofía Castro", "correo": "sofia.castro@universidad.cl"},
                    {"nombre": "Dr. Diego Herrera", "correo": "diego.herrera@universidad.cl"},
                    {"nombre": "Dra. Valentina Torres", "correo": "valentina.torres@universidad.cl"}
                ],
                "alumnos": [
                    {"nombre": "Ana Silva", "correo": "ana.silva@student.cl", "fecha_ingreso": "2024-03-01"},
                    {"nombre": "Carlos Rojas", "correo": "carlos.rojas@student.cl", "fecha_ingreso": "2024-03-01"},
                    {"nombre": "María Fernández", "correo": "maria.fernandez@student.cl", "fecha_ingreso": "2024-08-01"},
                    {"nombre": "Diego Morales", "correo": "diego.morales@student.cl", "fecha_ingreso": "2025-03-01"},
                    {"nombre": "Sofía Chen", "correo": "sofia.chen@student.cl", "fecha_ingreso": "2024-03-01"},
                    {"nombre": "Miguel Torres", "correo": "miguel.torres@student.cl", "fecha_ingreso": "2023-08-01"},
                    {"nombre": "Valentina Silva", "correo": "valentina.silva@student.cl", "fecha_ingreso": "2023-08-01"},
                    {"nombre": "Sebastián Vargas", "correo": "sebastian.vargas@student.cl", "fecha_ingreso": "2024-08-01"},
                    {"nombre": "Catalina Ruiz", "correo": "catalina.ruiz@student.cl", "fecha_ingreso": "2024-03-01"},
                    {"nombre": "Andrés Mendoza", "correo": "andres.mendoza@student.cl", "fecha_ingreso": "2025-03-01"}
                ]
            }
    except Exception:
        return {}

def procesar_datos_json(datos):
    """Procesa los datos JSON y los inserta en la base de datos"""
    resultado = []
    contadores = {"cursos": 0, "profesores": 0, "alumnos": 0, "instancias": 0, "secciones": 0, "topicos": 0, "evaluaciones": 0, "instancias_topico": 0, "notas": 0}
    
    # 1. Crear cursos
    if 'cursos' in datos:
        for curso_data in datos['cursos']:
            try:
                Curso.crear(curso_data['codigo'], curso_data['nombre'], curso_data.get('requisitos', ''))
                contadores["cursos"] += 1
            except Exception as e:
                resultado.append(f"Error creando curso {curso_data['codigo']}: {str(e)}")
    
    # 2. Crear profesores
    if 'profesores' in datos:
        for profesor_data in datos['profesores']:
            try:
                Profesor.crear(profesor_data['nombre'], profesor_data['correo'])
                contadores["profesores"] += 1
            except Exception as e:
                resultado.append(f"Error creando profesor {profesor_data['nombre']}: {str(e)}")
      # 3. Crear alumnos
    if 'alumnos' in datos:
        for alumno_data in datos['alumnos']:
            try:
                Alumno.crear(alumno_data['nombre'], alumno_data['correo'], alumno_data['fecha_ingreso'])
                contadores["alumnos"] += 1
            except Exception as e:
                resultado.append(f"Error creando alumno {alumno_data['nombre']}: {str(e)}")
    
    # 4. Crear tópicos
    if 'topicos' in datos:
        for topico_data in datos['topicos']:
            try:
                Topico.crear(topico_data['nombre'], topico_data.get('descripcion', ''))
                contadores["topicos"] += 1
            except Exception as e:
                resultado.append(f"Error creando tópico {topico_data['nombre']}: {str(e)}")
    
    # 5. Crear evaluaciones (independientes de sección por ahora)
    if 'evaluaciones' in datos:
        for evaluacion_data in datos['evaluaciones']:
            try:
                Evaluacion.crear(
                    evaluacion_data['nombre'], 
                    evaluacion_data.get('tipo', 'GE'), 
                    evaluacion_data.get('porcentaje', 0)
                )
                contadores["evaluaciones"] += 1
            except Exception as e:
                resultado.append(f"Error creando evaluación {evaluacion_data['nombre']}: {str(e)}")
    
    # 6. Crear instancias de curso
    if 'instancias_curso' in datos:
        for instancia_data in datos['instancias_curso']:
            try:
                # Buscar curso por código
                cursos = Curso.obtener_todos()
                curso_id = None
                for curso in cursos:
                    if curso[1] == instancia_data['curso_codigo']:  # curso[1] es el código
                        curso_id = curso[0]  # curso[0] es el ID
                        break
                
                if curso_id:
                    InstanciaCurso.crear(instancia_data['semestre'], instancia_data['anio'], curso_id)
                    contadores["instancias"] += 1
                else:
                    resultado.append(f"Error: Curso {instancia_data['curso_codigo']} no encontrado")
            except Exception as e:
                resultado.append(f"Error creando instancia: {str(e)}")
    
    # 7. Crear secciones
    if 'secciones' in datos:
        for seccion_data in datos['secciones']:
            try:
                # Buscar instancia de curso
                instancias = InstanciaCurso.obtener_todos()
                instancia_id = None
                ic_data = seccion_data['instancia_curso']
                
                for instancia in instancias:
                    if (instancia['semestre'] == ic_data['semestre'] and 
                        instancia['anio'] == ic_data['anio'] and 
                        instancia['curso_codigo'] == ic_data['curso_codigo']):
                        instancia_id = instancia['id']
                        break
                
                if instancia_id:
                    Seccion.crear(seccion_data['numero'], instancia_id)
                    contadores["secciones"] += 1
                else:
                    resultado.append(f"Error: Instancia de curso no encontrada para sección")
            except Exception as e:
                resultado.append(f"Error creando sección: {str(e)}")
    
    # 8. Crear instancias de tópico
    if 'instancias_topico' in datos:
        for it_data in datos['instancias_topico']:
            try:
                # Buscar tópico por nombre
                topicos = Topico.obtener_todos()
                topico_id = None
                for topico in topicos:
                    if topico['nombre'] == it_data['topico_nombre']:
                        topico_id = topico['id']
                        break
                
                # Buscar instancia de curso
                instancias = InstanciaCurso.obtener_todos()
                instancia_id = None
                ic_data = it_data['instancia_curso']
                
                for instancia in instancias:
                    if (instancia['semestre'] == ic_data['semestre'] and 
                        instancia['anio'] == ic_data['anio'] and 
                        instancia['curso_codigo'] == ic_data['curso_codigo']):
                        instancia_id = instancia['id']
                        break
                
                # Buscar evaluación por nombre
                evaluaciones = Evaluacion.obtener_todos()
                evaluacion_id = None
                for evaluacion in evaluaciones:
                    if evaluacion['nombre'] == it_data['evaluacion_nombre']:
                        evaluacion_id = evaluacion['id']
                        break
                
                if topico_id and instancia_id and evaluacion_id:
                    InstanciaTopico.crear(topico_id, instancia_id, evaluacion_id)
                    contadores["instancias_topico"] += 1
                else:
                    resultado.append(f"Error: No se pudo crear instancia de tópico (faltan referencias)")
            except Exception as e:
                resultado.append(f"Error creando instancia de tópico: {str(e)}")
    
    # 9. Crear notas
    if 'notas' in datos:
        for nota_data in datos['notas']:
            try:
                # Buscar alumno por correo
                alumnos = Alumno.obtener_todos()
                alumno_id = None
                for alumno in alumnos:
                    if alumno[2] == nota_data['alumno_correo']:  # alumno[2] es el correo
                        alumno_id = alumno[0]  # alumno[0] es el ID
                        break
                
                # Buscar instancia de tópico
                instancias_topico = InstanciaTopico.obtener_todos()
                instancia_topico_id = None
                
                for it in instancias_topico:
                    # Verificar si coincide con el tópico y la instancia de curso
                    if (it['topico_nombre'] == nota_data['topico_nombre'] and
                        it['semestre'] == nota_data['instancia_curso']['semestre'] and
                        it['anio'] == nota_data['instancia_curso']['anio'] and
                        it['curso_codigo'] == nota_data['instancia_curso']['curso_codigo']):
                        instancia_topico_id = it['id']
                        break
                
                if alumno_id and instancia_topico_id:
                    Nota.crear(alumno_id, instancia_topico_id, nota_data['nota'])
                    contadores["notas"] += 1
                else:
                    resultado.append(f"Error: No se pudo crear nota (faltan referencias)")
            except Exception as e:
                resultado.append(f"Error creando nota: {str(e)}")
    
    # Generar resumen de resultados
    resumen = []
    for entidad, cantidad in contadores.items():
        if cantidad > 0:
            resumen.append(f"{cantidad} {entidad}")
    
    if resumen:
        resultado.insert(0, f"✅ Cargados exitosamente: {', '.join(resumen)}")
    
    return '; '.join(resultado) if resultado else "Carga completada exitosamente"

# API REST endpoint para carga JSON
@json_bp.route('/api/cargar-json', methods=['POST'])
def api_cargar_json():
    """API endpoint para carga masiva de datos JSON"""
    try:
        # Verificar Content-Type
        if not request.is_json:
            return jsonify({'error': 'Content-Type debe ser application/json'}), 400
        
        datos = request.get_json()
        if not datos:
            return jsonify({'error': 'No se recibieron datos JSON'}), 400
        
        # Procesar los datos
        resultado = procesar_datos_json(datos)
        
        return jsonify({
            'success': True,
            'mensaje': 'Datos cargados exitosamente',
            'detalle': resultado
        }), 200
        
    except json.JSONDecodeError:
        return jsonify({'error': 'JSON inválido'}), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error procesando datos: {str(e)}'
        }), 500

@json_bp.route('/api/validar-json', methods=['POST'])
def api_validar_json():
    """API endpoint para validar estructura JSON sin cargar datos"""
    try:
        if not request.is_json:
            return jsonify({'error': 'Content-Type debe ser application/json'}), 400
        
        datos = request.get_json()
        if not datos:
            return jsonify({'error': 'No se recibieron datos JSON'}), 400
        
        # Validar estructura
        entidades_validas = ['cursos', 'profesores', 'alumnos', 'instancias_curso', 
                           'secciones', 'topicos', 'evaluaciones', 'instancias_topico', 'notas']
        
        entidades_encontradas = []
        errores = []
        
        for key in datos.keys():
            if key in entidades_validas:
                entidades_encontradas.append(key)
                # Validar que sea una lista
                if not isinstance(datos[key], list):
                    errores.append(f"'{key}' debe ser una lista")
            else:
                errores.append(f"Entidad desconocida: '{key}'")
        
        # Contar elementos por entidad
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

    return '; '.join(resultado) if resultado else "Carga completada exitosamente"
