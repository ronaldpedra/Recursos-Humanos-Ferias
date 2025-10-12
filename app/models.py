"""
/Recursos-Humanos-Ferias/app/models.py
"""
import enum
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db


class PapelUsuario(enum.Enum):
    MILITAR = 'Militar'
    CHEFE_SECAO = 'Chefe de Seção'
    GESTOR = 'Gestor de Pessoal'


class StatusFerias(enum.Enum):
    SOLICITADA = 'Solicitada'
    APROVADA_CHEFE = 'Aprovada pelo Chefe'
    APROVADA_GESTOR = 'Aprovada (Gestor)'
    REPROVADA = 'Reprovada'
    ALTERADA = 'Alterada'
    CANCELADA = 'Cancelada'


class Usuario(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    nome_completo = db.Column(db.String(150), nullable=False)
    nome_guerra = db.Column(db.String(50), nullable=False, unique=True)
    identidade = db.Column(db.String(20), unique=True, nullable=False)
    posto_grad = db.Column(db.String(50), nullable=False)  # Ex: 3º Sgt, Cap
    password_hash = db.Column(db.String(256), nullable=False)
    papel = db.Column(db.Enum(PapelUsuario), nullable=False, default=PapelUsuario.MILITAR)

    secao_id = db.Column(db.Integer, db.ForeignKey('secao.id'))
    secao = db.relationship('Secao', back_populates='integrantes', foreign_keys=[secao_id])

    periodos_aquisitivos = db.relationship('PeriodoAquisitivo', back_populates='usuario', lazy='dynamic')
    solicitacoes = db.relationship('SolicitacaoFerias', back_populates='solicitante', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Secao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), unique=True, nullable=False)
    chefe_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))

    chefe = db.relationship('Usuario', foreign_keys=[chefe_id])
    integrantes = db.relationship('Usuario', back_populates='secao', foreign_keys=[Usuario.secao_id])


class PeriodoAquisitivo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    ano_referencia = db.Column(db.Integer, nullable=False)  # Ex: 2025
    data_inicio_periodo = db.Column(db.Date, nullable=False)
    data_fim_periodo = db.Column(db.Date, nullable=False)
    dias_saldo = db.Column(db.Integer, nullable=False, default=30)

    usuario = db.relationship('Usuario', back_populates='periodos_aquisitivos')
    solicitacoes_vinculadas = db.relationship('SolicitacaoFerias', back_populates='periodo_aquisitivo')


class SolicitacaoFerias(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    solicitante_id = db.Column(
        db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    periodo_aquisitivo_id = db.Column(db.Integer, db.ForeignKey('periodo_aquisitivo.id'), nullable=False)

    data_inicio = db.Column(db.Date, nullable=False)
    data_fim = db.Column(db.Date, nullable=False)
    dias_solicitados = db.Column(db.Integer, nullable=False) # Ex: "30_DIAS", "15_DIAS", "10_DIAS", "DESCONTO"
    tipo_solicitacao = db.Column(db.String(50))
    status = db.Column(db.Enum(StatusFerias), nullable=False, default=StatusFerias.SOLICITADA)

    data_solicitacao = db.Column(db.DateTime, default=db.func.current_timestamp())
    justificativa_reprovacao = db.Column(db.Text)

    solicitante = db.relationship('Usuario', back_populates='solicitacoes')
    periodo_aquisitivo = db.relationship('PeriodoAquisitivo', back_populates='solicitacoes_vinculadas')
