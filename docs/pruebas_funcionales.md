# Pruebas funcionales

## Alcance de prueba

Las pruebas funcionales verifican los flujos mínimos exigidos para considerar el prototipo como componente validable en entorno simulado: autenticación, inventario, mesa de ayuda, cierre de tickets, reportes y exportación CSV.

| Caso | Flujo | Entrada | Resultado esperado |
|---|---|---|---|
| PF-01 | Autenticación | admin/admin123 | Acceso al panel de control. |
| PF-02 | Inventario | Registro de activo con código único | El activo aparece en la lista y se puede consultar. |
| PF-03 | Tickets | Creación de ticket con prioridad alta | El ticket queda abierto y asociado al solicitante. |
| PF-04 | Gestión de tickets | Cambio a estado Cerrado con resolución | El ticket conserva resolución y fecha de cierre. |
| PF-05 | Reportes | Consulta del panel de reportes | Se muestran métricas de activos y tickets. |
| PF-06 | Exportación | Descarga de activos CSV | El sistema responde con archivo text/csv. |

## Ejecución automática

```bash
pytest -q
```

## Resultado esperado de la prueba automatizada

```text
6 passed
```

## Observaciones de validación TRL5

El prototipo se valida en ambiente simulado con datos de demostración, usuarios de prueba, rutas funcionales y persistencia local. Este nivel permite evidenciar integración de componentes, operación básica y documentación técnica, sin afirmar despliegue productivo ni medición de impacto institucional de largo plazo.
