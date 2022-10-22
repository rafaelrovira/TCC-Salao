from flask import Flask, redirect, render_template, url_for, request
import flask_login
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt
# models
import models.user_models as cli
import models.agenda_models as agend


# Configs
app = Flask(__name__)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///salao.db'
app.config['SECRET_KEY'] = "uma chave super secreta"

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Classe para criar a table usuário
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(200),   nullable=False)
    telefone = db.Column(db.String(30), nullable=False)


# Classe para criar a table funcionário
class Funcionario(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(200),   nullable=False)
    telefone = db.Column(db.String(30), nullable=False)


# Classe para criar a table cliente
class Cliente(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(200),   nullable=False)
    telefone = db.Column(db.String(30), nullable=False)

# Classe para criar a table agenda
class Agenda(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False)
    data = db.Column(db.DateTime(200),  nullable=False)
    servico = db.Column(db.String(20), nullable=False)
    telefone = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(200),   nullable=False)


# Cria o database
db.create_all()


# Classe para os formulários de usuário
class RegisterForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=30)], render_kw={"placeholder": "Usuário"})
    password = PasswordField(validators=[InputRequired(), Length(min=4, max=80)], render_kw={"placeholder": "Senha"})
    email = StringField(validators=[InputRequired()], render_kw={"placeholder": "E-mail"})
    telefone = StringField(validators=[InputRequired()], render_kw={"placeholder": "Telefone"})
    submit = SubmitField("Register")

    def validate_username(self, username):
        existing_user_username = User.query.filter_by(
            username=username.data).first()

        if existing_user_username:
            raise ValidationError(
                "Esse nome de usuário já existe, por favor, escolha um diferente")


class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(
        min=4, max=30)], render_kw={"placeholder": ""})
    password = PasswordField(validators=[InputRequired(), Length(
        min=4, max=80)], render_kw={"placeholder": ""})
    submit = SubmitField("Login")



# Rotas
@app.route('/')
def home():
    return render_template('home.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('dashboard'))
        else:
            return("Usuário incorreto")
    return render_template('login.html', form=form)


@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    return render_template('dashboard.html')


@app.route('/agendar_servico', methods=['GET', 'POST'])
@login_required
#precisa puxar os dados de login do user
def agendar_servico():
    user = flask_login.current_user
    username = user.username
    email = user.email
    telefone = user.telefone

    if request.method == "POST":
        data = request.form['calendario_data']
        hora = request.form['calendario_hora']
        nome_servico = request.form['nome_servico']

        #tratamento da data e hora
        datetime_str = f"{data} {hora}"
        datetime_object = datetime.strptime(datetime_str, '%d/%m/%Y %H:%M:%S')

        novo_agendamento = agend.adicionar_agendamento(username, email, telefone, datetime_object, nome_servico)


    return render_template('agendar_servico.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        form_name = form.username.data
        form_password = form.password.data
        form_email = form.email.data
        form_telefone = form.telefone.data
        hashed_password = bcrypt.generate_password_hash(form_password)
        # cria o usuário
        new_user = cli.adicionar_user(
            form_name, hashed_password, form_email, form_telefone)
        return redirect(url_for('login'))
    return render_template('register.html', form=form)


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    return render_template('profile.html')


# Main
if __name__ == '__main__':
    app.run(debug=True, port=8081)
