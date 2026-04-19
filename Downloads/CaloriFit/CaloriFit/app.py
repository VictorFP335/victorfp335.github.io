from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'chave_super_secreta_padrao')

DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///calorifit_v3.db')
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    nome = db.Column(db.String(150), nullable=False)
    idade = db.Column(db.Integer, nullable=False)
    peso = db.Column(db.Float, nullable=False) # em kg
    altura = db.Column(db.Float, nullable=False) # em cm
    sexo = db.Column(db.String(1), nullable=False) # 'M' ou 'F'
    objetivo = db.Column(db.String(50), nullable=True)
    anotacoes = db.Column(db.Text, nullable=True)
    refeicoes = db.relationship('Refeicao', backref='user', lazy=True)
    exercicios = db.relationship('Exercicio', backref='user', lazy=True)

    def calcular_bmr(self):
        # Fórmula de Harris-Benedict
        if self.sexo.upper() == 'M':
            return 88.362 + (13.397 * self.peso) + (4.799 * self.altura) - (5.677 * self.idade)
        else:
            return 447.593 + (9.247 * self.peso) + (3.098 * self.altura) - (4.330 * self.idade)

class Refeicao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(100), nullable=False)
    calorias = db.Column(db.Integer, nullable=False)
    data = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Exercicio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    calorias = db.Column(db.Integer, nullable=False)
    data = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Autenticação
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, senha):
            login_user(user)
            return redirect(url_for('home'))
        else:
            flash('Login inválido. Verifique suas credenciais.', 'error')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')
        nome = request.form.get('nome')
        idade = int(request.form.get('idade'))
        peso = float(request.form.get('peso'))
        altura = float(request.form.get('altura'))
        sexo = request.form.get('sexo')
        objetivo = request.form.get('objetivo')
        anotacoes = request.form.get('anotacoes')

        if User.query.filter_by(email=email).first():
            flash('Email já cadastrado.', 'error')
            return redirect(url_for('register'))

        novo_usuario = User(
            email=email,
            password_hash=generate_password_hash(senha),
            nome=nome,
            idade=idade,
            peso=peso,
            altura=altura,
            sexo=sexo,
            objetivo=objetivo,
            anotacoes=anotacoes
        )
        db.session.add(novo_usuario)
        db.session.commit()
        login_user(novo_usuario)
        return redirect(url_for('home'))
        
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        if user:
            # Em um cenário real enviaríamos um e-mail com token.
            # Aqui simularemos via flash para facilitar o teste.
            flash('Simulação: Um link de recuperação foi enviado para o seu e-mail (Token Simulado)', 'info')
        else:
            flash('E-mail não encontrado.', 'error')
    return render_template('forgot_password.html')

# Dashboard
@app.route('/')
@login_required
def home():
    refeicoes_data = Refeicao.query.filter_by(user_id=current_user.id).all()
    exercicios_data = Exercicio.query.filter_by(user_id=current_user.id).all()
    
    # Processamento para agrupar por dia (Gráficos melhorados)
    consumo_por_dia = {}
    gasto_por_dia = {}
    
    total_consumido = 0
    total_gasto = 0
    hj = datetime.now().strftime("%d/%m/%Y")
    
    for r in refeicoes_data:
        dia = r.data.split(' ')[0]
        consumo_por_dia[dia] = consumo_por_dia.get(dia, 0) + r.calorias
        if dia == hj:
            total_consumido += r.calorias
            
    for e in exercicios_data:
        dia = e.data.split(' ')[0]
        gasto_por_dia[dia] = gasto_por_dia.get(dia, 0) + e.calorias
        if dia == hj:
            total_gasto += e.calorias

    # Combinar todas as datas (únicas e ordenadas em formato string pra simplicar)
    todas_datas = sorted(list(set(list(consumo_por_dia.keys()) + list(gasto_por_dia.keys()))))
    
    grafico_consumo = [consumo_por_dia.get(d, 0) for d in todas_datas]
    grafico_gasto = [gasto_por_dia.get(d, 0) for d in todas_datas]
    
    # Harris-Benedict BMR
    bmr = current_user.calcular_bmr()
    calorias_restantes = bmr + total_gasto - total_consumido

    return render_template(
        'home.html',
        bmr=round(bmr, 2),
        total_consumido=total_consumido,
        total_gasto=total_gasto,
        calorias_restantes=round(calorias_restantes, 2),
        labels_dias=todas_datas,
        dados_consumo=grafico_consumo,
        dados_gasto=grafico_gasto
    )

@app.route('/refeicoes')
@login_required
def mostrar_refeicoes():
    refeicoes = Refeicao.query.filter_by(user_id=current_user.id).all()
    return render_template('refeicoes.html', refeicoes=refeicoes)

@app.route('/add_refeicao', methods=['POST'])
@login_required
def add_refeicao():
    descricao = request.form['descricao']
    calorias = int(request.form['calorias'])
    data = datetime.now().strftime("%d/%m/%Y %H:%M")
    nova = Refeicao(descricao=descricao, calorias=calorias, data=data, user_id=current_user.id)
    db.session.add(nova)
    db.session.commit()
    return redirect('/refeicoes')

@app.route('/exercicios')
@login_required
def mostrar_exercicios():
    exercicios = Exercicio.query.filter_by(user_id=current_user.id).all()
    return render_template('exercicios.html', exercicios=exercicios)

@app.route('/add_exercicio', methods=['POST'])
@login_required
def add_exercicio():
    nome = request.form['nome']
    calorias = int(request.form['calorias'])
    data = datetime.now().strftime("%d/%m/%Y %H:%M")
    novo = Exercicio(nome=nome, calorias=calorias, data=data, user_id=current_user.id)
    db.session.add(novo)
    db.session.commit()
    return redirect('/exercicios')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
