from sga.models.instancia_curso import InstanciaCurso

print('=== INSTANCIAS DE CURSO EXISTENTES ===')
instancias = InstanciaCurso.obtener_todos()
print(f'Total instancias encontradas: {len(instancias)}')
for instancia in instancias:
    print(f'ID: {instancia["id"]}, Semestre: {instancia["semestre"]}, Año: {instancia["anio"]}, Curso: {instancia["curso_codigo"]}')
