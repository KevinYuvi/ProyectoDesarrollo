# app.py
from flask import Flask, render_template, request, redirect, url_for, session
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Omitir la lógica de autenticación
        session['user'] = request.form['email']  # Añadir el usuario a la sesión
        return redirect(url_for('ingresar'))
    return render_template('login.html')

@app.route('/ingresar', methods=['GET'])
def ingresar():
    return render_template('ingresar.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        print(request.form['firstname'])
        return render_template('intereses.html')
    else:
        return render_template('register.html')

@app.route('/intereses', methods=['GET', 'POST'])
def intereses():
    #Solo ingresa al if si en la pagina mandamos algo
    if request.method == 'POST':
        return render_template('ingresar.html')
    else:
        #De lo contrario carga la plantilla de intereses
        return render_template('intereses.html')

@app.route('/logout')
def logout():
    session.pop('user', None)  # Cierra sesión de usuario de la sesión
    return redirect(url_for('home'))
if __name__ == '__main__':
    app.run(debug=True)
