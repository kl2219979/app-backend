#!/usr/bin/env bash
# -----------------------------------------------------------------------------
# setup.sh
# -----------------------------------------------------------------------------
# QUÉ ES:
#   Preparación inicial del proyecto en tu máquina (una vez, o cuando cambien deps).
#
# POR QUÉ EXISTE:
#   Evita pasos manuales olvidados: venv, pip install, archivo .env, permisos.
#
# QUÉ HACE:
#   - Crea .venv si no existe
#   - Instala requirements-dev.txt (app + pytest + ruff)
#   - Copia .env.example → .env si aún no tienes .env
#   - Da permiso de ejecución a migrate/entrypoint
#
# QUÉ NO HACE:
#   No enciende la base ni la API. Eso lo haces después (ver mensajes al final).
#
# Guía completa: docs/COMO_FUNCIONA.md
# -----------------------------------------------------------------------------
set -euo pipefail

cd "$(dirname "$0")/.."

if [ ! -d ".venv" ]; then
  echo "[setup] Creando entorno virtual .venv ..."
  python3 -m venv .venv
fi

# shellcheck disable=SC1091
source .venv/bin/activate
echo "[setup] Instalando dependencias..."
pip install -r requirements-dev.txt

if [ ! -f ".env" ]; then
  cp .env.example .env
  echo "[setup] Creado .env a partir de .env.example (ajusta secretos si hace falta)."
fi

chmod +x scripts/migrate.sh scripts/entrypoint.sh

echo ""
echo "[setup] Entorno listo."
echo ""
echo "Siguiente (BD desacoplada + Alembic crea las tablas):"
echo "  1. docker compose up db -d"
echo "  2. ./scripts/migrate.sh"
echo "  3. source .venv/bin/activate && uvicorn app.main:app --reload"
echo ""
echo "Lee docs/COMO_FUNCIONA.md si quieres entender el porqué de cada paso."
echo "O todo junto: docker compose up --build"
