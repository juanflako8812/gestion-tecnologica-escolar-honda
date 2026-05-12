# Requerimientos del prototipo

## Actores

| Actor | Descripción operativa |
|---|---|
| Administrador | Usuario con permisos para gestionar activos, tickets, mantenimientos, reportes y bitácora. |
| Soporte | Usuario responsable de atender tickets y registrar intervenciones técnicas. |
| Usuario solicitante | Usuario que reporta fallas o necesidades de soporte asociadas a recursos tecnológicos. |

## Requerimientos funcionales

| Código | Requerimiento | Prioridad | Criterio de aceptación |
|---|---|---|---|
| RF-01 | El sistema debe permitir iniciar y cerrar sesión. | Alta | El usuario autenticado accede al panel y el usuario no autenticado es redirigido al ingreso. |
| RF-02 | El sistema debe permitir registrar activos tecnológicos. | Alta | El activo queda almacenado con código, nombre, categoría, ubicación, estado y responsable. |
| RF-03 | El sistema debe permitir consultar y filtrar activos. | Alta | La lista permite búsqueda por texto y filtrado por estado. |
| RF-04 | El sistema debe permitir editar activos. | Alta | Los cambios quedan actualizados y visibles en el detalle del activo. |
| RF-05 | El sistema debe permitir crear tickets de soporte. | Alta | El ticket queda registrado con título, descripción, prioridad, solicitante y activo asociado opcional. |
| RF-06 | El sistema debe permitir asignar y cerrar tickets. | Alta | El ticket cambia de estado, registra responsable, resolución y fecha de cierre. |
| RF-07 | El sistema debe permitir registrar mantenimientos. | Alta | La intervención queda asociada a un activo y, de forma opcional, a un ticket. |
| RF-08 | El sistema debe permitir visualizar reportes básicos. | Media | El panel muestra conteos de activos, tickets y tiempo promedio de resolución. |
| RF-09 | El sistema debe permitir exportar activos y tickets en CSV. | Media | La descarga genera archivos CSV con campos operativos. |
| RF-10 | El sistema debe registrar bitácora de acciones críticas. | Media | Inicio de sesión, creación y actualización quedan registrados con actor, acción y fecha. |

## Requerimientos no funcionales

| Código | Requerimiento | Criterio de aceptación |
|---|---|---|
| RNF-01 | Usabilidad | La navegación debe permitir acceder a inventario, tickets, mantenimiento y reportes desde el menú principal. |
| RNF-02 | Seguridad básica | Las contraseñas se almacenan mediante hash PBKDF2 y las sesiones se administran con middleware de sesión. |
| RNF-03 | Portabilidad | El prototipo debe ejecutarse localmente con Python y dependencias declaradas en requirements.txt. |
| RNF-04 | Mantenibilidad | El código debe estar separado en módulos de aplicación, base de datos, autenticación, plantillas y pruebas. |
| RNF-05 | Trazabilidad | Las operaciones críticas deben quedar registradas en la tabla de auditoría. |
| RNF-06 | Validación | El prototipo debe incluir pruebas automatizadas ejecutables con pytest. |

## Historias de usuario

| Código | Historia de usuario | Criterio de aceptación |
|---|---|---|
| HU-01 | Como administrador, se requiere registrar activos para conocer los recursos tecnológicos disponibles. | El activo creado aparece en la lista y en el detalle. |
| HU-02 | Como usuario solicitante, se requiere reportar una falla para que soporte pueda atenderla. | El ticket queda en estado abierto y asociado al solicitante. |
| HU-03 | Como responsable de soporte, se requiere asignar y cerrar tickets para documentar la atención realizada. | El ticket cerrado registra resolución y fecha de cierre. |
| HU-04 | Como responsable institucional, se requiere consultar reportes para priorizar mantenimiento y reposición. | El panel muestra métricas agregadas y permite exportar CSV. |
| HU-05 | Como tutor evaluador, se requiere revisar código y pruebas para verificar el cumplimiento TRL5. | El repositorio contiene código, documentación, pruebas y guía de socialización. |
