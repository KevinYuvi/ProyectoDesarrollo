from flask import Flask, render_template, request, redirect, url_for, session, Response
from flask_mysqldb import MySQL, MySQLdb
import hashlib

app = Flask(__name__, template_folder='templates')

app.secret_key = 'your_secret_key'

#Configuracion de la base de datos
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '1234'
app.config['MYSQL_DB'] = 'prueba1' #Base de datos
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

#Inicializar la extension de MySQL
mysql = MySQL(app)

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
                
        cur=mysql.connection.cursor()
        cur.execute("SELECT * FROM usuarios WHERE email = %s AND password = %s", (_correo, _password,))
        account = cur.fetchone()
        
        if account:
            session['logueado'] = True
            session['id'] = account['id']
            return render_template("ingresar.html")
        else:
            return render_template('login.html')

@app.route('/ingresar', methods=['GET', 'POST'])
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
    app.run(host='localhost', debug=True, port=2024)

