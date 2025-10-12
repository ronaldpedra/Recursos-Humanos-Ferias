# SISTEMA DE GESTÃO DE FÉRIAS (SGF)

## Roadmap do Projeto: Sistema de Gestão de Férias (SGF)

*Fase 1: Configuração do Ambiente e Estrutura do Projeto*

*Fase 2: Modelagem do Banco de Dados (O Coração do Sistema)*

*Fase 3: Lógica do Backend - Rotas e Regras de Negócio (Flask)*

*Fase 4: Autenticação e Níveis de Acesso (Login e Permissões)*

*Fase 5: Desenvolvimento do Frontend (Templates e Interatividade)*

*Fase 6: Implementação dos Fluxos de Usuário (Militar, Chefe, Gestor)*

---

## Fase 1: Configuração do Ambiente e Estrutura do Projeto

Os arquivos serão organizados seguindo a estrutura típica para um projeto Flask como a seguir:

```bash
/Recursos-Humanos-Ferias/
|-- app/
|   |-- routes/             # (Opcional, mas bom para organizar)
|   |   |-- auth_routes.py
|   |   |-- militar_routes.py
|   |   |-- chefe_routes.py
|   |   `-- gestor_routes.py
|   |-- static/
|   |   |-- css/
|   |   `-- js/
|   |-- templates/
|   |   |-- base.html
|   |   |-- login.html
|   |   `-- ... (outros templates)
|   |-- __init__.py         # Inicializa a aplicação Flask e extensões
|   |-- forms.py            # Definição dos formulários do projeto
|   |-- models.py           # Definição dos modelos do SQLAlchemy
|
|-- Documentation/
|-- migrations/             # Para o Flask-Migrate
|-- venv/
|-- .env                    # Variáveis de ambiente (NÃO versionar no Git)
|-- .gitattributes
|-- .gitignore
|-- config.py               # Configurações da aplicação
|-- LICENSE
|-- README.md
|-- requirements.txt        # Dependências do Python
`-- run.py                  # Ponto de entrada para rodar a aplicação
```

**1. Dependências (requirements.txt):**

```bash
alembic==1.16.5
blinker==1.9.0
click==8.3.0
colorama==0.4.6
Flask==3.1.2
Flask-Login==0.6.3
Flask-Migrate==4.1.0
Flask-SQLAlchemy==3.1.1
Flask-WTF==1.2.2
greenlet==3.2.4
itsdangerous==2.2.0
Jinja2==3.1.6
Mako==1.3.10
MarkupSafe==3.0.3
python-dotenv==1.1.1
SQLAlchemy==2.0.44
typing_extensions==4.15.0
Werkzeug==3.1.3             # Para hash de senhas
WTForms==3.2.1
```

**2. Variáveis de Ambiente (.env):**

Será utilizado o .env para o controle das variáveis de ambiente.

```bash
# .env
SECRET_KEY='uma-chave-secreta-muito-forte-e-aleatoria'
DATABASE_URL='sqlite:///ferias.db' # Ou 'postgresql://user:password@host/dbname'
```

---

# Fase 2: Modelagem do Banco de Dados (SQLAlchemy)

Esta é a parte mais crítica. Precisamos representar corretamente os usuários, seções, períodos aquisitivos e as solicitações.

A seguir verificaremos o `app/models.py`:

