"""/Recursos-Humanos-Ferias/app/routes/militar_routes.py"""

from datetime import timedelta, date
from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import PeriodoAquisitivo, SolicitacaoFerias, StatusFerias
from app.forms import SolicitacaoFeriasForm
from app import db


bp = Blueprint('militar', __name__)

@bp.route('/dashboard')
@login_required
def dashboard():
    periodos = PeriodoAquisitivo.query.filter_by(usuario_id=current_user.id).order_by(PeriodoAquisitivo.ano_referencia.asc()).all()
    solicitacoes = SolicitacaoFerias.query.filter_by(solicitante_id=current_user.id).order_by(SolicitacaoFerias.data_solicitacao.desc()).all()

    saldo_total = sum(p.dias_saldo for p in periodos)

    return render_template(
        'militar/dashboard.html',
        title='Meu Dashboard',
        periodos=periodos,
        solicitacoes=solicitacoes,
        saldo_total=saldo_total
    )

@bp.route('/solicitar', methods=['GET', 'POST'])
@login_required
def solicitar_ferias():
    form = SolicitacaoFeriasForm()

    if form.validate_on_submit():
        tipo = form.tipo_solicitacao.data
        dias_a_solicitar = 0
        if tipo == '30_DIAS': dias_a_solicitar = 30
        elif tipo == '15_DIAS': dias_a_solicitar = 15
        elif tipo == '10_DIAS': dias_a_solicitar = 10
        elif tipo == 'DESCONTO': dias_a_solicitar = form.dias_solicitados.data

        data_inicio_req = form.data_inicio.data
        data_fim_req = data_inicio_req + timedelta(days=dias_a_solicitar - 1)

        # 1. Encontrar o período aquisitivo mais antigo com saldo disponível
        periodo_alvo = PeriodoAquisitivo.query.filter(
            PeriodoAquisitivo.usuario_id == current_user.id,
            PeriodoAquisitivo.dias_saldo > 0,
            PeriodoAquisitivo.data_fim_periodo <= date.today() # Garante que o direito já foi adquirido
        ).order_by(PeriodoAquisitivo.ano_referencia.asc()).first()

        # 2. Valida se há um período e se o saldo é suficiente
        if not periodo_alvo:
            flash('Você não possui saldo de férias disponível ou nenhum período foi adquirido ainda.', 'danger')
            return redirect(url_for('militar.solicitar_ferias'))
        
        if periodo_alvo.dias_saldo < dias_a_solicitar:
            flash(f'Saldo insuficiente no período mais antigo ({periodo_alvo.ano_referencia}). Saldo: {periodo_alvo.dias_saldo} dias.', 'danger')
            return redirect(url_for('militar.solicitar_ferias'))
        
        # 3. Criar a solicitação e atualizar o saldo
        try:
            nova_solicitacao = SolicitacaoFerias(
                solicitante_id=current_user.id,
                periodo_aquisitivo_id=periodo_alvo.id,
                data_inicio=data_inicio_req,
                data_fim=data_fim_req,
                dias_solicitados=dias_a_solicitar,
                tipo_solicitacao=tipo,
                status=StatusFerias.SOLICITADA
            )

            # 4. Debitar o saldo do período
            periodo_alvo.dias_saldo -= dias_a_solicitar

            db.session.add(nova_solicitacao)
            db.session.commit()
            flash('Sua solicitação de férias foi enviada com sucesso!', 'success')
            return redirect(url_for('militar.dashboard'))
        
        except Exception as e:
            db.session.rollback()
            flash(f'Ocorreu um erro ao processar sua solicitação: {e}', 'danger')

    return render_template('militar/solicitar_ferias.html', title='Solicitar Férias', form=form)
