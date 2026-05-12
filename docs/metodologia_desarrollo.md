# Metodología de desarrollo

## Enfoque general

El desarrollo del prototipo se organiza mediante un enfoque ágil basado en Scrum, articulado con el ciclo CDIO: concebir, diseñar, implementar y operar. Scrum se utiliza para ordenar el trabajo en iteraciones cortas, priorizar historias de usuario y validar incrementos funcionales; CDIO se usa como marco ingenieril para asegurar que el problema institucional se traduzca en una solución construida y operada en entorno simulado.

## Roles del proyecto

| Rol | Responsabilidad en el prototipo |
|---|---|
| Product owner académico | Define alcance, criterios de aceptación y prioridad de módulos. |
| Desarrollador | Construye backend, interfaz, base de datos y pruebas funcionales. |
| Usuario validador | Ejecuta flujos de prueba de inventario, tickets y mantenimiento. |
| Tutor | Revisa evidencia, repositorio, documentación y demostración funcional. |

## Sprints definidos

| Sprint | Fase CDIO | Producto del sprint | Evidencia |
|---|---|---|---|
| Sprint 1 | Concebir | Diagnóstico operativo y backlog priorizado | Historias de usuario y matriz de requerimientos |
| Sprint 2 | Diseñar | Arquitectura, modelo de datos e interfaces base | Diseño integral y prototipos de navegación |
| Sprint 3 | Implementar | Módulo de autenticación e inventario | Código, pruebas y registros de activos |
| Sprint 4 | Implementar | Módulo de tickets y mantenimiento | Código, pruebas y flujos de soporte |
| Sprint 5 | Operar | Reportes, exportaciones y validación TRL5 | Pruebas funcionales, bitácora y guía de video |

## Criterios de aceptación global

| Criterio | Verificación |
|---|---|
| El sistema permite iniciar sesión con roles diferenciados. | Prueba funcional de autenticación. |
| El sistema permite registrar, consultar y editar activos tecnológicos. | Prueba funcional de inventario. |
| El sistema permite crear, asignar y cerrar tickets de soporte. | Prueba funcional de mesa de ayuda. |
| El sistema permite registrar mantenimientos preventivos y correctivos. | Prueba funcional de mantenimiento. |
| El sistema presenta reportes operativos y exportación CSV. | Prueba funcional de reportes. |
| El sistema cuenta con documentación mínima para ejecución y socialización. | README, diseño integral, pruebas y guía de video. |

## Control de cambios

Las modificaciones del prototipo deben registrarse mediante commits de Git con mensajes descriptivos, de modo que el tutor pueda consultar trazabilidad del código y evidenciar el avance incremental del desarrollo.
