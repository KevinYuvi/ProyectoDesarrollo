# app.py
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Omitir la lógica de autenticación
        session['user'] = request.form['email']  # Añadir el usuario a la sesión
        return redirect(url_for('ingresar'))
    return render_template('login.html')

@app.route('/ingresar')
def ingresar():
    return render_template('ingresar.html')

@app.route('/logout')
def logout():
    session.pop('user', None)  # Cierra sesión de usuario de la sesión
    return redirect(url_for('home'))
if __name__ == '__main__':
    app.run(debug=True)
