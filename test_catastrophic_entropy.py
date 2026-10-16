# -*- coding: utf-8 -*-
"""
Test Suite: Captura de CatastrophicEntropyError y Purga Automática de Memoria (SP 800-90A / FIPS 204)
Desarrollado colaborativamente por Lázaro López Paz e Inteligencia Artificial.
"""

import unittest
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient

# Excepción personalizada para fallos de entropía catastróficos según NIST SP 800-90A
class CatastrophicEntropyError(Exception):
    """Lanzada cuando la fuente de entropía (ESV/RNG) sufre un fallo permanente o crítico."""
    pass

class CryptographicEngine:
    def __init__(self):
        self.in_error_state = False
        self.sensitive_buffer = {}

    def reset(self):
        self.in_error_state = False
        self.sensitive_buffer = {}

    def simulate_key_gen_or_sign(self, force_catastrophic_fail: bool = False):
        if self.in_error_state:
            raise CatastrophicEntropyError(
                "El módulo criptográfico está en estado de error bloqueado. "
                "Se requiere reinicio o reinstanciación física."
            )

        # Cargar variables sensibles en memoria temporal
        self.sensitive_buffer = {
            "s1": [10, 20, 30, 40],
            "s2": [5, 15, 25, 35],
            "rnd": b"\x00" * 32,
            "seed_K": b"\xff" * 32
        }

        if force_catastrophic_fail:
            try:
                # Simular fallo catastrófico en el test de salud o generador ESV
                raise CatastrophicEntropyError("Fallo catastrófico en el generador de ruido ESV (SP 800-90B)")
            finally:
                # Purga inmediata de memoria sensible ante fallo
                self.purge_sensitive_memory()
                self.in_error_state = True

        return {"status": "SUCCESS", "signature": "30450220..."}

    def purge_sensitive_memory(self):
        """Zeroizado/purga segura de buffers sensibles."""
        for key in list(self.sensitive_buffer.keys()):
            self.sensitive_buffer[key] = None
        self.sensitive_buffer.clear()

# Instancia global del motor
crypto_engine = CryptographicEngine()

# API FastAPI de prueba
app = FastAPI(title="Quantum Blueprint - Entropy Isolation Test")

@app.exception_handler(CatastrophicEntropyError)
async def catastrophic_entropy_handler(request: Request, exc: CatastrophicEntropyError):
    # Asegurar purga de memoria
    crypto_engine.purge_sensitive_memory()
    crypto_engine.in_error_state = True
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error_code": "CRYPTO_ENTROPY_CATASTROPHIC_FAILURE",
            "message": str(exc),
            "engine_status": "LOCKED"
        }
    )

@app.post("/crypto/sign")
def sign_endpoint(fail: bool = False):
    result = crypto_engine.simulate_key_gen_or_sign(force_catastrophic_fail=fail)
    return result

class TestCatastrophicEntropyHandling(unittest.TestCase):
    def setUp(self):
        crypto_engine.reset()
        self.client = TestClient(app)

    def test_01_normal_signing_operation(self):
        """Verifica que la operación normal de firma funciona correctamente."""
        response = self.client.post("/crypto/sign?fail=false")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "SUCCESS")

    def test_02_catastrophic_error_capture_and_500_response(self):
        """Verifica la captura de CatastrophicEntropyError y el retorno de HTTP 500 estructurado."""
        response = self.client.post("/crypto/sign?fail=true")
        self.assertEqual(response.status_code, 500)
        data = response.json()
        self.assertEqual(data["error_code"], "CRYPTO_ENTROPY_CATASTROPHIC_FAILURE")
        self.assertEqual(data["engine_status"], "LOCKED")

    def test_03_automatic_memory_purging(self):
        """Comprueba que los buffers sensibles son zeroizados de forma inmediata tras el error."""
        self.client.post("/crypto/sign?fail=true")
        self.assertEqual(len(crypto_engine.sensitive_buffer), 0, "El buffer sensible no se purgó correctamente")

    def test_04_engine_locking_after_failure(self):
        """Verifica que tras un error catastrófico, peticiones subsecuentes son bloqueadas inmediatamente."""
        # Provocar fallo
        self.client.post("/crypto/sign?fail=true")
        self.assertTrue(crypto_engine.in_error_state)

        # Intento posterior de firma sin parámetro de fallo (debe seguir bloqueado)
        response_subsequent = self.client.post("/crypto/sign?fail=false")
        self.assertEqual(response_subsequent.status_code, 500)
        self.assertEqual(response_subsequent.json()["engine_status"], "LOCKED")

if __name__ == "__main__":
    unittest.main()
