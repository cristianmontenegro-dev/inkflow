from flask import Flask, render_template, request # <-- Agregamos 'request'

app = Flask(__name__)

@app.route('/')
def inicio():
    return render_template('index.html')

@app.route('/contacto')
def contacto():
    return "<h1 style='color: blue;'>📞 Contáctame</h1><a href='/'>Volver al inicio</a>"

# --- NUEVA RUTA PARA RECIBIR EL FORMULARIO ---
@app.route('/reservar', methods=['POST']) # methods=['POST'] significa "recibe datos"
def reservar():
    # Leemos lo que el usuario escribió en los inputs
    nombre_cliente = request.form.get('nombre')
    idea_cliente = request.form.get('idea')
    
    # Guardamos la reserva en un archivo de texto
    with open("reservas.txt", "a", encoding="utf-8") as archivo:
        archivo.write(f"Cliente: {nombre_cliente} | Idea: {idea_cliente}\n")
    
    # Le mostramos un mensaje al cliente
    return f"""
    <h1 style='color: green;'>¡Gracias, {nombre_cliente}!</h1>
    <p>Tu idea de tatuaje fue guardada en nuestro sistema.</p>
    <a href='/'>Volver al inicio</a>
    """

if __name__ == '__main__':
    app.run(debug=True)
