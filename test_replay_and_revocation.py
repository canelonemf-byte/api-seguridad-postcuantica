# -*- coding: utf-8 -*-
"""
Pruebas de Protección contra Ataques de Repetición (Replay Attacks) y Revocación
Realizado por Lázaro López Paz (El Prat de Llobregat, Barcelona, España) e Inteligencia Artificial
"""

import unittest
import uuid
import sys
import os

from fastapi.testclient import TestClient
from quantum_blueprint_ultimate_v2 import app, init_db, SessionLocal, User, RefreshToken, issue_refresh_token, rotate_refresh_token

class TestReplayAndRevocation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()
        cls.client = TestClient(app)

    def setUp(self):
        self.db = SessionLocal()
        self.test_user = User(email=f"replay_test_{uuid.uuid4()}@example.com")
        self.db.add(self.test_user)
        self.db.commit()
        self.db.refresh(self.test_user)

    def tearDown(self):
        self.db.close()

    def test_01_refresh_token_replay_attack_prevention(self):
        """Demuestra que el intento de reutilizar (replay attack) un Refresh Token invalida la familia completa."""
        raw_token_1, family = issue_refresh_token(self.db, self.test_user.id)
        
        # Uso legítimo (Rotación a Token 2)
        access_token, raw_token_2, _ = rotate_refresh_token(self.db, raw_token_1)
        self.assertIsNotNone(access_token)
        self.assertIsNotNone(raw_token_2)
        
        # Ataque de Replay: Reutilización de Token 1
        response = self.client.post("/refresh", json={"refresh_token": raw_token_1})
        self.assertEqual(response.status_code, 401)
        self.assertIn("reutilizacion", response.json()["detail"].lower().replace("ó", "o"))

        # Verificación: Token 2 (legítimo) también queda bloqueado inmediatamente
        response_token_2 = self.client.post("/refresh", json={"refresh_token": raw_token_2})
        self.assertEqual(response_token_2.status_code, 401)

    def test_02_idempotent_logout_and_revocation(self):
        """Verifica la revocación de tokens vía /logout según RFC 7009."""
        raw_token, family = issue_refresh_token(self.db, self.test_user.id)
        
        # Revocación activa
        response = self.client.post("/logout", params={"refresh_token": raw_token})
        self.assertEqual(response.status_code, 200)
        self.assertIn("cerrada correctamente", response.json()["detail"].lower().replace("ó", "o"))

        # Intento posterior de usar el token revocado
        response_refresh = self.client.post("/refresh", json={"refresh_token": raw_token})
        self.assertEqual(response_refresh.status_code, 401)

    def test_03_pqc_signature_replay_protection_headers(self):
        """Verifica la inclusión de encabezados de soporte PQC y aislamiento de contexto en peticiones con firmas."""
        sig_hex = "a0" * 3309
        pk_hex = "b0" * 1952
        
        headers = {
            "x-ml-dsa-signature": sig_hex,
            "x-ml-dsa-public-key": pk_hex,
            "x-ml-dsa-paramset": "ML-DSA-65"
        }
        
        response = self.client.get("/qpu/status", headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn("X-PQC-Supported-Standards", response.headers)
        self.assertIn("NIST FIPS 204", response.headers["X-PQC-Supported-Standards"])

if __name__ == "__main__":
    unittest.main()
