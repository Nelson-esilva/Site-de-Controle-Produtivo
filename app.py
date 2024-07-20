from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime
import pandas as pd
import json
import plotly.express as px
import plotly.io as pio

# Criação da aplicação Flask
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///novo-_banco_de_dados.db'  # Configuração do URI do banco de dados
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Desabilita a modificação do rastreamento
app.config['SECRET_KEY'] = 'your_secret_key'  # Chave secreta para segurança

# Inicialização do banco de dados e gerenciador de login
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Página de login

# Definição do modelo Usuario para autenticação
class Usuario(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Identificador único do usuário
    user = db.Column(db.String(80), unique=True, nullable=False)  # Nome de usuário
    senha = db.Column(db.String(120), nullable=False)  # Senha do usuário (em texto plano)
    matricula = db.Column(db.String(20), unique=True, nullable=False)  # Matrícula do usuário

# Definição do modelo DadosPrograma para armazenar dados de produção
class DadosPrograma(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Identificador único do dado
    nproduto = db.Column(db.String(100))  # Nome do produto
    peso = db.Column(db.String(20))  # Peso do produto
    datai = db.Column(db.Date)  # Data de início
    horai = db.Column(db.Time)  # Hora de início
    dataf = db.Column(db.Date)  # Data de fim
    horaf = db.Column(db.Time)  # Hora de fim
    marcha = db.Column(db.Boolean)  # Indicador de marcha
    defprod = db.Column(db.String(100))  # Defeito do produto
    motivo = db.Column(db.String(100))  # Motivo do registro
    acaocorre = db.Column(db.String(100))  # Ação corretiva
    respons = db.Column(db.String(100))  # Responsável
    obs = db.Column(db.String(200))  # Observações

# Criação das tabelas no banco de dados
with app.app_context():
    db.create_all()

# Função para carregar o usuário com base no ID
@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

# Rota para a página inicial, redireciona para a página de login
@app.route('/')
def home():
    return redirect(url_for('login'))

# Rota para a página de login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']  # Obtém o nome de usuário do formulário
        password = request.form['password']  # Obtém a senha do formulário
        user = Usuario.query.filter_by(user=username).first()  # Busca o usuário no banco de dados
        if user and user.senha == password:  # Verifica se a senha está correta
            login_user(user)  # Faz login do usuário
            return redirect(url_for('profile'))  # Redireciona para a página de perfil
        else:
            flash('Login Failed. Check your username and password')  # Mensagem de erro
    return render_template('login.html')  # Renderiza a página de login

# Rota para a página de registro de novos usuários
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']  # Obtém o nome de usuário do formulário
        password = request.form['password']  # Obtém a senha do formulário
        matricula = request.form['matricula']  # Obtém a matrícula do formulário
        new_user = Usuario(user=username, senha=password, matricula=matricula)  # Cria um novo usuário
        db.session.add(new_user)  # Adiciona o usuário ao banco de dados
        db.session.commit()  # Salva as alterações
        flash('User registered successfully!')  # Mensagem de sucesso
        return redirect(url_for('login'))  # Redireciona para a página de login
    return render_template('register.html')  # Renderiza a página de registro

# Rota para a página de perfil do usuário
@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html')  # Renderiza a página de perfil

# Rota para a página de relatórios
@app.route('/relatorios', methods=['GET', 'POST'])
@login_required
def relatorios():
    colunas = [col.name for col in DadosPrograma.__table__.columns]  # Obtém os nomes das colunas do modelo DadosPrograma
    return render_template('relatorios.html', colunas=colunas)  # Renderiza a página de relatórios

# Rota para obter dados de gráficos
@app.route('/get_graph_data', methods=['POST'])
@login_required
def get_graph_data():
    data = request.json  # Obtém dados JSON da solicitação
    graph_type = data.get('graph_type', 'bar')  # Tipo de gráfico
    coluna_x = data.get('coluna_x')  # Coluna do eixo X
    coluna_y = data.get('coluna_y')  # Coluna do eixo Y

    dados = DadosPrograma.query.all()  # Obtém todos os dados do banco de dados
    df = pd.DataFrame([(dado.nproduto, dado.peso, dado.datai, dado.horai, dado.dataf, dado.horaf, dado.marcha, dado.defprod, dado.motivo, dado.acaocorre, dado.respons, dado.obs) for dado in dados],
                      columns=['nproduto', 'peso', 'datai', 'horai', 'dataf', 'horaf', 'marcha', 'defprod', 'motivo', 'acaocorre', 'respons', 'obs'])

    if not coluna_x or not coluna_y:  # Verifica se as colunas foram fornecidas
        return jsonify({'data': [], 'layout': {}})  # Retorna dados vazios se as colunas não estiverem presentes

    if graph_type == 'line':
        fig = px.line(df, x=coluna_x, y=coluna_y)  # Cria um gráfico de linha
    elif graph_type == 'bar':
        fig = px.bar(df, x=coluna_x, y=coluna_y)  # Cria um gráfico de barras
    elif graph_type == 'pie':
        fig = px.pie(df, names=coluna_x, values=coluna_y)  # Cria um gráfico de pizza
    elif graph_type == 'scatter':
        fig = px.scatter(df, x=coluna_x, y=coluna_y)  # Cria um gráfico de dispersão
    
    graph_json = pio.to_json(fig, pretty=True)  # Converte o gráfico para JSON
    graph_data = json.loads(graph_json)  # Converte o JSON em um dicionário

    return jsonify(graph_data)  # Retorna os dados do gráfico em JSON

# Rota para o logout do usuário
@app.route('/logout')
@login_required
def logout():
    logout_user()  # Faz logout do usuário
    return redirect(url_for('login'))  # Redireciona para a página de login

# Rota para consultar dados com filtros
@app.route('/consultar_dados', methods=['GET', 'POST'])
def consultar_dados():
    dados_json = []  # Inicializa uma lista vazia para dados
    if request.method == 'POST':
        filtro = request.form.get('filtro')  # Obtém o filtro do formulário
        colunas = request.form.getlist('colunas')  # Obtém as colunas selecionadas
        query = DadosPrograma.query  # Cria uma consulta para o modelo DadosPrograma

        if filtro == 'diaria':
            dia = request.form.get('data_diaria')  # Obtém a data diária do formulário
            if dia:
                dia = datetime.strptime(dia, '%Y-%m-%d').date()  # Converte a string para uma data
                query = query.filter(DadosPrograma.datai == dia)  # Filtra os dados pela data
        elif filtro == 'mensal':
            mes = request.form.get('data_mensal')  # Obtém o mês e ano do formulário
            if mes:
                ano, mes = mes.split('-')  # Divide o ano e mês
                query = query.filter(db.extract('month', DadosPrograma.datai) == int(mes),
                                    db.extract('year', DadosPrograma.datai) == int(ano))  # Filtra pelos dados do mês e ano
        elif filtro == 'intervalo':
            data_inicio = request.form.get('data_inicio')  # Obtém a data de início
            data_fim = request.form.get('data_fim')  # Obtém a data de fim
            if data_inicio and data_fim:
                data_inicio = datetime.strptime(data_inicio, '%Y-%m-%d')  # Converte a string para data
                data_fim = datetime.strptime(data_fim, '%Y-%m-%d')  # Converte a string para data
                query = query.filter(DadosPrograma.datai.between(data_inicio, data_fim))  # Filtra pelos dados dentro do intervalo
        elif filtro == 'todo':
            # Nenhum filtro específico, apenas todos os dados
            pass

        dados = query.all()  # Obtém todos os dados filtrados

        dados_exibidos = []  # Lista para armazenar os dados exibidos
        for dado in dados:
            dado_info = {
                'id': dado.id,
                'nproduto': dado.nproduto,
                'peso': dado.peso,
                'datai': dado.datai.strftime('%d/%m/%Y'),  # Formato de data brasileiro
                'horai': dado.horai.strftime('%H:%M:%S') if dado.horai else '',  # Hora de início
                'dataf': dado.dataf.strftime('%d/%m/%Y') if dado.dataf else '',  # Data de fim
                'horaf': dado.horaf.strftime('%H:%M:%S') if dado.horaf else '',  # Hora de fim
                'marcha': dado.marcha,
                'defprod': dado.defprod,
                'motivo': dado.motivo,
                'acaocorre': dado.acaocorre,
                'respons': dado.respons,
                'obs': dado.obs
            }

            # Adiciona apenas as colunas selecionadas
            for coluna in list(dado_info.keys()):
                if coluna not in colunas:
                    dado_info.pop(coluna)

            dados_exibidos.append(dado_info)  # Adiciona os dados à lista de dados exibidos

        return render_template('consultar_dados.html', dados=dados_exibidos)  # Renderiza a página com os dados filtrados

    return render_template('consultar_dados.html', dados=dados_json)  # Renderiza a página de consulta de dados

# Rota para incluir novos dados
@app.route('/incluir_dados', methods=['GET', 'POST'])
@login_required
def incluir_dados():
    if request.method == 'POST':
        nproduto = request.form['nproduto']  # Obtém o nome do produto
        peso = request.form['peso']  # Obtém o peso do produto
        datai = datetime.strptime(request.form['datai'], '%Y-%m-%d').date()  # Converte a string para data
        horai = datetime.strptime(request.form['horai'], '%H:%M').time()  # Converte a string para hora
        dataf = datetime.strptime(request.form['dataf'], '%Y-%m-%d').date()  # Converte a string para data
        horaf = datetime.strptime(request.form['horaf'], '%H:%M').time()  # Converte a string para hora
        marcha = request.form.get('marcha') == 'True'  # Obtém o valor booleano para marcha
        defprod = request.form['defprod']  # Obtém o defeito do produto
        motivo = request.form['motivo']  # Obtém o motivo do registro
        acaocorre = request.form['acaocorre']  # Obtém a ação corretiva
        respons = request.form['respons']  # Obtém o responsável
        obs = request.form['obs']  # Obtém as observações

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

        db.session.add(novo_dado)  # Adiciona o novo dado ao banco de dados
        db.session.commit()  # Salva as alterações
        flash('Dados incluídos com sucesso!')  # Mensagem de sucesso
        return redirect(url_for('profile'))  # Redireciona para a página de perfil
    
    return render_template('incluir_dados.html')  # Renderiza a página para inclusão de dados

# Rota para a página de ocorrências (não definida detalhadamente)
@app.route('/ocorrencias')
@login_required
def ocorrencias():
    return render_template('ocorrencias.html')  # Renderiza a página de ocorrências

# Executa a aplicação Flask em modo de depuração
if __name__ == '__main__':
    app.run(debug=True)
