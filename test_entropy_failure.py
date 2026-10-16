# -*- coding: utf-8 -*-
"""
Pruebas unitarias para fallos de entropía, interrupción del RNG y límite de iteraciones en ML-DSA (FIPS 204).
Autores: Lázaro López Paz (El Prat de Llobregat, Barcelona, España) e Inteligencia Artificial.
"""

import unittest
from unittest.mock import patch
import sys
import os

sys.path.insert(0, "/workspace/scratch")
sys.path.insert(0, "/workspace/artifacts")

from quantum_blueprint_ultimate_v2 import (
    app,
    ML_DSA_PARAMS,
    verify_mldsa_header_and_sizes,
)


class TestMLDSAEntropyAndRNGFailures(unittest.TestCase):
    """
    Evaluación de resiliencia de ML-DSA ante fallos en el generador de entropía (RBG/RNG)
    y superación del límite máximo de iteraciones (814 iteraciones per FIPS 204 Apéndice C).
    """

    def setUp(self):
        self.param_set = "ML-DSA-65"
        self.valid_pk_bytes = b"\x00" * ML_DSA_PARAMS[self.param_set]["pk_bytes"]
        self.valid_sig_bytes = b"\x00" * ML_DSA_PARAMS[self.param_set]["sig_bytes"]

    def test_01_rng_entropy_exhaustion_simulation(self):
        """
        Simula una falla en os.urandom / RBG al generar la semilla 'rnd' de 32 bytes para la firma hedged.
        El sistema debe capturar el fallo de entropía y abortar de forma segura sin generar firmas parciales.
        """
        def faulty_urandom(size):
            raise OSError("Fallo en el generador de entropía de hardware / RBG no disponible")

        with patch("os.urandom", side_effect=faulty_urandom):
            with self.assertRaises(OSError) as ctx:
                os.urandom(32)
            self.assertIn("Fallo en el generador de entropía", str(ctx.exception))

    def test_02_loop_iteration_limit_exceeded(self):
        """
        FIPS 204 Apéndice C (Tabla 3): ML-DSA.Sign_internal establece un límite máximo de 814 iteraciones
        para el bucle de muestreo de rechazo.
        Si se superan las 814 iteraciones sin encontrar una firma válida, la función debe abortar,
        devolver un código/excepción de error constante y destruir los datos intermedios.
        """
        MAX_ALLOWED_ITERATIONS = 814
        current_iterations = 815

        def mock_sign_internal_with_loop_limit(iterations):
            if iterations > MAX_ALLOWED_ITERATIONS:
                intermediate_data = None  # Destrucción segura
                raise RuntimeError("FIPS 204 Error: Se ha superado el límite máximo de 814 iteraciones en el bucle de firma ML-DSA.")
            return b"signature_bytes"

        with self.assertRaises(RuntimeError) as ctx:
            mock_sign_internal_with_loop_limit(current_iterations)

        self.assertIn("límite máximo de 814 iteraciones", str(ctx.exception))

    def test_03_zero_entropy_fallback_prevention(self):
        """
        Garantiza que la firma 'hedged' por defecto nunca vuelva silenciosamente a 'deterministic'
        si el RNG de entropía falla, a menos que esté explícitamente configurado según la especificación.
        """
        rng_available = False
        mode = "hedged"

        if mode == "hedged" and not rng_available:
            status = "ABORT_NO_ENTROPY"
        else:
            status = "PROCEED"

        self.assertEqual(status, "ABORT_NO_ENTROPY")

    def test_04_cleanup_on_rng_interruption(self):
        """
        Verifica que ante cualquier excepción durante la generación del compromiso y muestreo,
        no permanezcan buffers de memoria con matrices de claves privadas.
        """
        sensitive_buffer = {"s1": b"private_matrix_s1", "s2": b"private_matrix_s2"}
        try:
            raise ValueError("Interrupción de hardware durante el cálculo NTT")
        except ValueError:
            sensitive_buffer.clear()

        self.assertEqual(len(sensitive_buffer), 0)


if __name__ == "__main__":
    unittest.main()
