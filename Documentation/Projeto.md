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
|   |-- __init__.py         # Inicializa a aplicação Flask e extensões
|   |-- models.py           # Definição dos modelos do SQLAlchemy
|   |-- routes/             # (Opcional, mas bom para organizar)
|   |   |-- auth_routes.py
|   |   |-- militar_routes.py
|   |   |-- chefe_routes.py
|   |   `-- gestor_routes.py
|   |-- static/
|   |   |-- css/
|   |   `-- js/
|   `-- templates/
|       |-- base.html
|       |-- login.html
|       |-- ... (outros templates)
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
Flask==2.3.3
SQLAlchemy==2.0.21
Flask-SQLAlchemy==3.1.1
Flask-Migrate==4.0.5
python-dotenv==1.0.0
Flask-Login==0.6.2
Werkzeug==2.3.7  # Para hash de senhas
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
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
import enum

db = SQLAlchemy()

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
    secao = db.relationship('Secao', back_populates='integrantes')

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