"""
InkFlow — Sistema de reservas para estudio de tatuajes.

Estructura del archivo:
    1. Configuración
    2. Base de datos
    3. Utilidades y validaciones
    4. Rutas públicas (clientes)
    5. Rutas privadas (administrador)
    6. Galería y exportación
    7. Manejo de errores
"""

import csv
import hmac
import io
import logging
import os
import re
import secrets
import sqlite3
from datetime import datetime
from functools import wraps

import cloudinary
import cloudinary.uploader
from flask import (
    Flask, Response, flash, g, redirect, render_template,
    request, session, url_for,
)
from werkzeug.security import check_password_hash

# Si existe un archivo .env (desarrollo), carga sus variables automáticamente.
# En producción no hace falta: las variables vienen del panel del hosting.
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# ==========================================
# 1. CONFIGURACIÓN
# ==========================================

DATABASE = os.environ.get("DATABASE_PATH", "inkflow.db")
IS_PRODUCTION = os.environ.get("FLASK_ENV", "production") == "production"

# Estados posibles de una reserva (evita escribir textos sueltos por todo el código)
ESTADO_PENDIENTE = "pendiente"
ESTADO_COMPLETADA = "completada"

# Política de depósito: la calcula el SERVIDOR, el cliente ya no la escribe.
# Se puede ajustar desde variables de entorno sin tocar el código.
DEPOSITO_PORCENTAJE = float(os.environ.get("DEPOSITO_PORCENTAJE", "30"))  # % del presupuesto
DEPOSITO_MINIMO = float(os.environ.get("DEPOSITO_MINIMO", "50000"))      # COP
PRECIO_MAXIMO = 50_000_000                                                # tope de cordura

EXTENSIONES_PERMITIDAS = {"png", "jpg", "jpeg", "webp", "gif"}
EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("inkflow")

app = Flask(__name__)

# La clave secreta DEBE venir del entorno en producción: si es fija o pública,
# cualquiera puede falsificar una sesión de administrador.
app.secret_key = os.environ.get("SECRET_KEY")
if not app.secret_key:
    if IS_PRODUCTION:
        raise RuntimeError("Falta la variable de entorno SECRET_KEY.")
    app.secret_key = "clave-solo-para-desarrollo"

app.config.update(
    SESSION_COOKIE_HTTPONLY=True,       # JavaScript no puede leer la cookie
    SESSION_COOKIE_SAMESITE="Lax",      # Protege contra envíos desde otros sitios
    SESSION_COOKIE_SECURE=IS_PRODUCTION,  # Solo por HTTPS en producción
    MAX_CONTENT_LENGTH=8 * 1024 * 1024,   # Máx. 8 MB por subida de imagen
)

# Cloudinary: las credenciales SOLO se leen del entorno, nunca del código.
cloudinary.config(
    cloud_name=os.environ.get("CLOUDINARY_CLOUD_NAME"),
    api_key=os.environ.get("CLOUDINARY_API_KEY"),
    api_secret=os.environ.get("CLOUDINARY_API_SECRET"),
    secure=True,
)

# Credenciales del administrador (también desde el entorno).
ADMIN_USER = os.environ.get("ADMIN_USER")
ADMIN_PASS = os.environ.get("ADMIN_PASS")            # opción simple
ADMIN_PASS_HASH = os.environ.get("ADMIN_PASS_HASH")  # opción recomendada (hash)

if IS_PRODUCTION and not (ADMIN_USER and (ADMIN_PASS or ADMIN_PASS_HASH)):
    raise RuntimeError("Faltan ADMIN_USER y ADMIN_PASS (o ADMIN_PASS_HASH).")


# ==========================================
# 2. BASE DE DATOS
# ==========================================

