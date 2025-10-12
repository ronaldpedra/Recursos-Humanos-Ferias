"""
/projeto-ferias/run.py
"""

import click
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

@app.cli.command('create-gestor')
@click.argument('nome_guerra')
@click.argument('identidade')
@click.argument('password')
def create_gestor(nome_guerra, identidade, password):
    """Cria um novo usuário com o papel de Gestor"""
    if Usuario.query.filter_by(identidade=identidade).first():
        print(f'Erro: Usuário com identidade {identidade} já existe.')
        return
    
    gestor = Usuario(
        nome_completo = f'{nome_guerra} (Gestor)',
        nome_guerra = nome_guerra,
        identidade = identidade,
        posto_grad = 'Admin'
        papel = PapelUsuario.GESTOR
    )
    gestor.set_password(password)
    db.session.add(gestor)
    db.session.commit()
    print(f"Usuário Gestor '{nome_guerra}' criado com sucesso!")

if __name__ == '__main__':
    app.run(debug=True)
