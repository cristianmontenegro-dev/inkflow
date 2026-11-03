from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os
import cloudinary
import cloudinary.uploader

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'inkflow_super_secreto_2026')

# --- CONFIGURACIÓN DE CLOUDINARY ---
cloudinary.config( 
  cloud_name = os.environ.get('CLOUDINARY_CLOUD_NAME', 'tgzwbtsk'), 
  api_key = os.environ.get('CLOUDINARY_API_KEY', '126599169651419'), 
  api_secret = os.environ.get('CLOUDINARY_API_SECRET', 'Yz9hq1hLx06VMgLYCgXI8HvNssY'), # <-- Pon tu secreto real aquí
  secure = True
)

def init_db():
    conn = sqlite3.connect('inkflow.db')
    cursor = conn.cursor()
    # Tabla de reservas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reservas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            idea TEXT NOT NULL
        )
    ''')
    # Tabla de flashes (galería)
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

# --- RUTA DE INICIO (PÚBLICA) ---
@app.route('/')
def inicio():
    conn = sqlite3.connect('inkflow.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM flashes")
    flashes = cursor.fetchall()
    conn.close()
    return render_template('index.html', lista_flashes=flashes)

# --- RUTA PARA RECIBIR EL FORMULARIO ---
@app.route('/reservar', methods=['POST'])
def reservar():
    nombre_cliente = request.form.get('nombre')
    idea_cliente = request.form.get('idea')
    
    conn = sqlite3.connect('inkflow.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO reservas (nombre, idea) VALUES (?, ?)", (nombre_cliente, idea_cliente))
    conn.commit()
    conn.close()
    
    return redirect(url_for('inicio'))

# --- RUTA DE LOGIN ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form.get('usuario')
        contrasena = request.form.get('contrasena')
        
        usuario_correcto = os.environ.get('ADMIN_USER', 'cristian')
        contrasena_correcta = os.environ.get('ADMIN_PASS', 'tatuaje2026')
        
        if usuario == usuario_correcto and contrasena == contrasena_correcta:
            session['logged_in'] = True
            return redirect(url_for('admin'))
        else:
            return render_template('login.html', error="Usuario o contraseña incorrectos")
            
    return render_template('login.html')

# --- RUTA DE LOGOUT ---
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

# --- RUTA DE ADMINISTRADOR (PROTEGIDA) ---
@app.route('/admin')
def admin():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
        
    conn = sqlite3.connect('inkflow.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM reservas")
    reservas = cursor.fetchall()
    
    cursor.execute("SELECT * FROM flashes")
    flashes = cursor.fetchall()
    
    conn.close()
    return render_template('admin.html', lista_reservas=reservas, lista_flashes=flashes)

# --- RUTA PARA BORRAR RESERVA ---
@app.route('/borrar/<int:id>')
def borrar(id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
        
    conn = sqlite3.connect('inkflow.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM reservas WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin')) 

# --- RUTA PARA EDITAR RESERVA ---
@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
        
    conn = sqlite3.connect('inkflow.db')
    cursor = conn.cursor()

    if request.method == 'POST':
        nuevo_nombre = request.form.get('nombre')
        nueva_idea = request.form.get('idea')
        cursor.execute("UPDATE reservas SET nombre = ?, idea = ? WHERE id = ?", (nuevo_nombre, nueva_idea, id))
        conn.commit()
        conn.close()
        return redirect(url_for('admin'))
    else:
        cursor.execute("SELECT * FROM reservas WHERE id = ?", (id,))
        reserva = cursor.fetchone()
        conn.close()
        return render_template('editar.html', reserva=reserva)

# --- RUTA PARA SUBIR FLASH A LA NUBE ---
@app.route('/subir_flash', methods=['POST'])
def subir_flash():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
        
    titulo = request.form.get('titulo')
    archivo = request.files['imagen']
    
    if archivo and archivo.filename != '':
        # Subimos la imagen a Cloudinary
        resultado = cloudinary.uploader.upload(archivo)
        url_imagen = resultado['secure_url']
        
        # Guardamos el título y la URL en la base de datos
        conn = sqlite3.connect('inkflow.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO flashes (titulo, imagen) VALUES (?, ?)", (titulo, url_imagen))
        conn.commit()
        conn.close()
        
    return redirect(url_for('admin'))

# --- RUTA PARA BORRAR FLASH ---
@app.route('/borrar_flash/<int:id>')
def borrar_flash(id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
        
    conn = sqlite3.connect('inkflow.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM flashes WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
