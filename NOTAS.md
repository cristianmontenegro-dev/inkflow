  Diario de desarrollo

## 2026-10-09 — Día 1

✅ Logros
- Sitio InkFlow online en GitHub Pages
- Repo profesional con README
- Python 3.14.8 instalado
- Primer script: calculadora de tatuajes

🧠 Aprendí
- GitHub Pages ignora archivos sin `.nojekyll`
- Diferencia entre rutas `css/styles.css` y `styles.css`
- Python: `input()`, `float()`, diccionarios, `f-strings`

 🎯 Próximo lunes
- Agregar descuento a la calculadora
- Agregar sección "Diario de práctica" al sitio
- Bloque de 75 min (30 Python + 30 InkFlow + 10 commit)

## 2026-10-13 — Día 2

 ✅ Logros
- Descuento del 15% para clientes recurrentes
- Instagram agregado al footer

 🧠 Aprendí
- Condicionales `if` en Python
- Cómo aplicar porcentajes a variables

  ## 2026-10-14 — Día 3

 ✅ Logros
- Cotizaciones se guardan en `cotizaciones.txt`
- Historial con fecha, cliente, zona, precio

 🧠 Aprendí
- `open("archivo.txt", "a")` = agregar sin borrar
- `datetime.now()` para fecha/hora actual
- F-strings con variables: `f"Hola {nombre}"`

  ## 2026-10-15 — Día 4

 ✅ Logros
- Script `estadisticas.py` lee cotizaciones.txt
- Calcula: total, promedio, cliente más caro

 🧠 Aprendí
- `open(..., "r")` para leer archivos
- `.split("|")` corta strings en partes
- `.replace()` limpia texto
- `sum()`, `max()`, `len()` built-in
- Listas con `.append()`

  ## 2026-10-16 — Día 5

 ✅ Logros
- Zona más pedida agregada a estadísticas
- Script analiza 5 datos: total, clientes, promedio, más caro, zona top

 🧠 Aprendí
- Diccionarios `{}` para contar cosas
- `if x in diccionario` pa' verificar si existe
- `max(dicc, key=dicc.get)` para encontrar el mayor

  ## 2026-10-19 — Día 6 (Semana 2)

 ✅ Logros
- Instalé Flask.
- Creé mi primer servidor web con Python.
- Conecté el backend (Python) con el frontend (HTML/CSS).
- Agregué rutas nuevas (`/contacto`).

  ## 2026-10-20 — Día 7 (Conexión Frontend-Backend)

 ✅ Logros
- Creé un formulario HTML conectado a Flask.
- Python recibe los datos (POST) y los guarda en `reservas.txt`.
- El ciclo de enviar y recibir datos funciona perfecto.

 🧠 Aprendí
- Uso de `request.form.get()` para leer datos.
- Atributos HTML: `action` y `method="POST"`.
- Flujo completo de una aplicación web.

 🧠 Aprendí
- Qué es un servidor y cómo funciona.
- El decorador `@app.route()`.
- A usar `render_template()` para buscar HTML.
- La importancia de las carpetas `templates` y `static`.

  ## 2026-10-21 — Día 8 (Panel de Control)

 ✅ Logros
- Flask lee el archivo `reservas.txt` y lo envía al HTML.
- Uso de Jinja2 para mostrar datos dinámicos.
- Redirección al inicio después de enviar el formulario.

 🧠 Aprendí
- `{% for %}` y `{% if %}` en Jinja2.
- Manejo de errores con `try/except` (por si el archivo no existe).
- `redirect()` y `url_for()` en Flask.

  ## 2026-10-22 — Día 9 (SQLite)

 ✅ Logros
- Migré las reservas de un archivo .txt a una base de datos SQLite.
- Flask lee la base de datos y muestra los datos con sus IDs.

  ## 2026-10-23 — Día 10 (CRUD Completo)

 ✅ Logros
