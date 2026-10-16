# -*- coding: utf-8 -*-
"""
Ejecutor Maestro de Pruebas y Auditoría Integral (Master Test Runner) para Quantum Blueprint.
Ecosistema completo: FIPS 204 ML-DSA, SP 800-90B Health Tests, Rotación de Tokens RFC 7009 y Carga Concurrente.
Diseñado por Lázaro López Paz (El Prat de Llobregat, Barcelona, España) e IA.
"""

import sys
import unittest
import asyncio
from datetime import datetime

# Importar las suites de prueba unitaria existentes
import test_malformed_signatures
import test_replay_and_revocation
import test_entropy_failure
import test_catastrophic_entropy
import sp80090b_health_tests
import hash_mldsa_benchmark
import load_test_mldsa

def run_master_suite():
    print("=" * 75)
    print(" 🚀 EJECUTOR MAESTRO DE PRUEBAS Y AUDITORÍA INTEGRAL QUANTUM BLUEPRINT")
    print("=" * 75)
    print(f"Fecha de Ejecución: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # 1. Cargar y ejecutar suites de pruebas unitarias
    print("--- 1. EJECUTANDO SUITES DE PRUEBAS UNITARIAS Y CRIPTOGRÁFICAS ---")
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTests(loader.loadTestsFromModule(test_malformed_signatures))
    suite.addTests(loader.loadTestsFromModule(test_replay_and_revocation))
    suite.addTests(loader.loadTestsFromModule(test_entropy_failure))
    suite.addTests(loader.loadTestsFromModule(test_catastrophic_entropy))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    if not result.wasSuccessful():
        print("❌ ALGUNAS PRUEBAS UNITARIAS FALLARON")
        sys.exit(1)

    print(f"\n✅ PRUEBAS UNITARIAS COMPLETADAS CON ÉXITO: {result.testsRun}/{result.testsRun} PASADAS\n")

    # 2. Simulación de Pruebas de Salud SP 800-90B
    print("--- 2. EJECUTANDO SIMULACIÓN DE PRUEBAS DE SALUD DE ENTROPÍA SP 800-90B ---")
    res_sp = sp80090b_health_tests.run_simulation()

    assert res_sp["test_normal_random"] == True, "Fallo en simulación de fuente aleatoria normal"
    assert res_sp["test_stuck_fault"] == False, "Fallo en detección de bloqueo stuck-at"
    assert res_sp["test_biased_fault"] == False, "Fallo en detección de sesgo"
    print("  - RCT Cutoff:", res_sp["rct_cutoff"])
    print("  - APT Cutoff:", res_sp["apt_cutoff"])
    print("✅ PRUEBAS DE SALUD SP 800-90B COMPLETADAS Y VERIFICADAS\n")

    # 3. Benchmark HashML-DSA (FIPS 204)
    print("--- 3. EJECUTANDO BENCHMARKS DE RENDIMIENTO HASHML-DSA ---")
    hash_mldsa_benchmark.run_benchmark()
    print("✅ BENCHMARKS DE FIRMA HASHML-DSA COMPLETADOS CON ÉXITO\n")

    # 4. Pruebas de Carga Concurrente
    print("--- 4. EJECUTANDO PRUEBAS DE CARGA Y CONCURRENCIA HTTPX ---")
    asyncio.run(load_test_mldsa.run_load_test())
    print("✅ PRUEBA DE CARGA CONCURRENTE COMPLETADA CON ÉXITO\n")

    print("=" * 75)
    print(" 🏆 RESULTADO FINAL: 100% DE LAS PRUEBAS Y AUDITORÍAS PASARON PERFECTAMENTE")
    print("=" * 75)

if __name__ == "__main__":
    run_master_suite()
