"""
Simulador de Pruebas de Salud en Tiempo de Ejecución (Health Testing)
según la norma NIST SP 800-90B (Sección 4).

Este módulo implementa:
1. Repetition Count Test (RCT): Detecta si la fuente de ruido se queda "bloqueada" produciendo el mismo valor.
2. Adaptive Proportion Test (APT): Detecta caídas de entropía evaluando la frecuencia de apariciones dentro de una ventana.

Desarrollado para el Ecosistema Quantum Blueprint.
Autoría: Lázaro López Paz (El Prat de Llobregat, Barcelona, España) e Inteligencia Artificial.
"""

import math
import random
from typing import List, Tuple, Dict, Any


class RepetitionCountTest:
    """
    Repetition Count Test (NIST SP 800-90B Sección 4.4.1)
    Verifica que no se repita secuencialmente un mismo símbolo más veces que el límite H.
    """
    def __init__(self, min_entropy_bits: float, alpha_bits: float = 40.0):
        """
        :param min_entropy_bits: Min-entropía estimada por muestra (H_min)
        :param alpha_bits: Probabilidad de falso positivo de 2^(-alpha_bits) (por defecto 2^-40)
        """
        self.h_min = min_entropy_bits
        # Límite C = 1 + ceil(alpha_bits / H_min)
        self.cutoff = 1 + math.ceil(alpha_bits / self.h_min)
        self.last_sample = None
        self.current_count = 0

    def reset(self):
        self.last_sample = None
        self.current_count = 0

    def process_sample(self, sample: int) -> bool:
        """
        Procesa una muestra. Devuelve True si pasa la prueba, False si falla (excede cutoff).
        """
        if self.last_sample is None:
            self.last_sample = sample
            self.current_count = 1
            return True

        if sample == self.last_sample:
            self.current_count += 1
            if self.current_count >= self.cutoff:
                return False  # Fallo de salud (Repetición excesiva)
        else:
            self.last_sample = sample
            self.current_count = 1

        return True


class AdaptiveProportionTest:
    """
    Adaptive Proportion Test (NIST SP 800-90B Sección 4.4.2)
    Examina ventanas continuas de W muestras para comprobar que la muestra inicial no se repita con frecuencia anómala.
    """
    def __init__(self, min_entropy_bits: float, window_size: int = 512, alpha_bits: float = 40.0):
        """
        :param min_entropy_bits: Min-entropía estimada (H_min)
        :param window_size: Tamaño de la ventana W (512 o 1024)
        :param alpha_bits: Falso positivo 2^(-alpha_bits)
        """
        self.h_min = min_entropy_bits
        self.w = window_size
        self.cutoff = self._calculate_cutoff(alpha_bits)
        
        self.reset()

    def _calculate_cutoff(self, alpha_bits: float) -> int:
        """
        Calcula el límite C utilizando la aproximación binomial para la min-entropía especificada.
        """
        p = 2.0 ** (-self.h_min)
        # Aproximación conservadora para el límite C en ventana W
        p_fail = 2.0 ** (-alpha_bits)
        
        mu = (self.w - 1) * p
        sigma = math.sqrt((self.w - 1) * p * (1.0 - p))
        z = math.sqrt(2.0 * math.log(1.0 / p_fail))
        cutoff = math.ceil(1 + mu + z * sigma)
        return max(cutoff, 2)

    def reset(self):
        self.first_sample = None
        self.count = 0
        self.window_index = 0

    def process_sample(self, sample: int) -> bool:
        """
        Procesa una muestra dentro de la ventana. Devuelve True si pasa, False si detecta sesgo que excede el cutoff.
        """
        if self.window_index == 0:
            self.first_sample = sample
            self.count = 1
            self.window_index = 1
            return True

        if sample == self.first_sample:
            self.count += 1
            if self.count >= self.cutoff:
                return False  # Fallo de salud (Entropía degradada)

        self.window_index += 1
        if self.window_index >= self.w:
            self.window_index = 0

        return True


def run_simulation() -> Dict[str, Any]:
    """Ejecuta una simulación completa con datos limpios y datos defectuosos."""
    h_min = 1.0  # 1 bit de min-entropía
    
    rct = RepetitionCountTest(min_entropy_bits=h_min, alpha_bits=40.0)
    apt = AdaptiveProportionTest(min_entropy_bits=h_min, window_size=512, alpha_bits=40.0)
    
    results = {
        "rct_cutoff": rct.cutoff,
        "apt_cutoff": apt.cutoff,
        "test_normal_random": None,
        "test_stuck_fault": None,
        "test_biased_fault": None
    }
    
    # 1. Prueba con aleatoriedad normal
    rct.reset()
    apt.reset()
    passed_normal = True
    random.seed(42)
    for _ in range(2000):
        val = random.randint(0, 1)
        if not rct.process_sample(val) or not apt.process_sample(val):
            passed_normal = False
            break
    results["test_normal_random"] = passed_normal
    
    # 2. Prueba con fallo de bloqueo (stuck-at)
    rct.reset()
    apt.reset()
    passed_stuck = True
    for i in range(100):
        val = 1
        if not rct.process_sample(val) or not apt.process_sample(val):
            passed_stuck = False
            break
    results["test_stuck_fault"] = passed_stuck
    
    # 3. Prueba con fallo de sesgo en la proporción
    rct.reset()
    apt.reset()
    passed_biased = True
    for _ in range(1000):
        val = 1 if random.random() < 0.92 else 0
        if not rct.process_sample(val) or not apt.process_sample(val):
            passed_biased = False
            break
    results["test_biased_fault"] = passed_biased
    
    return results


if __name__ == "__main__":
    res = run_simulation()
    print("=== RESULTADOS DE SIMULACIÓN DE PRUEBAS DE SALUD SP 800-90B ===")
    print(f"Límite RCT (Repetition Count Cutoff): {res['rct_cutoff']} repeticiones consecutivas")
    print(f"Límite APT (Adaptive Proportion Cutoff): {res['apt_cutoff']} apariciones en ventana 512")
    print(f"1. Fuente Aleatoria Normal: {'PASÓ ✅' if res['test_normal_random'] else 'FALLÓ ❌'}")
    print(f"2. Detección de Falla de Bloqueo (Stuck-at): {'BLOQUEADO / DETECTADO ✅' if not res['test_stuck_fault'] else 'NO DETECTADO ❌'}")
    print(f"3. Detección de Falla de Sesgo (Biased Entropy): {'SESGO DETECTADO ✅' if not res['test_biased_fault'] else 'NO DETECTADO ❌'}")