def get_db():
    """Devuelve la conexión de la petición actual (una sola por petición)."""
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        # Row permite acceder por índice (r[0]) Y por nombre (r["nombre"]),
        # así tus plantillas actuales siguen funcionando.
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def cerrar_db(_error=None):
    """Cierra la conexión automáticamente al terminar cada petición."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    """Crea las tablas si no existen."""
    db = sqlite3.connect(DATABASE)
    db.executescript(
        """
        CREATE TABLE IF NOT EXISTS reservas (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre   TEXT NOT NULL,
            email    TEXT NOT NULL,
            idea     TEXT NOT NULL,
            fecha    TEXT NOT NULL,
            hora     TEXT NOT NULL,
            precio   REAL DEFAULT 0,
            deposito REAL DEFAULT 0,
            pagado   BOOLEAN DEFAULT 0,
            estado   TEXT DEFAULT 'pendiente'
        );

        CREATE TABLE IF NOT EXISTS flashes (
            id     INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            imagen TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS resenas (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            email      TEXT NOT NULL,
            comentario TEXT NOT NULL,
            estrellas  INTEGER NOT NULL
        );

        -- Índices: aceleran las búsquedas cuando crezca el número de reservas
        CREATE INDEX IF NOT EXISTS idx_reservas_email  ON reservas(email);
        CREATE INDEX IF NOT EXISTS idx_reservas_estado ON reservas(estado);
        CREATE INDEX IF NOT EXISTS idx_reservas_fecha  ON reservas(fecha, hora);
        """
    )
    db.commit()
    db.close()


init_db()


# ==========================================
# 3. UTILIDADES Y VALIDACIONES
# ==========================================

def admin_requerido(vista):
    """Decorador: protege una ruta para que solo entre el administrador."""
    @wraps(vista)
    def envoltura(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect(url_for("login"))
        return vista(*args, **kwargs)
    return envoltura


def generar_csrf():
    """Token anti-CSRF guardado en la sesión; las plantillas lo usan con {{ csrf_token() }}."""
    if "csrf" not in session:
        session["csrf"] = secrets.token_hex(16)
    return session["csrf"]


app.jinja_env.globals["csrf_token"] = generar_csrf


def csrf_protegido(vista):
    """Decorador: rechaza el POST si no trae el token CSRF correcto."""
    @wraps(vista)
    def envoltura(*args, **kwargs):
        if request.method != "POST":
            return vista(*args, **kwargs)  # el token solo se exige al ENVIAR formularios
        enviado = request.form.get("csrf_token", "")
        esperado = session.get("csrf", "")
        if not esperado or not hmac.compare_digest(enviado, esperado):
            flash("❌ Solicitud inválida o sesión vencida. Intenta de nuevo.", "error")
            destino = "admin" if session.get("logged_in") else "inicio"
            return redirect(url_for(destino))
        return vista(*args, **kwargs)
    return envoltura


def calcular_deposito(precio):
    """Depósito = % del presupuesto (con mínimo), redondeado a miles y nunca mayor al total."""
    bruto = max(precio * DEPOSITO_PORCENTAJE / 100, DEPOSITO_MINIMO)
    return float(min(precio, round(bruto, -3)))


def credenciales_validas(usuario, contrasena):
    """Compara usuario/contraseña de forma segura (resistente a ataques de tiempo)."""
    if not usuario or not contrasena or not ADMIN_USER:
        return False
    usuario_ok = hmac.compare_digest(usuario, ADMIN_USER)
    if ADMIN_PASS_HASH:
        pass_ok = check_password_hash(ADMIN_PASS_HASH, contrasena)
    elif ADMIN_PASS:
        pass_ok = hmac.compare_digest(contrasena, ADMIN_PASS)
    else:
        pass_ok = False
    return usuario_ok and pass_ok


def a_numero(valor, por_defecto=0.0):
    """Convierte un texto a número no negativo; si falla, devuelve el valor por defecto."""
    try:
        numero = float(valor)
    except (TypeError, ValueError):
        return por_defecto
    return numero if numero >= 0 else por_defecto


def fecha_valida(texto):
    """True si el texto tiene formato AAAA-MM-DD."""
    try:
        datetime.strptime(texto, "%Y-%m-%d")
        return True
    except (TypeError, ValueError):
        return False


def extension_permitida(nombre_archivo):
    return "." in nombre_archivo and \
        nombre_archivo.rsplit(".", 1)[1].lower() in EXTENSIONES_PERMITIDAS


def horario_ocupado(db, fecha, hora, excluir_id=None):
    """True si ya existe una cita pendiente en ese día y hora."""
    consulta = "SELECT 1 FROM reservas WHERE fecha = ? AND hora = ? AND estado = ?"
    params = [fecha, hora, ESTADO_PENDIENTE]
    if excluir_id is not None:
        consulta += " AND id != ?"
        params.append(excluir_id)
    return db.execute(consulta, params).fetchone() is not None


# ==========================================
# 4. RUTAS PÚBLICAS (clientes)
# ==========================================

@app.route("/")
def inicio():
    db = get_db()
    flashes = db.execute("SELECT * FROM flashes").fetchall()
    resenas = db.execute("SELECT * FROM resenas ORDER BY id DESC LIMIT 3").fetchall()
    return render_template(
        "index.html",
        lista_flashes=flashes,
        lista_resenas=resenas,
        deposito_porcentaje=int(DEPOSITO_PORCENTAJE),
        deposito_minimo=DEPOSITO_MINIMO,
        hoy=datetime.now().strftime("%Y-%m-%d"),
    )


@app.route("/reservar", methods=["POST"])
def reservar():
    nombre = request.form.get("nombre", "").strip()
    email = request.form.get("email", "").strip().lower()
    idea = request.form.get("idea", "").strip()
    fecha = request.form.get("fecha", "").strip()
    hora = request.form.get("hora", "").strip()
    precio = a_numero(request.form.get("precio"))   # presupuesto estimado del cliente
    deposito = calcular_deposito(precio)            # lo decide el servidor, no el cliente

    # --- Validaciones ---
    if not 0 < precio <= PRECIO_MAXIMO:
        flash("❌ Indica un presupuesto válido.", "error")
        return redirect(url_for("inicio"))

    if not all([nombre, email, idea, fecha, hora]):
        flash("❌ Completa todos los campos para agendar tu cita.", "error")
        return redirect(url_for("inicio"))

    if not EMAIL_REGEX.match(email):
        flash("❌ El correo no parece válido.", "error")
        return redirect(url_for("inicio"))

    if not fecha_valida(fecha):
        flash("❌ La fecha no es válida.", "error")
        return redirect(url_for("inicio"))

    if fecha < datetime.now().strftime("%Y-%m-%d"):
        flash("❌ Error: No puedes reservar en el pasado.", "error")
        return redirect(url_for("inicio"))

    db = get_db()

    # Evita que dos clientes reserven el mismo horario (¡dinero perdido y clientes molestos!)
    if horario_ocupado(db, fecha, hora):
        flash("⏰ Ese horario ya está ocupado. Elige otra hora, por favor.", "error")
        return redirect(url_for("inicio"))

    db.execute(
        """INSERT INTO reservas (nombre, email, idea, fecha, hora, precio, deposito)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (nombre, email, idea, fecha, hora, precio, deposito),
    )
    db.commit()

    flash(f"¡Tu cita ha sido agendada! Recuerda abonar el depósito de ${deposito:,.0f}. 🖤", "success")
    return redirect(url_for("inicio"))


