"""
/Recursos-Humanos-Ferias
"""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length


class LoginForm(FlaskForm):
    """Formulário de login."""
    identidade = StringField(
        'Identidade',
        validators=[DataRequired(message="Por favor, insira sua identidade.")]
    )
    password = PasswordField(
        'Senha',
        validators=[DataRequired(message="Por favor, insira sua senha.")]
    )
    remember_me = BooleanField('Lembrar-me')
    submit = SubmitField('Entrar')
