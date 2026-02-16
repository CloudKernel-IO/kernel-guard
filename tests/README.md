# Tests - Kernel-Guard

Suite completa de tests para Kernel-Guard: unitarios, integración y cobertura.

## 📋 Estructura

```
tests/
├── __init__.py              # Marca el directorio como paquete
├── conftest.py              # Fixtures compartidos para todos los tests
├── test_base_provider.py    # Tests de la clase base CloudProvider
├── test_main.py             # Tests unitarios de main.py
├── test_reporter.py         # Tests unitarios de Reporter
├── test_providers.py        # Tests unitarios de Azure/AWS/GCP providers
└── test_integration.py      # Tests de integración end-to-end
```

## 🚀 Instalación de dependencias

```bash
# Instalar dependencias de test
pip install -e ".[test]"

# O manualmente
pip install pytest pytest-cov pytest-mock moto freezegun
```

## ▶️ Ejecutar los tests

### Todos los tests con cobertura
```bash
pytest
```

### Solo tests unitarios
```bash
pytest tests/test_main.py tests/test_reporter.py tests/test_providers.py
```

### Solo tests de integración
```bash
pytest tests/test_integration.py
```

### Test específico
```bash
pytest tests/test_main.py::TestClassifySeverity::test_critical_severity_with_emoji
```

### Con más verbosidad
```bash
pytest -v
```

### Sin captura de output (ver prints)
```bash
pytest -s
```

## 📊 Cobertura de Código

### Generar reporte HTML
```bash
pytest --cov=. --cov-report=html
```

El reporte se genera en `htmlcov/index.html`

### Ver cobertura en terminal
```bash
pytest --cov=. --cov-report=term-missing
```

### Verificar umbral mínimo (80%)
```bash
pytest --cov=. --cov-fail-under=80
```

## 🧪 Tests incluidos

### Tests Unitarios

#### `test_main.py`
- ✅ Clasificación de severidad (HIGH/MEDIUM/LOW/INFO)
- ✅ Ejecución de scan por cloud (Azure/AWS/GCP)
- ✅ Generación de reportes opcionales
- ✅ Manejo de errores

#### `test_reporter.py`
- ✅ Generación de archivos HTML
- ✅ Estructura HTML correcta
- ✅ Inclusión de todos los resultados
- ✅ Aplicación de estilos CSS
- ✅ Manejo de listas vacías

#### `test_providers.py`
- ✅ **Azure**: Discos huérfanos, SQL TDE, Storage público, NSG abiertos
- ✅ **AWS**: S3 público, IAM keys viejas, EIPs huérfanos, SG abiertos, volúmenes sin encriptar
- ✅ **GCP**: VMs con IP pública, discos sin KMS, discos huérfanos

#### `test_base_provider.py`
- ✅ Clase abstracta CloudProvider
- ✅ Método scan() no implementado
- ✅ Herencia correcta

### Tests de Integración

#### `test_integration.py`
- ✅ Scan completo de Azure con reporte
- ✅ Scan completo de AWS con todos los checks
- ✅ Scan completo de GCP
- ✅ Manejo de errores de autenticación
- ✅ Formato de salida en consola

## 🎯 Objetivos de Cobertura

| Módulo | Objetivo | Estado |
|--------|----------|--------|
| main.py | 90%+ | ✅ |
| core/reporter.py | 90%+ | ✅ |
| core/base_provider.py | 100% | ✅ |
| providers/*.py | 80%+ | ✅ |

## 🔧 Fixtures Disponibles

Ver `conftest.py` para fixtures reutilizables:

- `mock_azure_credential` - Credenciales de Azure mockeadas
- `mock_azure_resource_client` - Cliente de recursos de Azure
- `mock_boto3_session` - Sesión de boto3 para AWS
- `mock_gcp_instances_client` - Cliente de instancias GCP
- `mock_gcp_disks_client` - Cliente de discos GCP
- `sample_results` - Datos de ejemplo para tests
- `mock_datetime` - Datetime controlado para tests determinísticos

## 📝 Convenciones

- **Nomenclatura**: `test_<funcionalidad>_<escenario>`
- **Organización**: Tests agrupados en clases por componente
- **Mocks**: Usar `@patch` para dependencias externas
- **Assertions**: Verificar comportamiento Y estado

## 🐛 Debugging

```bash
# Ejecutar test específico con pdb
pytest tests/test_main.py::test_azure_scan -v --pdb

# Ver warnings
pytest -v -W all

# Mostrar fixtures disponibles
pytest --fixtures
```

## 🔄 CI/CD

Los tests se configuran para ejecutarse automáticamente en:
- Pre-commit (opcional)
- Pull Requests
- Push a main

Configuración mínima en `.github/workflows/tests.yml` (ver archivo adjunto)

## ✅ Checklist antes de commit

- [ ] Todos los tests pasan: `pytest`
- [ ] Cobertura > 80%: `pytest --cov=. --cov-fail-under=80`
- [ ] Sin errores de linting (si aplica): `ruff check .`
- [ ] Nuevos tests para nuevo código
