# Arandu

Ejercicio ARANDÚ 26 — Cdo FDR.

## board/

`board-administracion-personal.html` — Board de Administración de Personal.
Aplicación autónoma: se abre directamente en el navegador, sin servidor, sin
internet y sin dependencias externas. Apta para pen drive.

Módulos: situación general de efectivos, planilla numérica, organigrama y
asignación de puestos, rol de combate, rol de armamento, novedades sanitarias,
control de documentación, alertas de comando y gestión de datos.

Los datos se guardan en el `localStorage` del navegador donde se abre el
archivo: no viajan dentro del HTML. El respaldo y el traslado entre equipos se
harán mediante la exportación del módulo "Gestión de datos".
