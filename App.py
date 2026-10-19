from flask import Flask, render_template

app = Flask(__name__)

# --- 1. RUTA DE INICIO ---
@app.route('/')
def inicio():
    # Esto le dice a Flask: "Busca el index.html en la carpeta templates"
    return render_template('index.html')

# --- 2. RUTA DE CONTACTO ---
@app.route('/contacto')
def contacto():
    return """
    <h1 style='color: blue;'>📞 Contáctame</h1>
    <p>Escríbeme a mi Instagram: <a href="https://www.instagram.com/cristian_rojas328/" target="_blank">@cristian_rojas328</a></p>
    <a href='/'>Volver al inicio</a>
    """

# --- 3. ARRANCAR EL SERVIDOR ---
if __name__ == '__main__':
    app.run(debug=True)
