// Configuración de la API
const API_BASE = '/api';

// Variables globales
let currentEditingId = null;
let currentEditingType = null;

// Función para cambiar entre secciones
function showSection(sectionName) {
    // Ocultar todas las secciones
    document.querySelectorAll('.content-section').forEach(section => {
        section.classList.remove('active');
    });
    
    // Remover active de todos los nav-links
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
    });
    
    // Mostrar la sección seleccionada
    document.getElementById(sectionName).classList.add('active');
    
    // Activar el nav-link correspondiente
    event.target.classList.add('active');
    
    // Cargar datos según la sección
    switch(sectionName) {
        case 'dashboard':
            loadDashboardData();
            break;
        case 'cursos':
            loadCursos();
            break;
        case 'profesores':
            loadProfesores();
            break;
        case 'alumnos':
            loadAlumnos();
            break;
    }
}

// Función para mostrar alertas
function showAlert(message, type = 'success') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // Insertar al inicio del main-content
    const mainContent = document.querySelector('.main-content');
    mainContent.insertBefore(alertDiv, mainContent.firstChild);
    
    // Auto-eliminar después de 5 segundos
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 5000);
}

// Funciones para el Dashboard
async function loadDashboardData() {
    try {
        const [cursosRes, profesoresRes, alumnosRes] = await Promise.all([
            fetch(`${API_BASE}/cursos`),
            fetch(`${API_BASE}/profesores`),
            fetch(`${API_BASE}/alumnos`)
        ]);
        
        const cursosData = await cursosRes.json();
        const profesoresData = await profesoresRes.json();
        const alumnosData = await alumnosRes.json();
        
        document.getElementById('total-cursos').textContent = cursosData.cursos?.length || 0;
        document.getElementById('total-profesores').textContent = profesoresData.profesores?.length || 0;
        document.getElementById('total-alumnos').textContent = alumnosData.alumnos?.length || 0;
    } catch (error) {
        console.error('Error cargando datos del dashboard:', error);
    }
}

// Funciones para Cursos
async function loadCursos() {
    try {
        const response = await fetch(`${API_BASE}/cursos`);
        const data = await response.json();
        
        const tbody = document.getElementById('cursos-table');
        tbody.innerHTML = '';
        
        if (data.cursos && data.cursos.length > 0) {
            data.cursos.forEach(curso => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${curso.id}</td>
                    <td><span class="badge bg-primary">${curso.codigo}</span></td>
                    <td>${curso.nombre}</td>
                    <td>${curso.requisitos || 'Sin requisitos'}</td>
                    <td>
                        <button class="btn btn-sm btn-outline-primary me-1" onclick="editCurso(${curso.id})">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-danger" onclick="deleteCurso(${curso.id})">
                            <i class="fas fa-trash"></i>
                        </button>
                    </td>
                `;
                tbody.appendChild(row);
            });
        } else {
            tbody.innerHTML = '<tr><td colspan="5" class="text-center">No hay cursos registrados</td></tr>';
        }
    } catch (error) {
        console.error('Error cargando cursos:', error);
        showAlert('Error al cargar los cursos', 'danger');
    }
}

function resetCursoForm() {
    document.getElementById('cursoForm').reset();
    document.getElementById('cursoId').value = '';
    document.getElementById('cursoModalTitle').textContent = 'Nuevo Curso';
    currentEditingId = null;
    currentEditingType = null;
}

async function saveCurso() {
    const id = document.getElementById('cursoId').value;
    const codigo = document.getElementById('cursoCodigo').value;
    const nombre = document.getElementById('cursoNombre').value;
    const requisitos = document.getElementById('cursoRequisitos').value;
    
    if (!codigo || !nombre) {
        showAlert('Código y nombre son requeridos', 'warning');
        return;
    }
    
    const cursoData = { codigo, nombre, requisitos };
    
    try {
        let response;
        if (id) {
            // Actualizar curso existente
            response = await fetch(`${API_BASE}/cursos/${id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(cursoData)
            });
        } else {
            // Crear nuevo curso
            response = await fetch(`${API_BASE}/cursos`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(cursoData)
            });
        }
        
        if (response.ok) {
            showAlert(id ? 'Curso actualizado exitosamente' : 'Curso creado exitosamente');
            loadCursos();
            bootstrap.Modal.getInstance(document.getElementById('cursoModal')).hide();
        } else {
            const error = await response.json();
            showAlert(error.error || 'Error al guardar el curso', 'danger');
        }
    } catch (error) {
        console.error('Error guardando curso:', error);
        showAlert('Error al guardar el curso', 'danger');
    }
}