- Completé el ciclo CRUD (Create, Read, Delete).
- Agregué botón para borrar reservas con SQLite.
- Creé `.gitignore` para proteger la base de datos.
- Instalé SQLite Viewer en VS Code para ver las tablas como Excel.

 🧠 Aprendí
- El comando `DELETE FROM` en SQL.
- El uso de la etiqueta `<a>` para botones.
- Parámetros dinámicos en rutas de Flask: `/borrar/<int:id>`.
- Cómo inspeccionar una base de datos relacional.
- Las tarjetas se ven profesionales con la etiqueta del ID.

 🧠 Aprendí
- Consultas SQL básicas (CREATE TABLE, INSERT, SELECT).
- Manejo de tuplas en Python y Jinja2.
- Uso de `sqlite3` en Flask.

  ## 2026-10-26 — Día 11 (Confirmación de borrado)

 ✅ Logros
- Agregué un pop-up de confirmación con JavaScript al botón de borrar.
- Jinja2 inyecta el nombre del cliente en la alerta de JS.

 🧠 Aprendí
- Uso de `onclick` en HTML.
- Función `confirm()` de JavaScript.
- Cómo mezclar variables de Python en código JS.

  ## 2026-10-27 — Día 12 (Despliegue a Producción)

 ✅ Logros
- Configuré `requirements.txt` y `Procfile`.
- Subí InkFlow a Render.
- **La aplicación está en vivo en internet.** 🚀

🧠 Aprendí
- Qué es Gunicorn y para qué sirve en producción.
- Cómo desplegar aplicaciones Flask en la nube.
- El funcionamiento del plan gratuito de Render.

## 2026-10-28 — Día 13 (Panel de Administrador y CRUD Completo)

 ✅ Logros
- Separé la vista pública (`/`) de la vista de administrador (`/admin`).
- Agregué la ruta `/editar/<id>` y el archivo `editar.html`.
- Completé el CRUD al 100% (Crear, Leer, Actualizar y Borrar).

 🧠 Aprendí
- A crear rutas con múltiples métodos (`methods=['GET', 'POST']`).
- A usar `UPDATE` en SQL para modificar datos existentes.
- A mantener la interfaz pública limpia y usar una ruta secreta para el panel.

## 2026-10-29 — Día 14 (Seguridad y Sesiones)

 ✅ Logros
- Agregué autenticación al panel de administrador.
- Creé la página de `login.html` y el botón de cerrar sesión.
- Protegí todas las rutas del panel usando `session`.

 🧠 Aprendí
- El uso de `session` en Flask para recordar a un usuario.
- A redirigir usuarios no autorizados al login.
- El concepto de Autenticación y Autorización.

## 2026-10-30 — Día 15 (Variables de Entorno en Producción)

 ✅ Logros
- Saqué la contraseña hardcodeada del código.
- Configuré las Environment Variables en Render (`ADMIN_USER`, `ADMIN_PASS`, `SECRET_KEY`).

  ## 2026-11-02 — Día 16 (Galería de Flash)

 ✅ Logros
- Implementé la subida de archivos (imágenes) con Flask.
- Creé la galería de flashes en el panel de admin.
- Los clientes ahora ven la galería en la página principal.

 🧠 Aprendí
- Uso de `enctype="multipart/form-data"` en HTML.
- Manejo de archivos con `request.files` y `secure_filename`.
- Guardado de imágenes en carpetas locales (`static/uploads`).

  ## 2026-11-03 — Día 17 (Cloudinary y Producción)

 ✅ Logros
- Integré Cloudinary para el almacenamiento de imágenes en la nube.
- Configuré las variables de entorno en Render para Cloudinary y Seguridad.
- Probé el login y la subida de fotos en producción.
- Arreglé el diseño del panel de administrador.

 🧠 Aprendí
- Cómo subir archivos a un servicio externo (Cloudinary).
- La diferencia entre almacenamiento local y almacenamiento en la nube.
- Cómo manejar credenciales sensibles en producción.
- Probé el nuevo login seguro en producción.

 🧠 Aprendí
