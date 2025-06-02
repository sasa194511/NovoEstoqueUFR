from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from src.models import db, Usuario

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('Por favor, preencha todos os campos.', 'danger')
            return render_template('login.html')
        
        user = Usuario.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash(f'Bem-vindo, {user.username}!', 'success')
            
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('index'))
        else:
            flash('Usuário ou senha inválidos.', 'danger')
    
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if not username or not password or not confirm_password:
            flash('Por favor, preencha todos os campos.', 'danger')
            return render_template('register.html')
            
        if password != confirm_password:
            flash('As senhas não coincidem.', 'danger')
            return render_template('register.html')
            
        existing_user = Usuario.query.filter_by(username=username).first()
        if existing_user:
            flash('Este nome de usuário já está em uso.', 'danger')
            return render_template('register.html')
            
        new_user = Usuario(
            username=username,
            password=generate_password_hash(password),
            is_admin=False
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Cadastro realizado com sucesso! Faça login para continuar.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Você saiu do sistema.', 'info')
    return redirect(url_for('auth.login'))
