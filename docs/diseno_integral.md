# Diseño integral del prototipo

## Arquitectura

El prototipo se estructura como aplicación web con renderizado de plantillas HTML, lógica de negocio en Python y persistencia en SQLite para simulación local. La arquitectura permite ejecutar el sistema en un entorno controlado, validar los módulos comprometidos y documentar evidencia funcional correspondiente al nivel TRL5.

| Capa | Componente | Función |
|---|---|---|
| Presentación | Plantillas Jinja2, HTML y CSS | Presentar formularios, listas, detalles y reportes. |
| Aplicación | FastAPI | Administrar rutas, sesiones, validación de formularios y respuestas. |
| Dominio | Funciones de inventario, tickets, mantenimiento y reportes | Ejecutar reglas operativas del prototipo. |
| Persistencia | SQLite | Almacenar usuarios, activos, tickets, mantenimientos y bitácora. |
| Pruebas | Pytest y TestClient | Validar flujos funcionales principales. |

## Modelo de datos

| Tabla | Propósito | Campos principales |
|---|---|---|
| users | Gestionar usuarios y roles. | username, password_hash, full_name, email, role, active. |
| assets | Registrar activos tecnológicos. | code, name, category, brand, model, serial, location, status, responsible. |
| tickets | Gestionar solicitudes de soporte. | title, description, priority, status, asset_id, requester_id, assigned_to_id, resolution. |
| maintenance | Documentar intervenciones preventivas y correctivas. | asset_id, ticket_id, maintenance_type, description, performed_by, result, cost. |
| audit_logs | Registrar acciones críticas. | actor, action, entity, entity_id, detail, created_at. |

## Flujos funcionales

| Flujo | Secuencia |
|---|---|
| Autenticación | El usuario ingresa credenciales, el sistema valida hash de contraseña, crea sesión y registra auditoría. |
| Inventario | El administrador o soporte registra activo, consulta lista, edita datos y visualiza historial asociado. |
| Mesa de ayuda | El usuario crea ticket, soporte asigna responsable, actualiza estado, registra resolución y cierra caso. |
| Mantenimiento | Soporte registra intervención sobre activo, asocia ticket si aplica y actualiza estado operativo. |
| Reportes | El sistema calcula conteos por estado, tickets por prioridad, tiempo promedio de cierre y exportaciones CSV. |

## Reglas de negocio

| Código | Regla |
|---|---|
| RN-01 | Solo usuarios autenticados pueden ingresar a los módulos internos. |
| RN-02 | Solo roles administrador y soporte pueden crear o editar activos. |
| RN-03 | Todos los usuarios autenticados pueden crear tickets. |
| RN-04 | Solo roles administrador y soporte pueden asignar, actualizar o cerrar tickets. |
| RN-05 | Un mantenimiento debe estar asociado siempre a un activo. |
| RN-06 | Un mantenimiento puede asociarse a un ticket si la intervención se deriva de una solicitud de soporte. |
| RN-07 | El cierre de un ticket debe registrar resolución y fecha de cierre. |
| RN-08 | Las acciones críticas deben quedar registradas en bitácora. |

## Indicadores operativos

| Indicador | Cálculo | Uso esperado |
|---|---|---|
| Activos registrados | Conteo total de activos | Medir cobertura inicial de inventario. |
| Tickets abiertos | Conteo de tickets no cerrados | Identificar carga pendiente de soporte. |
| Tickets cerrados | Conteo de tickets cerrados | Medir atención acumulada. |
| Tiempo promedio de cierre | Diferencia promedio entre creación y cierre | Evaluar desempeño inicial de atención. |
| Mantenimientos registrados | Conteo total de intervenciones | Verificar trazabilidad de soporte técnico. |
