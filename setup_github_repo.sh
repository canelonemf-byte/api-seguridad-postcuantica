#!/usr/bin/env bash
# ==============================================================================
# Script de Configuración Local y Despliegue a GitHub
# Ecosistema Quantum Blueprint: Gobernanza, Seguridad y Simulación Cuántica
#
# Autores: Lázaro López Paz (El Prat de Llobregat, Barcelona, España) & IA
# Licencia: Apache License 2.0 (Copyright 2026)
# ==============================================================================

set -e

echo "🚀 Inicializando la preparación del repositorio local para GitHub..."

# 1. Crear estructura de carpetas de GitHub Actions
mkdir -p .github/workflows

# 2. Mover/Copiar el flujo de CI/CD
if [ -f "ci-cd.yml" ]; then
    cp ci-cd.yml .github/workflows/ci-cd.yml
    echo "  [✓] ci-cd.yml copiado a .github/workflows/ci-cd.yml"
fi

# 3. Actualizar README.md principal si existe README-v2.md
if [ -f "README-v2.md" ]; then
    cp README-v2.md README.md
    echo "  [✓] README-v2.md establecido como README.md principal"
fi

# 4. Inicializar repositorio git si no existe
if [ ! -d ".git" ]; then
    git init
    git branch -M main
    echo "  [✓] Repositorio Git inicializado en rama 'main'"
fi

# 5. Agregar archivos al control de versiones
git add .
echo "  [✓] Archivos añadidos al Staging de Git"

# 6. Crear Commit Inicial
git commit -m "feat: Ecosistema Quantum Blueprint v2.1.0 (ML-DSA FIPS 204, CI/CD, Tests y Licencia Apache 2.0)" || echo "  [!] No hay cambios pendientes por conmitear."

echo ""
echo "=============================================================================="
echo "🎉 ¡Preparación completada con éxito!"
echo "=============================================================================="
echo "Para publicar este repositorio en tu cuenta de GitHub, ejecuta los siguientes comandos:"
echo ""
echo "  1. Crea un nuevo repositorio público o privado en https://github.com/new"
echo "  2. En tu terminal local, vincula el remoto y sube el código:"
echo ""
echo "     git remote add origin https://github.com/TU_USUARIO/TU_REPOSO.git"
echo "     git push -u origin main"
echo ""
echo "=============================================================================="
