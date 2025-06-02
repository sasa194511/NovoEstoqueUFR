from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class Usuario(db.Model, UserMixin):
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    data_cadastro = db.Column(db.DateTime, default=datetime.now)
    
    solicitacoes = db.relationship('Solicitacao', backref='usuario', lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<Usuario {self.username}>'

class Produto(db.Model):
    __tablename__ = 'produtos'
    
    codigo = db.Column(db.String(20), primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    quantidade = db.Column(db.Integer, nullable=False, default=0)
    categoria = db.Column(db.String(50))
    descricao = db.Column(db.String(255))
    data_cadastro = db.Column(db.DateTime, default=datetime.now)
    data_atualizacao = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    movimentacoes = db.relationship('Movimentacao', backref='produto', lazy=True, cascade="all, delete-orphan")
    solicitacoes = db.relationship('Solicitacao', backref='produto', lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<Produto {self.codigo}: {self.nome}>'

class Movimentacao(db.Model):
    __tablename__ = 'movimentacoes'
    
    id = db.Column(db.Integer, primary_key=True)
    codigo_produto = db.Column(db.String(20), db.ForeignKey('produtos.codigo', ondelete='CASCADE'), nullable=False)
    tipo = db.Column(db.String(10), nullable=False)  # 'Entrada' ou 'Saída'
    quantidade = db.Column(db.Integer, nullable=False)
    data = db.Column(db.DateTime, default=datetime.now)
    observacao = db.Column(db.String(255))
    
    def __repr__(self):
        return f'<Movimentacao {self.id}: {self.tipo} de {self.quantidade} unidades de {self.codigo_produto}>'

class Solicitacao(db.Model):
    __tablename__ = 'solicitacoes'
    
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id', ondelete='CASCADE'), nullable=False)
    codigo_produto = db.Column(db.String(20), db.ForeignKey('produtos.codigo', ondelete='CASCADE'), nullable=False)
    quantidade_solicitada = db.Column(db.Integer, nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    data = db.Column(db.DateTime, default=datetime.now)
    status = db.Column(db.String(20), default='Pendente')  # 'Pendente', 'Aprovada', 'Recusada'
    
    def __repr__(self):
        return f'<Solicitacao {self.id}: {self.quantidade_solicitada} unidades de {self.codigo_produto}>'
