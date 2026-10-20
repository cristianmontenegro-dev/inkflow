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
