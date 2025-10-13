# /Recursos-Humanos-Ferias/app/routes/auth_routes.py

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
        return redirect(url_for('main.index'))

    form = LoginForm()
    if form.validate_on_submit():
        # Busca o usuário pela identidade no banco de dados
        user = Usuario.query.filter_by(identidade=form.identidade.data).first()

        # Verifica se o usuário existe e se a senha está correta
        if user is None or not user.check_password(form.password.data):
            flash('Identidade ou senha inválida', 'danger')
            return redirect(url_for('auth.login'))

        # Loga o usuário com o Flask-Login
        login_user(user, remember=form.remember_me.data)
        flash('Login realizado com sucesso!', 'success')

        # Redireciona para o dashboard apropriado
        return redirect(url_for('main.index'))

    return render_template('auth/login.html', title='Login', form=form)

@bp.route('/logout')
def logout():
    logout_user()
    flash('Você foi desconectado.', 'info')
    return redirect(url_for('auth.login'))
