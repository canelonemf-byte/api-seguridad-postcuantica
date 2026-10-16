# -*- coding: utf-8 -*-
"""
Suite de pruebas unitarias para verificación de firmas malformadas y alteradas en ML-DSA (FIPS 204).
Diseñado por Lázaro López Paz (El Prat de Llobregat, Barcelona, España) e IA.
"""

import unittest
from fastapi.testclient import TestClient
from quantum_blueprint_ultimate_v2 import app, ML_DSA_PARAMS

client = TestClient(app)

class TestMalformedMLDSASignatures(unittest.TestCase):

    def setUp(self):
        # Valores válidos de referencia para ML-DSA-65 según FIPS 204
        self.param_set = "ML-DSA-65"
        self.valid_pk_len = ML_DSA_PARAMS["ML-DSA-65"]["pk_bytes"]  # 1952 bytes -> 3904 hex chars
        self.valid_sig_len = ML_DSA_PARAMS["ML-DSA-65"]["sig_bytes"]  # 3309 bytes -> 6618 hex chars
        
        self.valid_pk_hex = "a" * (self.valid_pk_len * 2)
        self.valid_sig_hex = "b" * (self.valid_sig_len * 2)

    def test_01_signature_truncated(self):
        """Prueba de firma truncada (longitud menor a la especificada por FIPS 204)."""
        short_sig_hex = "b" * ((self.valid_sig_len - 10) * 2)
        headers = {
            "X-ML-DSA-Signature": short_sig_hex,
            "X-ML-DSA-Public-Key": self.valid_pk_hex,
            "X-ML-DSA-ParamSet": self.param_set
        }
        response = client.get("/qpu/status", headers=headers)
        self.assertEqual(response.status_code, 400)
        self.assertIn("Tamaño de firma no válido para ML-DSA-65", response.json()["detail"])

    def test_02_signature_oversized(self):
        """Prueba de firma sobre-extendida (longitud mayor a la especificada por FIPS 204)."""
        long_sig_hex = "b" * ((self.valid_sig_len + 50) * 2)
        headers = {
            "X-ML-DSA-Signature": long_sig_hex,
            "X-ML-DSA-Public-Key": self.valid_pk_hex,
            "X-ML-DSA-ParamSet": self.param_set
        }
        response = client.get("/qpu/status", headers=headers)
        self.assertEqual(response.status_code, 400)
        self.assertIn("Tamaño de firma no válido para ML-DSA-65", response.json()["detail"])

    def test_03_public_key_malformed_length(self):
        """Prueba de clave pública con tamaño incorrecto para el parámetro seleccionado."""
        bad_pk_hex = "a" * ((self.valid_pk_len - 100) * 2)
        headers = {
            "X-ML-DSA-Signature": self.valid_sig_hex,
            "X-ML-DSA-Public-Key": bad_pk_hex,
            "X-ML-DSA-ParamSet": self.param_set
        }
        response = client.get("/qpu/status", headers=headers)
        self.assertEqual(response.status_code, 400)
        self.assertIn("Tamaño de clave pública no válido para ML-DSA-65", response.json()["detail"])

    def test_04_invalid_hex_encoding(self):
        """Prueba con caracteres hexadecimales inválidos (corrupción de datos)."""
        corrupted_sig_hex = "Z" * (self.valid_sig_len * 2)
        headers = {
            "X-ML-DSA-Signature": corrupted_sig_hex,
            "X-ML-DSA-Public-Key": self.valid_pk_hex,
            "X-ML-DSA-ParamSet": self.param_set
        }
        response = client.get("/qpu/status", headers=headers)
        self.assertEqual(response.status_code, 400)
        self.assertIn("Formato hexadecimal no válido en los encabezados ML-DSA", response.json()["detail"])

    def test_05_unknown_parameter_set(self):
        """Prueba con conjunto de parámetros no estandarizado."""
        headers = {
            "X-ML-DSA-Signature": self.valid_sig_hex,
            "X-ML-DSA-Public-Key": self.valid_pk_hex,
            "X-ML-DSA-ParamSet": "ML-DSA-999"
        }
        response = client.get("/qpu/status", headers=headers)
        self.assertEqual(response.status_code, 400)
        self.assertIn("Conjunto de parámetros no reconocido: ML-DSA-999", response.json()["detail"])

    def test_06_verify_endpoint_malformed_payload(self):
        """Prueba sobre el endpoint de verificación directa /mldsa/verify con firma malformada en JSON."""
        payload = {
            "parameter_set": "ML-DSA-65",
            "public_key_hex": self.valid_pk_hex,
            "signature_hex": "1234567890abcdef",  # Firma de longitud incorrecta
            "payload": "Mensaje de prueba",
            "pre_hashed": True
        }
        response = client.post("/mldsa/verify", json=payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn("Tamaño de firma no válido para ML-DSA-65", response.json()["detail"])

if __name__ == "__main__":
    unittest.main()
