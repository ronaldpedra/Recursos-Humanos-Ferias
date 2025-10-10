# ./app/__init__.py

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
# ele será redirecionado para a rota.
login_manager.login_view = 'auth.login' # 'auth' é o nome do Blueprint que criaremos

def create_app(config_class=Config):
    """
    Fábrica que cria e configura a instância da aplicação Flask.
    """
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Inicializa as extensões com a app
    db.init_app(app)
    migrate.init_app(app)
    login_manager.init_app(app)