from sga.db.database import execute_query

class Seccion:
    def __init__(self, id=None, numero=None, instancia_id=None, profesor_id=None, sala_id=None):
        self.id = id
        self.numero = numero
        self.instancia_id = instancia_id
        self.profesor_id = profesor_id
        self.sala_id = sala_id

    @classmethod
    def crear(cls, numero, instancia_id, profesor_id=None, sala_id=None):
        q = "INSERT INTO secciones (numero, instancia_id, profesor_id, sala_id) VALUES (%s,%s,%s,%s)"
        sid = execute_query(q, (numero, instancia_id, profesor_id, sala_id))
        return cls(sid, numero, instancia_id, profesor_id, sala_id)

    @classmethod
    def obtener_todos(cls):
        q = """
        SELECT s.id,s.numero,s.instancia_id,s.profesor_id,s.sala_id,
               ic.semestre,ic.anio,c.codigo,c.nombre,ic.cerrado,
               p.nombre,coalesce(sa.nombre,'')
        FROM secciones s
        JOIN instancias_curso ic ON ic.id=s.instancia_id
        JOIN cursos c           ON c.id=ic.curso_id
        LEFT JOIN profesores p  ON p.id=s.profesor_id
        LEFT JOIN salas sa      ON sa.id=s.sala_id
        ORDER BY ic.anio DESC,ic.semestre DESC,s.numero"""
        rows = execute_query(q)
        return [{
            'id':r[0],'numero':r[1],'instancia_id':r[2],'profesor_id':r[3],'sala_id':r[4],
            'semestre':r[5],'anio':r[6],'curso_codigo':r[7],'curso_nombre':r[8],'curso_cerrado':bool(r[9]),
            'profesor_nombre':r[10] or 'Sin asignar','sala_nombre':r[11] or 'Sin asignar'
        } for r in rows]

    @classmethod
    def obtener_por_id(cls, sid):
        r = execute_query("SELECT id,numero,instancia_id,profesor_id,sala_id FROM secciones WHERE id=%s",(sid,))
        if r:
            a=r[0]
            return cls(a[0],a[1],a[2],a[3],a[4])
        return None

    def actualizar(self):
        q="UPDATE secciones SET numero=%s,instancia_id=%s,profesor_id=%s,sala_id=%s WHERE id=%s"
        execute_query(q,(self.numero,self.instancia_id,self.profesor_id,self.sala_id,self.id))
        return True

    @staticmethod
    def asignar_sala(seccion_id, sala_id):
        execute_query("UPDATE secciones SET sala_id=%s WHERE id=%s",(sala_id,seccion_id))

    @staticmethod
    def eliminar(sid):
        execute_query("DELETE FROM secciones WHERE id=%s",(sid,))

    @staticmethod
    def obtener_profesores_disponibles(instancia_id, seccion_id_actual=None):
        from sga.models.profesor import Profesor
        todos = Profesor.get_all()
        q="SELECT DISTINCT profesor_id FROM secciones WHERE instancia_id=%s AND profesor_id IS NOT NULL"
        params=[instancia_id]
        if seccion_id_actual:
            q+=" AND id!=%s"
            params.append(seccion_id_actual)
        ocupados = [p[0] for p in execute_query(q,params)]
        return [{'id':p[0],'nombre':p[1],'correo':p[2]} for p in todos if p[0] not in ocupados]