```python
# app/models.py
import enum
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db


# Usando Enums para padronizar papéis e status
class PapelUsuario(enum.Enum):
    MILITAR = 'Militar'
    CHEFE_SECAO = 'Chefe de Seção'
    GESTOR = 'Gestor de Pessoal'

class StatusFerias(enum.Enum):
    SOLICITADA = 'Solicitada'
    APROVADA_CHEFE = 'Aprovada pelo Chefe'
    APROVADA_GESTOR = 'Aprovada (Gestor)'
    REPROVADA = 'Reprovada'
    ALTERADA = 'Alterada'
    CANCELADA = 'Cancelada'

class Usuario(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    nome_completo = db.Column(db.String(150), nullable=False)
    nome_guerra = db.Column(db.String(50), nullable=False, unique=True)
    identidade = db.Column(db.String(20), unique=True, nullable=False)
    posto_grad = db.Column(db.String(50), nullable=False) # Ex: 3º Sgt, Cap
    password_hash = db.Column(db.String(256), nullable=False)
    papel = db.Column(db.Enum(PapelUsuario), nullable=False, default=PapelUsuario.MILITAR)
    
    secao_id = db.Column(db.Integer, db.ForeignKey('secao.id'))
    secao = db.relationship('Secao', back_populates='integrantes', foreign_keys=[secao_id])

    periodos_aquisitivos = db.relationship('PeriodoAquisitivo', back_populates='usuario', lazy='dynamic')
    solicitacoes = db.relationship('SolicitacaoFerias', back_populates='solicitante', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Secao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), unique=True, nullable=False)
    chefe_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))

    chefe = db.relationship('Usuario', foreign_keys=[chefe_id])
    integrantes = db.relationship('Usuario', back_populates='secao', foreign_keys=[Usuario.secao_id])

class PeriodoAquisitivo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    ano_referencia = db.Column(db.Integer, nullable=False) # Ex: 2025
    data_inicio_periodo = db.Column(db.Date, nullable=False)
    data_fim_periodo = db.Column(db.Date, nullable=False) # Data em que o direito é adquirido
    dias_saldo = db.Column(db.Integer, nullable=False, default=30)
    
    usuario = db.relationship('Usuario', back_populates='periodos_aquisitivos')
    solicitacoes_vinculadas = db.relationship('SolicitacaoFerias', back_populates='periodo_aquisitivo')

class SolicitacaoFerias(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    solicitante_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    periodo_aquisitivo_id = db.Column(db.Integer, db.ForeignKey('periodo_aquisitivo.id'), nullable=False)
    
    data_inicio = db.Column(db.Date, nullable=False)
    data_fim = db.Column(db.Date, nullable=False)
    dias_solicitados = db.Column(db.Integer, nullable=False)
    
    tipo_solicitacao = db.Column(db.String(50)) # Ex: "30_DIAS", "15_DIAS", "10_DIAS", "DESCONTO"
    status = db.Column(db.Enum(StatusFerias), nullable=False, default=StatusFerias.SOLICITADA)
    
    data_solicitacao = db.Column(db.DateTime, default=db.func.current_timestamp())
    justificativa_reprovacao = db.Column(db.Text)
    
    solicitante = db.relationship('Usuario', back_populates='solicitacoes')
    periodo_aquisitivo = db.relationship('PeriodoAquisitivo', back_populates='solicitacoes_vinculadas')
```

**Lógica Chave a ser implementada no Backend:**

- **Criação do Período Aquisitivo:** Uma função (talvez executada periodicamente ou manualmente pelo gestor) criará os `PeriodoAquisitivo` para os militares, calculando as datas com base nas regras que você forneceu.

- **Consumo de Férias:** Ao criar uma `SolicitacaoFerias`, a lógica **DEVE** buscar o `PeriodoAquisitivo` mais antigo do militar com `dias_saldo > 0` e vincular a solicitação a ele, abatendo o saldo. Se uma solicitação (ex: 30 dias) consumir o saldo de um período antigo (ex: 20 dias) e precisar de mais, ela precisará ser vinculada a múltiplos períodos ou a lógica terá que ser mais complexa (o mais simples é vincular ao mais antigo e garantir que ele tenha saldo suficiente para a parcela solicitada). A regra de consumir o mais antigo é primordial.

- **Cálculo de Dias:** A diferença entre `data_fim` e `data_inicio` deve corresponder aos `dias_solicitados`.

---

# Fase 3: Lógica do Backend - Rotas e Regras de Negócio (Flask)

**Aqui é onde a mágica acontece. Usando Blueprints para organizar:**

