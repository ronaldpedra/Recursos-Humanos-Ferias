"""
/projeto-ferias/app/__init__.py
"""
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
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # Importa os modelos para que o Flask-Migrate os reconheça
    from app.models import Usuario

    # Função para carregar o usuário da sessão
    @login_manager.user_loader
    def load_user(user_id):
        return Usuario.query.get(int(user_id))

    # --- Registro dos Blueprints (nossas rotas organizadas) ---
    from app.routes.auth_routes import bp as auth_bp
    app.register_blueprint(auth_bp) # Nao precisa de prefixo para login

    # Vamos criar um Blueprint principal para a página inicial
    from flask import Blueprint, render_template
    from flask_login import login_required

    main_bp = Blueprint('main', __name__)

    @main_bp.route('/')
    @main_bp.route('/index')
    @login_required # Protege essa rota, exigindo login
    def index():
        return '<h1>Bem-vindo ao Sistema de Gestão de Férias!</h1>'
    
    app.register_blueprint(main_bp)


    # Apenas uma rota de teste para garantir que tudo está funcionando
    @app.route('/teste')
    def test_page():
        return '<h1>A configuração inicial está funcionando!</h1>'

    return app