@app.route("/mi-perfil", methods=["GET", "POST"])
def mi_perfil():
    reservas_cliente = []
    total_completados = 0
    email_buscado = ""

    if request.method == "POST":
        email_buscado = request.form.get("email", "").strip().lower()
        db = get_db()

        reservas_cliente = db.execute(
            "SELECT * FROM reservas WHERE email = ? ORDER BY fecha DESC",
            (email_buscado,),
        ).fetchall()

        # Tatuajes completados = puntos de lealtad
        total_completados = db.execute(
            "SELECT COUNT(*) FROM reservas WHERE email = ? AND estado = ?",
            (email_buscado, ESTADO_COMPLETADA),
        ).fetchone()[0]

        if not reservas_cliente:
            flash("No encontramos reservas con ese correo. ¡Anímate a agendar!", "error")

    return render_template(
        "perfil.html",
        reservas=reservas_cliente,
        total_completados=total_completados,
        email=email_buscado,
    )


@app.route("/dejar-resena", methods=["GET", "POST"])
def dejar_resena():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        comentario = request.form.get("comentario", "").strip()
        estrellas = request.form.get("estrellas", type=int)

        if not EMAIL_REGEX.match(email) or not comentario or estrellas not in range(1, 6):
            flash("❌ Revisa los datos: correo, comentario y estrellas (1 a 5).", "error")
            return redirect(url_for("dejar_resena"))

        db = get_db()
        db.execute(
            "INSERT INTO resenas (email, comentario, estrellas) VALUES (?, ?, ?)",
            (email, comentario, estrellas),
        )
        db.commit()

        flash("¡Gracias por tu reseña! Nos ayuda a seguir creciendo. ⭐", "success")
        return redirect(url_for("inicio"))

    return render_template("resena.html")


# ==========================================
# 5. RUTAS PRIVADAS (administrador)
# ==========================================

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = request.form.get("usuario", "")
        contrasena = request.form.get("contrasena", "")

        if credenciales_validas(usuario, contrasena):
            session.clear()
            session["logged_in"] = True
            flash("¡Bienvenido al panel de administración! 👋", "success")
            return redirect(url_for("admin"))

        log.warning("Intento de login fallido desde %s", request.remote_addr)
        flash("Usuario o contraseña incorrectos. 🚫", "error")
        return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("Has cerrado sesión correctamente. 🔒", "success")
    return redirect(url_for("login"))


