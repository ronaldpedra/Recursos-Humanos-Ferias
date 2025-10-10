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
    @app.route('/teste')
    def test_page():
        return '<h1>A configuração inicial está funcionando!</h1>'
    
    return app