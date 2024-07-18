from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime
import pandas as pd
import plotly.express as px
import plotly.io as pio

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///seu_banco_de_dados.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
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
    return redirect(url_for('login'))  # Redireciona para a página de login

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

@app.route('/relatorios', methods=['GET', 'POST'])
def relatorios():
    colunas = [col.name for col in DadosPrograma.__table__.columns]
    dados = DadosPrograma.query.all()
    df = pd.DataFrame([(dado.nproduto, dado.peso, dado.datai, dado.horai, dado.dataf, dado.horaf, dado.marcha, dado.defprod, dado.motivo, dado.acaocorre, dado.respons, dado.obs) for dado in dados],
                      columns=['nproduto', 'peso', 'datai', 'horai', 'dataf', 'horaf', 'marcha', 'defprod', 'motivo', 'acaocorre', 'respons', 'obs'])

    fig = None
    selected_columns = []

    if request.method == 'POST':
        selected_columns = request.form.getlist('colunas')
        if selected_columns:
            df = df[selected_columns]
            fig = px.line(df, x=selected_columns[0], y=selected_columns[1:])
            graph_html = pio.to_html(fig, full_html=False)
        else:
            graph_html = ""

    else:
        graph_html = ""

    return render_template('relatorios.html', colunas=colunas, graph_html=graph_html, selected_columns=selected_columns)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/consultar_dados', methods=['GET', 'POST'])
def consultar_dados():
    dados_json = []
    if request.method == 'POST':
        filtro = request.form.get('filtro')
        colunas = request.form.getlist('colunas')
        query = DadosPrograma.query

        if filtro == 'diaria':
            dia = request.form.get('data_diaria')
            if dia:
                dia = datetime.strptime(dia, '%Y-%m-%d').date()
                query = query.filter(DadosPrograma.datai == dia)
        elif filtro == 'mensal':
            mes = request.form.get('data_mensal')
            if mes:
                ano, mes = mes.split('-')
                query = query.filter(db.extract('month', DadosPrograma.datai) == int(mes),
                                    db.extract('year', DadosPrograma.datai) == int(ano))
        elif filtro == 'intervalo':
            data_inicio = request.form.get('data_inicio')
            data_fim = request.form.get('data_fim')
            if data_inicio and data_fim:
                data_inicio = datetime.strptime(data_inicio, '%Y-%m-%d')
                data_fim = datetime.strptime(data_fim, '%Y-%m-%d')
                query = query.filter(DadosPrograma.datai.between(data_inicio, data_fim))
        elif filtro == 'todo':
            # Nenhum filtro específico, apenas todos os dados
            pass

        dados = query.all()

        dados_exibidos = []
        for dado in dados:
            dado_info = {
                'id': dado.id,
                'nproduto': dado.nproduto,
                'peso': dado.peso,
                'datai': dado.datai.strftime('%d/%m/%Y'),  # Formato brasileiro
                'horai': dado.horai.strftime('%H:%M:%S') if dado.horai else '',
                'dataf': dado.dataf.strftime('%d/%m/%Y') if dado.dataf else '',
                'horaf': dado.horaf.strftime('%H:%M:%S') if dado.horaf else '',
                'marcha': dado.marcha,
                'defprod': dado.defprod,
                'motivo': dado.motivo,
                'acaocorre': dado.acaocorre,
                'respons': dado.respons,
                'obs': dado.obs
            }

            # Adiciona colunas selecionadas
            for coluna in list(dado_info.keys()):
                if coluna not in colunas:
                    dado_info.pop(coluna)

            dados_exibidos.append(dado_info)

        return render_template('consultar_dados.html', dados=dados_exibidos)

    return render_template('consultar_dados.html', dados=dados_json)

@app.route('/incluir_dados', methods=['GET', 'POST'])
@login_required
def incluir_dados():
    if request.method == 'POST':
        nproduto = request.form['nproduto']
        peso = request.form['peso']
        datai = datetime.strptime(request.form['datai'], '%Y-%m-%d').date()
        horai = datetime.strptime(request.form['horai'], '%H:%M').time()
        dataf = datetime.strptime(request.form['dataf'], '%Y-%m-%d').date()
        horaf = datetime.strptime(request.form['horaf'], '%H:%M').time()
        marcha = request.form.get('marcha') == 'True'
        defprod = request.form['defprod']
        motivo = request.form['motivo']
        acaocorre = request.form['acaocorre']
        respons = request.form['respons']
        obs = request.form['obs']

        novo_dado = DadosPrograma(
            nproduto=nproduto,
            peso=peso,
            datai=datai,
            horai=horai,
            dataf=dataf,
            horaf=horaf,
            marcha=marcha,
            defprod=defprod,
            motivo=motivo,
            acaocorre=acaocorre,
            respons=respons,
            obs=obs
        )

        db.session.add(novo_dado)
        db.session.commit()
        flash('Dados incluídos com sucesso!')
        return redirect(url_for('profile'))
    
    return render_template('incluir_dados.html')

@app.route('/ocorrencias')
@login_required
def ocorrencias():
    return render_template('ocorrencias.html')

if __name__ == '__main__':
    app.run(debug=True)