- `auth_routes.py`:

    - `/login`: Autentica o usuário e o redireciona para seu dashboard específico (Militar, Chefe, Gestor).

    - `/logout`: Encerra a sessão.

- `militar_routes.py`:

    - `/dashboard`: Tela principal do militar. Mostra o saldo de férias por período aquisitivo, o status das solicitações atuais e um botão para nova solicitação.

    - `/solicitar_ferias`: Formulário para nova solicitação. O frontend (JS) pode ajudar a validar as datas (períodos de 10, 15, 30 dias ou desconto).

    - `/solicitacao/<id>/alterar`: Formulário para solicitar alteração.

- `chefe_routes.py`:

    - `/chefe/dashboard`: Mostra uma lista de solicitações pendentes dos integrantes da sua seção.

    - `/chefe/equipe`: Visualiza o planejamento de férias de toda a sua equipe (aprovadas e solicitadas).

    - `/chefe/solicitacao/<id>/avaliar`: Tela para aprovar, reprovar (com justificativa) ou editar a solicitação de um militar.

- `gestor_routes.py`:

    - `/gestor/dashboard`: Visão geral de todas as solicitações.

    - `/gestor/usuarios`: CRUD de usuários (criar, designar papel, vincular à seção).

    - `/gestor/secoes`: CRUD de seções (criar, designar chefe).

    - `/gestor/ferias/editar/<id>`: Permissão total para editar qualquer solicitação.

---

**Próximos Passos Imediatos**

1. **Montar a Estrutura de Pastas**: Crie as pastas e arquivos conforme descrito na Fase 1.

2. **Configurar o Ambiente Virtual e Instalar as Dependências**:

```bash
python -m venv venv
source venv/bin/activate  # ou venv\Scripts\activate no Windows
pip install -r requirements.txt
```

3. **Codificar os Modelos**: Crie o arquivo `app/models.py` com o código planejado.

4. **Configurar a Aplicação Inicial**: Criar o `__init__.py`, `config.py` e `run.py` para carregar as configurações do `.env`, inicializar o Flask, o SQLAlchemy e o Flask-Migrate.

---

**Esqueleto da nossa aplicação Flask**

 A seguir implemente o código para os três arquivos essenciais que inicializam tudo: `config.py`, `app/__init__.py` e `run.py`.

---

**Passo 1: Arquivo de Configuração (`config.py`)**

Este arquivo irá carregar as variáveis do seu arquivo `.env` e disponibilizá-las para a aplicação.

Crie o arquivo `config.py` na raiz do projeto (`/projeto-ferias/config.py`) e adicione o seguinte código:

```python
# /projeto-ferias/config.py

import os
from dotenv import load_dotenv

# Encontra o caminho absoluto para o diretório raiz do projeto
basedir = os.path.abspath(os.path.dirname(__file__))

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    """Configurações base da aplicação."""
    # Chave secreta para proteger sessões e cookies. MUDE ISSO!
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'voce-nunca-vai-adivinhar'
    
    # Configuração do SQLAlchemy
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'ferias.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
```

**Explicação:**

`load_dotenv()`: Lê o seu arquivo .env e carrega as variáveis (como `SECRET_KEY` e `DATABASE_URL`).

`SQLALCHEMY_DATABASE_URI`: Informa ao SQLAlchemy onde está nosso banco de dados. Usamos SQLite por padrão para facilitar o início, mas pode ser facilmente trocado para PostgreSQL ou MySQL no `.env`.

---

**Passo 2: A Fábrica da Aplicação (`app/__init__.py`)**

Este é o coração da nossa aplicação. Usaremos o padrão "Application Factory", que é uma boa prática para tornar a aplicação mais modular.

Crie o arquivo `__init__.py` dentro da pasta `app` (`/projeto-ferias/app/__init__.py`) e adicione:

