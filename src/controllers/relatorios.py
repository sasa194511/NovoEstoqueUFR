from flask import Blueprint, render_template, send_file, flash, request
from flask_login import login_required, current_user
from src.models import db, Produto, Movimentacao
from src.controllers.produtos import admin_required
import csv
from io import StringIO
from datetime import datetime

relatorios_bp = Blueprint('relatorios', __name__, url_prefix='/relatorios')

@relatorios_bp.route('/exportar')
@login_required
@admin_required
def exportar():
    """Rota para exportar dados do estoque para CSV"""
    tipo = request.args.get('tipo', 'produtos')
    
    if tipo == 'produtos':
        return exportar_produtos()
    elif tipo == 'movimentacoes':
        return exportar_movimentacoes()
    else:
        flash('Tipo de relatório inválido.', 'danger')
        return render_template('exportar.html')

def exportar_produtos():
    """Função para exportar produtos para CSV"""
    try:
        # Busca otimizada de produtos
        produtos = Produto.query.order_by(Produto.codigo).all()
        
        # Criação do arquivo CSV
        si = StringIO()
        writer = csv.writer(si)
        writer.writerow(['Código', 'Nome', 'Categoria', 'Quantidade', 'Descrição'])
        
        for produto in produtos:
            writer.writerow([
                produto.codigo,
                produto.nome,
                produto.categoria or '',
                produto.quantidade,
                produto.descricao or ''
            ])
        
        output = si.getvalue()
        si.close()
        
        # Nome do arquivo com timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'produtos_{timestamp}.csv'
        
        # Envio do arquivo
        return send_file(
            StringIO(output),
            mimetype='text/csv',
            as_attachment=True,
            download_name=filename
        )
    
    except Exception as e:
        flash(f'Erro ao exportar produtos: {str(e)}', 'danger')
        return render_template('exportar.html')

def exportar_movimentacoes():
    """Função para exportar movimentações para CSV"""
    try:
        # Parâmetros de filtro
        data_inicio = request.args.get('data_inicio', '').strip()
        data_fim = request.args.get('data_fim', '').strip()
        
        # Construção da query com filtros
        query = db.session.query(
            Movimentacao, Produto.nome
        ).join(
            Produto, Movimentacao.codigo_produto == Produto.codigo
        )
        
        if data_inicio:
            try:
                data_inicio_dt = datetime.strptime(data_inicio, '%Y-%m-%d')
                query = query.filter(Movimentacao.data >= data_inicio_dt)
            except ValueError:
                pass
        
        if data_fim:
            try:
                data_fim_dt = datetime.strptime(data_fim, '%Y-%m-%d')
                query = query.filter(Movimentacao.data <= data_fim_dt)
            except ValueError:
                pass
        
        # Execução da query
        resultados = query.order_by(Movimentacao.data).all()
        
        # Criação do arquivo CSV
        si = StringIO()
        writer = csv.writer(si)
        writer.writerow(['ID', 'Código', 'Produto', 'Tipo', 'Quantidade', 'Data', 'Observação'])
        
        for mov, nome_produto in resultados:
            writer.writerow([
                mov.id,
                mov.codigo_produto,
                nome_produto,
                mov.tipo,
                mov.quantidade,
                mov.data.strftime('%d/%m/%Y %H:%M:%S'),
                mov.observacao or ''
            ])
        
        output = si.getvalue()
        si.close()
        
        # Nome do arquivo com timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'movimentacoes_{timestamp}.csv'
        
        # Envio do arquivo
        return send_file(
            StringIO(output),
            mimetype='text/csv',
            as_attachment=True,
            download_name=filename
        )
    
    except Exception as e:
        flash(f'Erro ao exportar movimentações: {str(e)}', 'danger')
        return render_template('exportar.html')

@relatorios_bp.route('/')
@login_required
@admin_required
def index():
    """Rota para página de relatórios"""
    return render_template('exportar.html')
