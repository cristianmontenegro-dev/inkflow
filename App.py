from flask import Flask, render_template, request, redirect, url_for, session, flash, Response
import sqlite3
import os
import io
import cloudinary
import cloudinary.uploader
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'inkflow_super_secreto_2026')

# --- CONFIGURACIÓN DE CLOUDINARY ---
cloudinary.config( 
  cloud_name = os.environ.get('CLOUDINARY_CLOUD_NAME', 'tgzwbtsk'), 
  api_key = os.environ.get('CLOUDINARY_API_KEY', '126599169651419'), 
  api_secret = os.environ.get('CLOUDINARY_API_SECRET', 'Yz9hq1hLx06WMgLYcgXI8HvNssY'), 
  secure = True
)

# --- 1. INICIALIZACIÓN DE LA BASE DE DATOS ---
def init_db():
    conn = sqlite3.connect('inkflow.db')
    cursor = conn.cursor()
    
    # Tabla de Reservas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reservas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            email TEXT NOT NULL,
            idea TEXT NOT NULL,
            fecha TEXT NOT NULL,
            hora TEXT NOT NULL,
            precio REAL DEFAULT 0,
            deposito REAL DEFAULT 0,
            pagado BOOLEAN DEFAULT 0,
            estado TEXT DEFAULT 'pendiente'
        )
    ''')
    
    # Tabla de Flashes (Galería)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS flashes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            imagen TEXT NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS resenas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            comentario TEXT NOT NULL,
            estrellas INTEGER NOT NULL
        )
    ''')

        # Tabla de Configuración (Para la marca del tatuador)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS configuracion (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_artista TEXT DEFAULT 'Cristian Rojas',
            biografia TEXT DEFAULT 'Tatuador independiente construyendo arte con disciplina.',
            instagram TEXT DEFAULT 'cristian_rojas328',
            whatsapp TEXT DEFAULT '573219341966',
            titulo_principal TEXT DEFAULT 'Del primer trazo a tu primer cliente.'
        )
    ''')

    cursor.execute("SELECT COUNT(*) FROM configuracion")
    if cursor.fetchone()[0] == 0:
        cursor.execute('''
            INSERT INTO configuracion (nombre_artista, biografia, instagram, whatsapp, titulo_principal)
            VALUES ('Cristian Rojas', 'Tatuador independiente construyendo arte con disciplina.', 'cristian_rojas328', '573219341966', 'Del primer trazo a tu primer cliente.')
        ''')
        
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS suscriptores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# ==========================================
# 2. RUTAS PÚBLICAS (CLIENTES)
# ==========================================

@app.route('/')
def inicio():
    conn = sqlite3.connect('inkflow.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM flashes")
    flashes = cursor.fetchall()
    
    cursor.execute("SELECT * FROM resenas ORDER BY id DESC LIMIT 3") 
    resenas = cursor.fetchall()
    
    # Traemos la CONFIGURACIÓN del tatuador
    cursor.execute("SELECT * FROM configuracion WHERE id = 1")
    config = cursor.fetchone()
    
    conn.close()
    return render_template('index.html', lista_flashes=flashes, lista_resenas=resenas, config=config)

@app.route('/reservar', methods=['POST'])
def reservar():
    # Datos del formulario
    nombre = request.form.get('nombre')
    email = request.form.get('email')
    idea = request.form.get('idea')
    fecha = request.form.get('fecha')
    hora = request.form.get('hora')
    precio = request.form.get('precio')
    deposito = request.form.get('deposito')
    
    # Validación de fecha
    hoy = datetime.now().strftime('%Y-%m-%d')
    if fecha < hoy:
        flash('❌ Error: No puedes reservar en el pasado.', 'error')
        return redirect(url_for('inicio'))
        
    conn = sqlite3.connect('inkflow.db')
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO reservas (nombre, email, idea, fecha, hora, precio, deposito) 
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (nombre, email, idea, fecha, hora, precio, deposito))
    conn.commit()
    conn.close()
    
    flash('¡Tu cita ha sido agendada! No olvides abonar el depósito. 🖤', 'success')
    return redirect(url_for('inicio'))

@app.route('/mi-perfil', methods=['GET', 'POST'])
def mi_perfil():
    reservas_cliente = []
    total_completados = 0
    email_buscado = ""
    
    if request.method == 'POST':
        email_buscado = request.form.get('email')
        
        conn = sqlite3.connect('inkflow.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM reservas WHERE email = ? ORDER BY fecha DESC", (email_buscado,))
        reservas_cliente = cursor.fetchall()
        
        cursor.execute("SELECT COUNT(*) FROM reservas WHERE email = ? AND estado = 'completada'", (email_buscado,))
        total_completados = cursor.fetchone()[0]
        conn.close()
        
        if not reservas_cliente:
            flash('No encontramos reservas con ese correo. ¡Anímate a agendar tu primera cita!', 'error')
            
    return render_template('perfil.html', reservas=reservas_cliente, total_completados=total_completados, email=email_buscado)

@app.route('/dejar-resena', methods=['GET', 'POST'])
def dejar_resena():
    if request.method == 'POST':
        email = request.form.get('email')
        comentario = request.form.get('comentario')
        estrellas = request.form.get('estrellas')
        
        conn = sqlite3.connect('inkflow.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO resenas (email, comentario, estrellas) VALUES (?, ?, ?)", (email, comentario, estrellas))
        conn.commit()
        conn.close()
        
        flash('¡Gracias por tu reseña! Nos ayuda a seguir mejorando. ⭐', 'success')
        return redirect(url_for('inicio'))
        
    return render_template('resena.html')

# ==========================================
# 3. RUTAS PRIVADAS (ADMINISTRADOR)
# ==========================================

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form.get('usuario')
        contrasena = request.form.get('contrasena')
        usuario_correcto = os.environ.get('ADMIN_USER', 'cristian')
        contrasena_correcta = os.environ.get('ADMIN_PASS', 'tatuaje2026')
        
        if usuario == usuario_correcto and contrasena == contrasena_correcta:
            session['logged_in'] = True
            flash('¡Bienvenido al panel de administración! 👋', 'success')
            return redirect(url_for('admin'))
        else:
            flash('Usuario o contraseña incorrectos. 🚫', 'error')
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('Has cerrado sesión correctamente. 🔒', 'success')
    return redirect(url_for('login'))

@app.route('/admin')
def admin():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    fecha_filtro = request.args.get('fecha')
    conn = sqlite3.connect('inkflow.db')
    cursor = conn.cursor()
    
    if fecha_filtro:
        cursor.execute("SELECT * FROM reservas WHERE fecha = ? AND estado = 'pendiente'", (fecha_filtro,))
    else:
        cursor.execute("SELECT * FROM reservas WHERE estado = 'pendiente'")
    reservas = cursor.fetchall()

    cursor.execute("SELECT COUNT(*) FROM reservas WHERE estado = 'pendiente'")
    total_pendientes = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM reservas WHERE estado = 'completada'")
    total_completadas = cursor.fetchone()[0]
    
    cursor.execute("SELECT SUM(precio) FROM reservas WHERE estado = 'completada'")
    ingresos_totales = cursor.fetchone()[0] or 0
    
    cursor.execute("SELECT * FROM flashes")
    flashes = cursor.fetchall()
    
    cursor.execute("SELECT fecha, precio FROM reservas WHERE estado = 'completada' ORDER BY fecha ASC LIMIT 5")
    datos_grafico = cursor.fetchall()
    fechas_grafico = [fila[0] for fila in datos_grafico]
    precios_grafico = [fila[1] for fila in datos_grafico]
    
    conn.close()
    
    return render_template('admin.html', lista_reservas=reservas, lista_flashes=flashes, 
                           fecha_filtro=fecha_filtro, total_pendientes=total_pendientes, 
                           total_completadas=total_completadas, ingresos_totales=ingresos_totales,
                           fechas_grafico=fechas_grafico, precios_grafico=precios_grafico)

@app.route('/completar/<int:id>')
def completar(id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    conn = sqlite3.connect('inkflow.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE reservas SET estado = 'completada' WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    flash('¡Tatuaje marcado como completado! ✅', 'success')
    return redirect(url_for('admin'))

@app.route('/pagar_deposito/<int:id>')
def pagar_deposito(id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    conn = sqlite3.connect('inkflow.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE reservas SET pagado = 1 WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    flash('¡Depósito confirmado! El cliente ya dejó el abono. 💸', 'success')
    return redirect(url_for('admin'))

@app.route('/historial')
def historial():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    conn = sqlite3.connect('inkflow.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM reservas WHERE estado = 'completada'")
    completadas = cursor.fetchall()
    conn.close()
    return render_template('historial.html', lista_completadas=completadas)

@app.route('/borrar/<int:id>')
def borrar(id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    conn = sqlite3.connect('inkflow.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM reservas WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    flash('Reserva eliminada. 🗑️', 'success')
    return redirect(url_for('admin')) 

@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    conn = sqlite3.connect('inkflow.db')
    cursor = conn.cursor()

    if request.method == 'POST':
        nombre = request.form.get('nombre')
        email = request.form.get('email')
        idea = request.form.get('idea')
        fecha = request.form.get('fecha')
        hora = request.form.get('hora')
        cursor.execute("""
            UPDATE reservas SET nombre = ?, email = ?, idea = ?, fecha = ?, hora = ? WHERE id = ?
        """, (nombre, email, idea, fecha, hora, id))
        conn.commit()
        conn.close()
        flash('Reserva actualizada correctamente. ✏️', 'success')
        return redirect(url_for('admin'))
    else:
        cursor.execute("SELECT * FROM reservas WHERE id = ?", (id,))
        reserva = cursor.fetchone()
        conn.close()
        return render_template('editar.html', reserva=reserva)

# ==========================================
# 4. GALERÍA Y EXPORTACIÓN
# ==========================================

@app.route('/subir_flash', methods=['POST'])
def subir_flash():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    titulo = request.form.get('titulo')
    archivo = request.files['imagen']
    
    if archivo and archivo.filename != '':
        resultado = cloudinary.uploader.upload(archivo)
        url_imagen = resultado['secure_url']
        
        conn = sqlite3.connect('inkflow.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO flashes (titulo, imagen) VALUES (?, ?)", (titulo, url_imagen))
        conn.commit()
        conn.close()
        flash('¡Flash subido con éxito! 🎨', 'success')
    return redirect(url_for('admin'))

@app.route('/borrar_flash/<int:id>')
def borrar_flash(id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    conn = sqlite3.connect('inkflow.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM flashes WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    flash('Flash eliminado. 🗑️', 'success')
    return redirect(url_for('admin'))

@app.route('/exportar')
def exportar():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    conn = sqlite3.connect('inkflow.db')
    cursor = conn.cursor()
    cursor.execute("SELECT nombre, email, idea, fecha, hora, precio, deposito, pagado, estado FROM reservas")
    reservas = cursor.fetchall()
    conn.close()
    
    output = io.StringIO()
    output.write("=== REPORTE FINANCIERO INKFLOW ===\n\n")
    for r in reservas:
        estado_pago = "Pagado" if r[7] == 1 else "Pendiente"
        output.write(f"Cliente: {r[0]} | Email: {r[1]} | Idea: {r[2]}\n")
        output.write(f"Fecha: {r[3]} {r[4]} | Total: ${r[5]} | Depósito: ${r[6]} ({estado_pago}) | Cita: {r[8]}\n")
        output.write("-" * 50 + "\n")
        
    return Response(output.getvalue(), mimetype="text/plain",
                    headers={"Content-Disposition": "attachment;filename=reporte_inkflow.txt"})

@app.route('/configuracion', methods=['GET', 'POST'])
def configuracion():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('inkflow.db')
    cursor = conn.cursor()
    
    if request.method == 'POST':
        nombre = request.form.get('nombre_artista')
        bio = request.form.get('biografia')
        insta = request.form.get('instagram')
        wpp = request.form.get('whatsapp')
        titulo = request.form.get('titulo_principal')
        
        cursor.execute("""
            UPDATE configuracion SET nombre_artista = ?, biografia = ?, instagram = ?, whatsapp = ?, titulo_principal = ? WHERE id = 1
        """, (nombre, bio, insta, wpp, titulo))
        conn.commit()
        flash('¡Configuración guardada! Tu página se ha actualizado. ✨', 'success')
        return redirect(url_for('configuracion'))
        
    cursor.execute("SELECT * FROM configuracion WHERE id = 1")
    config = cursor.fetchone()
    conn.close()
    
    return render_template('configuracion.html', config=config)

@app.route('/suscribirse', methods=['POST'])
def suscribirse():
    email = request.form.get('email_suscriptor')
    conn = sqlite3.connect('inkflow.db')
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO suscriptores (email) VALUES (?)", (email,))
        conn.commit()
        flash('¡Estás en la lista VIP! Recibirás mis próximos drops antes que nadie. 🖤', 'success')
    except sqlite3.IntegrityError:
        flash('Este correo ya está en la lista. ¡Atento a las novedades! 😉', 'error')
    conn.close()
    return redirect(url_for('inicio'))

@app.errorhandler(404)
def pagina_no_encontrada(error):
    return render_template('404.html'), 404

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)