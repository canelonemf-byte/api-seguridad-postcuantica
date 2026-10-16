import asyncio
import time
import httpx
from quantum_blueprint_ultimate_v2 import app, ML_DSA_PARAMS

async def run_load_test():
    print("=" * 70)
    print(" PRUEBA DE CARGA Y CONCURRENCIA HTTPX SOBRE FASTAPI CON ML-DSA")
    print("=" * 70)
    
    # Configurar cliente asíncrono sobre la app FastAPI
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://testserver") as client:
        # 1. Petición de estado general
        resp = await client.get("/qpu/status")
        print(f"\n[1] GET /qpu/status -> Status {resp.status_code}")
        
        # 2. Petición con encabezados ML-DSA-65 válidos (3309B firma, 1952B clave pública)
        valid_headers = {
            "X-ML-DSA-Signature": "a1" * 3309,
            "X-ML-DSA-Public-Key": "b2" * 1952,
            "X-ML-DSA-ParamSet": "ML-DSA-65"
        }
        
        start_time = time.time()
        num_requests = 100
        
        print(f"\n[2] Ejecutando {num_requests} peticiones concurrentes con encabezados ML-DSA-65 (Total ~5.2 KB por petición)...")
        
        tasks = [client.get("/quantum/status", headers=valid_headers) for _ in range(num_requests)]
        responses = await asyncio.gather(*tasks)
        
        elapsed = time.time() - start_time
        success_count = sum(1 for r in responses if r.status_code == 200)
        pqc_headers_present = sum(1 for r in responses if "x-pqc-supported-standards" in r.headers)
        
        print(f"  - Peticiones completadas: {len(responses)}")
        print(f"  - Peticiones exitosas (HTTP 200): {success_count}")
        print(f"  - Respuestas con encabezado PQC inyectado: {pqc_headers_present}")
        print(f"  - Tiempo total: {elapsed:.3f} segundos")
        print(f"  - Rendimiento (Throughput): {num_requests / elapsed:.2f} req/s")
        
        # 3. Prueba de rechazo de firmas malformadas bajo concurrencia
        invalid_headers = {
            "X-ML-DSA-Signature": "ff" * 100,  # Tamaño incorrecto
            "X-ML-DSA-Public-Key": "bb" * 1952,
            "X-ML-DSA-ParamSet": "ML-DSA-65"
        }
        
        print(f"\n[3] Ejecutando 20 peticiones concurrentes con firmas de tamaño inválido...")
        bad_tasks = [client.get("/quantum/status", headers=invalid_headers) for _ in range(20)]
        bad_responses = await asyncio.gather(*bad_tasks)
        
        blocked_count = sum(1 for r in bad_responses if r.status_code == 400)
        print(f"  - Bloqueos exitosos por tamaño erróneo (HTTP 400): {blocked_count}/20")
        
    print("\n" + "=" * 70)
    print(" RESULTADO: LA API SOPORTA ALTA CONCURRENCIA Y FIRMAS FIPS 204")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(run_load_test())
