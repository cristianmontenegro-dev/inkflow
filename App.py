from flask import Flask, render_template, request, redirect, url_for, session, flash, Response
import sqlite3
import os
import io
import cloudinary
import cloudinary.uploader
from datetime import datetime

app = Flask(__name__)
# Clave secreta para las sesiones (cámbiala en producción por seguridad)
app.secret_key = os.environ.get('SECRET_KEY', 'inkflow_super_secreto_2026')

# Configuración de Cloudinary (Tus credenciales)
cloudinary.config( 
  cloud_name = os.environ.get('CLOUDINARY_CLOUD_NAME', 'tgzwbtsk'), 
  api_key = os.environ.get('CLOUDINARY_API_KEY', '126599169651419'), 
  api_secret = os.environ.get('CLOUDINARY_API_SECRET', 'TU_SECRETO_AQUI'), 
  secure = True
)

# --- 1. INICIALIZACIÓN DE LA BASE DE DATOS ---
def init_db():
    conn = sqlite3.connect('inkflow.db')
    cursor = conn.cursor()
    # Tabla de reservas (ahora incluye el email del cliente)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reservas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            email TEXT NOT NULL,
            idea TEXT NOT NULL,
            fecha TEXT NOT NULL,
            hora TEXT NOT NULL,
            estado TEXT DEFAULT 'pendiente'
        )
    ''')
    # Tabla de flashes
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS flashes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            imagen TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# --- 2. RUTAS PÚBLICAS (CLIENTES) ---

@app.route('/')
def inicio():
    conn = sqlite3.connect('inkflow.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM flashes")
    flashes = cursor.fetchall()
    conn.close()
    return render_template('index.html', lista_flashes=flashes)

@app.route('/reservar', methods=['POST'])
def reservar():
    nombre = request.form.get('nombre')
    email = request.form.get('email')
    idea = request.form.get('idea')
    fecha = request.form.get('fecha')
    hora = request.form.get('hora')
    
    # Validaciones de seguridad
    hoy = datetime.now().strftime('%Y-%m-%d')
    if fecha < hoy:
        flash('❌ Error: No puedes reservar en el pasado.', 'error')
        return redirect(url_for('inicio'))
        
    conn = sqlite3.connect('inkflow.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO reservas (nombre, email, idea, fecha, hora) VALUES (?, ?, ?, ?, ?)", 
                   (nombre, email, idea, fecha, hora))
    conn.commit()
    conn.close()
    
    flash('¡Tu cita ha sido agendada con éxito! Revisa tu perfil con tu correo. 🖤', 'success')
    return redirect(url_for('inicio'))

# --- 3. EL PORTAL DEL CLIENTE (LA NUEVA JOYA PARA GENERAR INGRESOS) ---
@app.route('/mi-perfil', methods=['GET', 'POST'])
def mi_perfil():
    reservas_cliente = []
    total_completados = 0
    puntos_fidelidad = 0
    email_buscado = ""
    
    if request.method == 'POST':
        email_buscado = request.form.get('email')
        
        conn = sqlite3.connect('inkflow.db')
        cursor = conn.cursor()
        # Buscamos todas las reservas que pertenecen a ese correo
        cursor.execute("SELECT * FROM reservas WHERE email = ? ORDER BY fecha DESC", (email_buscado,))
        reservas_cliente = cursor.fetchall()
        
        # Contamos cuántos tatuajes completados tiene (para el sistema de lealtad)
        cursor.execute("SELECT COUNT(*) FROM reservas WHERE email = ? AND estado = 'completada'", (email_buscado,))
        total_completados = cursor.fetchone()[0]
        conn.close()
        
        if not reservas_cliente:
            flash('No encontramos reservas con ese correo. ¡Anímate a agendar tu primera cita!', 'error')
            
    return render_template('perfil.html', 
                           reservas=reservas_cliente, 
                           total_completados=total_completados,
                           email=email_buscado)

# --- 4. RUTAS DE ADMINISTRADOR (PRIVADAS) ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form.get('usuario')
        contrasena = request.form.get('contrasena')
        usuario_correcto = os.environ.get('ADMIN_USER', 'cristian')
        contrasena_correcta = os.environ.get('ADMIN_PASS', 'tatuaje2026')
        
        if usuario == usuario_correcto and contrasena == contrasena_correcta:
            session['logged_in'] = True
            flash('¡Bienvenido al panel de administración!', 'success')
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
    
    cursor.execute("SELECT * FROM flashes")
    flashes = cursor.fetchall()
    conn.close()
    
    return render_template('admin.html', lista_reservas=reservas, lista_flashes=flashes, 
                           fecha_filtro=fecha_filtro, total_pendientes=total_pendientes, 
                           total_completadas=total_completadas)

@app.route('/completar/<int:id>')
def completar(id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    conn = sqlite3.connect('inkflow.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE reservas SET estado = 'completada' WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    flash('¡Tatuaje marcado como completado! ✅ El cliente sumó puntos de lealtad.', 'success')
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
        cursor.execute("UPDATE reservas SET nombre = ?, email = ?, idea = ?, fecha = ?, hora = ? WHERE id = ?", 
                       (nombre, email, idea, fecha, hora, id))
        conn.commit()
        conn.close()
        flash('Reserva actualizada correctamente. ✏️', 'success')
        return redirect(url_for('admin'))
    else:
        cursor.execute("SELECT * FROM reservas WHERE id = ?", (id,))
        reserva = cursor.fetchone()
        conn.close()
        return render_template('editar.html', reserva=reserva)

# --- 5. RUTAS DE GALERÍA Y EXPORTACIÓN ---

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
    cursor.execute("SELECT nombre, email, idea, fecha, hora, estado FROM reservas")
    reservas = cursor.fetchall()
    conn.close()
    
    output = io.StringIO()
    output.write("=== REPORTE DE RESERVAS INKFLOW ===\n\n")
    for r in reservas:
        output.write(f"Cliente: {r[0]} | Email: {r[1]} | Idea: {r[2]} | Fecha: {r[3]} {r[4]} | Estado: {r[5]}\n")
        
    return Response(output.getvalue(), mimetype="text/plain",
                    headers={"Content-Disposition": "attachment;filename=reservas_inkflow.txt"})

@app.errorhandler(404)
def pagina_no_encontrada(error):
    return render_template('404.html'), 404

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)