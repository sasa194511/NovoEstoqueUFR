from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from src.models import db, Produto
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func
import re

produtos_bp = Blueprint('produtos', __name__, url_prefix='/produtos')

def admin_required(f):
    """Decorator para verificar se o usuário é administrador"""
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            flash('Acesso restrito a administradores.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@produtos_bp.route('/')
@login_required
def index():
    """Rota principal que lista os produtos"""
    # Otimizado para lidar com grandes volumes de dados
    page = request.args.get('page', 1, type=int)
    per_page = 20  # Número de itens por página
    
    # Busca com paginação
    produtos = Produto.query.order_by(Produto.nome).paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('index.html', produtos=produtos.items, pagination=produtos)


@produtos_bp.route('/listar')
@login_required
def listar():
    """Rota para listar produtos com opções de gerenciamento e busca"""
    # Obtém o termo de busca e a página da query string
    search_query = request.args.get('search', '', type=str)
    page = request.args.get('page', 1, type=int)
    per_page = 20  # Reduzido para evitar sobrecarga na tela

    # Consulta com filtro de busca (se houver) e paginação
    query = Produto.query
    if search_query:
        query = query.filter(Produto.nome.ilike(f'%{search_query}%'))  # Busca parcial no nome

    # Ordena e pagina os resultados
    produtos = query.order_by(Produto.nome).paginate(page=page, per_page=per_page, error_out=False)

    return render_template('produtos.html', produtos=produtos.items, pagination=produtos, search_query=search_query)
@produtos_bp.route('/cadastrar', methods=['POST'])
@admin_required
def cadastrar():
    """Rota para cadastrar um novo produto"""
    codigo = request.form.get('codigo', '').strip()
    nome = request.form.get('nome', '').strip()
    quantidade = request.form.get('quantidade', '0').strip()
    categoria = request.form.get('categoria', '').strip()
    descricao = request.form.get('descricao', '').strip()
    
    # Validações básicas
    if not codigo or not nome:
        flash('Código e nome são campos obrigatórios.', 'danger')
        return redirect(url_for('produtos.listar'))
    
    # Validação de quantidade
    try:
        quantidade = int(quantidade)
        if quantidade < 0:
            raise ValueError("Quantidade não pode ser negativa")
    except ValueError:
        flash('Quantidade deve ser um número inteiro não negativo.', 'danger')
        return redirect(url_for('produtos.listar'))
    
    # Validação de código (apenas letras, números e traços)
    if not re.match(r'^[A-Za-z0-9\-]+$', codigo):
        flash('Código deve conter apenas letras, números e traços.', 'danger')
        return redirect(url_for('produtos.listar'))
    
    # Criação do produto
    novo_produto = Produto(
        codigo=codigo,
        nome=nome,
        quantidade=quantidade,
        categoria=categoria if categoria else None,
        descricao=descricao if descricao else None
    )
    
    try:
        db.session.add(novo_produto)
        db.session.commit()
        flash(f'Produto "{nome}" cadastrado com sucesso!', 'success')
    except IntegrityError:
        db.session.rollback()
        flash(f'Erro: Código "{codigo}" já existe.', 'danger')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao cadastrar produto: {str(e)}', 'danger')
    
    return redirect(url_for('produtos.listar'))

@produtos_bp.route('/atualizar', methods=['POST'])
@admin_required
def atualizar():
    """Rota para atualizar um produto existente"""
    codigo = request.form.get('codigo', '').strip()
    nome = request.form.get('nome', '').strip()
    quantidade = request.form.get('quantidade', '0').strip()
    categoria = request.form.get('categoria', '').strip()
    descricao = request.form.get('descricao', '').strip()
    
    # Validações básicas
    if not codigo or not nome:
        flash('Código e nome são campos obrigatórios.', 'danger')
        return redirect(url_for('produtos.listar'))
    
    # Validação de quantidade
    try:
        quantidade = int(quantidade)
        if quantidade < 0:
            raise ValueError("Quantidade não pode ser negativa")
    except ValueError:
        flash('Quantidade deve ser um número inteiro não negativo.', 'danger')
        return redirect(url_for('produtos.listar'))
    
    # Busca do produto
    produto = Produto.query.get(codigo)
    if not produto:
        flash(f'Produto com código "{codigo}" não encontrado.', 'danger')
        return redirect(url_for('produtos.listar'))
    
    # Atualização do produto
    try:
        produto.nome = nome
        produto.quantidade = quantidade
        produto.categoria = categoria if categoria else None
        produto.descricao = descricao if descricao else None
        
        db.session.commit()
        flash(f'Produto "{nome}" atualizado com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao atualizar produto: {str(e)}', 'danger')
    
    return redirect(url_for('produtos.listar'))

@produtos_bp.route('/excluir/<codigo>')
@admin_required
def excluir(codigo):
    """Rota para excluir um produto"""
    produto = Produto.query.get(codigo)
    if not produto:
        flash(f'Produto com código "{codigo}" não encontrado.', 'danger')
        return redirect(url_for('produtos.listar'))
    
    try:
        nome = produto.nome
        db.session.delete(produto)
        db.session.commit()
        flash(f'Produto "{nome}" excluído com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao excluir produto: {str(e)}', 'danger')
    
    return redirect(url_for('produtos.listar'))

@produtos_bp.route('/buscar')
@login_required
def buscar():
    """Rota para buscar produtos (API JSON)"""
    termo = request.args.get('termo', '').strip()
    if not termo:
        return {'produtos': []}
    
    # Busca otimizada com LIKE e limitada a 10 resultados
    produtos = Produto.query.filter(
        (func.lower(Produto.codigo).contains(termo.lower())) | 
        (func.lower(Produto.nome).contains(termo.lower()))
    ).limit(10).all()
    
    return {
        'produtos': [
            {
                'codigo': p.codigo,
                'nome': p.nome,
                'quantidade': p.quantidade,
                'categoria': p.categoria
            } for p in produtos
        ]
    }
