from flask import Flask, request, render_template, redirect, url_for, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

# Configuración de Flask
app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Configuración de la base de datos SQLite
DATABASE = 'users.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def create_user_table():
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
        ''')
        conn.commit()

create_user_table()

# Ruta para la página de inicio
@app.route('/')
def home():
    return render_template('home.html')

# Ruta para registrar usuarios
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if not username or not password:
            flash('Por favor, complete todos los campos', 'warning')
            return redirect(url_for('register'))
        
        hashed_password = generate_password_hash(password, method='sha256')
        
        try:
            with get_db() as conn:
                cursor = conn.cursor()
                cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))
                conn.commit()
            flash('Usuario registrado exitosamente', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('El nombre de usuario ya existe', 'danger')
            return redirect(url_for('register'))

    return render_template('register.html')

# Ruta para iniciar sesión
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if not username or not password:
            flash('Por favor, complete todos los campos', 'warning')
            return redirect(url_for('login'))

        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT password FROM users WHERE username = ?', (username,))
            user = cursor.fetchone()
        
        if user and check_password_hash(user['password'], password):
            flash('Inicio de sesión exitoso', 'success')
            return redirect(url_for('home'))
        else:
            flash('Nombre de usuario o contraseña incorrectos', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')

if __name__ == '__main__':
    app.run(port=8500)
