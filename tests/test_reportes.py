#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de prueba para verificar que los reportes funcionen correctamente
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sga.models.reporte import Reporte
from sga.models.alumno import Alumno

def test_reportes():
    """Prueba básica de los reportes"""
    print("🧪 Iniciando pruebas de reportes...")
    
    try:
        # Test 1: Verificar que se pueden obtener alumnos
        print("\n1️⃣ Probando obtención de alumnos...")
        alumnos = Alumno.obtener_todos()
        print(f"   ✅ Se encontraron {len(alumnos)} alumnos")
        if alumnos:
            print(f"   📋 Primer alumno: {alumnos[0]}")
        
        # Test 2: Verificar método obtener_por_id
        if alumnos:
            print("\n2️⃣ Probando obtener_por_id...")
            primer_alumno_id = alumnos[0][0]
            alumno_detalle = Alumno.obtener_por_id(primer_alumno_id)
            print(f"   ✅ Alumno por ID: {alumno_detalle}")
        
        # Test 3: Verificar que los métodos de reportes existen
        print("\n3️⃣ Verificando métodos de reportes...")
        
        # Verificar instancias de tópico disponibles
        instancias_topico = Reporte.obtener_instancias_topico_disponibles()
        print(f"   ✅ Instancias de tópico disponibles: {len(instancias_topico)}")
        
        # Verificar cursos cerrados
        cursos_cerrados = Reporte.obtener_cursos_cerrados()
        print(f"   ✅ Cursos cerrados disponibles: {len(cursos_cerrados)}")
        
        print("\n🎉 ¡Todas las pruebas básicas pasaron!")
        print("\n📋 Resumen:")
        print(f"   • Alumnos en sistema: {len(alumnos)}")
        print(f"   • Instancias de tópico: {len(instancias_topico)}")
        print(f"   • Cursos cerrados: {len(cursos_cerrados)}")
        
        if len(cursos_cerrados) > 0:
            print("   ✅ Sistema listo para reportes B y C")
        else:
            print("   ⚠️  No hay cursos cerrados - solo reporte A disponible")
            
        if len(instancias_topico) > 0:
            print("   ✅ Reporte A disponible")
        else:
            print("   ⚠️  No hay instancias de tópico")
        
    except Exception as e:
        print(f"❌ Error en las pruebas: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_reportes()
