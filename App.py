from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'inkflow_super_secreto_2026'

def init_db():
    conn = sqlite3.connect('inkflow.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reservas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            idea TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def inicio():
    return render_template('index.html')


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


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form.get('usuario')
        contrasena = request.form.get('contrasena')
        
        if usuario == 'cristian' and contrasena == 'tatuaje2026':
            session['logged_in'] = True 
            return redirect(url_for('admin'))
        else:
            return render_template('login.html', error="Usuario o contraseña incorrectos")
            
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('logged_in', None) 
    return redirect(url_for('login'))


@app.route('/admin')
def admin():
    
    if not session.get('logged_in'):
        return redirect(url_for('login'))
        
    conn = sqlite3.connect('inkflow.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM reservas")
    reservas = cursor.fetchall()
    conn.close()
    
    return render_template('admin.html', lista_reservas=reservas)


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

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
