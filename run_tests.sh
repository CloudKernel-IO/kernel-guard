#!/usr/bin/env bash
# Script para ejecutar tests localmente antes de commit

set -e

echo "🧪 Ejecutando suite de tests Kernel-Guard..."
echo ""

echo "📦 1. Verificando dependencias..."
pip install -q -e ".[test]"

echo "🔍 2. Ejecutando tests unitarios..."
pytest tests/test_main.py tests/test_reporter.py tests/test_providers.py tests/test_base_provider.py -v

echo "🔗 3. Ejecutando tests de integración..."
pytest tests/test_integration.py -v

echo "📊 4. Generando reporte de cobertura..."
pytest --cov=. --cov-report=term-missing --cov-report=html

echo "✅ 5. Verificando umbral de cobertura (80%)..."
pytest --cov=. --cov-fail-under=80

echo ""
echo "🎉 ¡Todos los tests pasaron! Cobertura > 80%"
echo "📄 Reporte HTML disponible en: htmlcov/index.html"