```python
# /projeto-ferias/app/__init__.py

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import Config

# Inicializa as extensões (sem vincular a uma app específica ainda)
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
# Define a view de login. Se um usuário não logado tentar acessar uma página protegida,
# ele será redirecionado para esta rota.
login_manager.login_view = 'auth.login' # 'auth' é o nome do Blueprint que criaremos

def create_app(config_class=Config):
    """
    Fábrica que cria e configura a instância da aplicação Flask.
    """
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Inicializa as extensões com a app
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    
    # Importa os modelos para que o Flask-Migrate os reconheça
    from app.models import Usuario

    # Função para carregar o usuário da sessão
    @login_manager.user_loader
    def load_user(user_id):
        return Usuario.query.get(int(user_id))

    # --- Registro dos Blueprints (nossas rotas organizadas) ---
    # Ainda não criamos esses arquivos, mas já deixamos a estrutura pronta.
    # from app.routes.auth_routes import bp as auth_bp
    # app.register_blueprint(auth_bp, url_prefix='/auth')

    # from app.routes.militar_routes import bp as militar_bp
    # app.register_blueprint(militar_bp, url_prefix='/militar')
    
    # Apenas uma rota de teste para garantir que tudo está funcionando
    @app.route('/test')
    def test_page():
        return '<h1>A configuração inicial está funcionando!</h1>'

    return app
```

**Explicação:**

- A função `create_app` é a "fábrica". Ela monta nossa aplicação, carrega as configurações e conecta as extensões (como o banco de dados).

- `login_manager.user_loader`: É uma função exigida pelo Flask-Login. Ela explica como encontrar um usuário no banco de dados a partir do ID que é salvo na sessão do navegador.

---

**Passo 3: Ponto de Entrada (`run.py`)**

Este é o script que você executará para iniciar o servidor de desenvolvimento.

Crie o arquivo `run.py` na raiz do projeto (`/projeto-ferias/run.py`):

```python
# /projeto-ferias/run.py

from app import create_app, db
from app.models import Usuario, Secao, PeriodoAquisitivo, SolicitacaoFerias

# Cria a instância da aplicação usando a nossa fábrica
app = create_app()

@app.shell_context_processor
def make_shell_context():
    """
    Disponibiliza os modelos no shell do Flask para facilitar testes.
    Comando: flask shell
    """
    return {
        'db': db, 
        'Usuario': Usuario, 
        'Secao': Secao, 
        'PeriodoAquisitivo': PeriodoAquisitivo,
        'SolicitacaoFerias': SolicitacaoFerias
    }

if __name__ == '__main__':
    app.run(debug=True)
```

---

**O que Fazer Agora: Inicializando o Banco de Dados**

Com esses arquivos e o `app/models.py` que fizemos antes, a estrutura base está pronta. O próximo passo é criar o banco de dados.

Abra seu terminal na pasta raiz `/projeto-ferias/` (com o ambiente virtual `venv` ativado) e execute os seguintes comandos em sequência:

1. **Informe ao Flask qual é a sua aplicação principal:**

- No Linux/macOS: `export FLASK_APP=run.py`

- No Windows: `set FLASK_APP=run.py`

2. **Crie o repositório de migrações (só precisa ser feito uma vez):**

```bash
flask db init
```

Isso criará a pasta migrations.

3. **Crie a primeira migração (um "snapshot" dos seus modelos):**

```bash
flask db migrate -m "Estrutura inicial do banco de dados"
```

Isso lerá seus modelos em `app/models.py` e criará um script de migração na pasta `migrations/versions/`.

4. **Aplique a migração para criar o banco de dados:**

```bash
flask db upgrade
```

Este comando executará o script e criará o arquivo `ferias.db` na raiz do seu projeto com todas as tabelas que definimos!

**Ao final, você terá um servidor Flask rodando.** Você pode iniciar o servidor com `flask run` ou `python run.py` e acessar `http://127.0.0.1:5000/test` no seu navegador para ver a mensagem de confirmação.

---

Vamos construir o sistema de autenticação. Esta é uma parte fundamental e faremos isso de forma segura e organizada, utilizando as melhores práticas do Flask.

Nosso plano será:

1. **Criar os formulários** de login e registro com a extensão Flask-WTF para validação e segurança.

