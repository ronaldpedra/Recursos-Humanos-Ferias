# /Recursos-Humanos-Ferias/app/routes/gestor_routes.py

from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import Usuario, Secao, PapelUsuario
from app.forms import SecaoForm, UsuarioCreateForm
from app.decorators import gestor_required


bp = Blueprint('gestor', __name__)

@bp.route('/dashboard')
@login_required
@gestor_required
def dashboard():
    return render_template('gestor/dashboard.html', title='Dashboard do Gestor')

@bp.route('/secoes', methods=['GET', 'POST'])
@login_required
@gestor_required
def gerenciar_secoes():
    form = SecaoForm()
    if form.validate_on_submit():
        nova_secao = Secao(nome=form.nome.data)
        db.session.add(nova_secao)
        db.session.commit()
        flash('Seção criada com sucesso!', 'success')
        return redirect(url_for('gestor.gerenciar_secoes'))
    
    secoes = Secao.query.order_by(Secao.nome).all()
    return render_template('gestor/secoes.html', title='Gerenciar Seções', form=form, secoes=secoes)

@bp.route('/usuarios', methods=['GET', 'POST'])
@login_required
@gestor_required
def gerenciar_usuarios():
    form = UsuarioCreateForm()
    # Popula o campo de seleção de seções com as seções do banco
    form.secao_id.choices = [(s.id, s.nome) for s in Secao.query.order_by('nome').all()]

    if form.validate_on_submit():
        user = Usuario(
            nome_completo=form.nome_completo.data,
            nome_guerra=form.nome_guerra.data,
            identidade=form.identidade.data,
            posto_grad=form.posto_grad.data,
            secao_id=form.secao_id.data,
            papel=PapelUsuario[form.papel.data]
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Militar cadastrado com sucesso!', 'success')
        return render_template(url_for('gestor.gerenciar_usuarios'))
    
    usuarios = Usuario.query.order_by(Usuario.nome_completo).all()
    return render_template('gestor/usuarios.html', title='Gerenciar Militares', form=form, usuarios=usuarios)