- Qué son las variables de entorno y por qué son vitales para la seguridad.
- Uso de `os.environ.get()` en Python.
- Cómo funciona un flujo de despliegue seguro.

  ## 2026-11-05 — Día 18 (Calendario de Citas)

 ✅ Logros
- Agregué campos de fecha y hora al formulario público.
- La base de datos SQLite ahora guarda fecha y hora por reserva.
- El panel de administrador muestra las citas con un formato de agenda.
- El formulario de edición permite modificar la fecha y la hora.

 🧠 Aprendí
- Uso de inputs HTML `type="date"` y `type="time"`.
- Modificación de tablas SQLite para agregar nuevas columnas.
- Formateo de datos en Jinja2 para mostrarlos de forma legible.

## 2026-11-06 — Día 19 (Filtro por Fecha)

 ✅ Logros
- Implementé un buscador por fecha en el panel de administrador.
- Uso de parámetros de URL (`GET`) para filtrar reservas.
- Agregué un botón para limpiar el filtro.

 🧠 Aprendí
- Consultas SQL con `WHERE` para filtrar datos.
- Uso de `request.args.get()` en Flask.
- Cómo mantener el estado de un filtro en el HTML (Jinja2).

  ## 2026-11-07 — Día 20 (Responsive Design y Bug Fixing)

 ✅ Logros
- Implementé diseño responsivo (Media Queries) para celulares.
- Arreglé el error "Invalid Signature" en Cloudinary (API Secret incorrecto).
- Configuré el secreto real tanto en local como en Render.

 🧠 Aprendí
- Cómo usar el modo dispositivo en las DevTools del navegador.
- Cómo diagnosticar y solucionar errores de autenticación en APIs.
- La importancia de los espacios en blanco en las variables de entorno.

  ## 2026-11-09 — Día 21 (Portafolio y Documentación)

 ✅ Logros
- Subí capturas de pantalla de la app al repositorio.
- Actualicé el `README.md` con una descripción profesional, insignias (badges) y las imágenes del proyecto.
- Solucioné un bloqueo de seguridad de Windows cambiando de PowerShell a Command Prompt.

🧠 Aprendí
- A documentar un proyecto para que sea atractivo para reclutadores/clientes.
- Cómo solucionar restricciones de seguridad de Windows en la terminal.

  ## 2026-11-10 — Día 22 (Gestión de Estados e Historial)

 ✅ Logros
- Implementé el "Soft Delete" cambiando el estado de las reservas en lugar de borrarlas.
- Agregué la columna `estado` a la base de datos.
- Creé el botón "Completar" y la página de "Historial".

 🧠 Aprendí
- La importancia de no borrar datos, sino archivar estados.
- Cómo hacer consultas SQL filtrando por el campo `estado`.

## 2026-11-11 — Día 23 (Dashboard de Estadísticas)

 ✅ Logros
- Implementé tarjetas de resumen en el panel de administrador.
- Usé el comando `COUNT()` de SQL para contar citas pendientes y completadas.
- El panel ahora muestra métricas en tiempo real.

 🧠 Aprendí
- A usar funciones de agregación en SQL (`COUNT`).
- A estructurar un Dashboard visual con CSS Grid.
- Cómo calcular datos en el backend y mostrarlos en el frontend.

  ## 2026-11-12 — Día 24 (Toque Premium y Animaciones)

 ✅ Logros
- Agregué animaciones de entrada (fadeInUp) al Hero.
- Implementé micro-interacciones (hover) en botones, tarjetas e inputs.
- La app ahora tiene una sensación visual de nivel profesional.

 🧠 Aprendí
- Uso de `@keyframes` en CSS para animaciones.
- Aplicación de `transform`, `transition` y `box-shadow` para efectos de profundidad.
- La importancia de las micro-interacciones en la experiencia de usuario (UX).
