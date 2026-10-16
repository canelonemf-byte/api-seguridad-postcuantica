# LLP API Gateway v3.0

Gateway científico interoperable, sin dependencias externas, Python 3.8+.

## APIs

NASA Image and Video Library; PubChem PUG REST; RCSB PDB Search API v2; Wikimedia Commons; CERN Open Data; Crossref REST v1; OpenAlex; Europe PMC; ChEMBL; arXiv.

## Salida

- JSON compacto.
- JSONL: un registro por línea.
- Contrato: `llp.conector.v1`.
- Gateway: `llp.ecosystem_gateway.v1`.
- Sin `null`, sin campos vacíos, `snake_case`.
- No guarda ni imprime secretos.

## Resiliencia

- timeout configurable.
- reintentos con backoff.
- respeta `Retry-After` cuando existe.
- distingue errores HTTP de errores de transporte/parsing.
- limita el tamaño de respuesta.
- registra latencia e intentos.

## Seguridad e integración

Las credenciales, si una API las requiere, deben entrar por variables de entorno y nunca formar parte del JSONL. El catálogo actual no necesita autenticación para sus probes públicos. World Bank/Banco Mundial queda explícitamente excluido del ecosistema.

## Validación ejecutada

`py_compile` correcto y validación estructural del manifiesto: 10 APIs registradas.

No se declara una prueba en vivo de las 10 APIs en este entorno; la ejecución real depende de conectividad, límites y disponibilidad de cada servicio.
