from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///seu_banco_de_dados.db'
app.config['SECRET_KEY'] = 'your_secret_key'
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Definição do modelo Usuario
class Usuario(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(80), unique=True, nullable=False)
    senha = db.Column(db.String(120), nullable=False)
    matricula = db.Column(db.String(20), unique=True, nullable=False)

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

# Criação de todas as tabelas
with app.app_context():
    db.create_all()

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

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        matricula = request.form['matricula']
        new_user = Usuario(user=username, senha=password, matricula=matricula)
        db.session.add(new_user)
        db.session.commit()
        flash('User registered successfully!')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/relatorios')
@login_required
def relatorios():
    return render_template('relatorios.html')

@app.route('/analise-dos-dados', methods=['GET', 'POST'])
@login_required
def analise_dos_dados():
    if request.method == 'POST':
        # Handle data inclusion
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

        new_data = DadosPrograma(
            nproduto=nproduto, peso=peso, datai=datai, horai=horai, dataf=dataf,
            horaf=horaf, marcha=marcha, defprod=defprod, motivo=motivo, 
            acaocorre=acaocorre, respons=respons, obs=obs
        )
        db.session.add(new_data)
        db.session.commit()
        flash('Dados incluídos com sucesso!')
        return redirect(url_for('analise_dos_dados'))

    dados_programa = DadosPrograma.query.all()
    return render_template('analise_dos_dados.html', dados_programa=dados_programa)

@app.route('/consultar_dados', methods=['GET'])
def consultar_dados():
    dados = DadosPrograma.query.all()  # Supondo que 'DadosPrograma' seja o modelo correto
    return render_template('consultar_dados.html', dados=dados)

@app.route('/ocorrencias')
@login_required
def ocorrencias():
    return render_template('ocorrencias.html')

if __name__ == '__main__':
    app.run(debug=True)
