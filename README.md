# 🛡️ Kernel-Guard

> **Infrastructure Drift & Security Compliance Engine**

[![Poetry](https://img.shields.io/endpoint?url=https://python-poetry.org/badge/v0.json)](https://python-poetry.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/tests-44%20passed-brightgreen.svg)](tests/)
[![Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen.svg)](htmlcov/)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/)

**Kernel-Guard** es el motor de cumplimiento de [CloudKernel.app](https://cloudkernel.app). Su misión es garantizar que la infraestructura cloud desplegada no sufra desviaciones (*drift*) respecto a las definiciones de Infraestructura como Código (IaC) y los estándares de seguridad corporativos.

---

## 🚀 Capacidades Core

* **Drift Analytics**: Identifica en tiempo real recursos creados o modificados manualmente a través del portal de Azure/AWS.
* **Compliance Enforcement**: Verifica que cada recurso cumpla con el esquema de etiquetado (`ManagedBy: Terraform`) y políticas de exposición.
* **Security Guardrails**: Alerta temprana sobre configuraciones de red inseguras o recursos huérfanos.
* **Multi-Cloud Ready**: Diseñado para integrarse en arquitecturas híbridas.

## 🛠️ Stack Tecnológico

* **Lenguaje:** Python 3.11+
* **Gestión de Dependencias:** [Poetry](https://python-poetry.org/)
* **Integración:** Azure SDK for Python / Boto3

## 📦 Instalación

Asegúrate de tener Poetry instalado.

```bash
# Instalar dependencias de producción
poetry install

# Instalar dependencias de test
pip install -e ".[test]"

# Activar el entorno virtual
poetry shell
```

## 🧪 Testing

El proyecto cuenta con una **suite completa de tests** con **100% de cobertura de código**.

### 📊 Estadísticas

```
✅ 44 tests pasados
✅ 100% de cobertura de código
✅ Tests unitarios + integración
```

| Módulo | Tests | Cobertura |
|--------|-------|-----------|
| `main.py` | 13 | 100% |
| `core/reporter.py` | 8 | 100% |
| `core/base_provider.py` | 6 | 100% |
| `providers/azure_provider.py` | 4 | 100% |
| `providers/aws_provider.py` | 4 | 100% |
| `providers/gcp_provider.py` | 3 | 100% |
| **Integración end-to-end** | 6 | 100% |

### ⚡ Ejecución Rápida

```bash
# Opción 1: Script automatizado (recomendado)
.\run_tests.ps1              # Windows
./run_tests.sh               # Linux/Mac

# Opción 2: Pytest directo
pytest                       # Ejecutar todos los tests
pytest -v                    # Con salida verbosa
```

### 🎯 Tests Específicos

```bash
# Tests unitarios por módulo
pytest tests/test_main.py              # Lógica principal y clasificación
pytest tests/test_reporter.py          # Generación de reportes HTML
pytest tests/test_providers.py         # Providers Azure/AWS/GCP
pytest tests/test_base_provider.py     # Clase base abstracta

# Tests de integración
pytest tests/test_integration.py       # End-to-end completos

# Ejecutar un test específico
pytest tests/test_main.py::TestClassifySeverity::test_critical_severity_with_emoji
```

### 📈 Reportes de Cobertura

```bash
# Reporte HTML interactivo (abre htmlcov/index.html)
pytest --cov=. --cov-report=html

# Reporte en terminal con líneas faltantes
pytest --cov=. --cov-report=term-missing

# Verificar umbral mínimo (configurado en 80%)
pytest --cov-fail-under=80
```

### 🧩 Tipos de Tests Incluidos

**Tests Unitarios** (35 tests):
- ✅ Clasificación de severidad (HIGH/MEDIUM/LOW/INFO)
- ✅ Escaneo por cloud provider (Azure/AWS/GCP)
- ✅ Generación de reportes HTML con estilos
- ✅ Detección de vulnerabilidades específicas:
  - Azure: Discos huérfanos, SQL TDE, Storage público, NSG abiertos
  - AWS: S3 público, IAM keys antiguas, EIPs huérfanos, volúmenes sin encriptar
  - GCP: VMs con IP pública, discos sin KMS, recursos huérfanos

**Tests de Integración** (6 tests):
- ✅ Flujo completo Azure → Reporte HTML
- ✅ Flujo completo AWS con múltiples checks
- ✅ Flujo completo GCP
- ✅ Manejo de errores de autenticación
- ✅ Formato de salida en consola
- ✅ Validación de argumentos CLI

### 🔧 Configuración

Los tests utilizan **mocks** para simular las APIs de cloud providers, por lo que:
- ✅ No requieren credenciales reales
- ✅ Se ejecutan en milisegundos
- ✅ Son determinísticos y reproducibles
- ✅ Pueden ejecutarse en CI/CD

### 📚 Documentación Detallada

Ver [tests/README.md](tests/README.md) para:
- Estructura completa de tests
- Fixtures disponibles
- Convenciones de testing
- Debugging y troubleshooting
- Configuración de CI/CD

## 📄 Licencia

MIT License - ver [LICENSE](LICENSE) para más información.