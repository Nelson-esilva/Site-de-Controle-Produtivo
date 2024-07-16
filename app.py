from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class Usuario(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(100), unique=True, nullable=False)
    senha = db.Column(db.String(20), nullable=False)
    matricula = db.Column(db.String(30))

class DadosPrograma(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nproduto = db.Column(db.String(100))
    peso = db.Column(db.String(20))
    datai = db.Column(db.Date)
    horai = db.Column(db.Time)
    dataf = db.Column(db.Date)
    horaf = db.Column(db.Time)
    marcha = db.Column(db.Boolean)
    defprod = db.Column(db.String(100))
    motivo = db.Column(db.String(100))
    acaocorre = db.Column(db.String(100))
    respons = db.Column(db.String(100))
    obs = db.Column(db.String(200))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        matricula = request.form['matricula']
        
        # Verificar se o usuário já existe
        if Usuario.query.filter_by(user=username).first():
            flash('Usuário já existe. Escolha outro.')
            return redirect(url_for('register'))
        
        # Criar novo usuário
        new_user = Usuario(user=username, senha=password, matricula=matricula)
        db.session.add(new_user)
        db.session.commit()
        
        flash('Usuário criado com sucesso! Você pode fazer login agora.')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = Usuario.query.filter_by(user=username).first()
        if user and user.senha == password:
            login_user(user)
            return redirect(url_for('profile'))
        else:
            flash('Login Failed. Check your username and password')
    return render_template('login.html')

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', name=current_user.user)

@app.route('/analise_dados')
@login_required
def analise_dados():
    return render_template('analise_dados.html')

@app.route('/consultar_dados')
@login_required
def consultar_dados():
    dados = DadosPrograma.query.all()
    return render_template('consultar_dados.html', dados=dados)

@app.route('/incluir_dados', methods=['GET', 'POST'])
@login_required
def incluir_dados():
    if request.method == 'POST':
        nproduto = request.form['nproduto']
        peso = request.form['peso']
        datai = request.form['datai']
        horai = request.form['horai']
        dataf = request.form['dataf']
        horaf = request.form['horaf']
        marcha = 'marcha' in request.form
        defprod = request.form['defprod']
        motivo = request.form['motivo']
        acaocorre = request.form['acaocorre']
        respons = request.form['respons']
        obs = request.form['obs']
        
        new_dado = DadosPrograma(nproduto=nproduto, peso=peso, datai=datai, horai=horai, dataf=dataf, horaf=horaf, marcha=marcha, defprod=defprod, motivo=motivo, acaocorre=acaocorre, respons=respons, obs=obs)
        db.session.add(new_dado)
        db.session.commit()
        
        flash('Dados incluídos com sucesso!')
        return redirect(url_for('consultar_dados'))
    
    return render_template('incluir_dados.html')

@app.route('/relatorios')
@login_required
def relatorios():
    return "Página de Relatórios"

@app.route('/ocorrencias')
@login_required
def ocorrencias():
    return "Página de Ocorrências"

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

def init_db():
    with app.app_context():
        db.create_all()  # Create tables if they don't exist

if __name__ == '__main__':
    if not os.path.exists('users.db'):
        init_db()
    app.run(debug=True)