@app.route("/admin")
@admin_requerido
def admin():
    db = get_db()
    fecha_filtro = request.args.get("fecha")

    # 1. Reservas pendientes (todas o filtradas por fecha)
    if fecha_filtro:
        reservas = db.execute(
            "SELECT * FROM reservas WHERE fecha = ? AND estado = ? ORDER BY hora",
            (fecha_filtro, ESTADO_PENDIENTE),
        ).fetchall()
    else:
        reservas = db.execute(
            "SELECT * FROM reservas WHERE estado = ? ORDER BY fecha, hora",
            (ESTADO_PENDIENTE,),
        ).fetchall()

    # 2. Estadísticas del dashboard (una sola consulta en vez de tres)
    stats = db.execute(
        """SELECT
               SUM(estado = ?)                                   AS pendientes,
               SUM(estado = ?)                                   AS completadas,
               COALESCE(SUM(CASE WHEN estado = ? THEN precio END), 0) AS ingresos
           FROM reservas""",
        (ESTADO_PENDIENTE, ESTADO_COMPLETADA, ESTADO_COMPLETADA),
    ).fetchone()

    # 3. Galería de flashes
    flashes = db.execute("SELECT * FROM flashes").fetchall()

    # 4. Gráfico: las ÚLTIMAS 5 citas completadas, en orden cronológico
    #    (antes se mostraban las 5 más antiguas, no las más recientes)
    datos_grafico = db.execute(
        """SELECT fecha, precio FROM (
               SELECT fecha, precio FROM reservas
               WHERE estado = ? ORDER BY fecha DESC LIMIT 5
           ) ORDER BY fecha ASC""",
        (ESTADO_COMPLETADA,),
    ).fetchall()

    return render_template(
        "admin.html",
        lista_reservas=reservas,
        lista_flashes=flashes,
        fecha_filtro=fecha_filtro,
        total_pendientes=stats["pendientes"] or 0,
        total_completadas=stats["completadas"] or 0,
        ingresos_totales=stats["ingresos"] or 0,
        fechas_grafico=[fila["fecha"] for fila in datos_grafico],
        precios_grafico=[fila["precio"] for fila in datos_grafico],
    )


@app.route("/completar/<int:id>", methods=["POST"])
@admin_requerido
@csrf_protegido
def completar(id):
    db = get_db()
    # Precio final: el tatuador confirma cuánto cobró de verdad (los ingresos salen de aquí)
    precio_final = a_numero(request.form.get("precio_final"), por_defecto=None)
    if precio_final is not None and 0 < precio_final <= PRECIO_MAXIMO:
        db.execute("UPDATE reservas SET estado = ?, precio = ? WHERE id = ?",
                   (ESTADO_COMPLETADA, precio_final, id))
    else:
        db.execute("UPDATE reservas SET estado = ? WHERE id = ?", (ESTADO_COMPLETADA, id))
    db.commit()
    flash("¡Tatuaje marcado como completado! ✅", "success")
    return redirect(url_for("admin"))


@app.route("/pagar_deposito/<int:id>", methods=["POST"])
@admin_requerido
@csrf_protegido
def pagar_deposito(id):
    db = get_db()
    db.execute("UPDATE reservas SET pagado = 1 WHERE id = ?", (id,))
    db.commit()
    flash("¡Depósito confirmado! El cliente ya dejó el abono. 💸", "success")
    return redirect(url_for("admin"))


@app.route("/historial")
@admin_requerido
def historial():
    completadas = get_db().execute(
        "SELECT * FROM reservas WHERE estado = ? ORDER BY fecha DESC",
        (ESTADO_COMPLETADA,),
    ).fetchall()
    return render_template("historial.html", lista_completadas=completadas)


@app.route("/borrar/<int:id>", methods=["POST"])
@admin_requerido
@csrf_protegido
def borrar(id):
    db = get_db()
    db.execute("DELETE FROM reservas WHERE id = ?", (id,))
    db.commit()
    flash("Reserva eliminada. 🗑️", "success")
    return redirect(url_for("admin"))


