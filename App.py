from flask import Flask, render_template, request, redirect, url_for
import sqlite3 # <-- Importamos la base de datos

app = Flask(__name__)

# --- FUNCIÓN PARA CREAR LA BASE DE DATOS ---
def init_db():
    # Se conecta al archivo inkflow.db (si no existe, lo crea)
    conn = sqlite3.connect('inkflow.db')
    cursor = conn.cursor()
    # Crea la tabla 'reservas' si no existe
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reservas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            idea TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Ejecutamos la función para asegurarnos de que la base de datos existe
init_db()

# --- RUTA DE INICIO ---
@app.route('/')
def inicio():
    conn = sqlite3.connect('inkflow.db')
    cursor = conn.cursor()
    # Le pedimos a la base de datos TODAS las reservas
    cursor.execute("SELECT * FROM reservas")
    reservas = cursor.fetchall() # Guarda todo en una lista
    conn.close()
    
    return render_template('index.html', lista_reservas=reservas)

# --- RUTA PARA RECIBIR EL FORMULARIO ---
@app.route('/reservar', methods=['POST'])
def reservar():
    nombre_cliente = request.form.get('nombre')
    idea_cliente = request.form.get('idea')
    
    conn = sqlite3.connect('inkflow.db')
    cursor = conn.cursor()
    # Insertamos los datos (los signos ? evitan hackeos, se llaman 'consultas parametrizadas')
    cursor.execute("INSERT INTO reservas (nombre, idea) VALUES (?, ?)", (nombre_cliente, idea_cliente))
    conn.commit()
    conn.close()
    
    return redirect(url_for('inicio'))

@app.route('/borrar/<int:id>')
def borrar(id):
    conn = sqlite3.connect('inkflow.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM reservas WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('inicio'))

import os

if __name__ == '__main__':
    # En local usa el 5000, en Render usará el puerto que le asignen
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
