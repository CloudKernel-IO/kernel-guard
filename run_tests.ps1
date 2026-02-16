# PowerShell script para ejecutar tests en Windows

Write-Host "🧪 Ejecutando suite de tests Kernel-Guard..." -ForegroundColor Cyan
Write-Host ""

Write-Host "📦 1. Verificando dependencias..." -ForegroundColor Yellow
pip install -q -e ".[test]"

Write-Host "🔍 2. Ejecutando tests unitarios..." -ForegroundColor Yellow
pytest tests/test_main.py tests/test_reporter.py tests/test_providers.py tests/test_base_provider.py -v

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Tests unitarios fallaron" -ForegroundColor Red
    exit 1
}

Write-Host "🔗 3. Ejecutando tests de integración..." -ForegroundColor Yellow
pytest tests/test_integration.py -v

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Tests de integración fallaron" -ForegroundColor Red
    exit 1
}

Write-Host "📊 4. Generando reporte de cobertura..." -ForegroundColor Yellow
pytest --cov=. --cov-report=term-missing --cov-report=html

Write-Host "✅ 5. Verificando umbral de cobertura (80%)..." -ForegroundColor Yellow
pytest --cov=. --cov-fail-under=80

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "🎉 ¡Todos los tests pasaron! Cobertura > 80%" -ForegroundColor Green
    Write-Host "📄 Reporte HTML disponible en: htmlcov/index.html" -ForegroundColor Cyan
} else {
    Write-Host "❌ Cobertura insuficiente (< 80%)" -ForegroundColor Red
    exit 1
}
