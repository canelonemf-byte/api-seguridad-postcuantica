# Quantum Blueprint: Gobernanza, Seguridad y Simulación Cuántica (v2.1.0)

> **Autoría y Desarrollo**: Realizado de forma colaborativa por **Lázaro López Paz** (El Prat de Llobregat, Barcelona, España) e **Inteligencia Artificial**.

---

## 📌 Descripción del Proyecto

**Quantum Blueprint** es un ecosistema unificado en **FastAPI** y **Python** diseñado para la gobernanza, simulación cuántica acelerada y protección criptográfica de la cadena de suministro (*supply chain*). El sistema integra autenticación avanzada con rotación de tokens antirrobo, conectores para plataformas QPU (IBM Quantum e IonQ), un simulador cuántico local y un middleware de seguridad poscuántica basado en el estándar **NIST FIPS 204 (ML-DSA)**.

---

## 🚀 Arquitectura y Componentes Principales

1. **API Backend (`quantum_blueprint_ultimate_v2.py`)**:
   - **FastAPI v2.1.0** & **SQLAlchemy** con motor SQLite.
   - **Rotación Antirrobo de Refresh Tokens**: Expiración a 30 días, hashing SHA-256 y detección automática de reutilización con revocación en cascada por familias de tokens (RFC 7009).
   - **Gobernanza QPU**: Auditoría de credenciales y SDKs (`qiskit_ibm_runtime`, `qiskit_ionq`) condicionada a la variable `HUMAN_APPROVAL=1`.
   - **Simulación Cuántica**: Motor `AerSimulator` con aceleración GPU y *fallback* transparente a CPU.

2. **Middleware Poscuántico ML-DSA (NIST FIPS 204)**:
   - Validación automática de firmas digitales en los encabezados HTTP (`X-ML-DSA-Signature`, `X-ML-DSA-Public-Key`, `X-ML-DSA-ParamSet`).
   - Verificación estricta de tamaños FIPS 204 (**ML-DSA-44**, **ML-DSA-65**, **ML-DSA-87**).
   - Soporte para **HashML-DSA** (Pre-hash con SHA-512) para el firmado eficiente de artefactos pesados.

---

## ⚙️ Integración Continua (CI/CD) con GitHub Actions

Crea el archivo `.github/workflows/ci-cd.yml` en el repositorio para automatizar las pruebas unitarias, los benchmarks poscuánticos y la construcción de la imagen Docker:

```yaml
name: Quantum Blueprint CI/CD Pipeline

on:
  push:
    branches: [ "main", "develop" ]
  pull_request:
    branches: [ "main" ]

jobs:
  test-and-benchmark:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout Código
      uses: actions/checkout@v4

    - name: Configurar Python 3.12
      uses: actions/setup-python@v5
      with:
        python-version: '3.12'

    - name: Instalar Dependencias
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install httpx pytest

    - name: Ejecutar Pruebas de Unidad y Seguridad
      run: |
        python -m unittest discover -s . -p "test_*.py"

    - name: Ejecutar Benchmark HashML-DSA (FIPS 204)
      run: |
        python hash_mldsa_benchmark.py

    - name: Ejecutar Prueba de Carga Concurrente HTTPX
      run: |
        python load_test_mldsa.py

  docker-build:
    needs: test-and-benchmark
    runs-on: ubuntu-latest

    steps:
    - name: Checkout Código
      uses: actions/checkout@v4

    - name: Construir Imagen Docker
      run: |
        docker build -t quantum-blueprint:v2.1.0 .

    - name: Verificar Contenedor con Buffer 64KB (Uvicorn)
      run: |
        docker run -d -p 8000:8000 --name quantum_app quantum-blueprint:v2.1.0
        sleep 3
        curl -I http://localhost:8000/qpu/status
        docker stop quantum_app
```

---

## 🛠️ Despliegue en Producción (Docker & Uvicorn)

El servidor requiere la ampliación del buffer de encabezados HTTP a **64 KB** para procesar las firmas poscuánticas sin rechazar peticiones:

```bash
# Construcción
docker build -t quantum-blueprint:v2.1.0 .

# Ejecución
docker run -d -p 8000:8000 -e HUMAN_APPROVAL=1 quantum-blueprint:v2.1.0
```

---

## 📄 Licencia y Protección Legal de Autoría

Este proyecto está distribuido bajo la **Licencia Apache 2.0** (Apache License, Version 2.0).

```text
Copyright 2026 Lázaro López Paz (El Prat de Llobregat, Barcelona, España) e Inteligencia Artificial

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```

---

## 📊 Créditos y Autoría

* **Dirección del Proyecto, Concepto y Arquitectura**: **Lázaro López Paz** (El Prat de Llobregat, Barcelona, España).
* **Co-desarrollo e Implementación**: **Inteligencia Artificial**.
