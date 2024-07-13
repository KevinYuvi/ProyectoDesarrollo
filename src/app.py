from flask import Flask, render_template, request, redirect, url_for, session
from pymongo import MongoClient
from bson.objectid import ObjectId


app = Flask(__name__)

app.secret_key = 'your_secret_key'  # Necesario para manejar sesiones

client = MongoClient("mongodb://localhost:27017/")
db = client["voluntariado"]
users_collection = db["usuarios"]

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
    if request.method == 'POST':
        user_id = session.get('user_id')  # Asegúrate de que el ID del usuario esté almacenado en la sesión
        interests = request.form.getlist('interests')  # Obtener la lista de intereses seleccionados
        
        if user_id:
            # Actualizar la base de datos con los intereses del usuario
            users_collection.update_one({'_id': ObjectId(user_id)}, {'$set': {'interests': interests}})
            return redirect(url_for('index'))
        else:
            return redirect(url_for('login'))  # Redirigir al inicio de sesión si el ID de usuario no está disponible

    return render_template('intereses.html')

@app.route('/logout')
def logout():
    session.pop('user', None)  # Cierra sesión de usuario de la sesión
    return redirect(url_for('home'))
if __name__ == '__main__':
    app.run(debug=True)
