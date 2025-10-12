"""
/projeto-ferias/app/__init__.py
"""
import click
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
# 'auth' é o nome do Blueprint que criaremos
login_manager.login_view = 'auth.login'


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
    from app.models import Usuario, PapelUsuario

    # Função para carregar o usuário da sessão
    @login_manager.user_loader
    def load_user(user_id):
        return Usuario.query.get(int(user_id))

    # --- Registro dos Blueprints (nossas rotas organizadas) ---
    from app.routes.auth_routes import bp as auth_bp
    app.register_blueprint(auth_bp)  # Nao precisa de prefixo para login

    # Vamos criar um Blueprint principal para a página inicial
    from flask import Blueprint
    from flask_login import login_required

    main_bp = Blueprint('main', __name__)

    @main_bp.route('/')
    @main_bp.route('/index')
    @login_required  # Protege essa rota, exigindo login
    def index():
        return '<h1>Bem-vindo ao Sistema de Gestão de Férias!</h1>'

    app.register_blueprint(main_bp)

    @app.cli.command("create-gestor")
    @click.argument("nome_guerra")
    @click.argument("identidade")
    @click.argument("password")
    def create_gestor(nome_guerra, identidade, password):
        """Cria um novo usuário com o papel de Gestor"""
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

    # Apenas uma rota de teste para garantir que tudo está funcionando

    @app.route('/teste')
    def test_page():
        return '<h1>A configuração inicial está funcionando!</h1>'

    return app
