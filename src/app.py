from flask import Flask, render_template, request, redirect, url_for, session, Response
from flask_mysqldb import MySQL, MySQLdb
from pymongo import MongoClient
from bson.objectid import ObjectId

app = Flask(__name__, template_folder='templates')

app.secret_key = 'your_secret_key'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'prueba1' #Base de datos
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

#Inicializar la extension de MySQL
mysql = MySQL(app)

client = MongoClient("mongodb://localhost:27017/")
db = client["voluntariado"]
users_collection = db["usuarios"]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html')
    
@app.route('/acceso_login', methods=['GET', 'POST'])
def acceso_login():
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        _correo = request.form['email']
        _password = request.form['password']
        try:
            cur = mysql.connection.cursor()
            cur.execute("SELECT * FROM usuarios WHERE email = %s AND password = %s", (_correo, _password))
            account = cur.fetchone()
            cur.close()
            
            if account:
                session['logueado'] = True
                session['id'] = account['id']
                return render_template("ingresar.html")
            else:
                return render_template('login.html', error='Credenciales inválidas. Por favor, intenta nuevamente.')
        except Exception as e:
            return str(e)
    return render_template('login.html')

@app.route('/ingresar', methods=['GET'])
def ingresar():
    return render_template('ingresar.html')

@app.route('/registro', methods=['GET', 'POST'])
def registro():
        return render_template('registro.html')
    
@app.route('/crear_registro', methods = ['GET', 'POST'])
def crear_registro():
    if request.method == 'POST':
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        phone = request.form['phone']
        country = request.form['country']
        email = request.form['email']
        password = request.form['password']
        try:
            cur = mysql.connection.cursor()
            cur.execute(
                "INSERT INTO usuarios (firstname, lastname, phone, country, email, password) VALUES (%s, %s, %s, %s, %s, %s)",
                (firstname, lastname, phone, country, email, password)
            )
            mysql.connection.commit()
            cur.close()
            return render_template('intereses.html')
        except Exception as e:
            return str(e)

    return render_template('crear_registro.html')

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
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.secret_key = 'your_secret_key'
    app.run(host='localhost', debug=True, port=2024)
    
