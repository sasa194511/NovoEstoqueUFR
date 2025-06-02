from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from src.models import db, Produto, Movimentacao
from src.controllers.produtos import admin_required
from datetime import datetime
from sqlalchemy import func, desc

movimentacoes_bp = Blueprint('movimentacoes', __name__, url_prefix='/movimentacoes')

@movimentacoes_bp.route('/')
@login_required
def listar():
    """Rota para listar movimentações com filtros"""
    # Parâmetros de filtro
    filtro_codigo = request.args.get('filtro_codigo', '').strip()
    filtro_tipo = request.args.get('filtro_tipo', '').strip()
    filtro_data_inicio = request.args.get('filtro_data_inicio', '').strip()
    filtro_data_fim = request.args.get('filtro_data_fim', '').strip()
    
    # Paginação
    page = request.args.get('page', 1, type=int)
    per_page = 20  # Número de itens por página
    
    # Construção da query com filtros
    query = Movimentacao.query
    
    if filtro_codigo:
        query = query.filter(Movimentacao.codigo_produto.ilike(f'%{filtro_codigo}%'))
    
    if filtro_tipo:
        query = query.filter(Movimentacao.tipo == filtro_tipo)
    
    if filtro_data_inicio:
        try:
            data_inicio = datetime.strptime(filtro_data_inicio, '%Y-%m-%d')
            query = query.filter(func.date(Movimentacao.data) >= data_inicio)
        except ValueError:
            flash('Formato de data inválido para Data Início.', 'warning')
    
    if filtro_data_fim:
        try:
            data_fim = datetime.strptime(filtro_data_fim, '%Y-%m-%d')
            query = query.filter(func.date(Movimentacao.data) <= data_fim)
        except ValueError:
            flash('Formato de data inválido para Data Fim.', 'warning')
    
    # Ordenação e paginação
    movimentacoes = query.order_by(desc(Movimentacao.data)).paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('movimentacoes.html', 
                          movimentacoes=movimentacoes.items, 
                          pagination=movimentacoes)

@movimentacoes_bp.route('/registrar', methods=['POST'])
@login_required
def registrar():
    """Rota para registrar uma nova movimentação"""
    codigo = request.form.get('codigo', '').strip()
    tipo = request.form.get('tipo', '').strip()
    quantidade = request.form.get('quantidade', '0').strip()
    observacao = request.form.get('observacao', '').strip()
    
    # Validações básicas
    if not codigo or not tipo:
        flash('Código e tipo são campos obrigatórios.', 'danger')
        return redirect(url_for('movimentacoes.listar'))
    
    if tipo not in ['Entrada', 'Saída']:
        flash('Tipo de movimentação inválido.', 'danger')
        return redirect(url_for('movimentacoes.listar'))
    
    # Validação de quantidade
    try:
        quantidade = int(quantidade)
        if quantidade <= 0:
            raise ValueError("Quantidade deve ser maior que zero")
    except ValueError:
        flash('Quantidade deve ser um número inteiro positivo.', 'danger')
        return redirect(url_for('movimentacoes.listar'))
    
    # Busca do produto
    produto = Produto.query.get(codigo)
    if not produto:
        flash(f'Produto com código "{codigo}" não encontrado.', 'danger')
        return redirect(url_for('movimentacoes.listar'))
    
    # Verificação de estoque para saídas
    if tipo == 'Saída' and quantidade > produto.quantidade:
        flash(f'Quantidade insuficiente em estoque. Disponível: {produto.quantidade}', 'danger')
        return redirect(url_for('movimentacoes.listar'))
    
    # Atualização do estoque
    try:
        if tipo == 'Entrada':
            produto.quantidade += quantidade
        else:  # Saída
            produto.quantidade -= quantidade
        
        # Registro da movimentação
        movimentacao = Movimentacao(
            codigo_produto=codigo,
            tipo=tipo,
            quantidade=quantidade,
            observacao=observacao if observacao else None
        )
        
        db.session.add(movimentacao)
        db.session.commit()
        
        flash(f'Movimentação de {tipo} registrada com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao registrar movimentação: {str(e)}', 'danger')
    
    return redirect(url_for('movimentacoes.listar'))
