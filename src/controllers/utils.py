from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from src.models import db, Produto
from sqlalchemy import func, or_, desc, Index, text
from sqlalchemy.exc import OperationalError
import time

utils_bp = Blueprint('utils', __name__, url_prefix='/utils')

@utils_bp.route('/otimizar_db')
@login_required
def otimizar_db():
    """Rota para otimizar o banco de dados (apenas para administradores)"""
    if not current_user.is_admin:
        flash('Acesso restrito a administradores.', 'danger')
        return redirect(url_for('index'))
    
    try:
        # Criar índices para campos frequentemente pesquisados
        criar_indices()
        
        # Executar VACUUM para otimizar o banco SQLite
        if 'sqlite' in db.engine.url.drivername:
            db.session.execute(text('VACUUM'))
        
        # Executar ANALYZE para atualizar estatísticas
        if 'sqlite' in db.engine.url.drivername:
            db.session.execute(text('ANALYZE'))
        
        db.session.commit()
        flash('Banco de dados otimizado com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao otimizar banco de dados: {str(e)}', 'danger')
    
    return redirect(url_for('index'))

def criar_indices():
    """Função para criar índices no banco de dados"""
    # Verificar se os índices já existem antes de criar
    indices_existentes = []
    
    try:
        # Obter lista de índices existentes
        if 'sqlite' in db.engine.url.drivername:
            result = db.session.execute(text("SELECT name FROM sqlite_master WHERE type='index'"))
            indices_existentes = [row[0] for row in result]
    except:
        pass
    
    # Criar índices se não existirem
    try:
        if 'idx_produtos_nome' not in indices_existentes:
            db.session.execute(text('CREATE INDEX idx_produtos_nome ON produtos (nome)'))
        
        if 'idx_produtos_categoria' not in indices_existentes:
            db.session.execute(text('CREATE INDEX idx_produtos_categoria ON produtos (categoria)'))
        
        if 'idx_movimentacoes_codigo_produto' not in indices_existentes:
            db.session.execute(text('CREATE INDEX idx_movimentacoes_codigo_produto ON movimentacoes (codigo_produto)'))
        
        if 'idx_movimentacoes_data' not in indices_existentes:
            db.session.execute(text('CREATE INDEX idx_movimentacoes_data ON movimentacoes (data)'))
        
        if 'idx_solicitacoes_usuario_id' not in indices_existentes:
            db.session.execute(text('CREATE INDEX idx_solicitacoes_usuario_id ON solicitacoes (usuario_id)'))
        
        if 'idx_solicitacoes_status' not in indices_existentes:
            db.session.execute(text('CREATE INDEX idx_solicitacoes_status ON solicitacoes (status)'))
        
        db.session.commit()
    except OperationalError:
        # Alguns índices podem já existir ou não ser suportados
        db.session.rollback()

@utils_bp.route('/busca_avancada')
@login_required
def busca_avancada():
    """API para busca avançada de produtos com otimização para grandes volumes"""
    termo = request.args.get('termo', '').strip()
    categoria = request.args.get('categoria', '').strip()
    min_qtd = request.args.get('min_qtd', '').strip()
    max_qtd = request.args.get('max_qtd', '').strip()
    
    # Iniciar a query base
    query = Produto.query
    
    # Aplicar filtros
    if termo:
        # Otimização: usar LIKE com % apenas no final para aproveitar índices
        if termo.startswith('%') or termo.endswith('%'):
            # Busca com LIKE padrão
            query = query.filter(or_(
                Produto.codigo.ilike(f'%{termo}%'),
                Produto.nome.ilike(f'%{termo}%')
            ))
        else:
            # Busca otimizada para índices
            query = query.filter(or_(
                Produto.codigo.ilike(f'{termo}%'),
                Produto.nome.ilike(f'{termo}%')
            ))
    
    if categoria:
        query = query.filter(Produto.categoria == categoria)
    
    if min_qtd:
        try:
            min_qtd = int(min_qtd)
            query = query.filter(Produto.quantidade >= min_qtd)
        except ValueError:
            pass
    
    if max_qtd:
        try:
            max_qtd = int(max_qtd)
            query = query.filter(Produto.quantidade <= max_qtd)
        except ValueError:
            pass
    
    # Limitar resultados para performance
    produtos = query.order_by(Produto.nome).limit(100).all()
    
    # Formatar resultados
    resultados = []
    for p in produtos:
        resultados.append({
            'codigo': p.codigo,
            'nome': p.nome,
            'quantidade': p.quantidade,
            'categoria': p.categoria or 'Sem categoria'
        })
    
    return jsonify(resultados)

@utils_bp.route('/estatisticas')
@login_required
def estatisticas():
    """API para obter estatísticas do sistema"""
    if not current_user.is_admin:
        return jsonify({'error': 'Acesso não autorizado'}), 403
    
    try:
        # Medir tempo de execução
        inicio = time.time()
        
        # Total de produtos
        total_produtos = db.session.query(func.count(Produto.codigo)).scalar()
        
        # Total de itens em estoque
        total_itens = db.session.query(func.sum(Produto.quantidade)).scalar() or 0
        
        # Produtos com estoque baixo (menos de 5 unidades)
        estoque_baixo = db.session.query(func.count(Produto.codigo))\
            .filter(Produto.quantidade > 0, Produto.quantidade < 5).scalar()
        
        # Produtos sem estoque
        sem_estoque = db.session.query(func.count(Produto.codigo))\
            .filter(Produto.quantidade == 0).scalar()
        
        # Categorias mais comuns
        categorias = db.session.query(
            Produto.categoria, 
            func.count(Produto.codigo).label('total')
        ).group_by(Produto.categoria).order_by(desc('total')).limit(5).all()
        
        # Tempo de execução
        tempo_execucao = time.time() - inicio
        
        return jsonify({
            'total_produtos': total_produtos,
            'total_itens': total_itens,
            'estoque_baixo': estoque_baixo,
            'sem_estoque': sem_estoque,
            'categorias': [{'nome': c[0] or 'Sem categoria', 'total': c[1]} for c in categorias],
            'tempo_execucao': round(tempo_execucao, 3)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
