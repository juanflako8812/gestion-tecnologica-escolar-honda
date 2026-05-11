# Prototipo TRL5: Gestión tecnológica escolar

## Identificación del proyecto

**Título:** Diseño e implementación de un prototipo funcional de plataforma web para la gestión tecnológica escolar en una institución educativa de Honda, Tolima.

**Propósito:** centralizar el inventario de activos tecnológicos, la mesa de ayuda y el seguimiento de mantenimiento para mejorar la trazabilidad operativa de equipos, solicitudes e intervenciones técnicas en contexto escolar.

**Nivel de maduración tecnológica:** TRL5, validación de componentes en entorno simulado con datos de prueba, usuarios demo, pruebas funcionales automatizadas y documentación técnica.

## Alcance funcional

El prototipo incluye los siguientes módulos:

- Autenticación con roles: administrador, soporte y usuario solicitante.
- Inventario de activos tecnológicos: registro, edición, consulta, estado, ubicación y responsable.
- Mesa de ayuda: creación, asignación, priorización, cierre y trazabilidad de tickets.
- Mantenimiento: registro de intervenciones preventivas y correctivas asociadas a activos.
- Reportes operativos: métricas de activos, tickets, cierres, prioridades y tiempo promedio de atención.
- Exportación CSV para inventario y tickets.
- Bitácora básica de acciones críticas.

## Tecnologías usadas

- Python 3.11 o superior.
- FastAPI.
- Uvicorn.
- Jinja2.
- SQLite para simulación local.
- HTML, CSS y JavaScript básico.
- Pytest para pruebas funcionales.

## Instalación local

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\\Scripts\\activate     # Windows
pip install -r requirements.txt
```

## Ejecución del prototipo

```bash
uvicorn app.main:app --reload
```

Luego se ingresa en el navegador a:

```text
http://127.0.0.1:8000
```

## Usuarios de demostración

| Rol | Usuario | Contraseña |
|---|---|---|
| Administrador | admin | admin123 |
| Soporte | soporte | soporte123 |
| Usuario solicitante | docente | docente123 |

Las credenciales anteriores son únicamente para el entorno simulado del prototipo; para operación real deben reemplazarse por credenciales institucionales y política de contraseñas definida.

## Pruebas

```bash
pytest -q
```

Las pruebas verifican autenticación, creación de activos, creación y cierre de tickets, consulta de reportes y exportación de información.

## Preparación del repositorio en GitHub

El proyecto queda listo para ser subido al repositorio:

```bash
git init
git add .
git commit -m "Prototipo TRL5 de gestion tecnologica escolar"
git branch -M main
git remote add origin https://github.com/juanflako8812/gestion-tecnologica-escolar-honda.git
git push -u origin main
```

Cuando el repositorio exista y el contenido sea cargado, el enlace público será:

```text
https://github.com/juanflako8812/gestion-tecnologica-escolar-honda
```

## Estructura del proyecto

```text
app/
  main.py
  database.py
  auth.py
  templates/
  static/css/app.css
docs/
  metodologia_desarrollo.md
  requerimientos.md
  diseno_integral.md
  pruebas_funcionales.md
  guia_video_socializacion.md
tests/
  test_app.py
.github/workflows/
  tests.yml
requirements.txt
README.md
```

## Evidencia para fase práctica

Este paquete contiene código funcional, documentación de metodología de desarrollo, requerimientos, diseño integral, pruebas funcionales, manual breve de ejecución y guía para grabar el video de socialización de máximo 10 minutos.
