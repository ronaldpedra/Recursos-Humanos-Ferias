"""
/Recursos-Humanos-Ferias/app/forms.py
"""
from flask import flash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError, Optional
from .models import Usuario, PapelUsuario


class LoginForm(FlaskForm):
    """Formulário de login."""
    identidade = StringField('Identidade', validators=[DataRequired(message="Por favor, insira sua identidade.")])
    password = PasswordField('Senha', validators=[DataRequired(message="Por favor, insira sua senha.")])
    remember_me = BooleanField('Lembrar-me')
    submit = SubmitField('Entrar')

class SecaoForm(FlaskForm):
    """Formulário para criar ou editar uma Seção."""
    nome = StringField('Nome da Seção', validators=[DataRequired(), Length(min=3, max=100)])
    # chefe_id = SelectField('Chefe da Seção', coerce=int, validators=[Optional()])
    submit = SubmitField('Salvar Seção')

class SecaoEditForm(FlaskForm):
    nome = StringField('Nome da Seção', validators=[DataRequired(), Length(min=3, max=100)])
    chefe_id = SelectField('Chefe da Seção', coerce=int, validators=[Optional()])
    submit = SubmitField('Salvar Alterações')

class UsuarioCreateForm(FlaskForm):
    """Formulário para o Gestor criar um novo usuário."""
    nome_completo = StringField('Nome Completo', validators=[DataRequired()])
    nome_guerra = StringField('Nome de Guerra', validators=[DataRequired()])
    identidade = StringField('Identidade', validators=[DataRequired()])
    posto_grad = StringField('Posto/Graduação', validators=[DataRequired()])
    secao_id = SelectField('Seção', coerce=int, validators=[Optional()])
    papel = SelectField('Papel', choices=[(papel.name, papel.value) for papel in PapelUsuario], validators=[DataRequired()])
    password = PasswordField('Senha', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('Confirmar Senha', validators=[DataRequired(), EqualTo('password', message='As senhas devem ser iguais.')])
    submit = SubmitField('Cadastrar Militar')

    def validate_identidade(self, identidade):
        user = Usuario.query.filter_by(identidade=identidade.data).first()
        if user:
            flash('A identidade informada já está cadastrada. Este Militar não foi registrado.', 'danger')
            raise ValidationError('Esta identidade já está em uso.')

class UsuarioEditForm(FlaskForm):
    nome_completo = StringField('Nome Completo', validators=[DataRequired()])
    nome_guerra = StringField('Nome de Guerra', validators=[DataRequired()])
    identidade = StringField('Identidade', validators=[DataRequired()])
    posto_grad = StringField('Posto/Graduação', validators=[DataRequired()])
    secao_id = SelectField('Seção', coerce=int, validators=[Optional()])
    papel = SelectField('Papel', choices=[(papel.name, papel.value) for papel in PapelUsuario], validators=[DataRequired()])
    submit = SubmitField('Salvar Alterações')

    def __init__(self, original_identidade, *args, **kwargs):
        super(UsuarioEditForm, self).__init__(*args, **kwargs)
        self.original_identidade = original_identidade

    def validate_identidade(self, identidade):
        if identidade.data != self.original_identidade:
            user = Usuario.query.filter_by(identidade=identidade.data).first()
            if user:
                flash('A identidade que está tentando atualizar já existe na base de dados.', 'danger')
                raise ValidationError('Esta identidade já está em uso.')
