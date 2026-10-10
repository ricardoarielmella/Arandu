# Board de logística — Ejercicio Arandú 2026

Un solo HTML (`board-logistica-arandu.html`) y dos archivos de datos. El board detecta el tipo de JSON al cargarlo y muestra solo las pestañas que corresponden.

| Archivo | Campo `tipo` | Contenido |
|---|---|---|
| Logística de personal | `logistica-personal` | Datos personales, bancarios y de emergencia, situación militar, rol de combate, organigrama, parte sanitaria, documentación, fotografía de legajo (120 px), edad. |
| Logística de material | `logistica-material` | Embarque, vehículo de marcha (conductor o pasajero), armamento y material, licencia, QR (texto y datos), nacimiento y sexo para Migraciones. |

DNI, grado, apellido y nombre viajan en ambos. El DNI vincula a cada efectivo entre los dos archivos. Cada campo tiene un único archivo responsable.

## Imágenes de DNI y QR

No viajan dentro del JSON. Se guardan en el equipo (IndexedDB) y se importan como archivos sueltos o ZIP, nombrados `DNI_dni.jpg` y `DNI_qr.jpg`. La descarga genera ZIP de unos 25 MB.

## Seguridad

El repositorio es público: los JSON, las imágenes y cualquier archivo con datos personales no se versionan (`.gitignore`).
