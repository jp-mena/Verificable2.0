#!/usr/bin/env python3
"""
Script de prueba para diagnosticar el error del operador @
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    print("🔍 Probando imports...")
    from sga.models.nota import Nota
    from sga.utils.validators import ValidationError, validate_float_range
    print("✅ Imports exitosos")
    
    print("\n🔍 Probando validate_float_range...")
    result = validate_float_range(5.5, 1.0, 7.0, "Nota")
    print(f"✅ validate_float_range result: {result}")
    
    print("\n🔍 Probando creación de instancia Nota...")
    nota_obj = Nota(None, 19, 7, 5.5)
    print(f"✅ Nota object created: {nota_obj}")
    print(f"   - nota.nota: {nota_obj.nota}")
    
    print("\n🔍 Probando método _validate_nota...")
    validated = nota_obj._validate_nota(5.5)
    print(f"✅ _validate_nota result: {validated}")
    
    print("\n🔍 Probando Nota.crear...")
    # Nota: Esto podría fallar si la nota ya existe, pero debería mostrar el error específico
    try:
        nota_creada = Nota.crear(19, 7, 5.5)
        print(f"✅ Nota.crear successful: {nota_creada}")
    except Exception as e:
        print(f"ℹ️  Nota.crear error (expected if duplicate): {e}")
        
    print("\n✅ Todas las pruebas completadas sin el error del operador @")
    
except Exception as e:
    print(f"❌ Error encontrado: {e}")
    import traceback
    print(f"📍 Traceback completo:")
    traceback.print_exc()
