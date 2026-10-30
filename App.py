from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os

app = Flask(__name__)

app.secret_key = os.environ.get('SECRET_KEY', 'inkflow_super_secreto_2026')

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