2. **Desenvolver as rotas** (`/login`, `/logout`) dentro de um Blueprint para manter o código organizado.

3. **Criar os templates HTML** para a página de login e um template base que será herdado por todas as outras páginas.

4. **Criar um comando customizado** para cadastrar o primeiro usuário "Gestor" de forma segura, sem precisar de uma página de registro pública.

---

**Passo 1: Adicionar Flask-WTF e Criar os Formulários**

Primeiro, vamos adicionar a biblioteca que nos ajudará a gerenciar os formulários.

1. Adicione `Flask-WTF` ao seu arquivo `requirements.txt`:

```bash
alembic==1.16.5
blinker==1.9.0
click==8.3.0
colorama==0.4.6
Flask==3.1.2
Flask-Login==0.6.3
Flask-Migrate==4.1.0
Flask-SQLAlchemy==3.1.1
Flask-WTF==1.2.2            # Gestão de formulários
greenlet==3.2.4
itsdangerous==2.2.0
Jinja2==3.1.6
Mako==1.3.10
MarkupSafe==3.0.3
python-dotenv==1.1.1
SQLAlchemy==2.0.44
typing_extensions==4.15.0
Werkzeug==3.1.3             # Para hash de senhas
WTForms==3.2.1
```

2. Instale a nova dependência no seu ambiente virtual (`venv`):

```bash
pip install -r requirements.txt
```

3. Agora, crie um novo arquivo `app/forms.py` para definir nossos formulários.

**Adicione o seguinte código ao arquivo** `/projeto-ferias/app/forms.py`:

```python
# /projeto-ferias/app/forms.py

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length

class LoginForm(FlaskForm):
    """Formulário de login."""
    identidade = StringField(
        'Identidade', 
        validators=[DataRequired(message="Por favor, insira sua identidade.")]
    )
    password = PasswordField(
        'Senha', 
        validators=[DataRequired(message="Por favor, insira sua senha.")]
    )
    remember_me = BooleanField('Lembrar-me')
    submit = SubmitField('Entrar')
```

---

**Passo 2: Criar o Blueprint de Autenticação e as Rotas**

Vamos organizar nossas rotas de autenticação em um arquivo separado.

1. Crie uma nova pasta routes dentro de `app`.

2. Dentro de `app/routes`, crie o arquivo `auth_routes.py`.

**Adicione o seguinte código ao arquivo** /projeto-ferias/app/routes/auth_routes.py:

```python
# /projeto-ferias/app/routes/auth_routes.py

from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user
from app.models import Usuario
from app.forms import LoginForm

# Cria um Blueprint chamado 'auth'
bp = Blueprint('auth', __name__)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    # Se o usuário já estiver logado, redireciona para uma página principal
    if current_user.is_authenticated:
        return redirect(url_for('main.index')) # Criaremos essa rota 'main.index' depois

    form = LoginForm()
    if form.validate_on_submit():
        # Busca o usuário pela identidade no banco de dados
        user = Usuario.query.filter_by(identidade=form.identidade.data).first()
        
        # Verifica se o usuário existe e se a senha está correta
        if user is None or not user.check_password(form.password.data):
            flash('Identidade ou senha inválida.', 'danger')
            return redirect(url_for('auth.login'))
        
        # Loga o usuário com o Flask-Login
        login_user(user, remember=form.remember_me.data)
        flash('Login realizado com sucesso!', 'success')
        
        # Redireciona para o dashboard apropriado (vamos implementar essa lógica depois)
        # Por enquanto, vamos para uma página genérica
        return redirect(url_for('main.index'))

    return render_template('auth/login.html', title='Login', form=form)

@bp.route('/logout')
def logout():
    logout_user()
    flash('Você foi desconectado.', 'info')
    return redirect(url_for('auth.login'))
```

---

**Passo 3: Criar os Templates HTML**

Agora, vamos criar a interface visual.

1. Crie a pasta `auth` dentro de `app/templates`.

