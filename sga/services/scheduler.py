from collections import defaultdict
from ortools.sat.python import cp_model
from sga.db.database import execute_query
from sga.models.sala import Sala
from sga.models.bloque import Bloque
from sga.models.horario import Horario

class SchedulerService:
    def __init__(self, semestre=None, anio=None):
        self.semestre = semestre
        self.anio = anio
        self.salas = []
        self.bloques = []
        self.secciones = []
        self.placements = defaultdict(list)
        self.allowed_rooms = defaultdict(list)
        self.omitidas = []

    def _load_salas(self):
        self.salas = [{"id": r[0], "capacidad": r[2]} for r in Sala.obtener_todas()]

    def _load_bloques(self):
        self.bloques = [{"id": r[0], "dia": r[1]} for r in Bloque.obtener_todos()]

    def _load_secciones(self):
        base = """
            SELECT s.id,
                   s.profesor_id,
                   s.instancia_id,      -- ← añade esto
                   c.creditos,
                   s.sala_id
            FROM secciones s
            JOIN instancias_curso ic ON ic.id = s.instancia_id
            JOIN cursos c            ON c.id = ic.curso_id
        """
    
        params = ()
        if self.semestre and self.anio:
            base += " WHERE ic.semestre = %s AND ic.anio = %s"
            params = (self.semestre, self.anio)
    
        rows = execute_query(base, params)
    
        for sid, pid, inst_id, cred, sala_fija in rows:
            if cred > 4:
                self.omitidas.append(sid)
                continue
            
            alumnos = execute_query(
                "SELECT alumno_id FROM inscripciones WHERE instancia_curso_id = %s",
                (inst_id,),
            )
        
            self.secciones.append(
                dict(
                    id=sid,
                    profesor_id=pid,
                    creditos=cred,
                    sala_fija=sala_fija,
                    alumnos={a[0] for a in alumnos},
                    n_alumnos=len(alumnos),
                )
            )

    def _build_placements(self):
        by_day = defaultdict(list)
        for b in self.bloques:
            by_day[b["dia"]].append(b)
        plc = 0
        for s in self.secciones:
            k = s["creditos"]
            for dia, lista in by_day.items():
                lista.sort(key=lambda x: x["id"])
                for i in range(len(lista) - k + 1):
                    win = lista[i : i + k]
                    self.placements[s["id"]].append({"plc": plc, "bloques": win})
                    plc += 1

    def _create_variables(self):
        self.X = {}
        for s in self.secciones:
            rooms = (
                [r for r in self.salas if r["id"] == s["sala_fija"]]
                if s["sala_fija"]
                else self.salas
            )
            self.allowed_rooms[s["id"]] = rooms
            for p in self.placements[s["id"]]:
                for r in rooms:
                    self.X[(s["id"], p["plc"], r["id"])] = self.model.NewBoolVar(
                        f"y_{s['id']}_{p['plc']}_{r['id']}"
                    )

    def _add_constraints(self):
        for s in self.secciones:
            self.model.Add(
                sum(
                    self.X[(s["id"], p["plc"], r["id"])]
                    for p in self.placements[s["id"]]
                    for r in self.allowed_rooms[s["id"]]
                )
                == 1
            )
        for s in self.secciones:
            for p in self.placements[s["id"]]:
                for r in self.allowed_rooms[s["id"]]:
                    self.model.Add(
                        self.X[(s["id"], p["plc"], r["id"])] * s["n_alumnos"]
                        <= r["capacidad"]
                    )
        for b in self.bloques:
            for r in self.salas:
                self.model.Add(
                    sum(
                        self.X[(s["id"], p["plc"], r["id"])]
                        for s in self.secciones
                        for p in self.placements[s["id"]]
                        if r in self.allowed_rooms[s["id"]] and b in p["bloques"]
                    )
                    <= 1
                )
            profs = {s["profesor_id"] for s in self.secciones}
            for prof in profs:
                self.model.Add(
                    sum(
                        self.X[(s["id"], p["plc"], r["id"])]
                        for s in self.secciones
                        if s["profesor_id"] == prof
                        for p in self.placements[s["id"]]
                        for r in self.allowed_rooms[s["id"]]
                        if b in p["bloques"]
                    )
                    <= 1
                )
            alumnos = {a for s in self.secciones for a in s["alumnos"]}
            for alumno in alumnos:
                self.model.Add(
                    sum(
                        self.X[(s["id"], p["plc"], r["id"])]
                        for s in self.secciones
                        if alumno in s["alumnos"]
                        for p in self.placements[s["id"]]
                        for r in self.allowed_rooms[s["id"]]
                        if b in p["bloques"]
                    )
                    <= 1
                )
        self.model.Minimize(
            sum(
                b["dia"] * self.X[(s["id"], p["plc"], r["id"])]
                for s in self.secciones
                for p in self.placements[s["id"]]
                for r in self.allowed_rooms[s["id"]]
                for b in p["bloques"]
            )
        )

    def solve_and_persist(self):
        self._load_salas()
        self._load_bloques()
        self._load_secciones()
        if not self.secciones:
            return False, "Sin secciones programables"
        self._build_placements()
        self.model = cp_model.CpModel()
        self._create_variables()
        self._add_constraints()
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = 15
        status = solver.Solve(self.model)
        if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            return False, "Sin solución con secciones válidas"
        Horario.vaciar_semestre(self.semestre, self.anio)
        for (sid, pid, rid), var in self.X.items():
            if solver.Value(var):
                blks = next(p for p in self.placements[sid] if p["plc"] == pid)[
                    "bloques"
                ]
                for b in blks:
                    Horario.insertar(sid, b["id"], rid)
        msg = f"Horario generado ({len(self.secciones)} secciones)"
        if self.omitidas:
            msg += f"; omitidas {len(self.omitidas)} (>4 créditos)"
        return True, msg
