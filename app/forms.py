"""
/Recursos-Humanos-Ferias/app/forms.py
"""
from flask import flash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, DateField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError, Optional
from .models import Usuario, PapelUsuario
from datetime import date

# ---Formulários de Acesso---

class LoginForm(FlaskForm):
    """Formulário de login."""
    identidade = StringField('Identidade', validators=[DataRequired(message="Por favor, insira sua identidade.")])
    password = PasswordField('Senha', validators=[DataRequired(message="Por favor, insira sua senha.")])
    remember_me = BooleanField('Lembrar-me')
    submit = SubmitField('Entrar')

# ---Formulários para Seções---

class SecaoForm(FlaskForm):
    """Formulário para criar ou editar uma Seção."""
    nome = StringField('Nome da Seção', validators=[DataRequired(), Length(min=3, max=100)])
    submit = SubmitField('Salvar Seção')

class SecaoEditForm(FlaskForm):
    nome = StringField('Nome da Seção', validators=[DataRequired(), Length(min=3, max=100)])
    chefe_id = SelectField('Chefe da Seção', coerce=int, validators=[Optional()])
    submit = SubmitField('Salvar Alterações')

# ---Formulários para Usuários---

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

# ---Formulários para Solicitação de Férias---

class SolicitacaoFeriasForm(FlaskForm):
    """Formulário para o militar solicitar férias"""
    tipo_solicitacao = SelectField(
        'Tipo de Período',
        choices=[
            ('', '--- Selecione o tipo ---'),
            ('30_DIAS', 'Período único de 30 dias'),
            ('15_DIAS', 'Período de 15 dias'),
            ('10_DIAS', 'Período de 10 dias'),
            ('DESCONTO', 'Desconto em Férias (dias avulsos)')
        ],
        validators=[DataRequired(message="Selecione o tipo de período.")]
    )
    data_inicio = DateField(
        'Data de Início',
        format='%Y-%m-%d',
        validators=[DataRequired(message="A data de início é obrigatória.")]
    )
    dias_solicitados = SelectField(
        'Dias a Descontar',
        choices=[(i, str(i)) for i in range(1, 31)],
        coerce=int,
        validators=[Optional()]
    )
    submit = SubmitField('Enviar Solicitações')

    def validate_data_inicio(self, data_inicio):
        if data_inicio.data < date.today():
            raise ValidationError("A data de início não pode ser no passado.")
