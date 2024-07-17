from flask import Flask, render_template, request, redirect, url_for, session, Response, flash
from flask_mysqldb import MySQL, MySQLdb
from pymongo import MongoClient
from bson.objectid import ObjectId

app = Flask(__name__, template_folder='templates')

app.secret_key = 'grupo6'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '1234'
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
                session['user_id'] = account['id']  # Almacenar el ID del usuario en la sesión
                return redirect(url_for('ingresar'))
            else:
                #Validacion de usuario y contraseña
                flash("Credenciales inválidas. Por favor, intenta nuevamente.", "error")
                return redirect(url_for('login'))
        
        except Exception as e:
            return str(e)
    return render_template('login.html')


@app.route('/ingresar', methods=['GET'])
def ingresar():
    return render_template('ingresar.html')

@app.route('/registro', methods=['GET', 'POST'])
def registro():
        return render_template('registro.html')
    
@app.route('/crear_registro', methods=['GET', 'POST'])
def crear_registro():
    if request.method == 'POST':
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        phone = request.form['phone']
        country = request.form['country']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        #Validacion campo telefono
        if not phone.isdigit():
            flash("El campo de teléfono solo debe contener números.", "error")
            return redirect(url_for('registro'))
        
        #Validacion campo nombre
        if not firstname.isalpha():
            flash("El campo de nombre solo debe contener letras.", "error")
            return redirect(url_for('registro'))
        
        #Validacion campo apellido
        if not lastname.isalpha():
            flash("El campo de apellido solo debe contener letras.", "error")
            return redirect(url_for('registro'))

        #Validacion campo confirmar contraseña
        if password != confirm_password:
            flash("Las contraseñas no coinciden. Por favor, inténtelo de nuevo.", "error")
            return redirect(url_for('registro'))
          
        try:
            #Validacion de correo existente
            cur = mysql.connection.cursor() 
            cur.execute("SELECT email FROM usuarios WHERE email = %s", (email,))
            existing_email = cur.fetchone()  
            if existing_email:
                flash("El correo ya está registrado. Por favor, use otro correo.", "error")
                return redirect(url_for('registro'))
            
            #Insertar el registro correcto en la base
            cur.execute(
                "INSERT INTO usuarios (firstname, lastname, phone, country, email, password) VALUES (%s, %s, %s, %s, %s, %s)",
                (firstname, lastname, phone, country, email, password)
            )
            mysql.connection.commit()
            
            # Obtener el ID del usuario recién insertado
            user_id = cur.lastrowid
            cur.close()

            # Almacenar el ID del usuario en la sesión
            session['user_id'] = user_id

            return redirect(url_for('intereses'))
        except Exception as e:
            return str(e)

    return render_template('crear_registro.html')


@app.route('/intereses', methods=['GET', 'POST'])
def intereses():
    if request.method == 'POST':
        user_id = session.get('user_id')  # Obtener el ID del usuario desde la sesión
        interes = request.form.getlist('interes')  # Obtener la lista de intereses seleccionados

        if user_id:
            # Crear el documento para MongoDB
            usuario_intereses = {
                "_id": str(user_id),
                "intereses": ', '.join(interes)  # Convertir la lista de intereses en una cadena separada por comas
            }

            # Insertar o actualizar el documento en la colección de MongoDB
            users_collection.update_one(
                {'_id': usuario_intereses['_id']}, 
                {'$set': usuario_intereses}, 
                upsert=True
            )

            return redirect(url_for('index'))
        else:
            return redirect(url_for('login'))  # Redirigir al inicio de sesión si el ID de usuario no está disponible

    return render_template('intereses.html')

@app.route('/logout')
def logout():
    session.pop('user', None)  # Cierra sesión de usuario de la sesión
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.secret_key = 'grupo6'
    app.run(host='localhost', debug=True, port=2024)
    