2. Crie o arquivo `base.html` em `app/templates/`. Este será nosso template mestre.

Código para `/projeto-ferias/app/templates/base.html`:

```html
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <title>{{ title }} - SGF</title>
</head>
<body>
    <div class="container mt-4">
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ category }} alert-dismissible fade show" role="alert">
                        {{ message }}
                        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                    </div>
                {% endfor %}
            {% endif %}
        {% endwith %}

        {% block content %}{% endblock %}
    </div>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
```

3. Agora, crie a página de login em `app/templates/auth/login.html`.

**Código para** `/projeto-ferias/app/templates/auth/login.html`:

```html
{% extends "base.html" %}

{% block content %}
<div class="row justify-content-center">
    <div class="col-md-6 col-lg-4">
        <div class="card">
            <div class="card-body">
                <h3 class="card-title text-center mb-4">Acessar Sistema</h3>
                <form method="POST" action="" novalidate>
                    {{ form.hidden_tag() }}
                    <div class="mb-3">
                        {{ form.identidade.label(class="form-label") }}
                        {{ form.identidade(class="form-control") }}
                        {% for error in form.identidade.errors %}
                            <span class="text-danger">{{ error }}</span>
                        {% endfor %}
                    </div>
                    <div class="mb-3">
                        {{ form.password.label(class="form-label") }}
                        {{ form.password(class="form-control") }}
                         {% for error in form.password.errors %}
                            <span class="text-danger">{{ error }}</span>
                        {% endfor %}
                    </div>
                    <div class="mb-3 form-check">
                        {{ form.remember_me(class="form-check-input") }}
                        {{ form.remember_me.label(class="form-check-label") }}
                    </div>
                    <div class="d-grid">
                        {{ form.submit(class="btn btn-primary") }}
                    </div>
                </form>
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

---

**Passo 4: Registrar o Blueprint e Criar uma Rota Principal**

Agora, precisamos dizer à nossa aplicação para usar as rotas que acabamos de criar.

Modifique seu arquivo `/projeto-ferias/app/__init__.py`:

```python
# ... (imports no início) ...

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    
    from app.models import Usuario
    
    # ... (@login_manager.user_loader) ...

    # --- Registro dos Blueprints ---
    from app.routes.auth_routes import bp as auth_bp
    app.register_blueprint(auth_bp) # Não precisa de prefixo para /login

    # Vamos criar um Blueprint principal para a página inicial
    from flask import Blueprint, render_template
    from flask_login import login_required
    
    main_bp = Blueprint('main', __name__)

    @main_bp.route('/')
    @main_bp.route('/index')
    @login_required # Protege esta rota, exigindo login
    def index():
        return "<h1>Bem-vindo ao Sistema de Gestão de Férias!</h1>"

    app.register_blueprint(main_bp)

    @app.route('/test')
    def test_page():
        return '<h1>A configuração inicial está funcionando!</h1>'

    return app
```

---

**Passo 5: Criar o Comando para Cadastrar o Gestor**

Esta é a forma mais segura de criar o primeiro usuário. Adicionaremos um comando personalizado ao Flask.

**Abra o arquivo `run.py` e adicione o seguinte código:**

```python
# /projeto-ferias/run.py

from app import create_app, db
from app.models import Usuario, Secao, PeriodoAquisitivo, SolicitacaoFerias, PapelUsuario
import click # Importe o click

app = create_app()

# ... (código do make_shell_context) ...

@app.cli.command("create-gestor")
@click.argument("nome_guerra")
@click.argument("identidade")
@click.argument("password")
def create_gestor(nome_guerra, identidade, password):
    """Cria um novo usuário com o papel de Gestor."""
    if Usuario.query.filter_by(identidade=identidade).first():
        print(f"Erro: Usuário com identidade {identidade} já existe.")
        return

    gestor = Usuario(
        nome_completo=f"{nome_guerra} (Gestor)",
        nome_guerra=nome_guerra,
        identidade=identidade,
        posto_grad="Admin",
        papel=PapelUsuario.GESTOR
    )
    gestor.set_password(password)
    db.session.add(gestor)
    db.session.commit()
    print(f"Usuário Gestor '{nome_guerra}' criado com sucesso!")

