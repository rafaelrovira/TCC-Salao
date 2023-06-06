from flask import Flask, redirect, render_template, url_for, request
import flask_login
from flask_mail import Message, Mail
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt
from datetime import date

# models
import models.user_models as usr
import models.agenda_models as agend

# Configs
app = Flask(__name__)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///salao.db'
app.config['SECRET_KEY'] = "uma chave super secreta"

#config e-mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'contato.salaobarbearia@gmail.com'
app.config['MAIL_DEFAULT_SENDER'] = 'contato.salaobarbearia@gmail.com'
app.config['MAIL_PASSWORD'] = 'obphdvlonygiaqsu'

mail = Mail(app)


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
    level = db.Column(db.String(30),    nullable=False)
    #teste abaixo
    agendamentos = db.relationship('Agenda', backref='usuario', lazy=True)

# Classe para criar a table agenda
class Agenda(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    username = db.Column(db.String(20), nullable=False)
    data = db.Column(db.DateTime(200),  nullable=False)
    servico = db.Column(db.String(20), nullable=False)
    telefone = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(200),   nullable=False)

# Cria o database
db.create_all()

# Cria o primeiro administrador
#admin_password = bcrypt.generate_password_hash('admin')
#admin = User(username='admin', password=admin_password, email='admin@example.com', telefone='1195448652', level='admin')
#db.session.add(admin)
#db.session.commit()


# Classe para os formulários de usuário
class RegisterForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=30)], render_kw={"placeholder": "Digite o nome de usuário"})
    password = PasswordField(validators=[InputRequired(), Length(min=4, max=80)], render_kw={"placeholder": "Senha"})
    email = StringField(validators=[InputRequired()], render_kw={"placeholder": "E-mail"})
    telefone = StringField(validators=[InputRequired()], render_kw={"placeholder": "Telefone"})
    submit = SubmitField("Cadastrar")

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
    submit = SubmitField("Entrar")


class ConsultaForm(FlaskForm):
    email = StringField(validators=[InputRequired()], render_kw={"placeholder": "E-mail"})
    submit = SubmitField("Consultar")


class DeleteForm(FlaskForm):
    email = StringField(validators=[InputRequired()], render_kw={"placeholder": "E-mail"})
    submit = SubmitField("Deletar")

#Functions

def enviar_email(destinatario, assunto, corpo):
    msg = Message(assunto, recipients=[destinatario])
    msg.body = corpo
    mail.send(msg)


# Rotas
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                if user.level == "client":
                    login_user(user)
                    return redirect(url_for('dashboard'))
        
                if user.level == "admin":
                    login_user(user)
                    return redirect(url_for('dashboard'))
        else:
            return("Usuário incorreto")
    return render_template('login.html', form=form)


@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():

    user = flask_login.current_user
    username = user.username

    if current_user.level == "client":
        return render_template('dashboard_test_client.html', username=username)
    
    if current_user.level == "admin":
        return render_template('dashboard_test_admin.html', username=username)


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
        nome_servico = request.form['nome_servico']

        #tratamento da data e hora
        data = data.replace("T"," ")
        data = data.replace("-","/")
        datetime_object = datetime.strptime(data, '%Y/%m/%d %H:%M')
        novo_agendamento = agend.adicionar_agendamento(current_user.id, username, email, telefone, datetime_object, nome_servico)
        
        #notificação e-mail
        if novo_agendamento:
            assunto = "Confirmação de Agendamento"
            corpo = f"Olá {username}, o seu agendamento para o serviço {nome_servico} foi marcado para {datetime_object}."
            enviar_email(email, assunto, corpo)
            
            # Adicione a mensagem na sessão do Flask
            if current_user.level =="admin":
                return f"""
                <script>
                    alert("Agendamento realizado com sucesso !");
                </script>
                """ + render_template('agendar_servico_admin_teste.html')
            elif current_user.level == "client":
                return f"""
                <script>
                    alert("Agendamento realizado com sucesso !");
                </script>
                """ + render_template('agendar_servico_client_teste.html')

            
    if current_user.level == "admin":
        return render_template('agendar_servico_admin_teste.html')
    elif current_user.level == "client":
        return render_template('agendar_servico_client_teste.html')
    else:
        return render_template("register.html")


@app.route('/register_client', methods=['GET', 'POST'])
def register():
    form_client = RegisterForm()
    if form_client.validate_on_submit():   
        form_name = form_client.username.data
        form_password = form_client.password.data
        form_email = form_client.email.data
        form_telefone = form_client.telefone.data
        hashed_password = bcrypt.generate_password_hash(form_password)

        # cria o usuário
        new_user = usr.adicionar_user(form_name, hashed_password, form_email, form_telefone, level="client")
        return redirect(url_for('login'))
    
    return render_template('register.html', form=form_client)