async function editCurso(id) {
    try {
        const response = await fetch(`${API_BASE}/cursos/${id}`);
        const curso = await response.json();
        
        document.getElementById('cursoId').value = curso.id;
        document.getElementById('cursoCodigo').value = curso.codigo;
        document.getElementById('cursoNombre').value = curso.nombre;
        document.getElementById('cursoRequisitos').value = curso.requisitos || '';
        document.getElementById('cursoModalTitle').textContent = 'Editar Curso';
        
        new bootstrap.Modal(document.getElementById('cursoModal')).show();
    } catch (error) {
        console.error('Error cargando curso:', error);
        showAlert('Error al cargar el curso', 'danger');
    }
}

async function deleteCurso(id) {
    if (confirm('¿Estás seguro de que quieres eliminar este curso?')) {
        try {
            const response = await fetch(`${API_BASE}/cursos/${id}`, {
                method: 'DELETE'
            });
            
            if (response.ok) {
                showAlert('Curso eliminado exitosamente');
                loadCursos();
            } else {
                const error = await response.json();
                showAlert(error.error || 'Error al eliminar el curso', 'danger');
            }
        } catch (error) {
            console.error('Error eliminando curso:', error);
            showAlert('Error al eliminar el curso', 'danger');
        }
    }
}

// Funciones para Profesores
async function loadProfesores() {
    try {
        const response = await fetch(`${API_BASE}/profesores`);
        const data = await response.json();
        
        const tbody = document.getElementById('profesores-table');
        tbody.innerHTML = '';
        
        if (data.profesores && data.profesores.length > 0) {
            data.profesores.forEach(profesor => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${profesor.id}</td>
                    <td>${profesor.nombre}</td>
                    <td><a href="mailto:${profesor.correo}">${profesor.correo}</a></td>
                    <td>
                        <button class="btn btn-sm btn-outline-success me-1" onclick="editProfesor(${profesor.id})">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-danger" onclick="deleteProfesor(${profesor.id})">
                            <i class="fas fa-trash"></i>
                        </button>
                    </td>
                `;
                tbody.appendChild(row);
            });
        } else {
            tbody.innerHTML = '<tr><td colspan="4" class="text-center">No hay profesores registrados</td></tr>';
        }
    } catch (error) {
        console.error('Error cargando profesores:', error);
        showAlert('Error al cargar los profesores', 'danger');
    }
}

function resetProfesorForm() {
    document.getElementById('profesorForm').reset();
    document.getElementById('profesorId').value = '';
    document.getElementById('profesorModalTitle').textContent = 'Nuevo Profesor';
}

async function saveProfesor() {
    const id = document.getElementById('profesorId').value;
    const nombre = document.getElementById('profesorNombre').value;
    const correo = document.getElementById('profesorCorreo').value;
    
    if (!nombre || !correo) {
        showAlert('Nombre y correo son requeridos', 'warning');
        return;
    }
    
    const profesorData = { nombre, correo };
    
    try {
        let response;
        if (id) {
            response = await fetch(`${API_BASE}/profesores/${id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(profesorData)
            });
        } else {
            response = await fetch(`${API_BASE}/profesores`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(profesorData)
            });
        }
        
        if (response.ok) {
            showAlert(id ? 'Profesor actualizado exitosamente' : 'Profesor creado exitosamente');
            loadProfesores();
            bootstrap.Modal.getInstance(document.getElementById('profesorModal')).hide();
        } else {
            const error = await response.json();
            showAlert(error.error || 'Error al guardar el profesor', 'danger');
        }
    } catch (error) {
        console.error('Error guardando profesor:', error);
        showAlert('Error al guardar el profesor', 'danger');
    }
}

async function editProfesor(id) {
    try {
        const response = await fetch(`${API_BASE}/profesores/${id}`);
        const profesor = await response.json();
        
        document.getElementById('profesorId').value = profesor.id;
        document.getElementById('profesorNombre').value = profesor.nombre;
        document.getElementById('profesorCorreo').value = profesor.correo;
        document.getElementById('profesorModalTitle').textContent = 'Editar Profesor';
        
        new bootstrap.Modal(document.getElementById('profesorModal')).show();
    } catch (error) {
        console.error('Error cargando profesor:', error);
        showAlert('Error al cargar el profesor', 'danger');
    }
}

