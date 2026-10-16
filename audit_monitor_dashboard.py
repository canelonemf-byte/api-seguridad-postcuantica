# -*- coding: utf-8 -*-
"""
Script de Monitorización y Tablero de Métricas de Integridad de Logs de Auditoría en Tiempo Real.
Ecosistema Quantum Blueprint: FIPS 204 ML-DSA, SP 800-90B Entropy Monitoring, y FIPS 140-3 Audit Log Chaining.

Desarrollado colaborativamente por:
Lázaro López Paz (El Prat de Llobregat, Barcelona, España) e Inteligencia Artificial.
"""

import os
import sys
import time
import json
import hashlib
from datetime import datetime, timezone
from typing import List, Dict, Any

class AuditLogMonitor:
    """
    Monitor de Integridad de Logs de Auditoría y Métricas de Criptografía Poscuántica.
    Verifica el encadenamiento criptográfico Hash-Chain (SHA-512) y evalúa los parámetros FIPS 140-3 / FIPS 204.
    """
    def __init__(self, log_file_path: str = "/workspace/scratch/fips_audit.log"):
        self.log_file_path = log_file_path
        self.metrics = {
            "total_audit_events": 0,
            "chain_integrity_verified": True,
            "broken_chain_count": 0,
            "entropy_health_alerts": 0,
            "mldsa_signatures_processed": 0,
            "catastrophic_failures_blocked": 0,
            "parameter_sets_seen": {"ML-DSA-44": 0, "ML-DSA-65": 0, "ML-DSA-87": 0},
            "last_event_timestamp": None
        }
        self.last_hash = "0" * 64

    def generate_simulated_audit_stream(self, num_events: int = 10) -> List[Dict[str, Any]]:
        """Genera una secuencia simulada de eventos de auditoría inmutables encadenados."""
        stream = []
        event_types = [
            ("DRBG_INSTANTIATED", {"strength": "256-bit", "sp80090a_type": "CTR_DRBG"}),
            ("ENTROPY_HEALTH_CHECK", {"rct_status": "PASSED", "apt_status": "PASSED"}),
            ("MLDSA_KEYGEN", {"param_set": "ML-DSA-65", "pk_bytes": 1952}),
            ("MLDSA_SIGN_HEDGED", {"param_set": "ML-DSA-65", "sig_bytes": 3309, "iterations": 4}),
            ("HASH_MLDSA_SIGN", {"param_set": "ML-DSA-87", "prehash_alg": "SHA-512", "digest_bytes": 64}),
            ("TOKEN_REFRESH_ROTATED", {"rfc7009": True, "grace_period_sec": 30}),
            ("ENTROPY_HEALTH_CHECK", {"rct_status": "PASSED", "apt_status": "PASSED"}),
            ("MLDSA_SIGN_HEDGED", {"param_set": "ML-DSA-87", "sig_bytes": 4627, "iterations": 3}),
            ("CATASTROPHIC_ENTROPY_SIMULATION", {"sp80090b_alert": False, "status": "CONTROLLED_TEST"}),
            ("LOG_CHAIN_CHECKPOINT", {"fips140_3_compliant": True})
        ]

        prev_hash = "0" * 64
        for i in range(min(num_events, len(event_types))):
            action, details = event_types[i]
            timestamp = datetime.now(timezone.utc).isoformat()
            
            raw_event = {
                "seq_id": i + 1,
                "timestamp": timestamp,
                "action": action,
                "details": details,
                "prev_hash": prev_hash
            }
            
            # Calcular hash encadenado SHA-512
            event_bytes = json.dumps(raw_event, sort_keys=True).encode()
            current_hash = hashlib.sha512(event_bytes).hexdigest()[:64]
            raw_event["current_hash"] = current_hash
            
            prev_hash = current_hash
            stream.append(raw_event)
            
        return stream

    def verify_log_chain(self, events: List[Dict[str, Any]]) -> bool:
        """Verifica la continuidad e inmutabilidad de la cadena de hashes SHA-512."""
        expected_prev_hash = "0" * 64
        valid_chain = True

        for ev in events:
            self.metrics["total_audit_events"] += 1
            self.metrics["last_event_timestamp"] = ev["timestamp"]

            # Verificar coincidencia de hash anterior
            if ev["prev_hash"] != expected_prev_hash:
                valid_chain = False
                self.metrics["broken_chain_count"] += 1

            # Recalcular hash del evento
            check_data = {
                "seq_id": ev["seq_id"],
                "timestamp": ev["timestamp"],
                "action": ev["action"],
                "details": ev["details"],
                "prev_hash": ev["prev_hash"]
            }
            computed_hash = hashlib.sha512(json.dumps(check_data, sort_keys=True).encode()).hexdigest()[:64]
            if computed_hash != ev["current_hash"]:
                valid_chain = False
                self.metrics["broken_chain_count"] += 1

            # Contabilizar métricas específicas
            action = ev["action"]
            details = ev.get("details", {})

            if "MLDSA" in action or "HASH_MLDSA" in action:
                self.metrics["mldsa_signatures_processed"] += 1
                param = details.get("param_set", "ML-DSA-65")
                if param in self.metrics["parameter_sets_seen"]:
                    self.metrics["parameter_sets_seen"][param] += 1

            if "CATASTROPHIC" in action or details.get("sp80090b_alert") is True:
                self.metrics["entropy_health_alerts"] += 1

            expected_prev_hash = ev["current_hash"]

        self.metrics["chain_integrity_verified"] = valid_chain
        return valid_chain

    def display_dashboard(self, events: List[Dict[str, Any]]):
        """Muestra el tablero de control de auditoría en tiempo real."""
        print("=" * 75)
        print(" 📊 TABLERO DE MONITORIZACIÓN Y MÉTRICAS DE AUDITORÍA EN TIEMPO REAL")
        print(" Ecosistema Quantum Blueprint — FIPS 140-3 / FIPS 204 / NIST SP 800-90B")
        print(" Autoría: Lázaro López Paz (El Prat de Llobregat, Barcelona) e IA")
        print("=" * 75)
        print(f"Estado de Integridad Hash-Chain: {'✅ INTACTO / VERIFICADO' if self.metrics['chain_integrity_verified'] else '❌ CORRUPTO'}")
        print(f"Total de Eventos Auditados:     {self.metrics['total_audit_events']}")
        print(f"Eslabones Rotos Detectados:     {self.metrics['broken_chain_count']}")
        print(f"Alertas de Entropía SP 800-90B: {self.metrics['entropy_health_alerts']}")
        print(f"Firmas ML-DSA Procesadas:       {self.metrics['mldsa_signatures_processed']}")
        print(f"Última Actualización (UTC):     {self.metrics['last_event_timestamp']}")
        print("-" * 75)
        print(" Distribución por Parámetro ML-DSA:")
        for k, v in self.metrics["parameter_sets_seen"].items():
            print(f"   - {k}: {v} firmas")
        print("-" * 75)
        print(" 🔍 MUESTRA DE SECUENCIA DE LOGS ENCADENADOS (SHA-512):")
        for ev in events[:4]:
            print(f"   [#00{ev['seq_id']}] {ev['action']} | Prev: {ev['prev_hash'][:12]}... | Hash: {ev['current_hash'][:12]}...")
        print("=" * 75)

def run_monitor():
    monitor = AuditLogMonitor()
    events = monitor.generate_simulated_audit_stream(10)
    monitor.verify_log_chain(events)
    monitor.display_dashboard(events)

if __name__ == "__main__":
    run_monitor()