@app.route('/register_admin', methods=['GET', 'POST'])
@login_required
def admin_register(): 

    user = flask_login.current_user
    username = user.username

    #Validação pra ver se o usuário é admin
    user_level = current_user.level
    if user_level != "admin":
        return("Acesso Negado")
    
     # Verificar se o admin está autenticado e tem permissão de acesso
    form = RegisterForm()
    if form.validate_on_submit():   
        form_name = form.username.data
        form_password = form.password.data
        form_email = form.email.data
        form_telefone = form.telefone.data
        hashed_password = bcrypt.generate_password_hash(form_password)
    

        # cria o admin
        try:
            if current_user.level == "admin":
                new_admin = usr.adicionar_user(
                form_name, hashed_password, form_email, form_telefone, level='admin')
                return f"""
            <script>
                alert("Administrador criado com sucesso !");
            </script>
            """ + render_template('register_admin_teste.html', form=form, username=username)
        except AttributeError:
            return("Acesso negado, faça login com um usuário administrador")
        
    return render_template('register_admin_teste.html', form=form, username=username)


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/perfil', methods=['GET', 'POST'])
@login_required
def profile():

    user = flask_login.current_user
    username = user.username

    if current_user.level == "client":
        return render_template('profile_client_teste.html', username=username)
    
    if current_user.level == "admin":
        return render_template('profile_admin_teste.html',username=username)


@app.route('/consulta_user', methods=['GET', 'POST'])
@login_required
def consultar_user():

    if current_user.level == "client":
        return ("Você não tem permissão")
    
    if current_user.level == "admin":
        form = ConsultaForm()
        if form.validate_on_submit():
            form_email = form.email.data
            dados_user = usr.consultar_user(form_email)
            username = dados_user.username
            email = dados_user.email
            telefone = dados_user.telefone
            if username:
                flag = True
            return render_template('consulta_user.html', form=form, username=username, email=email, telefone=telefone, flag=flag)   
    return render_template('consulta_user.html', form=form)

@app.route('/deletar_user', methods=['GET', 'POST'])
@login_required
def deletar_user():
    user = flask_login.current_user
    username = user.username

    if current_user.level == "admin":
        form_delete = DeleteForm()
        if form_delete.validate_on_submit():
            email = form_delete.email.data
            # verificar se o user é um administrador
            dados_user = usr.consultar_user(email)
            if dados_user.level == "admin":
                usr.deleta_user(email)
                return f"""
            <script>
                alert("Usuário deletado com sucesso !");
            </script>
            """ + render_template('deletar_user_teste.html', form=form_delete, username = username)
                
            else:
                usr.deleta_user(email)
                return f"""
            <script>
                alert("Usuário deletado com sucesso !");
            </script>
            """ + render_template('deletar_user_teste.html', form=form_delete, username = username)
    else:
        return("Você não tem permissão para deletar usuários.")
    return render_template('deletar_user_teste.html', form=form_delete, username = username)

@app.route('/usuarios')
@login_required
def list_users():
    user = flask_login.current_user
    username = user.username
    if current_user.level == "client":
        return ("Você não tem permissão")
    
    if current_user.level == "admin":
        users = User.query.all()
        return render_template('users_test.html', users=users, username=username)


@app.route('/agendamentos_dia')
@login_required
def list_agendamentos_dia():

    user = flask_login.current_user
    username = user.username

    if current_user.level == "client":
        return ("Você não tem permissão")
    
    if current_user.level == "admin":
        users = User.query.all()
        hoje = datetime.today().strftime('%Y-%m-%d')
        agendamentos = Agenda.query.filter(Agenda.data >= datetime.combine(date.today(), datetime.min.time()), Agenda.data <= datetime.combine(date.today(), datetime.max.time())).all()
        return render_template('agendamentos_dia_teste.html', agendamentos=agendamentos, username=username)


@app.route('/agendamentos')
@login_required
def list_agendamentos_total():

    user = flask_login.current_user
    username = user.username

    if current_user.level == "client":
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        hoje = datetime.today().strftime('%Y-%m-%d')
        agendamentos = Agenda.query.filter_by(user_id=current_user.id).paginate(page=page, per_page=per_page)
        return render_template('agendamentos_total_client_teste.html', agendamentos=agendamentos, username=username)
        
 #como admin mostra todos os agendamentos
    if current_user.level == "admin":
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        hoje = datetime.today().strftime('%Y-%m-%d')
        agendamentos = Agenda.query.paginate(page=page, per_page=per_page)
        return render_template('agendamentos_total_admin_teste.html', agendamentos=agendamentos, username=username)

    
@app.route('/deletar-agendamento/<int:id_agendamento>', methods=['DELETE'])
@login_required
def deletar_agendamento(id_agendamento):
    agendamento = Agenda.query.filter_by(id=id_agendamento).first()
    if agendamento:
        db.session.delete(agendamento)
        db.session.commit()
        return 'Agendamento removido com sucesso!', 200
    else:
        return 'Agendamento não encontrado.', 404

  
@app.route('/about', methods=['GET'])
def about():
    return render_template('about.html')


@app.route('/services', methods=['GET'])
def services():
    return render_template('servicos.html')


@app.route('/contato', methods=['GET'])
def contact():
    return render_template('contact.html')

# Main
if __name__ == '__main__':
     app.run(debug=True, port=8081)
