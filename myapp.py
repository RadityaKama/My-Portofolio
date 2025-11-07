import pymysql
pymysql.install_as_MySQLdb()

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session 
)
from flask_mysqldb import MySQL
from functools import wraps
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

app.config['SECRET_KEY'] = '@#$%'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '' 
app.config['MYSQL_DB'] = 'portofolio'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor' 

UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static', 'image')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

mysql = MySQL(app)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def save_picture(file):
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return filename
    return None

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'loggedin' not in session:
            flash('Anda harus login untuk mengakses halaman ini.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE id = 1") 
        profile = cur.fetchone() 
        cur.execute("SELECT * FROM projects ORDER BY id DESC")
        projects = cur.fetchall() 
        cur.execute("SELECT * FROM skills")
        skills = cur.fetchall()
        cur.close()
        
        return render_template('index.html', 
                               profile=profile, 
                               projects=projects, 
                               skills=skills)
    except Exception as e:
        flash(f"Error database: {e}", "danger")
        return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'loggedin' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cur.fetchone()
        cur.close()
        
        if user and user['password'] == password:
            session['loggedin'] = True
            session['id'] = user['id']
            session['username'] = user['username']
            flash('Login berhasil!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Login Gagal. Cek username dan password.', 'danger')

    return render_template('login.html') 

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    flash('Anda telah logout.', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    admin_id = session['id']
    cur = mysql.connection.cursor()
    
    action = request.args.get('action')
    id = request.args.get('id', type=int)

    if request.method == 'POST':
        
        if action == 'add_project':
            title = request.form['title']
            description = request.form['description']
            link = request.form['link']
            
            filename = None
            if 'image' in request.files:
                file = request.files['image']
                if file.filename != '':
                    filename = save_picture(file)
            
            cur.execute(
                "INSERT INTO projects (title, description, link, image) VALUES (%s, %s, %s, %s)",
                (title, description, link, filename)
            )
            mysql.connection.commit()
            flash('Proyek baru berhasil ditambahkan!', 'success')

        elif action == 'edit_project' and id:
            title = request.form['title']
            description = request.form['description']
            link = request.form['link']
            
            cur.execute(
                "UPDATE projects SET title=%s, description=%s, link=%s WHERE id=%s",
                (title, description, link, id)
            )
            
            if 'image' in request.files:
                file = request.files['image']
                if file.filename != '':
                    filename = save_picture(file)
                    cur.execute("UPDATE projects SET image=%s WHERE id=%s", (filename, id))

            mysql.connection.commit()
            flash('Proyek berhasil diperbarui!', 'success')

        elif action == 'add_skill':
            name = request.form['name']
            level = request.form['level']
            icon = request.form['icon']
            cur.execute(
                "INSERT INTO skills (name, level, icon) VALUES (%s, %s, %s)",
                (name, level, icon)
            )
            mysql.connection.commit()
            flash('Skill baru berhasil ditambahkan!', 'success')

        elif action == 'edit_skill' and id:
            name = request.form['name']
            level = request.form['level']
            icon = request.form['icon']
            cur.execute(
                "UPDATE skills SET name=%s, level=%s, icon=%s WHERE id=%s",
                (name, level, icon, id)
            )
            mysql.connection.commit()
            flash('Skill berhasil diperbarui!', 'success')
        
        elif action == 'main' or action is None:
            name = request.form['name']
            bio = request.form['bio']
            
            cur.execute(
                "UPDATE users SET name=%s, bio=%s WHERE id=%s",
                (name, bio, admin_id)
            )

            if 'photo' in request.files:
                file = request.files['photo']
                if file.filename != '':
                    filename = save_picture(file)
                    cur.execute("UPDATE users SET photo=%s WHERE id=%s", (filename, admin_id))
            
            mysql.connection.commit()
            flash('Profil berhasil diperbarui!', 'success')
        
        cur.close()
        return redirect(url_for('dashboard'))

    admin_name = session.get('username', 'Admin')
    
    if action == 'add_project':
        cur.close()
        return render_template('dashboard.html', action=action, title="Tambah Proyek", project=None, admin_name=admin_name)

    elif action == 'edit_project' and id:
        cur.execute("SELECT * FROM projects WHERE id = %s", (id,))
        project = cur.fetchone()
        cur.close()
        if not project:
            flash('Proyek tidak ditemukan!', 'danger')
            return redirect(url_for('dashboard'))
        return render_template('dashboard.html', action=action, title="Edit Proyek", project=project, admin_name=admin_name)

    elif action == 'add_skill':
        cur.close()
        return render_template('dashboard.html', action=action, title="Tambah Skill", skill=None, admin_name=admin_name)

    elif action == 'edit_skill' and id:
        cur.execute("SELECT * FROM skills WHERE id = %s", (id,))
        skill = cur.fetchone()
        cur.close()
        if not skill:
            flash('Skill tidak ditemukan!', 'danger')
            return redirect(url_for('dashboard'))
        return render_template('dashboard.html', action=action, title="Edit Skill", skill=skill, admin_name=admin_name)

    else:
        cur.execute("SELECT * FROM users WHERE id = %s", (admin_id,))
        profile = cur.fetchone()
        cur.execute("SELECT * FROM projects")
        projects = cur.fetchall()
        cur.execute("SELECT * FROM skills")
        skills = cur.fetchall()
        cur.close()
        
        return render_template('dashboard.html', 
                               action='main',
                               profile=profile,
                               projects=projects, 
                               skills=skills, 
                               admin_name=admin_name)

@app.route('/admin/project/delete/<int:id>', methods=['POST'])
@login_required
def delete_project(id):
    try:
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM projects WHERE id = %s", (id,))
        mysql.connection.commit()
        cur.close()
        flash('Proyek berhasil dihapus.', 'success')
    except Exception as e:
        flash(f'Error saat menghapus: {e}', 'danger')
        
    return redirect(url_for('dashboard'))

@app.route('/admin/skill/delete/<int:id>', methods=['POST'])
@login_required
def delete_skill(id):
    try:
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM skills WHERE id = %s", (id,))
        mysql.connection.commit()
        cur.close()
        flash('Skill berhasil dihapus.', 'success')
    except Exception as e:
        flash(f'Error saat menghapus: {e}', 'danger')
        
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True)