async function deleteProfesor(id) {
    if (confirm('¿Estás seguro de que quieres eliminar este profesor?')) {
        try {
            const response = await fetch(`${API_BASE}/profesores/${id}`, {
                method: 'DELETE'
            });
            
            if (response.ok) {
                showAlert('Profesor eliminado exitosamente');
                loadProfesores();
            } else {
                const error = await response.json();
                showAlert(error.error || 'Error al eliminar el profesor', 'danger');
            }
        } catch (error) {
            console.error('Error eliminando profesor:', error);
            showAlert('Error al eliminar el profesor', 'danger');
        }
    }
}

// Funciones para Alumnos
async function loadAlumnos() {
    try {
        const response = await fetch(`${API_BASE}/alumnos`);
        const data = await response.json();
        
        const tbody = document.getElementById('alumnos-table');
        tbody.innerHTML = '';
        
        if (data.alumnos && data.alumnos.length > 0) {
            data.alumnos.forEach(alumno => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${alumno.id}</td>
                    <td>${alumno.nombre}</td>
                    <td><a href="mailto:${alumno.correo}">${alumno.correo}</a></td>
                    <td>${alumno.fecha_ingreso}</td>
                    <td>
                        <button class="btn btn-sm btn-outline-info me-1" onclick="editAlumno(${alumno.id})">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-danger" onclick="deleteAlumno(${alumno.id})">
                            <i class="fas fa-trash"></i>
                        </button>
                    </td>
                `;
                tbody.appendChild(row);
            });
        } else {
            tbody.innerHTML = '<tr><td colspan="5" class="text-center">No hay alumnos registrados</td></tr>';
        }
    } catch (error) {
        console.error('Error cargando alumnos:', error);
        showAlert('Error al cargar los alumnos', 'danger');
    }
}

function resetAlumnoForm() {
    document.getElementById('alumnoForm').reset();
    document.getElementById('alumnoId').value = '';
    document.getElementById('alumnoModalTitle').textContent = 'Nuevo Alumno';
}

async function saveAlumno() {
    const id = document.getElementById('alumnoId').value;
    const nombre = document.getElementById('alumnoNombre').value;
    const correo = document.getElementById('alumnoCorreo').value;
    const fecha_ingreso = document.getElementById('alumnoFechaIngreso').value;
    
    if (!nombre || !correo || !fecha_ingreso) {
        showAlert('Todos los campos son requeridos', 'warning');
        return;
    }
    
    const alumnoData = { nombre, correo, fecha_ingreso };
    
    try {
        let response;
        if (id) {
            response = await fetch(`${API_BASE}/alumnos/${id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(alumnoData)
            });
        } else {
            response = await fetch(`${API_BASE}/alumnos`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(alumnoData)
            });
        }
        
        if (response.ok) {
            showAlert(id ? 'Alumno actualizado exitosamente' : 'Alumno creado exitosamente');
            loadAlumnos();
            bootstrap.Modal.getInstance(document.getElementById('alumnoModal')).hide();
        } else {
            const error = await response.json();
            showAlert(error.error || 'Error al guardar el alumno', 'danger');
        }
    } catch (error) {
        console.error('Error guardando alumno:', error);
        showAlert('Error al guardar el alumno', 'danger');
    }
}

async function editAlumno(id) {
    try {
        const response = await fetch(`${API_BASE}/alumnos/${id}`);
        const alumno = await response.json();
        
        document.getElementById('alumnoId').value = alumno.id;
        document.getElementById('alumnoNombre').value = alumno.nombre;
        document.getElementById('alumnoCorreo').value = alumno.correo;
        document.getElementById('alumnoFechaIngreso').value = alumno.fecha_ingreso;
        document.getElementById('alumnoModalTitle').textContent = 'Editar Alumno';
        
        new bootstrap.Modal(document.getElementById('alumnoModal')).show();
    } catch (error) {
        console.error('Error cargando alumno:', error);
        showAlert('Error al cargar el alumno', 'danger');
    }
}

async function deleteAlumno(id) {
    if (confirm('¿Estás seguro de que quieres eliminar este alumno?')) {
        try {
            const response = await fetch(`${API_BASE}/alumnos/${id}`, {
                method: 'DELETE'
            });
            
            if (response.ok) {
                showAlert('Alumno eliminado exitosamente');
                loadAlumnos();
            } else {
                const error = await response.json();
                showAlert(error.error || 'Error al eliminar el alumno', 'danger');
            }
        } catch (error) {
            console.error('Error eliminando alumno:', error);
            showAlert('Error al eliminar el alumno', 'danger');
        }
    }
}

// Inicializar la aplicación
document.addEventListener('DOMContentLoaded', function() {
    loadDashboardData();
});