if __name__ == '__main__':
    app.run(debug=True)
```

**Como Usar**

1. **Abra o terminal** na pasta raiz do projeto com o ambiente virtual ativado.

2. **Execute o comando** para criar seu primeiro gestor, substituindo os dados pelos que você desejar:

```bash
flask create-gestor Chaves 1234567890 senhaforte123
```

Você deverá ver a mensagem: `Usuário Gestor 'Chaves' criado com sucesso!`

---

Ótimo! Vamos mergulhar na construção das funcionalidades do Gestor de Pessoal. Esta é a espinha dorsal administrativa do sistema, então vamos construí-la de forma robusta e intuitiva.

Nosso plano de ação será:

1. **Proteger as Rotas do Gestor**: Criaremos um mecanismo para garantir que apenas usuários com o papel de "Gestor" possam acessar essas páginas.

2. **Gerenciamento de Seções**: Construiremos a interface para o gestor criar, visualizar e editar as seções da organização.

3. **Gerenciamento de Militares**: Em seguida, faremos a interface para o gestor cadastrar novos militares, editar seus dados e vinculá-los a uma seção.

4. **Atualizar o Dashboard**: Criaremos um painel de controle para o Gestor, que servirá como ponto de partida para todas as ações administrativas.

---

**Passo 1: Criar um Decorator para Proteção de Rota**

Para evitar que um militar comum acesse as páginas de administração, criaremos um "decorator" personalizado.

Crie um novo arquivo chamado `decorators.py` dentro da pasta `app` (`/projeto-ferias/app/decorators.py`):

```python
# /projeto-ferias/app/decorators.py

from functools import wraps
from flask import abort
from flask_login import current_user
from .models import PapelUsuario

def gestor_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.papel != PapelUsuario.GESTOR:
            abort(403)  # Proibido o acesso
        return f(*args, **kwargs)
    return decorated_function
```

Este decorator `@gestor_required` poderá ser colocado acima de qualquer rota para protegê-la.

---

**Passo 2: Formulários para Gestão**

Vamos atualizar nosso arquivo `app/forms.py` para incluir os formulários de criação de Seção e Usuário.

**Adicione as seguintes classes ao arquivo** `/projeto-ferias/app/forms.py`:

```python
# ... (imports existentes) ...
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError
from .models import Usuario

# ... (LoginForm existente) ...

class SecaoForm(FlaskForm):
    """Formulário para criar ou editar uma Seção."""
    nome = StringField(
        'Nome da Seção', 
        validators=[DataRequired(), Length(min=3, max=100)]
    )
    submit = SubmitField('Salvar Seção')

class UsuarioCreateForm(FlaskForm):
    """Formulário para o Gestor criar um novo usuário."""
    nome_completo = StringField('Nome Completo', validators=[DataRequired()])
    nome_guerra = StringField('Nome de Guerra', validators=[DataRequired()])
    identidade = StringField('Identidade', validators=[DataRequired()])
    posto_grad = StringField('Posto/Graduação', validators=[DataRequired()])
    secao_id = SelectField('Seção', coerce=int, validators=[DataRequired()])
    papel = SelectField(
        'Papel', 
        choices=[(papel.name, papel.value) for papel in PapelUsuario],
        validators=[DataRequired()]
    )
    password = PasswordField(
        'Senha', 
        validators=[DataRequired(), Length(min=6)]
    )
    password2 = PasswordField(
        'Confirmar Senha', 
        validators=[DataRequired(), EqualTo('password', message='As senhas devem ser iguais.')]
    )
    submit = SubmitField('Cadastrar Militar')

    def validate_identidade(self, identidade):
        user = Usuario.query.filter_by(identidade=identidade.data).first()
        if user:
            raise ValidationError('Esta identidade já está em uso.')
```

---

