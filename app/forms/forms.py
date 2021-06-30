from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed 
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, EqualTo, Length, ValidationError
from app import db

class CadastroForm(FlaskForm):
    email = StringField("Email", 
        validators = [DataRequired(message="Campo Obrigatório")])
    nome = StringField("Nome", 
        validators = [DataRequired(message="Campo Obrigatório")])
    password = PasswordField("Senha", validators=[DataRequired()])
    confirma = PasswordField("Confirma senha", validators=[
        DataRequired(message="Confirmação de senha necessária."), 
        EqualTo('password', message="As senhas não correspondem")
        ])
    submit_btn = SubmitField("Cadastrar")

class LoginForm(FlaskForm):
    email = StringField("Email",
        validators = [DataRequired(message="Campo Obrigatório")])
    password = PasswordField("Senha", validators=[DataRequired()])
    submit_btn = SubmitField("Login")

    def validate_email(self, email):
        email_get = db.child('usuarios').order_by_child("email").equal_to(email.data).get()
        if len(email_get.val()) == 0:
            raise ValidationError("Email não cadastrado!")

class PostForm(FlaskForm):
    titulo = StringField("Título", 
        validators = [DataRequired(message="Campo Obrigatório")])
    corpo = StringField("Corpo da postagem",
        validators = [DataRequired(message="Campo Obrigatório")])
    foto = FileField("Imagem",
        validators = [FileAllowed(['jpg', 'png', 'jpeg'], message="Somente imagens são permitidos.")
    ])
    submit_btn = SubmitField("Publicar")
    
class RecuperaSenhaForm(FlaskForm):
    email = StringField("Email", 
        validators = [DataRequired(message="Campo Obrigatório")])
    submit_btn = SubmitField("Recuperar Senha")