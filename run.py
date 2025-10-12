"""
/projeto-ferias/run.py
"""

from app import create_app, db
from app.models import Usuario, Secao, PeriodoAquisitivo, SolicitacaoFerias

# Cria instância da aplicação usando a nossa fábrica
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
