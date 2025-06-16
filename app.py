from flask import Flask, jsonify, render_template
from db.database import init_database
from routes.curso_routes import curso_bp
from routes.profesor_routes import profesor_bp
from routes.alumno_routes import alumno_bp
from routes.instancia_curso_routes import instancia_curso_bp
from routes.seccion_routes import seccion_bp
from routes.evaluacion_routes import evaluacion_bp
from routes.topico_routes import topico_bp
from routes.instancia_topico_routes import instancia_topico_bp
from routes.nota_routes import nota_bp
from routes.json_routes import json_bp
from routes.reporte_routes import reporte_bp
from config.settings import FLASK_HOST, FLASK_PORT, FLASK_DEBUG

def create_app():
    """Factory function para crear la aplicación Flask"""
    app = Flask(__name__)
    app.secret_key = 'clave-secreta-para-desarrollo'  # En producción usar variable de entorno    # Ruta principal que sirve la interfaz web
    @app.route('/')
    def index():
        # Obtener estadísticas para el dashboard
        from models.curso import Curso
        from models.profesor import Profesor  
        from models.alumno import Alumno
        from models.instancia_curso import InstanciaCurso
        from models.seccion import Seccion
        from models.evaluacion import Evaluacion
        stats = {
            'total_cursos': len(Curso.obtener_todos()),
            'total_profesores': len(Profesor.obtener_todos()),
            'total_alumnos': len(Alumno.obtener_todos()),
            'instancias_activas': len([ic for ic in InstanciaCurso.obtener_todos() if not ic.get('fecha_cierre')]),
            'cursos_cerrados': len([ic for ic in InstanciaCurso.obtener_todos() if ic.get('fecha_cierre')]),
            'total_secciones': len(Seccion.obtener_todos()),
            'total_evaluaciones': len(Evaluacion.obtener_todos())
        }
        
        return render_template('index.html', stats=stats)
    
    # Ruta de bienvenida para la API (mantener compatibilidad)
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
            'documentacion': 'Ver README.md para más información'
        })    # Registrar blueprints
    app.register_blueprint(curso_bp, url_prefix='/api')
    app.register_blueprint(profesor_bp, url_prefix='/api')
    app.register_blueprint(alumno_bp, url_prefix='/api')
    app.register_blueprint(instancia_curso_bp)
    app.register_blueprint(seccion_bp)
    app.register_blueprint(evaluacion_bp)
    app.register_blueprint(topico_bp)
    app.register_blueprint(instancia_topico_bp)
    app.register_blueprint(nota_bp)
    app.register_blueprint(json_bp)
    app.register_blueprint(reporte_bp)
    
    return app

def main():
    """Función principal para ejecutar la aplicación"""
    # Inicializar la base de datos
    init_database()
    
    # Crear la aplicación
    app = create_app()
    
    # Ejecutar la aplicación
    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=FLASK_DEBUG)

if __name__ == '__main__':
    main()