@app.route("/editar/<int:id>", methods=["GET", "POST"])
@admin_requerido
@csrf_protegido
def editar(id):
    db = get_db()

    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        email = request.form.get("email", "").strip().lower()
        idea = request.form.get("idea", "").strip()
        fecha = request.form.get("fecha", "").strip()
        hora = request.form.get("hora", "").strip()

        if not all([nombre, email, idea, fecha, hora]) or not fecha_valida(fecha):
            flash("❌ Revisa los datos: todos los campos son obligatorios.", "error")
            return redirect(url_for("editar", id=id))

        if horario_ocupado(db, fecha, hora, excluir_id=id):
            flash("⏰ Ya hay otra cita en ese horario.", "error")
            return redirect(url_for("editar", id=id))

        db.execute(
            """UPDATE reservas
               SET nombre = ?, email = ?, idea = ?, fecha = ?, hora = ?
               WHERE id = ?""",
            (nombre, email, idea, fecha, hora, id),
        )
        db.commit()
        flash("Reserva actualizada correctamente. ✏️", "success")
        return redirect(url_for("admin"))

    reserva = db.execute("SELECT * FROM reservas WHERE id = ?", (id,)).fetchone()
    if reserva is None:
        return render_template("404.html"), 404
    return render_template("editar.html", reserva=reserva)


# ==========================================
# 6. GALERÍA Y EXPORTACIÓN
# ==========================================

@app.route("/subir_flash", methods=["POST"])
@admin_requerido
@csrf_protegido
def subir_flash():
    titulo = request.form.get("titulo", "").strip()
    archivo = request.files.get("imagen")

    if not titulo or not archivo or archivo.filename == "":
        flash("❌ Agrega un título y selecciona una imagen.", "error")
        return redirect(url_for("admin"))

    if not extension_permitida(archivo.filename):
        flash("❌ Formato no permitido. Usa PNG, JPG, WEBP o GIF.", "error")
        return redirect(url_for("admin"))

    try:
        resultado = cloudinary.uploader.upload(archivo, folder="inkflow/flashes")
    except Exception:
        log.exception("Error subiendo imagen a Cloudinary")
        flash("❌ No se pudo subir la imagen. Intenta de nuevo.", "error")
        return redirect(url_for("admin"))

    db = get_db()
    db.execute(
        "INSERT INTO flashes (titulo, imagen) VALUES (?, ?)",
        (titulo, resultado["secure_url"]),
    )
    db.commit()
    flash("¡Flash subido con éxito! 🎨", "success")
    return redirect(url_for("admin"))


@app.route("/borrar_flash/<int:id>", methods=["POST"])
@admin_requerido
@csrf_protegido
def borrar_flash(id):
    db = get_db()
    db.execute("DELETE FROM flashes WHERE id = ?", (id,))
    db.commit()
    flash("Flash eliminado. 🗑️", "success")
    return redirect(url_for("admin"))


@app.route("/exportar")
@admin_requerido
def exportar():
    """Reporte financiero en CSV (se abre directo en Excel / Google Sheets)."""
    filas = get_db().execute(
        """SELECT nombre, email, idea, fecha, hora, precio, deposito, pagado, estado
           FROM reservas ORDER BY fecha DESC"""
    ).fetchall()

    salida = io.StringIO()
    escritor = csv.writer(salida)
    escritor.writerow(["Cliente", "Email", "Idea", "Fecha", "Hora",
                       "Total", "Depósito", "Depósito pagado", "Estado de la cita"])
    for f in filas:
        escritor.writerow([f["nombre"], f["email"], f["idea"], f["fecha"], f["hora"],
                           f["precio"], f["deposito"],
                           "Sí" if f["pagado"] else "No", f["estado"]])

    # utf-8-sig: Excel muestra bien las tildes y la ñ
    contenido = "\ufeff" + salida.getvalue()
    return Response(
        contenido,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=reporte_inkflow.csv"},
    )


# ==========================================
# 7. MANEJO DE ERRORES
# ==========================================

@app.errorhandler(404)
def pagina_no_encontrada(_error):
    return render_template("404.html"), 404


@app.errorhandler(413)
def archivo_muy_grande(_error):
    flash("❌ La imagen es demasiado grande (máximo 8 MB).", "error")
    return redirect(url_for("admin"))


@app.errorhandler(500)
def error_interno(_error):
    log.exception("Error interno del servidor")
    return "Ocurrió un error inesperado. Intenta de nuevo en un momento.", 500


# ==========================================
# ARRANQUE
# ==========================================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    # debug SOLO en desarrollo: en producción expone el código y permite ejecutar comandos
    app.run(host="0.0.0.0", port=port, debug=not IS_PRODUCTION)