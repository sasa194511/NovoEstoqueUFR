from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from src.models import db, Produto, Solicitacao, Usuario
from src.controllers.produtos import admin_required
from datetime import datetime
from sqlalchemy import desc

solicitacoes_bp = Blueprint('solicitacoes', __name__, url_prefix='/solicitacoes')

@solicitacoes_bp.route('/minhas')
@login_required
def minhas():
    """Rota para listar solicitações do usuário atual"""
    # Paginação
    page = request.args.get('page', 1, type=int)
    per_page = 10  # Número de itens por página
    
    # Busca com paginação
    solicitacoes = Solicitacao.query.filter_by(usuario_id=current_user.id)\
        .order_by(desc(Solicitacao.data))\
        .paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('solicitacoes.html', 
                          solicitacoes=solicitacoes.items, 
                          pagination=solicitacoes)

@solicitacoes_bp.route('/criar', methods=['POST'])
@login_required
def criar():
    """Rota para criar uma nova solicitação"""
    codigo_produto = request.form.get('codigo_produto', '').strip()
    quantidade = request.form.get('quantidade', '0').strip()
    descricao = request.form.get('descricao', '').strip()
    
    # Validações básicas
    if not codigo_produto or not descricao:
        flash('Todos os campos são obrigatórios.', 'danger')
        return redirect(url_for('index'))
    
    # Validação de quantidade
    try:
        quantidade = int(quantidade)
        if quantidade <= 0:
            raise ValueError("Quantidade deve ser maior que zero")
    except ValueError:
        flash('Quantidade deve ser um número inteiro positivo.', 'danger')
        return redirect(url_for('index'))
    
    # Busca do produto
    produto = Produto.query.get(codigo_produto)
    if not produto:
        flash(f'Produto com código "{codigo_produto}" não encontrado.', 'danger')
        return redirect(url_for('index'))
    
    # Criação da solicitação
    try:
        solicitacao = Solicitacao(
            usuario_id=current_user.id,
            codigo_produto=codigo_produto,
            quantidade_solicitada=quantidade,
            descricao=descricao
        )
        
        db.session.add(solicitacao)
        db.session.commit()
        
        flash('Solicitação enviada com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao enviar solicitação: {str(e)}', 'danger')
    
    return redirect(url_for('solicitacoes.minhas'))

@solicitacoes_bp.route('/gerenciar', methods=['GET', 'POST'])
@admin_required
def gerenciar():
    """Rota para gerenciar solicitações (aprovar/recusar)"""
    if request.method == 'POST':
        solicitacao_id = request.form.get('solicitacao_id')
        acao = request.form.get('acao')
        
        if not solicitacao_id or not acao or acao not in ['aprovar', 'recusar']:
            flash('Parâmetros inválidos.', 'danger')
            return redirect(url_for('solicitacoes.gerenciar'))
        
        # Busca da solicitação
        solicitacao = Solicitacao.query.filter_by(id=solicitacao_id, status='Pendente').first()
        if not solicitacao:
            flash('Solicitação não encontrada ou já processada.', 'danger')
            return redirect(url_for('solicitacoes.gerenciar'))
        
        if acao == 'aprovar':
            # Verificação de estoque
            produto = Produto.query.get(solicitacao.codigo_produto)
            if not produto:
                flash('Produto não encontrado.', 'danger')
                return redirect(url_for('solicitacoes.gerenciar'))
            
            if solicitacao.quantidade_solicitada > produto.quantidade:
                flash(f'Quantidade insuficiente em estoque para {produto.nome}.', 'warning')
                return redirect(url_for('solicitacoes.gerenciar'))
            
            try:
                # Atualização do estoque
                produto.quantidade -= solicitacao.quantidade_solicitada
                
                # Atualização do status da solicitação
                solicitacao.status = 'Aprovada'
                
                # Registro da movimentação
                from src.models import Movimentacao
                movimentacao = Movimentacao(
                    codigo_produto=solicitacao.codigo_produto,
                    tipo='Saída',
                    quantidade=solicitacao.quantidade_solicitada,
                    observacao=f'Solicitação #{solicitacao.id} aprovada'
                )
                
                db.session.add(movimentacao)
                db.session.commit()
                
                flash(f'Solicitação #{solicitacao.id} aprovada com sucesso!', 'success')
            except Exception as e:
                db.session.rollback()
                flash(f'Erro ao aprovar solicitação: {str(e)}', 'danger')
        
        elif acao == 'recusar':
            try:
                solicitacao.status = 'Recusada'
                db.session.commit()
                
                flash(f'Solicitação #{solicitacao.id} recusada.', 'success')
            except Exception as e:
                db.session.rollback()
                flash(f'Erro ao recusar solicitação: {str(e)}', 'danger')
        
        return redirect(url_for('solicitacoes.gerenciar'))
    
    # GET: Listar solicitações
    # Solicitações pendentes
    solicitacoes_pendentes = db.session.query(
        Solicitacao, Usuario.username
    ).join(
        Usuario, Solicitacao.usuario_id == Usuario.id
    ).filter(
        Solicitacao.status == 'Pendente'
    ).order_by(
        desc(Solicitacao.data)
    ).all()
    
    # Histórico de solicitações (não pendentes)
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    solicitacoes_historico = db.session.query(
        Solicitacao, Usuario.username
    ).join(
        Usuario, Solicitacao.usuario_id == Usuario.id
    ).filter(
        Solicitacao.status != 'Pendente'
    ).order_by(
        desc(Solicitacao.data)
    ).paginate(page=page, per_page=per_page, error_out=False)
    
    # Preparar dados para o template
    pendentes = []
    for sol, username in solicitacoes_pendentes:
        item = {
            'id': sol.id,
            'username': username,
            'codigo_produto': sol.codigo_produto,
            'nome_produto': Produto.query.get(sol.codigo_produto).nome if Produto.query.get(sol.codigo_produto) else 'Produto não encontrado',
            'quantidade_solicitada': sol.quantidade_solicitada,
            'data': sol.data.strftime('%d/%m/%Y %H:%M'),
            'descricao': sol.descricao,
            'status': sol.status
        }
        pendentes.append(item)
    
    historico = []
    for sol, username in solicitacoes_historico.items:
        item = {
            'id': sol.id,
            'username': username,
            'codigo_produto': sol.codigo_produto,
            'nome_produto': Produto.query.get(sol.codigo_produto).nome if Produto.query.get(sol.codigo_produto) else 'Produto não encontrado',
            'quantidade_solicitada': sol.quantidade_solicitada,
            'data': sol.data.strftime('%d/%m/%Y %H:%M'),
            'descricao': sol.descricao,
            'status': sol.status
        }
        historico.append(item)
    
    return render_template('gerenciar.html', 
                          solicitacoes_pendentes=pendentes, 
                          solicitacoes_historico=historico,
                          pagination=solicitacoes_historico)
