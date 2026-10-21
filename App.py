from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

@app.route('/')
def inicio():
    # 1. Creamos una lista vacía
    reservas = []
    
    # 2. Intentamos leer el archivo reservas.txt
    try:
        with open("reservas.txt", "r", encoding="utf-8") as archivo:
            reservas = archivo.readlines()
    except FileNotFoundError:
        pass # Si el archivo no existe todavía, no pasa nada, la lista queda vacía
        
    # 3. Enviamos la lista al HTML (Jinja2 se encarga de mostrarla)
    return render_template('index.html', lista_reservas=reservas)

@app.route('/contacto')
def contacto():
    return "<h1 style='color: blue;'>📞 Contáctame</h1><a href='/'>Volver al inicio</a>"

@app.route('/reservar', methods=['POST'])
def reservar():
    nombre_cliente = request.form.get('nombre')
    idea_cliente = request.form.get('idea')
    
    with open("reservas.txt", "a", encoding="utf-8") as archivo:
        archivo.write(f"Cliente: {nombre_cliente} | Idea: {idea_cliente}\n")
    
    # ¡MAGIA! En vez de mostrar texto blanco, te redirige al inicio
    return redirect(url_for('inicio'))

if __name__ == '__main__':
    app.run(debug=True)
