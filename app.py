import logging
import traceback
from flask import Flask, jsonify, render_template, flash, redirect, url_for, request
from sga.db.database import init_database
from sga.routes.curso_routes import curso_bp
from sga.routes.profesor_routes import profesor_bp
from sga.routes.alumno_routes import alumno_bp
from sga.routes.instancia_curso_routes import instancia_curso_bp
from sga.routes.seccion_routes import seccion_bp
from sga.routes.evaluacion_routes import evaluacion_bp
from sga.routes.topico_routes import topico_bp
from sga.routes.instancia_topico_routes import instancia_topico_bp
from sga.routes.nota_routes import nota_bp
from sga.routes.json_routes import json_bp
from sga.routes.reporte_routes import reporte_bp
from sga.config.settings import FLASK_HOST, FLASK_PORT, FLASK_DEBUG
from sga.routes.horario_routes import horario_bp
from sga.routes.sala_routes import sala_bp
from sga.utils.validators import ValidationError

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('server.log'),
        logging.StreamHandler()
    ]
)

def create_app():
    app = Flask(__name__, 
                template_folder='sga/templates',
                static_folder='sga/static')
    app.secret_key = 'clave-secreta-para-desarrollo'
    
    @app.errorhandler(ValidationError)
    def handle_validation_error(e):
        if request.is_json:
            return jsonify({'error': str(e)}), 400
        else:
            flash(str(e), 'error')
            return redirect(request.referrer or url_for('index'))

    @app.errorhandler(404)
    def handle_not_found(e):
        if request.is_json:
            return jsonify({'error': 'Recurso no encontrado'}), 404
        else:
            flash('Página no encontrada', 'error')
            return render_template('error.html', error_code=404, error_message='Página no encontrada'), 404    @app.errorhandler(500)
        
    def handle_internal_error(e):
        app.logger.error(f"Error interno del servidor: {e}")
        app.logger.error(f"Traceback: {traceback.format_exc()}")
        if request.is_json:
            return jsonify({'error': 'Error interno del servidor'}), 500
        else:
            flash('Ha ocurrido un error interno. Por favor, intente nuevamente.', 'error')
            return render_template('error.html', error_code=500, error_message='Error interno del servidor'), 500

    @app.route('/')
    def index():
        stats = {
            'total_cursos': 0,
            'total_profesores': 0,
            'total_alumnos': 0,
            'instancias_activas': 0,
            'cursos_cerrados': 0,
            'total_secciones': 0,
            'total_evaluaciones': 0
        }
        
        try:
            from sga.models.curso import Curso
            from sga.models.profesor import Profesor  
            from sga.models.alumno import Alumno
            from sga.models.instancia_curso import InstanciaCurso
            from sga.models.seccion import Seccion
            from sga.models.evaluacion import Evaluacion            
            try:
                stats['total_cursos'] = len(Curso.get_all() or [])
            except Exception as e:
                print(f"Error cargando cursos: {e}")
                
            try:
                stats['total_profesores'] = len(Profesor.get_all() or [])
            except Exception as e:
                print(f"Error cargando profesores: {e}")
                
            try:
                stats['total_alumnos'] = len(Alumno.get_all() or [])
            except Exception as e:
                print(f"Error cargando alumnos: {e}")
                
            try:
                instancias = InstanciaCurso.obtener_todos() or []
                stats['instancias_activas'] = len([ic for ic in instancias if not ic.get('fecha_cierre')])
                stats['cursos_cerrados'] = len([ic for ic in instancias if ic.get('fecha_cierre')])
            except Exception as e:
                print(f"Error cargando instancias: {e}")
                
            try:
                stats['total_secciones'] = len(Seccion.obtener_todos() or [])
            except Exception as e:
                print(f"Error cargando secciones: {e}")
                
            try:
                stats['total_evaluaciones'] = len(Evaluacion.obtener_todos() or [])
            except Exception as e:
                print(f"Error cargando evaluaciones: {e}")
                
        except Exception as e:
            print(f"Error general al obtener estadísticas: {e}")
        
        return render_template('index.html', stats=stats)

    @app.route('/api')
    def api_welcome():
        return jsonify({
            'mensaje': 'Bienvenido al Sistema de Gestión Académica (SGA)',
            'version': '1.0',
            'endpoints': {
                'cursos': '/api/cursos',
                'profesores': '/api/profesores',
                'alumnos': '/api/alumnos'
            },
            'status': 'operativo'
        })
    
    try:
        app.register_blueprint(curso_bp)
        app.register_blueprint(profesor_bp)
        app.register_blueprint(alumno_bp)
        app.register_blueprint(instancia_curso_bp)
        app.register_blueprint(seccion_bp)
        app.register_blueprint(evaluacion_bp)
        app.register_blueprint(topico_bp)
        app.register_blueprint(instancia_topico_bp)
        app.register_blueprint(nota_bp)
        app.register_blueprint(json_bp)
        app.register_blueprint(reporte_bp)
        app.register_blueprint(horario_bp)
        app.register_blueprint(sala_bp)

    except Exception as e:
        print(f"Error al registrar blueprints: {e}")
    
    return app

def main():
    try:
        init_database()    
        app = create_app()
        app.run(host=FLASK_HOST, port=FLASK_PORT, debug=FLASK_DEBUG)

    except Exception as e:
        print(f"Error crítico al inicializar la aplicación: {e}")
        print("No se puede iniciar el servidor. Verifique la configuración y la base de datos.")

if __name__ == '__main__':
    main()
