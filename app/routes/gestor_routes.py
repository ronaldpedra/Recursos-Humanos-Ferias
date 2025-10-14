# /Recursos-Humanos-Ferias/app/routes/gestor_routes.py

from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required
from app import db
from app.models import Usuario, Secao, PapelUsuario
from app.forms import SecaoForm, SecaoEditForm, UsuarioCreateForm, UsuarioEditForm
from app.decorators import gestor_required

bp = Blueprint('gestor', __name__)

@bp.route('/dashboard')
@login_required
@gestor_required
def dashboard():
    return render_template('gestor/dashboard.html', title='Dashboard do Gestor')

# --- GERENCIAMENTO DE SEÇÕES ---

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

@bp.route('/secao/<int:id>/editar', methods=['GET', 'POST'])
@login_required
@gestor_required
def editar_secao(id):
    secao = Secao.query.get_or_404(id)
    form = SecaoEditForm(obj=secao)
    form.chefe_id.choices = [(0, 'Nenhum')] + [(u.id, f"{u.posto_grad} {u.nome_guerra}") for u in Usuario.query.order_by('nome_guerra').all()]

    if form.validate_on_submit():
        secao.nome = form.nome.data
        secao.chefe_id = form.chefe_id.data if form.chefe_id.data != 0 else None
        db.session.commit()
        flash('Seção atualizada com sucesso!', 'success')
        return redirect(url_for('gestor.gerenciar_secoes'))

    return render_template('gestor/editar_secao.html', title='Editar Seção', form=form, secao=secao)

# --- GERENCIAMENTO DE USUÁRIOS ---

@bp.route('/usuarios', methods=['GET', 'POST'])
@login_required
@gestor_required
def gerenciar_usuarios():
    form = UsuarioCreateForm()
    form.secao_id.choices = [(0, 'Nenhuma')] + [(s.id, s.nome) for s in Secao.query.order_by('nome').all()]

    if form.validate_on_submit():
        user = Usuario(
            nome_completo=form.nome_completo.data,
            nome_guerra=form.nome_guerra.data,
            identidade=form.identidade.data,
            posto_grad=form.posto_grad.data,
            secao_id=form.secao_id.data if form.secao_id.data != 0 else None,
            papel=PapelUsuario[form.papel.data]
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Militar cadastrado com sucesso!', 'success')
        return redirect(url_for('gestor.gerenciar_usuarios'))

    usuarios = Usuario.query.order_by(Usuario.nome_completo).all()
    return render_template('gestor/usuarios.html', title='Gerenciar Militares', form=form, usuarios=usuarios)

@bp.route('/usuario/<int:id>/editar', methods=['GET', 'POST'])
@login_required
@gestor_required
def editar_usuario(id):
    user = Usuario.query.get_or_404(id)
    form = UsuarioEditForm(original_identidade=user.identidate, obj=user)
    form.secao_id.choices = [(0, 'Nenhuma')] + [(s.id, s.nome) for s in Secao.query.order_by('nome').all()]

    if form.validate_on_submit():
        user.nome_completo = form.nome_completo.data
        user.nome_guerra = form.nome_guerra.data
        user.identidade = form.identidade.data
        user.posto_grad = form.posto_grad.data
        user.secao_id = form.secao_id.data if form.secao_id.data != 0 else None
        user.papel = PapelUsuario[form.papel.data]
        db.session.commit()
        flash('Dados do militar atualizados com sucesso!', 'success')
        return redirect(url_for('gestor.gerenciar_usuarios'))
    
    form.papel.data = user.papel.name
    form.secao_id.data = user.secao_id if user.secao_id else 0

    return render_template('gestor/editar_usuario.html', title='Editar Militar', form=form, usuario=user)
