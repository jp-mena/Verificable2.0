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
        self.omitidas = []

    def _load_salas(self):
        rows = Sala.obtener_todas()
        self.salas = [{"id": r[0], "capacidad": r[2]} for r in rows]

    def _load_bloques(self):
        rows = Bloque.obtener_todos()
        self.bloques = [{"id": r[0], "dia": r[1]} for r in rows]

    def _load_secciones(self):
        if self.semestre and self.anio:
            rows = execute_query(
                """SELECT s.id, s.profesor_id, s.sala_id, s.instancia_id, c.creditos
                       FROM secciones s
                       JOIN instancias_curso ic ON ic.id = s.instancia_id
                       JOIN cursos c           ON c.id  = ic.curso_id
                       WHERE ic.semestre = %s AND ic.anio = %s""",
                (self.semestre, self.anio))
        else:
            rows = execute_query(
                """SELECT s.id, s.profesor_id, s.sala_id, s.instancia_id, c.creditos
                       FROM secciones s
                       JOIN instancias_curso ic ON ic.id = s.instancia_id
                       JOIN cursos c           ON c.id  = ic.curso_id""")
        for sec_id, prof_id, sala_id, inst_id, cred in rows:
            if cred > 4:
                self.omitidas.append(sec_id)
                continue
            alumnos = execute_query(
                "SELECT alumno_id FROM inscripciones WHERE instancia_curso_id = %s",
                (inst_id,))
            self.secciones.append({
                "id": sec_id,
                "profesor_id": prof_id,
                "sala_fija": sala_id,
                "creditos": cred,
                "alumnos": {a[0] for a in alumnos},
                "n_alumnos": len(alumnos)
            })

    def _build_placements(self):
        bloques_por_dia = defaultdict(list)
        for b in self.bloques:
            bloques_por_dia[b["dia"].__int__()].append(b)
        self.placements = defaultdict(list)
        plc = 0
        for s in self.secciones:
            k = s["creditos"]
            for dia, lista in bloques_por_dia.items():
                lista.sort(key=lambda x: x["id"])
                for i in range(len(lista) - k + 1):
                    win = lista[i:i + k]
                    self.placements[s["id"].__int__()].append({"plc": plc, "bloques": win})
                    plc += 1

    def _create_variables(self):
        X = {}
        for s in self.secciones:
            rooms = [r for r in self.salas if r["id"] == s["sala_fija"]] if s["sala_fija"] else self.salas
            for p in self.placements[s["id"]]:
                for r in rooms:
                    X[(s["id"], p["plc"], r["id"])] = self.model.NewBoolVar(f"y_{s['id']}_{p['plc']}_{r['id']}")
        self.X = X

    def _constraints(self):
        for s in self.secciones:
            self.model.Add(sum(self.X[(s["id"], p["plc"], r["id"])] for p in self.placements[s["id"]] for r in self.salas) == 1)
        for s in self.secciones:
            for p in self.placements[s["id"]]:
                for r in self.salas:
                    if (s["id"], p["plc"], r["id"]) in self.X:
                        self.model.Add(self.X[(s["id"], p["plc"], r["id"])] * s["n_alumnos"] <= r["capacidad"])
        for b in self.bloques:
            for r in self.salas:
                self.model.Add(sum(self.X[(s["id"], p["plc"], r["id"])]
                                    for s in self.secciones
                                    for p in self.placements[s["id"]] if b in p["bloques"] and (s["id"], p["plc"], r["id"]) in self.X) <= 1)
            for prof in {s["profesor_id"] for s in self.secciones}:
                self.model.Add(sum(self.X[(s["id"], p["plc"], rr["id"])]
                                    for s in self.secciones if s["profesor_id"] == prof
                                    for p in self.placements[s["id"]]
                                    for rr in self.salas
                                    if b in p["bloques"] and (s["id"], p["plc"], rr["id"]) in self.X) <= 1)
            for alumno in {a for s in self.secciones for a in s["alumnos"]}:
                self.model.Add(sum(self.X[(s["id"], p["plc"], rr["id"])]
                                    for s in self.secciones if alumno in s["alumnos"]
                                    for p in self.placements[s["id"]]
                                    for rr in self.salas
                                    if b in p["bloques"] and (s["id"], p["plc"], rr["id"]) in self.X) <= 1)
        self.model.Minimize(sum(b["dia"] * self.X[(s["id"], p["plc"], r["id"])]
                                for s in self.secciones
                                for p in self.placements[s["id"]]
                                for r in self.salas
                                for b in p["bloques"]
                                if (s["id"], p["plc"], r["id"]) in self.X))

    def solve_and_persist(self):
        self._load_salas()
        self._load_bloques()
        self._load_secciones()
        if not self.secciones:
            return False, "Sin secciones programables"
        self._build_placements()
        self.model = cp_model.CpModel()
        self._create_variables()
        self._constraints()
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = 15
        status = solver.Solve(self.model)
        if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            return False, "Sin solución con secciones válidas"
        Horario.vaciar_todos()
        for (sid, pid, rid), var in self.X.items():
            if solver.Value(var):
                bloques = next(p for p in self.placements[sid] if p["plc"] == pid)["bloques"]
                for b in bloques:
                    Horario.insertar(sid, b["id"], rid)
        if self.omitidas:
            return True, f"Horario generado; omitidas {len(self.omitidas)} secciones >4 créditos"
        return True, "Horario generado"
