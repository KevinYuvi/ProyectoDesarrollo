from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from flask_mysqldb import MySQL
from pymongo import MongoClient
from bson.objectid import ObjectId
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import pandas as pd


app = Flask(__name__, template_folder='templates')

app.secret_key = 'your_secret_key'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'prueba1'  # Base de datos
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

# Inicializar la extensión de MySQL
mysql = MySQL(app)

client = MongoClient("mongodb://localhost:27017/")
db = client["voluntariado"]
usuarios_collection = db["usuarios"]
oportunidades_collection = db["oportunidades"]

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
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
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
    user_id = session.get('user_id')  # Obtener el ID del usuario desde la sesión
    if not user_id:
        return redirect(url_for('login'))  # Redirigir al inicio de sesión si el ID de usuario no está disponible

    if request.method == 'POST':
        intereses = request.form.getlist('intereses')  # Obtener la lista de intereses seleccionados

        if intereses:
            # Crear el documento para MongoDB
            user_interests_document = {
                "_id": str(user_id),
                "intereses": ', '.join(intereses)  # Convertir la lista de intereses en una cadena separada por comas
            }

            # Insertar o actualizar el documento en la colección de MongoDB
            usuarios_collection.update_one(
                {'_id': user_interests_document['_id']}, 
                {'$set': user_interests_document}, 
                upsert=True
            )

            return redirect(url_for('index'))
        else:
            return render_template('intereses.html', error='Por favor, selecciona al menos un interés.')
    
    return render_template('intereses.html')



# Función para obtener recomendaciones basadas en intereses de usuario
def obtener_recomendaciones(usuario_id, umbral_similitud=0.1):
    usuario = usuarios_collection.find_one({"_id": usuario_id})
    if not usuario:
        return []

    intereses_usuario = usuario.get("intereses", "")
    if not intereses_usuario:
        # Retorna un mensaje indicando que no hay intereses disponibles
        return [{"title": "No hay intereses", "description": "El usuario no tiene intereses seleccionados", "link": "#"}]

    oportunidades = list(oportunidades_collection.find())
    if not oportunidades:
        return []

    df = pd.DataFrame(oportunidades)

    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform([intereses_usuario] + list(df['description']))
    cosine_sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()

    # Filtrar oportunidades por umbral de similitud
    indices_similares = [i for i, sim in enumerate(cosine_sim) if sim >= umbral_similitud]

    recomendaciones = []
    for idx in indices_similares:
        recomendaciones.append({
            'title': df.iloc[idx]['title'],
            'description': df.iloc[idx]['description'],
            'link': df.iloc[idx]['link']
        })

    return recomendaciones

# Ruta para obtener recomendaciones mediante API
@app.route('/api/recommendations', methods=['POST'])
def get_recommendations():
    data = request.get_json()
    user_id = data.get('userId')
    umbral_similitud = data.get('umbralSimilitud', 0.01)  # Obtener el umbral de similitud del cuerpo de la solicitud, valor por defecto es 0.1

    recomendaciones = obtener_recomendaciones(user_id, umbral_similitud)
    
    return jsonify({'recommendations': recomendaciones})


@app.route('/api/search', methods=['POST'])
def search_voluntariados():
    data = request.get_json()
    query = data.get('query', '').strip().lower()

    if not query:
        return jsonify({'error': 'La consulta de búsqueda está vacía'}), 400

    oportunidades = list(oportunidades_collection.find())
    filtered_oportunidades = [
        oportunidad for oportunidad in oportunidades
        if query in oportunidad['title'].lower() or query in oportunidad['description'].lower()
    ]

    if not filtered_oportunidades:
        return jsonify({'voluntariados': []})

    recomendaciones = [
        {
            'title': oportunidad['title'],
            'description': oportunidad['description'][:100] + '...',
            'link': oportunidad['link']
        }
        for oportunidad in filtered_oportunidades
    ]

    return jsonify({'voluntariados': recomendaciones})


@app.route('/logout')
def logout():
    session.pop('user', None)  # Cierra sesión de usuario de la sesión
    session.pop('user_id', None)  # Asegúrate de eliminar también el user_id de la sesión
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.secret_key = 'your_secret_key'
    app.run(host='localhost', debug=True, port=2024)
