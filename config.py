"""
/projeto-ferias/congig.py
"""
import os
from dotenv import load_dotenv


# Encontra o caminho absoluto para o diretório raiz do projeto
basedir = os.path.abspath(os.path.dirname(__file__))

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv(os.path.join(basedir, '.env'))


class Config:
    """Configurações base da aplicação."""
    # Chave secreta para proteger sessões e cookies.
    SECRET_KEY = os.environ.get('SECRET_KEY')

    # Configuração do SQLAlchemy
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
