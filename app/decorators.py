# ./Recursos-Humanos-Ferias/app/decorators.py

from functools import wraps
from flask import abort
from flask_login import current_user
from .models import PapelUsuario


def gestor_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.papel != PapelUsuario.GESTOR:
            abort(403) # Proibido acesso
        return f(*args, **kwargs)
    return decorated_function
