import os
from flask import Flask, redirect, url_for
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect

# Inicialização do aplicativo Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', os.urandom(24))
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///estoque.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Proteção CSRF
csrf = CSRFProtect(app)

# Configuração do Login Manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Por favor, faça login para acessar esta página.'
login_manager.login_message_category = 'warning'

# Importação dos modelos
from src.models import db, Usuario

# Inicialização do banco de dados
db.init_app(app)

# Função para carregar usuário para o Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

# Registro dos blueprints
from src.controllers.auth import auth_bp
from src.controllers.produtos import produtos_bp
from src.controllers.movimentacoes import movimentacoes_bp
from src.controllers.solicitacoes import solicitacoes_bp
from src.controllers.relatorios import relatorios_bp
from src.controllers.utils import utils_bp

app.register_blueprint(auth_bp)
app.register_blueprint(produtos_bp)
app.register_blueprint(movimentacoes_bp)
app.register_blueprint(solicitacoes_bp)
app.register_blueprint(relatorios_bp)
app.register_blueprint(utils_bp)

# Rota principal - CORRIGIDA
@app.route('/')
def index():
    # Redirecionar para a rota de listagem de produtos
    return redirect(url_for('produtos.listar'))

# Contexto para templates
@app.context_processor
def inject_globals():
    from datetime import datetime
    return {
        'current_year': datetime.now().year
    }

# Inicialização do banco de dados
def init_db():
    with app.app_context():
        db.create_all()
        # Verificar se já existe um usuário admin
        admin = Usuario.query.filter_by(username='admin').first()
        if not admin:
            from werkzeug.security import generate_password_hash
            admin = Usuario(
                username='admin',
                password=generate_password_hash('admin'),
                is_admin=True
            )
            db.session.add(admin)
            db.session.commit()

# Execução do aplicativo
if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
